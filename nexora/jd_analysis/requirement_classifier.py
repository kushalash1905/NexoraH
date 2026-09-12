"""Requirement classification and structured JobDescription builder.

Classifies extracted requirements by importance (required/preferred/contextual)
and category (technical skill, experience, education, domain, soft skill),
attaches canonical skills and ontology relations, and builds the JobDescription schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union, Optional

from nexora.schemas import (
    JobDescription,
    JDRequirement,
    RequirementImportance,
    RequirementCategory,
    SectionType,
    ExtractionQuality
)
from nexora.parsers.pdf_parser import extract_pdf_blocks, extract_pdf_text, assess_extraction_quality
from nexora.parsers.section_normalizer import split_into_sections
from nexora.parsers.evidence_builder import load_skill_aliases, extract_and_normalize_skills
from nexora.jd_analysis.requirement_extractor import extract_raw_requirements, extract_years_of_experience, is_education_requirement
from nexora.jd_analysis.bias_detector import detect_jd_bias

_ONTOLOGY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ontology.json"


def load_ontology() -> dict:
    """Load tech ontology from data/ontology.json."""
    if not _ONTOLOGY_PATH.exists():
        return {}
    try:
        with open(_ONTOLOGY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# Keywords indicating soft skills
SOFT_SKILL_KEYWORDS = {
    "communication", "verbal communication", "written communication",
    "teamwork", "collaborate", "collaboration", "leadership", "mentor",
    "problem solving", "analytical thinking", "critical thinking",
    "self-starter", "fast-paced", "adaptability", "interpersonal",
    "organizational skills", "time management", "detail-oriented"
}

# Cues for contextual requirements
CONTEXTUAL_CUES = {
    "familiarity with", "understanding of", "exposure to",
    "interest in", "willingness to learn", "knowledge of",
    "appreciation for", "awareness of"
}

# Cues for preferred requirements
PREFERRED_CUES = {
    "preferred", "nice to have", "plus", "bonus", "desirable",
    "helpful", "advantageous", "ideally", "good to have"
}

# Cues for required requirements
REQUIRED_CUES = {
    "required", "must have", "must possess", "essential",
    "mandatory", "proven experience", "demonstrated track record",
    "minimum of"
}


def classify_importance(clause_text: str, section_type: SectionType) -> RequirementImportance:
    """Determine whether a requirement is REQUIRED, PREFERRED, or CONTEXTUAL."""
    lower = clause_text.lower()

    # Section-level override
    if section_type == SectionType.PREFERRED_QUALIFICATIONS:
        return RequirementImportance.PREFERRED

    # In-phrase cues
    if any(cue in lower for cue in PREFERRED_CUES):
        return RequirementImportance.PREFERRED

    if any(cue in lower for cue in CONTEXTUAL_CUES):
        return RequirementImportance.CONTEXTUAL

    if section_type == SectionType.RESPONSIBILITIES:
        return RequirementImportance.CONTEXTUAL

    if any(cue in lower for cue in REQUIRED_CUES):
        return RequirementImportance.REQUIRED

    if section_type == SectionType.REQUIREMENTS:
        return RequirementImportance.REQUIRED

    return RequirementImportance.CONTEXTUAL


def classify_category(
    clause_text: str,
    canonical_skills: list[str],
    min_years: Optional[float],
    is_education: bool
) -> RequirementCategory:
    """Determine the requirement category based on extracted signals."""
    lower = clause_text.lower()

    if is_education:
        return RequirementCategory.EDUCATION

    if min_years is not None and not canonical_skills:
        return RequirementCategory.EXPERIENCE_LEVEL

    if canonical_skills:
        return RequirementCategory.TECHNICAL_SKILL

    if any(kwd in lower for kwd in SOFT_SKILL_KEYWORDS):
        return RequirementCategory.SOFT_SKILL

    if any(kwd in lower for kwd in ["domain", "industry", "fintech", "healthcare", "compliance", "regulations"]):
        return RequirementCategory.DOMAIN_KNOWLEDGE

    return RequirementCategory.TECHNICAL_SKILL


def build_job_description_from_text(
    raw_text: str,
    jd_id: str,
    title: str = ""
) -> JobDescription:
    """Analyze raw JD text and construct a structured JobDescription object."""
    cleaned = raw_text.strip()
    quality = assess_extraction_quality(cleaned, num_pages=1, total_blocks=1, empty_blocks=0)
    sections = split_into_sections(cleaned)
    raw_reqs = extract_raw_requirements(cleaned)
    aliases = load_skill_aliases()

    # Detect title if not provided
    if not title and sections:
        first_lines = sections[0].content.splitlines()
        for line in first_lines[:3]:
            stripped = line.strip()
            if 3 <= len(stripped.split()) <= 8:
                title = stripped
                break
    if not title:
        title = "Job Description"

    classified_reqs: list[JDRequirement] = []
    for req in raw_reqs:
        skills, _ = extract_and_normalize_skills(req["text"], aliases)
        importance = classify_importance(req["text"], req["section_type"])
        category = classify_category(
            req["text"],
            canonical_skills=skills,
            min_years=req["min_years_experience"],
            is_education=req["is_education"]
        )
        
        weight = 1.0
        if importance == RequirementImportance.PREFERRED:
            weight = 0.5
        elif importance == RequirementImportance.CONTEXTUAL:
            weight = 0.25

        classified_reqs.append(JDRequirement(
            id=req["raw_id"],
            text=req["text"],
            category=category,
            importance=importance,
            canonical_skills=skills,
            aliases=[],
            weight=weight,
            min_years_experience=req["min_years_experience"],
            source_section=req["section_header"]
        ))

    bias_flags = detect_jd_bias(cleaned)

    return JobDescription(
        id=jd_id,
        title=title,
        raw_text=cleaned,
        sections=sections,
        requirements=classified_reqs,
        bias_flags=bias_flags,
        extraction_quality=quality
    )


def build_job_description_from_pdf(
    source: Union[str, Path, bytes],
    jd_id: str,
    title: str = ""
) -> JobDescription:
    """Analyze a JD PDF document and construct a structured JobDescription object."""
    full_text, quality = extract_pdf_text(source)
    jd = build_job_description_from_text(full_text, jd_id=jd_id, title=title)
    jd.extraction_quality = quality
    return jd
