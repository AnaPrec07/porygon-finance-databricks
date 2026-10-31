"""Pure helpers for landing-zone paths. Layout: <landing>/<user_id>/<file_name> (optionally nested)."""

from __future__ import annotations

import re

# Regex group 1 is the user_id. Shared by Python helpers and the pipeline (regexp_extract).
# user_id: UUID or opaque id of 8-64 chars, [A-Za-z0-9_-]. Never derived from file contents.
USER_ID_REGEX = r"/landing/([A-Za-z0-9_-]{8,64})/"

_USER_ID_RE = re.compile(USER_ID_REGEX)


def normalize_path(path: str) -> str:
    """Strip the `dbfs:` scheme so paths from Auto Loader and the filesystem compare equal."""
    return path[len("dbfs:") :] if path.startswith("dbfs:") else path


def user_id_from_path(path: str) -> str | None:
    """Return the user_id encoded in a landing path, or None if the path is not under a user prefix."""
    match = _USER_ID_RE.search(normalize_path(path))
    return match.group(1) if match else None


def files_to_purge(landed: list[str], committed: set[str]) -> list[str]:
    """Landed files that are safe to delete: only those already committed to bronze."""
    committed_norm = {normalize_path(p) for p in committed}
    return sorted(p for p in landed if normalize_path(p) in committed_norm)
