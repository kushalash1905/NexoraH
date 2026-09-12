"""Unit tests for the NEXORA matching engine."""

import pytest
from nexora.config import MODEL_PATH
from nexora.matching.evidence_retriever import (
    calculate_evidence_strength,
    retrieve_and_combine_evidence,
)
from nexora.matching.keyword_engine import (
    calculate_alias_match,
    calculate_exact_match,
    calculate_fuzzy_match,
    calculate_keyword_score,
    normalize_match_text,
    retrieve_bm25,
)
from nexora.matching.matcher import calculate_context_guard, match_requirement
from nexora.matching.ontology import (
    calculate_ontology_support,
    get_aliases,
    get_related_skills,
    load_aliases,
    load_ontology,
)
from nexora.matching.semantic_engine import calculate_semantic_score, load_embedding_model
from nexora.schemas import Candidate, EvidenceUnit, Requirement


@pytest.fixture(scope="session")
def embedding_model():
    """Load the local offline sentence-transformers model once for all tests."""
    return load_embedding_model(MODEL_PATH)


@pytest.fixture(scope="session")
def ontology_data():
    return load_ontology()


@pytest.fixture(scope="session")
def aliases_data():
    return load_aliases()


def test_token_safe_exact_match():
    """Java must not match JavaScript."""
    req_java = Requirement(
        requirement_id="req_java",
        text="Java",
        canonical="java",
        category="technology",
    )
    ev_js = [
        EvidenceUnit(
            evidence_id="ev_1",
            candidate_id="c_1",
            text="Developed web frontends using JavaScript and TypeScript.",
            normalized_text="developed web frontends using javascript and typescript.",
            section="projects",
        )
    ]
    # Exact match for Java against JavaScript should be 0.0
    exact_score = calculate_exact_match(req_java, ev_js)
    assert exact_score == 0.0

    # Exact match for Java against Java should be 1.0
    ev_java = [
        EvidenceUnit(
            evidence_id="ev_2",
            candidate_id="c_2",
            text="Developed backend microservices in Java using Spring Boot.",
            normalized_text="developed backend microservices in java using spring boot.",
            section="experience",
        )
    ]
    assert calculate_exact_match(req_java, ev_java) == 1.0


def test_alias_match(aliases_data, ontology_data):
    """'NodeJS' in resume must match 'Node.js' requirement via aliases."""
    req_node = Requirement(
        requirement_id="req_node",
        text="Node.js backend development",
        canonical="node.js",
        category="technology",
        aliases=["node", "nodejs", "node.js"],
    )
    ev_nodejs = [
        EvidenceUnit(
            evidence_id="ev_3",
            candidate_id="c_3",
            text="Built asynchronous event-driven services using NodeJS.",
            normalized_text="built asynchronous event-driven services using nodejs.",
            section="projects",
        )
    ]
    alias_score = calculate_alias_match(req_node, ev_nodejs, aliases=aliases_data, ontology=ontology_data)
    assert alias_score == 1.0


def test_fuzzy_match_conservative_cap():
    """Fuzzy matching must catch minor typos but cap credit at 0.45."""
    req_react = Requirement(
        requirement_id="req_react",
        text="React",
        canonical="react",
        category="technology",
    )
    # Typo: 'reakt' instead of 'react'
    ev_typo = [
        EvidenceUnit(
            evidence_id="ev_4",
            candidate_id="c_4",
            text="Created UI components using Reakt framework.",
            normalized_text="created ui components using reakt framework.",
            section="projects",
        )
    ]
    fuzzy_score = calculate_fuzzy_match(req_react, ev_typo)
    assert 0.0 < fuzzy_score <= 0.45


