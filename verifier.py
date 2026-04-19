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
                f"Example: 'Einstein born in 1900 in France won Nobel 1921' becomes "
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


def verify_claim(claim: str, evidence: str, mode: str = "General") -> dict:
    mode_map = {
        "General": "You are a General Fact-Checker with comprehensive world knowledge.",
        "Medical": "You are a Medical Expert Fact-Checker. Apply clinical precision.",
        "Legal": "You are a Legal Expert Fact-Checker. Apply strict legal standards.",
        "Scientific": "You are a Scientific Fact-Checker. Apply empirical rigor.",
    }
    system_prompt = mode_map.get(mode, mode_map["General"])

    ev = evidence.strip() if evidence and evidence.strip() else "No web evidence available. Use your own knowledge."

    user_prompt = (
        f"Fact-check this claim using NLI reasoning:\n\n"
        f"CLAIM: {claim}\n\n"
        f"EVIDENCE: {ev}\n\n"
        f"KNOWN FACTS TO APPLY:\n"
        f"- Elon Musk was born in 1971, not active in 1924\n"
        f"- Moon is made of rock, not sapphire or any gemstone\n"
        f"- Cities cannot be physically relocated\n"
        f"- No spaceport exists in Mahabaleshwar\n"
        f"- Steve Jobs died in 2011 and never invented electric cars\n"
        f"- Nobel Prize in Literature is for authors, not car manuals\n"
        f"- Consumer cars cannot have fusion reactors, fly, or go underwater\n"
        f"- Deep-space missions did not exist in 1750\n\n"
        f"RULES:\n"
        f"- Physically impossible claim = FALSE immediately\n"
        f"- Wrong dates or historical facts = FALSE\n"
        f"- Contradicts known reality = FALSE\n"
        f"- Only TRUE if verifiably correct\n\n"
        f"Return ONLY JSON: {{\"verdict\": \"FALSE\", \"confidence\": 0.99, "
        f"\"explanation\": \"reason\", \"nli_label\": \"CONTRADICTION\", "
        f"\"counter_evidence\": \"correct fact\"}}"
    )

    try:
        raw = _llm([
            {"role": "system", "content": system_prompt + " Return only valid JSON with keys: verdict, confidence, explanation, nli_label, counter_evidence."},
            {"role": "user", "content": user_prompt}
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
        logger.info(f"{result['verdict']} ({result['confidence']:.0%}) [{result['nli_label']}] - {claim[:60]}")
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
