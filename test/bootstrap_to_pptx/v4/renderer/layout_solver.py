from dataclasses import dataclass
from typing import List, Tuple
from .grid import Grid12
from parsers.generic_bootstrap_to_ilt import ILT, ILTRow, ILTItem

@dataclass
class Rect:
    left: float; top: float; width: float; height: float

def solve_layout(grid: Grid12, ilt: ILT, *, row_top_in: float, row_height_in: float, row_gap_in: float = 0.0) -> List[Tuple[Rect, ILTItem]]:
    """
    Flattens ILT rows into (Rect, ILTItem) placements.
    Simple policy: each ILTItem reserves its col_span at its offset; if a row overflows, start a new band below.
    """
    placements: List[Tuple[Rect, ILTItem]] = []
    cur_top = row_top_in
    for row in ilt.rows:
        cursor = 0
        for it in row.items:
            col_start = cursor + it.offset
            left, top, w, h = grid.rect_for(row_top_in=cur_top - grid.m_top, col_start=col_start, col_span=it.col_span, height_in=row_height_in)
            # respect h_frac if present
            if it.h_frac:
                h = h * it.h_frac
            placements.append((Rect(left, cur_top, w, h), it))
            cursor = col_start + it.col_span
        cur_top += row_height_in + row_gap_in
    return placements
