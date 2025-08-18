import re
from typing import List, Optional

_COL_BP = re.compile(r"^col(?:-(sm|md|lg|xl|xxl))?-(\d{1,2})$")
_BREAKPOINT_ORDER = ["xxl", "xl", "lg", "md", "sm", None]

def _bp_rank(bp: Optional[str]) -> int:
    return _BREAKPOINT_ORDER.index(bp)

def resolve_span(classes: List[str]) -> int:
    """
    Pick the span for the most specific breakpoint defined.
    Returns 0 if only 'col'/'col-auto' was used (unspecified), to be distributed later.
    """
    best = None  # (bp, span)
    for cls in classes or []:
        m = _COL_BP.match(cls)
        if m:
            bp = m.group(1)
            span = max(1, min(12, int(m.group(2))))
            if best is None or _bp_rank(bp) < _bp_rank(best[0]):
                best = (bp, span)
    return best[1] if best else 0

def resolve_offset(classes: List[str]) -> int:
    for cls in classes or []:
        if cls.startswith("offset-"):
            try:
                return max(0, min(11, int(cls.split("-")[1])))
            except Exception:
                pass
    return 0

def is_unbounded_col(classes: List[str]) -> bool:
    """True if it's a plain 'col' or 'col-auto' (no explicit span)."""
    return ("col" in classes) or ("col-auto" in classes)
