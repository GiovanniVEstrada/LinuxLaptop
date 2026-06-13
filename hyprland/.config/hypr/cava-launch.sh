#!/bin/bash
kitty \
  --title cava \
  --override background_opacity=0.0 \
  --override background=#05070b \
  --override remember_window_size=no \
  --override initial_window_width=900 \
  --override initial_window_height=120 \
  --override hide_window_decorations=yes \
  --override cursor_shape=block \
  --override cursor_blink_interval=0 \
  -e cava
