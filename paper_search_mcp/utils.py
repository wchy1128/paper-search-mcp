import hashlib
import re


def extract_doi(text: str) -> str:
    """Extract DOI from arbitrary text or URL if present."""
    if not text:
        return ""
    match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE)
    return match.group(0).rstrip(".,;)") if match else ""


def stable_id(prefix: str, text: str, length: int = 8, separator: str = "_") -> str:
    """Build a process-stable paper_id from a prefix and source text.

    Uses md5 (deterministic across processes / ``PYTHONHASHSEED``) instead of
    the built-in ``hash()``, which is randomized per process for strings and
    therefore unsuitable as a deduplication key or persistent identifier.

    Args:
        prefix: Source tag (e.g. ``"citeseerx"``, ``"dblp"``).
        text: Identifying text (title, URL, ...) to digest.
        length: Number of hex characters to keep from the digest (default 8).
        separator: String placed between prefix and digest (default ``"_"``).
            Use ``":"`` for connectors whose historical id format used a colon
            (e.g. SSRN's ``"ssrn:<id>"``), so primary and fallback ids stay
            consistent within the same source.

    Returns:
        Identifier of the form ``"{prefix}{separator}{hex}"``.
    """
    digest = hashlib.md5((text or "").encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{separator}{digest}"


def safe_filename(filename_hint: str, default: str = "paper") -> str:
    """Sanitize a string for use as a filename across operating systems.

    Replaces any run of characters outside ``[A-Za-z0-9._-]`` with a single
    underscore, strips leading/trailing dots and underscores, and truncates to
    120 characters. Returns ``default`` when the result is empty.

    Args:
        filename_hint: Raw identifier (e.g. ``"DOI:10.18653/v1/N18-3011"``).
        default: Fallback name when sanitization yields nothing.

    Returns:
        A filesystem-safe filename stem.
    """
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", filename_hint).strip("._")
    if not safe:
        return default
    return safe[:120]
