#!/usr/bin/env bash
# One-click fetch of the Chinese Word reference template for pandoc conversion.
# Source: Achuan-2/pandoc_docx_template (community-verified Chinese typography)
# Usage: ./fetch-word-template.sh [output_dir]
set -euo pipefail

OUT_DIR="${1:-.}"
TEMPLATE_URL="https://raw.githubusercontent.com/Achuan-2/pandoc_docx_template/main/templates/template_%E6%A0%87%E9%A2%98%E4%B8%8D%E7%BC%96%E5%8F%B7-%E5%88%97%E8%A1%A8%E7%AC%AC%E4%BA%8C%E8%A1%8C%E9%A1%B6%E6%A0%BC.docx"
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

echo "Saved to: $OUT_FILE"
echo ""
echo "Convert markdown to Word:"
echo "  pandoc input.md -o output.docx --reference-doc \"$OUT_FILE\""
