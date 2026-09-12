# Requirement review and formatting-neutral scoring

Copy into the project, merging folders. confidence.py is replaced; coordinate this
scoring change with the integration teammate. Other files are new.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Four new tests passed here (without real-model inference). Full integration and
live reranking must run on your laptop.

## UI connection

```python
from nexora.ranking.scoring import rank_candidates
from nexora.ui.requirement_review_view import render_requirement_review

review = render_requirement_review(jd, candidates, rank_candidates)
if review is not None:
    st.session_state['reviewed_result'] = review
```

Keep the reviewed result across reruns, but clear it when uploaded JD/resumes change.
The UI returns a revised JD, RankingResult, and removal audit. After submission,
replace the displayed ranking with review['ranking'], use review['jd'] for candidate
comparison, and regenerate explanations with your existing explanation function.
Never pair a revised ranking with the original requirement list or stale explanations.
Store the original JD/ranking separately so the recruiter can restore the baseline.

Ranking matching uses revised['requirements'], not raw_text: the raw JD is preserved
for source evidence. The UI must show that a recruiter reviewed and removed those
requirements. Requirement removal is not automatic and does not prove the old JD
was discriminatory. A fresher may outrank an experienced candidate based on skills;
removing tenure does not guarantee that outcome.

Experience/eligibility review suggestions are heuristic; all extracted requirements
remain selectable. This cannot remove a restriction the upstream parser never
extracted as a scoring requirement. The previous wording detector flags raw-text
phrases separately.

## Scoring change

Extraction quality no longer affects the confidence component used in fit scoring.
Its old contribution becomes a fixed neutral baseline. Evidence strength, required
coverage and signal agreement still affect scores. Original extraction warnings
remain on candidate objects and in the diagnostics panel. Do not describe the
confidence output as measuring PDF readability any longer.

This prevents quality metadata from penalizing otherwise identical evidence. It
cannot guarantee identical scores if a layout or unrecognized typo causes the
parser to extract different content. Do not claim all messy/scanned PDFs supported.

## No API required

The comparison panel calls local compare_candidates, which reads existing scores
and evidence and generates deterministic natural-language sentences. Streamlit
calls these Python functions directly. No hosted LLM, REST endpoint, or inference
API is required. This is a dropdown-based recruiter interaction, not an unrestricted
free-text chatbot. The offline pretrained embedding model is used for ranking only.
