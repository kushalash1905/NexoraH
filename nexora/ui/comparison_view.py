"""
Comparison and Recruiter Interaction view component for Streamlit UI.
"""

import streamlit as st
from nexora.explanations.comparison import compare_candidates, recruiter_answer


def render_comparison_view(final_result: dict):
    """
    Renders recruiter comparison tool and preset questions.
    """
    st.header("Recruiter Intelligence & Candidate Comparison")

    ranking = final_result.get("ranking", {})
    ranked_candidates = ranking.get("ranked_candidates", [])
    jd = final_result.get("jd", {})

    if len(ranked_candidates) < 2:
        st.warning("At least two candidates are required for comparison.")
        return

    cand_options = {c.get("candidate_id"): f"#{c.get('rank')} - {c.get('name')}" for c in ranked_candidates}
    keys = list(cand_options.keys())

    col1, col2 = st.columns(2)
    with col1:
        cand_a_id = st.selectbox("Select Candidate A", keys, index=0, format_func=lambda x: cand_options[x])
    with col2:
        cand_b_id = st.selectbox("Select Candidate B", keys, index=min(1, len(keys)-1), format_func=lambda x: cand_options[x])

    if cand_a_id and cand_b_id:
        st.subheader("Preset Recruiter Actions")
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

        action = None
        if btn_col1.button("Why is A > B?"):
            action = f"Why is candidate {cand_a_id} ranked above candidate {cand_b_id}?"
        if btn_col2.button("Compare A & B"):
            action = f"Compare candidate {cand_a_id} and candidate {cand_b_id}"
        if btn_col3.button("What is B missing?"):
            action = f"What is candidate {cand_b_id} missing?"
        if btn_col4.button("What would improve B?"):
            action = f"What would improve candidate {cand_b_id}?"

        custom_q = st.text_input("Or enter a recruiter question:", value=action or "")

        if custom_q:
            ans = recruiter_answer(
                question=custom_q,
                ranking_result=ranking,
                jd=jd,
                candidates=[],
                candidate_a_id=cand_a_id,
                candidate_b_id=cand_b_id
            )
            st.info(f"**Answer:** {ans.get('answer')}")

            if "comparison" in ans and ans["comparison"].get("top_requirement_contributors"):
                comp = ans["comparison"]
                st.subheader("Requirement Contribution Deltas")
                st.dataframe(comp.get("top_requirement_contributors"), use_container_width=True)
            elif "missing_info" in ans:
                st.json(ans["missing_info"])
            elif "improvement_info" in ans:
                st.json(ans["improvement_info"])
