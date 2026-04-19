import streamlit as st
from fpdf import FPDF
from config import config
from verifier import extract_claims, verify_claim, correct_claim
from search import search_evidence
from logger import logger

st.set_page_config(page_title="VERITAS | AI Forensic Engine", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
* { box-sizing: border-box; }
.stApp { background: radial-gradient(ellipse at top right, #0d1117 0%, #010409 100%); color: #e6edf3; font-family: 'Inter', sans-serif; }
.main-title { font-family: 'Orbitron', sans-serif; background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-align: center; font-size: 3.2rem; font-weight: 900; letter-spacing: 8px; padding: 15px 0 5px; }
.subtitle { text-align: center; color: #8b949e; font-size: 0.8rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 20px; font-family: 'Orbitron', sans-serif; }
.stTextArea textarea { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(0,242,254,0.3) !important; color: #e6edf3 !important; border-radius: 8px !important; }
.stButton button { background: linear-gradient(90deg, #00f2fe, #4facfe) !important; color: #000 !important; font-family: 'Orbitron', sans-serif !important; font-weight: 700 !important; letter-spacing: 2px !important; border: none !important; border-radius: 6px !important; }
.source-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
for k, v in [("total_scans", 0), ("total_claims", 0), ("total_hallucinations", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚙️ FORENSIC SETTINGS")
    mode = st.selectbox("Domain Mode", ["General", "Medical", "Legal", "Scientific"])
    st.markdown("---")
    st.markdown("### 📊 SESSION STATS")
    st.metric("Total Scans", st.session_state.total_scans)
    st.metric("Total Claims Checked", st.session_state.total_claims)
    st.metric("Total Hallucinations Found", st.session_state.total_hallucinations)
    st.markdown("---")
    st.markdown("### ℹ️ ABOUT")
    st.caption("VERITAS v3.0\nLLM Hallucination Detection\nLLaMA 3.3 70B + Tavily Search")


def generate_pdf(results, text_input, mode, rate):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "VERITAS - Hallucination Forensic Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Mode: {mode} | Hallucination Rate: {rate:.1f}% | Total Claims: {len(results)}", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "ORIGINAL TEXT:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, text_input[:800])
    pdf.ln(4)
    for i, r in enumerate(results):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, f"CLAIM {i+1}: {r['verdict']} ({int(r['confidence']*100)}%) [{r.get('nli_label','NEUTRAL')}]", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, f"Original: {r['claim']}")
        pdf.multi_cell(0, 5, f"Analysis: {r['explanation']}")
        if r.get("counter_evidence"):
            pdf.multi_cell(0, 5, f"Counter: {r['counter_evidence']}")
        if r.get("corrected"):
            pdf.multi_cell(0, 5, f"Corrected: {r['corrected']}")
        pdf.ln(2)
    return bytes(pdf.output())


tabs = st.tabs(["🔍 FORENSIC SCANNER", "📚 ARCHITECTURE"])

with tabs[0]:
    st.markdown('<div class="main-title">VERITAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">LLM Hallucination Detection & Auto-Correction Engine v3.0</div>', unsafe_allow_html=True)

    text_input = st.text_area("DATA INPUT BUFFER", height=180,
        placeholder="Paste any AI-generated text here to scan for hallucinations...")

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run = st.button("⚡ EXECUTE SCAN", use_container_width=True)
    with col_info:
        st.caption(f"Mode: **{mode}** | LLaMA 3.3 70B · Tavily Search · NLI · Source Authority Ranking")

    if run:
        if not text_input.strip():
            st.warning("⚠️ Please enter text to analyze.")
        else:
            results = []
            with st.status("⚡ Initializing Forensic Protocol...", expanded=True) as status:
                st.write("📡 Extracting atomic claims...")
                claims = extract_claims(text_input)

                if not claims:
                    status.update(label="⚠️ No Claims Detected", state="error")
                    st.error(f"No verifiable claims found.\nModel: `{config.GROQ_MODEL}`\nCheck API keys in .env file.")
                else:
                    st.write(f"✅ **{len(claims)} atomic claims** extracted. Verifying...")
                    for i, claim in enumerate(claims):
                        st.write(f"🛰️ [{i+1}/{len(claims)}] *{claim[:75]}{'...' if len(claim)>75 else ''}*")
                        evidence, sources = search_evidence(claim)
                        verdict_data = verify_claim(claim, evidence, mode)
                        verdict = verdict_data.get("verdict", "UNCERTAIN")
                        corrected = correct_claim(claim, evidence) if verdict == "FALSE" else None
                        results.append({
                            "claim": claim,
                            "verdict": verdict,
                            "confidence": verdict_data.get("confidence", 0.5),
                            "explanation": verdict_data.get("explanation", ""),
                            "nli_label": verdict_data.get("nli_label", "NEUTRAL"),
                            "counter_evidence": verdict_data.get("counter_evidence", ""),
                            "corrected": corrected,
                            "sources": sources[:3],
                        })
                    status.update(label="✅ SCAN COMPLETE", state="complete", expanded=False)

            if results:
                st.session_state.total_scans += 1
                st.session_state.total_claims += len(results)

                total = len(results)
                true_c  = sum(1 for r in results if r["verdict"] == "TRUE")
                false_c = sum(1 for r in results if r["verdict"] == "FALSE")
                uncertain_c = sum(1 for r in results if r["verdict"] == "UNCERTAIN")
                rate = (false_c / total) * 100
                st.session_state.total_hallucinations += false_c

                # REPORT CARD
                st.markdown("---")
                st.markdown("### 📊 HALLUCINATION REPORT CARD")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TOTAL CLAIMS", total)
                c2.metric("✅ VERIFIED TRUE", true_c)
                c3.metric("❌ HALLUCINATIONS", false_c)
                c4.metric("HALLUCINATION RATE", f"{rate:.1f}%",
                          delta="HIGH RISK" if rate > 50 else "LOW RISK",
                          delta_color="inverse" if rate > 50 else "normal")

                # HEATMAP
                st.markdown("---")
                st.markdown("### 🌡️ HEATMAP — ORIGINAL vs CORRECTED")
                col_orig, col_corr = st.columns(2)

                with col_orig:
                    st.markdown("**📄 Original Text (Highlighted)**")
                    highlighted = text_input
                    for r in results:
                        if r["claim"] in highlighted:
                            if r["verdict"] == "FALSE":
                                highlighted = highlighted.replace(r["claim"],
                                    f'<span style="background:#f8514966;padding:2px 4px;border-radius:3px;font-weight:bold">{r["claim"]}</span>')
                            elif r["verdict"] == "TRUE":
                                highlighted = highlighted.replace(r["claim"],
                                    f'<span style="background:#3fb95066;padding:2px 4px;border-radius:3px">{r["claim"]}</span>')
                    st.markdown(
                        f'<div style="background:rgba(255,255,255,0.03);padding:15px;border-radius:8px;'
                        f'border:1px solid rgba(255,255,255,0.1);line-height:1.9;font-size:0.9rem">{highlighted}</div>',
                        unsafe_allow_html=True)

                with col_corr:
                    st.markdown("**✏️ Auto-Corrected Text**")
                    corrected_text = text_input
                    for r in results:
                        if r.get("corrected") and r["claim"] in corrected_text:
                            corrected_text = corrected_text.replace(r["claim"], r["corrected"])
                    st.markdown(
                        f'<div style="background:rgba(63,185,80,0.05);padding:15px;border-radius:8px;'
                        f'border:1px solid rgba(63,185,80,0.2);line-height:1.9;font-size:0.9rem">{corrected_text}</div>',
                        unsafe_allow_html=True)

                # CLAIM CARDS
                st.markdown("---")
                st.markdown("### 🔬 CLAIM-BY-CLAIM ANALYSIS")

                for i, r in enumerate(results):
                    v = r["verdict"]
                    conf_pct = int(r["confidence"] * 100)
                    emoji = {"TRUE": "✅", "FALSE": "❌", "UNCERTAIN": "⚠️"}.get(v, "❓")
                    color = {"TRUE": "#3fb950", "FALSE": "#f85149", "UNCERTAIN": "#d29922"}.get(v, "#8b949e")
                    nli = r.get("nli_label", "NEUTRAL")
                    nli_color = {"CONTRADICTION": "#f85149", "ENTAILMENT": "#3fb950", "NEUTRAL": "#d29922"}.get(nli, "#8b949e")
                    label = f"{emoji} CLAIM {i+1}: {v} ({conf_pct}%) | NLI: {nli} — {r['claim'][:65]}{'...' if len(r['claim'])>65 else ''}"

                    with st.expander(label):
                        st.markdown("**📝 Original Claim:**")
                        st.info(r["claim"])

                        col_v, col_n = st.columns(2)
                        with col_v:
                            st.markdown(f"**Verdict:** <span style='color:{color};font-weight:bold'>{emoji} {v}</span>", unsafe_allow_html=True)
                            st.progress(r["confidence"], text=f"Confidence: {conf_pct}%")
                        with col_n:
                            st.markdown(f"**NLI:** <span style='color:{nli_color};font-weight:bold'>{nli}</span>", unsafe_allow_html=True)

                        st.markdown("**🔬 Analysis:**")
                        st.write(r["explanation"])

                        if r.get("counter_evidence"):
                            st.markdown("**💡 Counter Evidence:**")
                            st.warning(r["counter_evidence"])

                        if r.get("corrected"):
                            st.markdown("**✏️ Corrected Statement:**")
                            st.success(r["corrected"])

                        if r.get("sources"):
                            st.markdown("**🌐 Sources (Authority Ranked):**")
                            for s in r["sources"]:
                                url = s.get("url", "")
                                title = s.get("title", url)
                                trusted = any(d in url.lower() for d in [".gov", ".edu", "wikipedia", "reuters", "bbc"])
                                badge = "⭐ TRUSTED" if trusted else "📰"
                                st.markdown(
                                    f'<div class="source-card">{badge} <a href="{url}" target="_blank" style="color:#4facfe">{title}</a></div>',
                                    unsafe_allow_html=True)

                # SUMMARY
                st.markdown("---")
                if false_c == 0:
                    st.success("🎯 No hallucinations detected. Text appears factually accurate.")
                elif rate > 70:
                    st.error(f"🚨 CRITICAL: {rate:.1f}% hallucination rate detected.")
                else:
                    st.warning(f"⚠️ {false_c} hallucination(s) detected and auto-corrected.")

                # PDF DOWNLOAD
                st.markdown("---")
                st.markdown("### 📥 DOWNLOAD FORENSIC REPORT")
                try:
                    pdf_bytes = generate_pdf(results, text_input, mode, rate)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name="veritas_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}. Install: pip install fpdf2")

with tabs[1]:
    st.markdown("### 🏗️ VERITAS v3.0 Architecture")
    st.code("""
VERITAS v3.0 Pipeline:
INPUT TEXT
    → ATOMIC CLAIM EXTRACTOR (LLaMA 3.3 70B + JSON Mode)
    → AGENTIC SEARCH (Tavily + Source Authority Ranking)
    → NLI VERIFIER (ENTAILMENT / CONTRADICTION / NEUTRAL)
    → AUTO-CORRECTOR (LLaMA 3.3 70B)
    → FORENSIC DASHBOARD
       ├── Hallucination Report Card
       ├── Heatmap (Red=FALSE, Green=TRUE)
       ├── Side-by-side Original vs Corrected
       ├── Claim Cards with Evidence Sources
       ├── PDF Forensic Report Download
       └── Session Statistics
    """, language="text")
