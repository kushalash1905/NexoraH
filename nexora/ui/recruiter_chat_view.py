"""Typed local recruiter chat for the integrated Streamlit results view."""
import hashlib
import json
from nexora.explanations.recruiter_chat import answer_recruiter_question


def render_recruiter_chat(jd,candidates,ranking,key='recruiter_chat'):
    import streamlit as st
    def d(x):return x if isinstance(x,dict) else x.model_dump()
    # Clear stale conversation when the JD, ranking, or evidence changes.
    fingerprint=hashlib.sha256(json.dumps([d(jd),[d(c) for c in candidates],d(ranking)],default=str,sort_keys=True).encode()).hexdigest()
    state=st.session_state.setdefault(key,dict(fingerprint=fingerprint,messages=[]))
    if state['fingerprint']!=fingerprint:
        state=dict(fingerprint=fingerprint,messages=[]);st.session_state[key]=state
    st.subheader('Ask about your shortlist')
    st.caption('Local chat grounded in scores and resume evidence. Use names, IDs, or #1 / #2.')
    st.caption('Example: Why is #1 ranked above #2? · What is #1 missing? · Show evidence for #1')
    if st.button('Clear conversation',key=key+'_clear'):state['messages']=[]
    with st.expander('Candidate names and ranks'):
        result=d(ranking)
        st.dataframe([dict(rank=d(s)['rank'],name=d(s).get('name',''),candidate_id=d(s)['candidate_id']) for s in result.get('ranked_candidates',[])],hide_index=True)
    prompt=st.chat_input('Ask a question about these candidates',key=key+'_input')
    if prompt:
        answer=answer_recruiter_question(prompt,jd,candidates,ranking)
        state['messages'].extend([dict(role='user',text=prompt),dict(role='assistant',text=answer)])
    for message in state['messages']:
        with st.chat_message(message['role']):
            # Plain text prevents resume content being rendered as active Markdown.
            st.text(message['text'])
