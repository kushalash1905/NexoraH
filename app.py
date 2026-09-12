"""
NEXORA - Single-Process Local Streamlit Application.
Offline candidate intelligence system for candidate ranking and recruiter decision support.
"""

import streamlit as st
import os
from nexora.orchestrator import run_analysis
from nexora.ui.upload_view import render_upload_view
from nexora.ui.ranking_view import render_ranking_view
from nexora.ui.candidate_view import render_candidate_view
from nexora.ui.comparison_view import render_comparison_view
from nexora.ui.jd_quality_view import render_jd_quality_view

st.set_page_config(
    page_title="NEXORA | Offline Candidate Intelligence",
    page_icon="🎯",
    layout="wide"
)

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# Sidebar Navigation
st.sidebar.title("NEXORA Dashboard")
st.sidebar.markdown("**Offline Intelligence Engine**")
st.sidebar.caption("Wi-Fi Disabled · Local Embeddings")

menu = st.sidebar.radio(
    "Navigation",
    ["1. Upload & Analyze", "2. Ranking & Explanations", "3. Candidate Deep-Dive", "4. Recruiter Intelligence", "5. JD Quality & Bias Flags"]
)

if menu == "1. Upload & Analyze":
    jd_path, resume_paths = render_upload_view()
    if jd_path and resume_paths:
        with st.spinner("Processing documents locally with hybrid keyword and semantic analysis..."):
            try:
                result = run_analysis(jd_path, resume_paths)
                st.session_state["analysis_result"] = result
                st.success("Analysis complete! Proceed to '2. Ranking & Explanations'.")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

elif menu == "2. Ranking & Explanations":
    if st.session_state["analysis_result"]:
        render_ranking_view(st.session_state["analysis_result"])
    else:
        st.warning("Please upload JD and Resumes on the 'Upload & Analyze' page first.")

elif menu == "3. Candidate Deep-Dive":
    if st.session_state["analysis_result"]:
        render_candidate_view(st.session_state["analysis_result"])
    else:
        st.warning("Please run analysis first.")

elif menu == "4. Recruiter Intelligence":
    if st.session_state["analysis_result"]:
        render_comparison_view(st.session_state["analysis_result"])
    else:
        st.warning("Please run analysis first.")

elif menu == "5. JD Quality & Bias Flags":
    if st.session_state["analysis_result"]:
        render_jd_quality_view(st.session_state["analysis_result"])
    else:
        st.warning("Please run analysis first.")
