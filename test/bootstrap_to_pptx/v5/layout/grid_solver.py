from dataclasses import dataclass
from typing import List, Tuple
from v5.parsers.model import LayoutSlide, LayoutGroup

@dataclass
class Rect:
    left: float; top: float; width: float; height: float

@dataclass
class Grid12:
    slide_w: float
    slide_h: float
    margins: tuple[float, float, float, float]  # L, T, R, B
    gutter: float

    def __post_init__(self):
        self.mL, self.mT, self.mR, self.mB = self.margins
        self.content_w = self.slide_w - self.mL - self.mR
        self.content_h = self.slide_h - self.mT - self.mB
        # 12 columns have 11 gutters between them
        self.col_w = (self.content_w - 11 * self.gutter) / 12.0

    def rect_for(self, col_start: int, col_span: int, row_top: float, row_h: float) -> Rect:
        left = self.mL + col_start * (self.col_w + self.gutter)
        width = col_span * self.col_w + (col_span - 1) * self.gutter
        top = self.mT + row_top
        return Rect(left, top, width, row_h)

def solve_layout(slide_layout: LayoutSlide, page: dict, bands: dict, gutter_in: float) -> List[Tuple[Rect, LayoutGroup]]:
    """
    Convert proportional layout to absolute placements.
    Packing policy:
      - Accumulate within a visual band (row_height_in)
      - If used_cols + (offset + span) > 12 -> wrap to a new band
      - After finishing a .row, move to next band as well
    """
    grid = Grid12(page["width_in"], page["height_in"], tuple(page["margins_in"]), gutter_in)
    row_top = bands["row_top_in"]
    row_h   = bands["row_height_in"]
    placements: List[Tuple[Rect, LayoutGroup]] = []

    for row in slide_layout.rows:
        used_cols = 0
        for g in row.groups:
            take = g.offset + g.span
            if used_cols + take > 12:
                # wrap to new band
                row_top += row_h
                used_cols = 0
            col_start = used_cols + g.offset
            rect = grid.rect_for(col_start, g.span, row_top - grid.mT, row_h)
            placements.append((rect, g))
            used_cols = col_start + g.span
        # next band after finishing this .row
        row_top += row_h

    return placements
