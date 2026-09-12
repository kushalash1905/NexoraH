"""Evidence unit extraction and candidate profile construction.

Segments resume content into granular evidence units, normalizes skill aliases
and typos, attaches page/section provenance, extracts contact info, and
assembles the structured Candidate schema object.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Union, Optional
from rapidfuzz import fuzz

from nexora.schemas import (
    Candidate,
    EvidenceUnit,
    ParsedSection,
    SectionType,
    ExtractionQuality
)
from nexora.parsers.pdf_parser import extract_pdf_blocks, extract_pdf_text
from nexora.parsers.section_normalizer import (
    classify_section_header,
    is_likely_section_header,
    split_into_sections
)
from nexora.parsers.date_normalizer import (
    extract_date_range,
    calculate_total_experience_months
)

# Load aliases and ontology
_ALIASES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "aliases.json"


def load_skill_aliases() -> dict[str, str]:
    """Load canonical skill alias mapping from data/aliases.json."""
    if not _ALIASES_PATH.exists():
        return {}
    try:
        with open(_ALIASES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("aliases", {})
    except Exception:
        return {}


EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")


def extract_contact_info(text: str) -> tuple[str, Optional[str], Optional[str]]:
    """Extract candidate name, email, and phone from header text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    email = None
    phone = None
    email_match = EMAIL_REGEX.search(text)
    if email_match:
        email = email_match.group(0)
    
    phone_match = PHONE_REGEX.search(text)
    if phone_match:
        phone = phone_match.group(0)

    # Name is typically the first non-empty line before section headers or contact details
    name = "Candidate"
    for line in lines[:5]:
        if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
            continue
        clean_line = re.sub(r"[^A-Za-z\s.-]", "", line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4 and not is_likely_section_header(line):
            name = clean_line
            break

    return name, email, phone


def segment_text_into_bullets(text: str) -> list[str]:
    """Segment a section body into discrete bullet points or sentences."""
    # Split on explicit bullet characters or newlines
    lines = re.split(r"[\n\r]+", text)
    units: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Remove leading bullet symbols
        clean_bullet = re.sub(r"^[\s*•·\->\d.]+\s*", "", stripped).strip()
        if len(clean_bullet) > 10:
            units.append(clean_bullet)

    # If no lines were extracted, fallback to sentence splitting
    if not units and text.strip():
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        units = [s.strip() for s in sentences if len(s.strip()) > 10]

    return units


def extract_and_normalize_skills(
    text: str,
    aliases_dict: Optional[dict[str, str]] = None
) -> tuple[list[str], list[dict]]:
    """Scan text for known skill keywords, apply alias mappings and typo corrections.
    
    Returns:
        tuple[list[str], list[dict]]: Deduplicated list of canonical skill names,
        and normalization audit logs.
    """
    if aliases_dict is None:
        aliases_dict = load_skill_aliases()

    matched_skills: set[str] = set()
    norm_logs: list[dict] = []
    text_lower = f" {text.lower()} "

    # 1. Direct and multi-word phrase matching with word boundaries
    for alias, canonical in aliases_dict.items():
        pattern = rf"(?<![a-zA-Z0-9_-]){re.escape(alias)}(?![a-zA-Z0-9_-])"
        if re.search(pattern, text_lower):
            matched_skills.add(canonical)
            if alias.lower() != canonical.lower():
                norm_logs.append({
                    "original": alias,
                    "canonical": canonical,
                    "match_type": "alias_lookup",
                    "confidence": 1.0
                })

    # 2. Fuzzy typo detection for isolated tokens of reasonable length
    words = re.findall(r"\b[a-zA-Z]{5,15}\b", text_lower)
    for word in set(words):
        if word in aliases_dict:
            continue
        choices = {}
        for alias, canonical in aliases_dict.items():
            if len(alias) >= 5 and abs(len(word)-len(alias)) <= 1:
                sim = fuzz.ratio(word, alias)
                choices[canonical] = max(choices.get(canonical,0),sim)
        ordered = sorted(choices.items(), key=lambda item: -item[1])
        if ordered and ordered[0][1] >= 90 and (len(ordered)==1 or ordered[0][1]-ordered[1][1] >= 5):
            canonical, sim = ordered[0]
            matched_skills.add(canonical)
            norm_logs.append(dict(original=word,canonical=canonical,match_type="typo_fuzzy_match",confidence=round(sim/100,2)))

    return sorted(list(matched_skills)), norm_logs


def build_candidate_from_pdf(
    source: Union[str, Path, bytes],
    candidate_id: str
) -> Candidate:
    """Ingest a candidate resume PDF and produce a fully structured Candidate object."""
    blocks, quality = extract_pdf_blocks(source)
    aliases = load_skill_aliases()

    # Aggregate text for overall contact info and full sections
    full_text = "\n\n".join(b["text"] for b in blocks)
    name, email, phone = extract_contact_info(full_text)

    # Classify blocks into sections based on bounding boxes and detected headers
    sections: list[ParsedSection] = []
    current_sec_type = SectionType.SUMMARY
    current_header = "Header"
    current_blocks: list[dict] = []
    evidence_units: list[EvidenceUnit] = []
    all_extracted_skills: set[str] = set()
    all_norm_logs: list[dict] = []
    experience_ranges: list[dict] = []

    unit_counter = 1

    for block in blocks:
        text = block["text"]
        lines = text.splitlines()
        first_line = lines[0].strip() if lines else ""

        if is_likely_section_header(first_line):
            sec_type, conf = classify_section_header(first_line)
            if conf >= 0.75 and sec_type != SectionType.OTHER:
                # Flush previous section
                if current_blocks:
                    sec_body = "\n\n".join(b["text"] for b in current_blocks)
                    page_start = current_blocks[0]["page"]
                    page_end = current_blocks[-1]["page"]
                    sections.append(ParsedSection(
                        section_type=current_sec_type,
                        raw_header=current_header,
                        content=sec_body,
                        page_start=page_start,
                        page_end=page_end
                    ))
                all_norm_logs.append(dict(original=first_line, canonical=sec_type.value, match_type="section_header", confidence=conf, page=block["page"]))
                current_sec_type = sec_type
                current_header = first_line
                current_blocks = []

                remaining_lines = "\n".join(lines[1:]).strip()
                if not remaining_lines:
                    continue
                text = remaining_lines

        current_blocks.append(block)

        # Build evidence unit from block
        bullets = segment_text_into_bullets(text)
        date_info = extract_date_range(text)
        if date_info:
            all_norm_logs.append(dict(original=text, canonical=date_info["start_iso"]+" to "+date_info["end_iso"], match_type="date_range", warnings=date_info.get("warnings", []), page=block["page"]))
        if date_info and current_sec_type == SectionType.EXPERIENCE:
            experience_ranges.append(date_info)

        for bullet in bullets:
            unit_skills, unit_logs = extract_and_normalize_skills(bullet, aliases)
            all_extracted_skills.update(unit_skills)
            for log in unit_logs:
                log["unit_id"] = f"ev_{unit_counter}"
                all_norm_logs.append(log)

            ev = EvidenceUnit(
                unit_id=f"ev_{unit_counter}",
                candidate_id=candidate_id,
                text=bullet,
                section_type=current_sec_type,
                page_number=block["page"],
                bbox=block.get("bbox"),
                canonical_skills=unit_skills,
                date_start=date_info.get("start_iso") if date_info else None,
                date_end=date_info.get("end_iso") if date_info else None,
                duration_months=date_info.get("duration_months") if date_info else None
            )
            evidence_units.append(ev)
            unit_counter += 1

    # Flush final section
    if current_blocks:
        sec_body = "\n\n".join(b["text"] for b in current_blocks)
        sections.append(ParsedSection(
            section_type=current_sec_type,
            raw_header=current_header,
            content=sec_body,
            page_start=current_blocks[0]["page"],
            page_end=current_blocks[-1]["page"]
        ))

    total_exp_months = calculate_total_experience_months(experience_ranges)

    return Candidate(
        id=candidate_id,
        name=name,
        email=email,
        phone=phone,
        raw_text="\n\n".join(b.get("raw_text", b["text"]) for b in blocks),
        sections=sections,
        evidence_units=evidence_units,
        extracted_skills=sorted(list(all_extracted_skills)),
        total_experience_months=total_exp_months,
        extraction_quality=quality,
        normalization_log=all_norm_logs
    )


def build_candidate_from_text(
    raw_text: str,
    candidate_id: str
) -> Candidate:
    """Ingest raw resume text and produce a structured Candidate object."""
    from nexora.parsers.pdf_parser import assess_extraction_quality

    from nexora.parsers.pdf_parser import clean_text
    cleaned = clean_text(raw_text)
    quality = assess_extraction_quality(cleaned, num_pages=1, total_blocks=1, empty_blocks=0)
    aliases = load_skill_aliases()

    name, email, phone = extract_contact_info(cleaned)
    sections = split_into_sections(cleaned)
    
    evidence_units: list[EvidenceUnit] = []
    all_extracted_skills: set[str] = set()
    all_norm_logs: list[dict] = []
    experience_ranges: list[dict] = []
    unit_counter = 1

    for sec in sections:
        all_norm_logs.append(dict(original=sec.raw_header, canonical=sec.section_type.value, match_type="section_header", confidence=1.0))
        bullets = segment_text_into_bullets(sec.content)
        date_info = extract_date_range(sec.content)
        if date_info:
            all_norm_logs.append(dict(original=sec.content, canonical=date_info["start_iso"]+" to "+date_info["end_iso"], match_type="date_range", warnings=date_info.get("warnings", [])))
        if date_info and sec.section_type == SectionType.EXPERIENCE:
            experience_ranges.append(date_info)

        for bullet in bullets:
            unit_skills, unit_logs = extract_and_normalize_skills(bullet, aliases)
            all_extracted_skills.update(unit_skills)
            for log in unit_logs:
                log["unit_id"] = f"ev_{unit_counter}"
                all_norm_logs.append(log)

            ev = EvidenceUnit(
                unit_id=f"ev_{unit_counter}",
                candidate_id=candidate_id,
                text=bullet,
                section_type=sec.section_type,
                page_number=1,
                canonical_skills=unit_skills,
                date_start=date_info.get("start_iso") if date_info else None,
                date_end=date_info.get("end_iso") if date_info else None,
                duration_months=date_info.get("duration_months") if date_info else None
            )
            evidence_units.append(ev)
            unit_counter += 1

    total_exp_months = calculate_total_experience_months(experience_ranges)

    return Candidate(
        id=candidate_id,
        name=name,
        email=email,
        phone=phone,
        raw_text=raw_text,
        sections=sections,
        evidence_units=evidence_units,
        extracted_skills=sorted(list(all_extracted_skills)),
        total_experience_months=total_exp_months,
        extraction_quality=quality,
        normalization_log=all_norm_logs
    )
