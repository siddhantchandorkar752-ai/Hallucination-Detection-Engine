import json
import re
from groq import Groq
from config import config
from logger import logger

client = Groq(api_key=config.GROQ_API_KEY)

def extract_claims(text: str) -> list[str]:
    prompt = f"""Extract all factual claims from this text as a JSON array of strings.
Return ONLY the JSON array, nothing else.

Text: {text}

Output example: ["claim 1", "claim 2"]"""

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a fact-checking assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        claims = json.loads(raw[start:end])
        logger.info(f"Extracted {len(claims)} claims.")
        return claims[:config.MAX_CLAIMS_PER_TEXT]
    except Exception as e:
        logger.error(f"Claim extraction failed: {e}")
        return []


def verify_claim(claim: str, evidence: str) -> dict:
    prompt = f"""You are a professional fact-checker.
Claim: {claim}
Evidence: {evidence}

Return ONLY this JSON:
{{"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0.0 to 1.0, "explanation": "one sentence"}}"""

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a fact-checker. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        logger.info(f"Verdict: {result.get('verdict')}")
        return result
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return {"verdict": "UNCERTAIN", "confidence": 0.0, "explanation": str(e)}


def correct_claim(claim: str, evidence: str) -> str:
    prompt = f"""Rewrite this false claim as a corrected factual statement using the evidence.
Return ONLY the corrected claim, nothing else.

Original claim: {claim}
Evidence: {evidence}"""

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a fact-checker. Return only the corrected claim."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Correction failed: {e}")
        return claim
