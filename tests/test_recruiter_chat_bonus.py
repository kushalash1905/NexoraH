from nexora.explanations.recruiter_chat import answer_recruiter_question

def inputs():
    jd=dict(requirements=[dict(requirement_id='r',canonical='react',text='React',importance=1)])
    scores=[];candidates=[]
    for i,name,m in [(1,'Aarushi',.9),(2,'Sam',.6)]:
        cid=f'c{i}'
        scores.append(dict(candidate_id=cid,name=name,rank=i,score=78*m+5+5.6,experience_relevance=.5,confidence=80,missing_required=['Docker'],requirement_matches=[dict(requirement_id='r',final_requirement_score=m,status='partial_match',evidence_ids=[cid])]))
        candidates.append(dict(candidate_id=cid,evidence_units=[dict(evidence_id=cid,text='Built React project',page=1)]))
    return jd,candidates,dict(ranked_candidates=scores)

def ask(q):return answer_recruiter_question(q,*inputs())

def test_typed_comparison():
    out=ask('Why is Aarushi ranked above Sam?');assert '23.40-point' in out and 'Built React project' in out

def test_rank_reference():assert '23.40-point' in ask('Compare #1 and #2')
def test_reversed_question():assert ask('Why is Sam above Aarushi?').startswith('Aarushi has')
def test_missing():assert 'Docker' in ask('What is #1 missing?')
def test_evidence():assert 'Built React project' in ask('Show evidence for #1')
def test_unknown():assert 'Name two' in ask('Compare Unknown and Sam')
def test_duplicate_name():
    j,c,r=inputs();r['ranked_candidates'][1]['name']='Aarushi'
    assert 'shared' in answer_recruiter_question('Compare Aarushi and #2',j,c,r)
def test_unsupported():assert 'Try' in ask('Tell me a joke')
