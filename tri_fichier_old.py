import os
import re
import shutil
import hashlib
import time
import exifread
import customtkinter as ctk
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from datetime import datetime, timedelta
from PIL import Image

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
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
    "Code":       {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".json", ".xml"},
}
EXT_TO_DOC_TYPE = {ext: t for t, exts in DOC_TYPE_MAP.items() for ext in exts}

# ---------------------------------------------------------------------------
# Traductions
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    "fr": {
        "window_title":       "Organisateur de Fichiers",
        "tab_media":          "📷  Médias",
        "tab_docs":           "📄  Documents",
        "no_folder":          "📁  Aucun dossier sélectionné",
        "choose_folder":      "CHOISIR UN DOSSIER",
        "sort_format_label":  "Format de tri",
        "fmt_ym":             "Année / Mois",
        "fmt_y":              "Année",
        "sort_btn_ym":        "TRIER PAR DATE  (YYYY / YYYY-MM)",
        "sort_btn_y":         "TRIER PAR DATE  (YYYY)",
        "sort_docs_btn":      "TRIER PAR TYPE DE FICHIER",
        "legend_title":       "Dossiers créés automatiquement :",
        "legend_types":       "PDF · Word · Excel · PowerPoint · Texte · Archives · Code · Autres",
        "quit":               "Quitter",
        # Fenêtres de progression
        "scanning":           "Analyse des fichiers…",
        "moving_media":       "Déplacement des fichiers…",
        "moving_docs":        "Déplacement des documents…",
        "collecting":         "Collecte en cours…",
        "lbl_elapsed":        "⏱  Écoulé : {t}",
        "lbl_remaining":      "⏳  Restant : {t}",
        # Messages
        "warn_no_folder":     "Veuillez d'abord choisir un dossier.",
        "no_media_found":     "Aucun fichier média trouvé dans ce dossier.",
        "no_docs_found":      "Aucun document trouvé dans ce dossier.",
        "all_sorted_title":   "Tout est trié !",
        "all_sorted_media":   "{n} fichier(s) analysé(s) — tout est déjà correctement classé. 🎉",
        "all_sorted_docs":    "Aucun document à déplacer. {n} déjà bien classé(s).",
        "preview_media":      "Aperçu — {n} déplacement(s)",
        "preview_docs":       "Tri par type — {n} fichier(s)",
        "n_to_move":          "{n} fichier(s) à déplacer",
        "confirm":            "✅  Confirmer et trier",
        "cancel_btn":         "❌  Annuler",
        "result_title":       "Résultat",
        "result_ok":          "✅ Tri terminé !\n{n} fichier(s) déplacé(s).",
        "result_errors":      "\n⚠️ {e} erreur(s) — ces fichiers n'ont pas pu être déplacés.",
        "sum_already_ok":     "✅ {n} fichier(s) déjà bien classé(s) — ignorés",
        "sum_duplicates":     "🔁 {n} doublon(s) identique(s) — ignorés",
        "sum_ok_docs":        "✅ {n} fichier(s) déjà dans le bon dossier — ignorés",
        "manual_folder":      "_A_TRIER_MANUELLEMENT",
    },
    "en": {
        "window_title":       "File Organizer",
        "tab_media":          "📷  Media",
        "tab_docs":           "📄  Documents",
        "no_folder":          "📁  No folder selected",
        "choose_folder":      "CHOOSE A FOLDER",
        "sort_format_label":  "Sort format",
        "fmt_ym":             "Year / Month",
        "fmt_y":              "Year",
        "sort_btn_ym":        "SORT BY DATE  (YYYY / YYYY-MM)",
        "sort_btn_y":         "SORT BY DATE  (YYYY)",
        "sort_docs_btn":      "SORT BY FILE TYPE",
        "legend_title":       "Folders created automatically:",
        "legend_types":       "PDF · Word · Excel · PowerPoint · Text · Archives · Code · Others",
        "quit":               "Quit",
        "scanning":           "Scanning files…",
        "moving_media":       "Moving files…",
        "moving_docs":        "Moving documents…",
        "collecting":         "Collecting files…",
        "lbl_elapsed":        "⏱  Elapsed: {t}",
        "lbl_remaining":      "⏳  Remaining: {t}",
        "warn_no_folder":     "Please choose a folder first.",
        "no_media_found":     "No media files found in this folder.",
        "no_docs_found":      "No documents found in this folder.",
        "all_sorted_title":   "All sorted!",
        "all_sorted_media":   "{n} file(s) analyzed — everything is already correctly sorted. 🎉",
        "all_sorted_docs":    "Nothing to move. {n} file(s) already in the right folder.",
        "preview_media":      "Preview — {n} move(s)",
        "preview_docs":       "Sort by type — {n} file(s)",
        "n_to_move":          "{n} file(s) to move",
        "confirm":            "✅  Confirm and sort",
        "cancel_btn":         "❌  Cancel",
        "result_title":       "Result",
        "result_ok":          "✅ Done!\n{n} file(s) moved.",
        "result_errors":      "\n⚠️ {e} error(s) — these files could not be moved.",
        "sum_already_ok":     "✅ {n} file(s) already correctly sorted — skipped",
        "sum_duplicates":     "🔁 {n} identical duplicate(s) — skipped",
        "sum_ok_docs":        "✅ {n} file(s) already in the right folder — skipped",
        "manual_folder":      "_TO_SORT_MANUALLY",
    },
}

