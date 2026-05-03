"""Text normalisation: clean extracted resume text for downstream processing."""

from __future__ import annotations

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Normalise extracted resume text:
    - Restore unicode characters to ASCII where possible
    - Remove non-printable characters
    - Compress excess whitespace
    - Remove repeated separator lines (-------, ======)
    - Normalise bullet characters to ASCII hyphen
    - Strip leading/trailing whitespace
    """
    if not text:
        return ""

    # Normalise unicode (NFKD → ASCII)
    text = unicodedata.normalize("NFKD", text)

    # Replace common ligatures
    replacements = {
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2023": "-",
        "\u25cf": "-",
        "\u2012": "-",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Remove non-printable characters (keep newlines and tabs)
    text = "".join(
        ch for ch in text if unicodedata.category(ch) not in ("Cc", "Cf") or ch in "\n\t"
    )

    # Remove repeated separator lines
    text = re.sub(r"[-=_]{4,}", "", text)

    # Collapse multiple spaces on the same line (but preserve newlines)
    lines = text.split("\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]

    # Remove lines that are purely punctuation or very short noise
    lines = [line for line in lines if len(line) > 1 or line.isalpha()]

    # Collapse more than 2 consecutive blank lines into 2
    cleaned_lines: list[str] = []
    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def extract_candidate_name(text: str) -> str:
    """
    Heuristic: the candidate's name is usually on the first non-blank line
    and contains 2–4 words with title case.
    """
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return "Candidate"
