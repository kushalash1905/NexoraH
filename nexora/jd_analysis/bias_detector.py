"""Job Description bias and exclusionary wording detector.

Identifies gender-coded terms, ageist phrases, elitist pedigree filters,
and unrealistic tenure constraints, providing actionable explanations and
inclusive replacement suggestions.
"""

from __future__ import annotations

import re
from nexora.schemas import JDBiasFlag

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
