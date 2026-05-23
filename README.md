# 📁 File Organizer

A desktop app to automatically sort photos, videos and screenshots into folders by date — built with Python and a clean GUI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Recursive scan** — processes all subfolders automatically, not just the root
- **Smart date detection**, in priority order:
  1. EXIF metadata (photos, RAW files)
  2. Video metadata via MediaInfo (MP4, MOV, MKV…)
  3. Date parsed from filename (Android/macOS screenshots, e.g. `Screenshot_20231015_143022.png`)
  4. File system date as fallback
- **Wide format support**
  - Images: JPG, PNG, HEIC, WEBP, GIF, BMP, TIFF + RAW formats (CR2, CR3, NEF, ARW, DNG, ORF, RW2…)
  - Videos: MP4, MOV, AVI, MKV, WMV, FLV, 3GP, M4V, MTS, WEBM…
- **Duplicate detection** — skips identical files (size + MD5 check), nothing gets overwritten
- **Preview before sorting** — shows every move before it happens, with a confirm/cancel step
- **Clean output structure** — organizes into `YYYY/YYYY-MM/` folders
- **Auto-cleanup** — removes empty folders after sorting

---

## Output structure

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
python tri_fichier.py
```

1. Click **CHOISIR UN DOSSIER** and select the folder containing your media files
2. Click **TRIER PAR DATE** — the app will scan all files recursively
3. Review the preview (every move is listed before anything happens)
4. Click **Confirmer** to sort, or **Annuler** to cancel

---

## Built with

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI framework
- [exifread](https://github.com/ianare/exif-py) — EXIF metadata extraction
- [Pillow](https://python-pillow.org/) — image processing & HEIC/WEBP EXIF fallback
- [pymediainfo](https://pymediainfo.readthedocs.io/) — video metadata extraction

---

## License

MIT — free to use and modify.
