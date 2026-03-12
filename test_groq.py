from groq import Groq
from config import config

client = Groq(api_key=config.GROQ_API_KEY)
r = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Return only this JSON array: [\"test claim\"]"}],
    temperature=0.0,
    max_tokens=100
)
print(r.choices[0].message.content)
