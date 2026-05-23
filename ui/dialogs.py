"""
ui/dialogs.py — Reusable dialog windows.

  make_progress_win(root, title_key)  →  (window, update_fn)
  show_preview(root, title, lines, n)  →  bool (True = confirmed)
  show_done(moved, errors)             →  None
"""

import time
from collections.abc import Callable

import customtkinter as ctk
from tkinter import messagebox

from config import PASTEL_BG
from core.file_utils import fmt_time
from i18n import t

ProgressUpdate = Callable[[int, int, str], None]   # (current, total, filename)


# ---------------------------------------------------------------------------
# Progress window
# ---------------------------------------------------------------------------

def make_progress_win(root: ctk.CTk, title_key: str) -> tuple[ctk.CTkToplevel, ProgressUpdate]:
    """Create a progress window for a long-running operation.

    Returns
    -------
    (win, update_fn)

    Call ``update_fn(i, total, filename)`` from any thread; it will schedule
    the UI refresh on the main thread via ``root.after()``.
    """
    win = ctk.CTkToplevel(root)
    win.title(t(title_key))
    win.geometry("500x285")
    win.grab_set()
    win.resizable(False, False)
    win.configure(fg_color=PASTEL_BG)

    start_time = [time.time()]

    ctk.CTkLabel(win, text=t(title_key), font=("Helvetica", 14, "bold"),
                 fg_color="transparent").pack(pady=(18, 2))

    lbl_file = ctk.CTkLabel(win, text="", font=("Helvetica", 10),
                             text_color="#777", fg_color="transparent")
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
                           font=("Helvetica", 11), fg_color="transparent",
                           text_color="#555")
    lbl_el.pack(side="left", padx=22)

    lbl_rm = ctk.CTkLabel(frm_t, text=t("lbl_remaining", t="—"),
                           font=("Helvetica", 11), fg_color="transparent",
                           text_color="#555")
    lbl_rm.pack(side="left", padx=22)

    def update(i: int, total: int, filename: str = "") -> None:
        if total == 0:
            return
        elapsed = time.time() - start_time[0]
        short   = (filename[:44] + "…") if len(filename) > 46 else filename
        rem_str = f"~{fmt_time(elapsed / i * total - elapsed)}" if i > 0 else "—"
        # Schedule on main thread (safe to call from any thread)
        root.after(0, lambda: [
            lbl_file.configure(text=short),
            lbl_count.configure(text=f"{i} / {total}"),
            bar.set(i / total),
            lbl_el.configure(text=t("lbl_elapsed",   t=fmt_time(elapsed))),
            lbl_rm.configure(text=t("lbl_remaining", t=rem_str)),
        ])

    return win, update


# ---------------------------------------------------------------------------
# Preview / confirmation dialog
# ---------------------------------------------------------------------------

def show_preview(root: ctk.CTk, title: str, lines: list[str], n_to_move: int) -> bool:
    """Show a scrollable preview of planned moves and ask for confirmation.

    Returns ``True`` if the user clicked Confirm, ``False`` if cancelled.
    """
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("750x530")
    win.grab_set()
    win.configure(fg_color=PASTEL_BG)

    ctk.CTkLabel(win, text=t("n_to_move", n=n_to_move),
                 font=("Helvetica", 14, "bold"),
                 fg_color="transparent").pack(pady=10)

    text_area = ctk.CTkTextbox(
        win, wrap="none", font=("Consolas", 10),
        fg_color="#FFFFFF", border_color="#E0E0E0", border_width=1)
    text_area.pack(padx=15, pady=5, fill="both", expand=True)
    text_area.insert("0.0", "\n".join(lines))
    text_area.configure(state="disabled")

    result = {"confirm": False}

    def on_confirm() -> None:
        result["confirm"] = True
        win.destroy()

    frm = ctk.CTkFrame(win, fg_color="transparent")
    frm.pack(pady=15, fill="x")

    ctk.CTkButton(
        frm, text=t("confirm"), command=on_confirm,
        fg_color="#2ECC71", hover_color="#27AE60",
        font=("Helvetica", 12, "bold"), corner_radius=15,
    ).pack(side="left", expand=True, padx=12)

    ctk.CTkButton(
        frm, text=t("cancel_btn"), command=win.destroy,
        fg_color="#E74C3C", hover_color="#C0392B",
        font=("Helvetica", 12, "bold"), corner_radius=15,
    ).pack(side="right", expand=True, padx=12)

    win.wait_window()
    return result["confirm"]


# ---------------------------------------------------------------------------
# Completion message
# ---------------------------------------------------------------------------

def show_done(moved: int, errors: int) -> None:
    """Show a messagebox summarising the completed operation."""
    msg = t("result_ok", n=moved)
    if errors:
        msg += t("result_errors", e=errors)
    messagebox.showinfo(t("result_title"), msg)
