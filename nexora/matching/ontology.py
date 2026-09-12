"""Local skill ontology and relationship resolution for NEXORA."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nexora.config import DEFAULT_ALIASES_PATH, DEFAULT_ONTOLOGY_PATH
from nexora.schemas import Requirement


def load_ontology(ontology_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load the local ontology JSON file.
    
    Returns an empty dict if the file is missing or invalid.
    """
    path = Path(ontology_path) if ontology_path else DEFAULT_ONTOLOGY_PATH
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_aliases(aliases_path: Optional[Union[str, Path]] = None) -> Dict[str, List[str]]:
    """Load the local aliases JSON file.
    
    Returns an empty dict if the file is missing or invalid.
    """
    path = Path(aliases_path) if aliases_path else DEFAULT_ALIASES_PATH
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_req_field(requirement: Union[Requirement, Dict[str, Any]], field: str, default: Any = None) -> Any:
    """Helper to extract attribute from either a Pydantic Requirement or dict."""
    if isinstance(requirement, dict):
        return requirement.get(field, default)
    return getattr(requirement, field, default)


def get_aliases(
    requirement: Union[Requirement, Dict[str, Any]],
    aliases: Optional[Dict[str, List[str]]] = None,
    ontology: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Compile a deduplicated, lowercased list of aliases for a requirement.
    
    Combines:
    1. Aliases explicitly declared on the requirement.
    2. Aliases defined in aliases.json for the canonical term.
    3. Aliases defined in ontology.json for the canonical term.
    """
    canonical = str(_get_req_field(requirement, "canonical", "")).strip().lower()
    text = str(_get_req_field(requirement, "text", "")).strip().lower()
    
    collected: List[str] = []
    if canonical:
        collected.append(canonical)
    if text and text != canonical:
        collected.append(text)
        
    explicit_aliases = _get_req_field(requirement, "aliases", [])
    if explicit_aliases:
        collected.extend([str(a).strip().lower() for a in explicit_aliases if a])
        
    if aliases and canonical in aliases:
        collected.extend([str(a).strip().lower() for a in aliases[canonical] if a])
        
    if ontology and canonical in ontology:
        onto_aliases = ontology[canonical].get("aliases", [])
        collected.extend([str(a).strip().lower() for a in onto_aliases if a])
        
    # Deduplicate while preserving order
    seen = set()
    unique_aliases = []
    for alias in collected:
        if alias and alias not in seen:
            seen.add(alias)
            unique_aliases.append(alias)
            
    return unique_aliases


def get_related_skills(
    requirement: Union[Requirement, Dict[str, Any]],
    ontology: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Extract related skills and their support weights for a requirement.
    
    Combines:
    1. Explicit related_skills declared in the requirement.
    2. Related skills defined in ontology.json for the canonical requirement.
    """
    related_map: Dict[str, float] = {}
    
    # Check explicit related_skills on requirement
    req_related = _get_req_field(requirement, "related_skills", [])
    if req_related:
        for item in req_related:
            if isinstance(item, dict):
                c = str(item.get("canonical", "")).strip().lower()
                s = float(item.get("support", 0.5))
            else:
                c = str(getattr(item, "canonical", "")).strip().lower()
                s = float(getattr(item, "support", 0.5))
            if c:
                related_map[c] = s

    # Check ontology.json
    canonical = str(_get_req_field(requirement, "canonical", "")).strip().lower()
    if ontology and canonical in ontology:
        onto_related = ontology[canonical].get("related", {})
        for rel_skill, support in onto_related.items():
            rel_canonical = str(rel_skill).strip().lower()
            if rel_canonical:
                # Retain the higher support score if already present
                related_map[rel_canonical] = max(related_map.get(rel_canonical, 0.0), float(support))
                
    return related_map


def _contains_token(text: str, token: str) -> bool:
    """Safe token boundary match to prevent e.g. Java matching JavaScript.
    
    Uses alphanumeric boundary checks so tokens like 'nodejs' match in 'using nodejs.'
    while preventing substring collisions like 'java' in 'javascript'.
    """
    clean_token = token.strip().lower()
    if not clean_token:
        return False
    escaped = re.escape(clean_token)
    pattern = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
    return bool(re.search(pattern, text.lower()))



def calculate_ontology_support(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[Dict[str, Any], Any]],
    candidate: Optional[Union[Dict[str, Any], Any]] = None,
    ontology: Optional[Dict[str, Any]] = None,
    aliases: Optional[Dict[str, List[str]]] = None,
    exact_matched: bool = False,
    alias_matched: bool = False,
) -> float:
    """Calculate ontology / contextual support score O(r,c).
    
    If the requirement is already directly matched (exact or alias), ontology support is 1.0.
    Otherwise, inspects candidate evidence units and normalized skills for related skills.
    Returns the maximum support weight of any verified related skill, or 0.0.
    """
    if exact_matched or alias_matched:
        return 1.0
        
    related_skills = get_related_skills(requirement, ontology)
    if not related_skills:
        return 0.0
        
    # Extract candidate normalized skills if present
    candidate_skills = []
    if candidate:
        if isinstance(candidate, dict):
            candidate_skills = [str(s).strip().lower() for s in candidate.get("normalized_skills", [])]
        else:
            candidate_skills = [str(s).strip().lower() for s in getattr(candidate, "normalized_skills", [])]

    # Precompile search terms for related skills (including their aliases if available)
    related_search_terms: Dict[str, List[str]] = {}
    for rel_skill in related_skills:
        terms = [rel_skill]
        if aliases and rel_skill in aliases:
            terms.extend([str(a).strip().lower() for a in aliases[rel_skill]])
        if ontology and rel_skill in ontology:
            terms.extend([str(a).strip().lower() for a in ontology[rel_skill].get("aliases", [])])
        related_search_terms[rel_skill] = list(set(terms))

    best_support = 0.0
    
    # Check normalized skills first
    for rel_skill, support in related_skills.items():
        terms = related_search_terms[rel_skill]
        for term in terms:
            if term in candidate_skills:
                best_support = max(best_support, support)
                break

    # Check evidence units text
    for ev in evidence_units:
        if isinstance(ev, dict):
            text = str(ev.get("normalized_text") or ev.get("text") or "").lower()
        else:
            text = str(getattr(ev, "normalized_text", None) or getattr(ev, "text", "")).lower()
            
        for rel_skill, support in related_skills.items():
            if support <= best_support:
                continue
            terms = related_search_terms[rel_skill]
            for term in terms:
                if _contains_token(text, term):
                    best_support = max(best_support, support)
                    break

    return round(float(best_support), 4)
