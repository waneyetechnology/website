"""
Chinese Financial News Fetcher

Fetches financial headlines from major Chinese financial media:
- 新浪财经 (Sina Finance)
- 网易财经 (NetEase Finance)
- 凤凰财经 (ifeng Finance)
- 东方财富 (Eastmoney)
- 华尔街见闻 (Wallstreet CN)
- 第一财经 (Yicai)
- 21世纪财经 (21jingji)
- 财联社 (cls.cn)
"""

import os
import re
import hashlib
import random
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path
from ..log import logger
from .cn_deepseek_expert import create_cn_financial_expert

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _make_headline(title, url, source, published_at=None):
    """Build a standard headline dict."""
    domain = urlparse(url).netloc
    favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
    return {
        "headline": title,
        "url": url,
        "publishedAt": published_at,
        "source": source,
        "favicon": favicon,
    }


def _parse_rss_items(xml_text, source_name, max_items=15):
    """Parse generic RSS/Atom XML and return headline dicts."""
    headlines = []
    try:
        root = ET.fromstring(xml_text)
        # Handle both RSS 2.0 and Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for item in items[:max_items]:
            title_el = item.find("title") or item.find("atom:title", ns)
            link_el = item.find("link") or item.find("atom:link", ns)
            pub_el = item.find("pubDate") or item.find("atom:published", ns)

            title = title_el.text.strip() if title_el is not None and title_el.text else None
            # <link> in Atom can be an element with href attr
            if link_el is not None:
                link = link_el.text or link_el.get("href", "")
                link = link.strip() if link else None
            else:
                link = None

            pub = pub_el.text.strip() if pub_el is not None and pub_el.text else None

            if title and link:
                headlines.append(_make_headline(title, link, source_name, pub))
    except Exception as e:
        logger.warning(f"RSS parse error for {source_name}: {e}")
    return headlines


# ─── SINA FINANCE (新浪财经) ─────────────────────────────────────────────────

def fetch_sina_finance_headlines():
    """Fetch from Sina Finance RSS feeds."""
    headlines = []
    feeds = [
        ("https://rss.sina.com.cn/finance/gnews/index.xml", "新浪财经"),
        ("https://rss.sina.com.cn/finance/stock/cjkx/index.xml", "新浪股票"),
    ]
    for url, source in feeds:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                items = _parse_rss_items(resp.text, source)
                headlines.extend(items)
                logger.info(f"Fetched {len(items)} from {source}")
            else:
                logger.warning(f"Sina RSS {url} → {resp.status_code}")
        except Exception as e:
            logger.error(f"Sina Finance fetch error ({url}): {e}")
    return headlines


# ─── EASTMONEY (东方财富) ─────────────────────────────────────────────────────

