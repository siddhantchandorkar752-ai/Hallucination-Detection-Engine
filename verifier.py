from groq import Groq
from config import config
import json

# Initialize Groq Client
client = Groq(api_key=config.GROQ_API_KEY)

def extract_claims(text):
    """
    Extracts verifiable factual claims from the input text.
    """
    prompt = f"""
    Extract only the verifiable factual claims from the following text.
    Return the result as a JSON object with a key "claims" containing a list of strings.
    Text: {text}
    """
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        return data.get("claims", [])
    except Exception as e:
        print(f"Extraction Error: {e}")
        return []

def verify_claim(claim, evidence):
    """
    Compares a claim against evidence and returns a verdict.
    """
    prompt = f"""
    As a Fact-Checker, compare the [CLAIM] against the [EVIDENCE].
    [CLAIM]: "{claim}"
    [EVIDENCE]: "{evidence}"
    
    If the CLAIM is contradicted by EVIDENCE, mark it as "FALSE".
    If the CLAIM is supported by EVIDENCE, mark it as "TRUE".
    
    Return ONLY a JSON object:
    {{
        "verdict": "FALSE" or "TRUE",
        "confidence": 0-100,
        "explanation": "Short reason why"
    }}
    """
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return {"verdict": "ERROR", "confidence": 0, "explanation": "Verification failed"}

def correct_claim(claim, evidence):
    """
    Provides a corrected version of a hallucinated claim.
    """
    prompt = f"""
    Based on the evidence, correct the following false claim.
    Claim: {claim}
    Evidence: {evidence}
    Return only the corrected sentence.
    """
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return "Correction unavailable."
