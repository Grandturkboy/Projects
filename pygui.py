"""
pygui.py — Pygame sidebar UI library
=====================================
A lightweight, self-contained UI panel for Pygame simulations.
Inspired by the tkinter sidebar aesthetic: sections, sliders,
checkboxes, buttons, labels, and color pickers.

Usage
-----
    from pygui import GUI

    gui = GUI(width=240)                 # creates a 240px sidebar
    sim_card = gui.add_section("Simulation")
    speed_sl  = gui.add_slider(sim_card,  "Speed",      0,   10,  3.0)
    count_sl  = gui.add_slider(sim_card,  "Boid count", 10, 500, 100, step=1)

    disp_card = gui.add_section("Display")
    trails_cb = gui.add_checkbox(disp_card, "Show trails",  False)
    grid_cb   = gui.add_checkbox(disp_card, "Show grid",    False)

    gui.add_button(disp_card, "Reset", callback=reset_sim)

    # In your game loop:
    gui.handle_event(event)          # pass every pygame event
    canvas_x_offset = gui.width      # offset your simulation drawing

    # In your draw function:
    gui.draw(screen)

    # Read values:
    speed = speed_sl.value
    show_trails = trails_cb.value
"""

import pygame

# ── Palette ───────────────────────────────────────────────────────────────────
_C = {
    "sidebar_bg":   (22,  33,  62),
    "section_bg":   (15,  52,  96),
    "header_bg":    (233, 69,  96),
    "accent":       (233, 69,  96),
    "text":         (234, 234, 234),
    "muted":        (136, 146, 164),
    "trough":       (74,  85,  104),
    "thumb":        (233, 69,  96),
    "thumb_hover":  (255, 100, 120),
    "check_bg":     (15,  52,  96),
    "check_mark":   (233, 69,  96),
    "btn_bg":       (233, 69,  96),
    "btn_hover":    (255, 100, 120),
    "btn_text":     (255, 255, 255),
    "divider":      (40,  55,  85),
    "scrollbar":    (74,  85,  104),
}

_PAD   = 10   # horizontal padding inside cards
_GAP   = 6    # vertical gap between widgets
_FONT  = None
_FONT_SMALL = None


def _fonts():
    global _FONT, _FONT_SMALL
    if _FONT is None:
        pygame.font.init()
        try:
            _FONT       = pygame.font.SysFont("Courier New", 15, bold=True)
            _FONT_SMALL = pygame.font.SysFont("Courier New", 13, bold=True)
        except Exception:
            _FONT       = pygame.font.SysFont("monospace", 15, bold=True)
            _FONT_SMALL = pygame.font.SysFont("monospace", 13, bold=True)
    return _FONT, _FONT_SMALL


# ── Base widget ───────────────────────────────────────────────────────────────
class _Widget:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)

    def handle_event(self, event):
        pass

    def draw(self, surface, x, y, w):
        pass

    def height(self):
        return 0


# ── Label ─────────────────────────────────────────────────────────────────────
class Label(_Widget):
    """Static text line."""
    def __init__(self, text, color=None, small=False):
        super().__init__()
        self.text  = text
        self.color = color or _C["muted"]
        self.small = small

    def height(self):
        return 18

    def draw(self, surface, x, y, w):
        font, fsmall = _fonts()
        f = fsmall if self.small else font
        surf = f.render(self.text, True, self.color)
        surface.blit(surf, (x + _PAD, y + 2))


