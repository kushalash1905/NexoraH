# Remaining bonuses: JD wording and messy-resume handling

Merge these files into your repository; they update the existing parser modules.
Coordinate with the parsing and integration teammates before merging.
No cloud API or additional model is required.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Verification here: 25 parser/bonus tests passed, including generated PDF tests.
Real-model matching and the integrated Streamlit website need checking locally.
The existing bias test was updated to expect review-oriented categories:
vague_role_wording, narrow_eligibility, and narrow_tenure. This avoids unsupported
claims that informal labels prove gender bias or that tenure exceeds a tool's age.

## Integration

The existing parser calls detect_jd_bias and retains its list[JDBiasFlag] interface.
The richer analyzer supplies exact spans and context for the UI.

```python
from nexora.ui.bonus_quality_view import (
    render_jd_wording_review, render_resume_diagnostics,
)

render_jd_wording_review(jd.raw_text)  # use jd['raw_text'] for dictionaries
render_resume_diagnostics(candidates)
```

Call these in the results view, using the uploaded JD and parsed candidates.
Persist results across Streamlit reruns through the app's existing session state.
No app.py was supplied, so the panel is delivered separately for integration.
Warnings are human-review prompts and must not modify candidate scores.
No warnings is not a certification that the JD is fair.

## What changed

- Explicit gender, age, native-language and institution restrictions flagged.
- Role-level experience mismatch flagged when explicitly stated as required.
- Exact phrase positions and suggestions preserved; simple local negations handled.
- More heading aliases and stricter heading detection to preserve project sentences.
- Short unique margin content preserved; repeated margin text handled conservatively.
- Image blocks excluded from text extraction; original block text retained.
- Date separators tightened, Sept and ISO month ranges supported, reversed ranges rejected.
- Present uses the current machine date. Year-only duration assumptions are exposed.
- Skill typo correction requires a strong unambiguous best match.
- Section/date/skill normalization logs visible; raw input text retained.
- Duplicate section-block append fixed.

Limitations: rule-based wording review has incomplete coverage and contextual false
positives; regex PDF parsing does not solve every multi-column layout. Scanned PDFs
are warned about; OCR is not implemented. Year-only ranges still use the existing
Jan/Dec duration convention, now explicitly logged. Do not claim all PDFs supported.

Demo: upload a JD with 'male candidates only', a native-language restriction and an
institution restriction. Then show a resume with 'Technical Proficiency', 'NodeJS',
'Sept 2024 - Oct 2024', and the corresponding diagnostics.
