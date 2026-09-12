"""Comprehensive test suite for Person 2: Document Parsing & Intelligence Layer."""

from __future__ import annotations

import fitz  # PyMuPDF
import pytest

from nexora.schemas import (
    SectionType,
    RequirementImportance,
    RequirementCategory,
    Candidate,
    JobDescription
)
from nexora.parsers.section_normalizer import (
    classify_section_header,
    is_likely_section_header,
    split_into_sections
)
from nexora.parsers.date_normalizer import (
    extract_date_range,
    calculate_total_experience_months
)
from nexora.parsers.pdf_parser import (
    clean_text,
    assess_extraction_quality,
    extract_pdf_blocks,
    extract_pdf_text
)
from nexora.parsers.evidence_builder import (
    extract_contact_info,
    extract_and_normalize_skills,
    build_candidate_from_text,
    build_candidate_from_pdf
)
from nexora.jd_analysis.requirement_extractor import (
    extract_years_of_experience,
    is_education_requirement,
    decompound_requirement_phrase,
    extract_raw_requirements
)
from nexora.jd_analysis.requirement_classifier import (
    classify_importance,
    classify_category,
    build_job_description_from_text
)
from nexora.jd_analysis.bias_detector import detect_jd_bias


# ---------------------------------------------------------------------------
# Section Normalizer Tests
# ---------------------------------------------------------------------------

def test_section_header_classification():
    sec_type, conf = classify_section_header("Work Experience")
    assert sec_type == SectionType.EXPERIENCE
    assert conf >= 0.9

    sec_type, conf = classify_section_header("1. PROFESSIONAL BACKGROUND:")
    assert sec_type == SectionType.EXPERIENCE
    assert conf >= 0.8

    sec_type, conf = classify_section_header("Core Competencies & Stack")
    assert sec_type == SectionType.SKILLS

    sec_type, conf = classify_section_header("Education & Degrees")
    assert sec_type == SectionType.EDUCATION

    sec_type, conf = classify_section_header("Preferred Qualifications / Nice to Haves")
    assert sec_type == SectionType.PREFERRED_QUALIFICATIONS

    sec_type, conf = classify_section_header("What You'll Do")
    assert sec_type == SectionType.RESPONSIBILITIES


def test_is_likely_section_header():
    assert is_likely_section_header("EDUCATION") is True
    assert is_likely_section_header("Work Experience") is True
    assert is_likely_section_header("I developed scalable web applications using Python and Django.") is False
    assert is_likely_section_header("Why do you want this job?") is False


def test_split_into_sections():
    raw_doc = """
Jane Doe
jane.doe@example.com

PROFESSIONAL SUMMARY
Passionate software engineer with 5 years of backend experience.

EXPERIENCE
Software Engineer at Acme Corp (2021 - Present)
- Developed REST APIs in FastAPI and PostgreSQL.

EDUCATION
BS in Computer Science, State University, 2020.
    """
    sections = split_into_sections(raw_doc)
    assert len(sections) >= 3
    types = [s.section_type for s in sections]
    assert SectionType.SUMMARY in types
    assert SectionType.EXPERIENCE in types
    assert SectionType.EDUCATION in types


# ---------------------------------------------------------------------------
# Date Normalizer Tests
# ---------------------------------------------------------------------------

def test_extract_date_range():
    dr1 = extract_date_range("Software Engineer at Google (Jan 2021 - Present)")
    assert dr1 is not None
    assert dr1["start_iso"] == "2021-01"
    assert dr1["end_iso"] == "Present"
    assert dr1["duration_months"] > 30

    dr2 = extract_date_range("03/2019 to 08/2021 Backend Lead")
    assert dr2 is not None
    assert dr2["start_iso"] == "2019-03"
    assert dr2["end_iso"] == "2021-08"
    assert dr2["duration_months"] == 29

    dr3 = extract_date_range("2018 - 2022")
    assert dr3 is not None
    assert dr3["start_iso"] == "2018-01"
    assert dr3["end_iso"] == "2022-12"


def test_calculate_total_experience_months():
    # Two non-overlapping ranges: 12 months + 12 months = 24 months
    ranges = [
        {"start_iso": "2020-01", "end_iso": "2021-01"},
        {"start_iso": "2021-06", "end_iso": "2022-06"},
    ]
    total = calculate_total_experience_months(ranges)
    assert total == 24

    # Overlapping ranges: 2020-01 to 2021-06 and 2020-06 to 2022-01 -> merged is 2020-01 to 2022-01 = 24 months
    overlapping = [
        {"start_iso": "2020-01", "end_iso": "2021-06"},
        {"start_iso": "2020-06", "end_iso": "2022-01"},
    ]
    assert calculate_total_experience_months(overlapping) == 24


