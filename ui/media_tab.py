"""ui/media_tab.py - Media tab widgets and logic (PIL-rendered, no CTk halos)."""

import os
import threading
from tkinter import filedialog, messagebox

import state
from config import WIN_W
from core.sorter import run_moves, scan_media
from i18n import t
from ui.dialogs import make_progress_win, show_done, show_preview
from ui.widgets import CanvasButton, CanvasLabel, CanvasSegmented


def build_media_tab(canvas, root):
    """Build the Media tab on canvas.  Returns (ids, refs)."""

    CX = WIN_W // 2   # horizontal centre = 260

    # -- Folder label --------------------------------------------------
    folder_label = CanvasLabel(
        canvas, CX, 125, 462, 34,
        t("no_folder"),
        fg_color="#FADBD8", text_color="#7B4F50",
        font_size=12, bold=True, radius=17,
    )

    def _select_folder():
        chosen = filedialog.askdirectory()
        if chosen:
            state.media_source = chosen
            folder_label.configure(
                text=os.path.basename(chosen) or chosen,
                fg_color="#FFFFFF", text_color="#2C3E50",
            )

    # -- Choose folder button ------------------------------------------
    choose_btn = CanvasButton(
        canvas, CX, 175, 462, 42,
        t("choose_folder"),
        fg_color="#FF8C94", hover_color="#FF747D", text_color="#FFFFFF",
        font_size=12, bold=True,
        command=_select_folder,
    )

    # -- Sort format label (plain canvas text) -------------------------
    fmt_txt_id = canvas.create_text(
        CX, 223, text=t("sort_format_label"),
        font=("Helvetica", 11), fill="#555555", anchor="center",
    )

    # -- Format selector -----------------------------------------------
    def _on_format_change(value):
        state.sort_format = "year" if value == t("fmt_y") else "year_month"
        sort_btn.configure(
            text=t("sort_btn_ym") if state.sort_format == "year_month"
            else t("sort_btn_y"))

    format_selector = CanvasSegmented(
        canvas, CX, 252, 462, 32,
        [t("fmt_ym"), t("fmt_y")],
        fg_color="#F0E0E0",
        selected_color="#A8E6CF",
        text_color="#2C3E50",
        command=_on_format_change,
    )
    format_selector.set(t("fmt_ym"))

    # -- Organise logic ------------------------------------------------
    def _organize():
        if not state.media_source:
            messagebox.showwarning("", t("warn_no_folder"))
            return

        scan_win, scan_update = make_progress_win(root, "scanning")

        def _scan_task():
            to_move, preview_lines, already_ok, duplicates, total_found = \
                scan_media(state.media_source, state.sort_format,
                           update_cb=scan_update)

            summary = []
            if already_ok:
                summary.append(t("sum_already_ok", n=already_ok))
            if duplicates:
                summary.append(t("sum_duplicates", n=duplicates))
            if summary:
                preview_lines = summary + ["-" * 72] + preview_lines

            def _finalize():
                scan_win.destroy()
                if not to_move:
                    messagebox.showinfo(t("all_sorted_title"),
                                        t("all_sorted_media", n=total_found))
                    return
                if show_preview(root, t("preview_media", n=len(to_move)),
                                preview_lines, len(to_move)):
                    move_win, move_update = make_progress_win(root, "moving_media")

                    def _move_task():
                        moved, errors = run_moves(
                            to_move, state.media_source, update_cb=move_update)
                        root.after(0, lambda: [move_win.destroy(),
                                               show_done(moved, errors)])

                    threading.Thread(target=_move_task, daemon=True).start()

            root.after(0, _finalize)

        threading.Thread(target=_scan_task, daemon=True).start()

    # -- Sort button ---------------------------------------------------
    sort_btn = CanvasButton(
        canvas, CX, 300, 462, 42,
        t("sort_btn_ym"),
        fg_color="#A8E6CF", hover_color="#89D9BB", text_color="#2C3E50",
        font_size=12, bold=True,
        command=_organize,
    )

    ids = [
        folder_label.item_id,
        choose_btn.item_id,
        fmt_txt_id,
        format_selector.item_id,
        sort_btn.item_id,
    ]

    refs = {
        "folder_label":    folder_label,
        "choose_btn":      choose_btn,
        "fmt_txt_id":      fmt_txt_id,
        "format_selector": format_selector,
        "sort_btn":        sort_btn,
    }

    return ids, refs
