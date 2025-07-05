import unicodedata, re


def normalize(s: str) -> str:
    """Lowers, strips most punctuation, and normalizes unicode. Keeps apostrophes."""
    if not isinstance(s, str):
        return s

    s = s.lower()
    s = s.replace("’", "'").replace("‘", "'")  # normalize curly quotes
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s']", "", s)  # keep apostrophes
    s = re.sub(r"\s+", " ", s).strip()
    return s
