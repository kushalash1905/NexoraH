"""Confidence scoring and labeling for NEXORA candidate evaluations.

Confidence measures how strongly, consistently, and reliably the extracted
resume evidence supports the computed score. It is NOT a prediction of hiring
success or employee job performance.
"""

from typing import Any, Dict, List, Union

from nexora.config import (
    CONFIDENCE_EVIDENCE_WEIGHT,
    CONFIDENCE_EXTRACTION_QUALITY_WEIGHT,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    CONFIDENCE_REQUIRED_COVERAGE_WEIGHT,
    CONFIDENCE_SIGNAL_AGREEMENT_WEIGHT,
)
from nexora.schemas import Candidate, RequirementMatch


def confidence_label(confidence_value: float) -> str:
    """Map numeric confidence (0.0 - 1.0) to categorical label."""
    if confidence_value >= CONFIDENCE_HIGH_THRESHOLD:
        return "High"
    elif confidence_value >= CONFIDENCE_MEDIUM_THRESHOLD:
        return "Medium"
    return "Low"


def calculate_candidate_confidence(
    candidate: Union[Candidate, Dict[str, Any]],
    matches: List[Union[RequirementMatch, Dict[str, Any]]],
    required_coverage: float,
    extraction_quality: float = 1.0,
) -> float:
    """Calculate candidate confidence score C(c) in [0.0, 1.0].
    
    Formula:
    C(c) = 0.45 * avg_evidence_strength
         + 0.30 * required_coverage
         + 0.15 * extraction_quality
         + 0.10 * signal_agreement
         
    where signal_agreement = 1.0 - abs(keyword_alignment - semantic_alignment).
    """
    if not matches:
        return 0.0

    ev_strengths = []
    kw_scores = []
    sem_scores = []

    for m in matches:
        if isinstance(m, dict):
            ev_s = float(m.get("evidence_strength", 0.0))
            kw = float(m.get("keyword_score", 0.0))
            sem = float(m.get("semantic_score", 0.0))
            score = float(m.get("final_requirement_score", 0.0))
        else:
            ev_s = float(getattr(m, "evidence_strength", 0.0))
            kw = float(getattr(m, "keyword_score", 0.0))
            sem = float(getattr(m, "semantic_score", 0.0))
            score = float(getattr(m, "final_requirement_score", 0.0))

        # Only factor evidence strength from requirements with actual evidence
        if score >= 0.20 or ev_s > 0.25:
            ev_strengths.append(ev_s)
        kw_scores.append(kw)
        sem_scores.append(sem)

    avg_ev_strength = sum(ev_strengths) / len(ev_strengths) if ev_strengths else 0.25
    avg_kw = sum(kw_scores) / len(kw_scores) if kw_scores else 0.0
    avg_sem = sum(sem_scores) / len(sem_scores) if sem_scores else 0.0

    signal_agreement = max(0.0, 1.0 - abs(avg_kw - avg_sem))

    raw_conf = (
        CONFIDENCE_EVIDENCE_WEIGHT * avg_ev_strength
        + CONFIDENCE_REQUIRED_COVERAGE_WEIGHT * required_coverage
        + CONFIDENCE_EXTRACTION_QUALITY_WEIGHT * extraction_quality
        + CONFIDENCE_SIGNAL_AGREEMENT_WEIGHT * signal_agreement
    )

    return round(float(min(1.0, max(0.0, raw_conf))), 4)
