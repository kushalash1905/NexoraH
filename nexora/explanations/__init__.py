"""
Person 4 explanations module.
Exposes explanation generation, candidate comparison, and recruiter question handlers.
"""

from nexora.explanations.generator import (
    generate_top_three_explanations,
    get_missing_requirements,
    get_improvement_opportunities,
    build_normalization_summary,
    build_final_result
)
from nexora.explanations.comparison import compare_candidates, recruiter_answer
from nexora.explanations.templates import TOP_THREE_TEMPLATE, COMPARISON_SUMMARY_TEMPLATE
