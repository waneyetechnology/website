"""
History Saver

Saves analysis reports (DeepSeek JSON + indexed headlines) to a dedicated
'history' git branch at:  history/<yyyy>/<mm>/<dd>/<hh>/analysis-report.json

The headline index numbers in the saved file match the 1-based numbering
used in the analysis prompt, so consumers can correlate analysis references
back to specific headlines.
"""

import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .log import logger

# Git's canonical empty-tree SHA (always valid in any git repo)
_EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
HISTORY_BRANCH = "history"

# Repo root is two levels up from this file (src/history_saver.py → src/ → repo root)
_REPO_ROOT = Path(__file__).parent.parent


def save_analysis_history(analysis, headlines, repo_root=None):
    """
    Save the analysis JSON and its source headlines to the 'history' git branch.

    The written file has two top-level keys:
        "analysis"  – the unchanged DeepSeek analysis dict
        "headlines" – list of {index, headline, url, publishedAt} where
                      'index' is the 1-based position used in the analysis prompt

    Args:
        analysis (dict | None): Parsed analysis dict from DeepSeek.
        headlines (list): Ordered list of headline dicts (same order fed to the AI).
        repo_root (Path | str | None): Override repo root path (defaults to auto-detected).
    """
    if not analysis:
        logger.warning("No analysis available – skipping history save.")
        return

    root = Path(repo_root) if repo_root else _REPO_ROOT
    ts = _parse_analysis_timestamp(analysis)
    rel_path = f"history/{ts.strftime('%Y/%m/%d/%H')}/analysis-report.json"

    # Build indexed headlines matching the 1-based numbering in the analysis prompt
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
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    commit_message = f"history: {ts.strftime('%Y-%m-%d %H:00 UTC')}"

    try:
        _commit_file_to_branch(root, rel_path, report_json, commit_message)
        logger.info(f"Analysis history saved → branch '{HISTORY_BRANCH}': {rel_path}")
    except Exception as exc:
        logger.error(f"Failed to save analysis history: {exc}")


# ---------------------------------------------------------------------------
# Internal git helpers
# ---------------------------------------------------------------------------

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


def _ensure_history_branch(repo_root):
    """Create the history branch as an orphan if it does not yet exist."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", HISTORY_BRANCH],
        cwd=repo_root,
        capture_output=True,
    )
    if result.returncode == 0:
        return  # Already exists

    # Build an initial empty commit using git plumbing – no working-tree changes
    commit_result = subprocess.run(
        ["git", "commit-tree", _EMPTY_TREE_SHA, "-m", "Initialize history branch"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    commit_sha = commit_result.stdout.decode().strip()

    subprocess.run(
        ["git", "update-ref", f"refs/heads/{HISTORY_BRANCH}", commit_sha],
        cwd=repo_root,
        check=True,
    )
    logger.info(f"Created orphan branch '{HISTORY_BRANCH}'")


def _commit_file_to_branch(repo_root, rel_path, content, message):
    """
    Write *content* to *rel_path* on the history branch using a temporary
    git worktree so the current working tree is never touched.
    """
    _ensure_history_branch(repo_root)

    worktree_dir = tempfile.mkdtemp(prefix="waneye_history_")
    try:
        subprocess.run(
            ["git", "worktree", "add", worktree_dir, HISTORY_BRANCH],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )

        full_path = Path(worktree_dir) / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

        subprocess.run(["git", "add", rel_path], cwd=worktree_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=worktree_dir,
            check=True,
            capture_output=True,
        )

    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if exc.stderr else str(exc)
        raise RuntimeError(f"Git error while saving history: {stderr}") from exc
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree_dir],
            cwd=repo_root,
            capture_output=True,
        )
        shutil.rmtree(worktree_dir, ignore_errors=True)
