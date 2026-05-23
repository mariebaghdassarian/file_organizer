"""ui/widgets.py - PIL-rendered canvas widgets with no CTk frames (zero halos)."""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageTk


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

def _load_font(size=12, bold=False):
    """Load a TrueType font, falling back to PIL default."""
    if bold:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _hex_rgb(h):
    """Convert '#RRGGBB' or '#RGB' to (R, G, B) tuple."""
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _clean(text):
    """Strip non-BMP characters (emoji) that PIL TrueType fonts cannot render."""
    return "".join(c for c in text if ord(c) < 0x10000).strip()


def _measure(draw, text, font):
    """Return (width, height, x_offset, y_offset) for text."""
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]
    except AttributeError:
        tw, th = draw.textsize(text, font=font)
        return tw, th, 0, 0


def _center_text(draw, text, font, x0, y0, x1, y1, color):
    """Draw text centered inside the rectangle (x0,y0)-(x1,y1)."""
    tw, th, ox, oy = _measure(draw, text, font)
    cx = x0 + (x1 - x0 - tw) // 2 - ox
    cy = y0 + (y1 - y0 - th) // 2 - oy
    draw.text((cx, cy), text, fill=color, font=font)


# ---------------------------------------------------------------------------
# Image builders
# ---------------------------------------------------------------------------

def _pill(w, h, bg_hex, text, tc_hex, font_size=13, bold=True, radius=None):
    """Return an RGBA PIL Image: pill-shaped button with centered text."""
    r = radius if radius is not None else h // 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = _hex_rgb(bg_hex) + (255,)
    try:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=bg)
    except AttributeError:
        d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    font = _load_font(font_size, bold)
    tc = _hex_rgb(tc_hex) + (255,)
    _center_text(d, _clean(text), font, 0, 0, w, h, tc)
    return img


def _segmented(w, h, values, selected, fg, sel_color, tc):
    """Return an RGBA PIL Image: two-pill segmented control."""
    gap = 4
    seg_w = (w - gap) // 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = _load_font(11, True)
    r = h // 2
    tc_rgb = _hex_rgb(tc) + (255,)
    for i, val in enumerate(values):
        x0 = i * (seg_w + gap)
        x1 = x0 + seg_w - 1
        bg = _hex_rgb(sel_color if val == selected else fg) + (255,)
        try:
            d.rounded_rectangle([x0, 0, x1, h - 1], radius=r, fill=bg)
        except AttributeError:
            d.rectangle([x0, 0, x1, h - 1], fill=bg)
        _center_text(d, _clean(val), font, x0, 0, x1 + 1, h, tc_rgb)
    return img


