# Bootstrap HTML → PPTX (v2)

A modular, maintainable pipeline:

1) **Parse** HTML (Bootstrap) → semantic **SlideModel** (Python objects).
2) **Render** SlideModel → PPTX using `python-pptx`.

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Example:
python main.py --html "/mnt/data/test.html" --out "consulting_slide.pptx"

# Customize
config/mapping.json: CSS selectors → semantic roles.
config/icon_map.json: icon names → local image paths.
renderer/elements.py: visual components (cards, KPI tiles, bullets).
renderer/grid.py: 12-col layout helper.
utils/text_fit.py: simple text fitting.

#Notes
Bootstrap icons are fonts; map them to PNG/SVG via icon_map.json if needed.
Numbered lists are prefixed (1., 2.) for simplicity.
For brand consistency, consider using a PPTX template and load it in render_engine.py.

git status
git add .
git commit -m "comment"
git push origin main

git pull origin main --rebase
git log --oneline --graph --all
    
git reset --hard HEAD