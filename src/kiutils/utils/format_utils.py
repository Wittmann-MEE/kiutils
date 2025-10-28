def format_float(n: float) -> str:
    if n != 0.0 and abs(n) <= 0.0001:
        # Very small number: fixed-point with 16 decimals
        s = f"{n:.16f}"
        # Strip trailing zeros and possible trailing decimal
        s = s.rstrip("0").rstrip(".") if "." in s else s
    else:
        # Otherwise: general format with 10 significant digits
        s = f"{n:.10g}"

    return s
