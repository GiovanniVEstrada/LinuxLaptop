#!/usr/bin/env python3
"""IonVeil Control Center — media · volume · brightness · DND · notifications."""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell

import os, sys, signal, subprocess, shlex

LOCK             = "/tmp/.ionveil-cc.pid"
STORM_WALLPAPER  = os.path.expanduser("~/.config/hypr/storm-wallpaper.py")
BG_DIR           = os.path.expanduser("~/.config/backgrounds")
PANEL_W = 360
MARGIN_RIGHT = 22
MARGIN_TOP   = 5  # below waybar

CSS = """
* {
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
}

/* Fullscreen overlay — transparent */
window {
    background-color: transparent;
}

/* The visible panel card */
.panel {
    background-color: rgba(9, 14, 24, 0.97);
    border-radius: 18px;
    border: 1px solid rgba(110, 231, 255, 0.09);
    padding: 10px;
}

.card {
    background-color: rgba(15, 22, 38, 0.92);
    border-radius: 14px;
    border: 1px solid rgba(110, 231, 255, 0.06);
    padding: 14px;
    margin-bottom: 7px;
}

/* ── Media ── */
.track-title {
    color: #f6f8ff;
    font-size: 14px;
    font-weight: bold;
}
.track-artist {
    color: #5a6a90;
    font-size: 12px;
}
.ctrl-btn {
    background-color: rgba(110, 231, 255, 0.07);
    color: #5a6a90;
    border: none;
    border-radius: 50%;
    min-width: 36px;
    min-height: 36px;
    font-size: 16px;
    padding: 0;
}
.ctrl-btn:hover {
    background-color: rgba(110, 231, 255, 0.14);
    color: #f6f8ff;
}
.play-btn {
    background-color: rgba(110, 231, 255, 0.13);
    color: #6ee7ff;
    min-width: 44px;
    min-height: 44px;
    font-size: 20px;
}
.play-btn:hover {
    background-color: rgba(110, 231, 255, 0.25);
}

/* ── Sliders ── */
.slider-icon {
    color: #5a6a90;
    font-size: 16px;
    min-width: 24px;
}
scale trough {
    background-color: rgba(110, 231, 255, 0.09);
    border-radius: 4px;
    min-height: 4px;
}
scale trough highlight {
    background-color: #6ee7ff;
    border-radius: 4px;
}
scale slider {
    background-color: #f6f8ff;
    border-radius: 50%;
    min-width: 14px;
    min-height: 14px;
    border: none;
    box-shadow: none;
}
scale slider:hover {
    background-color: #6ee7ff;
}

/* ── DND ── */
.dnd-label {
    color: #aab4c8;
    font-size: 13px;
}
.toggle {
    background-color: rgba(90, 106, 144, 0.2);
    color: #5a6a90;
    border: 1px solid rgba(110, 231, 255, 0.07);
    border-radius: 10px;
    padding: 3px 14px;
    font-size: 11px;
    min-width: 52px;
}
.toggle:hover {
    background-color: rgba(90, 106, 144, 0.35);
    color: #aab4c8;
}
.toggle-on {
    background-color: rgba(255, 215, 0, 0.16);
    color: #ffd700;
    border-color: rgba(255, 215, 0, 0.32);
}
.toggle-on:hover {
    background-color: rgba(255, 215, 0, 0.26);
}
.toggle-green {
    background-color: rgba(149, 243, 195, 0.16);
    color: #95f3c3;
    border-color: rgba(149, 243, 195, 0.32);
}
.toggle-green:hover {
    background-color: rgba(149, 243, 195, 0.26);
}

/* ── Wallpaper picker ── */
.wallpaper-thumb {
    padding: 2px;
    border-radius: 7px;
    border: 1px solid rgba(110, 231, 255, 0.08);
    background-color: rgba(15, 22, 38, 0.4);
}
.wallpaper-thumb:hover {
    border-color: rgba(110, 231, 255, 0.45);
    background-color: rgba(110, 231, 255, 0.07);
}
.wallpaper-thumb.active {
    border-color: rgba(110, 231, 255, 0.7);
    box-shadow: 0 0 0 1px rgba(110, 231, 255, 0.25);
}

/* ── Notifications ── */
.section-label {
    color: #f6f8ff;
    font-size: 13px;
    font-weight: bold;
}
.clear-btn {
    background-color: transparent;
    color: #2a3a58;
    border: none;
    font-size: 11px;
    padding: 2px 4px;
}
.clear-btn:hover { color: #5a6a90; }
.empty-notif {
    color: #2a3a58;
    font-size: 12px;
    padding: 8px 0 2px;
}
"""


