import streamlit as st
from config import config
from verifier import extract_claims, verify_claim, correct_claim
from search import search_evidence
from logger import logger

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Veritas — LLM Hallucination Detection Engine")
st.caption(f"v{config.APP_VERSION} | Powered by LLaMA 3 70B + Tavily Search")

st.markdown("""
Paste any AI-generated text below.
Veritas will extract every factual claim, verify it against live web sources,
and generate a full Hallucination Report Card.
""")

text_input = st.text_area(
    "Paste AI-generated text here",
    height=200,
    placeholder="e.g. The Eiffel Tower was built in 1889. It is located in London..."
)

if st.button("Analyze for Hallucinations", type="primary"):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        config.validate()

        with st.spinner("Extracting claims..."):
            claims = extract_claims(text_input)

        if not claims:
            st.error("No claims could be extracted. Try different text.")
        else:
            st.success(f"Found {len(claims)} claims. Verifying...")

            results = []
            progress = st.progress(0)

            for i, claim in enumerate(claims):
                with st.spinner(f"Verifying claim {i+1}/{len(claims)}..."):
                    evidence = search_evidence(claim)
                    verdict = verify_claim(claim, evidence)
                    corrected = None
                    if verdict.get("verdict") in ["FALSE", "UNCERTAIN"]:
                        corrected = correct_claim(claim, evidence)
                    results.append({
                        "claim": claim,
                        "verdict": verdict,
                        "corrected": corrected,
                        "evidence": evidence[:300]
                    })
                progress.progress((i + 1) / len(claims))

            st.markdown("---")
            st.subheader("📋 Hallucination Report Card")

            true_count = sum(1 for r in results if r["verdict"].get("verdict") == "TRUE")
            false_count = sum(1 for r in results if r["verdict"].get("verdict") == "FALSE")
            uncertain_count = sum(1 for r in results if r["verdict"].get("verdict") == "UNCERTAIN")
            total = len(results)
            hallucination_rate = ((false_count + uncertain_count) / total) * 100

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Claims", total)
            col2.metric("True", true_count, delta=None)
            col3.metric("False", false_count, delta=None)
            col4.metric("Hallucination Rate", f"{hallucination_rate:.1f}%")

            st.markdown("---")

            for i, r in enumerate(results):
                verdict = r["verdict"].get("verdict", "UNCERTAIN")
                confidence = r["verdict"].get("confidence", 0.0)
                explanation = r["verdict"].get("explanation", "")

                if verdict == "TRUE":
                    color = "🟢"
                elif verdict == "FALSE":
                    color = "🔴"
                else:
                    color = "🟡"

                with st.expander(f"{color} Claim {i+1}: {r['claim'][:80]}..."):
                    st.markdown(f"**Verdict:** `{verdict}`")
                    st.markdown(f"**Confidence:** `{confidence:.0%}`")
                    st.markdown(f"**Explanation:** {explanation}")
                    if r["corrected"]:
                        st.markdown(f"**Corrected Claim:** ✅ {r['corrected']}")
                    st.markdown(f"**Evidence Preview:** _{r['evidence'][:200]}_")

            logger.info(f"Analysis complete. Hallucination rate: {hallucination_rate:.1f}%")
