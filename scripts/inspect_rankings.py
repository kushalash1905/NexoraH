"""
Ranking inspection script for Person 4.
Helps inspect ranking output and requirement-level scores/evidence.
Saves debug JSON outputs to debug/ folder.
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nexora.orchestrator import run_analysis


def inspect(jd_path: str, resume_dir: str):
    """
    Runs analysis and prints detailed ranking inspection to CLI.
    Dumps JSON debug files to debug/.
    """
    if not os.path.exists(jd_path):
        print(f"Error: JD file {jd_path} not found.")
        return

    if not os.path.exists(resume_dir):
        print(f"Error: Resume directory {resume_dir} not found.")
        return

    valid_exts = (".pdf", ".docx", ".txt", ".xml")
    resume_paths = [
        os.path.join(resume_dir, f) for f in os.listdir(resume_dir)
        if f.lower().endswith(valid_exts)
    ]

    if not resume_paths:
        print(f"No valid resumes found in {resume_dir}.")
        return

    print(f"Inspecting ranking for JD: {jd_path} across {len(resume_paths)} resumes...")

    result = run_analysis(jd_path, resume_paths)

    ranking = result.get("ranking", {})
    ranked_cands = ranking.get("ranked_candidates", [])

    print("\n================ CANDIDATE LEADERBOARD ================")
    for c in ranked_cands:
        print(f"Rank #{c.get('rank'):02d} | Candidate: {c.get('name'):<20} | Score: {c.get('score'):5.1f}/100 | Coverage: {int(c.get('required_coverage', 0)*100)}% | Confidence: {c.get('confidence'):.1f}% ({c.get('confidence_label')})")

    print("\n================ TOP THREE EXPLANATIONS ================")
    for exp in result.get("explanations", []):
        print(f"\n--- Rank #{exp.get('rank')} (Candidate {exp.get('candidate_id')}) ---")
        print(exp.get("summary"))

    print("\n================ NARROW-LANGUAGE FLAGS ================")
    for flag in result.get("bias_flags", []):
        print(f"[{flag.get('severity').upper()}] {flag.get('phrase')}: {flag.get('reason')}")

    # Create debug directory and save debug files
    debug_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debug"))
    os.makedirs(debug_dir, exist_ok=True)

    with open(os.path.join(debug_dir, "final_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\n[OK] Debug results saved to {debug_dir}/final_result.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Nexora candidate rankings.")
    parser.add_argument("--jd", type=str, help="Path to JD file", default="data/sample_jd.txt")
    parser.add_argument("--resumes", type=str, help="Directory containing resumes", default="data/resumes")
    args = parser.parse_args()

    inspect(args.jd, args.resumes)
