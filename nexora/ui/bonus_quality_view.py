"""Drop-in UI for JD wording review and resume extraction diagnostics."""
from nexora.jd_analysis.bias_detector import analyze_jd_wording


def render_jd_wording_review(jd_text):
    import streamlit as st
    st.subheader('JD wording review')
    st.caption('Potential restrictions for human review. Warnings do not change candidate scores.')
    flags=analyze_jd_wording(jd_text)
    if not flags:st.info('No wording matched the current rules. This is not a guarantee of an unbiased JD.')
    for flag in flags:
        with st.expander(f"{flag['bias_type']}: {flag['phrase']}"):
            st.text(flag['context'])
            st.write(flag['explanation'])
            st.write('Suggested revision: '+flag['alternative_suggestion'])
            st.caption(f"Text positions {flag['start']}–{flag['end']}")


def render_resume_diagnostics(candidates):
    import streamlit as st
    st.subheader('Resume parsing diagnostics')
    for candidate in candidates:
        c=candidate if isinstance(candidate,dict) else candidate.model_dump()
        with st.expander(c.get('name') or c.get('candidate_id') or c.get('id','Candidate')):
            q=c.get('extraction_quality',{})
            if hasattr(q,'model_dump'):q=q.model_dump()
            if isinstance(q,dict):
                for warning in q.get('warnings',[]):st.warning(warning)
            logs=c.get('normalization_log',[])
            if logs:
                for log in logs:
                    st.write(f"{log.get('match_type','Normalization')}: {log.get('original','')} → {log.get('canonical','')}")
                    for warning in log.get('warnings',[]):st.caption(warning)
            else:st.caption('No normalization events were recorded.')
            if not c.get('evidence_units'):st.warning('No evidence extracted; check whether OCR is required.')
