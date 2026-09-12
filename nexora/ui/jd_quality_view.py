"""
JD Quality and Narrow-Language view component for Streamlit UI.
"""

import streamlit as st


def render_jd_quality_view(final_result: dict):
    """
    Renders JD requirements and narrow-language detector flags.
    """
    st.header("JD Intelligence & Narrow-Language Diagnostics")

    jd = final_result.get("jd", {})
    bias_flags = final_result.get("bias_flags", [])

    st.subheader(f"Job Description: {jd.get('title', 'Role')} ({jd.get('company', 'Company')})")

    st.subheader("Extracted Requirements")
    reqs = jd.get("requirements", [])
    req_table = []
    for r in reqs:
        req_table.append({
            "Requirement ID": r.get("requirement_id"),
            "Text": r.get("text"),
            "Category": r.get("category"),
            "Type": r.get("requirement_type"),
            "Importance": r.get("importance")
        })
    st.dataframe(req_table, use_container_width=True)

    st.subheader("Narrow-Language & Restrictiveness Warnings")
    if bias_flags:
        for flag in bias_flags:
            sev = flag.get("severity", "medium").upper()
            if sev == "HIGH":
                st.error(f"**[{sev}] Phrase:** '{flag.get('phrase')}'\n\n**Reason:** {flag.get('reason')}\n\n**Suggestion:** {flag.get('suggestion')}")
            elif sev == "MEDIUM":
                st.warning(f"**[{sev}] Phrase:** '{flag.get('phrase')}'\n\n**Reason:** {flag.get('reason')}\n\n**Suggestion:** {flag.get('suggestion')}")
            else:
                st.info(f"**[{sev}] Phrase:** '{flag.get('phrase')}'\n\n**Reason:** {flag.get('reason')}\n\n**Suggestion:** {flag.get('suggestion')}")
    else:
        st.success("No overly narrow or restrictive wording detected in this Job Description.")
