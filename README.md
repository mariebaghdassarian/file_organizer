# 📁 File Organizer

A desktop app to automatically sort photos, videos, screenshots and documents into folders — built with Python and a clean GUI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

### 📷 Media tab — sort by date
- **Recursive scan** — processes all subfolders automatically
- **Smart date detection**, in priority order:
  1. EXIF metadata (photos, RAW files)
  2. Video metadata via MediaInfo (MP4, MOV, MKV…)
  3. Date parsed from filename (Android/macOS screenshots, e.g. `Screenshot_20231015_143022.png`)
  4. File-system date as fallback
- **Two output formats** — `YYYY/YYYY-MM` (year + month) or `YYYY` (year only)
- **Wide format support**
  - Images: JPG, PNG, HEIC, WEBP, GIF, BMP, TIFF + RAW (CR2, CR3, NEF, ARW, DNG, ORF, RW2…)
  - Videos: MP4, MOV, AVI, MKV, WMV, FLV, 3GP, M4V, MTS, WEBM…

### 📄 Documents tab — sort by type
- Automatically moves files into `PDF`, `Word`, `Excel`, `PowerPoint`, `Texte`, `Archives`, `Code` folders
- Unknown types go to an `Autres` / `Others` folder

### General
- **Duplicate detection** — skips identical files (size + MD5), nothing gets overwritten
- **Preview before sorting** — shows every planned move before anything happens
- **Auto-cleanup** — removes empty folders after sorting
- **FR / EN language switcher** — full interface translation at runtime

---

## Output structure (Media tab)

```
📂 Your folder/
├── 2022/
│   ├── 2022-06/
│   │   ├── IMG_4823.jpg
│   │   └── video_trip.mp4
│   └── 2022-11/
│       └── Screenshot_20221103_091500.png
├── 2023/
│   └── 2023-03/
│       └── photo.heic
└── _A_TRIER_MANUELLEMENT/   ← files where no date could be determined
```

---

## Project structure

```
file_organizer/
├── main.py              ← entry point  (python main.py)
├── config.py            ← window size, colours, file extensions
├── i18n.py              ← all UI strings in FR + EN
├── state.py             ← shared mutable state (selected folders, sort format)
├── requirements.txt
│
├── core/
│   ├── date_extractor.py   ← EXIF / video / filename / filesystem date logic
│   ├── file_utils.py       ← duplicate check, safe paths, directory walkers
│   └── sorter.py           ← scan + move logic (no UI dependency)
│
└── ui/
    ├── app.py           ← App class: window, canvas, tabs, language switcher
    ├── dialogs.py       ← progress window, preview dialog, result messagebox
    ├── media_tab.py     ← Media tab widgets
    └── docs_tab.py      ← Documents tab widgets
```

---

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

> **Note:** `pymediainfo` requires [MediaInfo](https://mediaarea.net/en/MediaInfo/Download) to be installed on your system.

---

## Usage

```bash
python main.py
```

1. Choose a tab: **📷 Media** (sort by date) or **📄 Documents** (sort by type)
2. Click **CHOOSE A FOLDER** and select the folder containing your files
3. *(Media only)* Choose the output format: `Year / Month` or `Year`
4. Click the sort button — the app scans all files recursively
5. Review the preview (every planned move is listed)
6. Click **Confirm** to sort, or **Cancel** to abort

---

## Build a standalone .exe (no Python required)

Run the included build script:

```bat
build_exe.bat
```

The script installs PyInstaller, bundles all assets, and produces `dist\FileOrganizer.exe`.

> **Prerequisite:** [MediaInfo](https://mediaarea.net/en/MediaInfo/Download/Windows) must still be installed separately on the target machine for video date extraction to work.

---

## Built with

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI framework
- [exifread](https://github.com/ianare/exif-py) — EXIF metadata extraction
- [Pillow](https://python-pillow.org/) — image processing & HEIC/WEBP EXIF fallback
- [pymediainfo](https://pymediainfo.readthedocs.io/) — video metadata extraction

---

## License

MIT — free to use and modify.
