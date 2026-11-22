from concurrent.futures import ThreadPoolExecutor

import trafilatura
from tavily import TavilyClient
from config import TAVILY_API_KEY, RECENCY_DAYS, DEPTH_CONFIG


def search_web(topic: str, depth: str, recency: str) -> list[dict]:
    """Search the web using Tavily API."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(
        query=topic,
        search_depth="advanced" if depth == "Advanced" else "basic",
        max_results=DEPTH_CONFIG[depth]["max_results"],
        days=RECENCY_DAYS[recency],
        include_raw_content=False,
    )
    return response.get("results", [])


def scrape_url(url: str) -> str:
    """Scrape article text from a URL using Trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        return trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
    except Exception:
        return ""


def scrape_all(results: list[dict]) -> list[dict]:
    """Scrape text for each search result (in parallel, order preserved)."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        texts = pool.map(scrape_url, [r.get("url", "") for r in results])

    enriched = []
    for r, text in zip(results, texts):
        text = text or r.get("content", "") or r.get("raw_content", "")
        if len(text) > 100:
            enriched.append({
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "text": text,
                "score": r.get("score", 0),
            })
    return enriched
