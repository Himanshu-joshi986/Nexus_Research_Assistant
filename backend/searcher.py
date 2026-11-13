import trafilatura
from tavily import TavilyClient
from config import TAVILY_API_KEY, RECENCY_DAYS


def search_web(topic: str, depth: str, recency: str) -> list[dict]:
    """Search the web using Tavily API."""
    from config import DEPTH_CONFIG
    max_results = DEPTH_CONFIG[depth]["max_results"]
    days = RECENCY_DAYS[recency]

    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(
        query=topic,
        search_depth="advanced" if depth == "Advanced" else "basic",
        max_results=max_results,
        days=days,
        include_raw_content=False,
    )
    return response.get("results", [])


def scrape_url(url: str) -> str:
    """Scrape article text from a URL using Trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        return text or ""
    except Exception:
        return ""


def scrape_all(results: list[dict]) -> list[dict]:
    """Scrape text for each search result."""
    enriched = []
    for r in results:
        url = r.get("url", "")
        text = scrape_url(url)
        if not text:
            text = r.get("content", "") or r.get("raw_content", "")
        if text and len(text) > 100:
            enriched.append({
                "url": url,
                "title": r.get("title", ""),
                "text": text,
                "score": r.get("score", 0),
            })
    return enriched

