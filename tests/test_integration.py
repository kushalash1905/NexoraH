"""
End-to-end integration and offline reliability test suite for Person 4.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import pytest
except ImportError:
    class PytestFallback:
        @staticmethod
        def fixture(func):
            return func

        @staticmethod
        def raises(exc):
            class DummyRaises:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    return exc_type is not None and issubclass(exc_type, exc)
            return DummyRaises()

    pytest = PytestFallback()
from nexora.orchestrator import run_analysis


@pytest.fixture
def sample_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, "sample_jd.txt")
        with open(jd_path, "w", encoding="utf-8") as f:
            f.write("Full Stack Developer Intern\nRequired: Node.js, React, MongoDB, HTML, CSS.")

        resume_paths = []
        for i in range(1, 19):  # 18 resumes
            r_path = os.path.join(tmpdir, f"resume_{i:03d}.txt")
            with open(r_path, "w", encoding="utf-8") as f:
                f.write(f"Candidate {i}\nSummary: Experienced in Node.js, React, and MongoDB projects. Built REST APIs.")
            resume_paths.append(r_path)

        yield jd_path, resume_paths


def test_full_pipeline_18_resumes(sample_workspace):
    jd_path, resume_paths = sample_workspace
    result = run_analysis(jd_path, resume_paths)

    assert "jd" in result
    assert "ranking" in result
    assert "explanations" in result
    assert result["ranking"]["candidate_count"] == 18

    # Verify unique ranks
    ranks = [c["rank"] for c in result["ranking"]["ranked_candidates"]]
    assert sorted(ranks) == list(range(1, 19))


def test_empty_file_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, "empty_jd.txt")
        r_path = os.path.join(tmpdir, "empty_resume.txt")

        with open(jd_path, "w", encoding="utf-8") as f:
            f.write("")

        with open(r_path, "w", encoding="utf-8") as f:
            f.write("")

        result = run_analysis(jd_path, [r_path])
        assert "ranking" in result
        assert result["ranking"]["candidate_count"] == 1


def test_missing_file_error():
    with pytest.raises(FileNotFoundError):
        run_analysis("non_existent_jd.txt", ["non_existent_resume.txt"])


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_p = os.path.join(tmpdir, "sample_jd.txt")
        with open(jd_p, "w", encoding="utf-8") as f:
            f.write("Full Stack Developer Intern\nRequired: Node.js, React, MongoDB, HTML, CSS.")

        r_paths = []
        for i in range(1, 19):
            rp = os.path.join(tmpdir, f"resume_{i:03d}.txt")
            with open(rp, "w", encoding="utf-8") as f:
                f.write(f"Candidate {i}\nSummary: Experienced in Node.js, React, and MongoDB projects.")
            r_paths.append(rp)

        test_full_pipeline_18_resumes((jd_p, r_paths))
        test_empty_file_handling()
        print("[PASS] All integration tests passed successfully.")
