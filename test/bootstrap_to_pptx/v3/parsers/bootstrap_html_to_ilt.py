import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

# Compile regex to match Bootstrap column classes like col-6, col-md-4, etc.
_COL_PAT = re.compile(r"^col(?:-(?:sm|md|lg|xl|xxl))?-(\d{1,2})$")

def _is_col_class_list(classes):
    """Return the first column width found in a class list, else None."""
    logging.debug(f"Checking for column width in classes: {classes}")
    if not classes:
        return None
    for c in classes:
        m = _COL_PAT.match(c)
        if m:
            try:
                width = max(1, min(12, int(m.group(1))))
                logging.debug(f"Matched column width: {width}")
                return width
            except ValueError:
                logging.warning(f"Invalid column width in class: {c}")
                pass
    return None

@dataclass
class ILTItem:
    kind: str
    classes: List[str] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)
    col_span: int = 12
    offset: int = 0
    height_frac: Optional[float] = None
    children: List["ILTItem"] = field(default_factory=list)

@dataclass
class ILTRow:
    items: List[ILTItem] = field(default_factory=list)

@dataclass
class ILT:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    decor: List[str] = field(default_factory=list)
    rows: List[ILTRow] = field(default_factory=list)
    footer_left: Optional[str] = None

def _classes(el):
    """Get the list of CSS classes for an element."""
    cls = el.get("class", []) if el else []
    logging.debug(f"Classes for element {el}: {cls}")
    return cls

def _get_col_span(cls: List[str]) -> int:
    """Get the column span (1–12) from a list of classes."""
    logging.debug(f"Getting column span from classes: {cls}")
    w = _is_col_class_list(cls)
    if w is not None:
        return w
    for c in cls:
        if c.startswith("col-"):
            try:
                return max(1, min(12, int(c.split("-")[1])))
            except Exception:
                continue
    return 12

def _get_offset(cls: List[str]) -> int:
    """Get the column offset (0–11) from a list of classes."""
    logging.debug(f"Getting offset from classes: {cls}")
    for c in cls:
        if c.startswith("offset-"):
            try:
                return max(0, min(11, int(c.split("-")[1])))
            except:
                pass
    return 0

def _get_hfrac(cls: List[str]) -> Optional[float]:
    """Get height fraction from Bootstrap-like h-* classes."""
    logging.debug(f"Getting height fraction from classes: {cls}")
    for c in cls:
        if c.startswith("h-"):
            m = {"25": 0.25, "50": 0.5, "75": 0.75, "100": 1.0}
            val = c.split("-")[1]
            if val in m:
                return m[val]
    return None

