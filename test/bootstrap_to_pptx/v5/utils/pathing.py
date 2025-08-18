from pathlib import Path

def resolve(base: Path, p: str) -> str:
    pp = Path(p)
    if pp.exists():
        return str(pp.resolve())
    alt = base / p
    if alt.exists():
        return str(alt.resolve())
    raise FileNotFoundError(p)
