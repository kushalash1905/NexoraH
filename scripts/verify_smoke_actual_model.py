"""Smoke test using the actual locally saved embedding model (no mocks).

Evaluates two structured candidate profiles against three requirements,
logging exact scores, keyword/semantic scores, and supporting evidence IDs.
"""

import os
import sys
from pathlib import Path

# Enforce strict offline execution
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from nexora.config import MODEL_PATH
from nexora.matching.ontology import load_aliases, load_ontology
from nexora.matching.semantic_engine import load_embedding_model
from nexora.ranking.scoring import rank_candidates
from nexora.schemas import Candidate, EvidenceUnit, JobDescription, Requirement


def main():
    print("=" * 70)
    print("NEXORA REAL OFFLINE MODEL SMOKE TEST (NO MOCKS)")
    print("=" * 70)

    # 1. Verify and load actual local embedding model
    print(f"\n[1] Verifying local model path: {MODEL_PATH}")
    assert MODEL_PATH.exists(), f"Model path {MODEL_PATH} must exist locally"
    assert (MODEL_PATH / "model.safetensors").exists(), "model.safetensors must exist"

    print("    Loading SentenceTransformer locally with local_files_only=True...")
    model = load_embedding_model(MODEL_PATH)
    assert model is not None
    print("    Model successfully loaded offline from local disk.")

    # 2. Define 3 requirements
    jd = {
        "jd_id": "jd_smoke_3req",
        "title": "Full Stack Engineer Intern",
        "requirements": [
            {
                "requirement_id": "req_react",
                "text": "React frontend web application development",
                "canonical": "react",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25,
                "aliases": ["react", "reactjs", "react.js"],
            },
            {
                "requirement_id": "req_node",
                "text": "Node.js backend API services",
                "canonical": "node.js",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25,
                "aliases": ["node", "nodejs", "node.js"],
                "related_skills": [{"canonical": "express", "support": 0.75}],
            },
            {
                "requirement_id": "req_docker",
                "text": "Docker containerization and deployment",
                "canonical": "docker",
                "category": "technology",
                "requirement_type": "preferred",
                "importance": 0.45,
                "aliases": ["docker", "containerized"],
            },
        ],
    }

    # 3. Define 2 structured candidates
    candidates = [
        {
            "candidate_id": "cand_alex",
            "name": "Alex Rivera (Full-Stack Focus)",
            "normalized_skills": ["react", "node.js"],
            "evidence_units": [
                {
                    "evidence_id": "ev_alex_01",
                    "candidate_id": "cand_alex",
                    "text": "Built responsive dashboard interfaces using React and Redux.",
                    "normalized_text": "built responsive dashboard interfaces using react and redux.",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": False,
                },
                {
                    "evidence_id": "ev_alex_02",
                    "candidate_id": "cand_alex",
                    "text": "Engineered Node.js backend microservices handling customer authentication.",
                    "normalized_text": "engineered node.js backend microservices handling customer authentication.",
                    "section": "experience",
                    "has_action_verb": True,
                    "has_outcome": True,
                },
            ],
            "extraction_quality": 0.95,
        },
        {
            "candidate_id": "cand_sam",
            "name": "Sam Taylor (DevOps & Express Focus)",
            "normalized_skills": ["express", "docker"],
            "evidence_units": [
                {
                    "evidence_id": "ev_sam_01",
                    "candidate_id": "cand_sam",
                    "text": "Developed REST API endpoints using Express framework for backend data routing.",
                    "normalized_text": "developed rest api endpoints using express framework for backend data routing.",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": False,
                },
                {
                    "evidence_id": "ev_sam_02",
                    "candidate_id": "cand_sam",
                    "text": "Automated Docker container builds and deployed multi-container environments.",
                    "normalized_text": "automated docker container builds and deployed multi-container environments.",
                    "section": "experience",
                    "has_action_verb": True,
                    "has_outcome": True,
                },
            ],
            "extraction_quality": 0.92,
        },
    ]

    print("\n[2] Executing rank_candidates with actual embeddings...")
    result = rank_candidates(jd=jd, candidates=candidates, model=model)

    print(f"\n[3] Ranking Results ({result.candidate_count} candidates evaluated):")
    print("-" * 70)

    for cand in result.ranked_candidates:
        print(f"\nRank #{cand.rank}: {cand.name} (ID: {cand.candidate_id})")
        print(f"  Final Score: {cand.score}/100")
        print(f"  Confidence:  {cand.confidence}% ({cand.confidence_label})")
        print(f"  Coverage:    Required={cand.required_coverage:.2%}, Preferred={cand.preferred_coverage:.2%}")
        print(f"  Alignment:   Keyword={cand.keyword_alignment:.2f}, Semantic={cand.semantic_alignment:.2f}, Evidence Strength={cand.evidence_strength:.2f}")
        print(f"  Matched:     {cand.matched_requirements}")
        print(f"  Missing:     {cand.missing_required}")
        print("  Requirement-Level Breakdown:")
        for m in cand.requirement_matches:
            print(f"    - {m.requirement_id:<12}: Score={m.final_requirement_score:.3f} | K={m.keyword_score:.2f}, S={m.semantic_score:.2f}, O={m.ontology_support:.2f}, E={m.evidence_strength:.2f}, Guard={m.context_guard:.2f} -> {m.status}")
            print(f"      Evidence IDs: {m.evidence_ids}")

    print("\n[4] Sensitivity Analysis across weights [0.30, 0.40, 0.50]:")
    print(f"  Stable Top Three: {result.sensitivity.stable_top_three}")
    print(f"  Rank Shifts:      {result.sensitivity.rank_changes}")
    print("=" * 70)


if __name__ == "__main__":
    main()
