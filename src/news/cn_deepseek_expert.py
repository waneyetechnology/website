"""
DeepSeek Financial Expert — Chinese Market Edition

Analyzes Chinese financial news and provides comprehensive market analysis
focused on A-shares, Hong Kong stocks, and China macro economy.
Uses the same DeepSeek API with a Chinese-market-focused prompt.
"""

import os
import time
from datetime import datetime, timezone, timedelta
import json
import re
import requests
from ..log import logger


class DeepSeekCNFinancialExpert:
    """AI financial analyst specialized in Chinese markets using the DeepSeek API."""

    DEFAULT_QUESTION = "今日中国金融市场有哪些重要动态？有哪些值得重点关注的新闻？"

    def __init__(self, api_key=None, analysis_question=None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        self.analysis_question = analysis_question or self.DEFAULT_QUESTION
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not set. CN financial analysis unavailable.")

    def is_available(self):
        return bool(self.api_key)

    def _prepare_headlines_text(self, headlines, max_headlines=None):
        items = headlines if max_headlines is None else headlines[:max_headlines]
        lines = []
        for i, h in enumerate(items, 1):
            lines.append(f"{i}. {h['headline']}")
            if h.get("url"):
                domain = urlparse_domain(h["url"])
                lines.append(f"   来源: {domain}")
            lines.append("")
        return "\n".join(lines).strip()

    def _create_analysis_prompt(self, headlines_text):
        beijing_tz = timezone(timedelta(hours=8))
        now_beijing = datetime.now(beijing_tz)
        current_date = now_beijing.strftime("%Y年%m月%d日")
        current_time = now_beijing.strftime("%H:%M")

        return f"""你是DeepSeek，一位专注于中国金融市场的高级AI分析师。你的专业领域包括：
- A股市场分析（上证、深证、创业板、科创板）
- 香港股市及港股通
- 中国宏观经济政策与货币政策
- 人民币汇率与大宗商品
- 中国上市公司基本面分析
- 中国经济数据解读（GDP、CPI、PPI、PMI、社融等）

请基于以下今日（{current_date}）中国财经新闻标题，提供专业的市场分析报告。

新闻标题列表：
{headlines_text}

请回答："{self.analysis_question}"

**重要要求：**
- 每个分析板块必须包含 "headline_sources" 字段（1-based 新闻编号数组），用于追溯分析依据
- 市场情绪评分（market_sentiment_score）应反映A股市场整体情绪，0-100分
- 重点关注中国特色行业：新能源、半导体、消费、地产、银行、医药生物
- ticker字段使用A股代码（如：600519.SH、000858.SZ）或港股代码（如：0700.HK）

请严格按照以下JSON格式输出，不要包含任何markdown格式：
{{
  "analysis_date": "{current_date}",
  "analysis_time": "{current_time}",
  "executive_summary": {{
    "key_highlights": ["列举所有重要要点"],
    "market_sentiment_score": 65,
    "overall_sentiment": "positive/negative/neutral",
    "headline_sources": [1, 2, 3]
  }},
  "market_insights": {{
    "sectors": [
      {{
        "sector": "新能源",
        "trend": "板块走势描述",
        "implications": "对投资者的影响",
        "headline_sources": [1, 3]
      }}
    ],
    "key_themes": ["列举所有主要市场主题"],
    "headline_sources": [1, 2, 3, 4, 5]
  }},
  "risk_assessment": [
    {{
      "risk_factor": "风险因素名称",
      "impact": "High/Medium/Low",
      "likelihood": "High/Medium/Low",
      "mitigation": "应对策略",
      "headline_sources": [2, 4]
    }}
  ],
  "strategic_recommendations": {{
    "opportunities": [
      {{
        "recommendation": "投资建议",
        "rationale": "推荐理由",
        "tickers": ["600519.SH"],
        "timeframe": "short/medium/long-term",
        "headline_sources": [1, 5]
      }}
    ],
    "defensive_moves": [
      {{
        "recommendation": "防御性操作建议",
        "rationale": "风险规避逻辑",
        "tickers": ["510300.SH"],
        "timeframe": "short/medium/long-term",
        "headline_sources": [2, 3]
      }}
    ]
  }},
  "market_outlook": {{
    "short_term": "1-3个月行情展望",
    "long_term": "6-12个月中长期展望",
    "key_catalysts": ["列举所有重要催化剂"],
    "watch_list": ["列举需重点关注的指标和事件"],
    "headline_sources": [1, 2, 3, 4, 5]
  }}
}}

请直接输出JSON，不要有任何其他文字。"""

    def _make_api_request(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是DeepSeek，专注于中国资本市场的资深金融分析师。"
                        "你的分析专业、客观、基于数据。"
                        "请始终以JSON格式输出分析结果，不要包含markdown格式。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 8000,
            "stream": False,
        }

        for attempt in range(3):
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)
                resp = requests.post(
                    self.base_url, headers=headers, json=payload, timeout=(30, 600)
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    if content:
                        return content
                else:
                    logger.error(f"DeepSeek CN API error: {resp.status_code}")
                    return None
            except requests.exceptions.Timeout:
                logger.warning(f"DeepSeek CN timeout attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"DeepSeek CN unexpected error: {e}")
                return None
        return None

    def analyze_headlines(self, headlines, max_headlines=None):
        if not self.is_available():
            logger.warning("DeepSeek API key not set; skipping CN analysis.")
            return None
        if not headlines:
            return None

        text = self._prepare_headlines_text(headlines, max_headlines)
        if not text:
            return None

        logger.info("Sending CN headlines to DeepSeek...")
        raw = self._make_api_request(self._create_analysis_prompt(text))
        if not raw:
            return None

        # Parse JSON
        cleaned = raw.strip()
        # Direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Strip code fences
        for fence in ["```json", "```JSON", "```"]:
            if cleaned.startswith(fence):
                cleaned = cleaned[len(fence):].lstrip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].rstrip()
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    pass

        # Regex extract
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Could not parse DeepSeek CN response as JSON, returning raw text")
        return raw


def urlparse_domain(url):
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.lstrip("www.")
    except Exception:
        return url


def create_cn_financial_expert(api_key=None):
    """Factory function for the Chinese financial expert."""
    return DeepSeekCNFinancialExpert(api_key=api_key)