def sh(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def bg(cmd):
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class ControlCenter(Gtk.Window):
    def __init__(self):
        super().__init__()

        # ── Layer shell: fullscreen transparent overlay ────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP,    True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT,   True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT,  True)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_title("ionveil-cc")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── Layout: Fixed so panel sits top-right ─────────────
        display = Gdk.Display.get_default()
        monitor = display.get_monitor(0)
        geo     = monitor.get_geometry()
        panel_x = geo.width  - PANEL_W - MARGIN_RIGHT
        panel_y = MARGIN_TOP

        fixed = Gtk.Fixed()
        self.add(fixed)

        panel = self._build_panel()
        panel.set_size_request(PANEL_W, -1)
        fixed.put(panel, panel_x, panel_y)
        self._panel     = panel
        self._panel_x   = panel_x
        self._panel_y   = panel_y

        # ── Click outside → close ─────────────────────────────
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._on_overlay_click)
        # Absorb all clicks inside the panel so they don't reach the overlay handler
        panel.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        panel.connect("button-press-event", lambda *_: True)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        self.show_all()
        GLib.timeout_add(2000, self._refresh_media)

    # ── Panel construction ────────────────────────────────────

    def _build_panel(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("panel")
        box.pack_start(self._media_card(),      False, False, 0)
        box.pack_start(self._sliders_card(),    False, False, 0)
        box.pack_start(self._wallpapers_card(), False, False, 0)
        box.pack_start(self._dnd_card(),        False, False, 0)
        box.pack_start(self._lowpower_card(),   False, False, 0)
        box.pack_start(self._notif_card(),      False, False, 0)
        return box

    # ── Media ─────────────────────────────────────────────────

    def _media_card(self):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("card")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._art = Gtk.Image()
        self._load_art()
        row.pack_start(self._art, False, False, 0)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info.set_valign(Gtk.Align.CENTER)

        self._title_lbl = Gtk.Label(xalign=0)
        self._title_lbl.get_style_context().add_class("track-title")
        self._title_lbl.set_ellipsize(3)
        self._title_lbl.set_max_width_chars(22)

        self._artist_lbl = Gtk.Label(xalign=0)
        self._artist_lbl.get_style_context().add_class("track-artist")
        self._artist_lbl.set_ellipsize(3)
        self._artist_lbl.set_max_width_chars(22)

        self._refresh_track_labels()
        info.pack_start(self._title_lbl,  False, False, 0)
        info.pack_start(self._artist_lbl, False, False, 0)
        row.pack_start(info, True, True, 0)
        card.pack_start(row, False, False, 0)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        controls.set_halign(Gtk.Align.CENTER)
        prev_btn       = self._ctrl_btn("󰒮", lambda *_: bg("playerctl previous"))
        self._play_btn = self._ctrl_btn("",  None, "play-btn")
        self._refresh_play_icon()
        self._play_btn.connect("clicked", self._toggle_play)
        next_btn = self._ctrl_btn("󰒭", lambda *_: bg("playerctl next"))
        controls.pack_start(prev_btn,       False, False, 0)
        controls.pack_start(self._play_btn, False, False, 0)
        controls.pack_start(next_btn,       False, False, 0)
        card.pack_start(controls, False, False, 0)
        return card

    def _ctrl_btn(self, label, handler, extra=None):
        btn = Gtk.Button(label=label)
        btn.get_style_context().add_class("ctrl-btn")
        if extra:
            btn.get_style_context().add_class(extra)
        if handler:
            btn.connect("clicked", handler)
        return btn

    def _load_art(self):
        url = sh("playerctl metadata mpris:artUrl")
        try:
            if url.startswith("file://"):
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(url[7:], 56, 56, True)
                self._art.set_from_pixbuf(pb)
                return
        except Exception:
            pass
        self._art.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)
        self._art.set_pixel_size(56)

    def _refresh_track_labels(self):
        self._title_lbl.set_text(sh("playerctl metadata title")  or "Nothing playing")
        self._artist_lbl.set_text(sh("playerctl metadata artist") or "—")

    def _refresh_play_icon(self):
        self._play_btn.set_label("󰏤" if sh("playerctl status") == "Playing" else "󰐊")

    def _toggle_play(self, *_):
        bg("playerctl play-pause")
        GLib.timeout_add(120, self._refresh_play_icon)

    def _refresh_media(self):
        self._refresh_track_labels()
        self._refresh_play_icon()
        return True

    # ── Sliders ───────────────────────────────────────────────

    def _sliders_card(self):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("card")
        vol    = int(sh("wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{printf \"%d\", $2*100}'") or 50)
        bright = int(sh("brightnessctl -m | awk -F, '{print $4}' | tr -d '%'") or 80)
        self._vol_slider    = self._make_slider(vol,    self._on_vol)
        self._bright_slider = self._make_slider(bright, self._on_bright)
        card.pack_start(self._slider_row("󰕾", self._vol_slider),    False, False, 0)
        card.pack_start(self._slider_row("󰖨", self._bright_slider), False, False, 0)
        return card

    def _make_slider(self, value, handler):
        s = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        s.set_draw_value(False)
        s.set_hexpand(True)
        s.set_value(value)
        s.connect("value-changed", handler)
        return s

    def _slider_row(self, icon, widget):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=icon)
        lbl.get_style_context().add_class("slider-icon")
        row.pack_start(lbl,    False, False, 0)
        row.pack_start(widget, True,  True,  0)
        return row

    def _on_vol(self, s):
        bg(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {int(s.get_value())}%")

    def _on_bright(self, s):
        bg(f"brightnessctl set {int(s.get_value())}%")

    # ── Wallpaper picker ──────────────────────────────────────

    def _get_wallpapers(self):
        exts = {'.png', '.jpg', '.jpeg', '.webp'}
        try:
            return sorted([
                os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR)
                if os.path.splitext(f)[1].lower() in exts
            ])
        except FileNotFoundError:
            return []

    def _wallpapers_card(self):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")

        header = Gtk.Label(label="Wallpaper", xalign=0)
        header.get_style_context().add_class("section-label")
        card.pack_start(header, False, False, 0)

        walls = self._get_wallpapers()
        if not walls:
            empty = Gtk.Label(label="No wallpapers found")
            empty.get_style_context().add_class("empty-notif")
            card.pack_start(empty, False, False, 0)
            return card

        COLS, THUMB_W, THUMB_H = 3, 100, 56
        grid = Gtk.Grid()
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self._wall_btns = {}

        for i, path in enumerate(walls):
            btn = Gtk.Button()
            btn.get_style_context().add_class("wallpaper-thumb")
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, THUMB_W, THUMB_H, False)
                btn.add(Gtk.Image.new_from_pixbuf(pb))
            except Exception:
                lbl = Gtk.Label(label=os.path.splitext(os.path.basename(path))[0][:10])
                lbl.set_size_request(THUMB_W, THUMB_H)
                btn.add(lbl)
            btn.connect("clicked", self._on_wallpaper_click, path)
            btn.set_tooltip_text(os.path.basename(path))
            self._wall_btns[path] = btn
            grid.attach(btn, i % COLS, i // COLS, 1, 1)

        card.pack_start(grid, False, False, 0)
        return card

    def _on_wallpaper_click(self, btn, path):
        for b in self._wall_btns.values():
            b.get_style_context().remove_class("active")
        btn.get_style_context().add_class("active")
        # Start daemon if not running, then set wallpaper
        bg(f"pgrep -x awww-daemon >/dev/null 2>&1 || (awww-daemon & sleep 0.3) && awww img {shlex.quote(path)} --transition-type fade --transition-duration 1")

    # ── DND ───────────────────────────────────────────────────

    def _dnd_card(self):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.get_style_context().add_class("card")
        lbl = Gtk.Label(label="Do Not Disturb", xalign=0)
        lbl.get_style_context().add_class("dnd-label")
        row.pack_start(lbl, True, True, 0)
        self._dnd_active = "do-not-disturb" in sh("makoctl mode")
        self._dnd_btn = Gtk.Button()
        self._dnd_btn.get_style_context().add_class("toggle")
        self._apply_dnd_style()
        self._dnd_btn.connect("clicked", self._toggle_dnd)
        row.pack_end(self._dnd_btn, False, False, 0)
        return row

    def _apply_dnd_style(self):
        ctx = self._dnd_btn.get_style_context()
        if self._dnd_active:
            self._dnd_btn.set_label("ON")
            ctx.add_class("toggle-on")
        else:
            self._dnd_btn.set_label("OFF")
            ctx.remove_class("toggle-on")

    def _toggle_dnd(self, *_):
        self._dnd_active = not self._dnd_active
        bg("makoctl mode -a do-not-disturb" if self._dnd_active else "makoctl mode -r do-not-disturb")
        self._apply_dnd_style()

    # ── Low Power ─────────────────────────────────────────────

    def _lowpower_card(self):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.get_style_context().add_class("card")
        lbl = Gtk.Label(label="Animations", xalign=0)
        lbl.get_style_context().add_class("dnd-label")
        row.pack_start(lbl, True, True, 0)
        self._lowpower_active = bool(sh("pgrep -f storm-wallpaper.py"))
        self._lp_btn = Gtk.Button()
        self._lp_btn.get_style_context().add_class("toggle")
        self._apply_lowpower_style()
        self._lp_btn.connect("clicked", self._toggle_lowpower)
        row.pack_end(self._lp_btn, False, False, 0)
        return row

    def _apply_lowpower_style(self):
        ctx = self._lp_btn.get_style_context()
        if self._lowpower_active:
            self._lp_btn.set_label("ON")
            ctx.add_class("toggle-green")
        else:
            self._lp_btn.set_label("OFF")
            ctx.remove_class("toggle-green")

    def _toggle_lowpower(self, *_):
        self._lowpower_active = not self._lowpower_active
        if self._lowpower_active:
            bg(f"python3 {STORM_WALLPAPER}")
        else:
            bg("pkill -f storm-wallpaper.py; pgrep -x awww-daemon >/dev/null 2>&1 || awww-daemon &")
        self._apply_lowpower_style()

    # ── Notifications ─────────────────────────────────────────

    def _notif_card(self):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.get_style_context().add_class("card")
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl = Gtk.Label(label="Notifications", xalign=0)
        lbl.get_style_context().add_class("section-label")
        header.pack_start(lbl, True, True, 0)
        clear = Gtk.Button(label="Clear all")
        clear.get_style_context().add_class("clear-btn")
        clear.connect("clicked", lambda *_: bg("makoctl dismiss --all"))
        header.pack_end(clear, False, False, 0)
        card.pack_start(header, False, False, 0)
        empty = Gtk.Label(label="No notifications")
        empty.get_style_context().add_class("empty-notif")
        card.pack_start(empty, False, False, 0)
        return card

    # ── Events ────────────────────────────────────────────────

    def _on_overlay_click(self, widget, event):
        alloc = self._panel.get_allocation()
        px, py = self._panel_x, self._panel_y
        if not (px <= event.x <= px + alloc.width and py <= event.y <= py + alloc.height):
            self._quit()
        return False

    def _on_key(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self._quit()

    def _quit(self):
        try:
            os.remove(LOCK)
        except FileNotFoundError:
            pass
        Gtk.main_quit()


def main():
    try:
        with open(LOCK) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(LOCK)
        sys.exit(0)
    except (FileNotFoundError, ValueError, ProcessLookupError):
        pass

    with open(LOCK, "w") as f:
        f.write(str(os.getpid()))

    signal.signal(signal.SIGTERM, lambda *_: (os.remove(LOCK), sys.exit(0)))

    ControlCenter()
    Gtk.main()


if __name__ == "__main__":
    main()
