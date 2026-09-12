"""
Explanation generator for Person 4.
Produces deterministic explanations, missing requirement lists, improvement opportunities,
messy resume normalization summaries, and final result assembly.
"""

from typing import List, Dict, Any, Optional
from nexora.explanations.templates import (
    TOP_THREE_TEMPLATE, format_cautious_missing, format_cautious_partial
)
from nexora.config import EVIDENCE_SOURCE_PRIORITY


def generate_top_three_explanations(
    ranking: Dict[str, Any],
    jd: Dict[str, Any],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generates deterministic top-three candidate explanations.
    """
    ranked_candidates = ranking.get("ranked_candidates", [])
    cand_dict_map = {c.get("candidate_id"): c for c in candidates}
    top_three = ranked_candidates[:3]

    explanations = []

    for cand_score in top_three:
        cand_id = cand_score.get("candidate_id", "")
        rank = cand_score.get("rank", 1)
        score = cand_score.get("score", 0.0)
        confidence_label = cand_score.get("confidence_label", "Medium")
        cand_name = cand_score.get("name", f"Candidate {cand_id}")

        cand_obj = cand_dict_map.get(cand_id, {})
        evidence_units = cand_obj.get("evidence_units", [])
        ev_map = {ev.get("evidence_id") if isinstance(ev, dict) else ev.evidence_id: (ev if isinstance(ev, dict) else ev.model_dump()) for ev in evidence_units}

        req_matches = cand_score.get("requirement_matches", [])

        # Sort matches by requirement contribution
        req_map = {r.get("requirement_id"): r for r in jd.get("requirements", [])}

        matched_reqs = []
        preferred_matches = []
        missing_reqs = []
        sections_found = set()
        evidence_list = []
        primary_snippet = "Relevant coursework and projects listed."

        for match in req_matches:
            req_id = match.get("requirement_id", "")
            req_info = req_map.get(req_id, {})
            req_name = req_info.get("canonical", req_info.get("text", req_id))
            req_type = req_info.get("requirement_type", "required")
            f_score = match.get("final_requirement_score", 0.0)

            if f_score >= 0.30:
                if req_type == "required":
                    matched_reqs.append(req_name)
                else:
                    preferred_matches.append(req_name)

                # Collect evidence snippets (priority: experience > projects > internship > certifications > education > summary > skills)
                ev_ids = match.get("evidence_ids", [])
                matched_evs = [ev_map[eid] for eid in ev_ids if eid in ev_map]

                # Sort by section priority
                matched_evs.sort(
                    key=lambda x: EVIDENCE_SOURCE_PRIORITY.get(x.get("section", "other"), 0.20),
                    reverse=True
                )

                for ev in matched_evs[:2]:  # Max 2 snippets per requirement
                    sec = ev.get("section", "projects")
                    sections_found.add(sec)
                    text = ev.get("text", "")
                    if text and primary_snippet == "Relevant coursework and projects listed.":
                        primary_snippet = text

                    evidence_list.append({
                        "requirement": req_name,
                        "text": text,
                        "section": sec,
                        "page": ev.get("page", 1),
                        "evidence_id": ev.get("evidence_id", "")
                    })
            else:
                if req_type == "required":
                    missing_reqs.append(format_cautious_missing(req_name))

        matched_str = ", ".join(matched_reqs[:4]) if matched_reqs else "general technical skills"
        missing_str = "; ".join(missing_reqs) if missing_reqs else "None"
        preferred_str = ", ".join(preferred_matches) if preferred_matches else "None"
        sections_str = ", ".join(sorted(list(sections_found))) if sections_found else "projects"

        formatted_summary = TOP_THREE_TEMPLATE.format(
            candidate=cand_name,
            rank=rank,
            score=score,
            confidence_label=confidence_label,
            matched_requirements=matched_str,
            sections=sections_str,
            evidence_snippet=primary_snippet,
            missing_requirements=missing_str,
            preferred_matches=preferred_str
        )

        explanations.append({
            "candidate_id": cand_id,
            "rank": rank,
            "score": score,
            "confidence_label": confidence_label,
            "summary": formatted_summary,
            "matched": matched_reqs,
            "missing": cand_score.get("missing_required", []),
            "evidence": evidence_list,
            "preferred_matches": preferred_matches
        })

    return explanations


def get_missing_requirements(candidate_score: Dict[str, Any], jd: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns missing required skills, weak skills, and preferred requirements without evidence.
    """
    cand_id = candidate_score.get("candidate_id", "")
    req_matches = candidate_score.get("requirement_matches", [])
    req_map = {r.get("requirement_id"): r for r in jd.get("requirements", [])}

    missing_required = []
    weak_required = []
    missing_preferred = []

    for match in req_matches:
        req_id = match.get("requirement_id", "")
        req_info = req_map.get(req_id, {})
        canonical = req_info.get("canonical", req_info.get("text", req_id))
        req_type = req_info.get("requirement_type", "required")
        f_score = match.get("final_requirement_score", 0.0)

        if req_type == "required":
            if f_score < 0.15:
                missing_required.append(format_cautious_missing(canonical))
            elif f_score < 0.35:
                weak_required.append(format_cautious_partial(canonical, "related tools"))
        else:
            if f_score < 0.30:
                missing_preferred.append(format_cautious_missing(canonical))

    return {
        "candidate_id": cand_id,
        "missing_required": missing_required,
        "weak_required": weak_required,
        "missing_preferred": missing_preferred,
        "evidence_status": "audited"
    }


def get_improvement_opportunities(candidate_score: Dict[str, Any], jd: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ranks improvement opportunities using importance * (1 - current_final_requirement_score).
    Prioritizes: missing required > weak required > missing preferred > weak preferred.
    """
    cand_id = candidate_score.get("candidate_id", "")
    req_matches = candidate_score.get("requirement_matches", [])
    req_map = {r.get("requirement_id"): r for r in jd.get("requirements", [])}

    opportunities = []

    for match in req_matches:
        req_id = match.get("requirement_id", "")
        req_info = req_map.get(req_id, {})
        canonical = req_info.get("canonical", req_info.get("text", req_id))
        req_type = req_info.get("requirement_type", "required")
        importance = req_info.get("importance", 1.0)
        f_score = match.get("final_requirement_score", 0.0)

        gap = 1.0 - f_score
        priority_score = round(importance * gap, 2)

        if f_score < 0.70:
            if req_type == "required":
                msg = f"Add clear project or experience evidence for {canonical}."
            else:
                msg = f"Demonstrating {canonical} experience will improve overall candidate match."

            opportunities.append({
                "requirement": canonical,
                "type": req_type,
                "current_score": round(f_score, 2),
                "priority": priority_score,
                "message": msg
            })

    # Sort by priority score descending
    opportunities.sort(key=lambda x: x["priority"], reverse=True)

    return {
        "candidate_id": cand_id,
        "improvement_opportunities": opportunities
    }


def build_normalization_summary(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregates Person 2's messy resume normalization logs, extraction quality, and quality flags.
    """
    summary = []

    for cand in candidates:
        cand_id = cand.get("candidate_id", "")
        name = cand.get("name", cand_id)
        ext_quality = cand.get("extraction_quality", 1.0)
        norm_log = cand.get("normalization_log", [])
        quality_flags = cand.get("quality_flags", ["text_extracted"])

        summary.append({
            "candidate_id": cand_id,
            "name": name,
            "extraction_quality": round(ext_quality * 100.0, 1),
            "normalizations": norm_log,
            "quality_flags": quality_flags
        })

    return summary


def build_final_result(
    jd: Dict[str, Any],
    ranking: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    explanations: List[Dict[str, Any]],
    comparison: Optional[Dict[str, Any]] = None,
    bias_flags: Optional[List[Dict[str, Any]]] = None,
    normalization_summary: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Assembles the final structured output object for the frontend.
    """
    return {
        "jd": jd,
        "ranking": ranking,
        "explanations": explanations,
        "comparison": comparison or {},
        "bias_flags": bias_flags or jd.get("bias_flags", []),
        "normalization_summary": normalization_summary or build_normalization_summary(candidates)
    }
