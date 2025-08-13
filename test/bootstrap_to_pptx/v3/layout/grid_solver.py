from utils.log import logger

def solve_grid_layout(layout_tree, overrides):
    logger.info("Mapping elements to 12-col grid...")
    grid = []
    for row in layout_tree:
        grid_row = []
        for col in row:
            col_classes = col["bootstrap_classes"]
            col_span = get_col_span(col_classes)
            grid_row.append({
                "type": col["type"],
                "content": col["content"],
                "col_span": col_span,
                "position": calculate_position(col_span, overrides)
            })
        grid.append(grid_row)
    return grid

def get_col_span(classes):
    # Example: col-6 → 6
    for cls in classes:
        if cls.startswith("col-"):
            try:
                return int(cls.split("-")[1])
            except:
                continue
    return 12

def calculate_position(col_span, overrides):
    # Calculate left/top/width/height based on col_span and overrides
    # Placeholder logic
    return {
        "left": col_span * 0.5,
        "top": 1,
        "width": col_span * 0.5,
        "height": 1.5
    }