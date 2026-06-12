#!/usr/bin/env python3
"""Generate IonVeil orbital ASCII logo for fastfetch — frozen frame of the ion animation."""
import math, os

RESET  = "\033[0m"
CYAN   = "\033[38;2;110;231;255m"
BLUE   = "\033[38;2;124;156;255m"
PINK   = "\033[38;2;255;107;214m"
MUTED  = "\033[38;2;170;180;200m"
WHITE  = "\033[38;2;255;255;255m"
DIM    = "\033[38;2;26;42;74m"
TRAIL1 = "\033[38;2;55;75;115m"
TRAIL2 = "\033[38;2;35;50;85m"

W, H = 43, 17
cx, cy = 21, 8

grid   = [[' '] * W for _ in range(H)]
colmap = [[None  ] * W for _ in range(H)]

def plot(x, y, ch, col, over=False):
    if 0 <= x < W and 0 <= y < H:
        if over or grid[y][x] == ' ':
            grid[y][x] = ch
            colmap[y][x] = col

def draw_orbit(rx, ry):
    seen = set()
    for deg in range(0, 360, 2):
        r = math.radians(deg)
        x = round(cx + rx * math.cos(r))
        y = round(cy + ry * math.sin(r))
        if (x, y) not in seen:
            seen.add((x, y))
            plot(x, y, '·', DIM)

draw_orbit(19, 7)  # outer
draw_orbit(13, 5)  # middle
draw_orbit( 6, 3)  # inner

def electron(rx, ry, angle_deg, col, trail_dir=1):
    """Place an electron with a short motion trail. trail_dir: +1 or -1."""
    for i, step in enumerate([30, 18], 1):
        ta = math.radians(angle_deg - trail_dir * step)
        tx = round(cx + rx * math.cos(ta))
        ty = round(cy + ry * math.sin(ta))
        plot(tx, ty, '·', TRAIL1 if i == 1 else TRAIL2, over=True)
    a = math.radians(angle_deg)
    plot(round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a)), '●', col, over=True)

# Outer  (cyan)  — upper-right,  moving down-right  (trail to the left)
electron(19, 7,  -38, CYAN,  trail_dir=1)
# Middle (pink)  — lower-left,   moving up-left     (trail to the right)
electron(13, 5,  148, PINK,  trail_dir=-1)
# Inner  (blue)  — upper-left,   moving down-left   (trail to the right)
electron( 6, 3, -118, BLUE,  trail_dir=-1)

# Nucleus crosshair (drawn on top)
for dx in range(-6, 7):
    if dx != 0:
        plot(cx + dx, cy, '─', CYAN, over=True)
plot(cx, cy,     '●', WHITE, over=True)
plot(cx, cy - 1, '│', BLUE,  over=True)
plot(cx, cy - 2, '│', BLUE,  over=True)
plot(cx, cy + 1, '│', BLUE,  over=True)
plot(cx, cy + 2, '│', BLUE,  over=True)

# Render to ANSI lines
lines = []
for row in range(H):
    parts = []
    for c in range(W):
        ch  = grid[row][c]
        col = colmap[row][c]
        parts.append(f"{col}{ch}{RESET}" if col else ' ')
    lines.append(''.join(parts))

lines += [
    '',
    f"  {CYAN}I{RESET}{MUTED}on{RESET}{BLUE}V{RESET}{MUTED}eil{RESET}  {DIM}tech-noir{RESET}",
]

out = os.path.join(os.path.dirname(__file__), "ionveil-logo.txt")
with open(out, 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"Written: {out}")
