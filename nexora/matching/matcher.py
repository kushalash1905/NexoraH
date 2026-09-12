"""Requirement matcher for NEXORA.

Coordinates keyword evaluation, semantic similarity, ontology support,
context guards, evidence quality, and anti-keyword-stuffing verification
to produce authoritative RequirementMatch objects.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from sentence_transformers import SentenceTransformer

from nexora.config import (
    MATCH_KEYWORD_WEIGHT,
    MATCH_ONTOLOGY_WEIGHT,
    MATCH_SEMANTIC_WEIGHT,
    STATUS_PARTIAL_THRESHOLD,
    STATUS_STRONG_THRESHOLD,
    STATUS_WEAK_THRESHOLD,
    TECH_CONTEXT_GUARD_PENALTY,
)
from nexora.matching.evidence_retriever import (
    calculate_evidence_strength,
    retrieve_and_combine_evidence,
)
from nexora.matching.keyword_engine import calculate_keyword_score
from nexora.matching.ontology import _get_req_field, calculate_ontology_support
from nexora.matching.semantic_engine import calculate_semantic_score
from nexora.schemas import Candidate, EvidenceUnit, Requirement, RequirementMatch


def calculate_context_guard(
    requirement: Union[Requirement, Dict[str, Any]],
    keyword_score: float,
    semantic_score: float,
    ontology_support: float,
) -> float:
    """Calculate contextual guard factor to suppress semantic false positives.
    
    For technology requirements:
    If there is no exact match, no alias match, and no ontology relationship
    (i.e. keyword_score == 0 and ontology_support == 0), then semantic similarity
    is restricted to TECH_CONTEXT_GUARD_PENALTY (0.25).
    
    Example:
    'Designed Photoshop mockups' evaluated against 'React frontend development'
    receives context_guard = 0.25, ensuring it stays well below the 0.30 threshold.
    """
    category = str(_get_req_field(requirement, "category", "technology")).strip().lower()
    if category == "technology":
        if keyword_score <= 0.05 and ontology_support <= 0.05:
            return TECH_CONTEXT_GUARD_PENALTY

    return 1.0


def classify_match(score: float) -> str:
    """Classify requirement match status based on authoritative thresholds."""
    if score >= STATUS_STRONG_THRESHOLD:
        return "strong_match"
    elif score >= STATUS_PARTIAL_THRESHOLD:
        return "partial_match"
    elif score >= STATUS_WEAK_THRESHOLD:
        return "weak_match"
    return "no_reliable_evidence"


def calculate_match_confidence(
    keyword_score: float,
    semantic_score: float,
    evidence_strength: float,
) -> float:
    """Compute local requirement match confidence in [0.0, 1.0]."""
    signal_agreement = 1.0 - abs(keyword_score - semantic_score)
    conf = 0.45 * evidence_strength + 0.35 * max(keyword_score, semantic_score) + 0.20 * signal_agreement
    return round(float(min(1.0, max(0.0, conf))), 4)


def _match_evidence(
    requirement: Union[Requirement, Dict[str, Any]],
    candidate: Union[Candidate, Dict[str, Any]],
    all_candidates: Optional[List[Union[Candidate, Dict[str, Any]]]] = None,
    model: Optional[SentenceTransformer] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
    max_candidate_bm25: Optional[float] = None,
    verification_factor: float = 1.0,
) -> RequirementMatch:
    """Evaluate a single requirement against a candidate's structured resume.
    
    Executes:
    1. Independent BM25 and Semantic retrieval.
    2. Evidence combination and provenance tracking.
    3. Keyword scoring with token boundaries and fuzzy matching.
    4. Local offline semantic embedding similarity.
    5. Ontology support lookup.
    6. Technology context guard verification.
    7. Evidence quality weighting.
    8. Composite hybrid requirement score calculation:
       M = E * (0.40*K + 0.40*S + 0.20*O) * guard
    """
    # Extract evidence units
    if isinstance(candidate, dict):
        evidence_units = candidate.get("evidence_units", [])
        cand_id = str(candidate.get("candidate_id", "unknown"))
    else:
        evidence_units = getattr(candidate, "evidence_units", [])
        cand_id = str(getattr(candidate, "candidate_id", "unknown"))

    req_id = str(_get_req_field(requirement, "requirement_id", "unknown"))

    # 1. Retrieve & combine evidence independently
    combined_evidence, evidence_ids_used = retrieve_and_combine_evidence(
        requirement=requirement,
        evidence_units=evidence_units,
        model=model,
        aliases=aliases,
        ontology=ontology,
        top_k=5,
    )

    # 2. Keyword score
    raw_keyword, kw_breakdown = calculate_keyword_score(
        requirement=requirement,
        evidence_units=combined_evidence if combined_evidence else evidence_units,
        candidate=candidate,
        aliases=aliases,
        ontology=ontology,
        max_candidate_bm25=max_candidate_bm25,
    )
    # Apply anti-keyword-stuffing verification adjustment if applicable
    adjusted_keyword = round(float(raw_keyword * (0.65 + 0.35 * verification_factor)), 4)

    # 3. Semantic score
    raw_semantic = 0.0
    if model is not None and combined_evidence:
        raw_semantic, _ = calculate_semantic_score(
            requirement=requirement,
            evidence_units=combined_evidence,
            model=model,
        )

    # 4. Ontology support
    exact_matched = kw_breakdown.get("k_exact", 0.0) > 0.0
    alias_matched = kw_breakdown.get("k_alias", 0.0) > 0.0
    ontology_support = calculate_ontology_support(
        requirement=requirement,
        evidence_units=combined_evidence if combined_evidence else evidence_units,
        candidate=candidate,
        ontology=ontology,
        aliases=aliases,
        exact_matched=exact_matched,
        alias_matched=alias_matched,
    )

    # 5. Best evidence strength
    if combined_evidence:
        best_ev_strength = max(
            [calculate_evidence_strength(ev, requirement) for ev in combined_evidence]
        )
    else:
        # Fallback to skills section level strength if skills listed in candidate
        best_ev_strength = 0.25 if exact_matched or alias_matched else 0.0

    # 6. Context guard
    context_guard = calculate_context_guard(
        requirement=requirement,
        keyword_score=adjusted_keyword,
        semantic_score=raw_semantic,
        ontology_support=ontology_support,
    )

    # 7. Final requirement score
    inner_score = (
        MATCH_KEYWORD_WEIGHT * adjusted_keyword
        + MATCH_SEMANTIC_WEIGHT * raw_semantic
        + MATCH_ONTOLOGY_WEIGHT * ontology_support
    )
    final_score = best_ev_strength * inner_score * context_guard
    final_score = round(float(min(1.0, max(0.0, final_score))), 4)

    # 8. Status and confidence
    status = classify_match(final_score)
    confidence = calculate_match_confidence(
        keyword_score=adjusted_keyword,
        semantic_score=raw_semantic,
        evidence_strength=best_ev_strength,
    )

    return RequirementMatch(
        candidate_id=cand_id,
        requirement_id=req_id,
        keyword_score=round(adjusted_keyword, 4),
        semantic_score=round(raw_semantic, 4),
        ontology_support=round(ontology_support, 4),
        evidence_strength=round(best_ev_strength, 4),
        context_guard=round(context_guard, 4),
        final_requirement_score=final_score,
        status=status,
        confidence=confidence,
        evidence_ids=evidence_ids_used[:2],
    )


def match_requirement(
    requirement, candidate, all_candidates=None, model=None, aliases=None,
    ontology=None, max_candidate_bm25=None, verification_factor=1.0,
) -> RequirementMatch:
    """Score each retrieved excerpt independently; retain the actual winner.

    Candidate-wide skill lists must not transfer credit to unrelated projects.
    The winning excerpt supplies keyword, semantic, ontology and quality signals.
    """
    cand = candidate if isinstance(candidate, dict) else candidate.model_dump()
    evidence = cand.get("evidence_units", [])
    selected, _ = retrieve_and_combine_evidence(
        requirement, evidence, model=model, aliases=aliases,
        ontology=ontology, top_k=5,
    )
    if not selected:
        return RequirementMatch(
            candidate_id=str(cand.get("candidate_id", "unknown")),
            requirement_id=str(_get_req_field(requirement, "requirement_id", "unknown")),
        )
    results = []
    for ev in selected:
        local_candidate = dict(cand, evidence_units=[ev], normalized_skills=[])
        result = _match_evidence(
            requirement, local_candidate, all_candidates, model, aliases,
            ontology, max_candidate_bm25, verification_factor,
        )
        # No evidence claim for a completely unsupported excerpt.
        if result.keyword_score == 0 and result.ontology_support == 0 and result.semantic_score == 0:
            result.evidence_ids = []
        results.append(result)
    return max(results, key=lambda m: (
        m.final_requirement_score, m.semantic_score, m.keyword_score,
    ))
