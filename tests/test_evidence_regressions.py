"""Evidence isolation and runtime validation regressions (no model download)."""
import pytest
from nexora.matching.matcher import match_requirement
from nexora.ranking.scoring import calculate_experience_relevance, rank_candidates


def ev(eid, text, section='projects', verb=True):
    return dict(evidence_id=eid, candidate_id='c', text=text,
                normalized_text=text.lower(), section=section, has_action_verb=verb)


def test_unrelated_project_cannot_boost_skill_evidence():
    req = dict(requirement_id='docker', text='Docker', canonical='docker', category='technology')
    skill = ev('skill', 'Docker', 'skills', False)
    project = ev('unrelated', 'Built Photoshop graphics for 100 users in 2024')
    a = dict(candidate_id='c', evidence_units=[skill], normalized_skills=['docker'])
    b = dict(a, evidence_units=[skill, project])
    first = match_requirement(req, a, aliases={}, ontology={})
    second = match_requirement(req, b, aliases={}, ontology={})
    assert second.evidence_strength == first.evidence_strength == .25
    assert second.evidence_ids == ['skill']
    assert second.final_requirement_score == first.final_requirement_score


def test_experience_ignores_unmatched_projects():
    candidate = dict(evidence_units=[ev('yes', 'Built a React app'), ev('no', 'Built unrelated artwork')])
    matches = [dict(final_requirement_score=.8, evidence_ids=['yes'])]
    assert calculate_experience_relevance(candidate, matches) == .5
    assert calculate_experience_relevance(candidate, []) == 0


def test_empty_requirements_fail_before_model_loading():
    with pytest.raises(ValueError, match='No JD requirements'):
        rank_candidates({'requirements': []}, [])


def test_empty_resume_evidence_reports_candidate():
    with pytest.raises(ValueError, match='no usable resume evidence'):
        rank_candidates({'requirements': [dict(requirement_id='r')]},
                        [dict(candidate_id='empty', evidence_units=[])])


def test_unfamiliar_skill_is_not_dropped():
    req = dict(requirement_id='new', text='Elixir', canonical='elixir', category='technology')
    candidate = dict(candidate_id='c', evidence_units=[ev('new_ev', 'Built services using Elixir')])
    match = match_requirement(req, candidate, aliases={}, ontology={})
    assert match.keyword_score > 0
    assert match.evidence_ids == ['new_ev']
