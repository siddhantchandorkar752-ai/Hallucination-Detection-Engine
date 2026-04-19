from groq import Groq
from config import config
import json

client = Groq(api_key=config.GROQ_API_KEY)

def verify_claim(claim, evidence):
    """
    Stricter prompt to ensure the model flags hallucinations correctly.
    """
    prompt = f"""
    As a Fact-Checker, compare the [CLAIM] against the [EVIDENCE].
    
    [CLAIM]: "{claim}"
    [EVIDENCE]: "{evidence}"
    
    Determine if the [CLAIM] is supported by the [EVIDENCE].
    - If the CLAIM is false based on EVIDENCE, mark it as "FALSE".
    - If the CLAIM is true based on EVIDENCE, mark it as "TRUE".
    
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

# Add extract_claims and correct_claim functions below as per your existing code