# ---------------------------------------------------------------------------
# Text Cleanup & Extraction Quality Tests
# ---------------------------------------------------------------------------

def test_clean_text():
    raw = "Here is an archi-\ntecture with ﬁne ligatures • and bullet points."
    cleaned = clean_text(raw)
    assert "architecture" in cleaned
    assert "fine" in cleaned
    assert "*" in cleaned


def test_assess_extraction_quality():
    clean_sample = "This is a clean and well-formed technical resume for a Senior Software Engineer. " * 15
    q_good = assess_extraction_quality(clean_sample, num_pages=1, total_blocks=5, empty_blocks=0)
    assert q_good.quality_score >= 0.85
    assert q_good.is_messy is False

    messy_sample = "$#@ %^& *() 123 456"
    q_bad = assess_extraction_quality(messy_sample, num_pages=1, total_blocks=5, empty_blocks=4)
    assert q_bad.quality_score < 0.70
    assert q_bad.is_messy is True
    assert len(q_bad.warnings) > 0


# ---------------------------------------------------------------------------
# Skill & Alias Normalization Tests
# ---------------------------------------------------------------------------

def test_extract_and_normalize_skills():
    text = "Proficient in pyhton, react.js, k8s, docker, and posgresql database."
    skills, logs = extract_and_normalize_skills(text)
    
    assert "Python" in skills
    assert "React" in skills
    assert "Kubernetes" in skills
    assert "Docker" in skills
    assert "PostgreSQL" in skills
    
    # Check that normalization logs captured typo/alias
    canonical_logs = {log["canonical"] for log in logs}
    assert "Python" in canonical_logs
    assert "Kubernetes" in canonical_logs


# ---------------------------------------------------------------------------
# Evidence Builder & Candidate Profile Tests
# ---------------------------------------------------------------------------

def test_extract_contact_info():
    header = """
    Alex Johnson
    alex.johnson@example.com
    (555) 123-4567 | San Francisco, CA
    """
    name, email, phone = extract_contact_info(header)
    assert name == "Alex Johnson"
    assert email == "alex.johnson@example.com"
    assert "555" in phone


def test_build_candidate_from_text():
    resume_text = """
    Alex Johnson
    alex.johnson@example.com
    555-123-4567

    SUMMARY
    Senior Full-Stack Engineer with 6 years of experience building scalable systems.

    EXPERIENCE
    Senior Engineer at Acme Corp (01/2021 - Present)
    - Architected microservices with Python, FastAPI, and Docker.
    - Managed Kubernetes clusters and PostgreSQL databases.

    Software Engineer at Beta Inc (01/2018 - 12/2020)
    - Developed frontend dashboards using React and TypeScript.

    EDUCATION
    BS in Computer Science, University of California, 2017.
    """
    cand = build_candidate_from_text(resume_text, candidate_id="cand_01")
    assert isinstance(cand, Candidate)
    assert cand.name == "Alex Johnson"
    assert cand.email == "alex.johnson@example.com"
    assert "Python" in cand.extracted_skills
    assert "FastAPI" in cand.extracted_skills
    assert "Docker" in cand.extracted_skills
    assert "Kubernetes" in cand.extracted_skills
    assert "React" in cand.extracted_skills
    assert cand.total_experience_months > 60
    assert len(cand.evidence_units) >= 3


# ---------------------------------------------------------------------------
# Synthetic In-Memory PDF Parser Tests
# ---------------------------------------------------------------------------

def test_pdf_parser_with_synthetic_pdf():
    # Create a 2-page synthetic PDF with header/footer
    doc = fitz.open()
    
    page1 = doc.new_page()
    page1.insert_text((50, 30), "Confidential - Header Text", fontsize=10)
    page1.insert_text((50, 100), "Sarah Connor\nsarah@sky.net\n(555) 000-1111", fontsize=12)
    page1.insert_text(
        (50, 180),
        "PROFESSIONAL SUMMARY\n"
        "Lead AI defense specialist with over 7 years of hands-on experience architecting distributed defense networks.\n"
        "Expertise across neural architecture engineering, Python pipelines, cloud infrastructure, and security response.\n\n"
        "EXPERIENCE\n"
        "Senior Defense Specialist at Cyberdyne Resistance (2020 - Present)\n"
        "- Engineered neural counter-measures and automated security networks using Python, PyTorch, and Docker containers.\n"
        "- Scaled distributed data ingestion pipelines across multi-node clusters processing high volume telemetry.\n"
        "- Collaborated with cross-functional defense teams to ensure mission reliability and zero-trust verification.",
        fontsize=10
    )
    page1.insert_text((50, 750), "Page 1 of 2", fontsize=10)

    page2 = doc.new_page()
    page2.insert_text((50, 30), "Confidential - Header Text", fontsize=10)
    page2.insert_text(
        (50, 100),
        "EDUCATION\n"
        "Bachelor of Science in Computer Engineering, Tech University, 2019.\n\n"
        "TECHNICAL SKILLS\n"
        "Python, PyTorch, Docker, Kubernetes, Linux, PostgreSQL, Git, CI/CD, Computer Vision, Deep Learning.",
        fontsize=10
    )
    page2.insert_text((50, 750), "Page 2 of 2", fontsize=10)

    pdf_bytes = doc.tobytes()
    doc.close()

    blocks, quality = extract_pdf_blocks(pdf_bytes)
    assert len(blocks) > 0
    assert quality.quality_score >= 0.70

    # Header and footer should be stripped
    all_text = " ".join(b["text"] for b in blocks)
    assert "Page 1 of 2" not in all_text
    assert "Sarah Connor" in all_text
    assert "PyTorch" in all_text

    # Build candidate from synthetic PDF
    cand = build_candidate_from_pdf(pdf_bytes, candidate_id="cand_pdf_01")
    assert cand.name == "Sarah Connor"
    assert cand.email == "sarah@sky.net"
    assert "PyTorch" in cand.extracted_skills
    assert "Python" in cand.extracted_skills
    assert len(cand.evidence_units) >= 1
    assert cand.evidence_units[0].page_number in (1, 2)


