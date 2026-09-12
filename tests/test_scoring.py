"""Unit tests for the NEXORA ranking, scoring, confidence, and sensitivity engine."""

import pytest
from nexora.config import MODEL_PATH
from nexora.matching.ontology import load_aliases, load_ontology
from nexora.matching.semantic_engine import load_embedding_model
from nexora.ranking.scoring import rank_candidates
from nexora.schemas import Candidate, EvidenceUnit, JobDescription, Requirement


@pytest.fixture(scope="session")
def embedding_model():
    return load_embedding_model(MODEL_PATH)


@pytest.fixture(scope="session")
def ontology_data():
    return load_ontology()


@pytest.fixture(scope="session")
def aliases_data():
    return load_aliases()


@pytest.fixture
def sample_fullstack_jd():
    return JobDescription(
        jd_id="jd_fullstack",
        title="Full Stack Developer",
        requirements=[
            Requirement(
                requirement_id="req_react",
                text="React frontend web development",
                canonical="react",
                category="technology",
                requirement_type="required",
                importance=1.25,
                aliases=["react", "reactjs", "react.js"],
            ),
            Requirement(
                requirement_id="req_node",
                text="Node.js backend development",
                canonical="node.js",
                category="technology",
                requirement_type="required",
                importance=1.25,
                aliases=["node", "nodejs", "node.js"],
                related_skills=[{"canonical": "express", "support": 0.75}],
            ),
            Requirement(
                requirement_id="req_mongo",
                text="MongoDB database management",
                canonical="mongodb",
                category="technology",
                requirement_type="required",
                importance=1.00,
                aliases=["mongodb", "mongo", "mongo db"],
            ),
            Requirement(
                requirement_id="req_docker",
                text="Docker container deployment",
                canonical="docker",
                category="technology",
                requirement_type="preferred",
                importance=0.45,
                aliases=["docker", "containerized"],
            ),
        ],
    )


def test_anti_keyword_stuffing_detection(embedding_model, aliases_data, ontology_data, sample_fullstack_jd):
    """A candidate who lists 20 skills in skills section but has 0 project evidence must be flagged."""
    stuffer = Candidate(
        candidate_id="cand_stuffer",
        name="Keyword Stuffer",
        normalized_skills=[
            "react", "node.js", "mongodb", "docker", "aws", "python",
            "java", "c++", "kubernetes", "sql", "git", "linux", "html", "css"
        ],
        evidence_units=[
            # Only skills section occurrences
            EvidenceUnit(
                evidence_id="ev_stuff_1",
                candidate_id="cand_stuffer",
                text="React, Node.js, MongoDB, Docker, AWS, Python, Java, C++, Kubernetes",
                normalized_text="react node.js mongodb docker aws python java c++ kubernetes",
                section="skills",
                has_action_verb=False,
                has_outcome=False,
            )
        ],
    )

    legit = Candidate(
        candidate_id="cand_legit",
        name="Legitimate Developer",
        normalized_skills=["react", "node.js"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_legit_1",
                candidate_id="cand_legit",
                text="Developed full-stack web application using React and Node.js for 1000 active users.",
                normalized_text="developed full-stack web application using react and node.js for 1000 active users.",
                section="projects",
                has_action_verb=True,
                has_outcome=True,
            )
        ],
    )

    result = rank_candidates(
        jd=sample_fullstack_jd,
        candidates=[stuffer, legit],
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    stuffer_score = next(c for c in result.ranked_candidates if c.candidate_id == "cand_stuffer")
    legit_score = next(c for c in result.ranked_candidates if c.candidate_id == "cand_legit")

    # The stuffer must be flagged with lexical_only_pattern
    assert stuffer_score.lexical_only_pattern is True
    # The legitimate developer with demonstrated project evidence must outrank the stuffer!
    assert legit_score.rank < stuffer_score.rank
    assert legit_score.score > stuffer_score.score


def test_missing_required_penalty(embedding_model, aliases_data, ontology_data, sample_fullstack_jd):
    """Missing a required technology must trigger a missing penalty and populate missing_required."""
    cand = Candidate(
        candidate_id="cand_no_db",
        name="Frontend Only",
        normalized_skills=["react"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_fe",
                candidate_id="cand_no_db",
                text="Engineered responsive client dashboards with React.",
                normalized_text="engineered responsive client dashboards with react.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    result = rank_candidates(
        jd=sample_fullstack_jd,
        candidates=[cand],
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    cand_res = result.ranked_candidates[0]
    # node.js and mongodb are required and missing
    assert "node.js" in cand_res.missing_required or "mongodb" in cand_res.missing_required


def test_preferred_cannot_dominate_required(embedding_model, aliases_data, ontology_data, sample_fullstack_jd):
    """A candidate with preferred Docker but missing required Node.js must not outrank a candidate with Node.js."""
    cand_has_required = Candidate(
        candidate_id="cand_node",
        name="Has Required Node",
        normalized_skills=["node.js"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_n",
                candidate_id="cand_node",
                text="Built backend microservices using Node.js.",
                normalized_text="built backend microservices using node.js.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    cand_has_preferred = Candidate(
        candidate_id="cand_docker",
        name="Has Preferred Docker Only",
        normalized_skills=["docker"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_d",
                candidate_id="cand_docker",
                text="Configured Docker containers for simple scripts.",
                normalized_text="configured docker containers for simple scripts.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    result = rank_candidates(
        jd=sample_fullstack_jd,
        candidates=[cand_has_preferred, cand_has_required],
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    top_cand = result.ranked_candidates[0]
    assert top_cand.candidate_id == "cand_node"
    assert top_cand.score > result.ranked_candidates[1].score


def test_ranking_sensitivity_analysis(embedding_model, aliases_data, ontology_data, sample_fullstack_jd):
    """Sensitivity analysis must test [0.30, 0.40, 0.50] and output stable flag."""
    c1 = Candidate(
        candidate_id="c1",
        name="Dev 1",
        normalized_skills=["react", "node.js", "mongodb"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_c1",
                candidate_id="c1",
                text="Developed complete full-stack web applications using React, Node.js, and MongoDB.",
                normalized_text="developed complete full-stack web applications using react, node.js, and mongodb.",
                section="experience",
                has_action_verb=True,
                has_outcome=True,
            )
        ],
    )
    c2 = Candidate(
        candidate_id="c2",
        name="Dev 2",
        normalized_skills=["react"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_c2",
                candidate_id="c2",
                text="Built React frontend interfaces.",
                normalized_text="built react frontend interfaces.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    result = rank_candidates(
        jd=sample_fullstack_jd,
        candidates=[c1, c2],
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    sensitivity = result.sensitivity
    assert sensitivity.semantic_weights_tested == [0.30, 0.40, 0.50]
    assert isinstance(sensitivity.stable_top_three, bool)
    assert c1.candidate_id == result.ranked_candidates[0].candidate_id
