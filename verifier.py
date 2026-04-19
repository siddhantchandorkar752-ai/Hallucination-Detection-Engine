import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)

EXTRACTION_SYSTEM = """You are an elite fact-extraction engine. Extract every verifiable factual claim.
Return ONLY a valid JSON array of strings. No markdown. No explanation.
NEVER return empty array if text has any facts."""

EXTRACTION_USER = """Extract every verifiable factual claim from this text as JSON array.

TEXT: {text}

Return ONLY JSON array like: ["claim 1", "claim 2", "claim 3"]"""

VERIFY_SYSTEM = """You are a world-class fact-checker with deep knowledge of history, science, technology, and current events.

CRITICAL RULES:
- Use BOTH the provided evidence AND your own knowledge to verify claims
- If a claim is clearly impossible or absurd (flying cars, liquid nitrogen fuel, Formula 1 won by a hatchback), mark FALSE
- If claim contradicts basic facts you know, mark FALSE even without evidence
- Be aggressive in detecting hallucinations — do not give benefit of doubt
- Confidence must reflect how certain you are

Return ONLY this JSON: {{"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.0-1.0, "explanation": "one sentence"}}"""

VERIFY_USER = """Fact-check this claim using evidence AND your knowledge.

CLAIM: {claim}

EVIDENCE FROM WEB: {evidence}

IMPORTANT: If the claim is physically impossible, historically wrong, or clearly absurd — mark it FALSE regardless of evidence.
Return ONLY JSON: {{"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.0-1.0, "explanation": "one sentence"}}"""


def extract_claims(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": EXTRACTION_USER.format(text=text.strip())}
            ],
            temperature=0.0,
            max_tokens=2048,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"`(?:json)?", "", raw).strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            lines = [l.strip().strip('"-,') for l in raw.split("\n") if l.strip().strip('"-,')]
            claims = [l for l in lines if len(l) > 10]
        else:
            claims = json.loads(raw[start:end])
        claims = [c.strip() for c in claims if isinstance(c, str) and len(c.strip()) > 5]
        logger.info(f"Extracted {len(claims)} claims.")
        return claims[:config.MAX_CLAIMS_PER_TEXT]
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return []


def verify_claim(claim: str, evidence: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": VERIFY_SYSTEM},
                {"role": "user", "content": VERIFY_USER.format(
                    claim=claim,
                    evidence=evidence if evidence else "No web evidence found. Use your own knowledge."
                )}
            ],
            temperature=0.0,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"`(?:json)?", "", raw).strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found")
        result = json.loads(raw[start:end])
        result["verdict"] = result.get("verdict", "UNCERTAIN").upper()
        if result["verdict"] not in ("TRUE", "FALSE", "UNCERTAIN"):
            result["verdict"] = "UNCERTAIN"
        result["confidence"] = float(result.get("confidence", 0.5))
        result["explanation"] = result.get("explanation", "")
        logger.info(f"Verdict: {result['verdict']} | Confidence: {result['confidence']:.2f}")
        return result
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return {"verdict": "UNCERTAIN", "confidence": 0.0, "explanation": str(e)}


def correct_claim(claim: str, evidence: str) -> str:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Rewrite false claims as correct factual statements. Return ONLY the corrected statement, nothing else."},
                {"role": "user", "content": f"False claim: {claim}\nEvidence: {evidence or 'Use your knowledge.'}\nReturn ONLY the corrected statement."}
            ],
            temperature=0.0,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip().strip('"')
    except Exception as e:
        logger.error(f"Correction failed: {e}")
        return claim
