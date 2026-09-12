"""
Deterministic templates and cautious phrasing for candidate explanations.
Strictly NO LLM.
"""

TOP_THREE_TEMPLATE = (
    "{candidate} ranked #{rank} with a score of {score}/100 and {confidence_label} confidence.\n\n"
    "The strongest matches were {matched_requirements}. Evidence came primarily from {sections}, including:\n\n"
    "“{evidence_snippet}”\n\n"
    "Weak or missing required requirements: {missing_requirements}.\n\n"
    "Preferred matches: {preferred_matches}."
)

COMPARISON_SUMMARY_TEMPLATE = (
    "{candidate_a} ranks above {candidate_b} mainly because:\n\n"
    "1. {largest_diff}\n"
    "2. {second_diff}\n"
    "3. {third_diff}\n\n"
    "{candidate_b_notes}"
)


def format_cautious_missing(skill_name: str) -> str:
    """Cautious phrasing for missing evidence."""
    return f"No reliable evidence was found for {skill_name}."


def format_cautious_partial(skill_name: str, context: str) -> str:
    """Cautious phrasing for partial evidence."""
    if context:
        return f"The resume provides partial evidence for {skill_name} through {context} work."
    return f"The resume provides partial evidence for {skill_name}."
