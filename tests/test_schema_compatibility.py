from nexora.schemas import (Candidate, EvidenceUnit, ExtractionQuality, JDRequirement,
    JobDescription, Requirement, RequirementCategory, RequirementImportance, SectionType)
from nexora.ranking.input_adapter import normalize_ranking_inputs


def test_parser_inputs_keep_provenance_and_quality():
    e = EvidenceUnit(unit_id='u', candidate_id='c', text='Built a React app',
                     section_type=SectionType.PROJECTS, page_number=2)
    c = Candidate(id='c', evidence_units=[e], extracted_skills=['React'],
                  extraction_quality=ExtractionQuality(quality_score=.8))
    j = JobDescription(id='j', requirements=[JDRequirement(id='r', text='React',
        category=RequirementCategory.TECHNICAL_SKILL,
        importance=RequirementImportance.REQUIRED, canonical_skills=['React'], weight=1.25)])
    job, candidates = normalize_ranking_inputs(j, [c])
    assert job['jd_id'] == 'j'
    assert job['requirements'][0]['category'] == 'technology'
    assert job['requirements'][0]['canonical'] == 'react'
    assert candidates[0]['extraction_quality'] == .8
    assert candidates[0]['evidence_units'][0]['evidence_id'] == 'u'
    assert candidates[0]['evidence_units'][0]['section'] == 'projects'
    assert candidates[0]['evidence_units'][0]['page'] == 2
    assert candidates[0]['evidence_units'][0]['has_action_verb']


def test_engine_inputs_remain_supported():
    e = EvidenceUnit(evidence_id='e', candidate_id='c', text='Docker', normalized_text='docker', section='skills')
    c = Candidate(candidate_id='c', name='Test', evidence_units=[e], extraction_quality=.7)
    j = JobDescription(jd_id='j', title='Test', requirements=[Requirement(requirement_id='r',text='Docker',canonical='docker')])
    job, candidates = normalize_ranking_inputs(j,[c])
    assert job['requirements'][0]['requirement_id'] == 'r'
    assert candidates[0]['evidence_units'][0]['section'] == 'skills'
    assert candidates[0]['extraction_quality'] == .7


def test_multiple_skills_preserve_total_requirement_weight():
    j = dict(id='j', requirements=[dict(id='r', text='React and Node.js', category='technical_skill',
             importance='required', weight=1.25, canonical_skills=['React','Node.js'])])
    job,_ = normalize_ranking_inputs(j,[])
    assert len(job['requirements']) == 2
    assert sum(r['importance'] for r in job['requirements']) == 1.25
    assert all(r['source_requirement_id']=='r' for r in job['requirements'])
