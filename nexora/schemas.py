"""Shared data schemas for the NEXORA candidate intelligence system.

This module provides common Pydantic models for representing structured
Job Descriptions, Candidates/Resumes, Evidence Units, Requirements, and
extraction quality metadata across all pipeline components.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class RequirementImportance(str, Enum):
    """Importance classification for a job description requirement."""
    REQUIRED = "required"
    PREFERRED = "preferred"
    CONTEXTUAL = "contextual"


class RequirementCategory(str, Enum):
    """Categorization of a job description requirement."""
    TECHNICAL_SKILL = "technical_skill"
    EXPERIENCE_LEVEL = "experience_level"
    EDUCATION = "education"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    SOFT_SKILL = "soft_skill"


class SectionType(str, Enum):
    """Canonical section types across resumes and job descriptions."""
    # Resume sections
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    PUBLICATIONS = "publications"
    AWARDS = "awards"
    
    # JD-specific sections
    RESPONSIBILITIES = "responsibilities"
    REQUIREMENTS = "requirements"
    PREFERRED_QUALIFICATIONS = "preferred_qualifications"
    ABOUT = "about"
    
    # Generic / Fallback
    OTHER = "other"


class ExtractionQuality(BaseModel):
    """Extraction quality diagnostics and messy-document detection metadata."""
    word_count: int = 0
    page_count: int = 1
    unparsed_blocks_count: int = 0
    density_ratio: float = 1.0
    is_messy: bool = False
    warnings: list[str] = Field(default_factory=list)
    quality_score: float = 1.0  # Normalized 0.0 to 1.0 scale


class ParsedSection(BaseModel):
    """A detected and normalized section within a document."""
    section_type: SectionType
    raw_header: str
    content: str
    page_start: int = 1
    page_end: int = 1


class EvidenceUnit(BaseModel):
    """A granular evidence segment (bullet/sentence) with provenance and skill metadata."""
    unit_id: str
    candidate_id: str
    text: str
    section_type: SectionType
    page_number: int = 1
    bbox: Optional[tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)
    canonical_skills: list[str] = Field(default_factory=list)
    date_start: Optional[str] = None  # e.g., "2021-01"
    date_end: Optional[str] = None    # e.g., "2023-06" or "Present"
    duration_months: Optional[int] = None


class JDBiasFlag(BaseModel):
    """Diagnostic flag for potentially narrow, exclusionary, or biased JD wording."""
    phrase: str
    bias_type: str  # e.g., "gender_coded", "ageist", "elitist_credential", "unreasonable_tenure"
    explanation: str
    alternative_suggestion: str


class JDRequirement(BaseModel):
    """A structured, classified requirement extracted from a Job Description."""
    id: str
    text: str
    category: RequirementCategory
    importance: RequirementImportance
    canonical_skills: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    weight: float = 1.0
    min_years_experience: Optional[float] = None
    source_section: Optional[str] = None


class JobDescription(BaseModel):
    """Structured representation of an ingested Job Description."""
    id: str
    title: str = ""
    raw_text: str = ""
    sections: list[ParsedSection] = Field(default_factory=list)
    requirements: list[JDRequirement] = Field(default_factory=list)
    bias_flags: list[JDBiasFlag] = Field(default_factory=list)
    extraction_quality: ExtractionQuality = Field(default_factory=ExtractionQuality)


class Candidate(BaseModel):
    """Structured representation of an ingested Candidate resume."""
    id: str
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str = ""
    sections: list[ParsedSection] = Field(default_factory=list)
    evidence_units: list[EvidenceUnit] = Field(default_factory=list)
    extracted_skills: list[str] = Field(default_factory=list)
    total_experience_months: int = 0
    extraction_quality: ExtractionQuality = Field(default_factory=ExtractionQuality)
    normalization_log: list[dict[str, Any]] = Field(default_factory=list)
