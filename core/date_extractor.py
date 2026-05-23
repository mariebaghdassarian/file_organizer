"""
core/date_extractor.py — Date extraction from media files.

Priority order (first hit wins):
  1. EXIF metadata          — images & RAW files
  2. Video container tags   — via pymediainfo
  3. Date parsed from the filename (Android / macOS screenshot naming)
  4. File-system mtime/ctime as last resort
"""

import os
import re
from datetime import datetime

import exifread
from PIL import Image

from config import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


# ---------------------------------------------------------------------------
# 1. EXIF  (images)
# ---------------------------------------------------------------------------

def get_exif_date(file_path: str) -> datetime | None:
    """Extract the original capture date from EXIF metadata."""
    # Fast path via exifread
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(
                f, stop_tag="EXIF DateTimeOriginal", details=False)
        for key in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
            if key in tags:
                return datetime.strptime(str(tags[key]), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # Fallback via Pillow (useful for HEIC / WEBP)
    try:
        with Image.open(file_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id in (36867, 36868, 306):   # DateTimeOriginal, Digitized, DateTime
                    if tag_id in exif:
                        return datetime.strptime(exif[tag_id], "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# 2. Video container metadata
# ---------------------------------------------------------------------------

def get_video_date(file_path: str) -> datetime | None:
    """Extract the recording date from a video file via pymediainfo."""
    try:
        from pymediainfo import MediaInfo
        info = MediaInfo.parse(file_path)
        for track in info.tracks:
            if track.track_type != "General":
                continue
            for field in (
                track.com_apple_quicktime_creationdate,
                track.encoded_date,
                track.tagged_date,
            ):
                if not field:
                    continue
                # ISO-8601 style: "2023-07-14T18:30:00" or "2023-07-14 18:30:00"
                m = re.search(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})", field)
                if m:
                    try:
                        d = datetime.strptime(
                            f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                        if 1980 < d.year < 2100:
                            return d
                    except Exception:
                        pass
                # Plain "UTC 2023-07-14 18:30:00"
                try:
                    clean = field.replace("UTC ", "").strip()[:19]
                    d = datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
                    if 1980 < d.year < 2100:
                        return d
                except Exception:
                    pass
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# 3. Filename parsing
# ---------------------------------------------------------------------------

def get_date_from_filename(filename: str) -> datetime | None:
    """Try to extract a date from common screenshot / camera naming patterns."""
    name = os.path.splitext(filename)[0]
    patterns = [
        # Full timestamp with separator: 2023-10-15T14_30_00 / 2023-10-15 14:30:00
        (r"(\d{4})[-_](\d{2})[-_](\d{2})[T_ -](\d{2})[.:\-](\d{2})[.:\-](\d{2})", 6),
        # Compact timestamp: 20231015_143000
        (r"(\d{4})(\d{2})(\d{2})[_\-](\d{2})(\d{2})(\d{2})(?!\d)", 6),
        # Date only with separators: 2023-10-15
        (r"(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)", 3),
        # Compact date: 20231015
        (r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)", 3),
    ]
    for pattern, ngroups in patterns:
        m = re.search(pattern, name)
        if not m:
            continue
        try:
            g = m.groups()
            y, mo, d = int(g[0]), int(g[1]), int(g[2])
            if not (1980 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31):
                continue
            if ngroups == 6:
                return datetime(y, mo, d, int(g[3]), int(g[4]), int(g[5]))
            return datetime(y, mo, d)
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# 4. Unified entry point
# ---------------------------------------------------------------------------

def get_reliable_date(file_path: str) -> datetime | None:
    """Return the best available date for a media file (see module docstring)."""
    ext = os.path.splitext(file_path)[1].lower()

    date: datetime | None = None

    if ext in IMAGE_EXTENSIONS:
        date = get_exif_date(file_path)

    if date is None and ext in VIDEO_EXTENSIONS:
        date = get_video_date(file_path)

    if date is None:
        date = get_date_from_filename(os.path.basename(file_path))

    if date is None:
        try:
            ts = min(os.path.getmtime(file_path), os.path.getctime(file_path))
            date = datetime.fromtimestamp(ts)
        except Exception:
            pass

    return date
