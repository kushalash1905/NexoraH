"""Matching engine subpackage."""

from nexora.matching.ontology import (
    load_ontology,
    load_aliases,
    get_aliases,
    get_related_skills,
    calculate_ontology_support,
)
from nexora.matching.keyword_engine import (
    normalize_match_text,
    calculate_exact_match,
    calculate_alias_match,
    calculate_fuzzy_match,
    retrieve_bm25,
    calculate_bm25_score,
    calculate_keyword_score,
)
from nexora.matching.semantic_engine import (
    load_embedding_model,
    encode_texts,
    calculate_semantic_score,
    retrieve_semantic_evidence,
)
from nexora.matching.evidence_retriever import (
    retrieve_and_combine_evidence,
    calculate_evidence_strength,
)
from nexora.matching.matcher import (
    match_requirement,
    calculate_context_guard,
    classify_match,
)

__all__ = [
    "load_ontology",
    "load_aliases",
    "get_aliases",
    "get_related_skills",
    "calculate_ontology_support",
    "normalize_match_text",
    "calculate_exact_match",
    "calculate_alias_match",
    "calculate_fuzzy_match",
    "retrieve_bm25",
    "calculate_bm25_score",
    "calculate_keyword_score",
    "load_embedding_model",
    "encode_texts",
    "calculate_semantic_score",
    "retrieve_semantic_evidence",
    "retrieve_and_combine_evidence",
    "calculate_evidence_strength",
    "match_requirement",
    "calculate_context_guard",
    "classify_match",
]
