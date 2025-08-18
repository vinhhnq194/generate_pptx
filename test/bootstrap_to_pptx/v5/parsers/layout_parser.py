from bs4 import BeautifulSoup
from .model import LayoutSlide, LayoutRow, LayoutGroup
from .bootstrap_norm import resolve_span, resolve_offset, is_unbounded_col

def _classes(el):
    return el.get("class", []) if el else []

def _direct_cols(row):
    # direct children that look like bootstrap columns
    return [c for c in row.find_all(recursive=False) if any(cc.startswith("col") for cc in _classes(c))]

def _distribute_unspecified(spans: list[int], unspecified_idx: list[int]) -> None:
    """
    Distribute remaining columns equally among unspecified 'col'/'col-auto'.
    Ensure each gets at least 1 col; if over-allocated, clamp later.
    """
    total_spec = sum(s for s in spans if s > 0)
    remaining = max(0, 12 - total_spec)
    n_uns = len(unspecified_idx)
    if n_uns == 0:
        return
    base = max(1, remaining // n_uns) if remaining > 0 else 1
    for i in unspecified_idx:
        spans[i] = base
    # if still leftover, add 1 to the first few
    leftover = max(0, remaining - base * n_uns)
    j = 0
    while leftover > 0 and j < n_uns:
        spans[unspecified_idx[j]] += 1
        leftover -= 1
        j += 1

def parse_layout_only(html_path: str) -> LayoutSlide:
    """
    Build a proportional layout (no content).
    - Each .row → LayoutRow
    - Each direct .col-* child → LayoutGroup(span/offset)
    - 'col'/'col-auto' share remaining width equally
    - Breakpoint priority: xxl > xl > lg > md > sm > base
    """
    soup = BeautifulSoup(open(html_path, "r", encoding="utf-8").read(), "lxml")
    slide = LayoutSlide()

    for row in soup.select(".row"):
        cols = _direct_cols(row)
        if not cols:
            continue

        spans = []
        unspecified = []
        for idx, col in enumerate(cols):
            cls = _classes(col)
            s = resolve_span(cls)
            spans.append(s)
            if s == 0 and is_unbounded_col(cls):
                unspecified.append(idx)

        _distribute_unspecified(spans, unspecified)
        # clamp to [1..12]
        spans = [max(1, min(12, s or 1)) for s in spans]

        layout_row = LayoutRow()
        for col, span in zip(cols, spans):
            cls = _classes(col)
            layout_row.groups.append(LayoutGroup(
                span=span,
                offset=resolve_offset(cls),
                classes=cls
            ))
        slide.rows.append(layout_row)

    return slide
