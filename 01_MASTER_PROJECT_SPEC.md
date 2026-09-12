# 01 MASTER PROJECT SPECIFICATION: NEXORA

**Project Name:** NEXORA  
**One-Line Description:** Nexora is a fully local, evidence-based candidate intelligence system that ranks 15–18 resumes against one Job Description using requirement-level keyword matching, semantic matching, and auditable evidence.  
**Target User:** Campus recruiters and hiring managers reviewing applicants for a single role.  
**Key Differentiator:** Nexora does not score a resume as one opaque document. It scores every candidate against every JD requirement and preserves the evidence that produced the score.

---

## 1. PROJECT CONSTRAINTS & NON-GOALS

### 1.1 Strict Constraints
The system MUST run fully locally without any cloud or internet dependencies.

**DO NOT USE:**
- OpenAI API
- Gemini API
- Claude API
- Groq / OpenRouter / Hugging Face hosted inference
- Cloud embedding APIs or cloud backends
- Paid or external APIs
- Internet-dependent services

**ALLOWED / APPROVED TECHNOLOGIES:**
- Python 3.10 / 3.11
- Streamlit (Single-Process Local Web App)
- PyMuPDF (PDF text extraction)
- sentence-transformers (`sentence-transformers/all-MiniLM-L6-v2`)
- rank_bm25 (BM25 retrieval)
- RapidFuzz (fuzzy matching)
- scikit-learn, PyTorch, NumPy
- Pydantic
- Local JSON data (ontology & aliases)

### 1.2 Non-Goals
Nexora does NOT:
- Call external APIs or cloud LLMs.
- Infer candidate personality or predict employee performance.
- Make legal or discrimination claims regarding JD wording.
- Hardcode candidate-specific score boosts.
- Require internet connectivity during runtime.

---

## 2. SYSTEM ARCHITECTURE & DATA FLOW

### 2.1 Single-Process Architecture

```
                         ┌──────────────────────┐
                         │        JD PDF        │
                         └───────────┬──────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ Local PDF Extraction │
                         │ PyMuPDF              │
                         └───────────┬──────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ JD Intelligence      │
                         │ Requirement extraction│
                         │ Required/preferred   │
                         │ Bias/narrowness flags│
                         └───────────┬──────────┘
                                     │
                                     │
┌──────────────────────┐             │             ┌──────────────────────┐
│     Resume PDFs      │             │             │ Local Skill Ontology │
└───────────┬──────────┘             │             │ Aliases & Relations  │
            │                        │             └───────────┬──────────┘
┌───────────▼──────────┐             │                         │
│ Resume Intelligence  │             │                         │
│ PDF Parsing          │             │                         │
│ Section Normalization│             │                         │
│ Evidence Construction│             │                         │
└───────────┬──────────┘             │                         │
            └────────────────────────┴─────────────────────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ Requirement Matching │
                         ├──────────────────────┤
                         │ Exact/Alias Matching │
                         │ BM25 Keyword Search  │
                         │ Semantic Embeddings  │
                         │ Ontology Support     │
                         │ Evidence Quality     │
                         │ Context Verification │
                         └───────────┬──────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ Hybrid Scoring       │
                         │ Required/Preferred   │
                         │ Missing Penalties    │
                         │ Anti-Keyword Stuffing│
                         │ Confidence Score     │
                         └───────────┬──────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ Candidate Ranking    │
                         │ Sensitivity Analysis │
                         └───────┬───────┬──────┘
                                 │       │
                  ┌──────────────▼─┐   ┌─▼─────────────────┐
                  │ Candidate Views│   │ Recruiter Tools   │
                  │ Ranking/Details│   │ Compare/Why/Miss  │
                  └────────────────┘   └───────────────────┘
```

---

## 3. AUTHORITATIVE DATA SCHEMAS

