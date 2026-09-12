"""Layout-aware local PDF parser and text extractor.

Extracts text blocks using PyMuPDF, eliminates repeated headers/footers,
normalizes unicode ligatures and hyphens, and assesses extraction quality
and formatting messiness.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Union, Optional
import fitz  # PyMuPDF

from nexora.schemas import ExtractionQuality


def clean_text(raw_text: str) -> str:
    """Perform unicode normalization, ligature replacement, and whitespace cleanup."""
    if not raw_text:
        return ""

    # 1. Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Common typographic ligatures
    ligatures = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "•": "*",
        "·": "*",
    }
    for k, v in ligatures.items():
        text = text.replace(k, v)

    # 3. De-hyphenate words broken across line wraps (e.g., 'archi-\ntecture' -> 'architecture')
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # 4. Standardize strange whitespaces (non-breaking spaces, zero-width chars)
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    
    # 5. Clean trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    # Collapse 3+ consecutive newlines to 2
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return cleaned.strip()


def _is_repeated_header_or_footer(
    bbox: tuple[float, float, float, float],
    page_height: float,
    text: str,
    page_num: int,
    total_pages: int
) -> bool:
    """Heuristic check for header/footer margins and typical patterns."""
    if total_pages <= 1:
        return False

    y0, y1 = bbox[1], bbox[3]
    y_mid = (y0 + y1) / 2.0
    margin_top = page_height * 0.15
    margin_bottom = page_height * 0.85

    # Check position in top or bottom margin
    in_margin = (y_mid <= margin_top) or (y_mid >= margin_bottom)
    if not in_margin:
        return False

    # Check for page numbers (e.g., "Page 1 of 2", "1 / 3", "2")
    stripped = text.strip().lower()
    if re.match(r"^(?:page\s+)?\d+(?:\s*(?:of|/)\s*\d+)?$", stripped):
        return True


    return False


def assess_extraction_quality(
    raw_text: str,
    num_pages: int,
    total_blocks: int,
    empty_blocks: int
) -> ExtractionQuality:
    """Compute extraction diagnostics, quality score, and messy-document detection."""
    words = raw_text.split()
    word_count = len(words)
    warnings: list[str] = []

    # Check for empty / very low content
    if word_count < 50:
        warnings.append("Extremely low word count; document may be scanned or image-only.")

    # Detect excessive non-alphanumeric noise (garbled characters)
    alnum_count = sum(c.isalnum() for c in raw_text)
    total_chars = max(1, len(raw_text))
    alnum_ratio = alnum_count / total_chars

    if alnum_ratio < 0.65:
        warnings.append(f"Low alphanumeric ratio ({alnum_ratio:.2%}); text may have encoding artifacts.")

    # Density ratio (words per page)
    words_per_page = word_count / max(1, num_pages)
    density_ratio = min(2.0, max(0.1, words_per_page / 400.0))  # standard ~400 words/page

    # Unparsed / empty block ratio
    unparsed_ratio = empty_blocks / max(1, total_blocks)
    if unparsed_ratio > 0.3:
        warnings.append(f"High ratio of empty/unparsed blocks ({unparsed_ratio:.1%}).")

    # Quality score calculation (0.0 to 1.0)
    score = 1.0
    if word_count < 100:
        score -= 0.3
    if alnum_ratio < 0.70:
        score -= 0.25
    if unparsed_ratio > 0.25:
        score -= 0.15
    if words_per_page < 80:
        score -= 0.2

    quality_score = max(0.0, min(1.0, round(score, 2)))
    is_messy = quality_score < 0.70 or len(warnings) >= 2

    return ExtractionQuality(
        word_count=word_count,
        page_count=num_pages,
        unparsed_blocks_count=empty_blocks,
        density_ratio=round(density_ratio, 2),
        is_messy=is_messy,
        warnings=warnings,
        quality_score=quality_score
    )


def extract_pdf_blocks(
    source: Union[str, Path, bytes]
) -> tuple[list[dict], ExtractionQuality]:
    """Extract layout-aware text blocks with bounding boxes and provenance.
    
    Returns:
        tuple[list[dict], ExtractionQuality]: Extracted blocks and document quality score.
        Each block is a dict with: 'page', 'bbox', 'text'.
    """
    if isinstance(source, (str, Path)):
        doc = fitz.open(str(source))
    else:
        doc = fitz.open(stream=source, filetype="pdf")

    total_pages = len(doc)
    extracted_blocks: list[dict] = []
    total_blocks_count = 0
    empty_blocks_count = 0
    full_text_pieces: list[str] = []

    # Only remove short margin text when it truly repeats across pages.
    repeated = {}
    for index in range(total_pages):
        pg = doc[index]
        for block in pg.get_text("blocks"):
            if len(block) > 6 and block[6] != 0: continue
            mid = (block[1]+block[3])/2
            text = clean_text(block[4])
            if text and len(text.split()) <= 4 and (mid <= pg.rect.height*.15 or mid >= pg.rect.height*.85):
                repeated.setdefault(text, set()).add(index)
    try:
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1
            page_height = page.rect.height
            # get_text("blocks") returns (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")

            for b in blocks:
                total_blocks_count += 1
                b_bbox = (b[0], b[1], b[2], b[3])
                if len(b) > 6 and b[6] != 0: continue
                b_text = b[4]
                
                cleaned_block = clean_text(b_text)
                if not cleaned_block:
                    empty_blocks_count += 1
                    continue

                # Filter out repeated headers/footers
                if _is_repeated_header_or_footer(b_bbox, page_height, cleaned_block, page_num, total_pages) or (len(repeated.get(cleaned_block, set())) > 1 and (page_num > 1 or re.search(r"\b(confidential|resume|curriculum vitae|header)\b", cleaned_block, re.I))):
                    continue

                extracted_blocks.append({
                    "page": page_num,
                    "bbox": b_bbox,
                    "text": cleaned_block,
                    "raw_text": b_text
                })
                full_text_pieces.append(cleaned_block)

        aggregated_text = "\n\n".join(full_text_pieces)
        quality = assess_extraction_quality(
            raw_text=aggregated_text,
            num_pages=total_pages,
            total_blocks=total_blocks_count,
            empty_blocks=empty_blocks_count
        )
        return extracted_blocks, quality

    finally:
        doc.close()


def extract_pdf_text(
    source: Union[str, Path, bytes]
) -> tuple[str, ExtractionQuality]:
    """Convenience function to extract cleaned full text from a PDF."""
    blocks, quality = extract_pdf_blocks(source)
    full_text = "\n\n".join(b["text"] for b in blocks)
    return full_text, quality
