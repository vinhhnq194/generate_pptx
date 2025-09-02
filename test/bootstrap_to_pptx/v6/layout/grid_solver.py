from dataclasses import dataclass
from typing import List, Tuple
from v6.parsers.model import LayoutTree, LayoutRow, LayoutCol

@dataclass
class Rect:
    left: float; top: float; width: float; height: float

# ---------- helpers to split a row into wrapped lines ----------

@dataclass
class LineCol:
    col: LayoutCol
    col_start: int  # starting column (0..11) after offset is applied
    span: int

def _row_to_lines(row: LayoutRow) -> List[List[LineCol]]:
    """
    Split a row into lines based on 12-col wrapping and offsets.
    Each line contains a sequence of LineCol with precomputed start/span.
    """
    lines: List[List[LineCol]] = [[]]
    used = 0
    for g in row.cols:
        take = g.offset + g.span
        if used + take > 12 and lines[-1]:  # wrap if it doesn't fit AND current line has content
            lines.append([])
            used = 0
        col_start = used + g.offset
        lines[-1].append(LineCol(col=g, col_start=col_start, span=g.span))
        used = col_start + g.span
    return lines

# ---------- measuring: how many height "units" are needed ----------

def _measure_col_units(col: LayoutCol) -> int:
    """
    Height units required by a column.
    - If no nested rows: 1 unit.
    - If nested rows: sum of the units of each nested row (rows stack vertically inside the column).
    """
    if not col.rows:
        return 1
    total = 0
    for nrow in col.rows:
        total += _measure_row_units(nrow)
    return max(1, total)

def _measure_row_units(row: LayoutRow) -> int:
    """
    Height units required by a row.
    - Split row into wrapped lines.
    - Each line's units = max(units of its columns in that line).
    - Row units = sum(line units).
    """
    lines = _row_to_lines(row)
    units = 0
    for line in lines:
        if not line:
            continue
        line_units = 1
        for lc in line:
            line_units = max(line_units, _measure_col_units(lc.col))
        units += line_units
    return max(1, units)

# ---------- placement inside a container ----------

def _place_line_in_container(
    line: List[LineCol],
    container: Rect,
    unit_h: float,
    base_gutter_pct: float
) -> List[Tuple[Rect, LayoutCol]]:
    """
    Place all columns of a single *line* within the given container.
    container.height is the total line height (line_units * unit_h).
    """
    placements: List[Tuple[Rect, LayoutCol]] = []
    gutter = base_gutter_pct * max(1e-6, container.width)
    colw = (container.width - 11 * gutter) / 12.0

    for lc in line:
        left = container.left + lc.col_start * (colw + gutter)
        width = lc.span * colw + (lc.span - 1) * gutter
        # each column gets full line height so nested rows fit
        rect = Rect(left, container.top, width, container.height)
        placements.append((rect, lc.col))
    return placements

def _place_row_in_container(
    row: LayoutRow,
    container: Rect,
    unit_h: float,
    base_gutter_pct: float
) -> List[Tuple[Rect, LayoutCol]]:
    """
    Place a full row (possibly multiple wrapped lines) into the container.
    Each line's height = (max nested units among its columns) * unit_h.
    Lines are stacked vertically inside the row container.
    """
    placements: List[Tuple[Rect, LayoutCol]] = []
    lines = _row_to_lines(row)

    cur_top = container.top
    for line in lines:
        if not line:
            continue
        # measure this line's height in units
        line_units = 1
        for lc in line:
            line_units = max(line_units, _measure_col_units(lc.col))
        line_h = line_units * unit_h

        line_container = Rect(container.left, cur_top, container.width, line_h)
        placements.extend(_place_line_in_container(line, line_container, unit_h, base_gutter_pct))
        cur_top += line_h

    return placements

# ---------- public: solve the whole tree ----------

def solve_layout_tree(tree: LayoutTree, page: dict, bands: dict) -> List[Tuple[Rect, LayoutCol]]:
    """
    Compute placements for all columns (including nested), avoiding overlaps:
    - Split each row into wrapped lines.
    - Give each line enough height to fit its nested rows.
    - Stack lines to get row height; stack rows to build page vertically.
    """
    placements: List[Tuple[Rect, LayoutCol]] = []

    L, T, R, B = page["margins_in"]
    content_w = page["width_in"] - L - R
    unit_h = bands["row_height_in"]     # the base "height unit"
    row_top_start = T + bands["row_top_in"]

    # proportional gutter based on root content width
    base_gutter_pct = page["gutter_in"] / max(1e-6, content_w)

    def place_rows(rows: List[LayoutRow], left: float, top: float, width: float) -> float:
        """
        Place a list of rows within a container at (left, top, width).
        Returns the new 'top' after placing all rows (i.e., total consumed height).
        """
        cur_top = top
        for row in rows:
            # measure row height (sum of line heights)
            row_units = _measure_row_units(row)
            row_h = row_units * unit_h

            row_container = Rect(left, cur_top, width, row_h)
            # place this row's lines & columns
            row_placements = _place_row_in_container(row, row_container, unit_h, base_gutter_pct)
            placements.extend(row_placements)

            # recurse: for each placed column that has nested rows, place them within that column rect
            # NOTE: we rely on the same unit_h for inner levels; line measurement already accounted for nested needs
            for rect, col in row_placements:
                if col.rows:
                    place_rows(col.rows, rect.left, rect.top, rect.width)
            cur_top += row_h
        return cur_top

    place_rows(tree.root_rows, L, row_top_start, content_w)
    return placements
