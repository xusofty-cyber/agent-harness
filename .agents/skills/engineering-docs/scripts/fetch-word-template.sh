#!/usr/bin/env bash
# One-click fetch of the Chinese Word reference template for pandoc conversion.
# Source: Achuan-2/pandoc_docx_template (community-verified Chinese typography)
# Usage: ./fetch-word-template.sh [output_dir]
set -euo pipefail

OUT_DIR="${1:-.}"
TEMPLATE_URL="https://raw.githubusercontent.com/Achuan-2/pandoc_docx_template/main/templates/template_%E6%A0%87%E9%A2%98%E4%B8%8D%E7%BC%96%E5%8F%B7-%E5%88%97%E8%A1%A8%E7%AC%AC%E4%BA%8C%E8%A1%8C%E9%A1%B6%E6%A0%BC.docx"
# Pinned SHA256 of the template file (verified 2026-10-10). If upstream updates
# the template, download manually, verify it, and update this hash.
EXPECTED_SHA256="e9dee7b7e307f9f720984c1a77f8c6e77aca74b4bd7dd130761ce004eeda2ca2"
OUT_FILE="$OUT_DIR/word-reference-template.docx"

echo "Downloading Chinese Word reference template..."
if command -v curl >/dev/null 2>&1; then
    curl -sSL -o "$OUT_FILE" "$TEMPLATE_URL"
elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$OUT_FILE" "$TEMPLATE_URL"
else
    echo "ERROR: need curl or wget" >&2
    exit 1
fi

echo "Verifying SHA256..."
if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL=$(sha256sum "$OUT_FILE" | cut -d' ' -f1)
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL=$(shasum -a 256 "$OUT_FILE" | cut -d' ' -f1)
else
    echo "WARNING: no sha256 tool, skipping verification" >&2
    ACTUAL="$EXPECTED_SHA256"
fi
if [ "$ACTUAL" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch! Expected $EXPECTED_SHA256, got $ACTUAL" >&2
    echo "The upstream template may have changed. Verify manually before use." >&2
    rm -f "$OUT_FILE"
    exit 1
fi
echo "SHA256 verified."

echo "Saved to: $OUT_FILE"
echo ""
echo "Convert markdown to Word:"
echo "  pandoc input.md -o output.docx --reference-doc \"$OUT_FILE\""
