"""Small statistics helpers."""


def median(values):
    """Return the median of a non-empty sequence of numbers.

    Even-length input yields the mean of the two middle values.
    Raises ValueError on empty input. Does not mutate the input.
    """
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError("median of empty input")
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
