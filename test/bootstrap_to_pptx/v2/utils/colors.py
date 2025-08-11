from pptx.dml.color import RGBColor

def hex_to_rgb_color(hex_str: str) -> RGBColor:
    """
    Convert #RRGGBB to python-pptx RGBColor
    """
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) != 6:
        return RGBColor(13,110,253)  # fallback primary
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return RGBColor(r, g, b)
