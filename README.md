# Veritas — LLM Hallucination Detection Engine

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LLaMA](https://img.shields.io/badge/LLaMA-3.3--70B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Real-time hallucination detection and self-correction engine powered by LLaMA 3.3 70B and live web search.

---

## The Problem

Large Language Models hallucinate — they generate confident, fluent, and completely false statements.
ChatGPT, Gemini, Claude — all hallucinate. No reliable open-source tool exists to detect and correct this in real time.

**Veritas solves this.**

---

## How It Works
```
Input Text (AI-generated)
        ↓
Claim Extractor — LLaMA 3.3 70B via Groq
        ↓
Evidence Retrieval — Tavily Live Web Search
        ↓
Verdict Engine — TRUE / FALSE / UNCERTAIN + Confidence Score
        ↓
Self-Correction — Rewrites false claims with sources
        ↓
Hallucination Report Card
```

---

## Features

- Extracts every factual claim from any AI-generated text
- Verifies each claim against live web sources in real time
- Assigns verdict: TRUE / FALSE / UNCERTAIN with confidence score
- Automatically rewrites false claims as corrected statements
- Generates a full Hallucination Report Card with hallucination rate
- Production-grade modular architecture

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | LLaMA 3.3 70B via Groq API |
| Search | Tavily Search API |
| UI | Streamlit |
| Config | python-dotenv |
| Logging | Python logging module |

---

## Project Structure
```
veritas/
├── app.py            # Streamlit UI
├── verifier.py       # Claim extraction, verification, correction
├── search.py         # Tavily search client
├── config.py         # Centralized configuration
├── logger.py         # Logging setup
├── main.py           # Entry point
├── requirements.txt  # Dependencies
├── .env.example      # Environment variable template
└── .gitignore
```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/siddhantchandorkar752-ai/Hallucination-Detection-Engine.git
cd Hallucination-Detection-Engine
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Set up API keys
```bash
cp .env.example .env
```

Add your keys to `.env`:
```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get free API keys:
- Groq: https://console.groq.com
- Tavily: https://app.tavily.com

### 4. Run
```bash
streamlit run app.py
```

---

## Example Output

Input:
> "The Eiffel Tower was built in 1756 and is located in London. Albert Einstein was born in France."

Output:
| Claim | Verdict | Confidence | Corrected |
|-------|---------|------------|-----------|
| Eiffel Tower built in 1756 | FALSE | 98% | Built in 1889 |
| Eiffel Tower located in London | FALSE | 99% | Located in Paris |
| Einstein born in France | FALSE | 97% | Born in Ulm, Germany |

Hallucination Rate: 100%

---

## Why Veritas

- Anthropic, OpenAI, and Google are actively researching hallucination detection
- No open-source tool exists that combines LLM reasoning + live web verification + auto-correction
- Veritas is the first open-source end-to-end hallucination detection and correction pipeline

---

## Roadmap

- [ ] Batch processing — analyze multiple documents
- [ ] API endpoint — integrate into any application
- [ ] Chrome extension — detect hallucinations on any webpage
- [ ] Support for GPT-4, Gemini, Claude outputs
- [ ] Citation generation with source links

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

**Siddhant Chandorkar**
[GitHub](https://github.com/siddhantchandorkar752-ai)
