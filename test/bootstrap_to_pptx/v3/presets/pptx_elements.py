import logging
from typing import Any, Dict
from pptx.util import Inches

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_element(prs: Any, slide: Any, element: Dict[str, Any], preset: Dict[str, Any], mapping: dict) -> None:
    """
    Create a pptx element on the slide using the preset and mapping.
    """
    logger.info(f"Creating element: {element['type']}")
    # Example for card/text
    if element["type"] == "card":
        shape = slide.shapes.add_shape(
            preset.get("shape_type", 1),
            Inches(element["position"]["left"]),
            Inches(element["position"]["top"]),
            Inches(element["position"]["width"]),
            Inches(element["position"]["height"])
        )
        apply_styles(shape, element, mapping)
    # Add more types as needed

def apply_styles(shape: Any, element: Dict[str, Any], mapping: dict) -> None:
    """
    Apply styles to a pptx shape using the mapping.
    """
    logger.debug(f"Applying styles for element: {element['type']}")
    # ...style logic...