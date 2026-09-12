"""
Upload view component for Streamlit UI.
"""

import streamlit as st
import tempfile
import os


def render_upload_view():
    """
    Renders file uploader for JD and Resumes. Returns (jd_path, resume_paths).
    """
    st.title("NEXORA Candidate Intelligence")
    st.caption("LOCAL MODE · NO EXTERNAL APIs · WI-FI INDEPENDENT")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Job Description")
        jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="jd_upload")

    with col2:
        st.subheader("2. Candidate Resumes")
        resume_files = st.file_uploader("Upload Resumes (PDF, DOCX, TXT, XML)", type=["pdf", "docx", "txt", "xml"], accept_multiple_files=True, key="resumes_upload")

    jd_path = None
    resume_paths = []

    if jd_file and resume_files:
        st.success(f"Loaded JD and {len(resume_files)} resumes.")

        if st.button("Run Intelligence Analysis", type="primary"):
            temp_dir = tempfile.mkdtemp()

            # Save JD
            jd_path = os.path.join(temp_dir, jd_file.name)
            with open(jd_path, "wb") as f:
                f.write(jd_file.getbuffer())

            # Save Resumes
            for r_file in resume_files:
                r_path = os.path.join(temp_dir, r_file.name)
                with open(r_path, "wb") as f:
                    f.write(r_file.getbuffer())
                resume_paths.append(r_path)

            return jd_path, resume_paths

    return None, []
