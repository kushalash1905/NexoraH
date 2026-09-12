"""Keyword matching engine for NEXORA.

Implements:
1. Token-safe exact canonical matching.
2. Alias matching via aliases.json and ontology.json.
3. Conservative RapidFuzz fuzzy matching (capped at 0.45).
4. BM25 candidate evidence index retrieval and normalized scoring.
5. Composite keyword score: K(r,c) = 0.50*exact + 0.25*alias + 0.15*fuzzy + 0.10*bm25.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union

from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz

from nexora.config import (
    FUZZY_RATIO_THRESHOLD,
    FUZZY_TECH_CAP,
    KEYWORD_ALIAS_WEIGHT,
    KEYWORD_BM25_WEIGHT,
    KEYWORD_EXACT_WEIGHT,
    KEYWORD_FUZZY_WEIGHT,
)
from nexora.matching.ontology import _contains_token, _get_req_field, get_aliases
from nexora.schemas import Candidate, EvidenceUnit, Requirement


def normalize_match_text(text: str) -> str:
    """Normalize text for token-safe matching.
    
    Converts to lowercase, normalizes unicode, normalizes whitespace,
    and strips non-standard punctuation while preserving dot in technical terms.
    """
    if not text:
        return ""
    # Normalize unicode (NFKD)
    normalized = unicodedata.normalize("NFKD", text)
    # Lowercase
    normalized = normalized.lower()
    # Replace newlines, tabs, multiple whitespace with a single space
    normalized = re.sub(r"[\r\n\t]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _extract_evidence_text(ev: Union[EvidenceUnit, Dict[str, Any]]) -> str:
    """Safely extract normalized text from an EvidenceUnit or dict."""
    if isinstance(ev, dict):
        return str(ev.get("normalized_text") or ev.get("text") or "").strip().lower()
    return str(getattr(ev, "normalized_text", None) or getattr(ev, "text", "")).strip().lower()


def calculate_exact_match(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    candidate: Optional[Union[Candidate, Dict[str, Any]]] = None,
) -> float:
    """Token-safe exact matching of canonical requirement term.
    
    Prevents substring collisions (e.g. 'Java' matching 'JavaScript').
    Returns 1.0 if found in evidence units or candidate normalized skills, else 0.0.
    """
    canonical = str(_get_req_field(requirement, "canonical", "")).strip().lower()
    if not canonical:
        canonical = str(_get_req_field(requirement, "text", "")).strip().lower()
    if not canonical:
        return 0.0

    # 1. Check candidate normalized skills list
    if candidate:
        cand_skills = []
        if isinstance(candidate, dict):
            cand_skills = [str(s).strip().lower() for s in candidate.get("normalized_skills", [])]
        else:
            cand_skills = [str(s).strip().lower() for s in getattr(candidate, "normalized_skills", [])]
        if canonical in cand_skills:
            return 1.0

    # 2. Check evidence units text using safe token boundaries
    for ev in evidence_units:
        ev_text = _extract_evidence_text(ev)
        if _contains_token(ev_text, canonical):
            return 1.0

    return 0.0


def calculate_alias_match(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
    candidate: Optional[Union[Candidate, Dict[str, Any]]] = None,
) -> float:
    """Check if any valid alias for the requirement appears in evidence.
    
    Returns 1.0 if an alias is found, else 0.0.
    """
    alias_list = get_aliases(requirement, aliases=aliases, ontology=ontology)
    if not alias_list:
        return 0.0

    # 1. Check candidate normalized skills list
    if candidate:
        cand_skills = []
        if isinstance(candidate, dict):
            cand_skills = [str(s).strip().lower() for s in candidate.get("normalized_skills", [])]
        else:
            cand_skills = [str(s).strip().lower() for s in getattr(candidate, "normalized_skills", [])]
        for alias in alias_list:
            if alias in cand_skills:
                return 1.0

    # 2. Check evidence units text
    for ev in evidence_units:
        ev_text = _extract_evidence_text(ev)
        for alias in alias_list:
            if _contains_token(ev_text, alias):
                return 1.0

    return 0.0


def calculate_fuzzy_match(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    candidate: Optional[Union[Candidate, Dict[str, Any]]] = None,
    exact_matched: bool = False,
    alias_matched: bool = False,
) -> float:
    """Conservative RapidFuzz token matching for typo detection.
    
    - Requires similarity >= FUZZY_RATIO_THRESHOLD (90.0).
    - Fuzzy-only technology credit is capped at FUZZY_TECH_CAP (0.45).
    - Cannot independently generate a full match.
    """
    if exact_matched or alias_matched:
        return 1.0

    canonical = str(_get_req_field(requirement, "canonical", "")).strip().lower()
    if not canonical or len(canonical) < 3:
        return 0.0

    best_ratio = 0.0

    # Helper to test fuzzy match on individual tokens/words
    def check_words(text_content: str) -> float:
        words = re.findall(r"[a-zA-Z0-9_\-\.]{3,}", text_content)
        max_r = 0.0
        for w in words:
            # Skip if lengths are too divergent
            if abs(len(w) - len(canonical)) > 2:
                continue
            r = fuzz.ratio(canonical, w)
            if r > max_r:
                max_r = r
        return max_r

    # Check candidate skills
    if candidate:
        cand_skills = []
        if isinstance(candidate, dict):
            cand_skills = [str(s).strip().lower() for s in candidate.get("normalized_skills", [])]
        else:
            cand_skills = [str(s).strip().lower() for s in getattr(candidate, "normalized_skills", [])]
        for skill in cand_skills:
            best_ratio = max(best_ratio, check_words(skill))

    # Check evidence units
    for ev in evidence_units:
        ev_text = _extract_evidence_text(ev)
        best_ratio = max(best_ratio, check_words(ev_text))

    if best_ratio >= FUZZY_RATIO_THRESHOLD:
        # Conservative cap: cannot exceed 0.45 on fuzzy alone
        return min(FUZZY_TECH_CAP, round(best_ratio / 100.0, 4))
    return 0.0


def _tokenize_for_bm25(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25 indexing."""
    tokens = re.findall(r"[a-zA-Z0-9_\-\.]+", text.lower())
    return [t for t in tokens if len(t) > 1]


