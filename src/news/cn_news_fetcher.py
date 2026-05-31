"""
Chinese Financial News Fetcher

Fetches financial headlines from Chinese and China-focused financial media:
- 新浪财经 (Sina Finance) — JSON roll API
- 东方财富快讯 (Eastmoney Kuaixun) — JS-var API
- 华尔街见闻 (Wallstreet CN) — live-feed JSON API
- 财新 (Caixin) — scraping
- 中国日报财经 (China Daily Biz) — RSS
- 南华早报 (SCMP China) — RSS
- 证券时报 (Securities Times) — scraping
- 中国证券报 (China Securities Journal) — scraping
- 网易财经 (NetEase Finance) — scraping fallback
- 凤凰财经 (ifeng Finance) — best-effort (China-hosted)
- 第一财经 (Yicai) — best-effort
- 财联社 (CLS) — best-effort
"""

import json
import re
import hashlib
import random
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


def _parse_rss_feed(xml_text, source_name, max_items=20):
    """Parse RSS 2.0 or Atom feed, return headline dicts."""
    headlines = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for item in items[:max_items]:
            title_el = item.find("title") or item.find("atom:title", ns)
            link_el = item.find("link") or item.find("atom:link", ns)
            pub_el = item.find("pubDate") or item.find("atom:published", ns)

            title = (title_el.text or "").strip() if title_el is not None else None
            if link_el is not None:
                link = (link_el.text or link_el.get("href", "")).strip()
            else:
                link = None
            pub = (pub_el.text or "").strip() if pub_el is not None else None

            if title and link:
                headlines.append(_make_headline(title, link, source_name, pub))
    except Exception as e:
        logger.warning(f"RSS parse error for {source_name}: {e}")
    return headlines


def _strip_html(text):
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ─── SINA FINANCE (新浪财经) ─────────────────────────────────────────────────
# Uses the Mix Roll API — accessible from outside China

def fetch_sina_finance_headlines():
    """Fetch from Sina Finance via their JSON roll API."""
    headlines = []
    # pageid=153 lid=2516 = general finance; lid=2584 = stocks
    api_urls = [
        ("https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=20&page=1", "新浪财经"),
        ("https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2584&num=20&page=1", "新浪股票"),
    ]
    for url, source in api_urls:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                data = resp.json()
                items = data.get("result", {}).get("data", [])
                if not isinstance(items, list):
                    items = []
                count = 0
                for item in items[:20]:
                    title = (item.get("title") or "").strip()
                    link = (item.get("url") or "").strip()
                    pub = item.get("ctime") or item.get("mtime")
                    if title and link and link.startswith("http"):
                        headlines.append(_make_headline(title, link, source, pub))
                        count += 1
                if count:
                    logger.info(f"Fetched {count} from {source}")
            else:
                logger.warning(f"Sina API {url} → {resp.status_code}")
        except Exception as e:
            logger.error(f"Sina Finance fetch error: {e}")
    return headlines


# ─── EASTMONEY KUAIXUN (东方财富快讯) ────────────────────────────────────────
# Kuaixun endpoint returns JS-wrapped JSON — accessible globally

def fetch_eastmoney_headlines():
    """Fetch fast financial flashes from Eastmoney (东方财富快讯)."""
    headlines = []
    url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_20_1_.html"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=12)
        if resp.ok:
            # Response: var ajaxResult={...};
            text = re.sub(r"^var\s+ajaxResult\s*=\s*", "", resp.text.strip()).rstrip(";")
            data = json.loads(text)
            items = data.get("LivesList", [])
            if not isinstance(items, list):
                items = []
            for item in items[:20]:
                title = (item.get("title") or item.get("content") or "").strip()
                title = _strip_html(title)
                newsid = item.get("newsid") or item.get("id", "")
                art_url = f"https://finance.eastmoney.com/a/{newsid}.html" if newsid else ""
                pub = item.get("showtime") or item.get("time")
                if title and art_url and len(title) > 5:
                    headlines.append(_make_headline(title, art_url, "东方财富", pub))
            logger.info(f"Fetched {len(headlines)} from Eastmoney")
        else:
            logger.warning(f"Eastmoney Kuaixun → {resp.status_code}")
    except Exception as e:
        logger.error(f"Eastmoney fetch error: {e}")
    return headlines


