"""Job description requirement extraction and phrase de-compounding.

Identifies requirements across qualifications and responsibilities sections,
splits multi-part compound requirements, and extracts constraints such as
years of experience and degree criteria.
"""

from __future__ import annotations

import re
from typing import Optional

from nexora.schemas import SectionType
from nexora.parsers.section_normalizer import split_into_sections


YEARS_EXP_REGEX = re.compile(
    r"(?:(?:at\s+least|minimum|min\.?)\s*)?(\d+(?:\.\d+)?)(?:\s*(?:-|to|\+)\s*(\d+(?:\.\d+)?))?\s*\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?",
    re.IGNORECASE
)

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "bs", "ba", "ms", "ma",
    "b.s.", "b.a.", "m.s.", "m.a.", "ph.d.", "degree in computer science",
    "degree in engineering", "stem"
]


def extract_years_of_experience(text: str) -> Optional[float]:
    """Extract minimum required years of experience mentioned in a requirement phrase."""
    match = YEARS_EXP_REGEX.search(text)
    if match:
        min_years_str = match.group(1)
        try:
            return float(min_years_str)
        except ValueError:
            return None
    return None


def is_education_requirement(text: str) -> bool:
    """Check if requirement phrase relates to degree or academic background."""
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(kwd)}\b", lower) for kwd in EDUCATION_KEYWORDS)


def decompound_requirement_phrase(phrase: str) -> list[str]:
    """Split compound requirements separated by semicolons or complex conjunctions.
    
    Preserves context when possible (e.g. 'Must have 5+ years of experience with Python, Docker, and AWS').
    """
    clean = phrase.strip()
    # Split on semicolons first
    parts = [p.strip() for p in re.split(r";\s*", clean) if len(p.strip()) > 5]
    
    # If single sentence with 'as well as' or 'along with'
    expanded_parts: list[str] = []
    for part in parts:
        subparts = re.split(r"\s+(?:as well as|along with)\s+", part, flags=re.IGNORECASE)
        expanded_parts.extend([sp.strip() for sp in subparts if len(sp.strip()) > 5])
        
    return expanded_parts if expanded_parts else [clean]


def extract_raw_requirements(jd_text: str) -> list[dict]:
    """Parse sections and extract raw requirement clauses with metadata."""
    sections = split_into_sections(jd_text)
    extracted: list[dict] = []
    req_id_counter = 1

    for sec in sections:
        lines = re.split(r"[\n\r]+", sec.content)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Strip leading bullets or numbering
            clean_clause = re.sub(r"^[\s*•·\->\d.]+\s*", "", stripped).strip()
            if len(clean_clause) < 8:
                continue

            sub_clauses = decompound_requirement_phrase(clean_clause)
            for clause in sub_clauses:
                exp_years = extract_years_of_experience(clause)
                is_edu = is_education_requirement(clause)

                extracted.append({
                    "raw_id": f"req_{req_id_counter}",
                    "text": clause,
                    "section_type": sec.section_type,
                    "section_header": sec.raw_header,
                    "min_years_experience": exp_years,
                    "is_education": is_edu
                })
                req_id_counter += 1

    return extracted
