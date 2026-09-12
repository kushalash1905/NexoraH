"""Evidence retrieval and quality scoring for NEXORA.

Combines independent BM25 retrieval and semantic vector retrieval,
deduplicates evidence units, and evaluates evidence strength based on
section provenance, action verbs, outcome metrics, and duration signals.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from sentence_transformers import SentenceTransformer

from nexora.config import (
    DEFAULT_BASE_STRENGTH,
    EVIDENCE_DURATION_BONUS,
    EVIDENCE_OUTCOME_BONUS,
    EVIDENCE_REPEAT_BONUS,
    EVIDENCE_VERB_BONUS,
    SECTION_BASE_STRENGTHS,
)
from nexora.matching.keyword_engine import retrieve_bm25
from nexora.matching.semantic_engine import retrieve_semantic_evidence
from nexora.schemas import EvidenceUnit, Requirement


ACTION_VERB_PATTERN = re.compile(
    r"\b(built|developed|implemented|deployed|integrated|designed|created|programmed|"
    r"engineered|maintained|optimized|automated|tested|architected|configured|spearheaded|"
    r"authored|refactored|launched|delivered|constructed|orchestrated)\b",
    re.IGNORECASE,
)

OUTCOME_METRIC_PATTERN = re.compile(
    r"\b(\d+%\s*|\d+\+?\s*users?|\d+\s*ms|latency|accuracy|production|throughput|performance|"
    r"reduced|increased|scaled|improved|accelerated|million|thousand|daily|monthly)\b",
    re.IGNORECASE,
)

DURATION_PATTERN = re.compile(
    r"\b(\d+\s*months?|\d+\s*years?|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|202\d|201\d)\b",
    re.IGNORECASE,
)


def _get_ev_field(ev: Union[EvidenceUnit, Dict[str, Any]], field: str, default: Any = None) -> Any:
    """Helper to extract an attribute from an EvidenceUnit or dict."""
    if isinstance(ev, dict):
        return ev.get(field, default)
    return getattr(ev, field, default)


def calculate_evidence_strength(
    evidence: Union[EvidenceUnit, Dict[str, Any]],
    requirement: Optional[Union[Requirement, Dict[str, Any]]] = None,
) -> float:
    """Calculate evidence strength E in [0.0, 1.0].
    
    Formula:
    E = clip(Base_section + 0.10*verb + 0.08*outcome + 0.05*duration + 0.05*repeat, 0.0, 1.0)
    """
    section = str(_get_ev_field(evidence, "section", "")).strip().lower()
    base_strength = SECTION_BASE_STRENGTHS.get(section, DEFAULT_BASE_STRENGTH)

    # Check action verb
    has_verb = bool(_get_ev_field(evidence, "has_action_verb", False))
    text = str(_get_ev_field(evidence, "normalized_text", None) or _get_ev_field(evidence, "text", "")).lower()
    if not has_verb and bool(ACTION_VERB_PATTERN.search(text)):
        has_verb = True

    # Check outcome metric
    has_outcome = bool(_get_ev_field(evidence, "has_outcome", False))
    if not has_outcome and bool(OUTCOME_METRIC_PATTERN.search(text)):
        has_outcome = True

    # Check duration
    has_duration = bool(_get_ev_field(evidence, "has_duration", False))
    if not has_duration and bool(DURATION_PATTERN.search(text)):
        has_duration = True

    # Check repetition
    repetition = int(_get_ev_field(evidence, "repetition_count", 1))
    has_repeat = repetition > 1

    total = (
        base_strength
        + (EVIDENCE_VERB_BONUS if has_verb else 0.0)
        + (EVIDENCE_OUTCOME_BONUS if has_outcome else 0.0)
        + (EVIDENCE_DURATION_BONUS if has_duration else 0.0)
        + (EVIDENCE_REPEAT_BONUS if has_repeat else 0.0)
    )

    return round(float(min(1.0, max(0.0, total))), 4)


def retrieve_and_combine_evidence(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    model: Optional[SentenceTransformer] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> Tuple[List[Union[EvidenceUnit, Dict[str, Any]]], List[str]]:
    """Retrieve evidence independently via BM25 and semantics, then combine sets.
    
    Returns:
        (combined_evidence_units, evidence_ids_used)
    """
    if not evidence_units:
        return [], []

    # 1. Independent BM25 retrieval
    bm25_results = retrieve_bm25(
        requirement=requirement,
        evidence_units=evidence_units,
        top_k=top_k,
        aliases=aliases,
        ontology=ontology,
    )

    # 2. Independent Semantic retrieval
    sem_results: List[Tuple[Union[EvidenceUnit, Dict[str, Any]], float]] = []
    if model is not None:
        sem_results = retrieve_semantic_evidence(
            requirement=requirement,
            evidence_units=evidence_units,
            model=model,
            top_k=top_k,
        )

    # 3. Combine and deduplicate
    combined_map: Dict[str, Union[EvidenceUnit, Dict[str, Any]]] = {}
    score_map: Dict[str, float] = {}

    max_bm25 = max([score for _, score in bm25_results], default=1.0)
    if max_bm25 <= 0:
        max_bm25 = 1.0

    for ev, bm_score in bm25_results:
        ev_id = str(_get_ev_field(ev, "evidence_id", id(ev)))
        combined_map[ev_id] = ev
        norm_bm = max(0.0, bm_score) / max_bm25
        ev_str = calculate_evidence_strength(ev, requirement)
        score_map[ev_id] = score_map.get(ev_id, 0.0) + 0.4 * norm_bm + 0.2 * ev_str

    for ev, sem_score in sem_results:
        ev_id = str(_get_ev_field(ev, "evidence_id", id(ev)))
        combined_map[ev_id] = ev
        norm_sem = max(0.0, sem_score)
        ev_str = calculate_evidence_strength(ev, requirement)
        score_map[ev_id] = score_map.get(ev_id, 0.0) + 0.4 * norm_sem + 0.2 * ev_str

    # Sort combined evidence by priority score
    sorted_ev_ids = sorted(score_map.keys(), key=lambda eid: score_map[eid], reverse=True)
    combined_units = [combined_map[eid] for eid in sorted_ev_ids[:top_k]]
    evidence_ids_used = [str(_get_ev_field(ev, "evidence_id", "")) for ev in combined_units]

    return combined_units, evidence_ids_used
