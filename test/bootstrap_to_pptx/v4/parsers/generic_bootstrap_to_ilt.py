from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re

@dataclass
class ILTItem:
    kind: str                      # card, kpi, steps, icon, table, image, chart, text
    classes: List[str] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)
    col_span: int = 12
    offset: int = 0
    h_frac: Optional[float] = None

@dataclass
class ILTRow:
    items: List[ILTItem] = field(default_factory=list)

@dataclass
class ILT:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    rows: List[ILTRow] = field(default_factory=list)
    footer_left: Optional[str] = None

_COL_PAT = re.compile(r"^col(?:-(?:sm|md|lg|xl|xxl))?-(\d{1,2})$")

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

def parse_generic_bootstrap_to_ilt(html_path: str) -> ILT:
    soup = BeautifulSoup(open(html_path,"r",encoding="utf-8").read(), "lxml")
    ilt = ILT()

    # title/subtitle (best-effort)
    t = soup.select_one("h1, h2.fw-bold, h2")
    s = soup.select_one("p.lead, p.text-muted, h3, h4")
    ilt.title = t.get_text(" ", strip=True) if t else None
    ilt.subtitle = s.get_text(" ", strip=True) if s else None

    for row in soup.select(".row"):
        direct_cols = [c for c in row.find_all(recursive=False) if any(cc.startswith("col-") for cc in _classes(c))]
        if not direct_cols: 
            continue
        ilt_row = ILTRow()
        for col in direct_cols:
            cls = _classes(col)
            col_span, off, hfrac = _col_span(cls), _offset(cls), _hfrac(cls)

            # gather items
            inner_items: List[ILTItem] = []

            # cards (narrative)
            for card in col.select(".card"):
                body = card.select_one(".card-body")
                if body:
                    paras = [p.get_text(" ", strip=True) for p in body.select("p")]
                    bullets = [li.get_text(" ", strip=True) for li in body.select("ul li, ol li")]
                    if paras or bullets:
                        inner_items.append(ILTItem(kind="card", classes=_classes(card),
                                                   content={"paragraphs": paras, "bullets": bullets}))

            # KPI-ish tiles
            for sb in col.select(".stat-box, .kpi, .tile"):
                headline = (sb.select_one(".fw-bold, .fs-3") or sb).get_text(" ", strip=True)
                small = sb.select_one("small")
                caption = small.get_text(" ", strip=True) if small else ""
                inner_items.append(ILTItem(kind="kpi", classes=_classes(sb),
                                           content={"headline": headline, "caption": caption}))

            # steps (ol)
            ol = col.select_one("ol")
            if ol and ol.select("li"):
                items = [li.get_text(" ", strip=True) for li in ol.select("li")]
                header_el = col.select_one(".card-header")
                header = header_el.get_text(" ", strip=True) if header_el else None
                inner_items.append(ILTItem(kind="steps", classes=_classes(ol), content={"header": header, "items": items}))

            # icons
            for icard in col.select(".card"):
                if icard.select_one("i"):
                    cap = icard.select_one("p, .small, .caption")
                    if cap:
                        icon_el = icard.select_one("i[class*='bi-'], i[class*='fa-']")
                        icon_name = None
                        if icon_el:
                            for cc in _classes(icon_el):
                                if cc.startswith(("bi-","fa-")) and cc not in ("bi","fa","fas","far"):
                                    icon_name = cc; break
                        inner_items.append(ILTItem(kind="icon", classes=_classes(icard),
                                                   content={"caption": cap.get_text(' ', strip=True), "icon": icon_name}))

            # tables
            for tb in col.select("table"):
                rows_data = []
                for tr in tb.select("tr"):
                    cells = [c.get_text(" ", strip=True) for c in tr.select("th, td")]
                    if cells: rows_data.append(cells)
                if rows_data:
                    inner_items.append(ILTItem(kind="table", classes=_classes(tb), content={"rows": rows_data}))

            # images
            for img in col.select("img[src]"):
                inner_items.append(ILTItem(kind="image", classes=_classes(img), content={"src": img["src"]}))

            # chart placeholder
            chart = col.select_one("[data-chart], .chart")
            if chart:
                spec = chart.get("data-chart", "{}")
                inner_items.append(ILTItem(kind="chart", classes=_classes(chart), content={"spec": spec}))

            if not inner_items:
                # fallback to plain text
                txt = col.get_text(" ", strip=True)
                if txt:
                    inner_items.append(ILTItem(kind="text", classes=cls, content={"text": txt}))

            # Append all inner items as independent slots within this column (simple approach)
            for it in inner_items:
                it.col_span, it.offset, it.h_frac = col_span, off, hfrac
                ilt_row.items.append(it)

        if ilt_row.items:
            ilt.rows.append(ilt_row)

    foot = soup.select_one(".footer, .footer-bar, footer")
    if foot:
        ilt.footer_left = foot.get_text(" ", strip=True)
    return ilt
