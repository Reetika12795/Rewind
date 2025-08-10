"""Lightweight Wikipedia extraction helper.

Performs:
1. Search (opensearch API)
2. Fetch page summary + first paragraphs (REST API)

We keep dependencies minimal: use requests only (already in project deps).
"""
from __future__ import annotations

import requests
from typing import Optional, Dict, Any

WIKI_API = "https://en.wikipedia.org/w/api.php"
REST_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"

def wiki_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    params = {
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "namespace": 0,
        "format": "json"
    }
    r = requests.get(WIKI_API, params=params, timeout=8)
    r.raise_for_status()
    data = r.json()
    # data = [searchTerm, titles[], descriptions[], urls[]]
    results = []
    if len(data) >= 4:
        for title, desc, url in zip(data[1], data[2], data[3]):
            results.append({"title": title, "description": desc, "url": url})
    return results


def wiki_summary(title: str) -> Optional[dict[str, Any]]:
    r = requests.get(REST_SUMMARY.format(requests.utils.quote(title)), timeout=8, headers={"accept": "application/json"})
    if r.status_code != 200:
        return None
    js = r.json()
    return {
        "title": js.get("title"),
        "extract": js.get("extract"),
        "description": js.get("description"),
        "content_urls": js.get("content_urls", {}).get("desktop", {}).get("page"),
    }


def contextual_wiki_lookup(location: str, target_year: int, extra_terms: list[str] | None = None) -> dict[str, Any]:
    """Try a few queries combining location + year + style hints; return consolidated info."""
    queries = [f"{location} {target_year}", f"History of {location}"]
    if extra_terms:
        for t in extra_terms[:3]:
            queries.append(f"{location} {t}")

    collected = []
    seen_titles = set()
    for q in queries:
        try:
            search_hits = wiki_search(q, limit=2)
        except Exception:
            continue
        for hit in search_hits:
            if hit["title"] in seen_titles:
                continue
            seen_titles.add(hit["title"])
            summary = wiki_summary(hit["title"]) or {}
            collected.append({
                "query": q,
                "title": hit["title"],
                "short_description": hit.get("description"),
                "summary": summary.get("extract"),
                "url": hit.get("url")
            })
    return {"results": collected[:5]}

__all__ = ["contextual_wiki_lookup"]
