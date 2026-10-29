"""Tiny CLI front end for tinycalc (used by task T3)."""
import sys

from calc import add, multiply


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 3:
        print("usage: cli.py <add|multiply> <a> <b>")
        return 2
    op, a, b = argv[0], float(argv[1]), float(argv[2])
    if op == "add":
        value = add(a, b)
    elif op == "multiply":
        value = multiply(a, b)
    else:
        print(f"unknown op: {op}")
        return 2
    print(f"Result: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
