def _is_textbox_empty(shape) -> bool:
    try:
        if not hasattr(shape, "text_frame"): return False
        txt = shape.text_frame.text if shape.text_frame else ""
        return (txt or "").strip() == ""
    except Exception:
        return False

def cleanup_slide(slide):
    keep = {"FOOTER_BAR"}
    to_delete = []
    for shp in slide.shapes:
        if getattr(shp, "name", "") in keep: 
            continue
        if _is_textbox_empty(shp): to_delete.append(shp); continue
        if shp.width == 0 or shp.height == 0: to_delete.append(shp)
    for shp in to_delete:
        sp = shp._element
        sp.getparent().remove(sp)
