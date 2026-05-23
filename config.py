"""config.py - Application-wide constants."""

import os
import sys


def resource_path(relative):
    """Resolve path for dev and PyInstaller bundles."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


WIN_W, WIN_H = 520, 600
PASTEL_BG = "#FEF6F6"

BG_IMAGE_PATH = resource_path("file_icon.png")
BG_OPACITY    = 0.30

# Card layer composited into the background to hide CTk widget halos
CARD_X1, CARD_Y1 = 22, 55
CARD_X2, CARD_Y2 = WIN_W - 22, 325
CARD_ALPHA        = 225   # 0-255

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif", ".bmp",
    ".heic", ".heif", ".webp", ".avif", ".jfif",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raw", ".orf", ".rw2", ".sr2",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv",
    ".3gp", ".3g2", ".m4v", ".mts", ".m2ts", ".ts",
    ".webm", ".mpg", ".mpeg", ".mp2",
}

ALL_MEDIA = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

DOC_TYPE_MAP = {
    "PDF":        {".pdf"},
    "Word":       {".doc", ".docx", ".odt"},
    "Excel":      {".xls", ".xlsx", ".ods", ".csv"},
    "PowerPoint": {".ppt", ".pptx", ".odp"},
    "Texte":      {".txt", ".md", ".rtf"},
    "Archives":   {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code":       {".py", ".js", ".ts", ".html", ".css", ".java",
                   ".cpp", ".c", ".json", ".xml"},
}

EXT_TO_DOC_TYPE = {
    ext: dtype
    for dtype, exts in DOC_TYPE_MAP.items()
    for ext in exts
}
