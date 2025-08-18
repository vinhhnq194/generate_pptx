# v5/main.py
import argparse
from pathlib import Path
from .renderer.render_engine import render_layout_only



HERE = Path(__file__).resolve().parent  # <-- folder containing this main.py

def _resolve(p: str) -> str:
    """Resolve path from CWD or relative to this file's directory."""
    pp = Path(p)
    if pp.exists():
        return str(pp.resolve())
    alt = HERE / p
    if alt.exists():
        return str(alt.resolve())
    raise FileNotFoundError(p)

def main():
    ap = argparse.ArgumentParser(description="v5 Layout-first Bootstrap HTML → PPTX")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--styles", default="config/styles.json")   # will resolve to v5/config/styles.json if needed
    ap.add_argument("--template", default=None)
    args = ap.parse_args()

    html = _resolve(args.html)
    styles = _resolve(args.styles)
    template = _resolve(args.template) if args.template else None

    prs = render_layout_only(html, styles, template)
    prs.save(args.out)
    print(f"Saved: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