# ── Slider ────────────────────────────────────────────────────────────────────
class Slider(_Widget):
    """Horizontal slider with live value display."""
    def __init__(self, label, min_val, max_val, default, step=None):
        super().__init__()
        self.label    = label
        self.min_val  = float(min_val)
        self.max_val  = float(max_val)
        self.step     = step
        self._value   = float(default)
        self._dragging = False
        self._hovered  = False

    @property
    def value(self):
        return int(self._value) if self.step and self.step >= 1 else round(self._value, 3)

    @value.setter
    def value(self, v):
        self._value = max(self.min_val, min(self.max_val, float(v)))

    def height(self):
        return 42

    def _trough_rect(self, x, y, w):
        tw = w - _PAD * 2
        return pygame.Rect(x + _PAD, y + 26, tw, 4)

    def _thumb_x(self, x, y, w):
        tr = self._trough_rect(x, y, w)
        t  = (self._value - self.min_val) / (self.max_val - self.min_val)
        return tr.x + int(t * tr.width)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
            if self._dragging:
                self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._dragging = True
                self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False

    def _set_from_mouse(self, mx):
        tr = self._trough_rect(self.rect.x, self.rect.y, self.rect.width)
        t  = (mx - tr.x) / tr.width
        t  = max(0.0, min(1.0, t))
        raw = self.min_val + t * (self.max_val - self.min_val)
        if self.step:
            raw = round(raw / self.step) * self.step
        self._value = max(self.min_val, min(self.max_val, raw))

    def draw(self, surface, x, y, w):
        self.rect = pygame.Rect(x, y, w, self.height())
        font, fsmall = _fonts()

        # label
        lbl  = fsmall.render(self.label, True, _C["text"])
        surface.blit(lbl, (x + _PAD, y + 2))

        # value
        val_str = str(self.value)
        vsurf = fsmall.render(val_str, True, _C["accent"])
        surface.blit(vsurf, (x + w - _PAD - vsurf.get_width(), y + 2))

        # trough
        tr = self._trough_rect(x, y, w)
        pygame.draw.rect(surface, _C["trough"], tr, border_radius=2)

        # filled portion
        tx = self._thumb_x(x, y, w)
        filled = pygame.Rect(tr.x, tr.y, tx - tr.x, tr.height)
        pygame.draw.rect(surface, _C["accent"], filled, border_radius=2)

        # thumb
        tc = _C["thumb_hover"] if (self._hovered or self._dragging) else _C["thumb"]
        pygame.draw.circle(surface, tc, (tx, tr.centery), 7)
        pygame.draw.circle(surface, _C["text"], (tx, tr.centery), 7, 1)


# ── Checkbox ──────────────────────────────────────────────────────────────────
class Checkbox(_Widget):
    """Toggle checkbox."""
    def __init__(self, label, default=False):
        super().__init__()
        self.label  = label
        self.value  = default
        self._hovered = False

    def height(self):
        return 24

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value

    def draw(self, surface, x, y, w):
        self.rect = pygame.Rect(x, y, w, self.height())
        _, fsmall = _fonts()

        # box
        box = pygame.Rect(x + _PAD, y + 4, 14, 14)
        col = _C["accent"] if self.value else _C["trough"]
        pygame.draw.rect(surface, col, box, border_radius=3)
        pygame.draw.rect(surface, _C["muted"], box, 1, border_radius=3)

        # checkmark
        if self.value:
            cx, cy = box.centerx, box.centery
            pygame.draw.line(surface, _C["btn_text"], (cx - 4, cy), (cx - 1, cy + 3), 2)
            pygame.draw.line(surface, _C["btn_text"], (cx - 1, cy + 3), (cx + 4, cy - 3), 2)

        # label
        lc = _C["text"] if self._hovered else _C["muted"]
        lbl = fsmall.render(self.label, True, lc)
        surface.blit(lbl, (x + _PAD + 20, y + 5))


# ── Button ────────────────────────────────────────────────────────────────────
class Button(_Widget):
    """Clickable button with optional callback."""
    def __init__(self, label, callback=None):
        super().__init__()
        self.label    = label
        self.callback = callback
        self._hovered = False
        self._pressed = False

    def height(self):
        return 28

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
            self._pressed = False

    def draw(self, surface, x, y, w):
        self.rect = pygame.Rect(x + _PAD, y, w - _PAD * 2, self.height())
        _, fsmall = _fonts()

        if self._pressed:
            col = (180, 40, 60)   # darker when held down
            offset = 1            # shift text down slightly to feel "pressed"
        elif self._hovered:
            col = _C["btn_hover"]
            offset = 0
        else:
            col = _C["btn_bg"]
            offset = 0

        pygame.draw.rect(surface, col, self.rect, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1, border_radius=5)

        lbl = fsmall.render(self.label, True, _C["btn_text"])
        lx  = self.rect.centerx - lbl.get_width() // 2
        ly  = self.rect.centery - lbl.get_height() // 2 + offset
        surface.blit(lbl, (lx, ly))


