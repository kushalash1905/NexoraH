# Candidate comparison bonus

Adds local deterministic comparison without re-running matching or using an API.

Copy nexora/ and tests/ into the repository root, merging directories.
No existing matching, ranking, parser, or UI files are replaced.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_candidate_comparison_bonus.py -v
```

Integration teammate: after ranking, pass the same structured JD and parsed
candidates used for ranking, plus the RankingResult, to:

```python
from nexora.ui.candidate_comparison_view import render_candidate_comparison

render_candidate_comparison(jd, candidates, ranking_result)
```

Use your existing variables; the ZIP has no app.py because none was supplied.
Keep this call inside the results view. Store the JD, candidates and ranking
in Streamlit session_state so widget interactions do not lose the results.
The panel does not upload PDFs or call the engine itself.

Direct function:

```python
from nexora.explanations.candidate_comparison import compare_candidates
comparison = compare_candidates(jd, candidates, ranking_result, 'candidate_a_id', 'candidate_b_id')
print(comparison['answer'])
```

Supports dictionaries and Pydantic inputs, including the supplied parser's
JDRequirement IDs and multi-skill expansion. Requirement-ID mismatch raises a
clear error instead of guessing. Each excerpt is looked up only in the selected
candidate's evidence. Displayed match status is not a claim of exact keyword
presence. Heuristic confidence is not a success probability.

Requirement differences are weighted contributions in final-score points.
The breakdown also includes relevant experience, confidence, missing-required
penalties and a reconciliation adjustment for clipping/rounding. These formulas
mirror the uploaded engine and must change together if that engine changes.

Verification here: six pure comparison tests passed; syntax checks passed.
The Streamlit panel needs testing inside your integrated website.
