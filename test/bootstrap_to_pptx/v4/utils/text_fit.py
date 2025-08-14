def wrap_text(s: str, limit: int = 36) -> str:
    if not s: return ""
    parts, cur, cnt = [], [], 0
    for w in s.split():
        if cnt + len(w) + (1 if cur else 0) > limit:
            parts.append(" ".join(cur)); cur=[w]; cnt=len(w)
        else:
            cur.append(w); cnt += len(w) + (1 if cur[:-1] else 0)
    if cur: parts.append(" ".join(cur))
    return "\n".join(parts)
