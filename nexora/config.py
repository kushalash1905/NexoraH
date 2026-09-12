"""
Configuration settings and constants for Nexora.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = MODELS_DIR / "all-MiniLM-L6-v2"

# Offline flags
OS_ENV_HF_OFFLINE = "1"
OS_ENV_TRANSFORMERS_OFFLINE = "1"

# Weighting constants
WEIGHT_REQUIRED_TECH = 1.25
WEIGHT_REQUIRED_STANDARD = 1.00
WEIGHT_PREFERRED = 0.45
WEIGHT_CONTEXTUAL = 0.30

# Hybrid scoring weights
WEIGHT_KEYWORD_FORMULA = 0.40
WEIGHT_SEMANTIC_FORMULA = 0.40
WEIGHT_ONTOLOGY_FORMULA = 0.20

# Final candidate score weights
WEIGHT_COVERAGE = 0.78
WEIGHT_EXPERIENCE_RELEVANCE = 0.10
WEIGHT_CONFIDENCE = 0.07
MISSING_REQUIRED_PENALTY_FACTOR = 0.12

# Evidence source priority
EVIDENCE_SOURCE_PRIORITY = {
    "experience": 0.80,
    "internship": 0.75,
    "projects": 0.65,
    "certifications": 0.45,
    "education": 0.40,
    "summary": 0.35,
    "skills": 0.25,
    "other": 0.20
}

# Confidence thresholds
CONFIDENCE_LABEL_HIGH = 0.75
CONFIDENCE_LABEL_MEDIUM = 0.50