def fetch_eastmoney_headlines():
    """Fetch from Eastmoney (东方财富) news API."""
    headlines = []
    # Eastmoney provides a JSON news API
    url = (
        "https://np-listapi.eastmoney.com/comm/wap/getListInfo"
        "?client=wap&type=1&mTypeAndCode=0&pageSize=20&pageIndex=1"
        "&callback=&token=Eastmoney_Bull_Client_Web"
    )
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=12)
        if resp.ok:
            data = resp.json()
            articles = (
                data.get("data", {}).get("list", [])
                or data.get("data", [])
            )
            for art in articles[:15]:
                title = art.get("title") or art.get("Title")
                art_url = art.get("url") or art.get("Url")
                pub = art.get("publishTime") or art.get("time")
                if title and art_url:
                    headlines.append(_make_headline(title, art_url, "东方财富", pub))
            logger.info(f"Fetched {len(headlines)} from Eastmoney API")
        else:
            logger.warning(f"Eastmoney API → {resp.status_code}")
    except Exception as e:
        logger.error(f"Eastmoney fetch error: {e}")

    # Fallback: scrape main page
    if not headlines:
        try:
            page_url = "https://finance.eastmoney.com/"
            resp = requests.get(page_url, headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.select("a[href*='eastmoney.com']")[:15]:
                    text = a.get_text(strip=True)
                    href = a.get("href", "")
                    if len(text) > 10 and href.startswith("http"):
                        headlines.append(_make_headline(text, href, "东方财富"))
                logger.info(f"Eastmoney scrape fallback: {len(headlines)} items")
        except Exception as e:
            logger.error(f"Eastmoney scrape fallback error: {e}")
    return headlines


# ─── NETEASE FINANCE (网易财经) ───────────────────────────────────────────────

def fetch_netease_finance_headlines():
    """Fetch from NetEase Finance (网易财经)."""
    headlines = []
    # NetEase Finance news list API
    urls = [
        "https://money.163.com/special/00252G50/newsdata_index.js",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                text = resp.text.strip()
                # Remove JSONP wrapper if present
                text = re.sub(r'^[^(]+\(', '', text).rstrip(");")
                import json
                items = json.loads(text)
                if isinstance(items, list):
                    for item in items[:15]:
                        title = item.get("title") or item.get("name")
                        link = item.get("url") or item.get("docurl")
                        pub = item.get("ptime") or item.get("time")
                        if title and link:
                            headlines.append(_make_headline(title, link, "网易财经", pub))
                logger.info(f"Fetched {len(headlines)} from NetEase Finance")
        except Exception as e:
            logger.error(f"NetEase Finance fetch error: {e}")

    # Fallback: scrape
    if not headlines:
        try:
            resp = requests.get("https://money.163.com/", headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.select(".news_title a, .mod_newslist a, h3 a")[:15]:
                    text = a.get_text(strip=True)
                    href = a.get("href", "")
                    if len(text) > 10 and href.startswith("http"):
                        headlines.append(_make_headline(text, href, "网易财经"))
        except Exception as e:
            logger.error(f"NetEase scrape fallback error: {e}")
    return headlines


# ─── IFENG FINANCE (凤凰财经) ────────────────────────────────────────────────

def fetch_ifeng_finance_headlines():
    """Fetch from ifeng Finance (凤凰财经) RSS."""
    headlines = []
    feeds = [
        ("https://rss.ifeng.com/finance.xml", "凤凰财经"),
        ("https://finance.ifeng.com/rss.xml", "凤凰财经"),
    ]
    for url, source in feeds:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                items = _parse_rss_items(resp.text, source)
                if items:
                    headlines.extend(items)
                    logger.info(f"Fetched {len(items)} from {source} ({url})")
                    break
            else:
                logger.warning(f"ifeng RSS {url} → {resp.status_code}")
        except Exception as e:
            logger.error(f"ifeng fetch error ({url}): {e}")

    # Fallback: scrape
    if not headlines:
        try:
            resp = requests.get("https://finance.ifeng.com/", headers=_HEADERS, timeout=12)
            if resp.ok:
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.select(".news-stream a, .list a, h3 a, h4 a")[:15]:
                    text = a.get_text(strip=True)
                    href = a.get("href", "")
                    if len(text) > 10 and ("ifeng.com" in href or href.startswith("/")):
                        if href.startswith("/"):
                            href = "https://finance.ifeng.com" + href
                        headlines.append(_make_headline(text, href, "凤凰财经"))
        except Exception as e:
            logger.error(f"ifeng scrape fallback error: {e}")
    return headlines


# ─── WALLSTREET CN (华尔街见闻) ───────────────────────────────────────────────

def fetch_wallstreetcn_headlines():
    """Fetch from Wallstreet CN (华尔街见闻)."""
    headlines = []
    # Wallstreet CN public API
    url = "https://api-one.wallstcn.com/apiv1/content/information-flow?channel=global-channel&cursor=0&limit=20&accept=article"
    try:
        resp = requests.get(url, headers={**_HEADERS, "Referer": "https://wallstreetcn.com/"}, timeout=12)
        if resp.ok:
            data = resp.json()
            items = data.get("data", {}).get("items", [])
            for item in items[:15]:
                resource = item.get("resource", {}) or {}
                title = resource.get("title") or resource.get("content_text", "")[:80]
                art_id = resource.get("id") or resource.get("uri", "")
                art_url = f"https://wallstreetcn.com/articles/{art_id}" if art_id else ""
                pub = resource.get("display_time") or resource.get("created_at")
                if title and art_url:
                    headlines.append(_make_headline(title, art_url, "华尔街见闻", pub))
            logger.info(f"Fetched {len(headlines)} from Wallstreet CN")
        else:
            logger.warning(f"Wallstreet CN API → {resp.status_code}")
    except Exception as e:
        logger.error(f"Wallstreet CN fetch error: {e}")
    return headlines


# ─── YICAI (第一财经) ─────────────────────────────────────────────────────────

def fetch_yicai_headlines():
    """Fetch from Yicai (第一财经)."""
    headlines = []
    try:
        resp = requests.get("https://www.yicai.com/news/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select(".m-con-lst a, .news-item a, h2 a, h3 a")[:15]:
                text = a.get_text(strip=True)
                href = a.get("href", "")
                if len(text) > 10:
                    if href.startswith("/"):
                        href = "https://www.yicai.com" + href
                    if href.startswith("http"):
                        headlines.append(_make_headline(text, href, "第一财经"))
            logger.info(f"Fetched {len(headlines)} from Yicai")
        else:
            logger.warning(f"Yicai → {resp.status_code}")
    except Exception as e:
        logger.error(f"Yicai fetch error: {e}")
    return headlines


# ─── CLS (财联社) ────────────────────────────────────────────────────────────

def fetch_cls_headlines():
    """Fetch from CLS (财联社) — fast financial news wire."""
    headlines = []
    url = "https://www.cls.cn/api/sw?app=CLS&sv=7.7.5&os=web"
    try:
        resp = requests.get(
            "https://www.cls.cn/telegraph",
            headers={**_HEADERS, "Referer": "https://www.cls.cn/"},
            timeout=12,
        )
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            for el in soup.select(".telegraph-content-box, .tele-title, .news-item")[:15]:
                text = el.get_text(strip=True)
                a = el.find("a")
                href = a.get("href", "") if a else ""
                if len(text) > 10:
                    if href.startswith("/"):
                        href = "https://www.cls.cn" + href
                    if not href.startswith("http"):
                        href = "https://www.cls.cn/telegraph"
                    headlines.append(_make_headline(text[:120], href, "财联社"))
            logger.info(f"Fetched {len(headlines)} from CLS")
    except Exception as e:
        logger.error(f"CLS fetch error: {e}")
    return headlines


# ─── 21JINGJI (21世纪财经) ────────────────────────────────────────────────────

def fetch_21jingji_headlines():
    """Fetch from 21st Century Business Herald (21世纪财经)."""
    headlines = []
    try:
        resp = requests.get("https://www.21jingji.com/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select(".news-item a, .article-item a, h2 a, h3 a")[:15]:
                text = a.get_text(strip=True)
                href = a.get("href", "")
                if len(text) > 10:
                    if href.startswith("/"):
                        href = "https://www.21jingji.com" + href
                    if href.startswith("http"):
                        headlines.append(_make_headline(text, href, "21世纪财经"))
            logger.info(f"Fetched {len(headlines)} from 21jingji")
        else:
            logger.warning(f"21jingji → {resp.status_code}")
    except Exception as e:
        logger.error(f"21jingji fetch error: {e}")
    return headlines


# ─── IMAGE HANDLING ───────────────────────────────────────────────────────────

def _ensure_cn_image_dir():
    base = Path(__file__).parent.parent.parent / "static" / "images" / "cn-headlines"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _fetch_cn_image(url, headline_id):
    """Simple image extraction for Chinese news articles."""
    img_dir = _ensure_cn_image_dir()
    img_path = img_dir / f"{headline_id}.jpg"
    rel_path = f"static/images/cn-headlines/{headline_id}.jpg"

    if img_path.exists():
        return rel_path

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if not resp.ok:
            return None
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # OG image first
        for prop in ["og:image", "twitter:image"]:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if meta and meta.get("content"):
                img_url = meta["content"].strip()
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                if img_url.startswith("http"):
                    _download_image(img_url, img_path, url)
                    if img_path.exists():
                        return rel_path

        # Article content images
        for img in soup.select("article img, .article-img img, .content img")[:3]:
            src = img.get("src") or img.get("data-src", "")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                if not src.startswith("http"):
                    parsed = urlparse(url)
                    src = f"{parsed.scheme}://{parsed.netloc}{src}"
                _download_image(src, img_path, url)
                if img_path.exists():
                    return rel_path
    except Exception as e:
        logger.debug(f"CN image fetch error for {headline_id}: {e}")
    return None


def _download_image(img_url, save_path, referer):
    try:
        headers = {**_HEADERS, "Referer": referer, "Accept": "image/*"}
        r = requests.get(img_url, headers=headers, timeout=10, stream=True)
        if r.ok and int(r.headers.get("content-length", 1000)) > 500:
            content = r.content
            if len(content) > 1000:
                with open(save_path, "wb") as f:
                    f.write(content)
    except Exception as e:
        logger.debug(f"Image download error {img_url}: {e}")


def cleanup_old_cn_images(current_headlines):
    """Remove cn-headline images not in current set."""
    current_ids = {hashlib.md5(h["url"].encode()).hexdigest() for h in current_headlines}
    img_dir = _ensure_cn_image_dir()
    deleted = 0
    for f in list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")):
        if f.stem not in current_ids:
            try:
                f.unlink()
                deleted += 1
            except Exception:
                pass
    if deleted:
        logger.info(f"Deleted {deleted} old CN images")
    return deleted


# ─── MAIN FETCH FUNCTION ─────────────────────────────────────────────────────

def fetch_cn_financial_headlines(test_mode=False):
    """
    Fetch financial headlines from major Chinese financial media sources.
    Returns dict with 'headlines' list and 'analysis' from DeepSeek.
    """
    sources = [
        fetch_sina_finance_headlines,
        fetch_eastmoney_headlines,
        fetch_netease_finance_headlines,
        fetch_ifeng_finance_headlines,
        fetch_wallstreetcn_headlines,
        fetch_yicai_headlines,
        fetch_cls_headlines,
        fetch_21jingji_headlines,
    ]

    weighted = [(random.random(), fn) for fn in sources]
    weighted.sort(reverse=True)

    all_headlines = []
    seen_urls = set()

    for _, fn in weighted:
        try:
            items = fn()
        except Exception as e:
            logger.error(f"Source {fn.__name__} failed: {e}")
            items = []

        if test_mode and items:
            items = items[:2]

        for h in items:
            url = h.get("url", "")
            norm_url = re.sub(r'(\?|&)(utm_[^&]*)(&|$)', '', url).rstrip("/")
            if norm_url and norm_url not in seen_urls:
                all_headlines.append(h)
                seen_urls.add(norm_url)

    logger.info(f"Total CN headlines collected: {len(all_headlines)}")

    # Shuffle for balanced processing
    random.shuffle(all_headlines)

    # Fetch images
    for h in all_headlines:
        headline_id = hashlib.md5(h["url"].encode()).hexdigest()
        h["image"] = _fetch_cn_image(h["url"], headline_id)

    # Generate analysis with DeepSeek
    logger.info("Generating CN financial analysis with DeepSeek...")
    expert = create_cn_financial_expert()
    analysis = expert.analyze_headlines(all_headlines)

    return {"headlines": all_headlines, "analysis": analysis}
