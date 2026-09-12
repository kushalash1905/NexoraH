"""Translate parser schemas to matching inputs without changing parser output."""
import re

def obj(value):
    return dict(value) if isinstance(value, dict) else value.model_dump()

def val(value):
    return getattr(value, 'value', value)

def normalize_ranking_inputs(jd, candidates):
    jd = obj(jd)
    jd['jd_id'] = jd.get('jd_id') or jd.get('id', '')
    requirements = []
    categories = {'technical_skill':'technology', 'experience_level':'experience',
                  'domain_knowledge':'domain', 'soft_skill':'soft_context'}
    for item in jd.get('requirements', []):
        r = obj(item)
        r['requirement_id'] = r.get('requirement_id') or r.get('id', '')
        cat = val(r.get('category', 'technology'))
        r['category'] = categories.get(cat, cat)
        imp = val(r.get('importance', 1.0))
        r['requirement_type'] = val(r.get('requirement_type') or (imp if isinstance(imp,str) else 'required'))
        r['importance'] = float(r.get('weight', 0)) if isinstance(imp,str) else float(imp)
        skills = r.get('canonical_skills', [])
        if not r.get('canonical') and skills:
            for i, skill in enumerate(skills):
                canonical = str(skill).lower()
                if canonical == 'express.js': canonical = 'express'
                requirements.append(dict(r, canonical=canonical, aliases=[],
                    requirement_id=r['requirement_id'] if len(skills)==1 else f"{r['requirement_id']}__{i}",
                    source_requirement_id=r['requirement_id'], importance=r['importance']/len(skills)))
        else:
            r['canonical'] = r.get('canonical') or r.get('text', '').lower()
            requirements.append(r)
    jd['requirements'] = requirements
    result = []
    for item in candidates:
        c = obj(item)
        c['candidate_id'] = c.get('candidate_id') or c.get('id', '')
        c['normalized_skills'] = [str(s).lower() for s in (c.get('normalized_skills') or c.get('extracted_skills', []))]
        q = c.get('extraction_quality', 1.0)
        if hasattr(q, 'model_dump'): q = q.model_dump()
        c['extraction_quality'] = float(q.get('quality_score', 1.0)) if isinstance(q, dict) else float(q)
        units = []
        for item in c.get('evidence_units', []):
            e = obj(item)
            e['evidence_id'] = e.get('evidence_id') or e.get('unit_id', '')
            section = val(e.get('section', 'other'))
            e['section'] = section if section != 'other' else val(e.get('section_type', 'other'))
            e['page'] = e.get('page_number', e.get('page', 1))
            e['normalized_text'] = e.get('normalized_text') or str(e.get('text', '')).lower()
            e['has_action_verb'] = bool(e.get('has_action_verb') or re.search(r'\b(built|developed|implemented|deployed|integrated|designed|created|optimized|automated|tested|containerized)\b', e['normalized_text']))
            e['has_duration'] = bool(e.get('has_duration') or e.get('duration_months') or e.get('date_start'))
            units.append(e)
        c['evidence_units'] = units
        result.append(c)
    return jd, result
