"""Candidate scoring and ranking engine for NEXORA.

Implements authoritative composite scoring, requirement weighting,
missing required penalties, anti-keyword-stuffing verification, experience relevance,
confidence calculation, and deterministic candidate ranking.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from sentence_transformers import SentenceTransformer

from nexora.config import (
    FINAL_CONFIDENCE_WEIGHT,
    FINAL_COVERAGE_WEIGHT,
    FINAL_EXPERIENCE_WEIGHT,
    LEXICAL_ONLY_DEMONSTRATED_THRESHOLD,
    LEXICAL_ONLY_KEYWORD_THRESHOLD,
    MISSING_REQUIRED_PENALTY_COEFF,
    STATUS_PARTIAL_THRESHOLD,
    STATUS_WEAK_THRESHOLD,
    WEIGHT_CONTEXTUAL,
    WEIGHT_PREFERRED,
    WEIGHT_REQUIRED_STANDARD,
    WEIGHT_REQUIRED_TECH,
)
from nexora.matching.matcher import match_requirement
from nexora.matching.ontology import (
    _get_req_field,
    load_aliases,
    load_ontology,
)
from nexora.matching.semantic_engine import load_embedding_model
from nexora.ranking.confidence import (
    calculate_candidate_confidence,
    confidence_label,
)
from nexora.ranking.sensitivity import calculate_sensitivity
from nexora.schemas import (
    Candidate,
    CandidateScore,
    JobDescription,
    RankingResult,
    Requirement,
    RequirementMatch,
)


def requirement_weight(requirement: Union[Requirement, Dict[str, Any]]) -> float:
    """Determine the importance weight W(r) of a requirement."""
    importance = float(_get_req_field(requirement, "importance", 0.0))
    if importance > 0.0:
        return importance

    r_type = str(_get_req_field(requirement, "requirement_type", "required")).strip().lower()
    r_cat = str(_get_req_field(requirement, "category", "technology")).strip().lower()

    if r_type == "required":
        if r_cat == "technology":
            return WEIGHT_REQUIRED_TECH
        return WEIGHT_REQUIRED_STANDARD
    elif r_type == "preferred":
        return WEIGHT_PREFERRED
    return WEIGHT_CONTEXTUAL


def calculate_missing_penalty(
    requirements: List[Union[Requirement, Dict[str, Any]]],
    matches: List[Union[RequirementMatch, Dict[str, Any]]],
) -> Tuple[float, List[str]]:
    """Compute the missing required penalty and list missing canonical requirements.
    
    Penalty formula:
    P_missing = 0.12 * [sum_{r in req}(indicator(M < 0.30) * W(r))] / sum_{all r}(W(r))
    """
    total_weight = sum([requirement_weight(r) for r in requirements])
    if total_weight <= 0:
        return 0.0, []

    missing_weight = 0.0
    missing_names: List[str] = []

    for req, m in zip(requirements, matches):
        r_type = str(_get_req_field(req, "requirement_type", "required")).strip().lower()
        score = float(_get_req_field(m, "final_requirement_score", 0.0))
        canonical = str(_get_req_field(req, "canonical", "") or _get_req_field(req, "text", "")).strip().lower()

        if r_type == "required" and score < STATUS_WEAK_THRESHOLD:
            missing_weight += requirement_weight(req)
            missing_names.append(canonical)

    penalty = MISSING_REQUIRED_PENALTY_COEFF * (missing_weight / total_weight)
    return round(float(penalty), 4), missing_names


def calculate_experience_relevance(
    candidate: Union[Candidate, Dict[str, Any]],
    matches: List[Union[RequirementMatch, Dict[str, Any]]],
) -> float:
    """Calculate experience relevance X(c).
    
    Formula:
    X(c) = relevant_demonstrated_evidence / (all_relevant_evidence + 1)
    """
    if isinstance(candidate, dict):
        evidence_units = candidate.get("evidence_units", [])
    else:
        evidence_units = getattr(candidate, "evidence_units", [])

    if not evidence_units:
        return 0.0

    relevant_ids = {
        str(eid)
        for match in matches
        if float(_get_req_field(match, "final_requirement_score", 0.0)) >= STATUS_WEAK_THRESHOLD
        for eid in _get_req_field(match, "evidence_ids", [])
    }
    relevant = [ev for ev in evidence_units
                if str(_get_req_field(ev, "evidence_id", "")) in relevant_ids]
    demonstrated_sections = {"projects", "project", "experience", "work experience", "internship", "internships"}
    demonstrated = sum(
        1 for ev in relevant
        if str(_get_req_field(ev, "section", "")).strip().lower() in demonstrated_sections
        and bool(_get_req_field(ev, "has_action_verb", False))
    )
    return round(demonstrated / float(len(relevant) + 1), 4)


def anti_keyword_stuffing_audit(
    candidate: Union[Candidate, Dict[str, Any]],
    requirements: List[Union[Requirement, Dict[str, Any]]],
    raw_matches: List[RequirementMatch],
) -> Tuple[float, bool]:
    """Audit candidate profile for lexical-only keyword stuffing patterns.
    
    Definitions:
    - matched_count = number of requirements with keyword support
    - demonstrated_count = number of matched requirements supported by project/experience evidence
    - evidence_unit_count = number of relevant evidence units
    
    Returns:
        (verification_factor, lexical_only_pattern_detected)
    """
    if isinstance(candidate, dict):
        evidence_units = candidate.get("evidence_units", [])
        cand_skills = candidate.get("normalized_skills", [])
    else:
        evidence_units = getattr(candidate, "evidence_units", [])
        cand_skills = getattr(candidate, "normalized_skills", [])

    demonstrated_sections = {"projects", "project", "experience", "work experience", "internship", "internships"}
    
    matched_count = sum([1 for m in raw_matches if m.keyword_score > 0.10])
    demonstrated_count = 0

    for m in raw_matches:
        if m.keyword_score > 0.10 and m.evidence_strength >= 0.50:
            demonstrated_count += 1

    ev_count = len(evidence_units)
    if matched_count == 0:
        return 1.0, False

    demonstrated_ratio = demonstrated_count / float(matched_count)
    unit_ratio = min(1.0, ev_count / float(matched_count))

    verification = 0.70 * demonstrated_ratio + 0.30 * unit_ratio
    verification = float(min(1.0, max(0.0, verification)))

    # Diagnostic trigger: high keyword coverage but very low demonstrated evidence
    keyword_coverage = matched_count / float(max(1, len(requirements)))
    is_lexical_only = (
        keyword_coverage >= LEXICAL_ONLY_KEYWORD_THRESHOLD
        and demonstrated_ratio < LEXICAL_ONLY_DEMONSTRATED_THRESHOLD
    )

    return round(verification, 4), is_lexical_only


def score_candidate(
    candidate: Union[Candidate, Dict[str, Any]],
    requirements: List[Union[Requirement, Dict[str, Any]]],
    matches: List[RequirementMatch],
    extraction_quality: float = 1.0,
    is_lexical_only: bool = False,
) -> CandidateScore:
    """Compute final candidate score and detailed alignment metrics."""
    cand_id = str(_get_req_field(candidate, "candidate_id", "unknown"))
    name = str(_get_req_field(candidate, "name", cand_id))

    total_weight = sum([requirement_weight(r) for r in requirements])
    if total_weight <= 0:
        total_weight = 1.0

    # 1. Total coverage
    cov_num = sum([requirement_weight(r) * m.final_requirement_score for r, m in zip(requirements, matches)])
    coverage = cov_num / total_weight

    # 2. Required coverage
    req_pairs = [(r, m) for r, m in zip(requirements, matches) if str(_get_req_field(r, "requirement_type", "required")).lower() == "required"]
    req_weight = sum([requirement_weight(r) for r, _ in req_pairs])
    if req_weight > 0:
        req_cov = sum([requirement_weight(r) * m.final_requirement_score for r, m in req_pairs]) / req_weight
    else:
        req_cov = coverage

    # 3. Preferred coverage
    pref_pairs = [(r, m) for r, m in zip(requirements, matches) if str(_get_req_field(r, "requirement_type", "")).lower() == "preferred"]
    pref_weight = sum([requirement_weight(r) for r, _ in pref_pairs])
    pref_cov = sum([requirement_weight(r) * m.final_requirement_score for r, m in pref_pairs]) / pref_weight if pref_weight > 0 else 0.0

    # 4. Missing penalty and missing canonical names
    missing_penalty, missing_required = calculate_missing_penalty(requirements, matches)

    # 5. Matched canonical names (>= partial match threshold or demonstrated evidence)
    matched_requirements = [
        str(_get_req_field(r, "canonical", "") or _get_req_field(r, "text", "")).strip().lower()
        for r, m in zip(requirements, matches)
        if m.final_requirement_score >= STATUS_PARTIAL_THRESHOLD
    ]

    # 6. Experience relevance
    exp_relevance = calculate_experience_relevance(candidate, matches)

    # 7. Confidence
    cand_ext_quality = float(_get_req_field(candidate, "extraction_quality", extraction_quality))
    conf_value = calculate_candidate_confidence(
        candidate=candidate,
        matches=matches,
        required_coverage=req_cov,
        extraction_quality=cand_ext_quality,
    )
    conf_pct = round(conf_value * 100.0, 1)
    conf_lbl = confidence_label(conf_value)

    # 8. Alignments
    kw_align = round(sum([m.keyword_score for m in matches]) / max(1, len(matches)), 4)
    sem_align = round(sum([m.semantic_score for m in matches]) / max(1, len(matches)), 4)
    ev_strength = round(sum([m.evidence_strength for m in matches]) / max(1, len(matches)), 4)

    # 9. Final Score Formula:
    # Score(c) = 100 * clip(0.78*coverage + 0.10*X + 0.07*C - P_missing, 0, 1)
    raw_final = (
        FINAL_COVERAGE_WEIGHT * coverage
        + FINAL_EXPERIENCE_WEIGHT * exp_relevance
        + FINAL_CONFIDENCE_WEIGHT * conf_value
        - missing_penalty
    )
    final_score = round(float(100.0 * min(1.0, max(0.0, raw_final))), 2)

    return CandidateScore(
        candidate_id=cand_id,
        name=name,
        rank=0,
        score=final_score,
        confidence=conf_pct,
        confidence_label=conf_lbl,
        required_coverage=round(float(req_cov), 4),
        preferred_coverage=round(float(pref_cov), 4),
        keyword_alignment=kw_align,
        semantic_alignment=sem_align,
        evidence_strength=ev_strength,
        experience_relevance=exp_relevance,
        missing_required=missing_required,
        matched_requirements=matched_requirements,
        requirement_matches=matches,
        lexical_only_pattern=is_lexical_only,
    )


def rank_candidates(
    jd: Union[JobDescription, Dict[str, Any]],
    candidates: List[Union[Candidate, Dict[str, Any]]],
    model: Optional[SentenceTransformer] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
) -> RankingResult:
    """Evaluate and rank all candidates against the given Job Description.
    
    100% offline, deterministic, and auditable.
    """
    from nexora.ranking.input_adapter import normalize_ranking_inputs
    jd, candidates = normalize_ranking_inputs(jd, candidates)
    jd_dict = jd
    requirements = jd_dict.get("requirements", [])
    if not requirements:
        raise ValueError("No JD requirements were extracted. Check the uploaded JD and parser.")
    requirement_ids = [str(_get_req_field(r, "requirement_id", "")) for r in requirements]
    if any(not rid for rid in requirement_ids) or len(set(requirement_ids)) != len(requirement_ids):
        raise ValueError("JD requirements must have nonempty unique requirement_id values.")
    candidate_ids = [str(_get_req_field(c, "candidate_id", "")) for c in candidates]
    if any(not cid for cid in candidate_ids) or len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("Candidates must have nonempty unique candidate_id values.")
    for cand in candidates:
        units = _get_req_field(cand, "evidence_units", [])
        if not any(str(_get_req_field(ev, "text", "") or _get_req_field(ev, "normalized_text", "")).strip() for ev in units):
            raise ValueError(f"Candidate {_get_req_field(cand, 'candidate_id', '')} has no usable resume evidence. Check PDF extraction.")

    if aliases is None:
        aliases = load_aliases()
    if ontology is None:
        ontology = load_ontology()
    if model is None:
        model = load_embedding_model()

    jd_dict = jd if isinstance(jd, dict) else jd.model_dump()
    requirements = jd_dict.get("requirements", [])
    jd_id = str(jd_dict.get("jd_id", "jd_001"))

    candidate_scores: List[CandidateScore] = []

    for cand in candidates:
        cand_dict = cand if isinstance(cand, dict) else cand.model_dump()

        # Step A: First pass matching to assess keyword vs evidence distribution
        initial_matches = [
            match_requirement(
                requirement=req,
                candidate=cand_dict,
                all_candidates=candidates,
                model=model,
                aliases=aliases,
                ontology=ontology,
                verification_factor=1.0,
            )
            for req in requirements
        ]

        # Step B: Anti-keyword-stuffing audit
        verif_factor, is_lexical_only = anti_keyword_stuffing_audit(cand_dict, requirements, initial_matches)

        # Step C: If verification penalty applies, compute final adjusted matches
        if verif_factor < 0.99:
            final_matches = [
                match_requirement(
                    requirement=req,
                    candidate=cand_dict,
                    all_candidates=candidates,
                    model=model,
                    aliases=aliases,
                    ontology=ontology,
                    verification_factor=verif_factor,
                )
                for req in requirements
            ]
        else:
            final_matches = initial_matches

        # Step D: Compute comprehensive candidate score
        cs = score_candidate(
            candidate=cand_dict,
            requirements=requirements,
            matches=final_matches,
            is_lexical_only=is_lexical_only,
        )
        candidate_scores.append(cs)

    # Sort deterministically: (-score, -required_coverage, -evidence_strength)
    candidate_scores.sort(
        key=lambda cs: (-cs.score, -cs.required_coverage, -cs.evidence_strength)
    )

    # Assign ranks 1 to N
    for rank_idx, cs in enumerate(candidate_scores, start=1):
        cs.rank = rank_idx

    # Sensitivity analysis
    sensitivity_result = calculate_sensitivity(
        jd=jd_dict,
        candidates=candidates,
        baseline_scores=candidate_scores,
    )

    return RankingResult(
        jd_id=jd_id,
        candidate_count=len(candidates),
        ranked_candidates=candidate_scores,
        top_three_explanations=[],
        sensitivity=sensitivity_result,
    )
