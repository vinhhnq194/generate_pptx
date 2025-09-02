# v6 – Layout-first (hierarchical) Bootstrap HTML → PPTX

**Goal:** replicate the correct layout using a recursive, container-relative 12-column grid.
- Parse `.row` / `.col-*` including **nested rows inside columns**
- Compute placements **relative to the parent container** (proportional gutter)
- Render placeholder rectangles only (content parsing comes later)

## Run
```bash
pip install -r v6/requirements.txt
python -m main --html tests/fixtures/simple_2col.html --out demo_v6.pptx
