import argparse, os
from pathlib import Path
from parsers.bootstrap_html_parser import parse_html_to_model
from renderer.render_engine import render_slide

HERE = Path(__file__).parent

def main():
    p = argparse.ArgumentParser(description="Convert Bootstrap HTML to PPTX (v2)")
    p.add_argument("--html", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--template", default=None)
    p.add_argument("--mapping", default=str(HERE / "config" / "mapping.json"))
    p.add_argument("--icons", default=str(HERE / "config" / "icon_map.json"))
    p.add_argument("--overrides", default=str(HERE / "config" / "layout_overrides.json"))
    p.add_argument("--slide-num", type=int, default=1)
    p.add_argument("--slide-count", type=int, default=1)
    args = p.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        alt = HERE / args.html
        if alt.exists():
            html_path = alt
        else:
            raise FileNotFoundError(html_path)

    model = parse_html_to_model(str(html_path), args.mapping, args.icons)
    prs = render_slide(model, template_path=args.template,
                       slide_num=args.slide_num, slide_count=args.slide_count,
                       overrides_path=args.overrides)
    prs.save(args.out)
    print(f"[OK] Saved: {Path(args.out).resolve()}")


# import argparse, os, json
# from pathlib import Path
# from parsers.bootstrap_html_parser import parse_html_to_model  # legacy
# from renderer.render_engine import render_slide               # legacy
# from renderer.render_engine import render_from_html           # NEW ILT pipeline

# HERE = Path(__file__).parent

# def load_json(p):
#     with open(p, "r", encoding="utf-8") as f:
#         return json.load(f)

# def main():
#     p = argparse.ArgumentParser(description="Convert Bootstrap HTML to PPTX (v2)")
#     p.add_argument("--html", required=True)
#     p.add_argument("--out", required=True)
#     p.add_argument("--template", default=None)
#     p.add_argument("--mapping", default=str(HERE / "config" / "mapping.json"))
#     p.add_argument("--icons", default=str(HERE / "config" / "icon_map.json"))
#     p.add_argument("--styles", default=str(HERE / "config" / "styles.json"))
#     p.add_argument("--overrides", default=str(HERE / "config" / "layout_overrides.json"))
#     p.add_argument("--slide-num", type=int, default=1)
#     p.add_argument("--slide-count", type=int, default=1)
#     p.add_argument("--pipeline", choices=["ilt","legacy"], default="ilt",
#                    help="ilt = new Intermediate Layout Tree flow (default); legacy = old SlideModel flow")
#     args = p.parse_args()

#     html_path = Path(args.html)
#     if not html_path.exists():
#         alt = HERE / args.html
#         if alt.exists(): html_path = alt
#         else: raise FileNotFoundError(html_path)

#     if args.pipeline == "ilt":
#         print("[pipeline] ILT")
#         styles = load_json(args.styles)
#         overrides = load_json(args.overrides) if os.path.exists(args.overrides) else {}
#         prs = render_from_html(
#             html_path=str(html_path),
#             mapping_path=args.mapping,
#             styles=styles,
#             overrides=overrides,
#             template_path=args.template,
#         )
#     else:
#         print("[pipeline] LEGACY")
#         model = parse_html_to_model(str(html_path), args.mapping, args.icons)
#         prs = render_slide(
#             model,
#             template_path=args.template,
#             slide_num=args.slide_num,
#             slide_count=args.slide_count,
#             overrides_path=args.overrides,
#         )

#     prs.save(args.out)
#     print(f"[OK] Saved: {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
