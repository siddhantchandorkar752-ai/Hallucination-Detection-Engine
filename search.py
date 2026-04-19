from tavily import TavilyClient
from config import config
from logger import logger

client = TavilyClient(api_key=config.TAVILY_API_KEY)

TRUSTED = [".gov", ".edu", ".org", "wikipedia", "reuters", "bbc", "nature", "who.int", "britannica", "nasa"]

def _score(result: dict) -> int:
    url = result.get("url", "").lower()
    score = 50
    for d in TRUSTED:
        if d in url:
            score += 20
            break
    score += min(30, len(result.get("content", "")) // 100)
    return score

def search_evidence(claim: str) -> tuple[str, list]:
    try:
        response = client.search(query=claim, search_depth="advanced", max_results=5)
        results = response.get("results", [])
        ranked = sorted(results, key=_score, reverse=True)
        evidence = " ".join([r.get("content", "") for r in ranked])
        logger.info(f"Found {len(ranked)} results for: {claim[:60]}")
        return evidence[:4000], ranked
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "", []
