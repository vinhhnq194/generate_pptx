# v2 – Bootstrap HTML → PPTX

**What it does:**  
- Parses Bootstrap-like HTML (.row / .col-*) into a SlideModel (Python objects).
- Renders SlideModel to PPTX using `python-pptx`.
- Uses mapping and icon config files for customization.

**How to use:**
```bash
python main.py --html path/to/input.html --out output.pptx
# Optional:
# --template path/to/template.pptx
# --mapping path/to/mapping.json
# --icons path/to/icon_map.json
# --overrides path/to/layout_overrides.json
```