"""Local JD wording review: warnings for human review, never ranking penalties."""
import re
from nexora.schemas import JDBiasFlag

RULES = [
    (r'\bwork\s+hard\s*,?\s*play\s+hard\b', 'vague_culture_wording', 'This slogan leaves work expectations unclear; review whether it implies unnecessary availability restrictions.', 'Describe working hours, collaboration and concrete performance expectations.'),
    (r'\bivy\s+league\s+(?:colleges?|universities)\b', 'elitist_credential', 'An institution-based preference may exclude applicants with equivalent demonstrated skills.', 'Describe the necessary competencies and accept equivalent qualifications.'),
    (r'\b(?:1[0-9]|[2-9][0-9])\+?\s*years?\s+(?:of\s+)?experience\s+(?:with|in)\s+\w+\b', 'narrow_tenure', 'A high tool-specific tenure minimum can be unnecessarily narrow; review whether demonstrated competence is sufficient.', 'Justify the tenure minimum or describe the required depth of practical experience.'),
    (r'\b(?:male|female|men|women)\s+(?:candidates?\s+|applicants?\s+)?only\b|\bonly\s+(?:male|female|men|women)\s+(?:candidates?|applicants?)\b', 'gender_restriction', 'Restricts applicants by gender rather than demonstrated job skills.', 'Describe the duties and qualifications; review whether the restriction is necessary.'),
    (r'\b(?:under|below)\s+\d{2}\s*(?:years?(?:\s+old)?|of\s+age)\b|\bage\s*(?:limit|below|under|:)\s*\d{2}\b|\byoung\s+(?:candidates?\s+only|and\s+energetic)\b', 'ageist', 'May exclude qualified applicants based on age.', 'Specify the actual duties, availability, and skills required.'),
    (r'\bnative\s+(?:english|hindi|french|german|spanish)\s+speakers?\s+(?:only|required)\b', 'language_restriction', 'Native-speaker status can be narrower than the language proficiency needed.', 'Specify the required spoken and written language proficiency.'),
    (r'\b(?:IIT|IIM|NIT|ivy\s+league)(?:s|\s+graduates?)?\s+only\b|\bonly\s+(?:IIT|IIM|NIT)(?:s|\s+graduates?)?\b|\b(?:top[-\s]tier\s+(?:universit(?:y|ies)|colleges?)|premier\s+institutes?)\b', 'elitist_credential', 'Institution-based screening may exclude applicants with equivalent demonstrated skills.', 'Accept equivalent qualifications or assess relevant projects and competencies.'),
    (r'\b(?:recent\s+grad(?:uate)?s?\s+only|digital\s+native)\b', 'narrow_eligibility', 'May unnecessarily restrict career changers or applicants from different backgrounds.', 'State entry-level scope and necessary eligibility explicitly.'),
    (r'\b(?:rockstar|ninja|guru)\b', 'vague_role_wording', 'Informal labels do not explain the competencies required; review for clarity.', 'Use a concrete role title and describe the expected skills.'),
]


def analyze_jd_wording(jd_text):
    """Return exact source spans, explanations and suggestions in source order."""
    flags=[]
    for pattern,kind,reason,suggestion in RULES:
        for match in re.finditer(pattern,jd_text,re.I):
            # Suppress common explicit negations in the same local phrase.
            prefix=jd_text[max(0,match.start()-40):match.start()]
            if re.search(r'\b(?:not|never|no|do\s+not)\s+(?:require\s+|restricted\s+to\s+)?$',prefix,re.I):continue
            flags.append(dict(phrase=match.group(),bias_type=kind,explanation=reason,
                alternative_suggestion=suggestion,start=match.start(),end=match.end(),
                context=jd_text[max(0,match.start()-60):min(len(jd_text),match.end()+60)],
                review_required=True))
    # Contextual role-level mismatch, not a claim about technology release dates.
    if re.search(r'\b(?:intern(?:ship)?|junior|entry[-\s]level)\b',jd_text,re.I):
        for match in re.finditer(r'\b([5-9]|\d{2})\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience\s+(?:required|mandatory|minimum)\b',jd_text,re.I):
            flags.append(dict(phrase=match.group(),bias_type='role_level_mismatch',
                explanation='This experience minimum may be inconsistent with the entry-level role; review the context.',
                alternative_suggestion='Align the minimum experience with the actual role responsibilities.',
                start=match.start(),end=match.end(),context=jd_text[max(0,match.start()-60):match.end()+60],review_required=True))
    return sorted(flags,key=lambda f:f['start'])


def detect_jd_bias(jd_text):
    """Preserve the parser's existing list[JDBiasFlag] interface."""
    return [JDBiasFlag(**{k:f[k] for k in ['phrase','bias_type','explanation','alternative_suggestion']})
            for f in analyze_jd_wording(jd_text)]
