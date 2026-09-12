# 05 PERSON 4 INTEGRATION AND BONUS SPECIFICATION: NEXORA

**Role:** Person 4 (Integration, Application Orchestration, Explanations, Recruiter Intelligence & Bonus Features)  
**Branch:** `feature/integration`  
**Core Goal:** Combine all modules into a robust, single-process, local Streamlit application with zero external API calls.

---

## 1. PERSON 4 RESPONSIBILITIES

### Owns:
- Application Orchestration (`run_analysis()`, `app.py`)
- Deterministic Explanation Engine (`generator.py`, `templates.py`)
- Candidate Comparison Engine (`comparison.py`)
- Recruiter Question Handler (`recruiter_answer()`)
- Missing & Improvement Suggestions (`get_missing_requirements()`, `get_improvement_opportunities()`)
- JD Narrowness / Bias Detector (`bias_detector.py`)
- Messy Resume Normalization Diagnostics Aggregation (`build_normalization_summary()`)
- Final Application Result Assembly (`build_final_result()`)
- Offline Smoke Testing (`scripts/offline_smoke_test.py`)
- Inspection Utility (`scripts/inspect_rankings.py`)
- Integration & Unit Tests (`tests/test_explanations.py`, `tests/test_integration.py`)
- README & Setup Instructions

---

## 2. APPLICATION FLOW & FUNCTION CALLS

```
Streamlit UI (app.py)
        │
        ▼
   run_analysis(jd_path, resume_paths)
        │
        ├──► Person 2: parse_jd()
        ├──► Person 2: parse_resume()
        ├──► Person 1: rank_candidates()
        ├──► Person 4: generate_top_three_explanations()
        ├──► Person 4: detect_bias_flags()
        ├──► Person 4: build_normalization_summary()
        └──► Person 4: build_final_result()
```

---

## 3. KEY INTERFACES & IMPLEMENTATIONS

### 3.1 `run_analysis(jd_path: str, resume_paths: list[str]) -> dict`
Orchestrates loading aliases/ontology, parsing documents, calculating candidate rankings, generating explanations, detecting JD flags, and aggregating messy resume diagnostics.

### 3.2 Explanations (`nexora/explanations/generator.py`)
Deterministic template filling based on top requirement matches, evidence strength, section provenance, and cautious phrasing (e.g., "No reliable evidence was found for X").

### 3.3 Candidate Comparison (`nexora/explanations/comparison.py`)
Computes requirement delta $\Delta_r = W(r) [M(r, A) - M(r, B)]$ and rank/score differences between any Candidate A and Candidate B.

### 3.4 Recruiter Questions (`recruiter_answer()`)
Regex-based intent classifier supporting:
- "Why is Candidate A ranked above Candidate B?"
- "Compare Candidate A and Candidate B."
- "What is Candidate B missing?"
- "What would improve Candidate B?"

### 3.5 JD Narrowness Detector (`nexora/jd_analysis/bias_detector.py`)
Flags excessive years of experience in junior roles, absolute phrasing ("must have", "non-negotiable"), and overly rigid technology stacks.

---

## 4. ACCEPTANCE CRITERIA

1. Fully offline startup and execution with Wi-Fi disabled.
2. Complete single-process Streamlit interface.
3. Deterministic evidence-backed explanations for top 3 candidates.
4. Auditable candidate comparison & recruiter question answers.
5. Zero HTTP calls or external API usage.
