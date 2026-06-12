#!/usr/bin/env python3
"""IonVeil terminal greeter — animated ion with orbiting electrons, then fastfetch."""
import math, time, sys, os, signal, subprocess

HIDE = "\033[?25l"
SHOW = "\033[?25h"
CLR  = "\033[2J\033[H"
RST  = "\033[0m"
BG   = "\033[48;2;5;7;11m"

def at(x, y):       return f"\033[{y};{x}H"
def fg(r, g, b):    return f"\033[38;2;{r};{g};{b}m"

CYAN  = fg(110, 231, 255)
BLUE  = fg(124, 156, 255)
PINK  = fg(255, 107, 214)
GREEN = fg(149, 243, 195)
DIM   = fg(26,  42,  74)
MUTED = fg(170, 180, 200)
WHITE = fg(255, 255, 255)

def cleanup(sig=None, frame=None):
    sys.stdout.write(SHOW + RST + "\033[?5l")
    sys.stdout.flush()
    if sig:
        sys.exit(0)

signal.signal(signal.SIGINT,  cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    cols = os.get_terminal_size().columns
    rows = os.get_terminal_size().lines
except OSError:
    cols, rows = 80, 24

cx = min(cols // 4 + 4, 36)
cy = rows // 2

FPS      = 30
DURATION = 3.0

# ── Pre-compute static orbit paths ──────────────────────────────
def orbit_pts(rx, ry):
    seen, out = set(), []
    for deg in range(0, 360, 2):
        r = math.radians(deg)
        x = round(cx + rx * math.cos(r))
        y = round(cy + ry * math.sin(r))
        if 1 <= x < cols and 1 <= y < rows and (x, y) not in seen:
            seen.add((x, y))
            out.append((x, y))
    return out

o1 = orbit_pts(20, 8)
o2 = orbit_pts(13, 5)
o3 = orbit_pts( 7, 3)

# ── Nucleus (IonVeil logo) ───────────────────────────────────────
NUCLEUS = [
    (0, -2, BLUE,  "│"),
    (0, -1, BLUE,  "│"),
    (-4, 0, CYAN,  "────"), (0, 0, WHITE, "●"), (1, 0, CYAN, "────"),
    (0,  1, BLUE,  "│"),
    (0,  2, BLUE,  "│"),
    (-2, -1, MUTED, "·"), (2, -1, MUTED, "·"),
    (-2,  1, MUTED, "·"), (2,  1, MUTED, "·"),
]

def render_nucleus(buf):
    for dx, dy, col, ch in NUCLEUS:
        x, y = cx + dx, cy + dy
        if 1 <= x < cols and 1 <= y < rows:
            buf.append(f"{at(x, y)}{col}{ch}{RST}")

# ── Electron configs [rx, ry, speed, color, phase] ──────────────
ELECTRONS = [
    (20, 8,  1.1,  CYAN,  0.0),
    (13, 5, -1.7,  PINK,  math.pi),
    ( 7, 3,  2.5,  BLUE,  math.pi / 2),
]

def render_electron(buf, rx, ry, angle, col):
    for i in range(6, 0, -1):
        ta = angle - i * 0.10
        tx = round(cx + rx * math.cos(ta))
        ty = round(cy + ry * math.sin(ta))
        if 1 <= tx < cols and 1 <= ty < rows:
            v = 20 + i * 18
            buf.append(f"{at(tx, ty)}\033[38;2;{v};{v+10};{v+30}m·{RST}")
    ex = round(cx + rx * math.cos(angle))
    ey = round(cy + ry * math.sin(angle))
    if 1 <= ex < cols and 1 <= ey < rows:
        buf.append(f"{at(ex, ey)}{col}●{RST}")

# ── Brand label ──────────────────────────────────────────────────
def render_brand(buf, t):
    ly = cy + 11
    if ly >= rows:
        return
    pulse = int(180 + 75 * abs(math.sin(t * 1.5)))
    pc = f"\033[38;2;{pulse};231;255m"
    buf.append(f"{at(cx-3, ly)}{pc}IonVeil{RST}")
    buf.append(f"{at(cx-4, ly+1)}{MUTED}tech-noir{RST}")

# ── Main animation loop ──────────────────────────────────────────
sys.stdout.write(HIDE + BG + CLR)
sys.stdout.flush()

total_frames = int(DURATION * FPS)
t0 = time.perf_counter()

for frame_n in range(total_frames):
    t = frame_n / FPS

    buf = [BG]

    for x, y in o1: buf.append(f"{at(x, y)}{DIM}·{RST}")
    for x, y in o2: buf.append(f"{at(x, y)}{DIM}·{RST}")
    for x, y in o3: buf.append(f"{at(x, y)}{DIM}·{RST}")

    for rx, ry, speed, col, phase in ELECTRONS:
        angle = t * speed * math.pi + phase
        render_electron(buf, rx, ry, angle, col)

    render_nucleus(buf)
    render_brand(buf, t)

    sys.stdout.write("".join(buf))
    sys.stdout.flush()

    elapsed = time.perf_counter() - t0
    target  = (frame_n + 1) / FPS
    sleep   = target - elapsed
    if sleep > 0:
        time.sleep(sleep)

# ── Hand off to fastfetch ────────────────────────────────────────
sys.stdout.write(BG + CLR + SHOW + RST)
sys.stdout.flush()

subprocess.run(["fastfetch"])
cleanup()
