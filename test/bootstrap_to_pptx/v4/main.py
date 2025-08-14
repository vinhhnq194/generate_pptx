import argparse
import logging
from pathlib import Path

from renderer.render_engine import render_from_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("v4")

HERE = Path(__file__).resolve().parent

def _resolve(p: str) -> str:
    pp = Path(p)
    if pp.exists(): return str(pp.resolve())
    alt = HERE / p
    if alt.exists(): return str(alt.resolve())
    raise FileNotFoundError(p)

def main():
    ap = argparse.ArgumentParser(description="Bootstrap HTML → PPTX (v4)")
    ap.add_argument("--html", required=True, help="Input HTML file")
    ap.add_argument("--out", required=True, help="Output PPTX file")
    ap.add_argument("--styles", default="config/styles.json")
    ap.add_argument("--presets", default="config/element_presets.json")
    ap.add_argument("--template", default=None, help="Optional POTX/PPTX template")
    args = ap.parse_args()

    html = _resolve(args.html)
    styles = _resolve(args.styles)
    presets = _resolve(args.presets)
    template = str(Path(args.template).resolve()) if args.template else None

    prs = render_from_html(html_path=html, styles_path=styles, presets_path=presets, template_path=template)
    prs.save(args.out)
    log.info(f"Saved: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
