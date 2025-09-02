import re
from typing import List, Optional

_COL_BP = re.compile(r"^col(?:-(sm|md|lg|xl|xxl))?-(\d{1,2})$")
_COL_AUTO = re.compile(r"^col(?:-(sm|md|lg|xl|xxl))?$")
_OFF_BP = re.compile(r"^offset(?:-(sm|md|lg|xl|xxl))?-(\d{1,2})$")

_BREAKPOINT_ORDER = ["xxl", "xl", "lg", "md", "sm", None]

def _rank(bp: Optional[str]) -> int:
    return _BREAKPOINT_ORDER.index(bp)

def resolve_span(classes: List[str]) -> int:
    """Return explicit span if any breakpointed col-*N exists; otherwise 0 (unspecified)."""
    best = None  # (bp, span)
    for cls in classes or []:
        m = _COL_BP.match(cls)
        if m:
            bp = m.group(1)
            span = max(1, min(12, int(m.group(2))))
            if best is None or _rank(bp) < _rank(best[0]):
                best = (bp, span)
    return best[1] if best else 0

def resolve_offset(classes: List[str]) -> int:
    """Return explicit offset if present (base or breakpointed); else 0."""
    best = None  # (bp, off)
    for cls in classes or []:
        m = _OFF_BP.match(cls)
        if m:
            bp = m.group(1)
            off = max(0, min(11, int(m.group(2))))
            if best is None or _rank(bp) < _rank(best[0]):
                best = (bp, off)
    return best[1] if best else 0

def is_unbounded_col(classes: List[str]) -> bool:
    """True if it's a plain 'col' or 'col-<bp>' (auto width)."""
    return any(_COL_AUTO.match(c) for c in classes or [])
