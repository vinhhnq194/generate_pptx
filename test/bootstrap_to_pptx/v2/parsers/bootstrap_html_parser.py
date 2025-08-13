import logging
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional
from schema.slide_model import (
    SlideModel, TitleBlock, DecorShape, Narrative, KpiTile,
    StepsList, IconHighlight, Outlook, FooterBar
)

# Configure logging (you can adjust the level to INFO to reduce output)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

def _text(el) -> str:
    """Extracts text from a BeautifulSoup element, strips extra spaces."""
    logging.debug(f"Extracting text from element: {el}")
    return el.get_text(" ", strip=True) if el else ""

def _hex_for_stat_box(classes: List[str]) -> str:
    """Maps Bootstrap-like classes to color hex codes."""
    logging.debug(f"Determining color for classes: {classes}")
    if not classes:
        return "#0d6efd"
    if "bg-secondary" in classes:
        return "#6c757d"
    if "bg-dark" in classes:
        return "#212529"
    return "#0d6efd"

def parse_html_to_model(html_path: str, mapping_path: str, icon_map_path: Optional[str] = None) -> SlideModel:
    logging.info(f"Parsing HTML file: {html_path}")
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    logging.debug("HTML file loaded and parsed with BeautifulSoup.")

    logging.info(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, "r", encoding="utf-8") as f:
        sel = json.load(f)
    logging.debug(f"Mapping selectors loaded: {sel}")

    icon_map = {}
    if icon_map_path:
        logging.info(f"Attempting to load icon mapping file: {icon_map_path}")
        try:
            with open(icon_map_path, "r", encoding="utf-8") as f:
                icon_map = json.load(f)
            logging.debug(f"Icon map loaded: {icon_map}")
        except FileNotFoundError:
            logging.warning(f"Icon mapping file not found at: {icon_map_path}")

    model = SlideModel()
    logging.info("Initialized empty SlideModel.")

    # Decor shapes
    if soup.select_one(sel.get("decor_diagonal", "")):
        logging.debug("Found diagonal decor shape.")
        # model.decor.append(DecorShape(kind="diagonal"))
    if soup.select_one(sel.get("decor_circle", "")):
        logging.debug("Found circle decor shape.")
        # model.decor.append(DecorShape(kind="circle"))

    # Title & Subtitle
    title = soup.select_one(sel.get("title", ""))
    subtitle = soup.select_one(sel.get("subtitle", ""))
    model.title_block = TitleBlock(title=_text(title), subtitle=_text(subtitle))
    logging.debug(f"TitleBlock set: {model.title_block}")

    # Main content row
    main_row = soup.select_one(sel.get("main_row", ""))
    if main_row:
        logging.debug("Main row found.")

        # LEFT COLUMN - narrative
        left_col = main_row.select_one(sel.get("left_col", ""))
        if left_col:
            logging.debug("Left column found.")

            # Narrative text
            body = left_col.select_one(sel.get("left_narrative_card_body", ""))
            if body:
                logging.debug("Left narrative card body found.")
                paras = [_text(p) for p in body.select("p") if _text(p)]
                bullets = [_text(li) for li in body.select("ul li") if _text(li)]
                model.narrative = Narrative(paragraphs=paras, bullets=bullets)
                logging.debug(f"Narrative set: {model.narrative}")

            # KPI tiles
            kpis = []
            for sb in left_col.select(sel.get("left_kpi_boxes", "")):
                logging.debug(f"Processing KPI stat box: {sb}")
                headline_el = sb.select_one(".fw-bold") or sb
                caption_el = sb.select_one("small")
                headline = _text(headline_el)
                caption = _text(caption_el)
                color = _hex_for_stat_box(sb.get("class", []))
                kpis.append(KpiTile(headline=headline, caption=caption, color_hex=color))
                logging.debug(f"Added KPI tile: {headline}, {caption}, {color}")
            model.kpis = kpis

        # RIGHT COLUMN - steps, icons, outlook
        right_col = main_row.select_one(sel.get("right_col", ""))
        if right_col:
            logging.debug("Right column found.")

            # Steps section
            steps_card = right_col.select_one(sel.get("right_steps_card", ""))
            if steps_card:
                logging.debug("Steps card found.")
                header = steps_card.select_one(sel.get("right_steps_header", ""))
                items = [_text(li) for li in steps_card.select(sel.get("right_steps_list", ""))]
                model.steps = StepsList(header=_text(header), items=items)
                logging.debug(f"Steps list set: {model.steps}")

            # Icons section
            icon_cards_parent = right_col.select_one(sel.get("right_icon_row", ""))
            icon_items = []
            if icon_cards_parent:
                logging.debug("Icon cards parent found.")
                for card in icon_cards_parent.select(sel.get("right_icon_cards", "")):
                    caption = card.select_one(sel.get("right_icon_caption", "")) or None
                    icon_i = card.select_one("i")
                    icon_name = None
                    if icon_i:
                        for c in icon_i.get("class", []):
                            if c.startswith("bi-") and c != "bi":
                                icon_name = c
                                break
                    icon_items.append(IconHighlight(icon_name=icon_name, caption=_text(caption)))
                    logging.debug(f"Added IconHighlight: {icon_name}, {caption}")
            model.icon_highlights = icon_items

            # Outlook section
            outlook_ps = right_col.select(sel.get("right_outlook_card_body", ""))
            if outlook_ps:
                outlook_text = " ".join(_text(p) for p in outlook_ps)
                model.outlook = Outlook(text=outlook_text)
                logging.debug(f"Outlook set: {model.outlook}")

    # Footer section
    footer = soup.select_one(sel.get("footer_bar", ""))
    if footer:
        logging.debug("Footer found.")
        left = soup.select_one(sel.get("footer_left", ""))
        right = soup.select_one(sel.get("footer_right", ""))
        model.footer = FooterBar(left_text=_text(left), right_text=_text(right))
        logging.debug(f"Footer set: {model.footer}")

    logging.info("HTML parsing completed. Returning SlideModel.")
    return model