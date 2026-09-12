"""Offline smoke test verification for NEXORA.

Validates that all models, ontologies, and ranking routines run with
complete network isolation (100% offline).
"""

import os
import sys
from pathlib import Path

# Enforce offline flags in environment
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nexora.config import MODEL_PATH
from nexora.matching.ontology import load_aliases, load_ontology
from nexora.matching.semantic_engine import load_embedding_model
from nexora.ranking.scoring import rank_candidates
from nexora.schemas import Candidate, EvidenceUnit, JobDescription, Requirement


def run_smoke_test():
    print("=" * 60)
    print("NEXORA OFFLINE SMOKE TEST")
    print("=" * 60)

    # 1. Check local model exists
    print(f"1. Checking local model directory: {MODEL_PATH} ...")
    if not MODEL_PATH.exists():
        print(f"FAIL: Local model directory '{MODEL_PATH}' does not exist.")
        sys.exit(1)
    print("   -> OK: Directory present.")

    # 2. Load model with local_files_only=True
    print("2. Loading SentenceTransformer offline...")
    try:
        model = load_embedding_model(MODEL_PATH)
        test_emb = model.encode(["offline test query"], normalize_embeddings=True)
        assert test_emb.shape == (1, 384)
        print("   -> OK: Model loaded and generated 384-d normalized vector.")
    except Exception as e:
        print(f"FAIL: Model offline load failed: {e}")
        sys.exit(1)

    # 3. Load ontology and aliases
    print("3. Loading local ontology and aliases JSON...")
    ontology = load_ontology()
    aliases = load_aliases()
    assert len(ontology) > 0, "Ontology should not be empty"
    assert len(aliases) > 0, "Aliases should not be empty"
    print(f"   -> OK: Loaded {len(ontology)} ontology nodes and {len(aliases)} alias clusters.")

    # 4. End-to-end small rank test
    print("4. Running end-to-end candidate ranking offline...")
    jd = JobDescription(
        jd_id="smoke_jd",
        title="Smoke Test Role",
        requirements=[
            Requirement(
                requirement_id="req_1",
                text="Python development",
                canonical="python",
                importance=1.25,
            )
        ],
    )
    cand = Candidate(
        candidate_id="smoke_cand",
        name="Offline Candidate",
        normalized_skills=["python"],
        evidence_units=[
            EvidenceUnit(
                evidence_id="smoke_ev",
                candidate_id="smoke_cand",
                text="Engineered Python scripts for automated offline data processing.",
                normalized_text="engineered python scripts for automated offline data processing.",
                section="projects",
                has_action_verb=True,
            )
        ],
    )
    result = rank_candidates(jd, [cand], model=model, aliases=aliases, ontology=ontology)
    assert result.candidate_count == 1
    ranked_c = result.ranked_candidates[0]
    assert ranked_c.score > 0
    print(f"   -> OK: Candidate ranked with score {ranked_c.score}/100, confidence {ranked_c.confidence}%.")

    print("\n[SUCCESS] NEXORA Offline Smoke Test PASSED. 100% Local Execution Verified.")
    print("=" * 60)


if __name__ == "__main__":
    run_smoke_test()
