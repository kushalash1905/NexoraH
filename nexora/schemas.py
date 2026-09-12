"""Authoritative data schemas for the NEXORA candidate intelligence system.

All modules (parsers, matching, ranking, explanations, and UI) adhere to these models.
Both Pydantic model validation and dict-like serialization are supported.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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


class JobDescription(BaseModel):
    """Structured Job Description document."""
    jd_id: str
    title: str
    company: str = ""
    raw_text: str = ""
    requirements: List[Requirement] = Field(default_factory=list)
    bias_flags: List[Dict[str, Any]] = Field(default_factory=list)
    extraction_quality: float = Field(default=1.0, ge=0.0, le=1.0)


class EvidenceUnit(BaseModel):
    """Granular resume evidence unit (sentence or bullet) with provenance."""
    evidence_id: str
    candidate_id: str
    text: str
    normalized_text: str
    section: str = Field(default="projects", description="skills, summary, experience, projects, education, certifications, other")
    source_type: str = "project"
    page: int = 1
    position: int = 0
    has_action_verb: bool = False
    has_outcome: bool = False
    has_duration: bool = False
    repetition_count: int = 1
    base_strength: float = Field(default=0.65, ge=0.0, le=1.0)


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


class Candidate(BaseModel):
    """Standard candidate input model for matching."""
    candidate_id: str
    name: str
    resume: Optional[Dict[str, Any]] = None
    evidence_units: List[EvidenceUnit] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list)
    experience_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
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
