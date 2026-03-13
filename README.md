<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,30:0d0d0d,60:1a0000,100:cc0000&height=250&section=header&text=VERITAS&fontSize=100&fontColor=ffffff&fontAlignY=38&desc=LLM%20Hallucination%20Detection%20%2B%20Auto-Correction%20Engine&descAlignY=62&descSize=22&animation=fadeIn" width="100%"/>

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=22&duration=3000&pause=800&color=FF6B6B&center=true&vCenter=true&multiline=true&width=800&height=120&lines=Extract+Every+Claim+%7C+Verify+Against+Live+Web;TRUE+%2F+FALSE+%2F+UNCERTAIN+%E2%80%94+Every+Single+Fact;Auto-Correct+Hallucinations+With+Cited+Sources;The+AI+That+Keeps+AI+Honest)](https://git.io/typing-svg)

<br/>

<img src="https://img.shields.io/badge/Python-3.11-FF6B6B?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/LLaMA_3.3-70B-FF8E53?style=for-the-badge&logo=meta&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq-Inference-FFD93D?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Tavily-Live_Search-6BCB77?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Streamlit-1.40-FF6B6B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-LIVE-00E676?style=for-the-badge"/>

<br/><br/>

> ### *"The most dangerous AI output is the one that sounds completely correct."*
> VERITAS extracts every factual claim, verifies it against live web sources, and rewrites what is wrong — automatically.

<br/>

[![Live Demo](https://img.shields.io/badge/%F0%9F%9A%80_LIVE_DEMO-Try_VERITAS_Now-FF6B6B?style=for-the-badge)](YOUR_STREAMLIT_URL_HERE)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/siddhantchandorkar752-ai/Hallucination-Detection-Engine)

</div>

---

## WHAT IS VERITAS?

```
╔══════════════════════════════════════════════════════════════════════╗
║     VERITAS — LLM Hallucination Detection Engine v1.0               ║
║     "Don't trust AI blindly. Verify every word."                    ║
║                                                                      ║
║     PIPELINE:  Extract → Verify → Score → Correct → Report         ║
║     MODELS:    LLaMA 3.3 70B via Groq (fastest open inference)      ║
║     SEARCH:    Tavily Live Web (real-time, not cached)              ║
║     OUTPUT:    TRUE / FALSE / UNCERTAIN + Hallucination Rate        ║
╚══════════════════════════════════════════════════════════════════════╝
```

Paste any AI-generated text from ChatGPT, Gemini, Claude — and VERITAS tears it apart claim by claim.

> Most AI tools tell you what they think. VERITAS tells you what is actually **true**.

---

## THE PROBLEM

```
Stanford HAI: LLMs hallucinate on up to 27% of factual queries.
In high-stakes domains — this is not annoying. It is dangerous.
```

| Domain | What Can Go Wrong |
|--------|-------------------|
| **Medical** | Wrong dosages, false drug interactions, misdiagnoses |
| **Legal** | Fabricated case citations — lawyers have been fined for this |
| **Financial** | Invented analyst quotes, false market statistics |
| **Academic** | Fake papers, wrong authors, incorrect research findings |

Perplexity shows *some* sources. ChatGPT shows none.
**VERITAS does all three: detect → verify → correct.**

---

## HOW IT WORKS

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INPUT: AI-Generated Text                        │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
               ┌────────────────────────────┐
               │      CLAIM EXTRACTOR       │  ← LLaMA 3.3 70B via Groq
               │   Structured JSON Output   │     isolates every fact
               └──────────────┬─────────────┘
                              │
                              ▼
               ┌────────────────────────────┐
               │    EVIDENCE RETRIEVAL      │  ← Tavily Live Web Search
               │    5 sources per claim     │     real-time, not cached
               └──────────────┬─────────────┘
                              │
                              ▼
               ┌────────────────────────────┐
               │      VERDICT ENGINE        │  ← TRUE / FALSE / UNCERTAIN
               │   Confidence % per claim   │     full reasoning chain
               └──────────────┬─────────────┘
                              │
                              ▼
               ┌────────────────────────────┐
               │   SELF-CORRECTION ENGINE   │  ← Rewrites false claims
               │   Cites live sources       │     with evidence
               └──────────────┬─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    HALLUCINATION REPORT CARD                         │
│         Rate | Per-Claim Table | Corrected Full Text                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## VERDICT SYSTEM

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   TRUE         Confidence > 85%   Claim verified by live sources    │
│                                                                      │
│   UNCERTAIN    Confidence 50-85%  Conflicting or weak evidence      │
│                                                                      │
│   FALSE        Confidence > 85%   Contradicted by live sources      │
│                                   + Auto-corrected with citation     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## LIVE EXAMPLE

**Input — AI-generated text with 4 hallucinations:**
```
"The Eiffel Tower was built in 1756 and is located in London.
 Albert Einstein was born in France.
 The Moon is 100,000 km from Earth."
```

**VERITAS Output:**

| Claim | Verdict | Confidence | Auto-Corrected |
|-------|:-------:|:----------:|----------------|
| Eiffel Tower built in 1756 | **FALSE** | 98% | Built in 1889 by Gustave Eiffel |
| Located in London | **FALSE** | 99% | Located in Paris, France |
| Einstein born in France | **FALSE** | 97% | Born in Ulm, Germany (1879) |
| Moon is 100,000 km away | **FALSE** | 96% | Average: 384,400 km |

```
HALLUCINATION RATE: 100%  |  Claims Checked: 4  |  Auto-Corrected: 4
```

---

## BENCHMARK RESULTS

| Text Type | Claims | Hallucination Rate | Avg Confidence |
|-----------|:------:|:-----------------:|:--------------:|
| AI-generated history | 8 | 87.5% | 94% |
| AI-generated science | 6 | 66.7% | 91% |
| Human-written news | 5 | 20.0% | 88% |

---

## WHY VERITAS IS DIFFERENT

| Capability | ChatGPT | Perplexity | **VERITAS** |
|-----------|:-------:|:----------:|:-----------:|
| Detects hallucinations | No | Partial | **Yes** |
| Live web verification | No | Yes | **Yes** |
| Per-claim verdict + confidence | No | No | **Yes** |
| Auto-corrects false claims | No | No | **Yes** |
| Full hallucination report | No | No | **Yes** |
| Open source | No | No | **Yes** |

---

## FEATURES

| Feature | Description |
|---------|-------------|
| **Claim Extraction** | Every verifiable fact isolated via structured LLM prompting |
| **Live Verification** | Real-time web search — not cached, not outdated |
| **Verdict + Confidence** | TRUE / FALSE / UNCERTAIN with % score per claim |
| **Auto-Correction** | False claims rewritten with cited live evidence |
| **Report Card** | Hallucination rate + full corrected text output |
| **Modular Architecture** | Clean file separation — each concern in its own module |
| **Secure Credentials** | API keys via `.env` — never hardcoded |

---

## TECH STACK

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | LLaMA 3.3 70B via Groq | Fastest open-source inference, free tier |
| **Search** | Tavily Search API | Purpose-built for AI agents, structured results |
| **UI** | Streamlit 1.40 | Fast iteration, clean data visualization |
| **Config** | python-dotenv | Secure environment variable management |
| **Logging** | Python logging | Production-grade observability |

---

## PROJECT STRUCTURE

```
veritas/
├── app.py              # Streamlit UI — full interface
├── verifier.py         # Claim extraction, verification, correction
├── search.py           # Tavily search client
├── config.py           # Centralized configuration
├── logger.py           # Production logging setup
├── main.py             # Entry point + API key validation
├── requirements.txt    # Pinned dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

---

## QUICK START

```bash
# 1. Clone
git clone https://github.com/siddhantchandorkar752-ai/Hallucination-Detection-Engine.git
cd Hallucination-Detection-Engine

# 2. Setup
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Add API keys to .env
GROQ_API_KEY=your_key_here       # free at console.groq.com
TAVILY_API_KEY=your_key_here     # free at app.tavily.com

# 4. Run
streamlit run app.py
```

---

## WHAT I LEARNED

- **LLM output is non-deterministic** — structured JSON prompting with strict validation is non-negotiable
- **Dependency conflicts are real** — `groq` + `httpx` version clashes cost hours. Pin transitive dependencies
- **Search quality gates everything** — Tavily result ranking directly determines verdict accuracy
- **Modular architecture saves you** — when Groq client broke, one file fix, nothing else touched
- **Production is not local** — Python version mismatches, missing libraries, cloud constraints are real engineering

---

## RESEARCH CONTEXT

Hallucination detection is active research at top labs:
- **Anthropic** — Constitutional AI and self-critique mechanisms
- **Google DeepMind** — SAFE: Search Augmented Factuality Evaluator
- **Meta AI** — FActScoring framework for LLM faithfulness

VERITAS is an open-source implementation of these directions — built for practical use without a research budget.

---

## ROADMAP

- [ ] Batch processing — analyze multiple documents simultaneously
- [ ] REST API — integrate VERITAS into any application
- [ ] Chrome extension — verify any webpage in real time
- [ ] Multi-model support — GPT-4o, Gemini 1.5, Claude 3.5
- [ ] Confidence calibration using historical accuracy tracking

---

## LICENSE

MIT License — free to use, modify, distribute.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0d0d0d,50:1a0000,100:0d0d0d&height=70&text=Siddhant%20Chandorkar&fontSize=30&fontColor=FF6B6B&fontAlign=50&fontAlignY=50" width="500"/>

<br/><br/>

[![GitHub](https://img.shields.io/badge/GitHub-siddhantchandorkar752--ai-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/siddhantchandorkar752-ai)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-siddhantchandorkar-FFD93D?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/siddhantchandorkar)

<br/>

*"I don't just use AI. I build systems that keep AI honest."*

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:cc0000,40:1a0000,100:000000&height=130&section=footer&text=VERITAS%20v1.0&fontSize=32&fontColor=FF6B6B&fontAlignY=68&animation=fadeIn" width="100%"/>

</div>
