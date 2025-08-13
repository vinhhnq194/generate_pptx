from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re

@dataclass
class ILTItem:
    kind: str                      # "card", "kpi", "steps", "icon", "table", "image", "chart", "text"
    classes: List[str] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)   # text, bullets, src, table, chart spec
    col_span: int = 12
    offset: int = 0
    h_frac: Optional[float] = None # 0.25/0.5/0.75/1.0

@dataclass
class ILTRow:
    items: List[ILTItem] = field(default_factory=list)

@dataclass
class ILTSlide:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    rows: List[ILTRow] = field(default_factory=list)
    footer_left: Optional[str] = None
    decor: List[str] = field(default_factory=list)

_COL_PAT = re.compile(r"^col(?:-(?:sm|md|lg|xl|xxl))?-(\d{1,2})$")
_REM = {0:0.0,1:0.25,2:0.5,3:1.0,4:1.5,5:3.0}

def _classes(el): return el.get("class", []) if el else []

def _col_span(cls: List[str]) -> int:
    for c in cls:
        m = _COL_PAT.match(c)
        if m:
            w = int(m.group(1))
            return max(1, min(12, w))
    return 12

def _offset(cls: List[str]) -> int:
    for c in cls:
        if c.startswith("offset-"):
            try: return max(0, min(11, int(c.split("-")[1])))
            except: pass
    return 0

def _hfrac(cls: List[str]) -> Optional[float]:
    for c in cls:
        if c.startswith("h-"):
            m = {"25":0.25,"50":0.5,"75":0.75,"100":1.0}
            v = c.split("-")[1]
            if v in m: return m[v]
    return None

def parse_generic_bootstrap_to_ilt(html_path: str) -> ILTSlide:
    soup = BeautifulSoup(open(html_path,"r",encoding="utf-8").read(), "lxml")
    ilt = ILTSlide()

    # try common title/subtitle patterns
    t = soup.select_one("h1, h2.fw-bold, h2")
    s = soup.select_one("p.lead, p.text-muted, h3, h4")
    ilt.title = t.get_text(" ", strip=True) if t else None
    ilt.subtitle = s.get_text(" ", strip=True) if s else None

    # each .row creates a new ILTRow, packing direct .col-* children
    for row in soup.select(".row"):
        direct_cols = [c for c in row.find_all(recursive=False) if any(cc.startswith("col-") for cc in _classes(c))]
        if not direct_cols: 
            continue
        ilt_row = ILTRow()
        for col in direct_cols:
            cls = _classes(col)
            group = ILTItem(kind="column", classes=cls, col_span=_col_span(cls), offset=_offset(cls), h_frac=_hfrac(cls))
            # discover items inside the column:

            # 1) cards of text (narrative, generic)
            for card in col.select(".card"):
                body = card.select_one(".card-body")
                if body:
                    paras = [p.get_text(" ", strip=True) for p in body.select("p")]
                    bullets = [li.get_text(" ", strip=True) for li in body.select("ul li, ol li")]
                    if paras or bullets:
                        group_item = ILTItem(kind="card", classes=_classes(card),
                                             content={"paragraphs": paras, "bullets": bullets})
                        ilt_row.items.append(group_item)

            # 2) KPI / stat-box style (solid tiles with headline+small)
            for sb in col.select(".stat-box, .kpi, .tile"):
                headline = (sb.select_one(".fw-bold, .fs-3") or sb).get_text(" ", strip=True)
                small = sb.select_one("small")
                caption = small.get_text(" ", strip=True) if small else ""
                ilt_row.items.append(ILTItem(kind="kpi", classes=_classes(sb), content={"headline": headline, "caption": caption}))

            # 3) steps (numbered list)
            ol = col.select_one("ol")
            if ol and ol.select("li"):
                items = [li.get_text(" ", strip=True) for li in ol.select("li")]
                header = None
                # if there's a card-header near it
                header_el = col.select_one(".card-header")
                if header_el:
                    header = header_el.get_text(" ", strip=True)
                ilt_row.items.append(ILTItem(kind="steps", classes=_classes(ol), content={"header": header, "items": items}))

            # 4) icon cards
            for icard in col.select(".card:has(i), .text-center:has(i)"):
                cap = icard.select_one("p, .small, .caption")
                icon_el = icard.select_one("i[class*='bi-'], i[class*='fa-']")
                if cap:
                    icon_name = None
                    if icon_el:
                        for cc in _classes(icon_el):
                            if cc.startswith(("bi-","fa-")) and cc not in ("bi","fa","fas","far"):
                                icon_name = cc
                                break
                    ilt_row.items.append(ILTItem(kind="icon", classes=_classes(icard),
                                                 content={"caption": cap.get_text(' ', strip=True), "icon": icon_name}))

            # 5) tables
            for tb in col.select("table"):
                rows = []
                for tr in tb.select("tr"):
                    cells = [c.get_text(" ", strip=True) for c in tr.select("th, td")]
                    if cells: rows.append(cells)
                if rows:
                    ilt_row.items.append(ILTItem(kind="table", classes=_classes(tb), content={"rows": rows}))

            # 6) images
            for img in col.select("img[src]"):
                ilt_row.items.append(ILTItem(kind="image", classes=_classes(img), content={"src": img["src"]}))

            # 7) charts (placeholder: data-chart JSON or .chart class)
            chart = col.select_one("[data-chart], .chart")
            if chart:
                spec = chart.get("data-chart", "{}")
                ilt_row.items.append(ILTItem(kind="chart", classes=_classes(chart), content={"spec": spec}))

            # If column is empty of known items, keep it as a 'text' block from direct text
            if not any(i for i in ilt_row.items):
                txt = col.get_text(" ", strip=True)
                if txt:
                    ilt_row.items.append(ILTItem(kind="text", classes=cls, content={"text": txt}))

        if ilt_row.items:
            ilt.rows.append(ilt_row)

    # footer guess
    foot = soup.select_one(".footer, .footer-bar, footer")
    if foot:
        ilt.footer_left = foot.get_text(" ", strip=True)
    return ilt
