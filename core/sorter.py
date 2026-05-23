"""
core/sorter.py — File scanning and moving logic.

This module is UI-agnostic: it performs the actual file-system work and
communicates progress only through plain callbacks.

The UI layer (ui/media_tab.py, ui/docs_tab.py) is responsible for:
  - running these functions in a background thread
  - wrapping the callbacks with root.after() for thread-safe UI updates
"""

import os
import shutil
from collections.abc import Callable

from config import EXT_TO_DOC_TYPE
from core.date_extractor import get_reliable_date
from core.file_utils import (
    collect_all_media,
    collect_all_docs,
    files_are_identical,
    unique_dest_path,
    remove_empty_dirs,
)
from i18n import t, get_lang

# Type alias for the progress callback
ProgressCallback = Callable[[int, int, str], None]   # (current, total, filename)


# ---------------------------------------------------------------------------
# Media scan
# ---------------------------------------------------------------------------

def scan_media(
    folder: str,
    sort_format: str,
    update_cb: ProgressCallback | None = None,
) -> tuple[list, list[str], int, int, int]:
    """Scan *folder* for media files and build a move plan.

    Parameters
    ----------
    folder:       Root folder to scan recursively.
    sort_format:  ``"year_month"`` → YYYY/YYYY-MM  |  ``"year"`` → YYYY
    update_cb:    Called as ``update_cb(i, total, filename)`` for each file.

    Returns
    -------
    (to_move, preview_lines, already_ok, duplicates, total_found)

    ``to_move`` is a list of ``(src_path, dest_dir, filename)`` tuples.
    """
    all_files = collect_all_media(folder)
    total = len(all_files)
    if total == 0:
        return [], [], 0, 0, 0

    to_move:       list[tuple[str, str, str]] = []
    preview_lines: list[str]                  = []
    already_ok  = 0
    duplicates  = 0

    for i, path in enumerate(all_files, 1):
        fname = os.path.basename(path)

        if update_cb:
            update_cb(i, total, fname)

        date = get_reliable_date(path)

        if date:
            if sort_format == "year":
                dest_dir = os.path.join(folder, date.strftime("%Y"))
                rel_dst  = os.path.join(date.strftime("%Y"), fname)
            else:
                dest_dir = os.path.join(
                    folder, date.strftime("%Y"), date.strftime("%Y-%m"))
                rel_dst  = os.path.join(
                    date.strftime("%Y"), date.strftime("%Y-%m"), fname)

            dest_path = os.path.join(dest_dir, fname)

            # File is already in the right place
            if os.path.normpath(path) == os.path.normpath(dest_path):
                already_ok += 1
                continue

            # Identical file already exists at destination → skip (duplicate)
            if os.path.exists(dest_path) and files_are_identical(path, dest_path):
                duplicates += 1
                preview_lines.append(
                    f"[skip dup]  {os.path.relpath(path, folder)}")
                continue

            rel_src = os.path.relpath(path, folder)
            preview_lines.append(f"{rel_src[:50].ljust(52)} →  {rel_dst}")
            to_move.append((path, dest_dir, fname))

        else:
            # No date found → manual sorting folder
            manual_dir = os.path.join(folder, t("manual_folder"))
            rel_src = os.path.relpath(path, folder)
            preview_lines.append(
                f"{rel_src[:50].ljust(52)} →  {t('manual_folder')}/{fname}")
            to_move.append((path, manual_dir, fname))

    return to_move, preview_lines, already_ok, duplicates, total


# ---------------------------------------------------------------------------
# Documents scan
# ---------------------------------------------------------------------------

def scan_docs(
    folder: str,
    update_cb: ProgressCallback | None = None,
) -> tuple[list, list[str], int, int]:
    """Scan *folder* for documents and build a move plan.

    Returns
    -------
    (to_move, preview_lines, already_ok, duplicates)
    """
    all_docs = collect_all_docs(folder)

    to_move:       list[tuple[str, str, str]] = []
    preview_lines: list[str]                  = []
    already_ok  = 0
    duplicates  = 0

    for i, path in enumerate(all_docs, 1):
        fname     = os.path.basename(path)
        ext       = os.path.splitext(fname)[1].lower()
        dtype     = EXT_TO_DOC_TYPE.get(ext, t("others"))
        dest_dir  = os.path.join(folder, dtype)
        dest_path = os.path.join(dest_dir, fname)

        if update_cb:
            update_cb(i, len(all_docs), fname)

        # Already in the right folder
        if os.path.normpath(os.path.dirname(path)) == os.path.normpath(dest_dir):
            already_ok += 1
            continue

        # Identical duplicate at destination
        if os.path.exists(dest_path) and files_are_identical(path, dest_path):
            duplicates += 1
            continue

        rel = os.path.relpath(path, folder)
        preview_lines.append(f"{rel[:50].ljust(52)} →  {dtype}/{fname}")
        to_move.append((path, dest_dir, fname))

    return to_move, preview_lines, already_ok, duplicates


# ---------------------------------------------------------------------------
# Move executor
# ---------------------------------------------------------------------------

def run_moves(
    files_data: list[tuple[str, str, str]],
    cleanup_folder: str,
    update_cb: ProgressCallback | None = None,
) -> tuple[int, int]:
    """Execute the planned file moves.

    Parameters
    ----------
    files_data:      List of ``(src_path, dest_dir, filename)`` tuples.
    cleanup_folder:  Root folder from which empty dirs are removed afterwards.
    update_cb:       Called as ``update_cb(i, total, filename)`` per file.

    Returns
    -------
    (moved_count, error_count)
    """
    total  = len(files_data)
    moved  = 0
    errors = 0

    for i, (src, dest_dir, fname) in enumerate(files_data, 1):
        if update_cb:
            update_cb(i, total, fname)
        os.makedirs(dest_dir, exist_ok=True)
        dest = unique_dest_path(dest_dir, fname)
        try:
            shutil.move(src, dest)
            moved += 1
        except Exception:
            errors += 1

    remove_empty_dirs(cleanup_folder)
    return moved, errors
