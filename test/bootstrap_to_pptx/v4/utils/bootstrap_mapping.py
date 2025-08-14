from dataclasses import dataclass
from typing import List, Optional
from pptx.dml.color import RGBColor
from pptx.util import Pt

BOOTSTRAP_COLORS = {
    "primary":  RGBColor(0x0D, 0x6E, 0xFD),
    "secondary":RGBColor(0x6C, 0x75, 0x7D),
    "success":  RGBColor(0x19, 0x87, 0x54),
    "danger":   RGBColor(0xDC, 0x35, 0x45),
    "warning":  RGBColor(0xFF, 0xC1, 0x07),
    "info":     RGBColor(0x0D, 0xCA, 0xF0),
    "light":    RGBColor(0xF8, 0xF9, 0xFA),
    "dark":     RGBColor(0x21, 0x25, 0x29),
}

@dataclass
class ParsedUtils:
    bg: Optional[str] = None
    border: Optional[int] = None
    border_zero: bool = False
    rounded: bool = False
    fw_bold: bool = False
    fst_italic: bool = False
    text_uppercase: bool = False
    text_color: Optional[str] = None

def parse_bootstrap_utils(classes: List[str]) -> ParsedUtils:
    p = ParsedUtils()
    for c in classes or []:
        if c == "border-0": p.border_zero = True
        elif c.startswith("border-"):
            try: p.border = int(c.split("-")[1])
            except: pass
        elif c == "rounded": p.rounded = True
        elif c == "fw-bold": p.fw_bold = True
        elif c == "fst-italic": p.fst_italic = True
        elif c == "text-uppercase": p.text_uppercase = True
        elif c.startswith("bg-"):
            key = c[3:]; 
            if key in BOOTSTRAP_COLORS: p.bg = key
        elif c.startswith("text-"):
            key = c[5:];
            if key in BOOTSTRAP_COLORS: p.text_color = key
    return p

def apply_shape_appearance_from_bootstrap(shape, classes: List[str]):
    p = parse_bootstrap_utils(classes)
    if p.bg:
        shape.fill.solid(); shape.fill.fore_color.rgb = BOOTSTRAP_COLORS[p.bg]
    if p.border_zero:
        try: shape.line.fill.background()
        except: pass
    else:
        from pptx.dml.color import RGBColor
        shape.line.color.rgb = RGBColor(0xDE,0xE2,0xE6)
        if p.border:
            width_map = {1:0.75,2:1.0,3:1.5,4:2.0,5:3.0}
            shape.line.width = Pt(width_map.get(p.border, 0.75))
    if p.rounded:
        try: shape.adjustments[0] = 0.16
        except: pass
