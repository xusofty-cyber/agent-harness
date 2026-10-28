"""Fixture tests. At the starting commit, test_subtract, test_power and
test_divide_rounding FAIL by design — each is the acceptance test of one
benchmark task (T1, T2, T4). The other tests pass at the start."""

from calc import add, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(5, 3) == 2


def test_multiply():
    assert multiply(2, 3) == 6


def test_divide():
    assert divide(6, 3) == 2


def test_power():
    from calc import power

    assert power(2, 3) == 8


def test_divide_rounding():
    assert divide(10, 3) == 3.33
