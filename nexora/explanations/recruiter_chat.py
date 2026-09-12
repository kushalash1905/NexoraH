"""Local, bounded recruiter Q&A over calculated rankings and evidence."""
import re
from nexora.explanations.candidate_comparison import compare_candidates


def _dict(x):
    return dict(x) if isinstance(x,dict) else x.model_dump()


def _norm(text):
    return re.sub(r'\s+', ' ', str(text).casefold()).strip()


def _references(question, scores):
    """Resolve IDs, full names and rank references; never guess duplicate names."""
    found=[]
    aliases={}
    for s in scores:
        cid=s['candidate_id']
        for alias in [cid,s.get('name','')]:
            if alias:aliases.setdefault(_norm(alias),set()).add(cid)
    # Longest names first prevents a short name inside a longer name matching twice.
    q=_norm(question);spans=[]
    for alias,cids in sorted(aliases.items(),key=lambda x:-len(x[0])):
        for m in re.finditer(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',q):
            if any(m.start()<end and m.end()>start for start,end in spans):continue
            if len(cids)>1:return [],f'The name "{alias}" is shared by multiple candidates. Use a candidate ID or rank, such as #1.'
            spans.append((m.start(),m.end()));found.append((m.start(),next(iter(cids))))
    for m in re.finditer(r'#\s*(\d+)\b|\brank\s*(\d+)\b',q):
        rank=int(m.group(1) or m.group(2))
        selected=[s['candidate_id'] for s in scores if s.get('rank')==rank]
        if len(selected)!=1:return [],f'No unique candidate at rank {rank}. Check the candidate list.'
        found.append((m.start(),selected[0]))
    ids=[]
    for _,cid in sorted(found):
        if cid not in ids:ids.append(cid)
    return ids,None


def answer_recruiter_question(question,jd,candidates,ranking):
    """Return readable text. No LLM, network access, or invented candidate data."""
    scores=[_dict(s) for s in _dict(ranking).get('ranked_candidates',[])]
    if not scores:return 'Run the ranking first, then ask about candidates.'
    ids,error=_references(question,scores)
    if error:return error
    q=_norm(question)
    by_id={s['candidate_id']:s for s in scores}
    if re.search(r'\b(help|examples|what can you)\b',q):
        return 'Try: "Why is #1 ranked above #2?", "Compare #2 and #3", "What is #1 missing?", or "Show evidence for #1". You can also use full names or candidate IDs.'
    if re.search(r'\b(compare|above|below|higher|lower|better|versus|vs|over|difference)\b',q):
        if len(ids)!=2:return 'Name two candidates using their full names, IDs, or ranks. Example: Why is #1 ranked above #2?'
        try:
            result=compare_candidates(jd,candidates,ranking,ids[0],ids[1])
        except (ValueError,KeyError,TypeError) as exc:
            return f'I cannot compare these results: {exc}'
        text=result['answer']
        rows=sorted(result['requirement_differences'],key=lambda r:-abs(r['difference']))[:2]
        quotes=[]
        for row in rows:
            for side in ['a','b']:
                name=result['candidate_'+side].get('name') or result['candidate_'+side]['candidate_id']
                for e in row[side+'_evidence'][:1]:
                    quotes.append(f"{name} — {row['requirement']}, page {e['page']}: {e['text']}")
        return text+ ('\n\nSupporting excerpts:\n'+'\n'.join(quotes) if quotes else '\n\nNo source excerpts were available for this comparison.')
    if re.search(r'\b(missing|lacks?|gaps?|improve)\b',q):
        if len(ids)!=1:return 'Name one candidate. Example: What is #1 missing?'
        s=by_id[ids[0]];missing=s.get('missing_required',[])
        name=s.get('name') or ids[0]
        if not missing:return f'{name}: no required skills were marked missing by this ranking. This does not guarantee complete qualification.'
        return f"{name}: reliable resume support was not found for {', '.join(missing)}. This does not prove the person lacks those skills. If asking how to improve the resume, add truthful supporting project or experience evidence for these requirements."
    if re.search(r'\b(evidence|excerpts?|proof)\b',q):
        if len(ids)!=1:return 'Name one candidate. Example: Show evidence for #1.'
        cid=ids[0];s=by_id[cid]
        candidate=next((_dict(c) for c in candidates if (_dict(c).get('candidate_id') or _dict(c).get('id'))==cid),{})
        units={e.get('evidence_id') or e.get('unit_id'):e for e in map(_dict,candidate.get('evidence_units',[]))}
        lines=[];seen=set()
        for match in s.get('requirement_matches',[]):
            m=_dict(match)
            for eid in m.get('evidence_ids',[]):
                if eid in seen:continue
                seen.add(eid);e=units.get(eid)
                if e:lines.append(f"Page {e.get('page_number',e.get('page',1))}: {e.get('text','')}")
        return '\n\n'.join(lines[:8]) if lines else 'No supporting source excerpts are available for this candidate.'
    if len(ids)==1 and re.search(r'\b(score|rank|summary)\b',q):
        s=by_id[ids[0]]
        return f"{s.get('name') or ids[0]} is ranked #{s['rank']} with fit score {s['score']:.2f}. This is a fit score, not a hiring-success probability. Ask for a comparison or evidence for details."
    return 'I can explain comparisons, scores, missing requirements, and resume evidence. Try "Why is #1 ranked above #2?" or type "help". Use full names, IDs, or #rank references.'
