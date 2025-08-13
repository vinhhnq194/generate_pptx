from pptx.util import Pt

def fit_font_size(text: str, max_chars: int, base_pt: int = 16, min_pt: int = 12) -> int:
    """
    Heuristic font fitter: gently reduces size as content length exceeds a rough budget.
    """
    if not text:
        return base_pt
    n = len(text.strip())
    if n <= max_chars:
        return base_pt
    ratio = max_chars / max(1, n)
    size = int(base_pt * (0.6 + 0.4 * ratio))  # stay in [~60%, 100%]
    return max(min_pt, size)

def wrap_text(s: str, limit: int = 35) -> str:
    """
    Simple greedy wrapper: breaks s into lines of ~limit chars without hyphenation.
    """
    if not s:
        return ""
    words = s.split()
    lines, line = [], []
    count = 0
    for w in words:
        add_len = len(w) + (1 if line else 0)
        if count + add_len > limit and line:
            lines.append(" ".join(line))
            line = [w]
            count = len(w)
        else:
            line.append(w)
            count += add_len
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines)