# ─── WALLSTREET CN (华尔街见闻) ───────────────────────────────────────────────
# Live-feed API is accessible globally and returns real-time Chinese market news

def fetch_wallstreetcn_headlines():
    """Fetch live market flashes from Wallstreet CN (华尔街见闻)."""
    headlines = []
    url = "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=30"
    try:
        resp = requests.get(
            url,
            headers={**_HEADERS, "Referer": "https://wallstreetcn.com/"},
            timeout=12,
        )
        if resp.ok:
            items = resp.json().get("data", {}).get("items", [])
            if not isinstance(items, list):
                items = []
            for item in items[:20]:
                content = _strip_html(item.get("content") or item.get("content_text") or "")
                title = item.get("title") or (content[:80] if content else "")
                art_uri = item.get("uri") or ""
                if not art_uri.startswith("http"):
                    art_uri = "https://wallstreetcn.com/livenews/" + str(item.get("id", ""))
                pub = item.get("display_time")
                if title and len(title) > 8:
                    headlines.append(_make_headline(title, art_uri, "华尔街见闻", pub))
            logger.info(f"Fetched {len(headlines)} from Wallstreet CN")
        else:
            logger.warning(f"Wallstreet CN → {resp.status_code}")
    except Exception as e:
        logger.error(f"Wallstreet CN fetch error: {e}")
    return headlines


# ─── CAIXIN (财新) ────────────────────────────────────────────────────────────
# caixin.com homepage is accessible globally

def fetch_caixin_headlines():
    """Fetch from Caixin (财新) homepage."""
    headlines = []
    try:
        resp = requests.get("https://www.caixin.com/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if (
                    len(text) > 10
                    and "caixin.com" in href
                    and re.search(r"/\d{4}-\d{2}-\d{2}/\d+", href)
                    and href not in seen
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "财新"))
            logger.info(f"Fetched {len(headlines)} from Caixin")
        else:
            logger.warning(f"Caixin → {resp.status_code}")
    except Exception as e:
        logger.error(f"Caixin fetch error: {e}")
    return headlines[:20]


# ─── CHINA DAILY (中国日报财经) ──────────────────────────────────────────────
# RSS feed, accessible globally

def fetch_chinadaily_headlines():
    """Fetch from China Daily Business RSS."""
    headlines = []
    feeds = [
        ("https://www.chinadaily.com.cn/rss/bizchina_rss.xml", "中国日报"),
        ("https://www.chinadaily.com.cn/rss/china_rss.xml", "中国日报"),
    ]
    for url, source in feeds:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                items = _parse_rss_feed(resp.text, source, max_items=15)
                if items:
                    headlines.extend(items)
                    logger.info(f"Fetched {len(items)} from {source} RSS")
                    break
            else:
                logger.warning(f"ChinaDaily RSS {url} → {resp.status_code}")
        except Exception as e:
            logger.error(f"ChinaDaily fetch error: {e}")
    return headlines


# ─── SCMP CHINA (南华早报) ────────────────────────────────────────────────────
# RSS accessible globally, China section covers markets and business

def fetch_scmp_headlines():
    """Fetch from SCMP China section RSS."""
    headlines = []
    feeds = [
        ("https://www.scmp.com/rss/5/feed", "南华早报"),          # China
        ("https://www.scmp.com/rss/92/feed", "南华早报"),          # Business
    ]
    for url, source in feeds:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=12)
            if resp.ok:
                items = _parse_rss_feed(resp.text, source, max_items=15)
                if items:
                    headlines.extend(items)
                    logger.info(f"Fetched {len(items)} from SCMP {url}")
                    break
            else:
                logger.warning(f"SCMP RSS {url} → {resp.status_code}")
        except Exception as e:
            logger.error(f"SCMP fetch error: {e}")
    return headlines


# ─── NETEASE FINANCE (网易财经) — best effort ─────────────────────────────────

