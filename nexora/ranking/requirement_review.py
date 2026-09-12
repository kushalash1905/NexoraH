"""Explicit recruiter review of potentially unnecessary JD constraints."""
from copy import deepcopy
import re


def _dict(x):
    return dict(x) if isinstance(x,dict) else x.model_dump()


def suggest_requirement_reviews(jd):
    suggestions=[]
    for item in _dict(jd).get('requirements',[]):
        r=_dict(item);rid=r.get('requirement_id') or r.get('id')
        text=r.get('source_text') or r.get('text','')
        category=getattr(r.get('category',''),'value',r.get('category',''))
        reason=None
        if category in ('experience','experience_level') or re.search(r'\b(?:years?\s+(?:of\s+)?experience|experienced|prior experience)\b',text,re.I):
            reason='Experience may reflect necessary duties or act as a proxy for skills. Review whether demonstrated competencies can substitute.'
        elif re.search(r'\b(?:male|female|native speaker|native english|IIT|IIM|ivy league|age limit)\b',text,re.I):
            reason='Potentially narrow eligibility restriction; review its relevance to the duties.'
        if reason:suggestions.append(dict(requirement_id=rid,text=text,reason=reason))
    return suggestions


def revise_requirements(jd, remove_ids):
    """Return an independent revised JD and audit log. No silent changes."""
    revised=deepcopy(_dict(jd));requirements=[_dict(r) for r in revised.get('requirements',[])]
    selected=set(remove_ids)
    known={r.get('requirement_id') or r.get('id') for r in requirements}
    if selected-known:raise ValueError('Unknown requirement selected for removal.')
    kept=[r for r in requirements if (r.get('requirement_id') or r.get('id')) not in selected]
    if not kept:raise ValueError('Keep at least one requirement for meaningful ranking.')
    removed=[r for r in requirements if (r.get('requirement_id') or r.get('id')) in selected]
    revised['requirements']=kept
    return revised, dict(removed_requirements=removed,original_count=len(requirements),revised_count=len(kept))
