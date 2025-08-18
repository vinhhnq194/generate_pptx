from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LayoutGroup:
    """One Bootstrap column group inside a row (proportional only)."""
    span: int               # 1..12 (0 means unspecified; should be resolved before use)
    offset: int = 0         # 0..11
    classes: List[str] = field(default_factory=list)  # keep classes for later content/styling

@dataclass
class LayoutRow:
    groups: List[LayoutGroup] = field(default_factory=list)

@dataclass
class LayoutSlide:
    rows: List[LayoutRow] = field(default_factory=list)
    title: Optional[str] = None
    subtitle: Optional[str] = None
