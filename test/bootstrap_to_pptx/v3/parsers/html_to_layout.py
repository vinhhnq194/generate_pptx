import logging
from typing import Any, List
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def parse_html_to_layout(html_path: str, mapping: dict) -> List[Any]:
    """
    Parse HTML file and return a layout tree of rows and columns.
    """
    logger.info(f"Reading HTML file: {html_path}")
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = []
    for row in soup.select(".row"):
        cols = row.find_all(class_=lambda c: c and c.startswith("col-"), recursive=False)
        row_data = []
        for col in cols:
            el_type = infer_element_type(col, mapping)
            row_data.append({
                "type": el_type,
                "content": col,
                "bootstrap_classes": col.get("class", [])
            })
        rows.append(row_data)
    logger.info(f"Detected {len(rows)} rows.")
    return rows

def infer_element_type(col: Any, mapping: dict) -> str:
    """
    Infer the element type (card, kpi, table, etc.) from Bootstrap classes.
    """
    classes = col.get("class", [])
    for el_type, triggers in mapping.get("element_triggers", {}).items():
        if any(cls in classes for cls in triggers):
            logger.debug(f"Element type '{el_type}' detected for classes: {classes}")
            return el_type
    return "text"