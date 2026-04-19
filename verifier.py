import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)

EXTRACTION_SYSTEM = """You are a claim extraction robot. Your ONLY job is to copy factual statements EXACTLY as written.

STRICT RULES:
1. Copy claims WORD FOR WORD from the original text
2. Do NOT fix, correct, or modify anything
3. Do NOT add "is incorrect" or "actually" or any corrections
4. Extract wrong facts AS-IS - that is the entire point
5. Each claim must be atomic - one fact per item
6. Return ONLY valid JSON array

EXAMPLE:
Text: "Napoleon was born in 1800 and was 4 feet tall"
Output: ["Napoleon was born in 1800", "Napoleon was 4 feet tall"]
NOT: ["Napoleon was born in 1769, not 1800", "Napoleon was 4 feet tall is incorrect"]"""

EXTRACTION_USER = """Copy each fact EXACTLY as written. Do NOT correct anything.

TEXT: {text}

Return ONLY JSON array with exact quotes from text:"""

VERIFY_SYSTEM = """You are a strict fact-checker. Check if the claim is true or false.

RULES:
- TRUE: claim is factually correct
- FALSE: claim is factually wrong, impossible, or contradicts known facts
- UNCERTAIN: genuinely cannot determine
- Be aggressive: absurd claims (flying cars, liquid nitrogen fuel) = FALSE immediately
- Use your knowledge even without evidence

Return ONLY: {"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.0-1.0, "explanation": "one line reason"}"""

VERIFY_USER = """Is this claim TRUE or FALSE?

CLAIM: {claim}

EVIDENCE: {evidence}

Return ONLY JSON: {"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.95, "explanation": "reason"}"""

CORRECT_SYSTEM = """Rewrite the false claim as a correct factual statement. Return ONLY the corrected statement. No prefix. No quotes."""


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
            max_tokens=4096,
        )
        raw = response.choices[0].message.content.strip()
        logger.info(f"Raw: {raw[:200]}")
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            lines = [l.strip().strip('",-') for l in raw.split("\n") if len(l.strip()) > 8]
            return lines[:config.MAX_CLAIMS_PER_TEXT]
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
                    evidence=evidence if evidence.strip() else "No evidence. Use your knowledge."
                )}
            ],
            temperature=0.0,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON")
        result = json.loads(raw[start:end])
        result["verdict"] = str(result.get("verdict", "UNCERTAIN")).upper().strip()
        if result["verdict"] not in ("TRUE", "FALSE", "UNCERTAIN"):
            result["verdict"] = "UNCERTAIN"
        result["confidence"] = min(1.0, max(0.0, float(result.get("confidence", 0.5))))
        result["explanation"] = result.get("explanation", "")
        logger.info(f"{result['verdict']} ({result['confidence']:.0%}) - {claim[:50]}")
        return result
    except Exception as e:
        logger.error(f"Verify failed: {e}")
        return {"verdict": "UNCERTAIN", "confidence": 0.0, "explanation": str(e)}


def correct_claim(claim: str, evidence: str) -> str:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": CORRECT_SYSTEM},
                {"role": "user", "content": f"False claim: {claim}\nEvidence: {evidence or 'Use your knowledge.'}\nCorrect version:"}
            ],
            temperature=0.0,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Correct failed: {e}")
        return claim
