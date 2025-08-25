# v3 – Scalable, Data-Driven Bootstrap HTML → PPTX

**What it does:**  
- Reads any Bootstrap-like HTML file.
- Infers rows/cols and element types (cards, KPIs, tables, images, charts, text).
- Lays out elements on a 12-col grid.
- Creates PPTX elements from presets and styles them using mapping tables.
- Fully config-driven and extensible.

**How to use:**
```bash
python main.py --html path/to/input.html --out output.pptx
# Optional:
# --mapping config/mapping.json
# --presets config/element_presets.json
# --overrides config/layout_overrides.json
```