"""
Job Description narrow-language and bias detector.

Provides both rule-based narrow requirement analysis (Person 4)
and gender-coded, ageist, elitist, and tenure constraint analysis (Person 1).
"""

from __future__ import annotations

import re
from typing import List, Dict, Any
from nexora.schemas import BiasFlag, JDBiasFlag

ABSOLUTE_PHRASES = [
    "must have",
    "only candidates",
    "non-negotiable",
    "strictly required",
    "perfect knowledge"
]

JUNIOR_CONTEXT_WORDS = ["intern", "internship", "junior", "entry-level", "entry level", "graduate"]
EQUIVALENT_WORDS = ["similar", "related", "comparable", "equivalent"]


def detect_bias_flags(jd_input: Any) -> List[Dict[str, Any]]:
    """
    Analyzes JD text or dict/schema for potentially narrow or restrictive wording.
    Returns a list of structured bias flags as dicts.
    """
    if isinstance(jd_input, dict):
        raw_text = jd_input.get("raw_text", "")
        title = jd_input.get("title", "")
        requirements = jd_input.get("requirements", [])
    elif hasattr(jd_input, "raw_text"):
        raw_text = jd_input.raw_text
        title = getattr(jd_input, "title", "")
        requirements = getattr(jd_input, "requirements", [])
    else:
        raw_text = str(jd_input)
        title = ""
        requirements = []

    flags: List[BiasFlag] = []
    text_lower = raw_text.lower()
    title_lower = title.lower()

    # Rule 1: Excessive years of experience for junior / intern role
    is_junior_context = any(w in title_lower or w in text_lower for w in JUNIOR_CONTEXT_WORDS)
    year_matches = re.finditer(r'(\d+)\+?\s*years?', text_lower)

    for m in year_matches:
        years_num = int(m.group(1))
        matched_phrase = m.group(0)

        if is_junior_context and years_num >= 2:
            flags.append(BiasFlag(
                phrase=matched_phrase,
                reason="Potentially narrow requirement for an internship or junior role.",
                suggestion="Consider equivalent project or internship experience.",
                severity="medium"
            ))
            break  # Flag once

    # Rule 2: Absolute wording
    for phrase in ABSOLUTE_PHRASES:
        if phrase in text_lower:
            sev = "high" if phrase in ["non-negotiable", "strictly required"] else "medium"
            flags.append(BiasFlag(
                phrase=phrase,
                reason="Potentially narrow wording: absolute language may exclude equivalent experience.",
                suggestion="Consider replacing rigid mandates with demonstrated skills or relevant projects.",
                severity=sev
            ))

    # Rule 3: Too many mandatory technologies (>= 5)
    req_tech_count = 0
    for req in requirements:
        req_dict = req if isinstance(req, dict) else (req.model_dump() if hasattr(req, "model_dump") else {})
        if req_dict.get("requirement_type") == "required" and req_dict.get("category") in ["technology", "technical_skill"]:
            req_tech_count += 1

    if req_tech_count >= 5:
        flags.append(BiasFlag(
            phrase=f"{req_tech_count} mandatory technologies required",
            reason="Potentially narrow wording: the JD may be overly specific about tools.",
            suggestion="Consider distinguishing core required skills from preferred tools.",
            severity="medium"
        ))

    # Rule 4: Missing equivalent-skill language
    if req_tech_count > 0 and not any(w in text_lower for w in EQUIVALENT_WORDS):
        flags.append(BiasFlag(
            phrase="No equivalent technology language",
            reason="The JD may benefit from explicitly accepting equivalent technologies or demonstrated project experience.",
            suggestion="Add wording such as 'or equivalent framework/experience'.",
            severity="low"
        ))

    return [f.model_dump() for f in flags]


BIAS_RULES: list[dict] = [
    # Gender-coded terminology
    {
        "pattern": r"\b(rockstar|ninja|hacker|guru)\b",
        "bias_type": "gender_coded",
        "explanation": "Overly aggressive or hyper-masculine archetype terms can discourage diverse applicants.",
        "suggestion": "Replace with professional descriptors such as 'expert', 'senior engineer', or 'specialist'."
    },
    {
        "pattern": r"\b(work\s+hard\s*,?\s*play\s+hard)\b",
        "bias_type": "gender_coded",
        "explanation": "Implies an all-consuming work culture that discourages candidates with caregiving responsibilities.",
        "suggestion": "Emphasize sustainable high performance, collaboration, and work-life balance."
    },
    {
        "pattern": r"\b(aggressive|dominate|crush\s+it)\b",
        "bias_type": "gender_coded",
        "explanation": "Aggressive, combative language skews male-coded and can reduce applicant diversity.",
        "suggestion": "Use growth-oriented terms like 'ambitious', 'results-driven', or 'proactive'."
    },

    # Ageist language
    {
        "pattern": r"\b(digital\s+native|young\s+and\s+energetic|youthful)\b",
        "bias_type": "ageist",
        "explanation": "Coded phrases that subtly or explicitly discriminate based on candidate age.",
        "suggestion": "Focus on required competencies, such as 'proficient with modern web technologies' or 'dynamic'."
    },
    {
        "pattern": r"\b(recent\s+grad(?:uate)?s?\s+only)\b",
        "bias_type": "ageist",
        "explanation": "Excludes qualified candidates transitioning careers or re-entering the workforce.",
        "suggestion": "Specify entry-level responsibilities rather than limiting candidate graduation recency."
    },

    # Elitist educational pedigree
    {
        "pattern": r"\b(ivy\s+league(?:\s+only)?|top\s+tier\s+(?:university|college|school)s?|premier\s+institutes?)\b",
        "bias_type": "elitist_credential",
        "explanation": "Arbitrary institutional pedigree requirements disadvantage candidates from non-traditional or diverse backgrounds.",
        "suggestion": "Specify core knowledge and demonstrable skill competencies instead of institutional pedigree."
    },

    # Unrealistic tenure constraints for modern technologies
    {
        "pattern": r"\b(?:1[0-9]|20)\+?\s*years?(?:\s+of)?(?:\s+experience)?(?:\s+with|\s+in)?\s+(?:kubernetes|k8s|fastapi|flutter|rust)\b",
        "bias_type": "unrealistic_tenure",
        "explanation": "Demands experience exceeding or nearly matching the entire existence of the technology.",
        "suggestion": "Lower tenure requirements to realistic durations (e.g., 3-5 years) focusing on project depth."
    }
]


def detect_jd_bias(jd_text: str) -> list[JDBiasFlag]:
    """Scan Job Description text for biased, exclusionary, or unrealistic language."""
    flags: list[JDBiasFlag] = []
    seen_phrases: set[str] = set()

    for rule in BIAS_RULES:
        for match in re.finditer(rule["pattern"], jd_text, re.IGNORECASE):
            phrase = match.group(0).strip()
            phrase_lower = phrase.lower()
            if phrase_lower in seen_phrases:
                continue
            seen_phrases.add(phrase_lower)

            flags.append(JDBiasFlag(
                phrase=phrase,
                bias_type=rule["bias_type"],
                explanation=rule["explanation"],
                alternative_suggestion=rule["suggestion"]
            ))

    return flags
