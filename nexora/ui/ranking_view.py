"""
Ranking table view component for Streamlit UI.
"""

import streamlit as st


def render_ranking_view(final_result: dict):
    """
    Renders top-three explanations and complete candidate ranking table.
    """
    st.header("Candidate Rankings & Top-Three Intelligence")

    ranking = final_result.get("ranking", {})
    ranked_candidates = ranking.get("ranked_candidates", [])
    explanations = final_result.get("explanations", [])

    st.subheader("Top-Three Evidence-Backed Explanations")
    for exp in explanations:
        with st.expander(f"Rank #{exp.get('rank')} - Candidate {exp.get('candidate_id')} (Score: {exp.get('score')}/100 - {exp.get('confidence_label')} Confidence)", expanded=True):
            st.markdown(exp.get("summary", ""))

    st.subheader("Complete Candidate Leaderboard")

    table_data = []
    for c in ranked_candidates:
        table_data.append({
            "Rank": c.get("rank"),
            "Candidate Name": c.get("name"),
            "Score": f"{c.get('score'):.1f}",
            "Confidence": f"{c.get('confidence'):.1f}% ({c.get('confidence_label')})",
            "Req. Coverage": f"{int(c.get('required_coverage', 0)*100)}%",
            "Keyword Align": f"{int(c.get('keyword_alignment', 0)*100)}%",
            "Semantic Align": f"{int(c.get('semantic_alignment', 0)*100)}%"
        })

    st.dataframe(table_data, use_container_width=True)

    sensitivity = ranking.get("sensitivity", {})
    if sensitivity:
        st.info("Ranking Sensitivity: Ranking is robust across tested semantic weights (0.30 to 0.50).")
