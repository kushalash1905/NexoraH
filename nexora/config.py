"""Configuration constants and mathematical weights for NEXORA."""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "all-MiniLM-L6-v2"
DEFAULT_ONTOLOGY_PATH = DATA_DIR / "ontology.json"
DEFAULT_ALIASES_PATH = DATA_DIR / "aliases.json"

# Section Base Evidence Strengths
SECTION_BASE_STRENGTHS = {
    "skills": 0.25,
    "summary": 0.35,
    "education": 0.40,
    "certifications": 0.45,
    "certification": 0.45,
    "projects": 0.65,
    "project": 0.65,
    "experience": 0.80,
    "work experience": 0.80,
    "internship": 0.80,
    "internships": 0.80,
    "employment": 0.80,
    "other": 0.30,
}
DEFAULT_BASE_STRENGTH = 0.50

# Evidence Bonus Signals
EVIDENCE_VERB_BONUS = 0.10
EVIDENCE_OUTCOME_BONUS = 0.08
EVIDENCE_DURATION_BONUS = 0.05
EVIDENCE_REPEAT_BONUS = 0.05

# Keyword Formula Coefficients: K = 0.50*exact + 0.25*alias + 0.15*fuzzy + 0.10*bm25
KEYWORD_EXACT_WEIGHT = 0.50
KEYWORD_ALIAS_WEIGHT = 0.25
KEYWORD_FUZZY_WEIGHT = 0.15
KEYWORD_BM25_WEIGHT = 0.10

# Fuzzy Matching Thresholds
FUZZY_RATIO_THRESHOLD = 80.0
FUZZY_TECH_CAP = 0.45

# Semantic Matching Bands
SEMANTIC_FLOOR = 0.35
SEMANTIC_MODERATE = 0.55
SEMANTIC_STRONG = 0.70
TECH_CONTEXT_GUARD_PENALTY = 0.25

# Requirement Match Formula Coefficients: M = E * (0.40*K + 0.40*S + 0.20*O) * guard
MATCH_KEYWORD_WEIGHT = 0.40
MATCH_SEMANTIC_WEIGHT = 0.40
MATCH_ONTOLOGY_WEIGHT = 0.20

# Requirement Match Status Thresholds
STATUS_STRONG_THRESHOLD = 0.70
STATUS_PARTIAL_THRESHOLD = 0.45
STATUS_WEAK_THRESHOLD = 0.30

# Requirement Importance Weights
WEIGHT_REQUIRED_TECH = 1.25
WEIGHT_REQUIRED_STANDARD = 1.00
WEIGHT_PREFERRED = 0.45
WEIGHT_CONTEXTUAL = 0.30

# Missing Penalty Coefficient
MISSING_REQUIRED_PENALTY_COEFF = 0.12

# Final Candidate Score Weights: Score = 100 * clip(0.78*cov + 0.10*X + 0.07*C - P_missing, 0, 1)
FINAL_COVERAGE_WEIGHT = 0.78
FINAL_EXPERIENCE_WEIGHT = 0.10
FINAL_CONFIDENCE_WEIGHT = 0.07

# Confidence Formula Weights: C = 0.45*ev_strength + 0.30*req_cov + 0.15*ext_qual + 0.10*signal_agree
CONFIDENCE_EVIDENCE_WEIGHT = 0.45
CONFIDENCE_REQUIRED_COVERAGE_WEIGHT = 0.30
CONFIDENCE_EXTRACTION_QUALITY_WEIGHT = 0.15
CONFIDENCE_SIGNAL_AGREEMENT_WEIGHT = 0.10

# Confidence Categorical Labels
CONFIDENCE_HIGH_THRESHOLD = 0.75
CONFIDENCE_MEDIUM_THRESHOLD = 0.50

# Anti-Keyword-Stuffing Thresholds
LEXICAL_ONLY_KEYWORD_THRESHOLD = 0.70
LEXICAL_ONLY_DEMONSTRATED_THRESHOLD = 0.30
