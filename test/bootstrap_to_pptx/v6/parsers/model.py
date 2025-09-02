from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LayoutRow:
    cols: List["LayoutCol"] = field(default_factory=list)

@dataclass
class LayoutCol:
    span: int
    offset: int = 0
    classes: List[str] = field(default_factory=list)
    rows: List[LayoutRow] = field(default_factory=list)  # nested rows

@dataclass
class LayoutTree:
    root_rows: List[LayoutRow] = field(default_factory=list)
    title: Optional[str] = None
    subtitle: Optional[str] = None
