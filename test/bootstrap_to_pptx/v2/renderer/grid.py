import logging
from pptx.util import Inches

# Set or adjust this in your app's entrypoint
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

class Grid12:
    """
    Simple 12-col grid helper for 16:9 slides.

    Logs:
      - Slide/margin/gutter config on init
      - Computed content area & column width
      - Every rect request with inputs and outputs
      - Warnings if col_start/col_span exceed the 12-col layout
    """

    def __init__(
        self,
        slide_width_in: float = 13.333,
        slide_height_in: float = 7.5,
        margins_in: tuple[float, float, float, float] = (0.6, 0.6, 0.6, 0.7),
        gutter_in: float = 0.2,
    ):
        logging.info("Initializing Grid12")
        logging.debug(f"Slide size (in): width={slide_width_in}, height={slide_height_in}")
        logging.debug(f"Margins (in): left={margins_in[0]}, top={margins_in[1]}, "
                      f"right={margins_in[2]}, bottom={margins_in[3]}")
        logging.debug(f"Gutter (in): {gutter_in}")

        self.sw = slide_width_in
        self.sh = slide_height_in
        self.m_left, self.m_top, self.m_right, self.m_bottom = margins_in
        self.gutter = gutter_in

        # Compute content area inside margins
        self.content_w = self.sw - self.m_left - self.m_right
        self.content_h = self.sh - self.m_top - self.m_bottom
        logging.debug(f"Content area (in): width={self.content_w}, height={self.content_h}")

        # There are 11 gutters between 12 columns
        total_gutters = 11 * self.gutter
        self.col_w = (self.content_w - total_gutters) / 12.0
        logging.debug(f"Total gutters (in): {total_gutters}")
        logging.debug(f"Computed column width (in): {self.col_w}")

    def rect_for(self, *, row_top_in: float, col_start: int, col_span: int, height_in: float):
        """
        Compute (left, top, width, height) in inches for a given row offset and column span.

        row_top_in: vertical offset (from top content margin) in inches
        col_start:  zero-based starting column index (0..11)
        col_span:   number of columns to span (1..12)
        height_in:  desired height in inches
        """
        logging.info("Grid12.rect_for called")
        logging.debug(f"Inputs -> row_top_in={row_top_in}, col_start={col_start}, "
                      f"col_span={col_span}, height_in={height_in}")

        # Light sanity checks with warnings (no hard fail to keep behavior unchanged)
        if col_start < 0 or col_start > 11:
            logging.warning(f"col_start={col_start} is outside 0..11")
        if col_span < 1 or col_span > 12:
            logging.warning(f"col_span={col_span} is outside 1..12")
        if (col_start + col_span) > 12:
            logging.warning(f"col_start+col_span={col_start + col_span} exceeds 12 columns")

        left = self.m_left + col_start * (self.col_w + self.gutter)
        width = col_span * self.col_w + (col_span - 1) * self.gutter
        top = self.m_top + row_top_in

        logging.debug(f"Computed -> left={left}, top={top}, width={width}, height={height_in}")
        return left, top, width, height_in

    @staticmethod
    def inches(x: float):
        """Convenience wrapper to convert inches to EMUs for python-pptx APIs."""
        logging.debug(f"Converting inches to EMUs: {x}\"")
        return Inches(x)