# ---------------------------------------------------------------------------
# Job Description Requirements & Intelligence Tests
# ---------------------------------------------------------------------------

def test_extract_years_of_experience():
    assert extract_years_of_experience("5+ years of experience with Python") == 5.0
    assert extract_years_of_experience("Minimum 3 years in distributed systems") == 3.0
    assert extract_years_of_experience("At least 4.5 years of industry experience") == 4.5
    assert extract_years_of_experience("Experience with React") is None


def test_is_education_requirement():
    assert is_education_requirement("Bachelor's degree in Computer Science or related field") is True
    assert is_education_requirement("BS or MS in STEM discipline") is True
    assert is_education_requirement("Proficient in Python and Go") is False


def test_decompound_requirement_phrase():
    comp = "5+ years with Python; 3+ years with Docker and Kubernetes as well as CI/CD"
    decomp = decompound_requirement_phrase(comp)
    assert len(decomp) >= 2


def test_build_job_description_from_text():
    jd_text = """
    Senior Backend Engineer - Platform Team

    ABOUT THE COMPANY
    We are an AI-driven logistics platform.

    RESPONSIBILITIES
    - Design and scale backend microservices.
    - Collaborate closely with frontend teams.

    MINIMUM QUALIFICATIONS
    - Must have 5+ years of experience with Python and FastAPI.
    - Required experience with PostgreSQL and Docker.
    - BS in Computer Science or equivalent.

    PREFERRED QUALIFICATIONS
    - Nice to have experience with Kubernetes and AWS.
    - Familiarity with GraphQL is a plus.
    """
    jd = build_job_description_from_text(jd_text, jd_id="jd_01")
    assert isinstance(jd, JobDescription)
    assert "Backend Engineer" in jd.title
    assert len(jd.requirements) >= 4

    req_map = {r.text: r for r in jd.requirements}
    
    # Check required requirements
    req_py = next((r for r in jd.requirements if "FastAPI" in r.canonical_skills), None)
    assert req_py is not None
    assert req_py.importance == RequirementImportance.REQUIRED
    assert req_py.min_years_experience == 5.0
    assert req_py.weight == 1.0

    # Check preferred requirement
    req_pref = next((r for r in jd.requirements if "Kubernetes" in r.canonical_skills), None)
    assert req_pref is not None
    assert req_pref.importance == RequirementImportance.PREFERRED
    assert req_pref.weight == 0.5


# ---------------------------------------------------------------------------
# Bias Detector Tests
# ---------------------------------------------------------------------------

def test_detect_jd_bias():
    biased_text = """
    We are looking for a rockstar developer who loves to work hard, play hard!
    Only digital native candidates from Ivy League colleges should apply.
    Must have 15+ years of experience with Kubernetes.
    """
    flags = detect_jd_bias(biased_text)
    assert len(flags) >= 4

    bias_types = {f.bias_type for f in flags}
    assert "gender_coded" in bias_types
    assert "ageist" in bias_types
    assert "elitist_credential" in bias_types
    assert "unrealistic_tenure" in bias_types

    # Ensure actionable suggestions are present
    for flag in flags:
        assert len(flag.explanation) > 10
        assert len(flag.alternative_suggestion) > 10


def test_clean_jd_bias_free():
    clean_text = """
    We are seeking a Senior Backend Engineer to join our collaborative team.
    Qualifications:
    - 5+ years of software development experience with Python and PostgreSQL.
    - Strong problem solving and communication skills.
    """
    flags = detect_jd_bias(clean_text)
    assert len(flags) == 0
