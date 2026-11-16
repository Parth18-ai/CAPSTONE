"""The tool: a small unit converter (manuals mix Nm / lbf-ft, psi / bar, etc.)."""

FACTORS = {
    ("nm", "lbf-ft"): 0.737562, ("lbf-ft", "nm"): 1 / 0.737562,
    ("psi", "bar"): 0.0689476, ("bar", "psi"): 14.5038,
    ("l", "gal"): 0.264172, ("gal", "l"): 3.78541,
    ("km", "mi"): 0.621371, ("mi", "km"): 1.60934,
}


def unit_convert(value: float, from_unit: str, to_unit: str) -> float:
    key = (from_unit.lower(), to_unit.lower())
    if key not in FACTORS:
        raise ValueError(f"Unsupported conversion: {from_unit} -> {to_unit}")
    return round(value * FACTORS[key], 2)
