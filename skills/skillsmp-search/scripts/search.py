#!/usr/bin/env python3
"""Search the SkillsMP marketplace (https://skillsmp.com) from the command line.

The API key is read from the SKILLSMP_API_KEY environment variable or, if that
is not set, from the file ~/.config/skillsmp/key. Uses only the Python standard
library, so it works anywhere Python 3 is installed.

Examples:
    python search.py "SEO"
    python search.py "automation" --occupation software-developers --sort recent
    python search.py "SQL" --category data-ai --limit 5 --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://skillsmp.com/api/v1/skills/search"
KEY_FILE = Path.home() / ".config" / "skillsmp" / "key"


def load_api_key() -> str | None:
    key = os.environ.get("SKILLSMP_API_KEY", "").strip()
    if key:
        return key
    try:
        return KEY_FILE.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def build_params(args: argparse.Namespace) -> dict[str, str]:
    params: dict[str, str] = {"q": args.query}
    if args.page:
        params["page"] = str(args.page)
    if args.limit:
        params["limit"] = str(args.limit)
    if args.sort:
        params["sortBy"] = args.sort
    if args.category:
        params["category"] = args.category
    if args.occupation:
        params["occupation"] = args.occupation
    if args.language:
        params["language"] = args.language
    return params


def search(args: argparse.Namespace, api_key: str) -> tuple[dict, dict]:
    """Return (parsed_json_body, response_headers). Raises on network failure."""
    url = f"{API_URL}?{urllib.parse.urlencode(build_params(args))}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            headers = dict(resp.headers)
            body = json.loads(resp.read().decode("utf-8"))
            return body, headers
    except urllib.error.HTTPError as exc:  # 4xx / 5xx still carry a JSON body
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw), dict(exc.headers)
        except json.JSONDecodeError:
            return {"success": False, "error": {"code": str(exc.code), "message": raw}}, dict(exc.headers)


def pick(item: dict, *keys: str):
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return None


def print_human(body: dict, headers: dict) -> None:
    if not body.get("success", True) or "error" in body:
        err = body.get("error", {})
        print(f"Error {err.get('code', '?')}: {err.get('message', 'unknown error')}", file=sys.stderr)
        return

    # Results live at data.skills; fall back to other common shapes defensively.
    results = body.get("results") or body.get("data") or body.get("skills") or []
    pagination = {}
    if isinstance(results, dict):
        pagination = results.get("pagination") or {}
        results = (
            results.get("skills")
            or results.get("items")
            or results.get("results")
            or []
        )

    if not results:
        print("No skills found. Try broader keywords or fewer filters.")
    else:
        for i, item in enumerate(results, 1):
            name = pick(item, "name", "title", "slug") or "(unnamed)"
            author = pick(item, "author", "creator", "owner")
            desc = pick(item, "description", "summary", "tagline") or ""
            lang = pick(item, "contentLanguage", "language")
            stars = pick(item, "stars", "starCount", "stargazers")
            url = pick(item, "skillUrl", "url", "link", "githubUrl", "html_url")
            header = f"{i}. {name}"
            if author:
                header += f" — {author}"
            if stars is not None:
                header += f"  ⭐ {stars}"
            if lang:
                header += f"  [{lang}]"
            print(header)
            if desc:
                print(f"   {desc.strip()[:220]}")
            if url:
                print(f"   {url}")

    if pagination:
        page = pagination.get("page")
        total_pages = pagination.get("totalPages")
        total = pagination.get("total")
        bits = []
        if page and total_pages:
            bits.append(f"page {page}/{total_pages}")
        if total is not None:
            approx = "" if pagination.get("totalIsExact", True) else "~"
            bits.append(f"{approx}{total} total")
        if pagination.get("hasNext"):
            bits.append("more available (use --page)")
        if bits:
            print(f"\n[{' · '.join(bits)}]")

    remaining = headers.get("X-RateLimit-Daily-Remaining")
    if remaining is not None:
        print(f"[quota] {remaining} requests left today")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Search the SkillsMP marketplace.")
    parser.add_argument("query", help="Search keywords (the 'q' parameter).")
    parser.add_argument("--page", type=int, help="Page number (default 1).")
    parser.add_argument("--limit", type=int, help="Items per page (max 50).")
    parser.add_argument("--sort", choices=["stars", "recent"], help="Sort order.")
    parser.add_argument("--category", help="Category slug, e.g. data-ai, devops.")
    parser.add_argument("--occupation", help="SOC occupation slug, e.g. software-developers.")
    parser.add_argument("--language", help="Content language ISO code, e.g. en, zh, ja.")
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response.")
    args = parser.parse_args(argv)

    # Windows consoles default to cp1252 and choke on non-ASCII skill content.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    api_key = load_api_key()
    if not api_key:
        print(
            "Missing API key. Set SKILLSMP_API_KEY or save the key in "
            f"{KEY_FILE} (get one at https://skillsmp.com).",
            file=sys.stderr,
        )
        return 2

    body, headers = search(args, api_key)
    if args.json:
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        print_human(body, headers)
    return 0 if body.get("success", True) and "error" not in body else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
