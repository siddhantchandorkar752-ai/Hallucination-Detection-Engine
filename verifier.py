import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)

EXTRACTION_SYSTEM = """You are an elite fact-extraction engine. Your ONLY job is to extract every verifiable factual claim from input text.

RULES:
- Extract ALL verifiable facts: dates, names, places, statistics, events, records, quantities
- Each claim must be a single, self-contained, checkable statement
- Never skip any fact, no matter how small
- Return ONLY a valid JSON array of strings — no markdown, no explanation, no preamble
- If text has 1 fact, return array with 1 item. If 10 facts, return 10 items.
- NEVER return empty array unless input has zero verifiable facts"""

EXTRACTION_USER = """Extract every single verifiable factual claim from this text as a JSON array.

TEXT:
{text}

Return ONLY the JSON array. Example format:
["The 2024 ICC T20 World Cup was hosted by the United States", "India defeated South Africa in the final", "Jasprit Bumrah was player of the tournament"]"""


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
        logger.info(f"Raw extraction response: {raw[:200]}")

        # Strip markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Find JSON array boundaries
        start = raw.find("[")
        end = raw.rfind("]") + 1

        if start == -1 or end == 0:
            logger.warning("No JSON array found. Attempting line-by-line parse.")
            lines = [l.strip().strip('"-,') for l in raw.split("\n") if l.strip().strip('"-,')]
            claims = [l for l in lines if len(l) > 10]
        else:
            claims = json.loads(raw[start:end])

        claims = [c.strip() for c in claims if isinstance(c, str) and len(c.strip()) > 5]
        logger.info(f"Extracted {len(claims)} claims.")
        return claims[:config.MAX_CLAIMS_PER_TEXT]

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}. Raw: {raw[:300]}")
        # Fallback: regex extract quoted strings
        fallback = re.findall(r'"([^"]{10,})"', raw)
        logger.info(f"Fallback extracted {len(fallback)} claims.")
        return fallback[:config.MAX_CLAIMS_PER_TEXT]
    except Exception as e:
        logger.error(f"Claim extraction failed: {e}")
        return []


VERIFY_SYSTEM = """You are a world-class fact-checker with access to provided evidence.

RULES:
- Verdict must be exactly: TRUE, FALSE, or UNCERTAIN
- TRUE: claim fully supported by evidence
- FALSE: claim contradicted by evidence  
- UNCERTAIN: evidence insufficient to confirm or deny
- Confidence: 0.0 (no confidence) to 1.0 (absolute certainty)
- Return ONLY valid JSON, no markdown, no preamble"""

VERIFY_USER = """Fact-check this claim against the evidence.

CLAIM: {claim}

EVIDENCE:
{evidence}

Return ONLY this exact JSON:
{{"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.85, "explanation": "One sentence explaining the verdict based on evidence."}}"""


def verify_claim(claim: str, evidence: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": VERIFY_SYSTEM},
                {"role": "user", "content": VERIFY_USER.format(claim=claim, evidence=evidence or "No evidence found.")}
            ],
            temperature=0.0,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object in response")

        result = json.loads(raw[start:end])

        # Validate + normalize
        result["verdict"] = result.get("verdict", "UNCERTAIN").upper()
        if result["verdict"] not in ("TRUE", "FALSE", "UNCERTAIN"):
            result["verdict"] = "UNCERTAIN"
        result["confidence"] = float(result.get("confidence", 0.5))
        result["explanation"] = result.get("explanation", "No explanation provided.")

        logger.info(f"Verdict: {result['verdict']} | Confidence: {result['confidence']:.2f}")
        return result

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return {"verdict": "UNCERTAIN", "confidence": 0.0, "explanation": f"Verification error: {str(e)}"}


CORRECT_SYSTEM = """You are a precise fact-corrector. Rewrite false claims using only evidence provided.
Return ONLY the corrected factual statement — no explanation, no prefix, no quotes."""

CORRECT_USER = """Rewrite this false claim as a correct factual statement using the evidence below.

FALSE CLAIM: {claim}

EVIDENCE:
{evidence}

Return ONLY the corrected statement."""


def correct_claim(claim: str, evidence: str) -> str:
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": CORRECT_SYSTEM},
                {"role": "user", "content": CORRECT_USER.format(claim=claim, evidence=evidence or "No evidence available.")}
            ],
            temperature=0.0,
            max_tokens=256,
        )
        corrected = response.choices[0].message.content.strip().strip('"')
        logger.info(f"Corrected: {corrected[:100]}")
        return corrected
    except Exception as e:
        logger.error(f"Correction failed: {e}")
        return claim
