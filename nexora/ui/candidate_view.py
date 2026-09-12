"""
Candidate detail view component for Streamlit UI.
"""

import streamlit as st


def render_candidate_view(final_result: dict):
    """
    Renders detailed candidate view including evidence cards, requirement matrix, and normalization log.
    """
    st.header("Candidate Deep-Dive & Evidence Auditing")

    ranking = final_result.get("ranking", {})
    ranked_candidates = ranking.get("ranked_candidates", [])

    if not ranked_candidates:
        st.warning("No candidates available.")
        return

    cand_options = {c.get("candidate_id"): f"#{c.get('rank')} - {c.get('name')} (Score: {c.get('score')})" for c in ranked_candidates}
    selected_id = st.selectbox("Select Candidate to Inspect", list(cand_options.keys()), format_func=lambda x: cand_options[x])

    selected_cand = next((c for c in ranked_candidates if c.get("candidate_id") == selected_id), None)

    if selected_cand:
        col1, col2, col3 = st.columns(3)
        col1.metric("Final Score", f"{selected_cand.get('score')}/100")
        col2.metric("Confidence", f"{selected_cand.get('confidence')}% ({selected_cand.get('confidence_label')})")
        col3.metric("Required Skill Coverage", f"{int(selected_cand.get('required_coverage', 0)*100)}%")

        st.subheader("Requirement Match Breakdown")
        req_table = []
        for m in selected_cand.get("requirement_matches", []):
            req_table.append({
                "Requirement ID": m.get("requirement_id"),
                "Keyword Score": f"{m.get('keyword_score'):.2f}",
                "Semantic Score": f"{m.get('semantic_score'):.2f}",
                "Ontology Support": f"{m.get('ontology_support'):.2f}",
                "Evidence Strength": f"{m.get('evidence_strength'):.2f}",
                "Final Score": f"{m.get('final_requirement_score'):.3f}",
                "Status": m.get("status")
            })
        st.dataframe(req_table, use_container_width=True)

        st.subheader("Missing & Weak Requirements")
        missing = selected_cand.get("missing_required", [])
        if missing:
            for m_item in missing:
                st.warning(f"No reliable evidence found for: {m_item}")
        else:
            st.success("All required skills satisfied with supporting evidence.")

        # Normalization log
        norm_summary = final_result.get("normalization_summary", [])
        cand_norm = next((n for n in norm_summary if n.get("candidate_id") == selected_id), None)
        if cand_norm:
            st.subheader("Messy Resume Normalization Diagnostics")
            st.write(f"**Extraction Quality:** {cand_norm.get('extraction_quality')}%")
            if cand_norm.get("normalizations"):
                st.json(cand_norm.get("normalizations"))
