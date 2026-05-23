"""ui/docs_tab.py - Documents tab widgets and logic (PIL-rendered, no CTk halos)."""

import os
import threading
from tkinter import filedialog, messagebox

import state
from config import WIN_W
from core.sorter import run_moves, scan_docs
from i18n import t
from ui.dialogs import make_progress_win, show_done, show_preview
from ui.widgets import CanvasButton, CanvasLabel, CanvasLegend


def build_docs_tab(canvas, root):
    """Build the Documents tab on canvas.  Returns (ids, refs)."""

    CX = WIN_W // 2   # horizontal centre = 260

    # -- Folder label --------------------------------------------------
    folder_label = CanvasLabel(
        canvas, CX, 125, 462, 34,
        t("no_folder"),
        fg_color="#D6EAF8", text_color="#1A5276",
        font_size=12, bold=True, radius=17,
    )

    def _select_folder():
        chosen = filedialog.askdirectory()
        if chosen:
            state.doc_source = chosen
            folder_label.configure(
                text=os.path.basename(chosen) or chosen,
                fg_color="#FFFFFF", text_color="#2C3E50",
            )

    # -- Choose folder button ------------------------------------------
    choose_btn = CanvasButton(
        canvas, CX, 175, 462, 42,
        t("choose_folder"),
        fg_color="#85C1E9", hover_color="#5DADE2", text_color="#FFFFFF",
        font_size=12, bold=True,
        command=_select_folder,
    )

    # -- Organise logic ------------------------------------------------
    def _organize():
        if not state.doc_source:
            messagebox.showwarning("", t("warn_no_folder"))
            return

        to_move, preview_lines, already_ok, duplicates = scan_docs(state.doc_source)

        summary = []
        if already_ok:
            summary.append(t("sum_ok_docs", n=already_ok))
        if duplicates:
            summary.append(t("sum_duplicates", n=duplicates))
        if summary:
            preview_lines = summary + ["-" * 72] + preview_lines

        if not to_move:
            messagebox.showinfo(t("all_sorted_title"),
                                t("all_sorted_docs", n=already_ok))
            return

        if show_preview(root, t("preview_docs", n=len(to_move)),
                        preview_lines, len(to_move)):
            move_win, move_update = make_progress_win(root, "moving_docs")

            def _move_task():
                moved, errors = run_moves(
                    to_move, state.doc_source, update_cb=move_update)
                root.after(0, lambda: [move_win.destroy(),
                                       show_done(moved, errors)])

            threading.Thread(target=_move_task, daemon=True).start()

    # -- Sort button ---------------------------------------------------
    sort_btn = CanvasButton(
        canvas, CX, 227, 462, 42,
        t("sort_docs_btn"),
        fg_color="#A9CCE3", hover_color="#7FB3D3", text_color="#1A3D5C",
        font_size=12, bold=True,
        command=_organize,
    )

    # -- Legend --------------------------------------------------------
    legend = CanvasLegend(
        canvas, CX, 296, 462, 64,
        t("legend_title"), t("legend_types"),
        bg_color="#EBF5FB",
    )

    ids = [
        folder_label.item_id,
        choose_btn.item_id,
        sort_btn.item_id,
        legend.item_id,
    ]

    refs = {
        "folder_label": folder_label,
        "choose_btn":   choose_btn,
        "sort_btn":     sort_btn,
        "legend":       legend,
    }

    return ids, refs
