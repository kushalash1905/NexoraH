"""
Application Orchestrator for Person 4.
Combines parsers, ranking engine, explanation engine, bias detector, and normalization diagnostics.
No HTTP communication. Works fully offline.
"""

import os
import json
from typing import List, Dict, Any

from nexora.parsers.evidence_builder import build_candidate_from_pdf, build_candidate_from_text
from nexora.jd_analysis.requirement_classifier import (
    build_job_description_from_pdf,
    build_job_description_from_text
)
from nexora.ranking import rank_candidates
from nexora.explanations.generator import (
    generate_top_three_explanations,
    build_normalization_summary,
    build_final_result
)
from nexora.jd_analysis.bias_detector import detect_bias_flags
from nexora.config import DATA_DIR


def load_json_file(filepath: str, default: dict) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def parse_jd_file(jd_path: str) -> Any:
    """Parse JD file using Person 2's actual parser/classifier implementation."""
    if jd_path.lower().endswith(".pdf"):
        return build_job_description_from_pdf(jd_path, jd_id="jd_001")
    else:
        with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        return build_job_description_from_text(raw_text, jd_id="jd_001")


def parse_resume_file(r_path: str, cand_id: str) -> Any:
    """Parse resume file using Person 2's actual evidence builder implementation."""
    if r_path.lower().endswith(".pdf"):
        return build_candidate_from_pdf(r_path, candidate_id=cand_id)
    else:
        with open(r_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        return build_candidate_from_text(raw_text, candidate_id=cand_id)


def run_analysis(
    jd_path: str,
    resume_paths: List[str]
) -> Dict[str, Any]:
    """
    Main orchestration function for Nexora.
    Takes JD path and list of resume paths. Returns final application result dictionary.
    """
    aliases_path = os.path.join(DATA_DIR, "aliases.json")
    ontology_path = os.path.join(DATA_DIR, "ontology.json")

    aliases = load_json_file(aliases_path, {})
    ontology = load_json_file(ontology_path, {})

    # 1. Parse JD using Person 2 implementation
    jd = parse_jd_file(jd_path)

    # 2. Parse every resume using Person 2 implementation
    candidates = []
    for idx, r_path in enumerate(resume_paths, start=1):
        cand_id = f"candidate_{idx:03d}"
        candidate = parse_resume_file(r_path, cand_id=cand_id)
        candidates.append(candidate)

    # 3. Rank candidates (Person 1)
    ranking_obj = rank_candidates(
        jd=jd,
        candidates=candidates,
        aliases=aliases,
        ontology=ontology
    )

    ranking_dict = ranking_obj.model_dump() if hasattr(ranking_obj, "model_dump") else ranking_obj
    jd_dict = jd.model_dump() if hasattr(jd, "model_dump") else jd
    cand_dicts = [c.model_dump() if hasattr(c, "model_dump") else c for c in candidates]

    # 4. Deterministic top-three explanations (Person 4)
    explanations = generate_top_three_explanations(
        ranking=ranking_dict,
        jd=jd_dict,
        candidates=cand_dicts
    )

    # Attach explanations to ranking object
    ranking_dict["top_three_explanations"] = explanations

    # 5. JD narrow-language / bias flags (Person 4 & Person 1)
    bias_flags = detect_bias_flags(jd_dict)
    jd_dict["bias_flags"] = bias_flags

    # 6. Messy resume normalization summary (Person 4)
    norm_summary = build_normalization_summary(cand_dicts)

    # 7. Assemble final result (Person 4)
    final_result = build_final_result(
        jd=jd_dict,
        ranking=ranking_dict,
        candidates=cand_dicts,
        explanations=explanations,
        comparison={},
        bias_flags=bias_flags,
        normalization_summary=norm_summary
    )

    return final_result
