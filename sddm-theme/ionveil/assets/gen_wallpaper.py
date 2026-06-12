#!/usr/bin/env python3
"""Generate the IonVeil wallpaper SVG — ported from the ionveil wallpaper engine."""
import math, os

W, H = 1920, 1080
fx, fy = 1344, 486  # focal point

def rings():
    radii = [58, 116, 196, 300, 430]
    out = []
    for i, r in enumerate(radii):
        op = 0.40 - i * 0.06
        col = "#6ee7ff" if i == 1 else "rgba(184,207,255,1)"
        sw = "1.4" if i == 1 else "1"
        out.append(f'<circle cx="{fx}" cy="{fy}" r="{r}" fill="none" stroke="{col}" stroke-opacity="{op:.3f}" stroke-width="{sw}"/>')
    return "\n  ".join(out)

def crosshair():
    return f'''<line x1="{fx}" y1="0" x2="{fx}" y2="{H}" stroke="rgba(184,207,255,1)" stroke-opacity="0.08"/>
  <line x1="0" y1="{fy}" x2="{W}" y2="{fy}" stroke="rgba(184,207,255,1)" stroke-opacity="0.08"/>'''

def ticks():
    out = []
    for x in range(fx - 440, fx + 441, 40):
        if x < 0 or x > W:
            continue
        major = ((x - fx) // 40) % 4 == 0
        h = 9 if major else 5
        op = 0.26 if major else 0.13
        out.append(
            f'<line x1="{x}" y1="{fy - h}" x2="{x}" y2="{fy + h}" '
            f'stroke="rgba(110,231,255,1)" stroke-opacity="{op}"/>'
        )
    return "\n  ".join(out)

def veil_mark():
    return f'''<g opacity="0.9">
    <circle cx="{fx}" cy="{fy}" r="70" fill="none" stroke="#6ee7ff" stroke-opacity="0.55" stroke-width="1.4"/>
    <clipPath id="veilClip"><circle cx="{fx}" cy="{fy}" r="70"/></clipPath>
    <g clip-path="url(#veilClip)">
      <line x1="{fx-70}" y1="{fy-22}" x2="{fx+70}" y2="{fy-22}" stroke="rgba(184,207,255,1)" stroke-opacity="0.4"/>
      <line x1="{fx-70}" y1="{fy+22}" x2="{fx+70}" y2="{fy+22}" stroke="rgba(184,207,255,1)" stroke-opacity="0.4"/>
      <line x1="{fx-70}" y1="{fy}" x2="{fx+70}" y2="{fy}" stroke="#6ee7ff" stroke-opacity="0.85" stroke-width="1.6"/>
      <line x1="{fx+8}" y1="{fy-12}" x2="{fx+52}" y2="{fy-12}" stroke="#ff6bd6" stroke-opacity="0.8" stroke-width="1.4"/>
    </g>
    <circle cx="{fx}" cy="{fy}" r="9" fill="#6ee7ff" fill-opacity="0.18"/>
    <circle cx="{fx}" cy="{fy}" r="3" fill="#dffaff"/>
  </g>'''

def waveform():
    # deterministic wave — same formula as the JS engine minus the Math.random()
    pts = []
    for x in range(0, W + 1, 8):
        y = (880
             + math.sin(x / 70) * 10
             + math.sin(x / 23 + 1.5) * 4)
        pts.append(f"L{x} {y:.1f}")
    d = f"M0 880 " + " ".join(pts)
    return f'<path d="{d}" fill="none" stroke="#6ee7ff" stroke-opacity="0.10" stroke-width="1"/>'

def hud_labels():
    # Bottom-left and bottom-right decorative labels matching the design
    return f'''
  <text x="32" y="{H - 52}" font-family="JetBrains Mono, monospace" font-size="13" fill="#6ee7ff" opacity="0.85">IonVeil</text>
  <text x="32" y="{H - 34}" font-family="JetBrains Mono, monospace" font-size="11" fill="#aab4c8" opacity="0.7">tech-noir desktop</text>
  <text x="32" y="{H - 18}" font-family="JetBrains Mono, monospace" font-size="11" fill="#aab4c8" opacity="0.7">palette  <tspan fill="#aab4c8">void</tspan>  /  <tspan fill="#6ee7ff">cyan</tspan>  /  <tspan fill="#ff6bd6">pink</tspan></text>

  <text text-anchor="end" x="{W - 32}" y="{H - 52}" font-family="JetBrains Mono, monospace" font-size="11" fill="#aab4c8" opacity="0.7">veil integrity <tspan fill="#95f3c3">98.4%</tspan></text>
  <text text-anchor="end" x="{W - 32}" y="{H - 34}" font-family="JetBrains Mono, monospace" font-size="11" fill="#aab4c8" opacity="0.7">interference <tspan fill="#6ee7ff">low</tspan>  ·  carrier <tspan fill="#6ee7ff">6e7eff</tspan></text>
  <text text-anchor="end" x="{W - 32}" y="{H - 18}" font-family="JetBrains Mono, monospace" font-size="11" fill="#aab4c8" opacity="0.7">link <tspan fill="#95f3c3">stable</tspan>  ·  2560×1440</text>

  <text x="32" y="32" font-family="JetBrains Mono, monospace" font-size="11" fill="#6ee7ff" opacity="0.6">● ionveil  ·  signal lock 47.6°n / 122.3°w  ·  depth -2140m</text>'''

svg = f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"
     xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{W}" height="{H}" fill="#05070b"/>

  <!-- Subtle radial glow at focal -->
  <defs>
    <radialGradient id="focalGlow" cx="{fx}" cy="{fy}" r="320" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0d2035"/>
      <stop offset="100%" stop-color="#05070b"/>
    </radialGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#focalGlow)"/>

  <!-- Crosshair -->
  {crosshair()}

  <!-- Rings -->
  {rings()}

  <!-- Ticks -->
  {ticks()}

  <!-- Waveform -->
  {waveform()}

  <!-- Veil mark (logo) -->
  {veil_mark()}

  <!-- HUD labels -->
  {hud_labels()}
</svg>'''

out = os.path.join(os.path.dirname(__file__), "wallpaper.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"Written: {out}")