def test_bm25_retrieval(aliases_data, ontology_data):
    """BM25 retrieves the most lexically relevant evidence unit."""
    req = Requirement(
        requirement_id="req_mongo",
        text="MongoDB database queries and indexing",
        canonical="mongodb",
        category="technology",
    )
    units = [
        EvidenceUnit(
            evidence_id="ev_irrelevant",
            candidate_id="c_5",
            text="Created vector graphics in Figma for user stories.",
            normalized_text="created vector graphics in figma for user stories.",
            section="projects",
        ),
        EvidenceUnit(
            evidence_id="ev_relevant",
            candidate_id="c_5",
            text="Designed MongoDB database schema and optimized aggregation queries.",
            normalized_text="designed mongodb database schema and optimized aggregation queries.",
            section="experience",
        ),
    ]
    results = retrieve_bm25(req, units, top_k=1, aliases=aliases_data, ontology=ontology_data)
    assert len(results) == 1
    best_unit, score = results[0]
    assert best_unit.evidence_id == "ev_relevant"
    assert score > 0.0


def test_evidence_strength_calculation():
    """Skills-section text gets ~0.25; project with action verbs and outcomes gets >0.75."""
    ev_skills = EvidenceUnit(
        evidence_id="ev_s",
        candidate_id="c_6",
        text="Docker",
        normalized_text="docker",
        section="skills",
    )
    strength_skills = calculate_evidence_strength(ev_skills)
    assert strength_skills == 0.25

    ev_project = EvidenceUnit(
        evidence_id="ev_p",
        candidate_id="c_6",
        text="Containerized and deployed microservices using Docker for 500 users.",
        normalized_text="containerized and deployed microservices using docker for 500 users.",
        section="projects",
        has_action_verb=True,
        has_outcome=True,
    )
    strength_project = calculate_evidence_strength(ev_project)
    assert strength_project >= 0.80


def test_express_partial_support_for_node(embedding_model, aliases_data, ontology_data):
    """Express and REST API must provide ontology support for Node.js without exact match."""
    req_node = Requirement(
        requirement_id="req_node",
        text="Node.js backend development",
        canonical="node.js",
        category="technology",
        importance=1.25,
        aliases=["node", "nodejs", "node.js"],
        related_skills=[
            {"canonical": "express", "support": 0.75},
            {"canonical": "rest api", "support": 0.55},
        ],
    )
    candidate = Candidate(
        candidate_id="cand_express",
        name="Express Developer",
        normalized_skills=["express", "rest api"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_exp",
                candidate_id="cand_express",
                text="Built REST APIs using Express and MongoDB for web platform.",
                normalized_text="built rest apis using express and mongodb for web platform.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    match = match_requirement(
        requirement=req_node,
        candidate=candidate,
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    # Exact Node.js keyword match is 0 (or small BM25 if any), but ontology support must be 0.75
    assert match.ontology_support >= 0.75
    assert match.semantic_score > 0.40
    assert match.context_guard == 1.0  # Protected from penalty because ontology_support exists!
    assert match.final_requirement_score > 0.25  # Meaningful partial credit


def test_photoshop_false_positive_suppressed(embedding_model, aliases_data, ontology_data):
    """'Photoshop mockups' evaluated against 'React' must be suppressed by context guard."""
    req_react = Requirement(
        requirement_id="req_react",
        text="React frontend development",
        canonical="react",
        category="technology",
        importance=1.25,
        aliases=["react", "reactjs", "react.js"],
    )
    candidate = Candidate(
        candidate_id="cand_designer",
        name="UI Designer",
        normalized_skills=["photoshop", "figma"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="ev_ps",
                candidate_id="cand_designer",
                text="Designed interactive Photoshop mockups and graphic prototypes.",
                normalized_text="designed interactive photoshop mockups and graphic prototypes.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )

    match = match_requirement(
        requirement=req_react,
        candidate=candidate,
        model=embedding_model,
        aliases=aliases_data,
        ontology=ontology_data,
    )

    assert match.keyword_score == 0.0
    assert match.ontology_support == 0.0
    assert match.context_guard == 0.25  # Guard triggered!
    assert match.final_requirement_score < 0.30
    assert match.status == "no_reliable_evidence"
