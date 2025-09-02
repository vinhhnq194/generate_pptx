def rem_to_inches(rem_value: float, rem: int = 16) -> float:
    """inches = (rem_value * rem px) / 96 px-per-inch"""
    return (rem_value * rem) / 96.0
