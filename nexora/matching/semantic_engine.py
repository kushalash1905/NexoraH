"""Local semantic embedding and similarity engine for NEXORA.

Uses sentence-transformers/all-MiniLM-L6-v2 strictly in offline mode (local_files_only=True).
Computes cosine similarity via dot product on normalized 384-dimensional sentence vectors.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from sentence_transformers import SentenceTransformer

from nexora.config import MODEL_PATH
from nexora.matching.ontology import _get_req_field
from nexora.schemas import EvidenceUnit, Requirement


_CACHED_MODEL: Optional[SentenceTransformer] = None


def load_embedding_model(model_path: Optional[Union[str, Path]] = None) -> SentenceTransformer:
    """Load the local sentence-transformers model offline.
    
    Raises FileNotFoundError with a clear message if the model directory is missing.
    Never attempts network calls or substitutes fake scores.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    path = Path(model_path) if model_path else MODEL_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Offline embedding model not found at '{path.resolve()}'. "
            "In accordance with offline hackathon requirements, the model must be downloaded and "
            "cached beforehand. Run 'python scripts/download_model.py' while online to cache it."
        )

    try:
        model = SentenceTransformer(str(path), local_files_only=True)
        _CACHED_MODEL = model
        return model
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load local embedding model from '{path.resolve()}': {exc}. "
            "Ensure the weights and tokenizer configuration files are intact in the models directory."
        ) from exc


def encode_texts(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    """Encode a list of text strings into normalized 384-dimensional embeddings."""
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return embeddings


def _extract_evidence_text(ev: Union[EvidenceUnit, Dict[str, Any]]) -> str:
    """Safely extract normalized text from an EvidenceUnit or dict."""
    if isinstance(ev, dict):
        return str(ev.get("normalized_text") or ev.get("text") or "").strip()
    return str(getattr(ev, "normalized_text", None) or getattr(ev, "text", "")).strip()


def retrieve_semantic_evidence(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    model: SentenceTransformer,
    top_k: int = 5,
) -> List[Tuple[Union[EvidenceUnit, Dict[str, Any]], float]]:
    """Retrieve top_k candidate evidence units independently based on semantic similarity.
    
    Computes cosine similarity (dot product on normalized embeddings).
    Returns list of (evidence_unit, similarity_score) sorted descending by similarity.
    """
    if not evidence_units:
        return []

    req_text = str(_get_req_field(requirement, "text", "")).strip()
    if not req_text:
        req_text = str(_get_req_field(requirement, "canonical", "")).strip()
    if not req_text:
        return [(ev, 0.0) for ev in evidence_units[:top_k]]

    ev_texts = [_extract_evidence_text(ev) for ev in evidence_units]
    # Filter out empty texts for encoding while maintaining index mapping
    valid_indices = [i for i, t in enumerate(ev_texts) if t]
    if not valid_indices:
        return [(ev, 0.0) for ev in evidence_units[:top_k]]

    valid_texts = [ev_texts[i] for i in valid_indices]

    # Encode requirement and candidate evidence
    req_vec = encode_texts([req_text], model)[0]  # shape (384,)
    ev_matrix = encode_texts(valid_texts, model)  # shape (M, 384)

    # Cosine similarity via dot product
    sims = np.dot(ev_matrix, req_vec)

    scored: List[Tuple[Union[EvidenceUnit, Dict[str, Any]], float]] = []
    for idx_in_valid, orig_idx in enumerate(valid_indices):
        scored.append((evidence_units[orig_idx], float(sims[idx_in_valid])))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def calculate_semantic_score(
    requirement: Union[Requirement, Dict[str, Any]],
    evidence_units: List[Union[EvidenceUnit, Dict[str, Any]]],
    model: SentenceTransformer,
) -> Tuple[float, List[Tuple[Union[EvidenceUnit, Dict[str, Any]], float]]]:
    """Compute S(r,c) = max over e of cosine(requirement, evidence).
    
    Returns:
        (max_semantic_score, top_evidence_pairs)
    """
    if not evidence_units:
        return 0.0, []

    retrieved = retrieve_semantic_evidence(requirement, evidence_units, model=model, top_k=5)
    if not retrieved:
        return 0.0, []

    best_score = max(0.0, retrieved[0][1])
    return round(float(best_score), 4), retrieved
