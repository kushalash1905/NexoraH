"""
Candidate comparison engine and recruiter question handler for Person 4.
Calculates requirement-level contribution deltas between Candidate A and Candidate B.
Handles recruiter question parsing via regex without LLMs.
"""

import re
from typing import List, Dict, Any, Optional
from nexora.explanations.generator import get_missing_requirements, get_improvement_opportunities

WHY_PATTERN = re.compile(r'why.*candidate\s+([a-zA-Z0-9_\-]+).*above.*candidate\s+([a-zA-Z0-9_\-]+)', re.IGNORECASE)
COMPARE_PATTERN = re.compile(r'compare.*candidate\s+([a-zA-Z0-9_\-]+).*(?:and|to|with).*candidate\s+([a-zA-Z0-9_\-]+)', re.IGNORECASE)
MISSING_PATTERN = re.compile(r'what.*candidate\s+([a-zA-Z0-9_\-]+).*missing', re.IGNORECASE)
IMPROVE_PATTERN = re.compile(r'what.*improve.*candidate\s+([a-zA-Z0-9_\-]+)', re.IGNORECASE)


def compare_candidates(
    candidate_a_id: str,
    candidate_b_id: str,
    ranking_result: Dict[str, Any],
    jd: Dict[str, Any],
    candidates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Deterministically compares Candidate A and Candidate B.
    Frontend must NOT calculate comparison logic.
    """
    ranked = ranking_result.get("ranked_candidates", [])
    cand_map = {c.get("candidate_id"): c for c in ranked}

    cand_a = cand_map.get(candidate_a_id)
    cand_b = cand_map.get(candidate_b_id)

    if not cand_a or not cand_b:
        return {
            "error": f"One or both candidates ({candidate_a_id}, {candidate_b_id}) not found in rankings."
        }

    score_diff = round(cand_a.get("score", 0.0) - cand_b.get("score", 0.0), 1)
    rank_diff = cand_b.get("rank", 0) - cand_a.get("rank", 0)

    dim_diffs = {
        "required_coverage": round(cand_a.get("required_coverage", 0.0) - cand_b.get("required_coverage", 0.0), 2),
        "preferred_coverage": round(cand_a.get("preferred_coverage", 0.0) - cand_b.get("preferred_coverage", 0.0), 2),
        "keyword_alignment": round(cand_a.get("keyword_alignment", 0.0) - cand_b.get("keyword_alignment", 0.0), 2),
        "semantic_alignment": round(cand_a.get("semantic_alignment", 0.0) - cand_b.get("semantic_alignment", 0.0), 2),
        "evidence_strength": round(cand_a.get("evidence_strength", 0.0) - cand_b.get("evidence_strength", 0.0), 2)
    }

    # Requirement-level contributors
    req_map = {r.get("requirement_id"): r for r in jd.get("requirements", [])}

    matches_a = {m.get("requirement_id"): m.get("final_requirement_score", 0.0) for m in cand_a.get("requirement_matches", [])}
    matches_b = {m.get("requirement_id"): m.get("final_requirement_score", 0.0) for m in cand_b.get("requirement_matches", [])}

    top_contributors = []

    for req_id, req_info in req_map.items():
        raw_importance = req_info.get("importance", 1.0)
        try:
            importance = float(raw_importance)
        except (ValueError, TypeError):
            imp_str = str(raw_importance).lower()
            if "preferred" in imp_str:
                importance = 0.45
            elif "contextual" in imp_str:
                importance = 0.30
            else:
                importance = 1.0

        canonical = req_info.get("canonical", req_info.get("text", req_id))

        score_a = matches_a.get(req_id, 0.0)
        score_b = matches_b.get(req_id, 0.0)

        delta = importance * (score_a - score_b)

        if abs(delta) > 0.01:
            top_contributors.append({
                "requirement": canonical,
                "candidate_a_score": round(score_a, 2),
                "candidate_b_score": round(score_b, 2),
                "weighted_difference": round(delta, 3),
                "favors": "candidate_a" if delta > 0 else "candidate_b"
            })

    # Sort contributors by absolute difference descending
    top_contributors.sort(key=lambda x: abs(x["weighted_difference"]), reverse=True)

    name_a = cand_a.get("name", candidate_a_id)
    name_b = cand_b.get("name", candidate_b_id)

    # Deterministic summary
    favors_a = [c for c in top_contributors if c["favors"] == "candidate_a"]
    top_skills_a = ", ".join([c["requirement"] for c in favors_a[:2]]) if favors_a else "core requirements"

    summary = (
        f"{name_a} ranks above {name_b} mainly because of stronger required-skill and project evidence for {top_skills_a}."
    )

    return {
        "candidate_a": candidate_a_id,
        "candidate_b": candidate_b_id,
        "candidate_a_name": name_a,
        "candidate_b_name": name_b,
        "score_difference": score_diff,
        "rank_difference": rank_diff,
        "dimension_differences": dim_diffs,
        "top_requirement_contributors": top_contributors[:5],
        "summary": summary
    }


def recruiter_answer(
    question: str,
    ranking_result: Dict[str, Any],
    jd: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    candidate_a_id: Optional[str] = None,
    candidate_b_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parses recruiter question and returns deterministic answer structured data.
    """
    q_str = question.strip()
    ranked = ranking_result.get("ranked_candidates", [])

    if not ranked:
        return {"answer": "No candidates available to inspect."}

    # Match WHY
    m_why = WHY_PATTERN.search(q_str)
    if m_why or (candidate_a_id and candidate_b_id and "why" in q_str.lower()):
        c_a = candidate_a_id or m_why.group(1).strip()
        c_b = candidate_b_id or m_why.group(2).strip()
        comp = compare_candidates(c_a, c_b, ranking_result, jd, candidates)
        return {
            "intent": "why_ranked_above",
            "comparison": comp,
            "answer": comp.get("summary", "Comparison calculated successfully.")
        }

    # Match COMPARE
    m_comp = COMPARE_PATTERN.search(q_str)
    if m_comp or (candidate_a_id and candidate_b_id and "compare" in q_str.lower()):
        c_a = candidate_a_id or (m_comp.group(1).strip() if m_comp else candidate_a_id)
        c_b = candidate_b_id or (m_comp.group(2).strip() if m_comp else candidate_b_id)
        comp = compare_candidates(c_a, c_b, ranking_result, jd, candidates)
        return {
            "intent": "compare_candidates",
            "comparison": comp,
            "answer": comp.get("summary", "Comparison calculated successfully.")
        }

    # Match MISSING
    m_miss = MISSING_PATTERN.search(q_str)
    if m_miss or (candidate_b_id and "missing" in q_str.lower()):
        c_id = candidate_b_id or (m_miss.group(1).strip() if m_miss else candidate_b_id)
        cand_score = next((c for c in ranked if c.get("candidate_id") == c_id or c.get("name").lower() == c_id.lower()), None)
        if cand_score:
            missing_info = get_missing_requirements(cand_score, jd)
            return {
                "intent": "what_is_missing",
                "missing_info": missing_info,
                "answer": f"{cand_score.get('name')} missing skills: " + (", ".join(missing_info.get("missing_required", [])) or "None")
            }

    # Match IMPROVE
    m_imp = IMPROVE_PATTERN.search(q_str)
    if m_imp or (candidate_b_id and "improve" in q_str.lower()):
        c_id = candidate_b_id or (m_imp.group(1).strip() if m_imp else candidate_b_id)
        cand_score = next((c for c in ranked if c.get("candidate_id") == c_id or c.get("name").lower() == c_id.lower()), None)
        if cand_score:
            opps = get_improvement_opportunities(cand_score, jd)
            return {
                "intent": "what_would_improve",
                "improvement_info": opps,
                "answer": f"Top improvement opportunities calculated for {cand_score.get('name')}."
            }

    return {
        "intent": "unknown",
        "answer": "Please select a supported question or use one of the preset actions in the UI."
    }
