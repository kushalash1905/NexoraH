# Typed recruiter chat

Copy nexora/ and tests/ into the repository, merging folders.
Requires the previously delivered nexora/explanations/candidate_comparison.py.
No external API, model download, or hosted chatbot service is used.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_recruiter_chat_bonus.py -v
```

Integration teammate: inside the results view, use the existing variables:

```python
from nexora.ui.recruiter_chat_view import render_recruiter_chat
render_recruiter_chat(jd, candidates, ranking_result)
```

Persist all three inputs in the app's Streamlit session state across reruns.
After reviewed requirement removal, pass the revised JD and revised ranking,
not the original JD. Keep parsed candidates for source evidence lookup.
The chat keeps its history and resets it when these inputs change.

Supported typed questions:
- Why is Aarushi ranked above Sam?
- Compare #1 and #2
- What is #2 missing?
- Show evidence for #1
- What is #2's score?
- Help

Use actual full candidate names, IDs, or #rank references. Candidate A/B are not
invented labels unless those are their real names. Ambiguous names need IDs/ranks.

This is a rule-based, task-specific local chatbot. It handles these question
families, not arbitrary conversation or follow-up pronouns. It never invents
an answer to an unsupported question. Sentences are constructed from existing
ranking calculations and candidate-owned source excerpts.

Eight pure chat tests passed here. Verify the chat input and history in the
integrated website; the app.py entry point was not supplied.
