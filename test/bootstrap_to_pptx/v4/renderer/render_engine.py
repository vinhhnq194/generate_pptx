from .pipeline import build_deck_from_html

def render_from_html(html_path: str, styles_path: str, presets_path: str, template_path: str | None = None):
    """Public wrapper so main.py can stay simple."""
    return build_deck_from_html(html_path=html_path, styles_path=styles_path, presets_path=presets_path, template_path=template_path)
