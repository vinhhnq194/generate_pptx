from dataclasses import dataclass
from typing import List, Tuple
from v6.parsers.model import LayoutTree, LayoutRow, LayoutCol

@dataclass
class Rect:
    left: float; top: float; width: float; height: float

def _place_row_in_container(row: LayoutRow, container: Rect, band_h: float, base_gutter_pct: float):
    """
    Place one row's columns inside 'container' using a local 12-col grid.
    Returns list[(Rect, LayoutCol)].
    """
    placements: List[Tuple[Rect, LayoutCol]] = []
    gutter = base_gutter_pct * max(1e-6, container.width)
    colw = (container.width - 11 * gutter) / 12.0

    used_cols = 0
    cur_top = container.top
    for col in row.cols:
        take = col.offset + col.span
        if used_cols + take > 12:
            # wrap to next band inside this same container
            cur_top += band_h
            used_cols = 0
        col_start = used_cols + col.offset
        left = container.left + col_start * (colw + gutter)
        width = col.span * colw + (col.span - 1) * gutter
        rect = Rect(left, cur_top, width, band_h)
        placements.append((rect, col))
        used_cols = col_start + col.span
    return placements

def solve_layout_tree(tree: LayoutTree, page: dict, bands: dict) -> List[Tuple[Rect, LayoutCol]]:
    """
    Recursively compute placements for all columns (including nested),
    using container-relative 12-col grids and proportional gutters.
    """
    placements: List[Tuple[Rect, LayoutCol]] = []

    L, T, R, B = page["margins_in"]
    content_w = page["width_in"] - L - R
    # band height is constant in this version
    band_h = bands["row_height_in"]

    # proportional gutter: base on root content width
    base_gutter_pct = page["gutter_in"] / max(1e-6, content_w)

    def place_rows(rows: List[LayoutRow], container_left: float, container_top: float, container_w: float):
        nonlocal placements
        cur_top = container_top
        for row in rows:
            row_container = Rect(container_left, cur_top, container_w, band_h)
            cols = _place_row_in_container(row, row_container, band_h, base_gutter_pct)
            for col_rect, col in cols:
                placements.append((col_rect, col))
                if col.rows:
                    # recurse inside this column's rect
                    place_rows(col.rows, col_rect.left, col_rect.top, col_rect.width)
            # next band for the next sibling row at this level
            cur_top += band_h

    # root container: full content width, starting at top + row_top_in
    place_rows(tree.root_rows, L, T + bands["row_top_in"], content_w)
    return placements
