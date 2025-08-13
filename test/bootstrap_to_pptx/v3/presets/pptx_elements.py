from pptx import Presentation
from pptx.util import Inches, Pt
from utils.log import logger

def create_element(prs, slide, element, preset, mapping):
    logger.info(f"Creating element: {element['type']}")
    # Use preset for geometry and style
    # Example for card/text
    if element["type"] == "card":
        shape = slide.shapes.add_shape(
            preset["shape_type"],
            Inches(element["position"]["left"]),
            Inches(element["position"]["top"]),
            Inches(element["position"]["width"]),
            Inches(element["position"]["height"])
        )
        apply_styles(shape, element, mapping)
    # Add more types (kpi, table, image, chart, text) as needed

def apply_styles(shape, element, mapping):
    # Use mapping to set fill, border, font, etc.
    pass