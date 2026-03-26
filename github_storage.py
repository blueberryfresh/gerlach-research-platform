"""
GitHub Storage Backend
Persists research data to a private GitHub repository so data survives
Streamlit Cloud redeploys (which wipe the local filesystem).

Usage:
  - save() methods in data_models call get_storage().write(...)
  - sync_from_github(DATA_DIR) is called once at app startup to restore data
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class GitHubStorage:
    """Store research data files in a private GitHub repository."""

    def __init__(self):
        if HAS_STREAMLIT and hasattr(st, "secrets"):
            self.token = st.secrets.get("GITHUB_DATA_TOKEN", "")
            self.owner = st.secrets.get("GITHUB_DATA_OWNER", "")
            self.repo  = st.secrets.get("GITHUB_DATA_REPO", "")
        else:
            self.token = os.environ.get("GITHUB_DATA_TOKEN", "")
            self.owner = os.environ.get("GITHUB_DATA_OWNER", "")
            self.repo  = os.environ.get("GITHUB_DATA_REPO", "")

        self.enabled = bool(self.token and self.owner and self.repo)
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        )

    def _get_sha(self, path: str) -> Optional[str]:
        """Return the SHA of an existing file, needed to update it."""
        try:
            r = requests.get(
                f"{self.base_url}/{path}", headers=self.headers, timeout=10
            )
            if r.status_code == 200:
                return r.json().get("sha")
        except Exception as e:
            logger.debug(f"GitHub SHA lookup failed for {path}: {e}")
        return None

    def write(self, path: str, data: dict) -> bool:
        """Create or update a JSON file in GitHub."""
        if not self.enabled:
            return False
        try:
            content = base64.b64encode(
                json.dumps(data, indent=2).encode()
            ).decode()
            payload = {"message": f"data: {path}", "content": content}
            sha = self._get_sha(path)
            if sha:
                payload["sha"] = sha
            r = requests.put(
                f"{self.base_url}/{path}",
                json=payload,
                headers=self.headers,
                timeout=15,
            )
            return r.status_code in (200, 201)
        except Exception as e:
            logger.error(f"GitHub write failed for {path}: {e}")
            return False

    def write_text(self, path: str, text: str) -> bool:
        """Create or update a plain-text (.md / .html) file in GitHub."""
        if not self.enabled:
            return False
        try:
            content = base64.b64encode(text.encode()).decode()
            payload = {"message": f"data: {path}", "content": content}
            sha = self._get_sha(path)
            if sha:
                payload["sha"] = sha
            r = requests.put(
                f"{self.base_url}/{path}",
                json=payload,
                headers=self.headers,
                timeout=15,
            )
            return r.status_code in (200, 201)
        except Exception as e:
            logger.error(f"GitHub write_text failed for {path}: {e}")
            return False

    def read_raw(self, path: str) -> Optional[str]:
        """Return the decoded text content of a GitHub file, or None."""
        try:
            r = requests.get(
                f"{self.base_url}/{path}", headers=self.headers, timeout=10
            )
            if r.status_code == 200:
                return base64.b64decode(r.json()["content"]).decode("utf-8")
        except Exception as e:
            logger.debug(f"GitHub read failed for {path}: {e}")
        return None

    def list_dir(self, directory: str) -> List[Dict]:
        """List items in a GitHub directory. Returns [{name, type, ...}, ...]."""
        try:
            r = requests.get(
                f"{self.base_url}/{directory}", headers=self.headers, timeout=10
            )
            if r.status_code == 200 and isinstance(r.json(), list):
                return r.json()
        except Exception as e:
            logger.debug(f"GitHub list failed for {directory}: {e}")
        return []


# ── Module-level singleton ────────────────────────────────────────────────────

_storage: Optional[GitHubStorage] = None


def get_storage() -> GitHubStorage:
    global _storage
    if _storage is None:
        _storage = GitHubStorage()
    return _storage


def sync_from_github(data_dir: Path) -> int:
    """
    Pull all GitHub data files to local filesystem (runs once at app startup).
    Only downloads files not already present locally.
    Returns the number of files synced.
    """
    storage = get_storage()
    if not storage.enabled:
        return 0

    synced = 0

    # JSON directories
    for directory in [
        "sessions", "assessments", "dialogues",
        "task_responses/noble", "task_responses/popcorn",
        "surveys", "reports", "api_logs",
    ]:
        for item in storage.list_dir(directory):
            if item.get("type") != "file" or not item["name"].endswith(".json"):
                continue
            local_path = data_dir / directory / item["name"]
            if local_path.exists():
                continue
            raw = storage.read_raw(f"{directory}/{item['name']}")
            if raw is not None:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(raw, encoding="utf-8")
                synced += 1

    # .md and .html report files
    for item in storage.list_dir("reports"):
        if item.get("type") != "file":
            continue
        if not item["name"].endswith((".md", ".html")):
            continue
        local_path = data_dir / "reports" / item["name"]
        if local_path.exists():
            continue
        raw = storage.read_raw(f"reports/{item['name']}")
        if raw is not None:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(raw, encoding="utf-8")
            synced += 1

    if synced:
        logger.info(f"Synced {synced} file(s) from GitHub to local filesystem")
    return synced
