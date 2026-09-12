import fitz
from nexora.jd_analysis.bias_detector import analyze_jd_wording
from nexora.parsers.section_normalizer import classify_section_header,is_likely_section_header
from nexora.parsers.date_normalizer import extract_date_range
from nexora.parsers.pdf_parser import extract_pdf_blocks
from nexora.parsers.evidence_builder import build_candidate_from_text,extract_and_normalize_skills
from nexora.schemas import SectionType


def test_explicit_restrictions_and_exact_spans():
    text='Male candidates only. Native English speakers only. IIT graduates only.'
    flags=analyze_jd_wording(text)
    assert len(flags)==3
    assert all(text[f['start']:f['end']]==f['phrase'] for f in flags)


def test_neutral_and_negated_text_not_flagged():
    assert analyze_jd_wording('English proficiency required. Applicants of all genders welcome.')==[]
    assert analyze_jd_wording('We do not require native English speakers only.')==[]


def test_role_level_warning():
    assert any(f['bias_type']=='role_level_mismatch' for f in analyze_jd_wording('Junior intern: 5 years of experience required.'))


def test_headers_and_sentences():
    assert classify_section_header('Technical Proficiency')[0]==SectionType.SKILLS
    assert classify_section_header('Tech Stack')[0]==SectionType.SKILLS
    assert not is_likely_section_header('Built projects using React')


def test_reversed_date_rejected_and_iso_supported():
    assert extract_date_range('Mar 2024 - Jan 2024') is None
    assert extract_date_range('2024-01 to 2024-03')['duration_months']==2
    assert extract_date_range('Sept 2024 - Oct 2024')['start_iso']=='2024-09'
    assert extract_date_range('2022 - 2024')['warnings']


def test_unique_short_top_margin_content_preserved():
    doc=fitz.open()
    for text in ['Aarushi','Docker']:
        page=doc.new_page();page.insert_text((50,40),text)
    raw=doc.tobytes();doc.close()
    blocks,_=extract_pdf_blocks(raw)
    assert {b['text'] for b in blocks}=={'Aarushi','Docker'}
    assert all('raw_text' in b for b in blocks)


def test_normalization_logs_and_original_text():
    text='Aarushi\nTechnical Proficiency:\nNodeJS, ReactJS\nWork Experience\nBuilt services Jan 2024 - Mar 2024'
    c=build_candidate_from_text(text,'c')
    assert c.raw_text==text
    assert any(l['match_type']=='section_header' for l in c.normalization_log)
    assert any(l['match_type']=='date_range' for l in c.normalization_log)


def test_ambiguous_fuzzy_skill_not_corrected():
    skills,logs=extract_and_normalize_skills('abcdefghij',{'abcdefghik':'Tool A','abcdefghil':'Tool B'})
    assert skills==[]
