#!/usr/bin/env python3
"""
Upload README.md to Confluence (personal space at zetes.atlassian.net).

Uses Confluence Cloud REST API v2. Requires:
  - CONFLUENCE_BASE_URL (default: https://zetes.atlassian.net)
  - CONFLUENCE_EMAIL (your Atlassian account email)
  - CONFLUENCE_API_TOKEN (create at https://id.atlassian.com/manage-profile/security/api-tokens)
  - Optional: CONFLUENCE_SPACE_ID — if not set, script uses HOMEPAGE_ID to resolve space from existing page.

Your personal space URL was:
  https://zetes.atlassian.net/wiki/spaces/~7120209703f1ace64744f9866e1da808024940/overview?homepageId=1547698850

So we use homepageId=1547698850 to get the page, then take spaceId from it.
"""

import os
import re
import sys
from pathlib import Path

# Load .env from project root if present
_project_root = Path(__file__).resolve().parent.parent
_env_file = _project_root / ".env"
if _env_file.is_file():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

# -----------------------------------------------------------------------------
# Config (from env or .env)
# -----------------------------------------------------------------------------
CONFLUENCE_BASE = os.environ.get("CONFLUENCE_BASE_URL", "https://zetes.atlassian.net").rstrip("/")
CONFLUENCE_EMAIL = os.environ.get("CONFLUENCE_EMAIL", "")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN", "")
# Use an existing page in your personal space to get spaceId (e.g. homepage)
HOMEPAGE_ID = os.environ.get("CONFLUENCE_HOMEPAGE_ID", "1547698850")
PAGE_TITLE = os.environ.get("CONFLUENCE_PAGE_TITLE", "Vendor-Independent PKI Model — Proposal for PKIC")
_source = os.environ.get("CONFLUENCE_SOURCE_FILE", "README.md")
README_PATH = Path(_source) if Path(_source).is_absolute() else _project_root / _source


def md_to_storage_simple(md: str) -> str:
    """Convert Markdown to HTML for Confluence storage (storage format accepts HTML-like content)."""
    try:
        import markdown
        html = markdown.markdown(
            md,
            extensions=["tables", "fenced_code", "nl2br"],
            output_format="html",
        )
        return html
    except ImportError:
        # Minimal fallback: no markdown lib — convert basics by hand
        html = md
        for level in range(1, 5):
            html = re.sub(rf"^#{level}\s+(.+)$", f"<h{level}>\\1</h{level}>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", html)
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
        html = re.sub(r"^---\s*$", "<hr/>", html, flags=re.MULTILINE)
        html = re.sub(r"\n\n+", "</p><p>", html)
        if not html.strip().startswith("<"):
            html = f"<p>{html}</p>"
        return html


def main():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print(
            "Set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN (create token at https://id.atlassian.com/manage-profile/security/api-tokens)",
            file=sys.stderr,
        )
        sys.exit(1)

    if not README_PATH.is_file():
        print(f"README not found: {README_PATH}", file=sys.stderr)
        sys.exit(1)

    md_content = README_PATH.read_text(encoding="utf-8")
    body_value = md_to_storage_simple(md_content)

    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # 1) Get spaceId from existing homepage in personal space
    print(f"Resolving space from page id {HOMEPAGE_ID}...")
    r = requests.get(
        f"{CONFLUENCE_BASE}/wiki/api/v2/pages/{HOMEPAGE_ID}",
        auth=auth,
        headers=headers,
    )
    if r.status_code != 200:
        print(f"Failed to get page: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    page_data = r.json()
    space_id = page_data.get("spaceId")
    if not space_id:
        print("Could not get spaceId from page response", file=sys.stderr)
        sys.exit(1)
    print(f"Space ID: {space_id}")

    # 2) Create new page in that space
    payload = {
        "spaceId": space_id,
        "status": "current",
        "title": PAGE_TITLE,
        "body": {
            "representation": "storage",
            "value": body_value,
        },
    }
    r = requests.post(
        f"{CONFLUENCE_BASE}/wiki/api/v2/pages",
        auth=auth,
        headers=headers,
        json=payload,
    )
    if r.status_code not in (200, 201):
        print(f"Failed to create page: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    created = r.json()
    page_id = created.get("id")
    links = created.get("_links", {})
    webui = links.get("webui", "")
    if webui and not webui.startswith("http"):
        webui = f"{CONFLUENCE_BASE}/wiki{webui}"
    print(f"Page created: id={page_id}")
    if webui:
        print(f"View at: {webui}")


if __name__ == "__main__":
    main()
