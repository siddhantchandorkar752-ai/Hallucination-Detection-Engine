import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)


def _call_llm(messages: list, max_tokens: int = 1024, json_mode: bool = True) -> str:
    kwargs = {
        "model": config.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()


def _parse_json(raw: str) -> dict | list:
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(raw)


def extract_claims(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    try:
        raw = _call_llm([
            {"role": "system", "content": "Extract factual claims. Return JSON with key 'claims' as array of strings. Copy claims EXACTLY as written. Do NOT fix or correct anything."},
            {"role": "user", "content": f"Split EVERY sentence into INDIVIDUAL atomic facts. Each distinct fact = one separate item. Never merge. Minimum 3-4 claims per sentence:\n\n{text.strip()}\n\nReturn: {{\"claims\": [\"exact claim 1\", \"exact claim 2\"]}}"}
        ], max_tokens=2048)
        data = _parse_json(raw)
        if isinstance(data, dict):
            claims = data.get("claims", data.get("facts", data.get("statements", [])))
        elif isinstance(data, list):
            claims = data
        else:
            claims = []
        claims = [str(c).strip() for c in claims if str(c).strip() and len(str(c).strip()) > 5]
        logger.info(f"Extracted {len(claims)} claims.")
        return claims[:config.MAX_CLAIMS_PER_TEXT]
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return []


def _generate_fallback_query(claim: str) -> str:
    try:
        raw = _call_llm([
            {"role": "system", "content": "Generate a better search query. Return JSON: {\"query\": \"search query\"}"},
            {"role": "user", "content": f"Generate a factual search query to verify: {claim}"}
        ], max_tokens=100)
        data = _parse_json(raw)
        return data.get("query", claim)
    except:
        words = claim.split()[:6]
        return " ".join(words)


def _rank_sources(results: list) -> list:
    trusted_domains = [".gov", ".edu", ".org", "wikipedia", "reuters", "bbc", "nature", "who.int", "nasa"]
    def score(r):
        url = r.get("url", "").lower()
        base = 50
        for d in trusted_domains:
            if d in url:
                base += 20
                break
        return base
    return sorted(results, key=score, reverse=True)


def search_with_retry(claim: str, search_fn) -> tuple[str, list]:
    try:
        results, evidence = search_fn(claim)
        if not evidence.strip():
            new_query = _generate_fallback_query(claim)
            logger.info(f"Retrying search with: {new_query}")
            results, evidence = search_fn(new_query)
        return evidence, results
    except Exception as e:
        logger.error(f"Search retry failed: {e}")
        return "", []


def verify_claim(claim: str, evidence: str, mode: str = "General") -> dict:
    mode_instructions = {
        "General": "You are a General Fact-Checker with broad knowledge.",
        "Medical": "You are a Medical Expert Fact-Checker. Apply clinical precision.",
        "Legal": "You are a Legal Expert Fact-Checker. Apply strict legal standards.",
        "Scientific": "You are a Scientific Fact-Checker. Apply empirical rigor.",
    }
    mode_prompt = mode_instructions.get(mode, mode_instructions["General"])

    prompt = f"""{mode_prompt}

Verify this claim using NLI (Natural Language Inference):
1. ENTAILMENT: Evidence supports the claim → TRUE
2. CONTRADICTION: Evidence or knowledge contradicts the claim → FALSE  
3. NEUTRAL: Cannot determine → UNCERTAIN

CLAIM: {claim}

EVIDENCE: {evidence if evidence and evidence.strip() else "No web evidence. Use your comprehensive knowledge."}

STRICT RULES:
- Physically impossible claims (cars flying, liquid nitrogen fuel) → FALSE
- Wrong historical dates/names/statistics → FALSE
- Claims contradicting well-known facts → FALSE
- Only TRUE if verifiably correct

Return ONLY JSON:
{{"verdict": "TRUE|FALSE|UNCERTAIN", "confidence": 0.99, "explanation": "detailed reason", "nli_label": "CONTRADICTION|ENTAILMENT|NEUTRAL", "counter_evidence": "what the correct fact is"}}"""

    try:
        raw = _call_llm([
            {"role": "system", "content": "You are a fact-checker. Return only valid JSON with keys: verdict, confidence, explanation, nli_label, counter_evidence."},
            {"role": "user", "content": prompt}
        ], max_tokens=512)
        data = _parse_json(raw)
        verdict = str(data.get("verdict", "UNCERTAIN")).upper().strip()
        if verdict not in ("TRUE", "FALSE", "UNCERTAIN"):
            verdict = "UNCERTAIN"
        result = {
            "verdict": verdict,
            "confidence": min(1.0, max(0.0, float(data.get("confidence", 0.5)))),
            "explanation": str(data.get("explanation", "No explanation.")),
            "nli_label": str(data.get("nli_label", "NEUTRAL")),
            "counter_evidence": str(data.get("counter_evidence", "")),
        }
        logger.info(f"{result['verdict']} ({result['confidence']:.0%}) [{result['nli_label']}] — {claim[:60]}")
        return result
    except Exception as e:
        logger.error(f"Verify failed: {e}")
        return {"verdict": "UNCERTAIN", "confidence": 0.0, "explanation": str(e), "nli_label": "NEUTRAL", "counter_evidence": ""}


def correct_claim(claim: str, evidence: str) -> str:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Rewrite false claims as correct factual statements. Return ONLY the corrected statement. No prefix, no quotes."},
                {"role": "user", "content": f"False claim: {claim}\nEvidence: {evidence or 'Use your knowledge.'}\nCorrected:"}
            ],
            temperature=0.0,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Correction failed: {e}")
        return claim