# ── Divider ───────────────────────────────────────────────────────────────────
class Divider(_Widget):
    def height(self):
        return 10

    def draw(self, surface, x, y, w):
        my = y + 5
        pygame.draw.line(surface, _C["divider"], (x + _PAD, my), (x + w - _PAD, my), 1)


# ── ColorPicker (hue strip) ───────────────────────────────────────────────────
class ColorPicker(_Widget):
    """
    Full HSV color picker.
      - Top strip:    hue selection
      - Middle square: saturation (x) × value (y)
      - Bottom strip: live swatch
    `.value` returns (r, g, b). `.hex` gets/sets a hex string like "#26743e".
    """
    _SQ  = 80   # saturation/value square height
    _HUE = 12   # hue strip height
    _SW  = 16   # swatch height

    def __init__(self, label, default_hue=0.0, default_sat=1.0, default_val=1.0):
        super().__init__()
        self.label  = label
        self._hue   = default_hue
        self._sat   = default_sat
        self._val   = default_val
        self._drag  = None          # "hue" | "sv"
        self._hue_strip  = None     # cached surfaces
        self._sv_surf    = None
        self._sv_hue_cached = None  # hue the sv surface was built for

    # ── Public value API ──────────────────────────────────────────────────────

    @property
    def value(self):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(self._hue, self._sat, self._val)
        return int(r * 255), int(g * 255), int(b * 255)

    @property
    def hex(self):
        r, g, b = self.value
        return f"#{r:02x}{g:02x}{b:02x}"

    @hex.setter
    def hex(self, hex_str):
        import colorsys
        hex_str = hex_str.lstrip("#")
        r = int(hex_str[0:2], 16) / 255
        g = int(hex_str[2:4], 16) / 255
        b = int(hex_str[4:6], 16) / 255
        self._hue, self._sat, self._val = colorsys.rgb_to_hsv(r, g, b)
        self._sv_surf = None   # force rebuild

    # ── Layout helpers ────────────────────────────────────────────────────────

    def height(self):
        return 22 + self._HUE + 4 + self._SQ + 4 + self._SW + _PAD

    def _hue_rect(self, x, y, w):
        return pygame.Rect(x + _PAD, y + 20, w - _PAD * 2, self._HUE)

    def _sq_rect(self, x, y, w):
        hr = self._hue_rect(x, y, w)
        return pygame.Rect(hr.x, hr.bottom + 4, hr.width, self._SQ)

    def _sw_rect(self, x, y, w):
        sq = self._sq_rect(x, y, w)
        return pygame.Rect(sq.x, sq.bottom + 4, sq.width, self._SW)

    # ── Surface builders ──────────────────────────────────────────────────────

    def _build_hue_strip(self, w):
        import colorsys
        surf = pygame.Surface((w, self._HUE))
        for i in range(w):
            r, g, b = colorsys.hsv_to_rgb(i / w, 1.0, 1.0)
            pygame.draw.line(surf, (int(r*255), int(g*255), int(b*255)),
                             (i, 0), (i, self._HUE - 1))
        return surf

    def _build_sv_surface(self, w, h):
        import colorsys
        surf = pygame.Surface((w, h))
        for xi in range(w):
            sat = xi / w
            for yi in range(h):
                val = 1.0 - yi / h
                r, g, b = colorsys.hsv_to_rgb(self._hue, sat, val)
                surf.set_at((xi, yi), (int(r*255), int(g*255), int(b*255)))
        return surf

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hue_rect(self.rect.x, self.rect.y, self.rect.width).collidepoint(event.pos):
                self._drag = "hue"
                self._pick_hue(event.pos[0])
            elif self._sq_rect(self.rect.x, self.rect.y, self.rect.width).collidepoint(event.pos):
                self._drag = "sv"
                self._pick_sv(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self._drag == "hue":
                self._pick_hue(event.pos[0])
            elif self._drag == "sv":
                self._pick_sv(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag = None

    def _pick_hue(self, mx):
        hr = self._hue_rect(self.rect.x, self.rect.y, self.rect.width)
        t  = (mx - hr.x) / hr.width
        self._hue = max(0.0, min(1.0, t))
        self._sv_surf = None    # hue changed → rebuild SV square

    def _pick_sv(self, pos):
        sq = self._sq_rect(self.rect.x, self.rect.y, self.rect.width)
        self._sat = max(0.0, min(1.0, (pos[0] - sq.x) / sq.width))
        self._val = max(0.0, min(1.0, 1.0 - (pos[1] - sq.y) / sq.height))

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface, x, y, w):
        self.rect = pygame.Rect(x, y, w, self.height())
        _, fsmall = _fonts()

        # label
        lbl = fsmall.render(self.label, True, _C["text"])
        surface.blit(lbl, (x + _PAD, y + 2))

        hr = self._hue_rect(x, y, w)
        sq = self._sq_rect(x, y, w)
        sw = self._sw_rect(x, y, w)

        # hue strip
        if self._hue_strip is None or self._hue_strip.get_width() != hr.width:
            self._hue_strip = self._build_hue_strip(hr.width)
        surface.blit(self._hue_strip, hr.topleft)
        pygame.draw.rect(surface, _C["muted"], hr, 1)
        # hue thumb
        hx = hr.x + int(self._hue * hr.width)
        pygame.draw.line(surface, _C["text"], (hx, hr.y - 2), (hx, hr.bottom + 2), 2)

        # SV square
        if self._sv_surf is None or self._sv_surf.get_size() != (sq.width, sq.height):
            self._sv_surf = self._build_sv_surface(sq.width, sq.height)
        surface.blit(self._sv_surf, sq.topleft)
        pygame.draw.rect(surface, _C["muted"], sq, 1)
        # SV crosshair
        cx = sq.x + int(self._sat * sq.width)
        cy = sq.y + int((1.0 - self._val) * sq.height)
        pygame.draw.line(surface, (255, 255, 255), (cx - 5, cy), (cx + 5, cy), 1)
        pygame.draw.line(surface, (255, 255, 255), (cx, cy - 5), (cx, cy + 5), 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 4, 1)

        # swatch
        pygame.draw.rect(surface, self.value, sw, border_radius=3)
        pygame.draw.rect(surface, _C["muted"], sw, 1, border_radius=3)


# ── Section ───────────────────────────────────────────────────────────────────
class Section:
    """A titled card containing widgets."""
    def __init__(self, title, width):
        self.title   = title
        self.width   = width
        self.widgets = []

    def _total_height(self):
        h = 28  # title bar
        for w in self.widgets:
            h += w.height() + _GAP
        h += _GAP  # bottom padding
        return h

    def handle_event(self, event):
        for w in self.widgets:
            w.handle_event(event)

    def draw(self, surface, x, y):
        font, fsmall = _fonts()
        iw = self.width - _PAD * 2   # inner width

        # card background
        card = pygame.Rect(x + _PAD, y, iw, self._total_height())
        pygame.draw.rect(surface, _C["section_bg"], card, border_radius=6)

        # title strip
        title_rect = pygame.Rect(x + _PAD, y, iw, 22)
        pygame.draw.rect(surface, _C["divider"], title_rect,
                         border_radius=6)
        tsurf = fsmall.render(self.title.upper(), True, _C["muted"])
        surface.blit(tsurf, (x + _PAD * 2, y + 4))

        # widgets
        wy = y + 28
        for widget in self.widgets:
            widget.draw(surface, x + _PAD, wy, iw)
            wy += widget.height() + _GAP

        return y + self._total_height()


# ── GUI ───────────────────────────────────────────────────────────────────────
class GUI:
    """
    Main sidebar panel.

    Parameters
    ----------
    width : int
        Pixel width of the sidebar (default 240).
    title : str
        Header text shown at the top.
    scroll : bool
        Enable mouse-wheel scrolling when content overflows (default True).
    """

    def __init__(self, width=240, title="⚙  SETTINGS", scroll=True):
        self.width    = width
        self.title    = title
        self.scroll   = scroll
        self._sections = []
        self._scroll_y = 0
        self._surface  = None   # off-screen buffer

    # ── Public API ────────────────────────────────────────────────────────────

    def add_section(self, title) -> Section:
        s = Section(title, self.width)
        self._sections.append(s)
        return s

    def add_slider(self, section: Section, label, min_val, max_val,
                   default, step=None) -> Slider:
        w = Slider(label, min_val, max_val, default, step)
        section.widgets.append(w)
        return w

    def add_checkbox(self, section: Section, label, default=False) -> Checkbox:
        w = Checkbox(label, default)
        section.widgets.append(w)
        return w

    def add_button(self, section: Section, label, callback=None) -> Button:
        w = Button(label, callback)
        section.widgets.append(w)
        return w

    def add_label(self, section: Section, text, color=None, small=False) -> Label:
        w = Label(text, color, small)
        section.widgets.append(w)
        return w

    def add_divider(self, section: Section) -> Divider:
        w = Divider()
        section.widgets.append(w)
        return w

    def add_color_picker(self, section: Section, label,
                         default_hue=0.6) -> ColorPicker:
        w = ColorPicker(label, default_hue)
        section.widgets.append(w)
        return w

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event):
        """Pass every pygame event here."""
        if self.scroll and event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx < self.width:
                content_h = self._content_height()
                # scroll speed scales with how much content is offscreen
                scroll_speed = max(20, content_h // 20)
                self._scroll_y += event.y * scroll_speed
                # clamp immediately so _translate_event sees correct offset
                screen_h = pygame.display.get_surface().get_height()
                max_scroll = max(0, content_h - screen_h)
                self._scroll_y = max(-max_scroll, min(0, self._scroll_y))

        translated = self._translate_event(event)
        if translated:
            for s in self._sections:
                s.handle_event(translated)

    def _translate_event(self, event):
        """Shift mouse coords by scroll offset so widgets always hit-test correctly."""
        pos_events = {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION}
        if event.type not in pos_events:
            return event
        mx, my = event.pos
        if mx > self.width:
            return None
        adj = pygame.event.Event(event.type, {**event.__dict__,
                                               "pos": (mx, my - self._scroll_y)})
        return adj

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface):
        """Draw the sidebar onto `surface`. Call every frame."""
        screen_h = surface.get_height()
        content_h = self._content_height()

        # Rebuild offscreen buffer whenever content size changes
        buf_h = max(screen_h, content_h + 50)
        if self._surface is None or self._surface.get_height() != buf_h:
            self._surface = pygame.Surface((self.width, buf_h))

        self._surface.fill(_C["sidebar_bg"])

        # Header — fixed at top of buffer (scrolls with content)
        header = pygame.Rect(0, 0, self.width, 40)
        pygame.draw.rect(self._surface, _C["header_bg"], header)
        font, _ = _fonts()
        hsurf = font.render(self.title, True, (255, 255, 255))
        self._surface.blit(hsurf, (self.width // 2 - hsurf.get_width() // 2, 12))

        # Sections
        sy = 48
        for section in self._sections:
            sy = section.draw(self._surface, 0, sy) + 8

        # Clamp scroll: scroll_y is <= 0, can scroll up to (content_h - screen_h)
        max_scroll = max(0, content_h - screen_h)
        self._scroll_y = max(-max_scroll, min(0, self._scroll_y))

        # Blit the visible window of the buffer
        surface.blit(self._surface, (0, 0),
                     pygame.Rect(0, -self._scroll_y, self.width, screen_h))

        # Scrollbar drawn on top (screen coords, not buffer coords)
        # if self.scroll and content_h > screen_h:
        #     self._draw_scrollbar(surface, screen_h, content_h)

        # Sidebar border
        pygame.draw.line(surface, _C["divider"], (self.width, 0), (self.width, screen_h), 2)

    def _content_height(self):
        h = 56
        for s in self._sections:
            h += s._total_height() + 8
        return h

    def _draw_scrollbar(self, surface, screen_h, content_h):
        ratio  = screen_h / content_h
        bar_h  = max(30, int(screen_h * ratio))
        # scroll_y is negative; convert to a positive scroll progress in [0,1]
        scroll_progress = -self._scroll_y / (content_h - screen_h)
        bar_y  = int(scroll_progress * (screen_h - bar_h))
        bar_rect = pygame.Rect(self.width - 5, bar_y, 4, bar_h)
        pygame.draw.rect(surface, _C["scrollbar"], bar_rect, border_radius=2)
