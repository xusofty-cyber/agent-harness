"""Duration parsing helpers."""

import re

_TOKEN = re.compile(r"(\d+)\s*([hms])", re.IGNORECASE)
_UNITS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """Parse a duration string into total seconds (int).

    See DECISIONS.md for the semantics chosen where the spec was silent.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty duration")
    total = 0
    pos = 0
    seen = set()
    stripped = text.strip()
    while pos < len(stripped):
        m = _TOKEN.match(stripped, pos)
        if not m:
            raise ValueError(f"invalid duration: {text!r}")
        amount, unit = int(m.group(1)), m.group(2).lower()
        if unit in seen:
            raise ValueError(f"repeated unit: {unit}")
        seen.add(unit)
        total += amount * _UNITS[unit]
        pos = m.end()
        while pos < len(stripped) and stripped[pos].isspace():
            pos += 1
    return total
