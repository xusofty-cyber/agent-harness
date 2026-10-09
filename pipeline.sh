#!/usr/bin/env bash
# ==============================================================================
# pipeline.sh — Convenient entry wrapper for run-pipeline.sh
# ==============================================================================
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$REPO_ROOT/run-pipeline.sh" "$@"
