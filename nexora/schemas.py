"""Shared data schemas for the NEXORA candidate intelligence system.

This module provides common Pydantic models for representing structured
Job Descriptions, Candidates/Resumes, Evidence Units, Requirements, and
extraction quality metadata across all pipeline components.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List


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
    unit_id: str = ""
    evidence_id: str = ""
    candidate_id: str
    text: str
    section_type: SectionType = SectionType.OTHER
    normalized_text: str = ""
    section: str = "other"
    source_type: str = "other"
    page: int = 1
    position: int = 0
    has_action_verb: bool = False
    has_outcome: bool = False
    has_duration: bool = False
    repetition_count: int = 1
    base_strength: float = 0.65
    page_number: int = 1
    bbox: Optional[tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)
    canonical_skills: list[str] = Field(default_factory=list)
    date_start: Optional[str] = None  # e.g., "2021-01"
    date_end: Optional[str] = None    # e.g., "2023-06" or "Present"
    duration_months: Optional[int] = None


    @model_validator(mode="before")
    @classmethod
    def synchronize_evidence(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        data.setdefault("evidence_id", data.get("unit_id", ""))
        data.setdefault("unit_id", data.get("evidence_id", ""))
        if not data.get("evidence_id"):
            raise ValueError("Evidence requires evidence_id or unit_id")
        section = data.get("section", data.get("section_type", "other"))
        section = getattr(section, "value", section)
        data.setdefault("section", section)
        data.setdefault("section_type", section)
        data.setdefault("page", data.get("page_number", 1))
        data.setdefault("page_number", data.get("page", 1))
        data.setdefault("normalized_text", str(data.get("text", "")).lower())
        data.setdefault("has_duration", bool(data.get("duration_months") or data.get("date_start")))
        return data


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
    id: str = ""
    jd_id: str = ""
    company: str = ""
    title: str = ""
    raw_text: str = ""
    sections: list[ParsedSection] = Field(default_factory=list)
    requirements: list[JDRequirement | Requirement] = Field(default_factory=list)
    bias_flags: list[JDBiasFlag | dict[str, Any]] = Field(default_factory=list)
    extraction_quality: ExtractionQuality | float = Field(default_factory=ExtractionQuality)


    @model_validator(mode="before")
    @classmethod
    def synchronize_id(cls, data):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("jd_id", data.get("id", ""))
            data.setdefault("id", data.get("jd_id", ""))
        return data


class Candidate(BaseModel):
    """Structured representation of an ingested Candidate resume."""
    id: str = ""
    candidate_id: str = ""
    resume: Optional[dict[str, Any]] = None
    normalized_skills: list[str] = Field(default_factory=list)
    experience_relevance: float = 0.0
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str = ""
    sections: list[ParsedSection] = Field(default_factory=list)
    evidence_units: list[EvidenceUnit] = Field(default_factory=list)
    extracted_skills: list[str] = Field(default_factory=list)
    total_experience_months: int = 0
    extraction_quality: ExtractionQuality | float = Field(default_factory=ExtractionQuality)
    normalization_log: list[dict[str, Any]] = Field(default_factory=list)


    @model_validator(mode="before")
    @classmethod
    def synchronize_candidate(cls, data):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("candidate_id", data.get("id", ""))
            data.setdefault("id", data.get("candidate_id", ""))
            data.setdefault("normalized_skills", data.get("extracted_skills", []))
            data.setdefault("extracted_skills", data.get("normalized_skills", []))
        return data


class RequirementRelatedSkill(BaseModel):
    """Related skill mapping with support coefficient."""
    canonical: str
    support: float = Field(default=0.5, ge=0.0, le=1.0)

class Requirement(BaseModel):
    """Structured job description requirement."""
    requirement_id: str
    text: str
    canonical: str
    category: str = Field(default="technology", description="technology, responsibility, domain, experience, education, soft_context")
    requirement_type: str = Field(default="required", description="required, preferred, contextual")
    importance: float = Field(default=1.0, ge=0.0)
    aliases: List[str] = Field(default_factory=list)
    related_skills: List[RequirementRelatedSkill] = Field(default_factory=list)
    source_text: str = ""

class Resume(BaseModel):
    """Structured candidate resume document."""
    candidate_id: str
    name: str
    raw_text: str = ""
    sections: Dict[str, List[str]] = Field(default_factory=dict)
    evidence_units: List[EvidenceUnit] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    normalization_log: List[Dict[str, Any]] = Field(default_factory=list)
    extraction_quality: float = Field(default=1.0, ge=0.0, le=1.0)

class RequirementMatch(BaseModel):
    """Detailed match evaluation for a single requirement and candidate."""
    candidate_id: str
    requirement_id: str
    keyword_score: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ontology_support: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    context_guard: float = Field(default=1.0, ge=0.0, le=1.0)
    final_requirement_score: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = Field(default="no_reliable_evidence", description="strong_match, partial_match, weak_match, no_reliable_evidence")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(default_factory=list)

class CandidateScore(BaseModel):
    """Aggregated score and diagnostics for a candidate."""
    candidate_id: str
    name: str
    rank: int = 0
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence_label: str = Field(default="Low", description="High, Medium, Low")
    required_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    preferred_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    keyword_alignment: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_alignment: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    experience_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_required: List[str] = Field(default_factory=list)
    matched_requirements: List[str] = Field(default_factory=list)
    requirement_matches: List[RequirementMatch] = Field(default_factory=list)
    lexical_only_pattern: bool = False

class RankingSensitivity(BaseModel):
    """Sensitivity analysis across varying semantic weights."""
    semantic_weights_tested: List[float] = Field(default_factory=lambda: [0.30, 0.40, 0.50])
    stable_top_three: bool = True
    rank_changes: List[Dict[str, Any]] = Field(default_factory=list)

class RankingResult(BaseModel):
    """Overall ranking output for the job description and candidate pool."""
    jd_id: str
    candidate_count: int
    ranked_candidates: List[CandidateScore] = Field(default_factory=list)
    top_three_explanations: List[Dict[str, Any]] = Field(default_factory=list)
    sensitivity: RankingSensitivity = Field(default_factory=RankingSensitivity)

JobDescription.model_rebuild()
