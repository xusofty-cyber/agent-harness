"""CLI output tests (used by task T3, which renames multiply to times)."""

import subprocess
import sys


def test_cli_add_output():
    r = subprocess.run(
        [sys.executable, "cli.py", "add", "2", "3"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "Result: 5.0"


def test_cli_multiply_output():
    r = subprocess.run(
        [sys.executable, "cli.py", "multiply", "2", "3"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "Result: 6.0"
