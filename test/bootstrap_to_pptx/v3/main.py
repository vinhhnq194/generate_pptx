import argparse
import json
import logging
from pathlib import Path
from parsers.html_to_layout import parse_html_to_layout
from layout.grid_solver import solve_grid_layout
from renderer.render_engine import render_slide
from renderer.render_engine import render_from_html    # new

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def load_json(p: str) -> dict:
    """Load a JSON file and return its contents."""
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded config: {p}")
        return data
    except Exception as e:
        logger.error(f"Failed to load {p}: {e}")
        raise

def main() -> None:
    """Main entry point for Bootstrap HTML to PPTX conversion (v3)."""
    parser = argparse.ArgumentParser(description="Bootstrap HTML → PPTX (v3, scalable)")
    parser.add_argument("--html", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mapping", default="config/mapping.json")
    parser.add_argument("--presets", default="config/element_presets.json")
    parser.add_argument("--overrides", default="config/layout_overrides.json")
    args = parser.parse_args()

    logger.info("Loading configs...")
    mapping = load_json(args.mapping)
    presets = load_json(args.presets)
    overrides = load_json(args.overrides)

    logger.info(f"Parsing HTML: {args.html}")
    layout_tree = parse_html_to_layout(args.html, mapping)

    logger.info("Solving grid layout...")
    grid_layout = solve_grid_layout(layout_tree, overrides)

    logger.info("Rendering PPTX...")
    prs = render_slide(grid_layout, presets, mapping)

    prs.save(args.out)
    logger.info(f"Saved PPTX: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()

# import argparse
# import json
# import logging
# from pathlib import Path

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# )
# logger = logging.getLogger(__name__)

# HERE = Path(__file__).parent.resolve()

# def _resolve(path_str: str) -> Path:
#     p = Path(path_str)
#     if p.exists():
#         return p.resolve()
#     p2 = (HERE / path_str)
#     if p2.exists():
#         return p2.resolve()
#     raise FileNotFoundError(f"File not found: {path_str}")

# def _maybe_resolve(path_str: str | None) -> Path | None:
#     if not path_str:
#         return None
#     try:
#         return _resolve(path_str)
#     except FileNotFoundError:
#         return None

# def _load_json(path_str: str) -> dict:
#     path = _resolve(path_str)
#     with path.open("r", encoding="utf-8") as f:
#         data = json.load(f)
#     logger.info(f"Loaded config: {path}")
#     return data

# def main() -> None:
#     """
#     Bootstrap HTML → PPTX (v3)
#     - scalable (default): generic Bootstrap parser → ILT → grid → presets → PPTX
#     - legacy: uses render_engine.render_slide (v2-style)
#     """
#     parser = argparse.ArgumentParser(description="Bootstrap HTML → PPTX (v3)")
#     parser.add_argument("--html", required=True, help="Path to input HTML")
#     parser.add_argument("--out", required=True, help="Path to output PPTX")
#     parser.add_argument("--pipeline", choices=["scalable", "legacy"], default="scalable")

#     # Scalable configs
#     parser.add_argument("--styles",    default="config/styles.json")
#     parser.add_argument("--presets",   default="config/element_presets.json")
#     parser.add_argument("--overrides", default="config/layout_overrides.json")
#     parser.add_argument("--template",  default=None)

#     # Legacy-only configs (kept for compatibility)
#     parser.add_argument("--mapping", default="config/mapping.json")
#     parser.add_argument("--icons",   default="config/icon_map.json")
#     parser.add_argument("--slide-num",   type=int, default=1)
#     parser.add_argument("--slide-count", type=int, default=1)

#     args = parser.parse_args()

#     html_path = _resolve(args.html)
#     out_path  = _resolve(args.out)

#     logger.info(f"Pipeline: {args.pipeline.upper()}")

#     if args.pipeline == "scalable":
#         # Import only when needed to avoid legacy import errors
#         from renderer.render_engine import render_from_html

#         styles    = _resolve(args.styles)
#         presets   = _resolve(args.presets)
#         overrides = _maybe_resolve(args.overrides)
#         template  = _maybe_resolve(args.template)

#         logger.info("Parsing + rendering via scalable pipeline…")
#         prs = render_from_html(
#             html_path=str(html_path),
#             styles_path=str(styles),
#             presets_path=str(presets),
#             overrides_path=str(overrides) if overrides else None,
#             template_path=str(template) if template else None,
#         )

#     else:
#         # LEGACY path using render_slide
#         try:
#             from renderer.render_engine import render_slide
#         except Exception as e:
#             raise RuntimeError("Legacy pipeline requires renderer.render_engine.render_slide.") from e

#         # Prefer the v2-style parser if present
#         parse_html_to_model = None
#         try:
#             from parsers.bootstrap_html_parser import parse_html_to_model  # v2 legacy
#         except Exception:
#             pass

#         if parse_html_to_model is None:
#             # As a fallback, try a v3 layout parser (only if you wrote an adapter for render_slide)
#             try:
#                 from parsers.html_to_layout import parse_html_to_layout  # v3
#             except Exception as e:
#                 raise RuntimeError(
#                     "No compatible legacy parser found. "
#                     "Expected parsers.bootstrap_html_parser.parse_html_to_model for render_slide."
#                 ) from e
#             # If you reach here, you likely need an adapter to convert layout->model.
#             raise RuntimeError(
#                 "parse_html_to_model not found. Add the v2 parser or use --pipeline scalable."
#             )

#         mapping_path = _resolve(args.mapping)
#         icons_path   = _maybe_resolve(args.icons)
#         overrides    = _maybe_resolve(args.overrides)
#         template     = _maybe_resolve(args.template)

#         logger.info("Loading mapping (legacy)…")
#         # mapping/icon files are handed to the legacy parser directly
#         model = parse_html_to_model(str(html_path), str(mapping_path), str(icons_path) if icons_path else None)

#         logger.info("Rendering PPTX via render_slide (legacy)…")
#         prs = render_slide(
#             model,
#             template_path=str(template) if template else None,
#             slide_num=args.slide_num,
#             slide_count=args.slide_count,
#             overrides_path=str(overrides) if overrides else None,
#         )

#     prs.save(str(out_path))
#     logger.info(f"Saved PPTX: {out_path}")

# if __name__ == "__main__":
#     main()
