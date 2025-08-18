def rem_to_inches(rem_value: float, rem: int = 16) -> float:
    """
    1 inch = 96 px; 1 rem = <rem> px.
    inches = (rem_value * rem) / 96
    """
    return (rem_value * rem) / 96.0
