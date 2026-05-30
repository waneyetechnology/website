"""HTML generator for the Chinese version of the site."""

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .log import logger
from .minify_assets import minify_html


def get_cn_template_env():
    project_root = Path(__file__).parent.parent
    templates_dir = project_root / "templates" / "cn"
    templates_dir.mkdir(exist_ok=True)
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_cn_html(news, pboc_rates, econ, indices, pboc_economy, financial_analysis=None):
    """Generate the Chinese version of the site HTML."""
    try:
        env = get_cn_template_env()
        template = env.get_template("index.html")

        beijing_tz = timezone(timedelta(hours=8))
        last_updated = datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M 北京时间")

        template_data = {
            "title": "万眼 - 中国金融市场实时资讯与分析",
            "page_title": "万眼 — 中国金融市场全景",
            "last_updated": last_updated,
            "cache_buster": int(time.time()),
            "news": news,
            "pboc_rates": pboc_rates,
            "econ": econ,
            "indices": indices,
            "pboc_economy": pboc_economy,
            "financial_analysis": financial_analysis,
        }

        html = template.render(**template_data)
        logger.info("Successfully rendered CN HTML with Jinja2 templates")
        return minify_html(html)

    except Exception as e:
        logger.error(f"Error generating CN HTML: {e}")
        raise
