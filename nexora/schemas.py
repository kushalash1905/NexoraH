"""
Authoritative data schemas for Nexora.
Supports both Pydantic models and dictionary serialization for maximum compatibility.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement_id: str
    text: str
    canonical: str
    category: str = "technology"  # technology, responsibility, domain, experience, education, soft_context
    requirement_type: str = "required"  # required, preferred, contextual
    importance: float = 1.0
    aliases: List[str] = Field(default_factory=list)
    related_skills: List[Dict[str, Any]] = Field(default_factory=list)  # [{"canonical": "express", "support": 0.75}]
    source_text: str = ""


class BiasFlag(BaseModel):
    phrase: str
    reason: str
    suggestion: str
    severity: str = "medium"  # low, medium, high


class JobDescription(BaseModel):
    jd_id: str
    title: str
    company: str = ""
    raw_text: str
    requirements: List[Requirement] = Field(default_factory=list)
    bias_flags: List[BiasFlag] = Field(default_factory=list)
    extraction_quality: float = 1.0
    quality_flags: List[str] = Field(default_factory=list)


class EvidenceUnit(BaseModel):
    evidence_id: str
    candidate_id: str
    text: str
    normalized_text: str
    section: str = "other"  # experience, projects, education, certifications, summary, skills
    source_type: str = "other"
    page: int = 1
    position: int = 0
    has_action_verb: bool = False
    has_outcome: bool = False
    has_duration: bool = False
    repetition_count: int = 1
    base_strength: float = 0.50


class NormalizationLog(BaseModel):
    raw: str
    normalized: str
    method: str = "alias"
    confidence: float = 1.0


class ResumeCandidate(BaseModel):
    candidate_id: str
    name: str
    raw_text: str
    sections: Dict[str, List[str]] = Field(default_factory=dict)
    evidence_units: List[EvidenceUnit] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    normalization_log: List[NormalizationLog] = Field(default_factory=list)
    extraction_quality: float = 1.0
    quality_flags: List[str] = Field(default_factory=list)


class RequirementMatch(BaseModel):
    candidate_id: str
    requirement_id: str
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    ontology_support: float = 0.0
    evidence_strength: float = 0.0
    context_guard: float = 1.0
    final_requirement_score: float = 0.0
    status: str = "no_match"  # exact_match, partial_match, weak_match, no_match
    confidence: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)


class CandidateScore(BaseModel):
    candidate_id: str
    name: str
    rank: int = 0
    score: float = 0.0
    confidence: float = 0.0
    confidence_label: str = "Medium"  # High, Medium, Low
    required_coverage: float = 0.0
    preferred_coverage: float = 0.0
    keyword_alignment: float = 0.0
    semantic_alignment: float = 0.0
    evidence_strength: float = 0.0
    experience_relevance: float = 0.0
    missing_required: List[str] = Field(default_factory=list)
    matched_requirements: List[str] = Field(default_factory=list)
    requirement_matches: List[RequirementMatch] = Field(default_factory=list)


class RankingResult(BaseModel):
    jd_id: str
    candidate_count: int
    ranked_candidates: List[CandidateScore] = Field(default_factory=list)
    top_three_explanations: List[Dict[str, Any]] = Field(default_factory=list)
    sensitivity: Dict[str, Any] = Field(default_factory=dict)


class FinalApplicationResult(BaseModel):
    jd: Dict[str, Any]
    ranking: Dict[str, Any]
    explanations: List[Dict[str, Any]] = Field(default_factory=list)
    comparison: Dict[str, Any] = Field(default_factory=dict)
    bias_flags: List[Dict[str, Any]] = Field(default_factory=list)
    normalization_summary: List[Dict[str, Any]] = Field(default_factory=list)
