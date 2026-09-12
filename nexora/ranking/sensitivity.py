"""Ranking sensitivity analysis for NEXORA.

Evaluates how stable the top-ranked candidates are when semantic vs. keyword
weights are adjusted across [0.30, 0.40, 0.50].
Does NOT modify the baseline official ranking.
"""

from typing import Any, Dict, List, Union

from nexora.config import (
    FINAL_COVERAGE_WEIGHT,
    FINAL_EXPERIENCE_WEIGHT,
    MISSING_REQUIRED_PENALTY_COEFF,
    WEIGHT_REQUIRED_STANDARD,
    WEIGHT_REQUIRED_TECH,
)
from nexora.ranking.confidence import calculate_candidate_confidence
from nexora.schemas import Candidate, CandidateScore, RankingSensitivity, Requirement


def _get_field(obj: Any, field: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def calculate_sensitivity(
    jd: Dict[str, Any],
    candidates: List[Union[Candidate, Dict[str, Any]]],
    baseline_scores: List[CandidateScore],
    tested_semantic_weights: List[float] = None,
) -> RankingSensitivity:
    """Evaluate ranking stability across varying semantic weights.
    
    Tests semantic weights (default [0.30, 0.40, 0.50]) while adjusting
    the keyword weight (K_w = 0.80 - S_w) and keeping ontology at 0.20.
    """
    if tested_semantic_weights is None:
        tested_semantic_weights = [0.30, 0.40, 0.50]

    if not baseline_scores or len(candidates) <= 1:
        return RankingSensitivity(
            semantic_weights_tested=tested_semantic_weights,
            stable_top_three=True,
            rank_changes=[],
        )

    # Baseline top 3 candidate IDs
    sorted_baseline = sorted(baseline_scores, key=lambda cs: cs.rank)
    baseline_top_three = [cs.candidate_id for cs in sorted_baseline[:3]]
    baseline_rank_map = {cs.candidate_id: cs.rank for cs in baseline_scores}

    # Map candidate_id -> list of requirement matches
    matches_by_candidate: Dict[str, List[Any]] = {}
    for cs in baseline_scores:
        matches_by_candidate[cs.candidate_id] = cs.requirement_matches

    requirements = jd.get("requirements", [])
    rank_changes: List[Dict[str, Any]] = []
    top_three_stable = True

    for s_weight in tested_semantic_weights:
        k_weight = round(0.80 - s_weight, 4)
        o_weight = 0.20

        sim_scores: List[Dict[str, Any]] = []

        for cs in baseline_scores:
            cand_id = cs.candidate_id
            cand_matches = matches_by_candidate.get(cand_id, [])

            # Recalculate requirement scores under this weight configuration
            total_req_weight = 0.0
            weighted_coverage_num = 0.0
            required_weight = 0.0
            required_coverage_num = 0.0
            missing_required_weight = 0.0

            for req, match in zip(requirements, cand_matches):
                # Determine requirement importance
                r_type = str(_get_field(req, "requirement_type", "required")).lower()
                r_cat = str(_get_field(req, "category", "technology")).lower()
                imp = float(_get_field(req, "importance", 1.0))
                if imp <= 0:
                    imp = WEIGHT_REQUIRED_TECH if (r_type == "required" and r_cat == "technology") else WEIGHT_REQUIRED_STANDARD

                total_req_weight += imp

                # Extract match components
                ev_str = float(_get_field(match, "evidence_strength", 0.0))
                kw = float(_get_field(match, "keyword_score", 0.0))
                sem = float(_get_field(match, "semantic_score", 0.0))
                ont = float(_get_field(match, "ontology_support", 0.0))
                guard = float(_get_field(match, "context_guard", 1.0))

                recalc_m = ev_str * (k_weight * kw + s_weight * sem + o_weight * ont) * guard
                weighted_coverage_num += imp * recalc_m

                if r_type == "required":
                    required_weight += imp
                    required_coverage_num += imp * recalc_m
                    if recalc_m < 0.30:
                        missing_required_weight += imp

            cov = weighted_coverage_num / max(total_req_weight, 1e-6)
            req_cov = required_coverage_num / max(required_weight, 1e-6)
            p_missing = MISSING_REQUIRED_PENALTY_COEFF * (missing_required_weight / max(total_req_weight, 1e-6))

            # Experience relevance & confidence from baseline
            exp_rel = cs.experience_relevance
            conf = cs.confidence / 100.0

            final_s = 100.0 * max(
                0.0,
                min(
                    1.0,
                    FINAL_COVERAGE_WEIGHT * cov
                    + FINAL_EXPERIENCE_WEIGHT * exp_rel
                    + 0.07 * conf
                    - p_missing,
                ),
            )

            sim_scores.append({
                "candidate_id": cand_id,
                "score": final_s,
                "required_coverage": req_cov,
                "evidence_strength": cs.evidence_strength,
            })

        # Sort under new weights
        sim_scores.sort(
            key=lambda x: (-x["score"], -x["required_coverage"], -x["evidence_strength"])
        )
        current_top_three = [x["candidate_id"] for x in sim_scores[:3]]

        # Check top 3 set consistency
        if set(current_top_three) != set(baseline_top_three):
            top_three_stable = False

        # Record rank changes
        for new_rank, item in enumerate(sim_scores, start=1):
            cid = item["candidate_id"]
            old_rank = baseline_rank_map.get(cid, new_rank)
            if old_rank != new_rank:
                rank_changes.append({
                    "semantic_weight": s_weight,
                    "candidate_id": cid,
                    "baseline_rank": old_rank,
                    "simulated_rank": new_rank,
                    "delta": old_rank - new_rank,
                })

    return RankingSensitivity(
        semantic_weights_tested=tested_semantic_weights,
        stable_top_three=top_three_stable,
        rank_changes=rank_changes,
    )
