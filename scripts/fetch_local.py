#!/usr/bin/env python3
"""Fetch all repositories of a topic into a local index.json.

Local companion to ``build_market.py``: it paginates through the GitHub
Search API (100 per page) instead of stopping at 200, so larger topics can be
inspected before the Action runs. The Search API itself caps one query at
1000 results.

Usage:
    python scripts/fetch_local.py
    python scripts/fetch_local.py --limit 1000 --out build/index.json
    GITHUB_TOKEN=... python scripts/fetch_local.py --topic class-toolkit

Without ``GITHUB_TOKEN`` the search API allows roughly 10 requests per minute,
so large fetches may pause while rate limiting is retried.

Exit codes:
    0  index written
    1  API / network / data error
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from build_market import build_index, fetch_tools, log

SEARCH_API_CAP = 1000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=os.path.join("build", "index.json"),
        help="output index.json path (default: build/index.json)",
    )
    parser.add_argument(
        "--topic",
        default=os.environ.get("MARKET_TOPIC", "class-toolkit"),
        help="GitHub topic to aggregate (default: class-toolkit)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.environ.get("MARKET_LIMIT", "0")),
        help="maximum repositories to keep; 0 means the API cap (1000)",
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

    limit = args.limit if args.limit > 0 else SEARCH_API_CAP
    if limit > SEARCH_API_CAP:
        log(f"limit {limit} exceeds the search API cap, using {SEARCH_API_CAP}")
        limit = SEARCH_API_CAP
    if not args.token:
        log("no GITHUB_TOKEN, unauthenticated search is rate limited")

    try:
        log(f"fetching topic '{args.topic}' locally (limit {limit})")
        tools = fetch_tools(args.topic, args.token, limit)
        if not tools and not args.allow_empty:
            raise RuntimeError("no repositories matched the topic")

        index = build_index(tools, args.topic)
        out_dir = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(index, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

        log(f"wrote {index['count']} tool(s) to {args.out}")
        if index["count"] >= limit:
            log("reached the requested limit; increase --limit for a wider scan")
        for tool in tools[:5]:
            log(f"  {tool['full_name']}  ★{tool['stars']}")
        return 0
    except (RuntimeError, OSError, ValueError) as error:
        log(f"error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
