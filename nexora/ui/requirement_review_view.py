"""Local reranking panel; caller supplies its existing ranking function."""
from nexora.ranking.requirement_review import suggest_requirement_reviews,revise_requirements


def render_requirement_review(jd,candidates,rank_function,key='jd_review'):
    """Returns revised result on submission. Caller must persist and display it."""
    import streamlit as st
    source=jd if isinstance(jd,dict) else jd.model_dump()
    requirements=[r if isinstance(r,dict) else r.model_dump() for r in source.get('requirements',[])]
    st.subheader('Review JD requirements and rerank')
    st.caption('Remove a restriction only after reviewing its relevance. Original JD remains unchanged.')
    for item in suggest_requirement_reviews(source):
        st.warning(item['text']+' — '+item['reason'])
    ids=[r.get('requirement_id') or r.get('id') for r in requirements]
    labels={rid:r.get('text',rid) for rid,r in zip(ids,requirements)}
    with st.form(key):
        selected=st.multiselect('Requirements to remove',ids,format_func=lambda x:labels[x])
        submitted=st.form_submit_button('Apply reviewed changes and rerank')
    if not submitted:return None
    if not selected:
        st.info('Select a requirement to remove first.');return None
    try:
        revised,audit=revise_requirements(source,selected)
        with st.spinner('Reranking using the revised requirements…'):
            ranking=rank_function(revised,candidates)
        st.success('Revised ranking calculated. Removed restrictions are recorded below.')
        st.json(audit)
        return dict(jd=revised,ranking=ranking,audit=audit)
    except (ValueError,RuntimeError) as exc:
        st.error(str(exc));return None
