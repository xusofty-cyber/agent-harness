"""Text utilities (three planned functions; see tests for the spec)."""

import re


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def truncate_middle(text, max_len):
    if max_len < 1:
        raise ValueError("max_len must be >= 1")
    if len(text) <= max_len:
        return text
    if max_len == 1:
        return "…"
    keep = max_len - 1
    head = (keep + 1) // 2
    tail = keep // 2
    return text[:head] + "…" + (text[len(text) - tail:] if tail else "")


def word_wrap(text, width):
    if width < 1:
        raise ValueError("width must be >= 1")
    words = text.split()
    lines = []
    current = ""
    for word in words:
        while len(word) > width:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:width])
            word = word[width:]
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)