def _legend_img(w, h, title, types_text, bg_hex):
    """Return an RGBA PIL Image: rounded legend box with title and body text."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = _hex_rgb(bg_hex) + (255,)
    try:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=bg)
    except AttributeError:
        d.rectangle([0, 0, w - 1, h - 1], fill=bg)

    # Title (bold, centered)
    ft_title = _load_font(10, True)
    tc_title = _hex_rgb("#1A5276") + (255,)
    _center_text(d, _clean(title), ft_title, 0, 4, w, 24, tc_title)

    # Body text (wrapped, centered)
    ft_body = _load_font(10, False)
    tc_body = _hex_rgb("#555555") + (255,)
    body = _clean(types_text)
    wrapped_lines = textwrap.wrap(body, width=62)
    y = 26
    for line in wrapped_lines:
        tw, th, ox, oy = _measure(d, line, ft_body)
        cx = (w - tw) // 2 - ox
        d.text((cx, y - oy), line, fill=tc_body, font=ft_body)
        y += th + 3

    return img


# ---------------------------------------------------------------------------
# Widget classes
# ---------------------------------------------------------------------------

class CanvasButton:
    """PIL-rendered button on a tkinter Canvas.  No CTk frame, zero halos."""

    def __init__(self, canvas, x, y, width, height, text,
                 fg_color, hover_color, text_color,
                 font_size=13, bold=True, radius=None, command=None):
        self._c        = canvas
        self._x        = x
        self._y        = y
        self._w        = width
        self._h        = height
        self._text     = text
        self._fg       = fg_color
        self._hov      = hover_color
        self._tc       = text_color
        self._fs       = font_size
        self._bold     = bold
        self._r        = radius
        self._cmd      = command
        self._hovered  = False
        self._photo    = None
        self.item_id   = None
        self._render(init=True)

    def _render(self, init=False):
        color = self._hov if self._hovered else self._fg
        img = _pill(self._w, self._h, color, self._text, self._tc,
                    self._fs, self._bold, self._r)
        self._photo = ImageTk.PhotoImage(img)
        if init:
            self.item_id = self._c.create_image(
                self._x, self._y, anchor="center", image=self._photo)
            self._c.tag_bind(self.item_id, "<Button-1>", self._on_click)
            self._c.tag_bind(self.item_id, "<Enter>",    self._on_enter)
            self._c.tag_bind(self.item_id, "<Leave>",    self._on_leave)
        else:
            self._c.itemconfigure(self.item_id, image=self._photo)

    def _on_click(self, _e):
        if self._cmd:
            self._cmd()

    def _on_enter(self, _e):
        self._hovered = True
        self._render()

    def _on_leave(self, _e):
        self._hovered = False
        self._render()

    def configure(self, text=None, fg_color=None, hover_color=None, text_color=None):
        changed = False
        if text        is not None: self._text = text;       changed = True
        if fg_color    is not None: self._fg   = fg_color;   changed = True
        if hover_color is not None: self._hov  = hover_color; changed = True
        if text_color  is not None: self._tc   = text_color; changed = True
        if changed:
            self._render()


class CanvasLabel:
    """PIL-rendered label (no interaction) on a tkinter Canvas."""

    def __init__(self, canvas, x, y, width, height, text,
                 fg_color, text_color, font_size=12, bold=True, radius=None):
        self._c      = canvas
        self._x      = x
        self._y      = y
        self._w      = width
        self._h      = height
        self._text   = text
        self._fg     = fg_color
        self._tc     = text_color
        self._fs     = font_size
        self._bold   = bold
        self._r      = radius
        self._photo  = None
        self.item_id = None
        self._render(init=True)

    def _render(self, init=False):
        img = _pill(self._w, self._h, self._fg, self._text, self._tc,
                    self._fs, self._bold, self._r)
        self._photo = ImageTk.PhotoImage(img)
        if init:
            self.item_id = self._c.create_image(
                self._x, self._y, anchor="center", image=self._photo)
        else:
            self._c.itemconfigure(self.item_id, image=self._photo)

    def configure(self, text=None, fg_color=None, text_color=None):
        changed = False
        if text       is not None: self._text = text;     changed = True
        if fg_color   is not None: self._fg   = fg_color; changed = True
        if text_color is not None: self._tc   = text_color; changed = True
        if changed:
            self._render()


class CanvasSegmented:
    """PIL-rendered two-segment selector on a tkinter Canvas."""

    def __init__(self, canvas, x, y, width, height, values,
                 fg_color, selected_color, text_color, command=None):
        self._c        = canvas
        self._x        = x
        self._y        = y
        self._w        = width
        self._h        = height
        self._values   = list(values)
        self._selected = values[0] if values else ""
        self._fg       = fg_color
        self._sel      = selected_color
        self._tc       = text_color
        self._cmd      = command
        self._photo    = None
        self.item_id   = None
        self._render(init=True)

    def _render(self, init=False):
        img = _segmented(self._w, self._h, self._values, self._selected,
                         self._fg, self._sel, self._tc)
        self._photo = ImageTk.PhotoImage(img)
        if init:
            self.item_id = self._c.create_image(
                self._x, self._y, anchor="center", image=self._photo)
            self._c.tag_bind(self.item_id, "<Button-1>", self._on_click)
        else:
            self._c.itemconfigure(self.item_id, image=self._photo)

    def _on_click(self, event):
        # Left half or right half of the image?
        idx = 0 if event.x < self._x else 1
        if 0 <= idx < len(self._values):
            self._selected = self._values[idx]
            self._render()
            if self._cmd:
                self._cmd(self._selected)

    def set(self, value):
        self._selected = value
        self._render()

    def configure(self, values=None, fg_color=None, selected_color=None,
                  text_color=None):
        changed = False
        if values is not None:
            self._values = list(values)
            if self._selected not in self._values and self._values:
                self._selected = self._values[0]
            changed = True
        if fg_color       is not None: self._fg  = fg_color;       changed = True
        if selected_color is not None: self._sel = selected_color; changed = True
        if text_color     is not None: self._tc  = text_color;     changed = True
        if changed:
            self._render()


class CanvasLegend:
    """PIL-rendered legend box (title + body text) on a tkinter Canvas."""

    def __init__(self, canvas, x, y, width, height, title, types_text,
                 bg_color="#EBF5FB"):
        self._c      = canvas
        self._x      = x
        self._y      = y
        self._w      = width
        self._h      = height
        self._title  = title
        self._types  = types_text
        self._bg     = bg_color
        self._photo  = None
        self.item_id = None
        self._render(init=True)

    def _render(self, init=False):
        img = _legend_img(self._w, self._h, self._title, self._types, self._bg)
        self._photo = ImageTk.PhotoImage(img)
        if init:
            self.item_id = self._c.create_image(
                self._x, self._y, anchor="center", image=self._photo)
        else:
            self._c.itemconfigure(self.item_id, image=self._photo)

    def configure(self, title=None, types_text=None):
        changed = False
        if title      is not None: self._title = title;      changed = True
        if types_text is not None: self._types = types_text; changed = True
        if changed:
            self._render()
