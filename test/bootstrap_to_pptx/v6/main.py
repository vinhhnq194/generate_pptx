import argparse
from pathlib import Path
from v6.renderer.render_engine import render_layout_only

HERE = Path(__file__).resolve().parent

def _resolve(p: str) -> str:
    pp = Path(p)
    if pp.exists():
        return str(pp.resolve())
    alt = HERE / p
    if alt.exists():
        return str(alt.resolve())
    raise FileNotFoundError(p)

def main():
    ap = argparse.ArgumentParser(description="v6 Layout-first (hierarchical) Bootstrap HTML → PPTX")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--styles", default="config/styles.json")
    ap.add_argument("--template", default=None)
    args = ap.parse_args()

    html = _resolve(args.html)
    styles = _resolve(args.styles)
    template = _resolve(args.template) if args.template else None

    prs = render_layout_only(html_path=html, styles_path=styles, template_path=template)
    prs.save(args.out)
    print(f"Saved: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
