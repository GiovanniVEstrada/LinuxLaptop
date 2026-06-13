#!/usr/bin/env python3
"""IonVeil storm wallpaper — gradient + animation on the Wayland bottom layer.
Sits above awww's background layer. Kill this process to reveal the awww wallpaper."""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, WebKit2, GtkLayerShell
import os

STORM_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storm', 'storm-overlay.html')

class StormWallpaper(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_decorated(False)
        self.set_app_paintable(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        # Bottom layer: above awww's background layer, below all windows.
        # Killing this process reveals the awww wallpaper underneath.
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        for edge in [GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT]:
            GtkLayerShell.set_anchor(self, edge, True)
        GtkLayerShell.set_exclusive_zone(self, -1)

        settings = WebKit2.Settings()
        settings.set_enable_javascript(True)
        settings.set_enable_webgl(True)
        settings.set_hardware_acceleration_policy(WebKit2.HardwareAccelerationPolicy.ALWAYS)

        wv = WebKit2.WebView.new_with_settings(settings)
        wv.set_background_color(Gdk.RGBA(0, 0, 0, 0))  # transparent — wallpaper shows through
        wv.load_uri(f'file://{STORM_HTML}')

        self.add(wv)
        self.show_all()

if __name__ == '__main__':
    StormWallpaper()
    Gtk.main()
