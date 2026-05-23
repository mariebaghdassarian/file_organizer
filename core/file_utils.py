"""
core/file_utils.py — Generic file-system helpers.

All functions here are pure utilities with no UI or translation concerns.
"""

import os
import hashlib

from config import ALL_MEDIA


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def files_are_identical(path_a: str, path_b: str) -> bool:
    """Return True if both files have the same size **and** MD5 hash."""
    if os.path.getsize(path_a) != os.path.getsize(path_b):
        return False

    def md5(path: str) -> str:
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65_536), b""):
                h.update(chunk)
        return h.hexdigest()

    return md5(path_a) == md5(path_b)


# ---------------------------------------------------------------------------
# Safe destination path
# ---------------------------------------------------------------------------

def unique_dest_path(dest_dir: str, filename: str) -> str:
    """Return a destination path that does not collide with an existing file.

    If *filename* is already taken, appends ``_1``, ``_2``, … until free.
    """
    dest = os.path.join(dest_dir, filename)
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest):
        dest = os.path.join(dest_dir, f"{base}_{counter}{ext}")
        counter += 1
    return dest


# ---------------------------------------------------------------------------
# Directory walkers
# ---------------------------------------------------------------------------

def collect_all_media(folder: str) -> list[str]:
    """Recursively return every media file path under *folder*."""
    result: list[str] = []
    for root_dir, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if os.path.splitext(f)[1].lower() in ALL_MEDIA:
                result.append(os.path.join(root_dir, f))
    return result


def collect_all_docs(folder: str) -> list[str]:
    """Recursively return every non-media file path under *folder*."""
    result: list[str] = []
    for root_dir, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext and ext not in ALL_MEDIA:
                result.append(os.path.join(root_dir, f))
    return result


def remove_empty_dirs(folder: str) -> None:
    """Delete every empty sub-directory inside *folder* (bottom-up)."""
    for root_dir, _dirs, _files in os.walk(folder, topdown=False):
        if root_dir == folder:
            continue
        try:
            if not os.listdir(root_dir):
                os.rmdir(root_dir)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Time formatting
# ---------------------------------------------------------------------------

def fmt_time(seconds: float) -> str:
    """Convert a duration in seconds to a human-readable string.

    Examples: ``"5s"``  ``"2m30s"``  ``"1h04m12s"``
    """
    s = int(max(0, seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    if m > 0:
        return f"{m}m{sec:02d}s"
    return f"{sec}s"
