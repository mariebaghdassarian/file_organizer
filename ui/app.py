"""
ui/app.py - Main application window.

All interactive controls are PIL-rendered canvas items (CanvasButton /
CanvasSegmented): no CTk widget frames, no halos, no white borders.

DPI note: ctk.deactivate_automatic_dpi_awareness() is called before the
root is created so that geometry("WxH") = PIL image pixels exactly.
"""

import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

import state
from config import (
    BG_IMAGE_PATH, BG_OPACITY,
    CARD_ALPHA, CARD_X1, CARD_X2, CARD_Y1, CARD_Y2,
    PASTEL_BG, WIN_H, WIN_W,
)
from i18n import set_lang, t
from ui.docs_tab import build_docs_tab
from ui.media_tab import build_media_tab
from ui.widgets import CanvasButton, CanvasSegmented


class App:
    """Top-level application class.  Instantiate then call .run()."""

    def __init__(self) -> None:
        self._setup_root()
        self._build_canvas()
        self._build_language_selector()
        self._build_tabs()

    # ------------------------------------------------------------------
    # Root window
    # ------------------------------------------------------------------

    def _setup_root(self) -> None:
        ctk.set_appearance_mode("light")
        # Disable CTk DPI scaling so geometry("WxH") = PIL image pixel size.
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except Exception:
            try:
                ctk.set_widget_scaling(1.0)
                ctk.set_window_scaling(1.0)
            except Exception:
                pass
        self.root = ctk.CTk()
        self.root.title(t("window_title"))
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=PASTEL_BG)

    # ------------------------------------------------------------------
    # Canvas + background image + card layer
    # ------------------------------------------------------------------

    def _build_canvas(self) -> None:
        """Compose the background photo (illustration + card) onto canvas."""
        self._bg_photo = None

        _hex = PASTEL_BG.lstrip("#")
        pr, pg, pb = (int(_hex[i:i + 2], 16) for i in (0, 2, 4))

        try:
            raw = Image.open(BG_IMAGE_PATH).convert("RGBA").resize(
                (WIN_W, WIN_H), Image.LANCZOS)
            r, g, b, a = raw.split()
            a = a.point(lambda v: int(v * BG_OPACITY))
            raw = Image.merge("RGBA", (r, g, b, a))
            base = Image.new("RGBA", (WIN_W, WIN_H), (pr, pg, pb, 255))
            composite = Image.alpha_composite(base, raw)

            card = Image.new("RGBA", (WIN_W, WIN_H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(card)
            fill = (pr, pg, pb, CARD_ALPHA)
            try:
                draw.rounded_rectangle(
                    [CARD_X1, CARD_Y1, CARD_X2, CARD_Y2],
                    radius=20, fill=fill)
            except AttributeError:
                draw.rectangle([CARD_X1, CARD_Y1, CARD_X2, CARD_Y2], fill=fill)

            composite = Image.alpha_composite(composite, card)
            self._bg_photo = ImageTk.PhotoImage(composite.convert("RGB"))

        except Exception:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=WIN_W, height=WIN_H,
            highlightthickness=0, bg=PASTEL_BG, bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        if self._bg_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)

    # ------------------------------------------------------------------
    # Language selector  (top-right)
    # ------------------------------------------------------------------

    def _build_language_selector(self) -> None:
        # Pill width=96, height=30; top-right corner at (WIN_W-14, 18)
        # => centre at (WIN_W - 14 - 48, 18 + 15) = (458, 33)
        lang_x = WIN_W - 14 - 48
        lang_y = 18 + 15
        self._lang_btn = CanvasSegmented(
            self.canvas, lang_x, lang_y, 96, 30,
            ["FR", "EN"],
            fg_color="#E8A0A8",
            selected_color="#C0392B",
            text_color="#FFFFFF",
            command=self._on_language_change,
        )
        self._lang_btn.set("FR")

    # ------------------------------------------------------------------
    # Tab bar + content
    # ------------------------------------------------------------------

    def _build_tabs(self) -> None:
        self._active_tab = "media"

        self._tab_media_btn = CanvasButton(
            self.canvas, WIN_W // 2 - 113, 74, 218, 34,
            t("tab_media"),
            fg_color="#FF8C94", hover_color="#FF747D", text_color="#FFFFFF",
            font_size=12, bold=True,
            command=lambda: self._switch_tab("media"),
        )
        self._tab_docs_btn = CanvasButton(
            self.canvas, WIN_W // 2 + 113, 74, 218, 34,
            t("tab_docs"),
            fg_color="#F5DEDE", hover_color="#F0C8C8", text_color="#555555",
            font_size=12, bold=True,
            command=lambda: self._switch_tab("docs"),
        )

        self._media_ids, self._media_refs = build_media_tab(self.canvas, self.root)
        self._docs_ids,  self._docs_refs  = build_docs_tab(self.canvas, self.root)

        # Start on Media tab -> hide Docs widgets
        for wid in self._docs_ids:
            self.canvas.itemconfigure(wid, state="hidden")

        self._quit_btn = CanvasButton(
            self.canvas, WIN_W // 2, 555, 180, 34,
            t("quit"),
            fg_color="#BDC3C7", hover_color="#A0A6A8", text_color="#2C3E50",
            font_size=12, bold=True,
            command=self.root.quit,
        )

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    @staticmethod
    def _set_active_style(btn) -> None:
        btn.configure(fg_color="#FF8C94", hover_color="#FF747D",
                      text_color="#FFFFFF")

    @staticmethod
    def _set_inactive_style(btn) -> None:
        btn.configure(fg_color="#F5DEDE", hover_color="#F0C8C8",
                      text_color="#555555")

    def _switch_tab(self, tab: str) -> None:
        self._active_tab = tab
        if tab == "media":
            self._set_active_style(self._tab_media_btn)
            self._set_inactive_style(self._tab_docs_btn)
            for wid in self._media_ids:
                self.canvas.itemconfigure(wid, state="normal")
            for wid in self._docs_ids:
                self.canvas.itemconfigure(wid, state="hidden")
        else:
            self._set_inactive_style(self._tab_media_btn)
            self._set_active_style(self._tab_docs_btn)
            for wid in self._media_ids:
                self.canvas.itemconfigure(wid, state="hidden")
            for wid in self._docs_ids:
                self.canvas.itemconfigure(wid, state="normal")

    # ------------------------------------------------------------------
    # Language switching
    # ------------------------------------------------------------------

    def _on_language_change(self, lang: str) -> None:
        set_lang(lang)
        self.root.title(t("window_title"))

        self._tab_media_btn.configure(text=t("tab_media"))
        self._tab_docs_btn.configure(text=t("tab_docs"))

        # Media tab
        if not state.media_source:
            self._media_refs["folder_label"].configure(text=t("no_folder"))
        self._media_refs["choose_btn"].configure(text=t("choose_folder"))
        self.canvas.itemconfigure(
            self._media_refs["fmt_txt_id"], text=t("sort_format_label"))
        self._media_refs["format_selector"].configure(
            values=[t("fmt_ym"), t("fmt_y")])
        self._media_refs["format_selector"].set(
            t("fmt_ym") if state.sort_format == "year_month" else t("fmt_y"))
        self._media_refs["sort_btn"].configure(
            text=t("sort_btn_ym") if state.sort_format == "year_month"
            else t("sort_btn_y"))

        # Docs tab
        if not state.doc_source:
            self._docs_refs["folder_label"].configure(text=t("no_folder"))
        self._docs_refs["choose_btn"].configure(text=t("choose_folder"))
        self._docs_refs["sort_btn"].configure(text=t("sort_docs_btn"))
        self._docs_refs["legend"].configure(
            title=t("legend_title"),
            types_text=t("legend_types"),
        )

        self._quit_btn.configure(text=t("quit"))

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()
