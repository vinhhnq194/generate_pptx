from bs4 import BeautifulSoup
from .model import LayoutTree, LayoutRow, LayoutCol
from .bootstrap_norm import resolve_span, resolve_offset, is_unbounded_col

def _classes(el):
    return el.get("class", []) if el else []

def _direct_children(el):
    return el.find_all(recursive=False)

def _direct_rows(parent):
    return [c for c in _direct_children(parent) if "row" in _classes(c)]

def _direct_cols(row):
    return [c for c in _direct_children(row) if any(cc.startswith("col") for cc in _classes(c))]

def _distribute_unspecified(spans, unspecified_idx):
    total_spec = sum(s for s in spans if s > 0)
    remaining = max(0, 12 - total_spec)
    n = len(unspecified_idx)
    if n == 0:
        return
    base = max(1, remaining // n) if remaining > 0 else 1
    for i in unspecified_idx:
        spans[i] = base
    leftover = max(0, remaining - base * n)
    for j in range(min(leftover, n)):
        spans[unspecified_idx[j]] += 1

def _parse_row(row_el) -> LayoutRow:
    row = LayoutRow()
    cols = _direct_cols(row_el)
    if not cols:
        return row

    spans = []
    unspecified = []
    for idx, col in enumerate(cols):
        cls = _classes(col)
        s = resolve_span(cls)
        spans.append(s)
        if s == 0 and is_unbounded_col(cls):
            unspecified.append(idx)
    _distribute_unspecified(spans, unspecified)
    spans = [max(1, min(12, s or 1)) for s in spans]

    for col_el, span in zip(cols, spans):
        cls = _classes(col_el)
        col = LayoutCol(span=span, offset=resolve_offset(cls), classes=cls)
        # nested rows directly under this column
        for nrow in _direct_rows(col_el):
            col.rows.append(_parse_row(nrow))
        row.cols.append(col)
    return row

def parse_layout_tree(html_path: str) -> LayoutTree:
    soup = BeautifulSoup(open(html_path, "r", encoding="utf-8").read(), "lxml")
    tree = LayoutTree()

    root = soup.body if soup.body else soup
    # top-level rows: direct rows under body (or root)
    for r in _direct_rows(root):
        tree.root_rows.append(_parse_row(r))

    # fallback: if none found, allow any .row (avoids empty slides on minimal HTML)
    if not tree.root_rows:
        for r in soup.select(".row"):
            tree.root_rows.append(_parse_row(r))
            break
    return tree
