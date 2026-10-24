"""Shima setup-wizard header (mobile/src/main/res/drawable-xxxhdpi/setup_header.9.png).

Same flat style and palette as gen_icon.py. Only the 510x455 interior is redrawn; the 1px nine-patch
border (stretch/padding markers) is copied from the existing file, so keep stretch areas plain:
left 6 columns, right column, top 4 rows (sky) and bottom 2 rows (sea).
Usage: python gen_header.py <existing setup_header.9.png> <out.9.png>   (needs ImageMagick with librsvg)
"""
import pathlib, subprocess, sys, tempfile

SKY, CLOUD, SEA = "#FFB7C5", "#FFCCD7", "#C94F7C"
FUJI_BODY, FUJI_CAP, FUJI_SHADE = "#FFEFF3", "#FFFFFF", "#8E2450"
W, H, HORIZON = 510, 455, 285

# Icon geometry (108-unit canvas, see gen_icon.py) scaled so the foot spans x 60..495 standing at y 358
S = 435 / 60; DX = 60 - 24 * S; DY = 358 - 66 * S
def t(points): return [(x * S + DX, y * S + DY) for x, y in points]
def poly(points): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"

BASE = 66.0
TOP_L, TOP_R = (49.0, 37.0), (59.0, 37.0)
LEFT, RIGHT = [TOP_L, (39.0, 53.0), (24.0, BASE)], [TOP_R, (69.0, 53.0), (84.0, BASE)]
FUJI = [LEFT[2], LEFT[1], TOP_L, TOP_R, RIGHT[1], RIGHT[2]]
def x_on(seg, y):
    for a, b in zip(seg, seg[1:]):
        if min(a[1], b[1]) <= y <= max(a[1], b[1]): return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
SNOW_Y = 47.0
lx, rx = x_on(LEFT, SNOW_Y), x_on(RIGHT, SNOW_Y)
ZIG = [(lx + (rx - lx) * i / 6, y) for i, y in enumerate([SNOW_Y, 51.5, 47.6, 52.5, 47.6, 51.5, SNOW_Y])]
CAP = [TOP_L, TOP_R] + ZIG[::-1]
SHADE = [(54.0, 37.0), TOP_R, RIGHT[1], RIGHT[2], (58.0, BASE)]
foot_l, foot_r = t([LEFT[2]])[0], t([RIGHT[2]])[0]
# Long shadow cast down-right at 45 deg; it must end above the bottom stretch rows and left of the right stretch column,
# otherwise the nine-patch repeats it into a stripe.
SHADOW_END_Y, SHADOW_MAX_X = H - 20, W - 12
SHADOW = [(foot_l[0] + 120, foot_l[1]), foot_r, (SHADOW_MAX_X, foot_r[1] + SHADOW_MAX_X - foot_r[0]),
          (SHADOW_MAX_X, SHADOW_END_Y), (foot_l[0] + 120 + SHADOW_END_Y - foot_l[1], SHADOW_END_Y)]

def pill(x, y, w, h):
    r = h / 2
    return f"M{x + r},{y} L{x + w - r},{y} A{r},{r} 0 0 1 {x + w - r},{y + h} L{x + r},{y + h} A{r},{r} 0 0 1 {x + r},{y} Z"
CLOUDS = " ".join([pill(52, 10, 130, 34), pill(104, 34, 114, 34),       # top left (as in Island's header)
                   pill(14, 160, 150, 34), pill(46, 184, 120, 34),      # left, behind the mountain
                   pill(300, 96, 110, 34), pill(278, 120, 98, 34)])     # right of the summit

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="{foot_r[1]}" x2="0" y2="{SHADOW_END_Y}">
<stop offset="0" stop-color="#000" stop-opacity="0.22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient></defs>
<rect width="{W}" height="{HORIZON}" fill="{SKY}"/><path d="{CLOUDS}" fill="{CLOUD}"/>
<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="{SEA}"/>
<path d="{poly(SHADOW)}" fill="url(#sh)"/>
<path d="{poly(t(FUJI))}" fill="{FUJI_BODY}"/><path d="{poly(t(CAP))}" fill="{FUJI_CAP}"/>
<path d="{poly(t(SHADE))}" fill="{FUJI_SHADE}" fill-opacity="0.13"/>
</svg>'''

src, dst = sys.argv[1], sys.argv[2]
with tempfile.TemporaryDirectory() as tmp:
    svg_path, art = pathlib.Path(tmp, "header.svg"), pathlib.Path(tmp, "art.png")
    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run(["magick", "-background", "none", str(svg_path), str(art)], check=True)
    # keep the original 1px nine-patch frame, replace only the interior
    subprocess.run(["magick", src, str(art), "-geometry", "+1+1", "-compose", "Copy", "-composite", f"PNG32:{dst}"], check=True)
print("ok", dst)
