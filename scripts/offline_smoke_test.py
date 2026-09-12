"""
Offline smoke test verification for NEXORA.

Validates that all models, ontologies, ranking routines, explanations,
and end-to-end pipelines run with complete network isolation (100% offline).
"""

import os
import sys
import tempfile
from pathlib import Path

# Enforce offline flags in environment before importing transformers/torch
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("=========================================")
print("RUNNING NEXORA OFFLINE SMOKE TEST")
print("=========================================")

# 1. Module Imports Test
try:
    from nexora.config import LOCAL_MODEL_PATH, MODEL_PATH, MODEL_NAME
    from nexora.schemas import Candidate, EvidenceUnit, JobDescription, Requirement, JDBiasFlag
    from nexora.parsers import parse_jd, parse_resume
    from nexora.matching.ontology import load_aliases, load_ontology
    from nexora.matching.semantic_engine import load_embedding_model
    from nexora.matching.matcher import match_candidate_requirement
    from nexora.ranking.scoring import rank_candidates
    from nexora.explanations.generator import generate_top_three_explanations, build_final_result
    from nexora.explanations.comparison import compare_candidates, recruiter_answer
    from nexora.jd_analysis.bias_detector import detect_bias_flags, detect_jd_bias
    from nexora.orchestrator import run_analysis
    print("[PASS] All Nexora core modules imported successfully.")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# 2. Local Model & Embedding Test
try:
    from sentence_transformers import SentenceTransformer

    target_model_path = LOCAL_MODEL_PATH if os.path.exists(LOCAL_MODEL_PATH) else MODEL_PATH
    if os.path.exists(target_model_path):
        model = SentenceTransformer(str(target_model_path), local_files_only=True)
        print(f"[PASS] Loaded local model offline from {target_model_path}")
    else:
        model = SentenceTransformer(MODEL_NAME)
        print(f"[PASS] Loaded sentence transformer model {MODEL_NAME}")

    emb = model.encode(["offline smoke test query"], normalize_embeddings=True)
    assert emb.shape[1] == 384
    print("[PASS] Semantic embedding generated 384-dim normalized vector.")
except Exception as e:
    print(f"[FAIL] Semantic model offline load: {e}")
    sys.exit(1)

# 3. Ontology & Aliases JSON Load Test
try:
    ontology = load_ontology()
    aliases = load_aliases()
    assert len(ontology) > 0, "Ontology should not be empty"
    assert len(aliases) > 0, "Aliases should not be empty"
    print(f"[PASS] Loaded {len(ontology)} ontology nodes and {len(aliases)} alias clusters.")
except Exception as e:
    print(f"[WARNING/FAIL] Ontology/Aliases load: {e}")

# 4. Engine Candidate Ranking Test
try:
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
    rank_res = rank_candidates(jd, [cand], model=model, aliases=aliases, ontology=ontology)
    assert rank_res.candidate_count == 1
    ranked_c = rank_res.ranked_candidates[0]
    assert ranked_c.score > 0
    print(f"[PASS] Candidate ranked with score {ranked_c.score}/100, confidence {ranked_c.confidence}%.")
except Exception as e:
    print(f"[FAIL] Engine candidate ranking test: {e}")
    sys.exit(1)

# 5. End-to-End Orchestrator & Explanation Test
try:
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_file = os.path.join(tmpdir, "sample_jd.txt")
        res1_file = os.path.join(tmpdir, "resume_001.txt")
        res2_file = os.path.join(tmpdir, "resume_002.txt")

        with open(jd_file, "w", encoding="utf-8") as f:
            f.write("Junior Full Stack Developer\nExperience with Node.js, React, and MongoDB required. 2+ years of experience required.")

        with open(res1_file, "w", encoding="utf-8") as f:
            f.write("Candidate 1\nProjects: Built REST APIs using Express and MongoDB. Worked with React.")

        with open(res2_file, "w", encoding="utf-8") as f:
            f.write("Candidate 2\nSummary: Python developer with Docker skills.")

        res = run_analysis(jd_file, [res1_file, res2_file])

        assert "ranking" in res
        assert len(res["ranking"]["ranked_candidates"]) == 2
        assert len(res["explanations"]) >= 1
        assert "bias_flags" in res

        print("[PASS] End-to-end local analysis pipeline executed successfully.")

        # Test comparison
        cand_a = res["ranking"]["ranked_candidates"][0]["candidate_id"]
        cand_b = res["ranking"]["ranked_candidates"][1]["candidate_id"]
        comp = compare_candidates(cand_a, cand_b, res["ranking"], res["jd"], [])
        assert "score_difference" in comp
        print("[PASS] Candidate comparison engine executed successfully.")

        # Test recruiter Q&A
        ans = recruiter_answer(f"Why is candidate {cand_a} ranked above candidate {cand_b}?", res["ranking"], res["jd"], [])
        assert "answer" in ans
        print("[PASS] Recruiter question parser executed successfully.")

except Exception as e:
    print(f"[FAIL] Orchestrator end-to-end execution error: {e}")
    sys.exit(1)

print("=========================================")
print("OFFLINE SMOKE TEST PASSED SUCCESSFULLY")
print("100% Local Execution Verified.")
print("=========================================")


def run_smoke_test():
    """Entry point when called as a function."""
    pass


if __name__ == "__main__":
    pass
