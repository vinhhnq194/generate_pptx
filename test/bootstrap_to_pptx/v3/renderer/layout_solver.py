import logging
from dataclasses import dataclass
from typing import List, Tuple
from .grid import Grid12

# tweak as needed at app entrypoint
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

@dataclass
class Rect:
    left: float
    top: float
    width: float
    height: float

def layout_rows(
    grid: Grid12,
    ilt_rows,
    band_top_in: float,
    band_height_in: float,
    row_gap_in: float = 0.2
) -> List[List[Tuple[Rect, object]]]:
    """
    Returns list of rows; each row is a list of (Rect, ILTItem Group).
    Each ILTItem is a 'column group' that may contain children (card, kpi, etc.)
    """
    logging.info("=== layout_rows start ===")
    logging.debug(f"Inputs -> band_top_in={band_top_in}, band_height_in={band_height_in}, row_gap_in={row_gap_in}")
    logging.debug(f"Total ILT rows: {len(ilt_rows)}")

    rows_out: List[List[Tuple[Rect, object]]] = []
    cur_top = band_top_in
    logging.debug(f"Initial cur_top={cur_top}")

    for row_idx, r in enumerate(ilt_rows):
        logging.info(f"-- Row {row_idx} --")
        row_rects: List[Tuple[Rect, object]] = []
        cursor = 0  # track used columns (0..12)
        logging.debug(f"Row {row_idx}: starting cursor={cursor}")

        for grp_idx, grp in enumerate(r.items):
            logging.debug(
                f"Row {row_idx} / Group {grp_idx}: offset={grp.offset}, span={grp.col_span}, "
                f"classes={getattr(grp, 'classes', None)} kind={getattr(grp, 'kind', 'column')}"
            )

            # offset columns are empty space; compute starting column
            col_start = cursor + grp.offset
            if col_start < 0 or col_start > 11:
                logging.warning(f"Row {row_idx} / Group {grp_idx}: col_start={col_start} outside 0..11")

            if grp.col_span < 1 or grp.col_span > 12:
                logging.warning(f"Row {row_idx} / Group {grp_idx}: col_span={grp.col_span} outside 1..12")

            if (col_start + grp.col_span) > 12:
                logging.warning(
                    f"Row {row_idx} / Group {grp_idx}: col_start+span={col_start + grp.col_span} exceeds 12 cols"
                )

            # rect_for expects vertical offset from top margin
            row_offset_from_margin = cur_top - grid.m_top
            logging.debug(
                f"Row {row_idx} / Group {grp_idx}: calling grid.rect_for("
                f"row_top_in={row_offset_from_margin}, col_start={col_start}, "
                f"col_span={grp.col_span}, height_in={band_height_in})"
            )

            left, top, width, height = grid.rect_for(
                row_top_in=row_offset_from_margin,
                col_start=col_start,
                col_span=grp.col_span,
                height_in=band_height_in
            )
            logging.debug(
                f"Row {row_idx} / Group {grp_idx}: rect -> left={left}, top={top}, width={width}, height={height}"
            )

            rect = Rect(left=left, top=cur_top, width=width, height=band_height_in)
            row_rects.append((rect, grp))
            logging.debug(f"Row {row_idx} / Group {grp_idx}: placed Rect={rect}")

            # advance cursor to the end of this group (offset + span consumed)
            cursor = col_start + grp.col_span
            logging.debug(f"Row {row_idx}: cursor advanced to {cursor}")

        rows_out.append(row_rects)
        logging.debug(f"Row {row_idx}: appended {len(row_rects)} rects")
        cur_top_before = cur_top
        cur_top += band_height_in + row_gap_in
        logging.debug(f"Row {row_idx}: cur_top moved from {cur_top_before} to {cur_top}")

    logging.info("=== layout_rows end ===")
    return rows_out
