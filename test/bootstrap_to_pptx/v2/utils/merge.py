def deep_update(base: dict, overrides: dict) -> dict:
    """
    Shallow + recursive dict merge. Mutates base and returns it.
    """
    for k, v in (overrides or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_update(base[k], v)
        else:
            base[k] = v
    return base
