"""Small statistics helpers."""


def median(values):
    """Return the median of a non-empty sequence of numbers."""
    ordered = sorted(values)
    return ordered[len(ordered) // 2]
