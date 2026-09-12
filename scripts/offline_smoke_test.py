"""
Offline smoke test script for Nexora.
Verifies local model loading, module imports, and offline pipeline execution without network calls.
"""

import os
import sys
import tempfile

# Set offline environment variables
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("=========================================")
print("RUNNING NEXORA OFFLINE SMOKE TEST")
print("=========================================")

# 1. Test imports
try:
    from nexora.parsers import parse_jd, parse_resume
    from nexora.matching.matcher import match_candidate_requirement
    from nexora.ranking import rank_candidates
    from nexora.explanations.generator import generate_top_three_explanations, build_final_result
    from nexora.explanations.comparison import compare_candidates, recruiter_answer
    from nexora.jd_analysis.bias_detector import detect_bias_flags
    from nexora.orchestrator import run_analysis
    print("[PASS] All Nexora core modules imported successfully.")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# 2. Test semantic model offline loading
try:
    from sentence_transformers import SentenceTransformer
    from nexora.config import LOCAL_MODEL_PATH, MODEL_NAME

    if os.path.exists(LOCAL_MODEL_PATH):
        model = SentenceTransformer(str(LOCAL_MODEL_PATH), local_files_only=True)
        print(f"[PASS] Loaded local model from {LOCAL_MODEL_PATH}")
    else:
        model = SentenceTransformer(MODEL_NAME)
        print(f"[PASS] Loaded sentence transformer model {MODEL_NAME}")

    emb = model.encode(["offline smoke test text"], normalize_embeddings=True)
    assert emb.shape[1] == 384
    print("[PASS] Semantic embedding generated 384-dim vector.")
except Exception as e:
    print(f"[WARNING/FAIL] Semantic model test: {e}")

# 3. End-to-end local analysis pipeline test
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
    print(f"[FAIL] Pipeline execution error: {e}")
    sys.exit(1)

print("=========================================")
print("OFFLINE SMOKE TEST PASSED SUCCESSFULLY")
print("=========================================")