### 3.1 Requirement Schema
```json
{
  "requirement_id": "req_node",
  "text": "Node.js backend development",
  "canonical": "node.js",
  "category": "technology",
  "requirement_type": "required",
  "importance": 1.25,
  "aliases": ["node", "nodejs", "node.js"],
  "related_skills": [
    { "canonical": "express", "support": 0.75 },
    { "canonical": "rest api", "support": 0.55 }
  ],
  "source_text": "Experience with Node.js backend development"
}
```

### 3.2 Evidence Unit Schema
```json
{
  "evidence_id": "ev_007_014",
  "candidate_id": "candidate_007",
  "text": "Built REST APIs using Express and MongoDB.",
  "normalized_text": "built rest apis using express and mongodb",
  "section": "projects",
  "source_type": "project",
  "page": 1,
  "position": 14,
  "has_action_verb": true,
  "has_outcome": false,
  "has_duration": false,
  "repetition_count": 1,
  "base_strength": 0.65
}
```

### 3.3 Requirement Match Schema
```json
{
  "candidate_id": "candidate_007",
  "requirement_id": "req_node",
  "keyword_score": 0.35,
  "semantic_score": 0.78,
  "ontology_support": 0.75,
  "evidence_strength": 0.82,
  "context_guard": 1.0,
  "final_requirement_score": 0.379,
  "status": "partial_match",
  "confidence": 0.87,
  "evidence_ids": ["ev_007_014"]
}
```

### 3.4 Candidate Score Schema
```json
{
  "candidate_id": "candidate_007",
  "name": "Candidate 7",
  "rank": 1,
  "score": 82.4,
  "confidence": 86.0,
  "confidence_label": "High",
  "required_coverage": 0.91,
  "preferred_coverage": 0.62,
  "keyword_alignment": 0.71,
  "semantic_alignment": 0.79,
  "evidence_strength": 0.84,
  "experience_relevance": 0.84,
  "missing_required": ["typescript"],
  "matched_requirements": ["react", "node.js", "mongodb"],
  "requirement_matches": []
}
```

---

## 4. HYBRID MATCHING & RANKING FORMULA

For every requirement $r$ and candidate $c$:

$$M(r,c) = E(r,c) \times \left[ 0.40 \cdot K(r,c) + 0.40 \cdot S(r,c) + 0.20 \cdot O(r,c) \right]$$

Where:
- $K(r,c)$: Keyword score (Exact + Alias + Fuzzy + BM25)
- $S(r,c)$: Semantic similarity using `all-MiniLM-L6-v2`
- $O(r,c)$: Local ontology support score
- $E(r,c)$: Evidence quality multiplier

---

## 5. RECRUITER INTELLIGENCE & EXPLANATIONS

1. **Deterministic Explanations:** Templates format top-three candidate summaries without using an LLM.
2. **Candidate Comparison:** Calculates requirement delta $\Delta_r = W(r) [M(r, A) - M(r, B)]$ to explain why Candidate A ranks above Candidate B.
3. **What is Missing / What Would Improve:** Lists weak and missing JD requirements prioritized by requirement importance.
4. **JD Narrow-Language Detector:** Flags restrictive wording (e.g. 2+ years experience for internships, absolute phrases like "must have").

---

## 6. WORKSPACE FOLDER STRUCTURE

```
nexora/
├── app.py
├── requirements.txt
├── README.md
├── 01_MASTER_PROJECT_SPEC.md
├── 05_PERSON_4_INTEGRATION_BONUS.md
├── models/
│   └── all-MiniLM-L6-v2/
├── data/
│   ├── ontology.json
│   └── aliases.json
├── nexora/
│   ├── schemas.py
│   ├── config.py
│   ├── parsers/
│   ├── jd_analysis/
│   │   └── bias_detector.py
│   ├── matching/
│   ├── ranking/
│   ├── explanations/
│   │   ├── templates.py
│   │   ├── generator.py
│   │   └── comparison.py
│   └── ui/
├── scripts/
│   ├── offline_smoke_test.py
│   └── inspect_rankings.py
└── tests/
    ├── test_explanations.py
    └── test_integration.py
```
