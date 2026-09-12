"""Date extraction, range normalization, and duration calculation.

Extracts non-standard date ranges from resume experiences, handles relative
terms ("Present", "Current", "Ongoing"), normalizes to YYYY-MM format,
and computes experience durations in months without double-counting overlaps.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

# Reference current date for resolving "Present" / "Current"
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

MONTH_NAMES: dict[str, int] = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

# Regex components
MONTHS_REGEX = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
YEAR_REGEX = r"(?:19|20)\d{2}"
PRESENT_REGEX = r"(?:present|current|now|ongoing|today|till\s+date)"
SEPARATOR_REGEX = r"(?:\s*[-–—]\s*|\s+to\s+)"

# Pattern for Month Year - Month Year / Present
RANGE_MONTH_YEAR = re.compile(
    rf"\b({MONTHS_REGEX})\.?\s+({YEAR_REGEX}){SEPARATOR_REGEX}(?:({MONTHS_REGEX})\.?\s+({YEAR_REGEX})|({PRESENT_REGEX}))\b",
    re.IGNORECASE
)

# Pattern for MM/YYYY - MM/YYYY / Present
RANGE_NUMERIC = re.compile(
    rf"\b(0?[1-9]|1[0-2])\s*[/-]\s*({YEAR_REGEX}){SEPARATOR_REGEX}(?:(0?[1-9]|1[0-2])\s*[/-]\s*({YEAR_REGEX})|({PRESENT_REGEX}))\b",
    re.IGNORECASE
)

# Pattern for Year - Year / Present
RANGE_YEAR_ONLY = re.compile(
    rf"\b({YEAR_REGEX}){SEPARATOR_REGEX}(?:({YEAR_REGEX})|({PRESENT_REGEX}))\b",
    re.IGNORECASE
)

# Single month-year
SINGLE_MONTH_YEAR = re.compile(
    rf"\b({MONTHS_REGEX})\.?\s+({YEAR_REGEX})\b",
    re.IGNORECASE
)


def _parse_month(month_str: Optional[str]) -> int:
    """Resolve month name or digit to an integer 1-12."""
    if not month_str:
        return 1
    m_clean = month_str.strip().lower().rstrip(".")
    if m_clean.isdigit():
        return int(m_clean)
    return MONTH_NAMES.get(m_clean, 1)


def _extract_date_range(text: str) -> Optional[dict]:
    """Extract and normalize a start/end date range and duration from text.
    
    Returns:
        Optional[dict]: Dictionary with keys:
            - 'start_raw': str
            - 'end_raw': str
            - 'start_iso': str (YYYY-MM)
            - 'end_iso': str (YYYY-MM or 'Present')
            - 'duration_months': int
    """
    # 1. Try Month Year - Month Year / Present
    match = RANGE_MONTH_YEAR.search(text)
    if match:
        start_m_str, start_y_str, end_m_str, end_y_str, present_str = match.groups()
        start_y = int(start_y_str)
        start_m = _parse_month(start_m_str)
        
        if present_str:
            end_y = CURRENT_YEAR
            end_m = CURRENT_MONTH
            end_iso = "Present"
        else:
            end_y = int(end_y_str)
            end_m = _parse_month(end_m_str)
            end_iso = f"{end_y:04d}-{end_m:02d}"
            
        start_iso = f"{start_y:04d}-{start_m:02d}"
        duration = max(1, (end_y - start_y) * 12 + (end_m - start_m))
        return {
            "start_raw": f"{start_m_str} {start_y_str}",
            "end_raw": present_str or f"{end_m_str} {end_y_str}",
            "start_iso": start_iso,
            "end_iso": end_iso,
            "duration_months": duration
        }

    # 2. Try MM/YYYY - MM/YYYY / Present
    match = RANGE_NUMERIC.search(text)
    if match:
        start_m_str, start_y_str, end_m_str, end_y_str, present_str = match.groups()
        start_y = int(start_y_str)
        start_m = int(start_m_str)
        
        if present_str:
            end_y = CURRENT_YEAR
            end_m = CURRENT_MONTH
            end_iso = "Present"
        else:
            end_y = int(end_y_str)
            end_m = int(end_m_str)
            end_iso = f"{end_y:04d}-{end_m:02d}"
            
        start_iso = f"{start_y:04d}-{start_m:02d}"
        duration = max(1, (end_y - start_y) * 12 + (end_m - start_m))
        return {
            "start_raw": f"{start_m_str}/{start_y_str}",
            "end_raw": present_str or f"{end_m_str}/{end_y_str}",
            "start_iso": start_iso,
            "end_iso": end_iso,
            "duration_months": duration
        }

    # 3. Try Year - Year / Present
    match = RANGE_YEAR_ONLY.search(text)
    if match:
        start_y_str, end_y_str, present_str = match.groups()
        start_y = int(start_y_str)
        start_m = 1
        
        if present_str:
            end_y = CURRENT_YEAR
            end_m = CURRENT_MONTH
            end_iso = "Present"
        else:
            end_y = int(end_y_str)
            end_m = 12
            end_iso = f"{end_y:04d}-12"
            
        start_iso = f"{start_y:04d}-01"
        duration = max(1, (end_y - start_y) * 12 + (end_m - start_m))
        return {
            "start_raw": start_y_str,
            "end_raw": present_str or end_y_str,
            "start_iso": start_iso,
            "end_iso": end_iso,
            "duration_months": duration
        }

    return None


def calculate_total_experience_months(date_ranges: list[dict]) -> int:
    """Calculate the total non-overlapping experience duration across multiple date ranges."""
    intervals: list[tuple[int, int]] = []
    
    for dr in date_ranges:
        if not dr or "start_iso" not in dr or "end_iso" not in dr:
            continue
            
        try:
            sy, sm = map(int, dr["start_iso"].split("-")[:2])
            start_val = sy * 12 + sm
            
            if dr["end_iso"] == "Present":
                end_val = CURRENT_YEAR * 12 + CURRENT_MONTH
            else:
                ey, em = map(int, dr["end_iso"].split("-")[:2])
                end_val = ey * 12 + em
                
            if end_val >= start_val:
                intervals.append((start_val, end_val))
        except Exception:
            continue
            
    if not intervals:
        return 0
        
    # Merge overlapping intervals
    intervals.sort(key=lambda x: x[0])
    merged: list[tuple[int, int]] = [intervals[0]]
    
    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        if current[0] <= prev_end:
            # Overlap: extend end if needed
            merged[-1] = (prev_start, max(prev_end, current[1]))
        else:
            merged.append(current)
            
    total_months = sum(end - start for start, end in merged)
    return total_months


def extract_date_range(text: str) -> Optional[dict]:
    """Reject reversed ranges; expose uncertainty for year-only dates."""
    result = _extract_date_range(text)
    if result is None:
        iso = re.search(r"\b((?:19|20)\d{2})-(0[1-9]|1[0-2])\s+(?:to|[-–—])\s+((?:19|20)\d{2})-(0[1-9]|1[0-2])\b", text)
        if iso:
            sy,sm,ey,em=map(int,iso.groups())
            result=dict(start_raw=iso.group(1)+'-'+iso.group(2),end_raw=iso.group(3)+'-'+iso.group(4),start_iso=f'{sy:04d}-{sm:02d}',end_iso=f'{ey:04d}-{em:02d}',duration_months=max(1,(ey-sy)*12+em-sm))
    if result is None:return None
    start=tuple(map(int,result['start_iso'].split('-')))
    end=(CURRENT_YEAR,CURRENT_MONTH) if result['end_iso']=='Present' else tuple(map(int,result['end_iso'].split('-')))
    if end < start:return None
    result['precision']='year' if re.fullmatch(YEAR_REGEX,result['start_raw']) else 'month'
    result['warnings']=['Months are unspecified; duration uses Jan-to-Dec assumptions.'] if result['precision']=='year' else []
    return result
