import streamlit as st
from config import config
from verifier import extract_claims, verify_claim, correct_claim
from search import search_evidence
from logger import logger

st.set_page_config(
    page_title="VERITAS | Hallucination Forensics",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
* { box-sizing: border-box; }
.stApp { background: radial-gradient(ellipse at top right, #0d1117 0%, #010409 100%); color: #e6edf3; font-family: 'Inter', sans-serif; }
.main-title { font-family: 'Orbitron', sans-serif; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-align: center; font-size: 3.5rem; font-weight: 900; letter-spacing: 8px; padding: 20px 0 5px 0; }
.subtitle { text-align: center; color: #8b949e; font-size: 0.85rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px; font-family: 'Orbitron', sans-serif; }
.stTextArea textarea { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(0,242,254,0.3) !important; color: #e6edf3 !important; font-family: 'Inter', sans-serif !important; border-radius: 8px !important; }
.stButton button { background: linear-gradient(90deg, #00f2fe, #4facfe) !important; color: #000 !important; font-family: 'Orbitron', sans-serif !important; font-weight: 700 !important; letter-spacing: 2px !important; border: none !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

tabs = st.tabs(["🔍 FORENSIC SCANNER", "📚 FRONTEND ARCHITECTURE"])

with tabs[0]:
    st.markdown('<div class="main-title">VERITAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">LLM Hallucination Detection & Auto-Correction Engine</div>', unsafe_allow_html=True)

    text_input = st.text_area(
        "DATA INPUT BUFFER",
        height=200,
        placeholder='Paste any AI-generated text here...\n\nExample: "The 2024 ICC T20 World Cup final was held at Narendra Modi Stadium. India defeated Australia to win the title."',
    )

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run = st.button("EXECUTE SCAN PROTOCOL", use_container_width=True)
    with col_info:
        st.caption("Powered by LLaMA 3.3 70B · Tavily Live Search · Real-time Fact Verification")

    if run:
        if not text_input.strip():
            st.warning("⚠️ Data buffer empty. Please input text to analyze.")
        else:
            results = []

            with st.status("⚡ Initializing Forensic Protocol...", expanded=True) as status:
                st.write("📡 Segmenting claims from input...")
                claims = extract_claims(text_input)
                logger.info(f"UI received {len(claims)} claims")

                if not claims:
                    status.update(label="⚠️ No Claims Detected", state="error", expanded=True)
                    st.error(
                        "**No verifiable claims detected.**\n\n"
                        "Possible reasons:\n"
                        "- API rate limit reached\n"
                        "- Check GROQ_API_KEY in .env\n"
                        f"- Model: `{config.GROQ_MODEL}`"
                    )
                else:
                    st.write(f"✅ **{len(claims)} claims** extracted. Verifying...")
                    for i, claim in enumerate(claims):
                        st.write(f"🛰️ Verifying {i+1}/{len(claims)}: *{claim[:80]}{'...' if len(claim)>80 else ''}*")
                        evidence = search_evidence(claim)
                        verdict_data = verify_claim(claim, evidence)
                        verdict = verdict_data.get("verdict", "UNCERTAIN")
                        corrected = correct_claim(claim, evidence) if verdict == "FALSE" else None
                        results.append({
                            "claim": claim, "verdict": verdict,
                            "confidence": verdict_data.get("confidence", 0.5),
                            "explanation": verdict_data.get("explanation", ""),
                            "corrected": corrected
                        })
                    status.update(label="✅ SCAN COMPLETE", state="complete", expanded=False)

            if results:
                total = len(results)
                true_c = sum(1 for r in results if r["verdict"] == "TRUE")
                false_c = sum(1 for r in results if r["verdict"] == "FALSE")
                uncertain_c = sum(1 for r in results if r["verdict"] == "UNCERTAIN")
                rate = (false_c / total) * 100

                st.markdown("---")
                st.markdown("### 📊 HALLUCINATION REPORT CARD")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TOTAL CLAIMS", total)
                c2.metric("✅ VERIFIED", true_c)
                c3.metric("❌ HALLUCINATIONS", false_c)
                c4.metric("HALLUCINATION RATE", f"{rate:.1f}%")

                st.markdown("---")
                st.markdown("### 🔬 CLAIM-BY-CLAIM ANALYSIS")

                for i, r in enumerate(results):
                    v = r["verdict"]
                    conf_pct = int(r["confidence"] * 100)
                    emoji = {"TRUE": "✅", "FALSE": "❌", "UNCERTAIN": "⚠️"}.get(v, "❓")
                    color = {"TRUE": "#3fb950", "FALSE": "#f85149", "UNCERTAIN": "#d29922"}.get(v, "#8b949e")

                    with st.expander(f"{emoji} CLAIM {i+1}: {v} ({conf_pct}%) — {r['claim'][:70]}{'...' if len(r['claim'])>70 else ''}"):
                        st.markdown("**📝 Original Claim:**")
                        st.info(r["claim"])
                        st.markdown("**🔬 Analysis:**")
                        st.write(r["explanation"])
                        st.markdown(f"**Verdict:** <span style='color:{color};font-weight:bold;'>{emoji} {v}</span>", unsafe_allow_html=True)
                        st.progress(r["confidence"], text=f"Confidence: {conf_pct}%")
                        if r["corrected"]:
                            st.markdown("**✏️ Auto-Corrected:**")
                            st.success(r["corrected"])

                if false_c == 0:
                    st.success("🎯 No hallucinations detected.")
                elif rate > 70:
                    st.error(f"🚨 CRITICAL: {rate:.1f}% hallucination rate.")
                else:
                    st.warning(f"⚠️ {false_c} hallucination(s) detected and corrected.")

with tabs[1]:
    st.markdown("### 🏗️ VERITAS Architecture")
    st.code("""
VERITAS Pipeline:
INPUT TEXT → CLAIM EXTRACTOR (LLaMA 3.3 70B)
    → EVIDENCE RETRIEVAL (Tavily Search)
    → VERDICT ENGINE (TRUE/FALSE/UNCERTAIN + Confidence)
    → AUTO-CORRECTION (Rewrite false claims)
    → REPORT CARD (Hallucination Rate + Per-claim breakdown)
    """, language="text")
