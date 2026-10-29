#!/usr/bin/env python3
"""Print the skill names for a deploy profile (Phase 4, 4-1).

Reads skills-profiles.json (the single source of truth for profile
membership). Used by deploy-agents.sh; deploy-agents.ps1 reads the same
file natively with ConvertFrom-Json.

Usage:
    profile-skills.py <minimal|standard|full> [--json]
    profile-skills.py --list-profiles

Exit codes: 0 ok; 2 unknown profile or unreadable profiles file.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES_FILE = ROOT / "skills-profiles.json"


def load():
    try:
        with open(PROFILES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"profile-skills: cannot read {PROFILES_FILE}: {e}", file=sys.stderr)
        sys.exit(2)


def main(argv):
    if argv == ["--list-profiles"]:
        print(" ".join(sorted(load()["profiles"])))
        return 0
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[-3], file=sys.stderr)
        print("usage: profile-skills.py <minimal|standard|full> [--json]", file=sys.stderr)
        return 2
    profile = args[0]
    data = load()
    profiles = data.get("profiles", {})
    if profile not in profiles:
        print(f"profile-skills: unknown profile {profile!r} "
              f"(known: {', '.join(sorted(profiles))})", file=sys.stderr)
        return 2
    skills = profiles[profile]["skills"]
    if as_json:
        print(json.dumps(skills))
    else:
        print(" ".join(skills))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
