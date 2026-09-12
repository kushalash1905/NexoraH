"""
Shared data schemas for the NEXORA candidate intelligence system.

Provides common Pydantic models for representing structured Job Descriptions,
Candidates/Resumes, Evidence Units, Requirements, and Ranking Results.
Fully compatible with both Person 1 matching engine and Person 4 orchestrator.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field, model_validator


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
    TECHNOLOGY = "technical_skill"


class SectionType(str, Enum):
    """Canonical section types across resumes and job descriptions."""
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    PUBLICATIONS = "publications"
    AWARDS = "awards"
    RESPONSIBILITIES = "responsibilities"
    REQUIREMENTS = "requirements"
    PREFERRED_QUALIFICATIONS = "preferred_qualifications"
    ABOUT = "about"
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
    candidate_id: str = ""
    text: str = ""
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
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    duration_months: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def synchronize_evidence(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        data.setdefault("evidence_id", data.get("unit_id", ""))
        data.setdefault("unit_id", data.get("evidence_id", ""))
        section = data.get("section", data.get("section_type", "other"))
        if hasattr(section, "value"):
            section = section.value
        data.setdefault("section", str(section))
        data.setdefault("section_type", section)
        data.setdefault("page", data.get("page_number", 1))
        data.setdefault("page_number", data.get("page", 1))
        data.setdefault("normalized_text", str(data.get("text", "")).lower())
        data.setdefault("has_duration", bool(data.get("duration_months") or data.get("date_start")))
        return data


class JDBiasFlag(BaseModel):
    """Diagnostic flag for potentially narrow, exclusionary, or biased JD wording."""
    phrase: str
    bias_type: str = "general"
    explanation: str = ""
    alternative_suggestion: str = ""
    reason: str = ""
    suggestion: str = ""
    severity: str = "medium"

    @model_validator(mode="before")
    @classmethod
    def synchronize_bias_flag(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        reason = data.get("reason") or data.get("explanation") or ""
        explanation = data.get("explanation") or data.get("reason") or ""
        suggestion = data.get("suggestion") or data.get("alternative_suggestion") or ""
        alt_suggestion = data.get("alternative_suggestion") or data.get("suggestion") or ""
        data.setdefault("reason", reason)
        data.setdefault("explanation", explanation)
        data.setdefault("suggestion", suggestion)
        data.setdefault("alternative_suggestion", alt_suggestion)
        return data


BiasFlag = JDBiasFlag


class RequirementRelatedSkill(BaseModel):
    """Related skill mapping with support coefficient."""
    canonical: str
    support: float = Field(default=0.5, ge=0.0, le=1.0)


class Requirement(BaseModel):
    """Structured job description requirement."""
    requirement_id: str = ""
    id: str = ""
    text: str = ""
    canonical: str = ""
    category: Any = "technical_skill"
    requirement_type: Any = "required"
    importance: Any = 1.0
    aliases: List[str] = Field(default_factory=list)
    related_skills: List[Any] = Field(default_factory=list)
    source_text: str = ""
    weight: float = 1.0
    min_years_experience: Optional[float] = None
    source_section: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def synchronize_req_id(cls, data):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("requirement_id", data.get("id", ""))
            data.setdefault("id", data.get("requirement_id", ""))
            data.setdefault("canonical", data.get("text", "").lower())
        return data


JDRequirement = Requirement


class NormalizationLog(BaseModel):
    raw: str
    normalized: str
    method: str = "alias"
    confidence: float = 1.0


class JobDescription(BaseModel):
    """Structured representation of an ingested Job Description."""
    id: str = ""
    jd_id: str = ""
    company: str = ""
    title: str = ""
    raw_text: str = ""
    sections: list[ParsedSection] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    bias_flags: list[JDBiasFlag] = Field(default_factory=list)
    extraction_quality: ExtractionQuality | float = Field(default_factory=ExtractionQuality)
    quality_flags: list[str] = Field(default_factory=list)

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
    sections: Any = Field(default_factory=list)
    evidence_units: list[EvidenceUnit] = Field(default_factory=list)
    extracted_skills: list[str] = Field(default_factory=list)
    total_experience_months: int = 0
    extraction_quality: ExtractionQuality | float = Field(default_factory=ExtractionQuality)
    normalization_log: list[Any] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)

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


ResumeCandidate = Candidate


class Resume(BaseModel):
    """Structured candidate resume document."""
    candidate_id: str
    name: str
    raw_text: str = ""
    sections: Dict[str, List[str]] = Field(default_factory=dict)
    evidence_units: List[EvidenceUnit] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    normalization_log: List[Any] = Field(default_factory=list)
    extraction_quality: float = 1.0
    quality_flags: List[str] = Field(default_factory=list)


class RequirementMatch(BaseModel):
    """Detailed match evaluation for a single requirement and candidate."""
    candidate_id: str
    requirement_id: str
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    ontology_support: float = 0.0
    evidence_strength: float = 0.0
    context_guard: float = 1.0
    final_requirement_score: float = 0.0
    status: str = "no_reliable_evidence"
    confidence: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)


class CandidateScore(BaseModel):
    """Aggregated score and diagnostics for a candidate."""
    candidate_id: str
    name: str
    rank: int = 0
    score: float = 0.0
    confidence: float = 0.0
    confidence_label: str = "Low"
    required_coverage: float = 0.0
    preferred_coverage: float = 0.0
    keyword_alignment: float = 0.0
    semantic_alignment: float = 0.0
    evidence_strength: float = 0.0
    experience_relevance: float = 0.0
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
    sensitivity: Any = Field(default_factory=RankingSensitivity)


class FinalApplicationResult(BaseModel):
    jd: Dict[str, Any]
    ranking: Dict[str, Any]
    explanations: List[Dict[str, Any]] = Field(default_factory=list)
    comparison: Dict[str, Any] = Field(default_factory=dict)
    bias_flags: List[Dict[str, Any]] = Field(default_factory=list)
    normalization_summary: List[Dict[str, Any]] = Field(default_factory=list)


JobDescription.model_rebuild()
