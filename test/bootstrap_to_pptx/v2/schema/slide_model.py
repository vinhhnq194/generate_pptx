import logging
from dataclasses import dataclass, field
from typing import List, Optional

# Configure logging (adjust level as needed in main app)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

@dataclass
class TitleBlock:
    title: Optional[str] = None
    subtitle: Optional[str] = None

    def __post_init__(self):
        logging.debug(f"TitleBlock created: title='{self.title}', subtitle='{self.subtitle}'")

@dataclass
class Narrative:
    paragraphs: List[str] = field(default_factory=list)
    bullets: List[str] = field(default_factory=list)

    def __post_init__(self):
        logging.debug(f"Narrative created: {len(self.paragraphs)} paragraphs, {len(self.bullets)} bullets")

@dataclass
class KpiTile:
    headline: str
    caption: str
    color_hex: str = "#0d6efd"

    def __post_init__(self):
        logging.debug(f"KpiTile created: headline='{self.headline}', caption='{self.caption}', color_hex='{self.color_hex}'")

@dataclass
class StepsList:
    header: Optional[str] = None
    items: List[str] = field(default_factory=list)

    def __post_init__(self):
        logging.debug(f"StepsList created: header='{self.header}', items={len(self.items)}")

@dataclass
class IconHighlight:
    icon_name: Optional[str] = None
    caption: str = ""

    def __post_init__(self):
        logging.debug(f"IconHighlight created: icon_name='{self.icon_name}', caption='{self.caption}'")

@dataclass
class Outlook:
    text: str = ""

    def __post_init__(self):
        logging.debug(f"Outlook created: text='{self.text[:50]}{'...' if len(self.text) > 50 else ''}'")

@dataclass
class FooterBar:
    left_text: str = ""
    right_text: str = ""

    def __post_init__(self):
        logging.debug(f"FooterBar created: left_text='{self.left_text}', right_text='{self.right_text}'")

@dataclass
class DecorShape:
    kind: str  # "diagonal" or "circle"

    def __post_init__(self):
        logging.debug(f"DecorShape created: kind='{self.kind}'")

@dataclass
class SlideModel:
    title_block: TitleBlock = field(default_factory=TitleBlock)
    decor: List[DecorShape] = field(default_factory=list)
    narrative: Optional[Narrative] = None
    kpis: List[KpiTile] = field(default_factory=list)
    steps: Optional[StepsList] = None
    icon_highlights: List[IconHighlight] = field(default_factory=list)
    outlook: Optional[Outlook] = None
    footer: Optional[FooterBar] = None

    def __post_init__(self):
        logging.debug(
            f"SlideModel created: title_block={self.title_block}, "
            f"decor_count={len(self.decor)}, "
            f"narrative={'present' if self.narrative else 'none'}, "
            f"kpis_count={len(self.kpis)}, "
            f"steps={'present' if self.steps else 'none'}, "
            f"icons_count={len(self.icon_highlights)}, "
            f"outlook={'present' if self.outlook else 'none'}, "
            f"footer={'present' if self.footer else 'none'}"
        )
