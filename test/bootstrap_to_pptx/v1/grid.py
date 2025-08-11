# grid.py
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

EMU_PER_INCH = 914400

class Grid12:
    """
    A simple 12-col grid helper.
    Units are in inches for readability; python-pptx converts to EMUs under the hood.
    """
    def __init__(self, slide_width_in=13.333, # 1280x720 ≈ 13.333x7.5 inches
                 margins_in=(0.5, 0.5, 0.5, 0.6),  # left, top, right, bottom
                 gutter_in=0.15):
        self.sw = slide_width_in
        self.m_left, self.m_top, self.m_right, self.m_bottom = margins_in
        self.gutter = gutter_in
        self.content_w = self.sw - self.m_left - self.m_right
        # 12 columns = 12 widths + 11 gutters
        total_gutters = 11 * self.gutter
        self.col_w = (self.content_w - total_gutters) / 12.0
    
    def rect_for(self, *, row_top_in, col_start, col_span, height_in):
        """
        Get (left, top, width, height) in Inches for a grid cell block.
        col_start is 0-based (0..11); col_span 1..12
        """
        left = self.m_left + col_start * (self.col_w + self.gutter)
        width = col_span * self.col_w + (col_span - 1) * self.gutter
        top = self.m_top + row_top_in
        return left, top, width, height_in
