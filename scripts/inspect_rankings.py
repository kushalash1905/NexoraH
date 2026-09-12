"""CLI inspection tool for NEXORA matching and ranking verification.

Allows judges and team members to inspect candidate scores, requirement breakdowns,
evidence units, and sensitivity diagnostics without opening a browser.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nexora.ranking.scoring import rank_candidates


def inspect_demo():
    # Sample synthetic test case with 4 requirements and 2 candidates
    sample_jd = {
        "jd_id": "jd_demo",
        "title": "Full Stack Developer Intern",
        "requirements": [
            {
                "requirement_id": "req_react",
                "text": "React frontend development",
                "canonical": "react",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25,
                "aliases": ["react", "reactjs", "react.js"],
                "related_skills": [{"canonical": "frontend development", "support": 0.70}],
            },
            {
                "requirement_id": "req_node",
                "text": "Node.js backend development",
                "canonical": "node.js",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.25,
                "aliases": ["node", "nodejs", "node.js"],
                "related_skills": [
                    {"canonical": "express", "support": 0.75},
                    {"canonical": "rest api", "support": 0.55},
                ],
            },
            {
                "requirement_id": "req_mongo",
                "text": "MongoDB database management",
                "canonical": "mongodb",
                "category": "technology",
                "requirement_type": "required",
                "importance": 1.00,
                "aliases": ["mongodb", "mongo", "mongo db"],
                "related_skills": [{"canonical": "database development", "support": 0.60}],
            },
            {
                "requirement_id": "req_docker",
                "text": "Docker containerization",
                "canonical": "docker",
                "category": "technology",
                "requirement_type": "preferred",
                "importance": 0.45,
                "aliases": ["docker", "dockerized", "containerized"],
                "related_skills": [{"canonical": "containerization", "support": 0.80}],
            },
        ],
    }

    sample_candidates = [
        {
            "candidate_id": "candidate_A",
            "name": "Candidate A (Express & MongoDB focused)",
            "normalized_skills": ["react", "express", "mongodb"],
            "evidence_units": [
                {
                    "evidence_id": "ev_a1",
                    "candidate_id": "candidate_A",
                    "text": "Developed responsive interactive UI dashboards using React.",
                    "normalized_text": "developed responsive interactive ui dashboards using react",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": True,
                },
                {
                    "evidence_id": "ev_a2",
                    "candidate_id": "candidate_A",
                    "text": "Built REST APIs using Express and MongoDB for backend services.",
                    "normalized_text": "built rest apis using express and mongodb for backend services",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": False,
                },
            ],
            "extraction_quality": 0.95,
        },
        {
            "candidate_id": "candidate_B",
            "name": "Candidate B (Direct Node.js & Docker)",
            "normalized_skills": ["react", "node.js", "docker"],
            "evidence_units": [
                {
                    "evidence_id": "ev_b1",
                    "candidate_id": "candidate_B",
                    "text": "Developed web applications using React and Node.js backend services.",
                    "normalized_text": "developed web applications using react and node.js backend services",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": True,
                },
                {
                    "evidence_id": "ev_b2",
                    "candidate_id": "candidate_B",
                    "text": "Containerized microservices and automated deployment using Docker.",
                    "normalized_text": "containerized microservices and automated deployment using docker",
                    "section": "projects",
                    "has_action_verb": True,
                    "has_outcome": True,
                },
            ],
            "extraction_quality": 0.95,
        },
    ]

    print("=" * 70)
    print("NEXORA RANKING & MATCHING INSPECTION")
    print("=" * 70)

    result = rank_candidates(sample_jd, sample_candidates)

    print(f"\nEvaluated {result.candidate_count} candidates against JD: {result.jd_id}")
    print("-" * 70)

    for cand in result.ranked_candidates:
        print(f"\n[Rank #{cand.rank}] {cand.name} (ID: {cand.candidate_id})")
        print(f"  Score: {cand.score}/100 | Confidence: {cand.confidence}% ({cand.confidence_label})")
        print(f"  Required Coverage: {cand.required_coverage:.2%} | Preferred Coverage: {cand.preferred_coverage:.2%}")
        print(f"  Keyword Align: {cand.keyword_alignment:.2f} | Semantic Align: {cand.semantic_alignment:.2f} | Ev Strength: {cand.evidence_strength:.2f}")
        print(f"  Matched: {', '.join(cand.matched_requirements) if cand.matched_requirements else 'None'}")
        print(f"  Missing Required: {', '.join(cand.missing_required) if cand.missing_required else 'None'}")
        print(f"  Lexical-Only Pattern: {cand.lexical_only_pattern}")
        print("  Requirement Matches:")
        for m in cand.requirement_matches:
            print(f"    - {m.requirement_id:<12}: Score={m.final_requirement_score:.3f} | K={m.keyword_score:.2f} S={m.semantic_score:.2f} O={m.ontology_support:.2f} E={m.evidence_strength:.2f} Guard={m.context_guard:.2f} -> {m.status}")

    print("\nSensitivity Analysis:")
    print(f"  Tested Weights: {result.sensitivity.semantic_weights_tested}")
    print(f"  Stable Top Three: {result.sensitivity.stable_top_three}")
    print(f"  Rank Changes: {result.sensitivity.rank_changes}")
    print("=" * 70)


if __name__ == "__main__":
    inspect_demo()