def fetch_netease_finance_headlines():
    """Fetch from NetEase Finance (网易财经)."""
    headlines = []
    try:
        resp = requests.get("https://money.163.com/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if (
                    len(text) > 10
                    and "money.163.com" in href
                    and href not in seen
                    and any(ord(c) > 0x4E00 for c in text)
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "网易财经"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from NetEase Finance")
    except Exception as e:
        logger.error(f"NetEase Finance fetch error: {e}")
    return headlines[:15]


# ─── IFENG FINANCE (凤凰财经) — best effort ──────────────────────────────────

def fetch_ifeng_finance_headlines():
    """Fetch from ifeng Finance (凤凰财经) — best effort."""
    headlines = []
    try:
        resp = requests.get("https://finance.ifeng.com/", headers=_HEADERS, timeout=10)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if href.startswith("/"):
                    href = "https://finance.ifeng.com" + href
                if (
                    len(text) > 10
                    and "ifeng.com" in href
                    and href not in seen
                    and any(ord(c) > 0x4E00 for c in text)
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "凤凰财经"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from ifeng Finance")
    except Exception as e:
        logger.debug(f"ifeng Finance unavailable: {e}")
    return headlines[:15]


# ─── YICAI (第一财经) — best effort ──────────────────────────────────────────

def fetch_yicai_headlines():
    """Fetch from Yicai (第一财经) — best effort."""
    headlines = []
    try:
        resp = requests.get("https://www.yicai.com/news/", headers=_HEADERS, timeout=10)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if href.startswith("/"):
                    href = "https://www.yicai.com" + href
                if (
                    len(text) > 10
                    and href.startswith("http")
                    and href not in seen
                    and any(ord(c) > 0x4E00 for c in text)
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "第一财经"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from Yicai")
    except Exception as e:
        logger.debug(f"Yicai unavailable: {e}")
    return headlines[:15]


# ─── CLS (财联社) — best effort ──────────────────────────────────────────────

def fetch_cls_headlines():
    """Fetch from CLS (财联社) — best effort."""
    headlines = []
    try:
        resp = requests.get(
            "https://www.cls.cn/telegraph",
            headers={**_HEADERS, "Referer": "https://www.cls.cn/"},
            timeout=10,
        )
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for el in soup.select(".telegraph-content-box, .tele-title, .news-item"):
                text = el.get_text(strip=True)
                a = el.find("a")
                href = (a.get("href", "") if a else "").strip()
                if href.startswith("/"):
                    href = "https://www.cls.cn" + href
                if not href.startswith("http"):
                    href = "https://www.cls.cn/telegraph"
                if len(text) > 10 and href not in seen:
                    seen.add(href)
                    headlines.append(_make_headline(text[:120], href, "财联社"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from CLS")
    except Exception as e:
        logger.debug(f"CLS unavailable: {e}")
    return headlines[:15]


# ─── SECURITIES TIMES (证券时报) ─────────────────────────────────────────────
# stcn.com homepage is accessible globally and renders articles server-side

def fetch_securities_times_headlines():
    """Fetch from Securities Times (证券时报 stcn.com) — scraping."""
    headlines = []
    try:
        resp = requests.get("https://www.stcn.com/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if href.startswith("/"):
                    href = "https://www.stcn.com" + href
                if (
                    len(text) > 10
                    and "/article/detail/" in href
                    and href not in seen
                    and any(ord(c) > 0x4E00 for c in text)
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "证券时报"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from 证券时报")
        else:
            logger.warning(f"证券时报 → {resp.status_code}")
    except Exception as e:
        logger.debug(f"证券时报 unavailable: {e}")
    return headlines[:20]


# ─── CHINA SECURITIES JOURNAL (中国证券报) ────────────────────────────────────
# cs.com.cn is the official CSRC-backed securities paper; server-side rendered

def fetch_china_securities_journal_headlines():
    """Fetch from China Securities Journal (中国证券报 cs.com.cn) — scraping."""
    headlines = []
    try:
        resp = requests.get("https://www.cs.com.cn/", headers=_HEADERS, timeout=12)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "gb18030"
            soup = BeautifulSoup(resp.content, "html.parser")
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                text = a.get_text(strip=True)
                if (
                    len(text) > 10
                    and "cs.com.cn" in href
                    and re.search(r"/\d{4}/\d{2}/\d{2}/", href)
                    and href not in seen
                    and any(ord(c) > 0x4E00 for c in text)
                ):
                    seen.add(href)
                    headlines.append(_make_headline(text, href, "中国证券报"))
            if headlines:
                logger.info(f"Fetched {len(headlines)} from 中国证券报")
        else:
            logger.warning(f"中国证券报 → {resp.status_code}")
    except Exception as e:
        logger.debug(f"中国证券报 unavailable: {e}")
    return headlines[:20]


# ─── IMAGE HANDLING ───────────────────────────────────────────────────────────

def _ensure_cn_image_dir():
    base = Path(__file__).parent.parent.parent / "static" / "images" / "cn-headlines"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _fetch_cn_image(url, headline_id):
    """
    Extract image for a CN headline. CN pages live at cn/index.html so all
    image paths must be prefixed with ../ to reach the static/ directory.

    Strategy:
      1. Return cached cn-headline image if already downloaded.
      2. Return existing dynamic image if already generated.
      3. Scrape OG/Twitter meta image from article page.
      4. Fall back to create_dynamic_image() (PIL-generated placeholder).
    """
    img_dir = _ensure_cn_image_dir()
    img_path = img_dir / f"{headline_id}.jpg"
    # Paths relative from cn/index.html → need ../
    rel_path = f"../static/images/cn-headlines/{headline_id}.jpg"

    # Check cached cn-headline image
    if img_path.exists():
        return rel_path

    # Check cached dynamic image
    dynamic_full = Path(__file__).parent.parent.parent / "static" / "images" / "dynamic" / f"{headline_id}.jpg"
    if dynamic_full.exists():
        return f"../static/images/dynamic/{headline_id}.jpg#dynamic"

    # Try to scrape OG/Twitter image from article
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if resp.ok:
            resp.encoding = resp.apparent_encoding or "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")

            # OG/Twitter meta image
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

            # Article body images
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

    # Fallback: generate dynamic PIL image (same as EN site fallback)
    try:
        from .news_fetcher import create_dynamic_image
        dyn = create_dynamic_image(headline_id)
        if dyn:
            return f"../{dyn}#dynamic"
    except Exception as e:
        logger.debug(f"CN dynamic image fallback failed for {headline_id}: {e}")

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
    Fetch financial headlines from Chinese and China-focused financial media.
    Returns dict with 'headlines' list and 'analysis' from DeepSeek.

    Priority sources (reliable globally):
      Sina Finance API, Eastmoney Kuaixun, Wallstreet CN, Caixin, China Daily RSS, SCMP,
      Securities Times, China Securities Journal

    Best-effort sources (may be blocked outside mainland China):
      NetEase, ifeng, Yicai, CLS
    """
    primary_sources = [
        fetch_sina_finance_headlines,
        fetch_eastmoney_headlines,
        fetch_wallstreetcn_headlines,
        fetch_caixin_headlines,
        fetch_chinadaily_headlines,
        fetch_scmp_headlines,
        fetch_securities_times_headlines,
        fetch_china_securities_journal_headlines,
    ]
    fallback_sources = [
        fetch_netease_finance_headlines,
        fetch_ifeng_finance_headlines,
        fetch_yicai_headlines,
        fetch_cls_headlines,
    ]

    all_headlines = []
    seen_urls = set()
    seen_titles = set()

    for fn in primary_sources + fallback_sources:
        try:
            items = fn()
        except Exception as e:
            logger.error(f"Source {fn.__name__} failed: {e}")
            items = []

        if test_mode and items:
            items = items[:2]

        for h in items:
            url = h.get("url", "")
            norm_url = re.sub(r"(\?|&)(utm_[^&]*)(&|$)", "", url).rstrip("/")
            # Normalize title: strip punctuation/spaces, lowercase, use first 20 chars
            raw_title = h.get("headline", "")
            norm_title = re.sub(r"[^\w\u4e00-\u9fff]", "", raw_title.lower())[:20]
            if norm_url and norm_url not in seen_urls and (not norm_title or norm_title not in seen_titles):
                all_headlines.append(h)
                seen_urls.add(norm_url)
                if norm_title:
                    seen_titles.add(norm_title)

    logger.info(f"Total CN headlines collected: {len(all_headlines)}")

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
