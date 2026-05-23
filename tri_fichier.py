import os
import re
import shutil
import hashlib
import exifread
import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image

# ---------------------------------------------------------------------------
# Extensions prises en charge
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

source_folder = ""

# ---------------------------------------------------------------------------
# Extraction de date
# ---------------------------------------------------------------------------

def get_exif_date(file_path):
    """Date EXIF via exifread (JPEG, TIFF, RAW…)"""
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
        for key in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
            if key in tags:
                return datetime.strptime(str(tags[key]), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # Fallback Pillow (HEIC, WEBP…)
    try:
        with Image.open(file_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id in (36867, 36868, 306):   # DateTimeOriginal, DateTimeDigitized, DateTime
                    if tag_id in exif:
                        return datetime.strptime(exif[tag_id], "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    return None


def get_video_date(file_path):
    """Date de création vidéo via pymediainfo (MP4, MOV, MKV…)"""
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
                # Format ISO : "2023-10-15T14:30:22Z" ou "2023-10-15T14:30:22+0200"
                m = re.search(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})", field)
                if m:
                    try:
                        d = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                        if 1980 < d.year < 2100:
                            return d
                    except Exception:
                        pass
                # Format MediaInfo classique : "UTC 2023-10-15 14:30:22"
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
    """
    Tente de lire une date dans le nom du fichier.
    Gère les patterns courants de screenshots :
      - Screenshot_20231015_143022.png  (Android)
      - Screenshot 2023-10-15 at 14.30.22.png  (macOS)
      - Capture d'écran 2023-10-15 à 14.30.22.png  (macOS FR)
      - IMG_20231015_143022.jpg
      - 2023-10-15_14-30-22_…
    """
    name = os.path.splitext(filename)[0]
    patterns = [
        # YYYY-MM-DD avec heure
        (r"(\d{4})[-_](\d{2})[-_](\d{2})[T_ -](\d{2})[.:\-](\d{2})[.:\-](\d{2})", 6),
        # YYYYMMDD_HHMMSS
        (r"(\d{4})(\d{2})(\d{2})[_\-](\d{2})(\d{2})(\d{2})(?!\d)", 6),
        # YYYY-MM-DD seul
        (r"(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)", 3),
        # YYYYMMDD seul (8 chiffres consécutifs)
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
    """
    Retourne la meilleure date disponible pour un fichier média, dans cet ordre :
    1. Données EXIF (images)
    2. Métadonnées vidéo (mediainfo)
    3. Date dans le nom du fichier (screenshots, etc.)
    4. Date système du fichier (fallback)
    """
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    date = None

    if ext in IMAGE_EXTENSIONS:
        date = get_exif_date(file_path)

    if date is None and ext in VIDEO_EXTENSIONS:
        date = get_video_date(file_path)

    if date is None:
        date = get_date_from_filename(filename)

    if date is None:
        try:
            ts = min(os.path.getmtime(file_path), os.path.getctime(file_path))
            date = datetime.fromtimestamp(ts)
        except Exception:
            pass

    return date


# ---------------------------------------------------------------------------
# Gestion des doublons
# ---------------------------------------------------------------------------

def files_are_identical(path_a, path_b):
    """Vrai si les deux fichiers ont la même taille ET le même hash MD5."""
    if os.path.getsize(path_a) != os.path.getsize(path_b):
        return False
    def md5(path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    return md5(path_a) == md5(path_b)


def unique_dest_path(dest_dir, filename):
    """
    Retourne un chemin de destination unique.
    Si un fichier du même nom existe déjà (mais est différent), ajoute _1, _2…
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
# Collecte des fichiers
# ---------------------------------------------------------------------------

def collect_all_media(folder):
    """Parcourt récursivement le dossier et retourne tous les fichiers média."""
    result = []
    for root_dir, dirs, files in os.walk(folder):
        # Ignorer les dossiers cachés
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if os.path.splitext(f)[1].lower() in ALL_MEDIA:
                result.append(os.path.join(root_dir, f))
    return result


def remove_empty_dirs(folder):
    """Supprime les sous-dossiers vides laissés après le tri."""
    for root_dir, dirs, files in os.walk(folder, topdown=False):
        if root_dir == folder:
            continue
        try:
            if not os.listdir(root_dir):
                os.rmdir(root_dir)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Interface — fonctions
# ---------------------------------------------------------------------------

def select_folder():
    global source_folder
    chosen = filedialog.askdirectory()
    if chosen:
        source_folder = chosen
        display = os.path.basename(chosen) or chosen
        folder_label.configure(
            text=f"📍 Dossier : {display}",
            fg_color="#FFFFFF",
            text_color="#2C3E50",
        )


def show_preview(title, lines, n_to_move):
    """Fenêtre d'aperçu avec confirmation. Retourne True si l'utilisateur confirme."""
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("750x520")
    win.grab_set()

    ctk.CTkLabel(
        win,
        text=f"{n_to_move} fichier(s) à déplacer",
        font=("Helvetica", 14, "bold"),
    ).pack(pady=10)

    text_area = ctk.CTkTextbox(win, wrap="none", font=("Consolas", 10))
    text_area.pack(padx=15, pady=5, fill="both", expand=True)
    text_area.insert("0.0", "\n".join(lines))
    text_area.configure(state="disabled")

    result = {"confirm": False}

    def on_confirm():
        result["confirm"] = True
        win.destroy()

    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(pady=15, fill="x")
    ctk.CTkButton(
        btn_frame, text="✅  Confirmer et trier", command=on_confirm,
        fg_color="#2ECC71", corner_radius=15, font=("Helvetica", 12, "bold"),
    ).pack(side="left", expand=True, padx=10)
    ctk.CTkButton(
        btn_frame, text="❌  Annuler", command=win.destroy,
        fg_color="#E74C3C", corner_radius=15, font=("Helvetica", 12, "bold"),
    ).pack(side="right", expand=True, padx=10)

    win.wait_window()
    return result["confirm"]


def organize_files():
    if not source_folder:
        messagebox.showwarning("Attention", "Veuillez d'abord choisir un dossier.")
        return

    # Fenêtre d'attente pendant le scan
    wait_win = ctk.CTkToplevel(root)
    wait_win.title("Analyse en cours…")
    wait_win.geometry("460x230")
    wait_win.grab_set()
    wait_win.resizable(False, False)

    ctk.CTkLabel(
        wait_win, text="Analyse des fichiers…", font=("Helvetica", 14, "bold")
    ).pack(pady=(20, 5))
    current_label = ctk.CTkLabel(wait_win, text="", font=("Helvetica", 10), text_color="gray")
    current_label.pack(pady=3)
    scan_bar = ctk.CTkProgressBar(wait_win, width=400)
    scan_bar.set(0)
    scan_bar.pack(pady=8)
    pct_label = ctk.CTkLabel(wait_win, text="0 %", font=("Helvetica", 11))
    pct_label.pack()

    def scan_task():
        all_files = collect_all_media(source_folder)
        total = len(all_files)

        if total == 0:
            root.after(
                0,
                lambda: [
                    wait_win.destroy(),
                    messagebox.showinfo("Info", "Aucun fichier média trouvé dans ce dossier."),
                ],
            )
            return

        to_move = []       # (src_path, dest_dir, filename)
        preview_lines = []
        already_ok = 0
        duplicates = 0

        for i, path in enumerate(all_files, 1):
            fname = os.path.basename(path)
            short = (fname[:38] + "…") if len(fname) > 40 else fname

            # Mise à jour barre de progression
            root.after(
                0,
                lambda s=short, p=i / total: [
                    current_label.configure(text=s),
                    scan_bar.set(p),
                    pct_label.configure(text=f"{int(p * 100)} %"),
                ],
            )

            date = get_reliable_date(path)

            if date:
                dest_dir = os.path.join(
                    source_folder, date.strftime("%Y"), date.strftime("%Y-%m")
                )
                dest_path = os.path.join(dest_dir, fname)
                norm_src = os.path.normpath(path)
                norm_dst = os.path.normpath(dest_path)

                # Déjà exactement au bon endroit ?
                if norm_src == norm_dst:
                    already_ok += 1
                    continue

                # Doublon identique à destination ?
                if os.path.exists(dest_path) and files_are_identical(path, dest_path):
                    duplicates += 1
                    preview_lines.append(
                        f"[DOUBLON ignoré]  {os.path.relpath(path, source_folder)}"
                    )
                    continue

                rel_src = os.path.relpath(path, source_folder)
                rel_dst = os.path.join(date.strftime("%Y"), date.strftime("%Y-%m"), fname)
                preview_lines.append(f"{rel_src[:50].ljust(52)} →  {rel_dst}")
                to_move.append((path, dest_dir, fname))

            else:
                dest_dir = os.path.join(source_folder, "_A_TRIER_MANUELLEMENT")
                rel_src = os.path.relpath(path, source_folder)
                preview_lines.append(
                    f"{rel_src[:50].ljust(52)} →  _A_TRIER_MANUELLEMENT/{fname}"
                )
                to_move.append((path, dest_dir, fname))

        # Résumé en tête de l'aperçu
        summary = []
        if already_ok:
            summary.append(f"✅ {already_ok} fichier(s) déjà bien classé(s) — ignorés")
        if duplicates:
            summary.append(f"🔁 {duplicates} doublon(s) identique(s) déjà présent(s) — ignorés")
        if summary:
            preview_lines = summary + ["─" * 70] + preview_lines

        root.after(0, lambda: finalize_scan(wait_win, to_move, preview_lines, total))

    threading.Thread(target=scan_task, daemon=True).start()


def finalize_scan(wait_win, to_move, preview_lines, total_found):
    wait_win.destroy()

    if not to_move:
        messagebox.showinfo(
            "Tout est déjà trié !",
            f"{total_found} fichier(s) analysé(s).\nTout est déjà correctement classé. 🎉",
        )
        return

    if show_preview(f"Aperçu du tri — {len(to_move)} déplacement(s)", preview_lines, len(to_move)):
        progress_bar.set(0)
        threading.Thread(target=exec_sort, args=(to_move,), daemon=True).start()


def exec_sort(files_data):
    total = len(files_data)
    moved = 0
    errors = 0

    for i, (src, dest_dir, fname) in enumerate(files_data, 1):
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = unique_dest_path(dest_dir, fname)

        try:
            shutil.move(src, dest_path)
            moved += 1
        except Exception:
            errors += 1

        root.after(0, lambda v=i / total: progress_bar.set(v))

    # Nettoyer les dossiers vides
    remove_empty_dirs(source_folder)

    msg = f"✅ Tri terminé !\n{moved} fichier(s) déplacé(s)."
    if errors:
        msg += f"\n⚠️ {errors} erreur(s) — ces fichiers n'ont pas pu être déplacés."

    root.after(
        0,
        lambda: [
            messagebox.showinfo("Résultat", msg),
            progress_bar.set(0),
        ],
    )


# ---------------------------------------------------------------------------
# Interface — construction
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("Organisateur de Médias")
root.geometry("520x560")
root.resizable(False, False)

# Image de fond
try:
    img = Image.open("C:/Users/MarieBaghdassarian/Documents/Tri_Dossier/file_icon.png")
    img = img.resize((520, 560), Image.LANCZOS).convert("RGBA")
    bg_image = ctk.CTkImage(light_image=img, size=(520, 560))
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.place(relwidth=1, relheight=1)
except Exception:
    pass

main_frame = ctk.CTkFrame(root, fg_color="transparent")
main_frame.pack(expand=True, fill="both", padx=50, pady=20)

folder_label = ctk.CTkLabel(
    main_frame,
    text="📁 Aucun dossier sélectionné",
    font=("Helvetica", 13, "bold"),
    corner_radius=10,
    height=35,
    fg_color="#FADBD8",
)
folder_label.pack(pady=(10, 20), fill="x")

ctk.CTkButton(
    main_frame,
    text="CHOISIR UN DOSSIER",
    command=select_folder,
    fg_color="#FF8C94",
    hover_color="#FF747D",
    text_color="white",
    font=("Helvetica", 12, "bold"),
    height=45,
    corner_radius=22,
).pack(pady=8, fill="x")

ctk.CTkButton(
    main_frame,
    text="TRIER PAR DATE  (YYYY / YYYY-MM)",
    command=organize_files,
    fg_color="#A8E6CF",
    hover_color="#89D9BB",
    text_color="#2C3E50",
    font=("Helvetica", 12, "bold"),
    height=45,
    corner_radius=22,
).pack(pady=8, fill="x")

progress_bar = ctk.CTkProgressBar(
    main_frame, width=300, height=12, progress_color="#3498DB"
)
progress_bar.set(0)
progress_bar.pack(pady=25)

ctk.CTkButton(
    main_frame,
    text="Quitter",
    command=root.quit,
    fg_color="#95A5A6",
    text_color="white",
    font=("Helvetica", 12, "bold"),
    height=40,
    corner_radius=20,
).pack(pady=(5, 0))

root.mainloop()
