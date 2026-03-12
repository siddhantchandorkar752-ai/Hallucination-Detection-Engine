from tavily import TavilyClient
from config import config
from logger import logger

client = TavilyClient(api_key=config.TAVILY_API_KEY)

def search_evidence(claim: str) -> str:
    try:
        response = client.search(
            query=claim,
            search_depth=config.TAVILY_SEARCH_DEPTH,
            max_results=config.TAVILY_MAX_RESULTS,
        )
        results = response.get("results", [])
        evidence = " ".join([r.get("content", "") for r in results])
        logger.info(f"Evidence retrieved for: {claim[:60]}")
        return evidence[:3000]
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return ""
