"""
History Saver

Writes analysis reports (DeepSeek JSON + indexed headlines) to disk at:
    history/<yyyy>/<mm>/<dd>/<hh>/analysis-report.json

The deploy workflow then commits and pushes this file to the 'history' branch.
The headline index numbers match the 1-based numbering used in the analysis
prompt, so consumers can correlate analysis references back to specific headlines.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .log import logger

# Repo root is two levels up from this file (src/history_saver.py → src/ → repo root)
_REPO_ROOT = Path(__file__).parent.parent


def save_analysis_history(analysis, headlines, repo_root=None):
    """
    Write the analysis JSON and its source headlines to disk.

    The written file has two top-level keys:
        "analysis"  – the unchanged DeepSeek analysis dict
        "headlines" – list of {index, headline, url, publishedAt} where
                      'index' is the 1-based position used in the analysis prompt

    Args:
        analysis (dict | None): Parsed analysis dict from DeepSeek.
        headlines (list): Ordered list of headline dicts (same order fed to the AI).
        repo_root (Path | str | None): Override repo root path (defaults to auto-detected).

    Returns:
        str | None: Relative path of the written file, or None if skipped.
    """
    if not analysis:
        logger.warning("No analysis available – skipping history save.")
        return None

    root = Path(repo_root) if repo_root else _REPO_ROOT
    ts = _parse_analysis_timestamp(analysis)
    rel_path = f"history/{ts.strftime('%Y/%m/%d/%H')}/analysis-report.json"

    indexed_headlines = [
        {
            "index": i + 1,
            "headline": h.get("headline", ""),
            "url": h.get("url", ""),
            "publishedAt": h.get("publishedAt"),
        }
        for i, h in enumerate(headlines)
    ]

    report = {
        "analysis": analysis,
        "headlines": indexed_headlines,
    }

    out_path = root / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Analysis report written to disk: {rel_path}")
    return rel_path


def _parse_analysis_timestamp(analysis):
    """
    Parse the timestamp from the analysis dict.

    Tries to combine ``analysis_date`` ("April 19, 2026") and
    ``analysis_time`` ("10:00") produced by the DeepSeek prompt.
    Falls back to the current UTC time if parsing fails.
    """
    date_str = analysis.get("analysis_date", "")
    time_str = analysis.get("analysis_time", "00:00") or "00:00"
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", f"{fmt} %H:%M")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    logger.warning("Could not parse analysis timestamp; using current UTC time.")
    return datetime.now(timezone.utc)
