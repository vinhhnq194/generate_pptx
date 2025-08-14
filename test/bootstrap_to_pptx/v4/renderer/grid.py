from dataclasses import dataclass

@dataclass
class Grid12:
    slide_width_in: float
    slide_height_in: float
    margins_in: tuple[float, float, float, float]  # left, top, right, bottom
    gutter_in: float

    def __post_init__(self):
        self.m_left, self.m_top, self.m_right, self.m_bottom = self.margins_in
        self.content_w = self.slide_width_in - self.m_left - self.m_right
        self.content_h = self.slide_height_in - self.m_top - self.m_bottom
        # 12 columns = 12 col widths + 11 gutters
        self.col_w = (self.content_w - 11*self.gutter_in) / 12.0

    def rect_for(self, *, row_top_in: float, col_start: int, col_span: int, height_in: float):
        left = self.m_left + col_start * (self.col_w + self.gutter_in)
        width = col_span * self.col_w + (col_span - 1) * self.gutter_in
        top = self.m_top + row_top_in
        return left, top, width, height_in

    # optional helpers
    def left_for(self, offset_cols: int) -> float:
        return self.m_left + offset_cols * (self.col_w + self.gutter_in)
    def width_for(self, span_cols: int) -> float:
        return max(0.0, span_cols * self.col_w + (span_cols - 1) * self.gutter_in)
