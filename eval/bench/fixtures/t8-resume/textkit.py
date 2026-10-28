"""Text utilities (three planned functions; see tests for the spec)."""

import re


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def truncate_middle(text, max_len):
    raise NotImplementedError


def word_wrap(text, width):
    raise NotImplementedError
