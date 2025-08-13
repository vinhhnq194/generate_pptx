import argparse, json, os
from pathlib import Path
from renderer.pipeline import build_deck_from_html

HERE = Path(__file__).parent

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--styles", default=str(HERE/"config"/"styles.json"))
    p.add_argument("--presets", default=str(HERE/"config"/"element_presets.json"))
    p.add_argument("--overrides", default=str(HERE/"config"/"layout_overrides.json"))
    p.add_argument("--template", default=None)
    args = p.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        alt = HERE / args.html
        if alt.exists(): html_path = alt
        else: raise FileNotFoundError(html_path)

    prs = build_deck_from_html(
        html_path=str(html_path),
        styles_path=args.styles,
        presets_path=args.presets,
        overrides_path=args.overrides if os.path.exists(args.overrides) else None,
        template_path=args.template
    )
    prs.save(args.out)
    print(f"[OK] Saved: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