current_lang = "fr"

def t(key, **kwargs):
    s = TRANSLATIONS[current_lang].get(key, key)
    return s.format(**kwargs) if kwargs else s

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
media_source = ""
doc_source   = ""
sort_format  = "year_month"   # "year_month" | "year"

PASTEL_BG = "#FEF6F6"

# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------

def get_exif_date(file_path):
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
        for key in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
            if key in tags:
                return datetime.strptime(str(tags[key]), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    try:
        with Image.open(file_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id in (36867, 36868, 306):
                    if tag_id in exif:
                        return datetime.strptime(exif[tag_id], "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None


def get_video_date(file_path):
    try:
        from pymediainfo import MediaInfo
        info = MediaInfo.parse(file_path)
        for track in info.tracks:
            if track.track_type != "General":
                continue
            for field in (track.com_apple_quicktime_creationdate,
                          track.encoded_date, track.tagged_date):
                if not field:
                    continue
                m = re.search(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})", field)
                if m:
                    try:
                        d = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                        if 1980 < d.year < 2100:
                            return d
                    except Exception:
                        pass
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


def get_date_from_filename(filename):
    name = os.path.splitext(filename)[0]
    patterns = [
        (r"(\d{4})[-_](\d{2})[-_](\d{2})[T_ -](\d{2})[.:\-](\d{2})[.:\-](\d{2})", 6),
        (r"(\d{4})(\d{2})(\d{2})[_\-](\d{2})(\d{2})(\d{2})(?!\d)", 6),
        (r"(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)", 3),
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


def get_reliable_date(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    date = None
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

# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def files_are_identical(a, b):
    if os.path.getsize(a) != os.path.getsize(b):
        return False
    def md5(p):
        h = hashlib.md5()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    return md5(a) == md5(b)


def unique_dest_path(dest_dir, filename):
    dest = os.path.join(dest_dir, filename)
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest):
        dest = os.path.join(dest_dir, f"{base}_{counter}{ext}")
        counter += 1
    return dest


def collect_all_media(folder):
    result = []
    for root_dir, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if os.path.splitext(f)[1].lower() in ALL_MEDIA:
                result.append(os.path.join(root_dir, f))
    return result


def collect_all_docs(folder):
    result = []
    for root_dir, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext and ext not in ALL_MEDIA:
                result.append(os.path.join(root_dir, f))
    return result


def remove_empty_dirs(folder):
    for root_dir, dirs, files in os.walk(folder, topdown=False):
        if root_dir == folder:
            continue
        try:
            if not os.listdir(root_dir):
                os.rmdir(root_dir)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Time helper
# ---------------------------------------------------------------------------

def fmt_time(seconds):
    s = int(max(0, seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    elif m > 0:
        return f"{m}m{sec:02d}s"
    else:
        return f"{sec}s"

# ---------------------------------------------------------------------------
# Progress window
# ---------------------------------------------------------------------------

def make_progress_win(title_key):
    win = ctk.CTkToplevel(root)
    win.title(t(title_key))
    win.geometry("500x285")
    win.grab_set()
    win.resizable(False, False)
    win.configure(fg_color=PASTEL_BG)

    start_time = [time.time()]

    ctk.CTkLabel(win, text=t(title_key), font=("Helvetica", 14, "bold"),
                 fg_color="transparent").pack(pady=(18, 2))
    lbl_file = ctk.CTkLabel(win, text="", font=("Helvetica", 10), text_color="#777",
                             fg_color="transparent")
    lbl_file.pack(pady=2)
    lbl_count = ctk.CTkLabel(win, text="— / —", font=("Helvetica", 13, "bold"),
                              fg_color="transparent")
    lbl_count.pack(pady=2)
    bar = ctk.CTkProgressBar(win, width=440, progress_color="#A8E6CF",
                              fg_color="#E0E0E0", height=10)
    bar.set(0)
    bar.pack(pady=10)
    frm_t = ctk.CTkFrame(win, fg_color="transparent")
    frm_t.pack(pady=2)
    lbl_el = ctk.CTkLabel(frm_t, text=t("lbl_elapsed", t="0s"),
                           font=("Helvetica", 11), fg_color="transparent", text_color="#555")
    lbl_el.pack(side="left", padx=22)
    lbl_rm = ctk.CTkLabel(frm_t, text=t("lbl_remaining", t="—"),
                           font=("Helvetica", 11), fg_color="transparent", text_color="#555")
    lbl_rm.pack(side="left", padx=22)

    def update(i, total, filename=""):
        if total == 0:
            return
        elapsed = time.time() - start_time[0]
        short   = (filename[:44] + "…") if len(filename) > 46 else filename
        rem_str = f"~{fmt_time(elapsed / i * total - elapsed)}" if i > 0 else "—"
        root.after(0, lambda: [
            lbl_file.configure(text=short),
            lbl_count.configure(text=f"{i} / {total}"),
            bar.set(i / total),
            lbl_el.configure(text=t("lbl_elapsed", t=fmt_time(elapsed))),
            lbl_rm.configure(text=t("lbl_remaining", t=rem_str)),
        ])

    return win, update

# ---------------------------------------------------------------------------
# Preview dialog
# ---------------------------------------------------------------------------

def show_preview(title, lines, n_to_move):
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("750x530")
    win.grab_set()
    win.configure(fg_color=PASTEL_BG)

    ctk.CTkLabel(win, text=t("n_to_move", n=n_to_move),
                 font=("Helvetica", 14, "bold"), fg_color="transparent").pack(pady=10)

    text_area = ctk.CTkTextbox(win, wrap="none", font=("Consolas", 10),
                                fg_color="#FFFFFF", border_color="#E0E0E0", border_width=1)
    text_area.pack(padx=15, pady=5, fill="both", expand=True)
    text_area.insert("0.0", "\n".join(lines))
    text_area.configure(state="disabled")

    result = {"confirm": False}

    def on_confirm():
        result["confirm"] = True
        win.destroy()

    frm = ctk.CTkFrame(win, fg_color="transparent")
    frm.pack(pady=15, fill="x")
    ctk.CTkButton(frm, text=t("confirm"), command=on_confirm,
                  fg_color="#2ECC71", hover_color="#27AE60",
                  font=("Helvetica", 12, "bold"), corner_radius=15).pack(side="left", expand=True, padx=12)
    ctk.CTkButton(frm, text=t("cancel_btn"), command=win.destroy,
                  fg_color="#E74C3C", hover_color="#C0392B",
                  font=("Helvetica", 12, "bold"), corner_radius=15).pack(side="right", expand=True, padx=12)

    win.wait_window()
    return result["confirm"]

# ---------------------------------------------------------------------------
# Generic mover (thread)
# ---------------------------------------------------------------------------

def run_moves(files_data, title_key, cleanup_folder, on_complete):
    win, update = make_progress_win(title_key)
    total  = len(files_data)
    moved  = 0
    errors = 0
    for i, (src, dest_dir, fname) in enumerate(files_data, 1):
        update(i, total, fname)
        os.makedirs(dest_dir, exist_ok=True)
        dest = unique_dest_path(dest_dir, fname)
        try:
            shutil.move(src, dest)
            moved += 1
        except Exception:
            errors += 1
    remove_empty_dirs(cleanup_folder)
    root.after(0, lambda: [win.destroy(), on_complete(moved, errors)])


def show_done(moved, errors):
    msg = t("result_ok", n=moved)
    if errors:
        msg += t("result_errors", e=errors)
    messagebox.showinfo(t("result_title"), msg)

# ---------------------------------------------------------------------------
# ── ONGLET MÉDIAS ──
# ---------------------------------------------------------------------------

def select_media_folder():
    global media_source
    chosen = filedialog.askdirectory()
    if chosen:
        media_source = chosen
        media_folder_label.configure(
            text=f"📍  {os.path.basename(chosen) or chosen}",
            fg_color="#FFFFFF", text_color="#2C3E50",
        )


def on_format_change(value):
    global sort_format
    sort_format = "year" if value == t("fmt_y") else "year_month"
    sort_button.configure(text=t("sort_btn_ym") if sort_format == "year_month" else t("sort_btn_y"))


def organize_media():
    if not media_source:
        messagebox.showwarning("", t("warn_no_folder"))
        return

    scan_win = ctk.CTkToplevel(root)
    scan_win.title(t("scanning"))
    scan_win.geometry("500x285")
    scan_win.grab_set()
    scan_win.resizable(False, False)
    scan_win.configure(fg_color=PASTEL_BG)
    scan_start = [time.time()]

    ctk.CTkLabel(scan_win, text=t("scanning"), font=("Helvetica", 14, "bold"),
                 fg_color="transparent").pack(pady=(18, 2))
    lbl_file  = ctk.CTkLabel(scan_win, text=t("collecting"), font=("Helvetica", 10),
                              text_color="#777", fg_color="transparent")
    lbl_file.pack(pady=2)
    lbl_count = ctk.CTkLabel(scan_win, text="— / —", font=("Helvetica", 13, "bold"),
                              fg_color="transparent")
    lbl_count.pack(pady=2)
    scan_bar  = ctk.CTkProgressBar(scan_win, width=440, progress_color="#A8E6CF",
                                    fg_color="#E0E0E0", height=10)
    scan_bar.set(0)
    scan_bar.pack(pady=10)
    frm_t = ctk.CTkFrame(scan_win, fg_color="transparent")
    frm_t.pack(pady=2)
    lbl_el = ctk.CTkLabel(frm_t, text=t("lbl_elapsed", t="0s"),
                           font=("Helvetica", 11), fg_color="transparent", text_color="#555")
    lbl_el.pack(side="left", padx=22)
    lbl_rm = ctk.CTkLabel(frm_t, text=t("lbl_remaining", t="—"),
                           font=("Helvetica", 11), fg_color="transparent", text_color="#555")
    lbl_rm.pack(side="left", padx=22)

    def scan_task():
        all_files = collect_all_media(media_source)
        total = len(all_files)

        if total == 0:
            root.after(0, lambda: [
                scan_win.destroy(),
                messagebox.showinfo("", t("no_media_found")),
            ])
            return

        root.after(0, lambda: lbl_count.configure(text=f"0 / {total}"))

        to_move       = []
        preview_lines = []
        already_ok    = 0
        duplicates    = 0

        for i, path in enumerate(all_files, 1):
            fname   = os.path.basename(path)
            elapsed = time.time() - scan_start[0]
            short   = (fname[:44] + "…") if len(fname) > 46 else fname
            rem_str = f"~{fmt_time(elapsed / i * total - elapsed)}" if i > 0 else "—"

            root.after(0, lambda s=short, p=i/total, c=f"{i} / {total}",
                        e=fmt_time(elapsed), r=rem_str: [
                lbl_file.configure(text=s),
                lbl_count.configure(text=c),
                scan_bar.set(p),
                lbl_el.configure(text=t("lbl_elapsed", t=e)),
                lbl_rm.configure(text=t("lbl_remaining", t=r)),
            ])

            date = get_reliable_date(path)

            if date:
                if sort_format == "year":
                    dest_dir = os.path.join(media_source, date.strftime("%Y"))
                    rel_dst  = os.path.join(date.strftime("%Y"), fname)
                else:
                    dest_dir = os.path.join(media_source, date.strftime("%Y"), date.strftime("%Y-%m"))
                    rel_dst  = os.path.join(date.strftime("%Y"), date.strftime("%Y-%m"), fname)

                dest_path = os.path.join(dest_dir, fname)

                if os.path.normpath(path) == os.path.normpath(dest_path):
                    already_ok += 1
                    continue
                if os.path.exists(dest_path) and files_are_identical(path, dest_path):
                    duplicates += 1
                    preview_lines.append(f"[skip dup]  {os.path.relpath(path, media_source)}")
                    continue

                rel_src = os.path.relpath(path, media_source)
                preview_lines.append(f"{rel_src[:50].ljust(52)} →  {rel_dst}")
                to_move.append((path, dest_dir, fname))
            else:
                manual_dir = os.path.join(media_source, t("manual_folder"))
                rel_src = os.path.relpath(path, media_source)
                preview_lines.append(
                    f"{rel_src[:50].ljust(52)} →  {t('manual_folder')}/{fname}")
                to_move.append((path, manual_dir, fname))

        summary = []
        if already_ok:  summary.append(t("sum_already_ok", n=already_ok))
        if duplicates:  summary.append(t("sum_duplicates", n=duplicates))
        if summary:     preview_lines = summary + ["─" * 72] + preview_lines

        root.after(0, lambda: _finalize_media(scan_win, to_move, preview_lines, total))

    threading.Thread(target=scan_task, daemon=True).start()


def _finalize_media(scan_win, to_move, preview_lines, total_found):
    scan_win.destroy()
    if not to_move:
        messagebox.showinfo(t("all_sorted_title"), t("all_sorted_media", n=total_found))
        return
    if show_preview(t("preview_media", n=len(to_move)), preview_lines, len(to_move)):
        threading.Thread(
            target=run_moves,
            args=(to_move, "moving_media", media_source, show_done),
            daemon=True,
        ).start()

# ---------------------------------------------------------------------------
# ── ONGLET DOCUMENTS ──
# ---------------------------------------------------------------------------

def select_doc_folder():
    global doc_source
    chosen = filedialog.askdirectory()
    if chosen:
        doc_source = chosen
        doc_folder_label.configure(
            text=f"📍  {os.path.basename(chosen) or chosen}",
            fg_color="#FFFFFF", text_color="#2C3E50",
        )


def organize_docs():
    if not doc_source:
        messagebox.showwarning("", t("warn_no_folder"))
        return

    all_docs = collect_all_docs(doc_source)
    if not all_docs:
        messagebox.showinfo("", t("no_docs_found"))
        return

    to_move       = []
    preview_lines = []
    already_ok    = 0
    duplicates    = 0

    for path in all_docs:
        fname     = os.path.basename(path)
        ext       = os.path.splitext(fname)[1].lower()
        dtype     = EXT_TO_DOC_TYPE.get(ext, "Autres" if current_lang == "fr" else "Others")
        dest_dir  = os.path.join(doc_source, dtype)
        dest_path = os.path.join(dest_dir, fname)

        if os.path.normpath(os.path.dirname(path)) == os.path.normpath(dest_dir):
            already_ok += 1
            continue
        if os.path.exists(dest_path) and files_are_identical(path, dest_path):
            duplicates += 1
            continue

        rel = os.path.relpath(path, doc_source)
        preview_lines.append(f"{rel[:50].ljust(52)} →  {dtype}/{fname}")
        to_move.append((path, dest_dir, fname))

    summary = []
    if already_ok: summary.append(t("sum_ok_docs", n=already_ok))
    if duplicates: summary.append(t("sum_duplicates", n=duplicates))
    if summary:    preview_lines = summary + ["─" * 72] + preview_lines

    if not to_move:
        messagebox.showinfo(t("all_sorted_title"), t("all_sorted_docs", n=already_ok))
        return

    if show_preview(t("preview_docs", n=len(to_move)), preview_lines, len(to_move)):
        threading.Thread(
            target=run_moves,
            args=(to_move, "moving_docs", doc_source, show_done),
            daemon=True,
        ).start()

# ---------------------------------------------------------------------------
# ── LANGUE ──
# ---------------------------------------------------------------------------

_ui_refs = {}

def set_language(lang):
    global current_lang
    current_lang = lang.lower()
    root.title(t("window_title"))

    _ui_refs["tab_media_btn"].configure(text=t("tab_media"))
    _ui_refs["tab_docs_btn"].configure(text=t("tab_docs"))

    if not media_source:
        _ui_refs["media_folder_label"].configure(text=t("no_folder"))
    if not doc_source:
        _ui_refs["doc_folder_label"].configure(text=t("no_folder"))

    _ui_refs["choose_media_btn"].configure(text=t("choose_folder"))
    canvas.itemconfigure(_ui_refs["fmt_txt_id"], text=t("sort_format_label"))
    _ui_refs["format_selector"].configure(values=[t("fmt_ym"), t("fmt_y")])
    _ui_refs["format_selector"].set(t("fmt_ym") if sort_format == "year_month" else t("fmt_y"))
    _ui_refs["sort_button"].configure(
        text=t("sort_btn_ym") if sort_format == "year_month" else t("sort_btn_y"))

    _ui_refs["choose_doc_btn"].configure(text=t("choose_folder"))
    _ui_refs["sort_docs_btn"].configure(text=t("sort_docs_btn"))
    _ui_refs["legend_title_lbl"].configure(text=t("legend_title"))
    _ui_refs["legend_types_lbl"].configure(text=t("legend_types"))
    _ui_refs["quit_btn"].configure(text=t("quit"))

# ---------------------------------------------------------------------------
# ── INTERFACE ──
# ---------------------------------------------------------------------------

WIN_W, WIN_H = 520, 600

ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title(t("window_title"))
root.geometry(f"{WIN_W}x{WIN_H}")
root.resizable(False, False)
root.configure(fg_color=PASTEL_BG)

# --- Image de fond dessinée sur un Canvas tkinter ---
# L'image est dessinée directement sur le canvas à ~30% d'opacité.
# Les espaces entre les widgets (qui sont collés sur le canvas) montrent l'image.
bg_photo = None
try:
    bg_pil = Image.open(
        "C:/Users/MarieBaghdassarian/Documents/Tri_Dossier/file_icon.png"
    ).convert("RGBA").resize((WIN_W, WIN_H), Image.LANCZOS)
    r, g, b, a = bg_pil.split()
    a = a.point(lambda x: int(x * 0.30))
    bg_pil = Image.merge("RGBA", (r, g, b, a))
    base = Image.new("RGBA", (WIN_W, WIN_H), (254, 246, 246, 255))
    bg_photo = ImageTk.PhotoImage(Image.alpha_composite(base, bg_pil).convert("RGB"))
except Exception:
    pass

canvas = tk.Canvas(root, width=WIN_W, height=WIN_H,
                   highlightthickness=0, bg=PASTEL_BG, bd=0)
canvas.pack(fill="both", expand=True)
if bg_photo:
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)

# Helper : colle un widget CTk sur le canvas à une position précise
def cw(widget, x, y, anchor="center", width=None, height=None):
    kw = {}
    if width:  kw["width"]  = width
    if height: kw["height"] = height
    return canvas.create_window(x, y, window=widget, anchor=anchor, **kw)

# ---------------------------------------------------------------------------
# Sélecteur de langue (en haut à droite)
# ---------------------------------------------------------------------------
lang_btn = ctk.CTkSegmentedButton(
    canvas, values=["FR", "EN"], command=set_language,
    width=90, height=26, font=("Helvetica", 10, "bold"),
    fg_color="#F5DEDE", selected_color="#FF8C94", selected_hover_color="#FF747D",
    unselected_color="#F5DEDE", unselected_hover_color="#F0C8C8",
    text_color="#2C3E50", corner_radius=13,
)
lang_btn.set("FR")
cw(lang_btn, WIN_W - 14, 16, anchor="ne")

# ---------------------------------------------------------------------------
# Barre d'onglets personnalisée (deux boutons)
# ---------------------------------------------------------------------------
active_tab = ["media"]

def _active(btn):
    btn.configure(fg_color="#FF8C94", hover_color="#FF747D", text_color="white")

def _inactive(btn):
    btn.configure(fg_color="#F5DEDE", hover_color="#F0C8C8", text_color="#666")

def switch_tab(tab):
    active_tab[0] = tab
    if tab == "media":
        _active(tab_media_btn);  _inactive(tab_docs_btn)
        for i in media_ids: canvas.itemconfigure(i, state="normal")
        for i in docs_ids:  canvas.itemconfigure(i, state="hidden")
    else:
        _inactive(tab_media_btn); _active(tab_docs_btn)
        for i in media_ids: canvas.itemconfigure(i, state="hidden")
        for i in docs_ids:  canvas.itemconfigure(i, state="normal")

tab_media_btn = ctk.CTkButton(canvas, text=t("tab_media"), width=218, height=34,
                               font=("Helvetica", 11, "bold"), corner_radius=17,
                               command=lambda: switch_tab("media"))
_active(tab_media_btn)

tab_docs_btn  = ctk.CTkButton(canvas, text=t("tab_docs"),  width=218, height=34,
                               font=("Helvetica", 11, "bold"), corner_radius=17,
                               command=lambda: switch_tab("docs"))
_inactive(tab_docs_btn)

cw(tab_media_btn, WIN_W//2 - 113, 54, anchor="center")
cw(tab_docs_btn,  WIN_W//2 + 113, 54, anchor="center")

# ---------------------------------------------------------------------------
# Onglet MÉDIAS
# ---------------------------------------------------------------------------
media_folder_label = ctk.CTkLabel(
    canvas, text=t("no_folder"), font=("Helvetica", 12, "bold"),
    corner_radius=10, height=34, fg_color="#FADBD8", text_color="#7B4F50")

choose_media_btn = ctk.CTkButton(
    canvas, text=t("choose_folder"), command=select_media_folder,
    fg_color="#FF8C94", hover_color="#FF747D", text_color="white",
    font=("Helvetica", 12, "bold"), height=42, corner_radius=21)

# Texte "Format de tri" dessiné directement sur le canvas → transparent sur l'image
fmt_txt_id = canvas.create_text(WIN_W//2, 203, text=t("sort_format_label"),
                                 font=("Helvetica", 11), fill="#555555", anchor="center")

format_selector = ctk.CTkSegmentedButton(
    canvas, values=[t("fmt_ym"), t("fmt_y")], command=on_format_change,
    font=("Helvetica", 11, "bold"), fg_color="#F0E0E0",
    selected_color="#A8E6CF", selected_hover_color="#89D9BB",
    unselected_color="#F0E0E0", unselected_hover_color="#E0D0D0",
    text_color="#2C3E50", height=32, corner_radius=16)
format_selector.set(t("fmt_ym"))

sort_button = ctk.CTkButton(
    canvas, text=t("sort_btn_ym"), command=organize_media,
    fg_color="#A8E6CF", hover_color="#89D9BB", text_color="#2C3E50",
    font=("Helvetica", 12, "bold"), height=42, corner_radius=21)

m1 = cw(media_folder_label, WIN_W//2, 105, anchor="center", width=462)
m2 = cw(choose_media_btn,   WIN_W//2, 155, anchor="center", width=462)
m3 = fmt_txt_id
m4 = cw(format_selector,    WIN_W//2, 232, anchor="center", width=462)
m5 = cw(sort_button,        WIN_W//2, 280, anchor="center", width=462)
media_ids = [m1, m2, m3, m4, m5]

# ---------------------------------------------------------------------------
# Onglet DOCUMENTS
# ---------------------------------------------------------------------------
doc_folder_label = ctk.CTkLabel(
    canvas, text=t("no_folder"), font=("Helvetica", 12, "bold"),
    corner_radius=10, height=34, fg_color="#D6EAF8", text_color="#1A5276")

choose_doc_btn = ctk.CTkButton(
    canvas, text=t("choose_folder"), command=select_doc_folder,
    fg_color="#85C1E9", hover_color="#5DADE2", text_color="white",
    font=("Helvetica", 12, "bold"), height=42, corner_radius=21)

sort_docs_btn = ctk.CTkButton(
    canvas, text=t("sort_docs_btn"), command=organize_docs,
    fg_color="#A9CCE3", hover_color="#7FB3D3", text_color="#1A3D5C",
    font=("Helvetica", 12, "bold"), height=42, corner_radius=21)

legend_frame = ctk.CTkFrame(canvas, fg_color="#EBF5FB", corner_radius=10)
legend_title_lbl = ctk.CTkLabel(legend_frame, text=t("legend_title"),
                                 font=("Helvetica", 10, "bold"), fg_color="transparent",
                                 text_color="#1A5276")
legend_title_lbl.pack(pady=(6, 2))
legend_types_lbl = ctk.CTkLabel(legend_frame, text=t("legend_types"),
                                 font=("Helvetica", 10), fg_color="transparent",
                                 text_color="#555", wraplength=400)
legend_types_lbl.pack(pady=(0, 8))

d1 = cw(doc_folder_label, WIN_W//2, 105, anchor="center", width=462)
d2 = cw(choose_doc_btn,   WIN_W//2, 155, anchor="center", width=462)
d3 = cw(sort_docs_btn,    WIN_W//2, 207, anchor="center", width=462)
d4 = cw(legend_frame,     WIN_W//2, 272, anchor="center", width=462)
docs_ids = [d1, d2, d3, d4]

# Démarrer sur l'onglet Médias
for i in docs_ids:
    canvas.itemconfigure(i, state="hidden")

# ---------------------------------------------------------------------------
# Bouton Quitter
# ---------------------------------------------------------------------------
quit_btn = ctk.CTkButton(
    canvas, text=t("quit"), command=root.quit,
    fg_color="#BDC3C7", hover_color="#A0A6A8", text_color="#2C3E50",
    font=("Helvetica", 11, "bold"), height=34, corner_radius=17)
cw(quit_btn, WIN_W//2, 555, anchor="center", width=180)

# ---------------------------------------------------------------------------
# Enregistrement des refs i18n
# ---------------------------------------------------------------------------
_ui_refs.update({
    "tab_media_btn":      tab_media_btn,
    "tab_docs_btn":       tab_docs_btn,
    "media_folder_label": media_folder_label,
    "doc_folder_label":   doc_folder_label,
    "choose_media_btn":   choose_media_btn,
    "fmt_txt_id":         fmt_txt_id,
    "format_selector":    format_selector,
    "sort_button":        sort_button,
    "choose_doc_btn":     choose_doc_btn,
    "sort_docs_btn":      sort_docs_btn,
    "legend_title_lbl":   legend_title_lbl,
    "legend_types_lbl":   legend_types_lbl,
    "quit_btn":           quit_btn,
})

root.mainloop()
