"""
JD narrow-language and bias detector.
Transparent local rule-based engine.
Does not make legal or discrimination conclusions.
"""

import re
from typing import List, Dict, Any
from nexora.schemas import BiasFlag, JobDescription

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
        title = jd_input.title
        requirements = jd_input.requirements
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
        req_dict = req if isinstance(req, dict) else req.model_dump()
        if req_dict.get("requirement_type") == "required" and req_dict.get("category") == "technology":
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
