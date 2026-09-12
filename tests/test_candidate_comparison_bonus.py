import pytest
from nexora.explanations.candidate_comparison import compare_candidates


def fixture():
    jd={'requirements':[dict(requirement_id='r',canonical='react',text='React',importance=1.25)]}
    def score(cid,m):
        return dict(candidate_id=cid,name=cid,rank=1 if cid=='a' else 2,score=78*m+5+5.6,
            experience_relevance=.5,confidence=80,missing_required=[],requirement_matches=[dict(
                requirement_id='r',final_requirement_score=m,status='strong_match',evidence_ids=[cid+'_ev'])])
    candidates=[dict(candidate_id=c,evidence_units=[dict(evidence_id=c+'_ev',text=c+' actual excerpt',page=2,section='projects')]) for c in ['a','b']]
    ranking={'ranked_candidates':[score('a',.9),score('b',.6)]}
    return jd,candidates,ranking


def test_contributions_reconcile_to_final_gap():
    jd,c,r=fixture();out=compare_candidates(jd,c,r,'a','b')
    assert sum(x['difference'] for x in out['component_differences'])==pytest.approx(out['score_difference'])
    assert out['requirement_differences'][0]['difference']==pytest.approx(23.4)
    assert out['requirement_differences'][0]['a_evidence'][0]['text']=='a actual excerpt'


def test_reverse_selection_is_honest():
    jd,c,r=fixture();out=compare_candidates(jd,c,r,'b','a')
    assert out['score_difference']<0
    assert out['answer'].startswith('a has')


def test_same_candidate_rejected():
    jd,c,r=fixture()
    with pytest.raises(ValueError,match='different'):compare_candidates(jd,c,r,'a','a')


def test_mismatched_jd_rejected():
    jd,c,r=fixture();jd['requirements'][0]['requirement_id']='wrong'
    with pytest.raises(ValueError,match='IDs differ'):compare_candidates(jd,c,r,'a','b')


def test_missing_excerpts_are_not_invented():
    jd,c,r=fixture();out=compare_candidates(jd,[],r,'a','b')
    assert out['requirement_differences'][0]['a_evidence']==[]


def test_equal_scores_report_tie():
    jd,c,r=fixture();r['ranked_candidates'][1]=dict(r['ranked_candidates'][0],candidate_id='b',name='b')
    assert 'equal displayed' in compare_candidates(jd,c,r,'a','b')['answer']