def parse_bootstrap_html_to_ilt(html_path: str, mapping: Dict[str, str]) -> ILT:
    logging.info(f"Parsing HTML file: {html_path}")
    soup = BeautifulSoup(open(html_path, "r", encoding="utf-8").read(), "lxml")

    ilt = ILT()
    logging.debug("Created new ILT object.")

    # Decor shapes
    if soup.select_one(mapping.get("decor_diagonal", "")):
        logging.debug("Found diagonal decor.")
        ilt.decor.append("diagonal")
    if soup.select_one(mapping.get("decor_circle", "")):
        logging.debug("Found circle decor.")
        ilt.decor.append("circle")

    # Title & Subtitle
    t = soup.select_one(mapping.get("title", ""))
    s = soup.select_one(mapping.get("subtitle", ""))
    ilt.title = t.get_text(" ", strip=True) if t else None
    ilt.subtitle = s.get_text(" ", strip=True) if s else None
    logging.debug(f"Title: {ilt.title}, Subtitle: {ilt.subtitle}")

    # MAIN GRID
    main = soup.select_one(mapping.get("main_row", ""))
    if main:
        logging.debug("Found main row container.")
        cols = []
        for child in main.find_all(recursive=False):
            cls = _classes(child)
            if _is_col_class_list(cls) is not None or any(c.startswith("col-") for c in cls):
                cols.append(child)
        logging.debug(f"Identified {len(cols)} column elements.")

        # Flow-pack columns into rows
        cur_row, cur_sum = ILTRow(), 0
        for col in cols:
            cls = _classes(col)
            span = _get_col_span(cls)
            off = _get_offset(cls)
            logging.debug(f"Processing column: span={span}, offset={off}")

            item_group = ILTItem(kind="column", classes=cls, col_span=span, offset=off)

            # Narrative
            n_body = col.select_one(mapping.get("left_narrative_card_body", ""))
            if n_body:
                paras = [p.get_text(" ", strip=True) for p in n_body.select("p") if p.get_text(strip=True)]
                bullets = [li.get_text(" ", strip=True) for li in n_body.select("ul li")]
                logging.debug(f"Found narrative: {len(paras)} paragraphs, {len(bullets)} bullets.")
                item_group.children.append(ILTItem(kind="card", classes=["card", "rounded"],
                                                   content={"paragraphs": paras, "bullets": bullets}))

            # KPIs
            kpis = col.select(mapping.get("left_kpi_boxes", ""))
            if kpis:
                logging.debug(f"Found {len(kpis)} KPI boxes.")
                for sb in kpis[:3]:
                    c2 = _classes(sb)
                    headline = (sb.select_one(".fw-bold") or sb).get_text(" ", strip=True)
                    caption = (sb.select_one("small") or sb).get_text(" ", strip=True)
                    item_group.children.append(ILTItem(kind="kpi", classes=c2,
                                                       content={"headline": headline, "caption": caption}))

            # Steps
            steps_card = col.select_one(mapping.get("right_steps_card", ""))
            if steps_card:
                header = steps_card.select_one(mapping.get("right_steps_header", ""))
                items = [li.get_text(" ", strip=True) for li in steps_card.select(mapping.get("right_steps_list", ""))]
                logging.debug(f"Found steps: header={header.get_text(strip=True) if header else None}, items={len(items)}")
                item_group.children.append(ILTItem(kind="steps", classes=_classes(steps_card),
                                                   content={"header": header.get_text(" ", strip=True) if header else None,
                                                            "items": items}))

            # Icons
            icon_row = col.select_one(mapping.get("right_icon_row", ""))
            if icon_row:
                cards = icon_row.select(mapping.get("right_icon_cards", ""))
                logging.debug(f"Found {len(cards)} icon cards.")
                for c in cards[:3]:
                    caption = c.select_one(mapping.get("right_icon_caption", ""))
                    icon_i = c.select_one("i")
                    icon_name = None
                    if icon_i:
                        for cc in _classes(icon_i):
                            if cc.startswith("bi-") and cc != "bi":
                                icon_name = cc
                                break
                    item_group.children.append(ILTItem(kind="icon", classes=_classes(c),
                                                       content={"caption": caption.get_text(" ", strip=True) if caption else "",
                                                                "icon": icon_name}))

            # Outlook
            outlook = col.select(mapping.get("right_outlook_card_body", ""))
            if outlook:
                txt = " ".join(o.get_text(" ", strip=True) for o in outlook)
                logging.debug(f"Found outlook text: {txt[:50]}...")
                item_group.children.append(ILTItem(kind="outlook", classes=["card"], content={"text": txt}))

            item_group.height_frac = _get_hfrac(cls)

            # Add to current row or start a new one if overflow
            take = off + span
            if cur_sum + take > 12:
                logging.debug("Row full — starting a new row.")
                ilt.rows.append(cur_row)
                cur_row, cur_sum = ILTRow(), 0
            cur_row.items.append(item_group)
            cur_sum += take

        if cur_row.items:
            logging.debug("Adding final row to ILT.")
            ilt.rows.append(cur_row)

    # Footer
    foot = soup.select_one(mapping.get("footer_left", ""))
    ilt.footer_left = foot.get_text(" ", strip=True) if foot else None
    logging.debug(f"Footer text: {ilt.footer_left}")

    logging.info("Finished parsing HTML into ILT object.")
    return ilt
