import logging
from pptx.util import Inches
from pptx.enum.text import MSO_AUTO_SIZE
from .elements import add_card, add_card_header, add_text, add_bullets, add_kpi_tile
from utils.bootstrap_mapping import apply_shape_appearance_from_bootstrap, apply_run_from_bootstrap
from utils.text_fit import wrap_text

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def build_column_contents(slide, rect, ilt_group, styles, icon_map, grid):
    """
    Create shapes inside this column group (card/kpi/steps/icons/outlook) and apply bootstrap mapping.
    """
    logging.info("=== Building column contents ===")
    logging.debug(f"Slide: {slide}, Rect: {rect}, ILT Group: {ilt_group.kind if hasattr(ilt_group, 'kind') else 'N/A'}")

    # Extract position and size from rect
    x, y, w, h = rect.left, rect.top, rect.width, rect.height
    y_cursor = y
    logging.debug(f"Initial position: x={x}, y={y}, width={w}, height={h}")

    # 1) Card narrative
    card_items = [c for c in ilt_group.children if c.kind == "card"]
    logging.debug(f"Found {len(card_items)} narrative card items.")
    if card_items:
        card_h = h * 0.68 if any(c.kind == "kpi" for c in ilt_group.children) else h
        logging.debug(f"Card height set to {card_h} inches.")
        card = add_card(slide, x, y_cursor, w, card_h, radius=True, shadow=True)
        logging.debug("Added card shape to slide.")
        apply_shape_appearance_from_bootstrap(card, ilt_group.classes)
        logging.debug("Applied Bootstrap styling to card.")

        content = card_items[0].content
        paras = content.get("paragraphs", [])
        bullets = content.get("bullets", [])
        logging.debug(f"Paragraph count: {len(paras)}, Bullet count: {len(bullets)}")

        tx, ty, tw = x + 0.3, y_cursor + 0.3, w - 0.6
        for i, p in enumerate(paras):
            logging.debug(f"Adding paragraph {i+1}: {p}")
            add_text(slide, tx, ty + i*0.38, tw, 0.34, p, size=styles["narrative"]["body_size_pt"])
        if bullets:
            logging.debug("Adding bullets to narrative card.")
            add_bullets(slide, tx, ty + 0.38*max(1, len(paras)), tw, 0.9, bullets,
                        size=styles["narrative"]["bullets_size_pt"])
        y_cursor += card_h + 0.25
        logging.debug(f"y_cursor moved to {y_cursor}")

    # 2) KPIs
    kpis = [c for c in ilt_group.children if c.kind == "kpi"]
    logging.debug(f"Found {len(kpis)} KPI tiles.")
    if kpis:
        gutter = styles["kpi"]["gap_in"]
        tile_w = (w - 2*gutter) / 3.0
        tile_h = styles["kpi"]["height_in"]
        for i, k in enumerate(kpis[:3]):
            caption = wrap_text(k.content.get("caption", ""), limit=styles["kpi"]["wrap_limit"])
            headline = k.content.get("headline", "")
            col = "primary"
            for cls in k.classes:
                if cls.startswith("bg-"):
                    col = cls.replace("bg-", "")
            logging.debug(f"Adding KPI tile {i+1}: headline={headline}, caption={caption}, color={col}")
            add_kpi_tile(slide, x + i*(tile_w + gutter), y_cursor, tile_w, tile_h,
                         headline=headline, caption=caption,
                         bg_hex="#" + "".join(f"{c:02x}" for c in (0x0D, 0x6E, 0xFD)))
        y_cursor += styles["kpi"]["height_in"] + styles["icons"]["gap_below_in"]
        logging.debug(f"y_cursor moved to {y_cursor}")

    # 3) Steps
    steps = [c for c in ilt_group.children if c.kind == "steps"]
    logging.debug(f"Found {len(steps)} step sections.")
    if steps:
        steps_h = h * styles["steps"]["height_ratio"]
        logging.debug(f"Steps card height: {steps_h}")
        card = add_card(slide, x, y_cursor, w, steps_h, radius=True, shadow=True)
        header = steps[0].content.get("header", "Steps")
        logging.debug(f"Adding steps card header: {header}")
        add_card_header(slide, card, header)
        tb = add_bullets(slide, x+0.3, y_cursor+0.7, w-0.6, steps_h-0.9,
                         steps[0].content.get("items", []), size=styles["steps"]["items_pt"], numbered=True)
        tb.text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        logging.debug("Steps bullets added with auto-size to fit text.")
        y_cursor += steps_h + styles["steps"]["gap_below_in"]
        logging.debug(f"y_cursor moved to {y_cursor}")

    # 4) Icons
    icons = [c for c in ilt_group.children if c.kind == "icon"]
    logging.debug(f"Found {len(icons)} icon items.")
    if icons:
        gutter = styles["icons"]["gap_in"]
        tile_w = (w - 2*gutter) / 3.0
        tile_h = styles["icons"]["height_in"]
        for i, ic in enumerate(icons[:3]):
            logging.debug(f"Adding icon {i+1}: caption={ic.content.get('caption', '')}")
            card = add_card(slide, x + i*(tile_w + gutter), y_cursor, tile_w, tile_h, radius=True, shadow=True)
            add_text(slide, x + i*(tile_w + gutter) + 0.2, y_cursor + 0.8, tile_w-0.4, 0.6,
                     ic.content.get("caption", ""), size=styles["icons"]["caption_pt"])
        y_cursor += tile_h + styles["icons"]["gap_below_in"]
        logging.debug(f"y_cursor moved to {y_cursor}")

    # 5) Outlook
    outlooks = [c for c in ilt_group.children if c.kind == "outlook"]
    logging.debug(f"Found {len(outlooks)} outlook sections.")
    if outlooks:
        out_h = max(styles["outlook"]["min_height_in"], (y + h) - y_cursor)
        logging.debug(f"Outlook card height: {out_h}")
        card = add_card(slide, x, y_cursor, w, out_h, radius=True, shadow=True)
        add_text(slide, x+0.3, y_cursor+0.3, w-0.6, out_h-0.6,
                 outlooks[0].content.get("text", ""), size=styles["outlook"]["body_pt"])
        logging.debug("Outlook text added.")

    logging.info("=== Finished building column contents ===")
