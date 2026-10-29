"""tinycalc — benchmark fixture for agent-harness Phase 3.

A deliberately tiny calculator. The starting commit contains exactly one
bug (T1: subtract returns the sum) and two missing behaviours (T2: no
power function; T4: divide does not round). T3 renames multiply to times.
"""

def add(a, b):
    return a + b


def subtract(a, b):
    # BUG (task T1): returns the sum instead of the difference.
    return a + b


def multiply(a, b):
    return a * b


def divide(a, b):
    """Return the exact quotient (task T4 changes this to 2-decimal rounding)."""
    return a / b
