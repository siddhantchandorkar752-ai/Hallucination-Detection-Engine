import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)


def _llm(messages: list, max_tokens: int = 1024, json_mode: bool = True) -> str:
    kwargs = {
        "model": config.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return client.chat.completions.create(**kwargs).choices[0].message.content.strip()


def _parse(raw: str) -> dict | list:
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(raw)


def extract_claims(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    try:
        raw = _llm([
            {"role": "system", "content": (
                "You are an atomic fact extractor. "
                "Split text into individual verifiable facts. "
                "Each fact = one array item. "
                "NEVER merge multiple facts into one item. "
                "Copy facts EXACTLY as written — do NOT fix or correct. "
                "Return JSON: {\"claims\": [\"fact1\", \"fact2\", ...]}"
            )},
            {"role": "user", "content": (
                f"Extract EVERY atomic fact from this text. "
                f"Each sentence should produce 3-5 separate claims.\n\n"
                f"TEXT:\n{text.strip()}\n\n"
                f"Example: 'Einstein born in 1900 in France won Nobel 1921' → "
                f"[\"Einstein was born in 1900\", \"Einstein was born in France\", \"Einstein won the Nobel Prize in 1921\"]\n\n"
                f"Return ONLY: {{\"claims\": [\"claim1\", \"claim2\", ...]}}"
            )}
        ], max_tokens=2048)

        data = _parse(raw)
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


def _fallback_query(claim: str) -> str:
    try:
        raw = _llm([
            {"role": "system", "content": "Generate search query. Return JSON: {\"query\": \"search terms\"}"},
            {"role": "user", "content": f"Search query to verify: {claim}"}
        ], max_tokens=100)
        return _parse(raw).get("query", claim)
    except:
        return " ".join(claim.split()[:6])


def verify_claim(claim: str, evidence: str, mode: str = "General") -> dict:
    mode_map = {
        "General": "You are a General Fact-Checker with broad world knowledge.",
        "Medical": "You are a Medical Expert Fact-Checker. Apply clinical precision.",
        "Legal": "You are a Legal Expert Fact-Checker. Apply strict legal standards.",
        "Scientific": "You are a Scientific Fact-Checker. Apply empirical rigor.",
    }
    system = mode_map.get(mode, mode_map["General"])

    try:
        raw = _llm([
            {"role": "system", "content": (
                f"{system} "
                "Use NLI reasoning: ENTAILMENT=TRUE, CONTRADICTION=FALSE, NEUTRAL=UNCERTAIN. "
                "Return JSON with keys: verdict, confidence, explanation, nli_label, counter_evidence."
            )},
            {"role": "user", "content": (
                f"Fact-check this claim:\n\nCLAIM: {claim}\n\n"
                f"EVIDENCE: {evidence if evidence and evidence.strip() else 'No web evidence. Use your knowledge.'}\n\n"
                "RULES:\n"
                "- Physically impossible = FALSE (cars flying, fusion reactor in consumer car, Nobel for user manual)\n"
                "- Wrong dates/names/stats = FALSE\n"
                "- Contradicts known facts = FALSE\n"
                "- Only TRUE if verifiably correct\n\n"
                "Return ONLY: {\"verdict\": \"FALSE\", \"confidence\": 0.99, "
                "\"explanation\": \"reason\", \"nli_label\": \"CONTRADICTION\", "
                "\"counter_evidence\": \"correct fact\"}"
            )}
        ], max_tokens=512)

        data = _parse(raw)
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
                {"role": "system", "content": "Rewrite the false claim as a correct factual statement. Return ONLY the corrected statement. No prefix, no quotes."},
                {"role": "user", "content": f"False claim: {claim}\nEvidence: {evidence or 'Use your knowledge.'}\nCorrected:"}
            ],
            temperature=0.0,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Correction failed: {e}")
        return claim
