import pytest
from nexora.ranking.requirement_review import revise_requirements,suggest_requirement_reviews
from nexora.ranking.confidence import calculate_candidate_confidence


def sample():return dict(requirements=[dict(id='r',text='React',category='technical_skill'),dict(id='x',text='3 years of experience',category='experience_level')])


def test_remove_experience_keeps_skills_and_original():
    jd=sample();new,audit=revise_requirements(jd,['x'])
    assert len(jd['requirements'])==2
    assert new['requirements']==[jd['requirements'][0]]
    assert audit['removed_requirements'][0]['id']=='x'


def test_review_does_not_auto_remove():
    jd=sample();assert suggest_requirement_reviews(jd)[0]['requirement_id']=='x'
    assert len(jd['requirements'])==2


def test_remove_all_or_unknown_rejected():
    with pytest.raises(ValueError):revise_requirements(sample(),['r','x'])
    with pytest.raises(ValueError):revise_requirements(sample(),['unknown'])


def test_format_quality_does_not_change_fit_confidence():
    matches=[dict(evidence_strength=.8,keyword_score=.9,semantic_score=.7,final_requirement_score=.7)]
    assert calculate_candidate_confidence({},matches,.7,extraction_quality=.2)==calculate_candidate_confidence({},matches,.7,extraction_quality=1)
