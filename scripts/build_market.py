#!/usr/bin/env python3
"""Build the class-toolkit market index.

Queries the GitHub Search API for repositories tagged with a topic (default:
``class-toolkit``) and writes a deterministic ``index.json`` consumed by the
ClassroomToolsMarket plugin.

The script intentionally depends on the Python standard library only, so the
GitHub Action can run it without installing anything.

Usage:
    GITHUB_TOKEN=... python scripts/build_market.py --out build/index.json

Exit codes:
    0  index written
    1  API / network / data error (the workflow then keeps the previous branch)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_ENDPOINT = "https://api.github.com/search/repositories"
USER_AGENT = "ClassroomToolsMarket-indexer/1.0"
MAX_RETRIES = 4


def log(message: str) -> None:
    print(f"[market] {message}", flush=True)


def request_json(url: str, token: str) -> dict:
    """GET a GitHub API URL with retries for rate limiting and 5xx errors."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    delay = 5
    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", "replace")
            if error.code in (403, 429) and attempt < MAX_RETRIES:
                wait = _retry_after(error, delay)
                log(f"rate limited ({error.code}), retrying in {wait}s")
                time.sleep(wait)
                delay *= 2
                continue
            raise RuntimeError(f"GitHub API {error.code}: {body[:300]}") from error
        except urllib.error.URLError as error:
            if attempt < MAX_RETRIES:
                log(f"network error ({error.reason}), retrying in {delay}s")
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"network error: {error.reason}") from error
    raise RuntimeError("GitHub API request failed")


def _retry_after(error: urllib.error.HTTPError, fallback: int) -> int:
    retry_after = error.headers.get("Retry-After")
    if retry_after and retry_after.isdigit():
        return max(1, int(retry_after))
    reset = error.headers.get("X-RateLimit-Reset")
    if reset and reset.isdigit():
        wait = int(reset) - int(time.time())
        if 0 < wait <= 300:
            return wait
    return fallback


def fetch_tools(topic: str, token: str, limit: int) -> list[dict]:
    query = urllib.parse.quote(f"topic:{topic}")
    tools: list[dict] = []
    page = 1

    while len(tools) < limit:
        per_page = min(100, limit - len(tools))
        url = (
            f"{API_ENDPOINT}?q={query}&sort=stars&order=desc"
            f"&per_page={per_page}&page={page}"
        )
        payload = request_json(url, token)
        items = payload.get("items") or []
        if not items:
            break

        for item in items:
            owner = (item.get("owner") or {}).get("login", "")
            tools.append(
                {
                    "full_name": item.get("full_name", ""),
                    "owner": owner,
                    "name": item.get("name", ""),
                    "description": item.get("description") or "",
                    "html_url": item.get("html_url", ""),
                    "homepage": item.get("homepage") or "",
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language") or "",
                    "topics": item.get("topics") or [],
                    "updated_at": item.get("updated_at", ""),
                    "default_branch": item.get("default_branch") or "main",
                }
            )

        if len(items) < per_page:
            break
        page += 1
        # Unauthenticated search allows about 10 requests/minute; pace the pages.
        time.sleep(1)

    tools = [tool for tool in tools if tool["full_name"] and tool["html_url"]]
    tools.sort(key=lambda tool: (-int(tool.get("stars") or 0), tool["full_name"]))
    return tools


def build_index(tools: list[dict], topic: str) -> dict:
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "topic": topic,
        "count": len(tools),
        "tools": tools,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="output index.json path")
    parser.add_argument(
        "--topic",
        default=os.environ.get("MARKET_TOPIC", "class-toolkit"),
        help="GitHub topic to aggregate (default: class-toolkit)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.environ.get("MARKET_LIMIT", "200")),
        help="maximum number of repositories to keep (default: 200)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub token (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="write an empty index instead of failing when no repository matches",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        log(f"fetching topic '{args.topic}' (limit {args.limit})")
        tools = fetch_tools(args.topic, args.token, max(1, args.limit))
        if not tools and not args.allow_empty:
            raise RuntimeError("no repositories matched the topic")

        index = build_index(tools, args.topic)
        out_dir = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(index, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        log(f"wrote {index['count']} tool(s) to {args.out}")
        return 0
    except (RuntimeError, OSError, ValueError) as error:
        log(f"error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
