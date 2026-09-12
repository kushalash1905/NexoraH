"""Parsers and document extraction module for NEXORA."""

from nexora.parsers.pdf_parser import (
    extract_pdf_blocks,
    extract_pdf_text,
    assess_extraction_quality,
    clean_text
)
from nexora.parsers.evidence_builder import (
    build_candidate_from_pdf,
    build_candidate_from_text,
    extract_and_normalize_skills,
    extract_contact_info,
    load_skill_aliases
)

__all__ = [
    "extract_pdf_blocks",
    "extract_pdf_text",
    "assess_extraction_quality",
    "clean_text",
    "build_candidate_from_pdf",
    "build_candidate_from_text",
    "extract_and_normalize_skills",
    "extract_contact_info",
    "load_skill_aliases",
]
