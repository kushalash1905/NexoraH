"""Section normalization and header detection for resumes and job descriptions.

Maps messy, non-standard section headings to canonical SectionType enums
using pattern matching, regex heuristics, and fuzzy similarity.
"""

from __future__ import annotations

import re
from typing import Optional
from rapidfuzz import fuzz

from nexora.schemas import SectionType, ParsedSection


# Canonical patterns and header synonyms
SECTION_PATTERNS: dict[SectionType, list[str]] = {
    SectionType.SUMMARY: [
        "summary", "professional summary", "executive summary", "career summary",
        "profile", "professional profile", "personal profile", "about me",
        "objective", "career objective", "personal statement", "overview"
    ],
    SectionType.EXPERIENCE: [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
        "relevant experience", "internships", "employment", "professional background"
    ],
    SectionType.EDUCATION: [
        "education", "academic background", "educational background",
        "academic qualifications", "degrees", "university", "academics",
        "education and training", "education & degrees", "college", "schooling"
    ],
    SectionType.SKILLS: [
        "skills", "technical skills", "core competencies", "technologies",
        "tools and technologies", "tools & technologies", "proficiencies",
        "areas of expertise", "key skills", "skill highlights", "technical proficiencies",
        "programming skills", "competencies", "stack", "technical proficiency", "tech stack", "technology stack", "core competencies & stack"
    ],
    SectionType.PROJECTS: [
        "projects", "key projects", "personal projects", "academic projects",
        "technical projects", "open source projects", "portfolio", "notable projects"
    ],
    SectionType.CERTIFICATIONS: [
        "certifications", "certificates", "licenses & certifications",
        "licenses and certifications", "accreditations", "credentials",
        "courses and certifications"
    ],
    SectionType.PUBLICATIONS: [
        "publications", "papers", "research", "articles", "patents and publications"
    ],
    SectionType.AWARDS: [
        "awards", "honors", "achievements", "recognitions", "accomplishments",
        "honors & awards", "honors and awards"
    ],
    SectionType.RESPONSIBILITIES: [
        "responsibilities", "duties", "what you'll do", "what you will do",
        "role overview", "core responsibilities", "key responsibilities",
        "the role", "job description", "scope of work"
    ],
    SectionType.REQUIREMENTS: [
        "requirements", "minimum qualifications", "basic qualifications",
        "must haves", "required skills", "what we're looking for",
        "required qualifications", "what you need", "eligibility criteria",
        "qualifications", "who you are"
    ],
    SectionType.PREFERRED_QUALIFICATIONS: [
        "preferred qualifications", "preferred qualifications / nice to haves", "nice to haves", "desired qualifications",
        "bonus points", "preferred skills", "pluses", "good to have",
        "what gives you an edge", "bonus qualifications", "nice to have"
    ],
    SectionType.ABOUT: [
        "about us", "about the company", "company overview", "who we are",
        "our mission", "company profile"
    ],
}


def _clean_header_candidate(text: str) -> str:
    """Strip numbering, punctuation, and leading/trailing noise from candidate headers."""
    cleaned = text.strip()
    # Strip markdown headers (#, ##), bullets, colons, numbers
    cleaned = re.sub(r"^[\s#*\->•·\d.]+\s*", "", cleaned)
    cleaned = re.sub(r"[:\-_|]+$", "", cleaned)
    return cleaned.strip()


def is_likely_section_header(line: str) -> bool:
    """Heuristic check to determine if a line of text represents a section header."""
    candidate = _clean_header_candidate(line)
    if not candidate:
        return False
    
    # Headers are rarely long sentences
    if len(candidate) > 55 or len(candidate.split()) > 6:
        return False
    
    # Check if candidate ends with a question mark or semicolon (unlikely header)
    if candidate.endswith(("?", ";", ".")):
        return False
        
    lower = candidate.lower()
    
    # Direct exact keyword check against known patterns
    for patterns in SECTION_PATTERNS.values():
        if lower in patterns:
            return True
            
    # Fuzzy match with patterns
    for patterns in SECTION_PATTERNS.values():
        for pat in patterns:
            if fuzz.ratio(lower, pat) >= 85:
                return True
                
    return False


def classify_section_header(header_text: str) -> tuple[SectionType, float]:
    """Classify a detected header into a canonical SectionType with a confidence score.
    
    Returns:
        tuple[SectionType, float]: The classified canonical section type and confidence score (0.0 to 1.0).
    """
    clean = _clean_header_candidate(header_text).lower()
    if not clean:
        return SectionType.OTHER, 0.0

    # 1. Exact match
    for sec_type, patterns in SECTION_PATTERNS.items():
        if clean in patterns:
            return sec_type, 1.0

    # 2. Conservative fuzzy matching against complete headings
    all_patterns: list[tuple[SectionType, str]] = []
    for sec_type, patterns in SECTION_PATTERNS.items():
        for pat in patterns:
            all_patterns.append((sec_type, pat))
    all_patterns.sort(key=lambda x: len(x[1]), reverse=True)

    # 3. Fuzzy matching via RapidFuzz
    best_type = SectionType.OTHER
    best_score = 0.0
    for sec_type, pat in all_patterns:
        sim = fuzz.ratio(clean, pat) / 100.0
        if sim > best_score:
            best_score = sim
            best_type = sec_type

    if best_score >= 0.85:
        return best_type, round(best_score, 2)
    return SectionType.OTHER, round(best_score, 2)


def split_into_sections(text: str) -> list[ParsedSection]:
    """Split raw text into parsed sections based on detected headers."""
    lines = text.splitlines()
    sections: list[ParsedSection] = []
    
    current_type = SectionType.SUMMARY  # Default initial section is often Summary or Contact
    current_header = "Header / Summary"
    current_content: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content.append(line)
            continue
            
        if is_likely_section_header(stripped):
            sec_type, conf = classify_section_header(stripped)
            if conf >= 0.75 and sec_type != SectionType.OTHER:
                # Save previous section if it has non-empty content
                body = "\n".join(current_content).strip()
                if body:
                    sections.append(ParsedSection(
                        section_type=current_type,
                        raw_header=current_header,
                        content=body,
                        page_start=1,
                        page_end=1
                    ))
                current_type = sec_type
                current_header = stripped
                current_content = []
                continue
                
        current_content.append(line)

    # Flush last section
    body = "\n".join(current_content).strip()
    if body:
        sections.append(ParsedSection(
            section_type=current_type,
            raw_header=current_header,
            content=body,
            page_start=1,
            page_end=1
        ))

    return sections
