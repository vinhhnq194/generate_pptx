from bs4 import BeautifulSoup
from utils.log import logger

def parse_html_to_layout(html_path, mapping):
    logger.info("Reading HTML file...")
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = []
    for row in soup.select(".row"):
        cols = row.find_all(class_=lambda c: c and c.startswith("col-"), recursive=False)
        row_data = []
        for col in cols:
            # Detect element type (card, kpi, table, etc.)
            el_type = infer_element_type(col, mapping)
            row_data.append({
                "type": el_type,
                "content": col,
                "bootstrap_classes": col.get("class", [])
            })
        rows.append(row_data)
    logger.info(f"Detected {len(rows)} rows.")
    return rows

def infer_element_type(col, mapping):
    # Simple heuristic: check for known Bootstrap classes
    classes = col.get("class", [])
    for el_type, triggers in mapping.get("element_triggers", {}).items():
        if any(cls in classes for cls in triggers):
            return el_type
    return "text"