def retrieve_bm25(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    top_k: int = 5,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
) -> List[Tuple[Union[EvidenceUnit, Dict[str, Any]], float]]:
    """Index candidate evidence units and retrieve top_k matching units.
    
    Returns a list of tuples: (evidence_unit, raw_bm25_score) sorted descending by score.
    """
    if not evidence_units:
        return []

    tokenized_corpus = [_tokenize_for_bm25(_extract_evidence_text(ev)) for ev in evidence_units]
    # Handle empty corpus tokens
    if not any(tokenized_corpus):
        return [(ev, 0.0) for ev in evidence_units[:top_k]]

    bm25 = BM25Okapi(tokenized_corpus)

    # Build query from requirement text, canonical, and aliases
    query_parts = [
        str(_get_req_field(requirement, "text", "")),
        str(_get_req_field(requirement, "canonical", "")),
    ]
    alias_list = get_aliases(requirement, aliases=aliases, ontology=ontology)
    query_parts.extend(alias_list)
    query_tokens = _tokenize_for_bm25(" ".join(query_parts))

    if not query_tokens:
        return [(ev, 0.0) for ev in evidence_units[:top_k]]

    scores = list(bm25.get_scores(query_tokens))
    query_set = set(query_tokens)

    # In rank_bm25, when corpus size is small (<= 2), Okapi IDF can yield 0 for terms appearing in 1 doc.
    # If all scores are non-positive, fallback to term overlap frequency.
    max_score = max(scores) if scores else 0.0
    if max_score <= 0.0:
        scores = [float(sum(1 for t in doc if t in query_set)) for doc in tokenized_corpus]
    else:
        scores = [float(s + 0.01 * sum(1 for t in doc if t in query_set)) for s, doc in zip(scores, tokenized_corpus)]

    scored_units = list(zip(evidence_units, scores))
    scored_units.sort(key=lambda x: x[1], reverse=True)

    return scored_units[:top_k]



def calculate_bm25_score(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    max_candidate_bm25: Optional[float] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
) -> float:
    """Calculate normalized BM25 score K_bm25 in [0.0, 1.0]."""
    if not evidence_units:
        return 0.0

    retrieved = retrieve_bm25(requirement, evidence_units, top_k=1, aliases=aliases, ontology=ontology)
    if not retrieved:
        return 0.0

    best_score = retrieved[0][1]
    if best_score <= 0.0:
        return 0.0

    if max_candidate_bm25 and max_candidate_bm25 > 0.0:
        normalized = best_score / (max_candidate_bm25 + 1e-6)
    else:
        # Heuristic normalization: BM25 score of ~5.0 is a solid match in short resume sentences
        normalized = min(1.0, best_score / 5.0)

    return round(float(min(1.0, max(0.0, normalized))), 4)


def calculate_keyword_score(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    candidate: Optional[Union[Candidate, Dict[str, Any]]] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
    max_candidate_bm25: Optional[float] = None,
) -> Tuple[float, Dict[str, float]]:
    """Compute composite keyword score:
    
    K(r,c) = 0.50 * K_exact + 0.25 * K_alias + 0.15 * K_fuzzy + 0.10 * K_bm25
    
    Returns:
        (composite_keyword_score, breakdown_dict)
    """
    k_exact = calculate_exact_match(requirement, evidence_units, candidate=candidate)
    k_alias = calculate_alias_match(requirement, evidence_units, aliases=aliases, ontology=ontology, candidate=candidate)
    k_fuzzy = calculate_fuzzy_match(
        requirement,
        evidence_units,
        candidate=candidate,
        exact_matched=(k_exact > 0),
        alias_matched=(k_alias > 0),
    )
    k_bm25 = calculate_bm25_score(
        requirement,
        evidence_units,
        max_candidate_bm25=max_candidate_bm25,
        aliases=aliases,
        ontology=ontology,
    )

    k_composite = (
        KEYWORD_EXACT_WEIGHT * k_exact
        + KEYWORD_ALIAS_WEIGHT * k_alias
        + KEYWORD_FUZZY_WEIGHT * k_fuzzy
        + KEYWORD_BM25_WEIGHT * k_bm25
    )
    k_composite = round(float(min(1.0, max(0.0, k_composite))), 4)

    breakdown = {
        "k_exact": k_exact,
        "k_alias": k_alias,
        "k_fuzzy": k_fuzzy,
        "k_bm25": k_bm25,
        "k_composite": k_composite,
    }
    return k_composite, breakdown
