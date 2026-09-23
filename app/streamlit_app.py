"""
Phase 10, Step 2: Streamlit UI - now a pure frontend, calling the
FastAPI backend instead of the pipeline functions directly.
"""

import requests
import streamlit as st

import os
API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Root Cause and Decision Agent", layout="wide")

st.title("AI Root Cause and Decision Agent")
st.caption("Evidence-grounded root cause analysis for microservice incidents (Sock Shop / RCAEval subset)")
st.caption(f"Backend: {API_BASE}")

# --- Fetch case list from the API ---
try:
    cases_response = requests.get(f"{API_BASE}/cases", timeout=5)
    cases_response.raise_for_status()
    cases = cases_response.json()
except requests.exceptions.ConnectionError:
    st.error(f"Could not reach the API at {API_BASE}. Is `uvicorn api.main:app --reload` running?")
    st.stop()

case_ids = [c["case"] for c in cases]
chosen_case = st.selectbox("Select an incident case:", case_ids)
case_info = next(c for c in cases if c["case"] == chosen_case)

col1, col2, col3 = st.columns(3)
col1.metric("Fault type", case_info["fault"])
col2.metric("True root cause (ground truth, for evaluation only)", case_info["root_cause_service"])
col3.metric("Duration", f"{case_info['duration_minutes']} min")

run_button = st.button("Run Root Cause Analysis", type="primary")

if run_button:
    with st.spinner("Calling API: scoring metrics, correlating logs, running grounded LLM reasoning..."):
        try:
            resp = requests.post(f"{API_BASE}/analyze/{chosen_case}", timeout=60)
            resp.raise_for_status()
            st.session_state["analysis"] = resp.json()
            st.session_state["case_id"] = chosen_case
        except requests.exceptions.RequestException as e:
            st.error(f"API call failed: {e}")

# --- Display results ---
if "analysis" in st.session_state and st.session_state.get("case_id") == chosen_case:
    analysis = st.session_state["analysis"]
    result = analysis["ai_decision"]

    st.subheader("Ranked Candidates (Evidence)")
    st.dataframe(analysis["ranked_candidates"], use_container_width=True)

    st.subheader("AI Decision")
    d1, d2 = st.columns([1, 3])
    with d1:
        st.metric("Root Cause", result.get("root_cause_service", "N/A"))
        st.metric("Confidence", result.get("confidence", "N/A"))
    with d2:
        st.markdown(f"**Explanation:** {result.get('explanation', '')}")
        st.markdown(f"**Recommended Action:** {result.get('recommended_action', '')}")
        st.markdown(f"**Evidence Gaps:** {result.get('evidence_gaps', '')}")

    st.caption(f"Decision ID: {analysis['decision_id']} (saved via API)")

    st.subheader("Human Validation")
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        if st.button("Confirm this decision"):
            r = requests.post(f"{API_BASE}/feedback", json={
                "decision_id": analysis["decision_id"], "verdict": "confirmed"
            })
            if r.ok:
                st.success("Feedback saved: confirmed.")
            else:
                st.error(f"Failed to save feedback: {r.text}")
    with f2:
        correction_service = st.text_input("Or correct to service:", key="correction_input")
    with f3:
        if st.button("Submit correction") and correction_service:
            r = requests.post(f"{API_BASE}/feedback", json={
                "decision_id": analysis["decision_id"],
                "verdict": "corrected",
                "corrected_service": correction_service,
            })
            if r.ok:
                st.success(f"Feedback saved: corrected to '{correction_service}'.")
            else:
                st.error(f"Failed to save feedback: {r.text}")

st.divider()
with st.expander("View all past decisions (from API)"):
    try:
        decisions = requests.get(f"{API_BASE}/decisions", timeout=5).json()
        st.json(decisions)
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch decisions: {e}")
    