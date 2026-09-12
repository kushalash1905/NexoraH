"""
Application Orchestrator for Person 4.
Combines parsers, ranking engine, explanation engine, bias detector, and normalization diagnostics.
No HTTP communication. Works fully offline.
"""

import os
import json
from typing import List, Dict, Any
from nexora.parsers import parse_jd, parse_resume
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

    # 1. Parse JD
    jd = parse_jd(path=jd_path, aliases=aliases, ontology=ontology)

    # 2. Parse every resume
    candidates = []
    for idx, r_path in enumerate(resume_paths, start=1):
        cand_id = f"candidate_{idx:03d}"
        candidate = parse_resume(path=r_path, candidate_id=cand_id, aliases=aliases)
        candidates.append(candidate)

    # 3. Rank candidates (Person 1)
    ranking = rank_candidates(
        jd=jd,
        candidates=candidates,
        aliases=aliases,
        ontology=ontology
    )

    # 4. Deterministic top-three explanations (Person 4)
    explanations = generate_top_three_explanations(
        ranking=ranking,
        jd=jd,
        candidates=candidates
    )

    # Attach explanations to ranking object
    ranking["top_three_explanations"] = explanations

    # 5. JD narrow-language / bias flags (Person 4)
    bias_flags = detect_bias_flags(jd)
    jd["bias_flags"] = bias_flags

    # 6. Messy resume normalization summary (Person 4)
    norm_summary = build_normalization_summary(candidates)

    # 7. Assemble final result (Person 4)
    final_result = build_final_result(
        jd=jd,
        ranking=ranking,
        candidates=candidates,
        explanations=explanations,
        comparison={},
        bias_flags=bias_flags,
        normalization_summary=norm_summary
    )

    return final_result
