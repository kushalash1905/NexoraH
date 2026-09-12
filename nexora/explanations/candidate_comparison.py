"""Offline comparison grounded in existing ranking scores and evidence."""
from nexora.config import (
    FINAL_COVERAGE_WEIGHT, FINAL_EXPERIENCE_WEIGHT, FINAL_CONFIDENCE_WEIGHT,
    MISSING_REQUIRED_PENALTY_COEFF, STATUS_WEAK_THRESHOLD,
    WEIGHT_REQUIRED_TECH, WEIGHT_REQUIRED_STANDARD, WEIGHT_PREFERRED, WEIGHT_CONTEXTUAL,
)


def _dict(value):
    return dict(value) if isinstance(value, dict) else value.model_dump()


def _value(value):
    return getattr(value, 'value', value)


def _requirements(jd):
    """Mirror the ranking adapter's requirement IDs and weights."""
    result = []
    for item in _dict(jd).get('requirements', []):
        r = _dict(item)
        rid = r.get('requirement_id') or r.get('id')
        imp = _value(r.get('importance', 1.0))
        kind = _value(r.get('requirement_type') or (imp if isinstance(imp, str) else 'required'))
        weight = float(r.get('weight', 0)) if isinstance(imp, str) else float(imp)
        category = _value(r.get('category', 'technology'))
        if weight <= 0:
            weight = (WEIGHT_REQUIRED_TECH if category in ('technology', 'technical_skill') else WEIGHT_REQUIRED_STANDARD) if kind == 'required' else WEIGHT_PREFERRED if kind == 'preferred' else WEIGHT_CONTEXTUAL
        skills = r.get('canonical_skills', [])
        if not r.get('canonical') and skills:
            for i, skill in enumerate(skills):
                result.append(dict(requirement_id=rid if len(skills)==1 else f'{rid}__{i}',
                    label=skill, requirement_type=kind, weight=weight/len(skills)))
        else:
            result.append(dict(requirement_id=rid, label=r.get('canonical') or r.get('text', rid),
                               requirement_type=kind, weight=weight))
    if not result or any(not r['requirement_id'] for r in result):
        raise ValueError('Comparison needs the JD requirements used for ranking.')
    if len({r['requirement_id'] for r in result}) != len(result):
        raise ValueError('Duplicate requirement IDs in comparison inputs.')
    return result


def compare_candidates(jd, candidates, ranking, candidate_a_id, candidate_b_id):
    """Accept parser/engine models or dictionaries; never recompute embeddings.

    Differences are in final-score points. Evidence is resolved only from the
    corresponding candidate. Missing excerpts are reported, never fabricated.
    """
    if candidate_a_id == candidate_b_id:
        raise ValueError('Choose two different candidates.')
    scores = {_dict(c)['candidate_id']: _dict(c) for c in _dict(ranking)['ranked_candidates']}
    if candidate_a_id not in scores or candidate_b_id not in scores:
        raise ValueError('Selected candidate is absent from the ranking.')
    a, b = scores[candidate_a_id], scores[candidate_b_id]
    requirements = _requirements(jd)
    total_weight = sum(r['weight'] for r in requirements)
    expected = {r['requirement_id'] for r in requirements}
    evidence = {}
    for candidate in candidates:
        c = _dict(candidate)
        cid = c.get('candidate_id') or c.get('id')
        units = [_dict(e) for e in c.get('evidence_units', [])]
        evidence[cid] = {e.get('evidence_id') or e.get('unit_id'): e for e in units}
    def matches(score):
        items = [_dict(m) for m in score.get('requirement_matches', [])]
        mapped = {m['requirement_id']: m for m in items}
        if set(mapped) != expected or len(mapped) != len(items):
            raise ValueError('Ranking and JD requirement IDs differ. Pass the JD used for this ranking.')
        return mapped
    am, bm = matches(a), matches(b)
    def excerpts(cid, match):
        result = []
        for eid in match.get('evidence_ids', []):
            e = evidence.get(cid, {}).get(eid)
            if e:
                result.append(dict(evidence_id=eid, text=e.get('text', ''),
                    section=_value(e.get('section_type', e.get('section', 'other'))),
                    page=e.get('page_number', e.get('page', 1))))
        return result
    rows = []
    for r in requirements:
        left, right = am[r['requirement_id']], bm[r['requirement_id']]
        lscore, rscore = left['final_requirement_score'], right['final_requirement_score']
        factor = 100 * FINAL_COVERAGE_WEIGHT * r['weight'] / total_weight
        rows.append(dict(requirement_id=r['requirement_id'], requirement=r['label'],
            requirement_type=r['requirement_type'], a_match_score=lscore, b_match_score=rscore,
            a_status=left['status'], b_status=right['status'],
            a_contribution=factor*lscore, b_contribution=factor*rscore,
            difference=factor*(lscore-rscore),
            a_evidence=excerpts(candidate_a_id,left), b_evidence=excerpts(candidate_b_id,right)))
    def penalty(mapped):
        return 100*MISSING_REQUIRED_PENALTY_COEFF*sum(r['weight'] for r in requirements
            if r['requirement_type']=='required' and mapped[r['requirement_id']]['final_requirement_score'] < STATUS_WEAK_THRESHOLD)/total_weight
    components = [
        dict(component='Requirement coverage', difference=sum(r['difference'] for r in rows)),
        dict(component='Demonstrated relevant experience', difference=100*FINAL_EXPERIENCE_WEIGHT*(a['experience_relevance']-b['experience_relevance'])),
        dict(component='Heuristic evidence confidence', difference=FINAL_CONFIDENCE_WEIGHT*(a['confidence']-b['confidence'])),
        dict(component='Missing-required penalty', difference=penalty(bm)-penalty(am)),
    ]
    gap = a['score']-b['score']
    residual = gap-sum(c['difference'] for c in components)
    components.append(dict(component='Clipping and rounding adjustment', difference=residual))
    aname, bname = a.get('name') or candidate_a_id, b.get('name') or candidate_b_id
    if abs(gap)<.005:
        opening=f'{aname} and {bname} have equal displayed fit scores ({a["score"]:.2f}). Their order may follow required coverage, evidence strength, or the input order for an exact tie.'
    else:
        higher, lower = (aname,bname) if gap>0 else (bname,aname)
        opening=f'{higher} has a {abs(gap):.2f}-point higher fit score than {lower}.'
    positive=sorted([r for r in rows if r['difference']>.005],key=lambda r:-r['difference'])[:3]
    negative=sorted([r for r in rows if r['difference']<-.005],key=lambda r:r['difference'])[:3]
    sentences=[opening]
    for name, selected, sign in [(aname,positive,1),(bname,negative,-1)]:
        if selected:
            detail=', '.join(f'{r["requirement"]} ({sign*r["difference"]:.2f} points)' for r in selected)
            sentences.append(f'{name} gains more requirement-coverage credit for {detail}.')
    for c in components[1:4]:
        if abs(c['difference'])>=.05:
            name=aname if c['difference']>0 else bname
            sentences.append(f'{c["component"]} favors {name} by {abs(c["difference"]):.2f} points.')
    sentences.append('Skills marked missing mean reliable support was not found in the supplied resume; they are not proof of inability.')
    return dict(candidate_a=a,candidate_b=b,score_difference=gap,answer=' '.join(sentences),
        requirement_differences=rows,component_differences=components,
        a_missing_required=a.get('missing_required',[]),b_missing_required=b.get('missing_required',[]))
