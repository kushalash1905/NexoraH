"""Drop-in Streamlit panel for an already completed ranking."""
from nexora.explanations.candidate_comparison import compare_candidates


def render_candidate_comparison(jd, candidates, ranking, key='bonus_compare'):
    import streamlit as st
    result = ranking if isinstance(ranking,dict) else ranking.model_dump()
    scores=result.get('ranked_candidates',[])
    scores=[s if isinstance(s,dict) else s.model_dump() for s in scores]
    st.subheader('Why this ranking?')
    st.caption('Compare actual score contributions and source evidence. Runs locally without an AI API.')
    if len(scores)<2:
        st.info('Rank at least two candidates to compare them.')
        return
    ids=[s['candidate_id'] for s in scores]
    labels={s['candidate_id']:f"#{s['rank']} · {s.get('name') or s['candidate_id']} ({s['candidate_id']})" for s in scores}
    with st.form(key):
        left,right=st.columns(2)
        a=left.selectbox('Candidate A',ids,format_func=lambda x:labels[x],key=key+'_a')
        b=right.selectbox('Candidate B',ids,index=1,format_func=lambda x:labels[x],key=key+'_b')
        submitted=st.form_submit_button('Explain comparison')
    if not submitted:return
    try:
        comparison=compare_candidates(jd,candidates,result,a,b)
    except (ValueError,KeyError,TypeError) as exc:
        st.error(f'Comparison could not run: {exc}')
        return
    st.write(comparison['answer'])
    st.dataframe([dict(Requirement=r['requirement'],Type=r['requirement_type'],
        A_points=round(r['a_contribution'],2),B_points=round(r['b_contribution'],2),
        A_minus_B=round(r['difference'],2)) for r in comparison['requirement_differences']],hide_index=True)
    with st.expander('Full score difference breakdown'):
        st.dataframe(comparison['component_differences'],hide_index=True)
    with st.expander('Supporting resume excerpts'):
        for row in comparison['requirement_differences']:
            st.write(row['requirement'])
            for label,field,status in [('A','a_evidence','a_status'),('B','b_evidence','b_status')]:
                st.caption(f"Candidate {label}: {row[status]}")
                for e in row[field]:
                    st.text(e['text'])
                    st.caption(f"Page {e['page']} · {e['section']} · {e['evidence_id']}")
                if not row[field]:st.caption('No source excerpt available for this match.')
