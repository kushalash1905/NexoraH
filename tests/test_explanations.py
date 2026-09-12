import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import pytest
except ImportError:
    class PytestFallback:
        @staticmethod
        def fixture(func):
            return func

        @staticmethod
        def raises(exc):
            class DummyRaises:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    return exc_type is not None and issubclass(exc_type, exc)
            return DummyRaises()

    pytest = PytestFallback()
from nexora.explanations.generator import (
    generate_top_three_explanations,
    get_missing_requirements,
    get_improvement_opportunities,
    build_normalization_summary
)
from nexora.explanations.comparison import compare_candidates, recruiter_answer
from nexora.jd_analysis.bias_detector import detect_bias_flags


@pytest.fixture
def sample_jd():
    return {
        "jd_id": "jd_test",
        "title": "Junior Full Stack Intern",
        "company": "TechNova",
        "raw_text": "Junior Full Stack Intern required. Must have 2+ years of experience. Strictly required: Node.js, React, MongoDB.",
        "requirements": [
            {
                "requirement_id": "req_node",
                "text": "Node.js backend development",
                "canonical": "node.js",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25
            },
            {
                "requirement_id": "req_react",
                "text": "React frontend development",
                "canonical": "react",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25
            },
            {
                "requirement_id": "req_docker",
                "text": "Docker containerization",
                "canonical": "docker",
                "category": "technology",
                "requirement_type": "preferred",
                "importance": 0.45
            }
        ]
    }


@pytest.fixture
def sample_ranking():
    return {
        "jd_id": "jd_test",
        "candidate_count": 2,
        "ranked_candidates": [
            {
                "candidate_id": "candidate_001",
                "name": "Candidate 1",
                "rank": 1,
                "score": 85.0,
                "confidence": 88.0,
                "confidence_label": "High",
                "required_coverage": 0.90,
                "preferred_coverage": 0.50,
                "keyword_alignment": 0.80,
                "semantic_alignment": 0.82,
                "evidence_strength": 0.85,
                "missing_required": ["typescript"],
                "requirement_matches": [
                    {
                        "candidate_id": "candidate_001",
                        "requirement_id": "req_node",
                        "final_requirement_score": 0.85,
                        "keyword_score": 0.9,
                        "semantic_score": 0.8,
                        "evidence_ids": ["ev_001_01"]
                    },
                    {
                        "candidate_id": "candidate_001",
                        "requirement_id": "req_react",
                        "final_requirement_score": 0.80,
                        "keyword_score": 0.8,
                        "semantic_score": 0.8,
                        "evidence_ids": ["ev_001_02"]
                    }
                ]
            },
            {
                "candidate_id": "candidate_002",
                "name": "Candidate 2",
                "rank": 2,
                "score": 50.0,
                "confidence": 60.0,
                "confidence_label": "Medium",
                "required_coverage": 0.40,
                "preferred_coverage": 0.00,
                "keyword_alignment": 0.40,
                "semantic_alignment": 0.45,
                "evidence_strength": 0.50,
                "missing_required": ["node.js", "react"],
                "requirement_matches": [
                    {
                        "candidate_id": "candidate_002",
                        "requirement_id": "req_node",
                        "final_requirement_score": 0.10,
                        "keyword_score": 0.0,
                        "semantic_score": 0.2,
                        "evidence_ids": []
                    }
                ]
            }
        ]
    }


def test_top_three_explanations(sample_ranking, sample_jd):
    candidates = [
        {
            "candidate_id": "candidate_001",
            "name": "Candidate 1",
            "evidence_units": [
                {"evidence_id": "ev_001_01", "text": "Built Node.js APIs.", "section": "projects", "page": 1},
                {"evidence_id": "ev_001_02", "text": "React development experience.", "section": "experience", "page": 1}
            ]
        }
    ]
    explanations = generate_top_three_explanations(sample_ranking, sample_jd, candidates)
    assert len(explanations) == 2
    assert explanations[0]["candidate_id"] == "candidate_001"
    assert "Candidate 1 ranked #1" in explanations[0]["summary"]


def test_candidate_comparison(sample_ranking, sample_jd):
    comp = compare_candidates("candidate_001", "candidate_002", sample_ranking, sample_jd, [])
    assert comp["candidate_a"] == "candidate_001"
    assert comp["candidate_b"] == "candidate_002"
    assert comp["score_difference"] == 35.0
    assert len(comp["top_requirement_contributors"]) > 0


def test_recruiter_question_answering(sample_ranking, sample_jd):
    ans = recruiter_answer("Why is candidate candidate_001 ranked above candidate candidate_002?", sample_ranking, sample_jd, [])
    assert ans["intent"] == "why_ranked_above"
    assert "Candidate 1 ranks above Candidate 2" in ans["answer"]


def test_missing_requirements(sample_ranking, sample_jd):
    cand_score = sample_ranking["ranked_candidates"][1]
    missing_info = get_missing_requirements(cand_score, sample_jd)
    assert len(missing_info["missing_required"]) > 0
    assert "No reliable evidence was found for node.js" in missing_info["missing_required"][0]


def test_improvement_opportunities(sample_ranking, sample_jd):
    cand_score = sample_ranking["ranked_candidates"][1]
    opps = get_improvement_opportunities(cand_score, sample_jd)
    assert len(opps["improvement_opportunities"]) > 0


def test_bias_detector(sample_jd):
    flags = detect_bias_flags(sample_jd)
    assert len(flags) > 0
    phrases = [f["phrase"] for f in flags]
    assert any("2+ years" in p for p in phrases) or any("strictly required" in p for p in phrases)


def test_normalization_summary():
    candidates = [
        {
            "candidate_id": "cand_01",
            "name": "Test Candidate",
            "extraction_quality": 0.95,
            "normalization_log": [{"raw": "NodeJS", "normalized": "node.js"}],
            "quality_flags": ["text_extracted"]
        }
    ]
    summary = build_normalization_summary(candidates)
    assert len(summary) == 1
    assert summary[0]["extraction_quality"] == 95.0


if __name__ == "__main__":
    jd = sample_jd()
    ranking = sample_ranking()
    test_top_three_explanations(ranking, jd)
    test_candidate_comparison(ranking, jd)
    test_recruiter_question_answering(ranking, jd)
    test_missing_requirements(ranking, jd)
    test_improvement_opportunities(ranking, jd)
    test_bias_detector(jd)
    test_normalization_summary()
    print("[PASS] All explanation tests passed successfully.")
