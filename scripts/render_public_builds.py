#!/usr/bin/env python3
"""Render a small light/dark SVG showing the latest original public repositories."""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USERNAME = os.environ.get("PROFILE_USERNAME", "Harshit-Dhyani")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=pushed"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def fetch_repos() -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "harshbuilds-profile-renderer",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(API, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def short_date(value: str | None) -> str:
    if not value:
        return "unknown"
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def age_label(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    days = max(0, (datetime.now(timezone.utc) - dt).days)
    if days == 0:
        return "TODAY"
    if days == 1:
        return "1D AGO"
    if days < 100:
        return f"{days}D AGO"
    return f"{days // 30}MO AGO"


def trim(text: str | None, limit: int = 58) -> str:
    value = " ".join((text or "No public description yet.").split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def pick_repos(repos: list[dict]) -> list[dict]:
    selected = []
    for repo in repos:
        if repo.get("fork"):
            continue
        if repo.get("name", "").lower() == USERNAME.lower():
            continue
        if repo.get("size", 0) == 0:
            continue
        selected.append(repo)
    selected.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return selected[:4]


def render(repos: list[dict], *, dark: bool) -> str:
    bg = "#090B0D" if dark else "#F5F1E8"
    fg = "#F5F1E8" if dark else "#151719"
    muted = "#89929A" if dark else "#6E7479"
    line = "#272D32" if dark else "#D5D0C8"
    accent = "#FFB000" if dark else "#C87800"
    green = "#65D6A6" if dark else "#228B61"

    rows = []
    for idx, repo in enumerate(repos):
        y = 110 + idx * 58
        name = escape(repo.get("name") or "unknown")
        language = escape(repo.get("language") or "mixed")
        description = escape(trim(repo.get("description")))
        date = short_date(repo.get("pushed_at"))
        age = age_label(repo.get("pushed_at"))
        rows.append(
            f'''\n  <g transform="translate(60 {y})">\n'''
            f'''    <circle cx="0" cy="-5" r="4" fill="{green}"><animate attributeName="opacity" values="1;.35;1" dur="{1.6 + idx * .17:.2f}s" repeatCount="indefinite"/></circle>\n'''
            f'''    <text x="22" y="0" fill="{fg}" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700">{name}</text>\n'''
            f'''    <text x="250" y="0" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">{language}</text>\n'''
            f'''    <text x="390" y="0" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">{date}</text>\n'''
            f'''    <text x="560" y="0" fill="{accent}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">{age}</text>\n'''
            f'''    <text x="700" y="0" fill="{muted}" font-family="Arial, Helvetica, sans-serif" font-size="13">{description}</text>\n'''
            f'''    <line x1="0" y1="25" x2="1160" y2="25" stroke="{line}"/>\n'''
            f'''  </g>'''
        )

    while len(rows) < 4:
        idx = len(rows)
        y = 110 + idx * 58
        rows.append(
            f'''\n  <g transform="translate(60 {y})"><text x="22" y="0" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">waiting for another public build signal…</text><line x1="0" y1="25" x2="1160" y2="25" stroke="{line}"/></g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="330" viewBox="0 0 1280 330" role="img" aria-labelledby="title desc">\n  <title id="title">Latest public build signals</title>\n  <desc id="desc">Four recently pushed original public repositories for {escape(USERNAME)}.</desc>\n  <rect width="1280" height="330" fill="{bg}"/>\n  <path d="M30 30h48v3H33v45h-3z" fill="{accent}"/>\n  <text x="60" y="58" fill="{fg}" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700">LATEST PUBLIC BUILD SIGNALS</text>\n  <text x="1220" y="57" text-anchor="end" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" letter-spacing="1.5">SOURCE / GITHUB PUBLIC REPOS</text>\n  <text x="82" y="86" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">REPO</text>\n  <text x="310" y="86" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">LANGUAGE</text>\n  <text x="450" y="86" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">LAST PUSH</text>\n  <text x="620" y="86" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">AGE</text>\n  <text x="760" y="86" fill="{muted}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">PUBLIC DESCRIPTION</text>{''.join(rows)}\n</svg>\n'''


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    repos = pick_repos(fetch_repos())
    (ASSETS / "live-builds-dark.svg").write_text(render(repos, dark=True), encoding="utf-8")
    (ASSETS / "live-builds-light.svg").write_text(render(repos, dark=False), encoding="utf-8")
    print("Rendered:", ", ".join(repo.get("name", "unknown") for repo in repos))


if __name__ == "__main__":
    main()
