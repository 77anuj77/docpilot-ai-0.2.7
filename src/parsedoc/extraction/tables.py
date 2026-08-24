"""ParseDoc Table Extraction helpers"""

from typing import List


def normalize_table(rows: List[List[str]]) -> dict:
    """Normalize a raw table (list of rows) into headers + rows.

    The first row is treated as the header row when it has the same width as
    the remaining rows.
    """
    if not rows:
        return {"headers": [], "rows": []}
    if len(rows) == 1:
        return {"headers": rows[0], "rows": []}
    headers, body = rows[0], rows[1:]
    # If widths mismatch, treat everything as body (no header)
    if any(len(r) != len(headers) for r in body):
        return {"headers": [], "rows": rows}
    return {"headers": headers, "rows": body}


def merge_tables(raw_tables: List[List[List[str]]]) -> List[dict]:
    """Normalize a list of raw tables."""
    return [normalize_table(t) for t in raw_tables if t]
