#!/usr/bin/env python3
"""Search for AI skills on two sources at once: skills.sh and SkillsMP.

skills.sh (the directory behind Vercel's skills CLI) needs no key and lists
how many times each skill was installed. SkillsMP (https://skillsmp.com) needs an
API key, read from the SKILLSMP_API_KEY environment variable or, if that is not
set, from the file ~/.config/skillsmp/key. If the key is missing or one source
is down, the other still answers. Uses only the Python standard library, so it
works anywhere Python 3 is installed.

Examples:
    python search.py "readme"
    python search.py "SQL" --source skills.sh --owner anthropics
    python search.py "automation" --source skillsmp --occupation software-developers --sort recent
    python search.py "SQL" --category data-ai --limit 5 --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://skillsmp.com/api/v1/skills/search"
SKILLS_SH_URL = "https://skills.sh/api/search"
SKILLS_SH_PAGE = "https://skills.sh/"
KEY_FILE = Path.home() / ".config" / "skillsmp" / "key"
# Cloudflare in front of skillsmp.com answers default client agents (Python-urllib,
# curl) with a 403 "Just a moment..." challenge page, before the API runs. A
# descriptive agent passes, so identify the tool instead of using the default.
USER_AGENT = "skillsmp-search/1.0 (Claude Code skill; +https://github.com/FFloriani/skills)"

SECTION_TITLES = {
    "skills.sh": "skills.sh (installs = how many times the skill was installed)",
    "skillsmp": "SkillsMP (stars = stars of the whole GitHub repo, not of the skill)",
}
# skills.sh "source" is owner/repo for GitHub skills; other hosts use other shapes.
_GITHUB_SOURCE = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+")

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b.?")
_stripped = 0


def clean(value) -> str:
    """Strip terminal escapes and control/invisible characters from API text.

    Marketplace fields are written by third parties: an escape sequence can
    rewrite what the terminal shows, and invisible Unicode (tag characters,
    zero-width, bidi) can smuggle instructions to a model reading the output.
    """
    global _stripped
    raw = str(value)
    kept = "".join(
        ch for ch in _ANSI.sub("", raw)
        if ch in "\n\t" or unicodedata.category(ch) not in ("Cc", "Cf", "Co", "Cn")
    )
    _stripped += len(raw) - len(kept)
    return kept


def clean_obj(obj):
    if isinstance(obj, str):
        return clean(obj)
    if isinstance(obj, list):
        return [clean_obj(v) for v in obj]
    if isinstance(obj, dict):
        return {clean(k): clean_obj(v) for k, v in obj.items()}
    return obj


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


def non_json_error(host: str, status: int, headers, raw: str) -> dict:
    """Short error for an HTTP error whose body is not JSON (usually an HTML page)."""
    if headers.get("cf-mitigated") == "challenge" or "Just a moment" in raw[:2000]:
        return {
            "code": "CLOUDFLARE_CHALLENGE",
            "message": (
                f"HTTP {status}: {host} answered with a Cloudflare challenge page instead of JSON, "
                f"so the request never reached the API. Retry later; if it persists {host} "
                "changed its bot rules, so search in a browser instead."
            ),
        }
    return {"code": str(status), "message": raw[:200]}


def search_skillsmp(args: argparse.Namespace, api_key: str) -> tuple[dict, dict]:
    """Query SkillsMP. Return (parsed_json_body, response_headers). Raises on network failure."""
    url = f"{API_URL}?{urllib.parse.urlencode(build_params(args))}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {api_key}", "User-Agent": USER_AGENT}
    )
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
            return {"success": False, "error": non_json_error("skillsmp.com", exc.code, exc.headers, raw)}, dict(exc.headers)


def search_skills_sh(args: argparse.Namespace) -> tuple[dict, dict]:
    """Query skills.sh (no key). Return (parsed_json_body, response_headers). Raises on network failure.

    Only q, limit and owner exist there; page and the SkillsMP filters are ignored by the server.
    """
    params = {"q": args.query, "limit": str(args.limit or 10)}
    if args.owner:
        params["owner"] = args.owner
    url = f"{SKILLS_SH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            return {"success": False, "error": non_json_error("skills.sh", exc.code, exc.headers, raw)}, dict(exc.headers)
        if isinstance(body, dict) and isinstance(body.get("error"), str):
            # skills.sh errors look like {"error": "Query must be at least 2 characters"}
            body = {"success": False, "error": {"code": str(exc.code), "message": body["error"]}}
        return body, dict(exc.headers)


def attempt(fn, *fn_args) -> tuple[dict, dict]:
    """Run one source. A network failure or odd reply there must not take the other source down."""
    try:
        body, headers = fn(*fn_args)
    except (OSError, ValueError) as exc:  # URLError, timeouts and bad JSON all land here
        reason = getattr(exc, "reason", exc)
        return {"success": False, "error": {"code": "NETWORK", "message": str(reason)}}, {}
    if not isinstance(body, dict):
        return {"success": False, "error": {"code": "BAD_RESPONSE", "message": "unexpected response shape"}}, headers
    return body, headers


def failed(body: dict) -> bool:
    return not body.get("success", True) or "error" in body


def pick(item: dict, *keys: str):
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return None


def print_error(label: str, body: dict) -> None:
    err = body.get("error", {})
    if not isinstance(err, dict):
        err = {"message": err}
    print(
        f"[{label}] Error {clean(err.get('code', '?'))}: {clean(err.get('message', 'unknown error'))}",
        file=sys.stderr,
    )


def print_skills_sh(body: dict, headers: dict) -> None:
    skills = body.get("skills") or []
    if not skills:
        print("No skills found. Try broader keywords or a different --owner.")
        return
    for i, item in enumerate(skills, 1):
        if not isinstance(item, dict):
            continue
        name = clean(pick(item, "name", "skillId") or "(unnamed)")
        source = clean(item.get("source") or "")
        installs = item.get("installs")
        header = f"{i}. {name}"
        if source:
            header += f" — {source}"
        if isinstance(installs, int) and installs > 0:
            header += f"  {installs:,} installs"
        print(header)
        slug = clean(item.get("id") or "")
        if slug:
            print(f"   {SKILLS_SH_PAGE}{urllib.parse.quote(slug, safe='/')}")
        if _GITHUB_SOURCE.fullmatch(source):
            print(f"   repo: https://github.com/{source}")


def print_skillsmp(body: dict, headers: dict) -> None:
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
            name = clean(pick(item, "name", "title", "slug") or "(unnamed)")
            author = clean(pick(item, "author", "creator", "owner") or "")
            desc = clean(pick(item, "description", "summary", "tagline") or "")
            lang = clean(pick(item, "contentLanguage", "language") or "")
            stars = pick(item, "stars", "starCount", "stargazers")
            stars = clean(stars) if stars is not None else None
            url = clean(pick(item, "skillUrl", "url", "link", "githubUrl", "html_url") or "")
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
    parser = argparse.ArgumentParser(description="Search AI skills on skills.sh and SkillsMP.")
    parser.add_argument("query", help="Search keywords (at least 2 characters).")
    parser.add_argument(
        "--source", choices=["all", "skills.sh", "skillsmp"], default="all",
        help="Where to search (default: all). skills.sh needs no key; skillsmp needs an API key.",
    )
    parser.add_argument("--limit", type=int, default=10, help="Items per source (default 10, max 50).")
    parser.add_argument("--owner", help="skills.sh only: GitHub owner of the repo, e.g. anthropics.")
    parser.add_argument("--page", type=int, help="SkillsMP only: page number (default 1).")
    parser.add_argument("--sort", choices=["stars", "recent"], help="SkillsMP only: sort order.")
    parser.add_argument("--category", help="SkillsMP only: category slug, e.g. data-ai, devops.")
    parser.add_argument("--occupation", help="SkillsMP only: SOC occupation slug, e.g. software-developers.")
    parser.add_argument("--language", help="SkillsMP only: content language ISO code, e.g. en, zh, ja.")
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response(s).")
    args = parser.parse_args(argv)

    # Windows consoles default to cp1252 and choke on non-ASCII skill content.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    results: dict[str, tuple[dict, dict]] = {}
    if args.source in ("all", "skills.sh"):
        results["skills.sh"] = attempt(search_skills_sh, args)
    if args.source in ("all", "skillsmp"):
        api_key = load_api_key()
        if api_key:
            results["skillsmp"] = attempt(search_skillsmp, args, api_key)
        elif args.source == "skillsmp":
            print(
                "Missing API key. Set SKILLSMP_API_KEY or save the key in "
                f"{KEY_FILE} (get one at https://skillsmp.com).",
                file=sys.stderr,
            )
            return 2
        else:
            print(
                "[skillsmp] skipped: no API key (set SKILLSMP_API_KEY or save it in "
                f"{KEY_FILE}). Showing skills.sh only.",
                file=sys.stderr,
            )
    if args.source == "all" and (args.page or args.sort or args.category or args.occupation or args.language):
        print(
            "[note] --page, --sort, --category, --occupation and --language apply to SkillsMP only; "
            "skills.sh ignores them.",
            file=sys.stderr,
        )

    if args.json:
        payload = {name: clean_obj(body) for name, (body, _) in results.items()}
        shown = payload if args.source == "all" else next(iter(payload.values()))
        print(json.dumps(shown, indent=2, ensure_ascii=False))
    else:
        first = True
        for name, (body, headers) in results.items():
            if failed(body):
                print_error(name, body)
                continue
            if args.source == "all":
                print(("" if first else "\n") + f"## {SECTION_TITLES[name]}")
            first = False
            (print_skills_sh if name == "skills.sh" else print_skillsmp)(body, headers)
    if _stripped:
        print(
            f"[warning] removed {_stripped} control/hidden characters from marketplace text; "
            "a listing carrying hidden characters is suspicious.",
            file=sys.stderr,
        )
    return 0 if any(not failed(body) for body, _ in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
