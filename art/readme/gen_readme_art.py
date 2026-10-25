"""README / GitHub artwork: banner (light + dark), social preview and feature icons.

Same flat style and geometry as ../icon/gen_icon.py: paper-fold Mount Fuji with long shadow, pill clouds, sakura sky, rose sea.
Text is set in Segoe UI Semibold (Windows); rendering needs ImageMagick with librsvg.
Usage: python gen_readme_art.py [out_dir]   (default: this directory)
"""
import pathlib, subprocess, sys

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent); out.mkdir(parents=True, exist_ok=True)

LIGHT = dict(sky="#FFB7C5", cloud="#FFCCD7", sea="#C94F7C", body="#FFEFF3", cap="#FFFFFF", shade="#8E2450", shade_op=0.13,
             shadow_op=0.22, title="#8E2450", text="#8E2450", star=None)
DARK = dict(sky="#3A1B2B", cloud="#4A2637", sea="#7A2650", body="#F2D5DF", cap="#FFF5F8", shade="#5A1735", shade_op=0.22,
            shadow_op=0.35, title="#FFB1C7", text="#F5D0DB", star="#F5C7D4")
FONT = "Segoe UI"

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")
def poly(points): return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in points) + " Z"
def pill(x, y, w, h):
    r = h / 2
    return (f"M{f(x + r)},{f(y)} L{f(x + w - r)},{f(y)} A{f(r)},{f(r)} 0 0 1 {f(x + w - r)},{f(y + h)} "
            f"L{f(x + r)},{f(y + h)} A{f(r)},{f(r)} 0 0 1 {f(x + r)},{f(y)} Z")
def x_on(seg, y):
    for a, b in zip(seg, seg[1:]):
        if min(a[1], b[1]) <= y <= max(a[1], b[1]): return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])

# --- Icon geometry (108-unit canvas), see gen_icon.py ---
BASE = 66.0
TOP_L, TOP_R = (49.0, 37.0), (59.0, 37.0)
LEFT, RIGHT = [TOP_L, (39.0, 53.0), (24.0, BASE)], [TOP_R, (69.0, 53.0), (84.0, BASE)]
FUJI = [LEFT[2], LEFT[1], TOP_L, TOP_R, RIGHT[1], RIGHT[2]]
SNOW_Y = 47.0
_lx, _rx = x_on(LEFT, SNOW_Y), x_on(RIGHT, SNOW_Y)
ZIG = [(_lx + (_rx - _lx) * i / 6, y) for i, y in enumerate([SNOW_Y, 51.5, 47.6, 52.5, 47.6, 51.5, SNOW_Y])]
CAP = [TOP_L, TOP_R] + ZIG[::-1]
SHADE = [(54.0, 37.0), TOP_R, RIGHT[1], RIGHT[2], (58.0, BASE)]

def fuji(p, cx, base_y, width, uid, shadow_len=2000):
    """Fuji with long shadow; foot spans `width` px centred on cx, standing on base_y."""
    s = width / 60
    def t(points): return [((x - 54) * s + cx, (y - BASE) * s + base_y) for x, y in points]
    (lx, by), (rx, _) = t([(44.0, BASE), RIGHT[2]])
    shadow = [(lx, by), (rx, by), (rx + shadow_len, by + shadow_len), (lx + shadow_len, by + shadow_len)]
    g0, g1 = t([(66.0, 66.0), (88.0, 88.0)])
    return (f'<linearGradient id="sh{uid}" gradientUnits="userSpaceOnUse" x1="{f(g0[0])}" y1="{f(g0[1])}" x2="{f(g1[0])}" y2="{f(g1[1])}">'
            f'<stop offset="0" stop-color="#000" stop-opacity="{p["shadow_op"]}"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
            f'<path d="{poly(shadow)}" fill="url(#sh{uid})"/>'
            f'<path d="{poly(t(FUJI))}" fill="{p["body"]}"/><path d="{poly(t(CAP))}" fill="{p["cap"]}"/>'
            f'<path d="{poly(t(SHADE))}" fill="{p["shade"]}" fill-opacity="{p["shade_op"]}"/>')

def clouds(p, pairs):   # pairs of offset pills, like the icon's
    return "".join(f'<path d="{pill(x, y, w, h)} {pill(x - 0.27 * w, y + 0.9 * h, 0.92 * w, h)}" fill="{p["cloud"]}"/>'
                   for x, y, w, h in pairs)

def stars(p, points):
    if not p["star"]: return ""
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{p["star"]}" fill-opacity="0.7"/>' for x, y, r in points)

def text(x, y, size, fill, s, weight=600, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}">{s}</text>')

def scene(p, w, h, horizon, fuji_cx, fuji_w, cloud_pairs, star_points, texts, radius=0):
    clip = f'<clipPath id="c"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>'
    body = (f'<rect width="{w}" height="{horizon}" fill="{p["sky"]}"/>' + stars(p, star_points) + clouds(p, cloud_pairs) +
            f'<rect y="{horizon}" width="{w}" height="{h - horizon}" fill="{p["sea"]}"/>' +
            fuji(p, fuji_cx, horizon + 2 * fuji_w / 60, fuji_w, 0) + texts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{clip}</defs><g clip-path="url(#c)">{body}</g></svg>')

def render(name, svg):
    (out / f"{name}.svg").write_text(svg, encoding="utf-8")
    subprocess.run(["magick", "-background", "none", str(out / f"{name}.svg"), "-strip", str(out / f"{name}.png")], check=True)
    (out / f"{name}.svg").unlink()   # Text needs the font: ship the PNG only

# --- Banner (README top, light + dark via <picture>) ---
BW, BH, B_HORIZON = 1600, 480, 340
B_CLOUDS = [(860, 96, 150, 30), (1400, 62, 120, 30), (1450, 236, 100, 26)]
B_STARS = [(700, 70, 3), (780, 180, 2.5), (980, 48, 2), (1290, 150, 3), (1500, 210, 2.5), (1180, 36, 2), (90, 60, 2.5), (520, 40, 2)]
for name, p in [("banner-light", LIGHT), ("banner-dark", DARK)]:
    render(name, scene(p, BW, BH, B_HORIZON, 1150, 600, B_CLOUDS, B_STARS,
                       text(120, 205, 150, p["title"], "Shima <tspan font-weight=\"400\" font-size=\"96\">島</tspan>") +
                       text(126, 275, 40, p["text"], "Isolate, clone and freeze Android apps", weight=400),
                       radius=28))

# --- Social preview (repo settings, 1280x640; keep a 40px margin clear) ---
render("social-preview", scene(LIGHT, 1280, 640, 440, 930, 520, [(700, 120, 130, 28), (1110, 84, 110, 28)], [],
                               text(96, 250, 140, LIGHT["title"], "Shima <tspan font-weight=\"400\" font-size=\"90\">島</tspan>") +
                               text(102, 320, 38, LIGHT["text"], "Isolate, clone and freeze Android apps", weight=400) +
                               text(102, 372, 30, LIGHT["text"], "De-Googled fork of Island · Material 3", weight=400)))

# --- Feature icons: white glyph on a sakura tile, long shadow down-right (SVG, no text) ---
TILE, GLYPH_SHADOW = 96, 0.14
def feature(name, glyph, accents="", ground=""):
    shadow = "".join(f'<use xlink:href="#g" x="{k}" y="{k}"/>' for k in range(1, 61))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{TILE}" height="{TILE}" '
           f'viewBox="0 0 {TILE} {TILE}"><defs><clipPath id="t"><rect width="{TILE}" height="{TILE}" rx="24"/></clipPath>'
           f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="1"><stop offset="0.35" stop-color="#fff"/>'
           f'<stop offset="0.95" stop-color="#fff" stop-opacity="0"/></linearGradient>'
           f'<mask id="m"><rect width="{TILE}" height="{TILE}" fill="url(#fade)"/></mask>'
           f'<g id="g">{glyph}</g></defs>'
           f'<g clip-path="url(#t)"><rect width="{TILE}" height="{TILE}" fill="{LIGHT["sky"]}"/>{ground}'
           f'<g mask="url(#m)" opacity="{GLYPH_SHADOW}" fill="#000">{shadow}</g>'
           f'<use xlink:href="#g" fill="#fff"/>{accents}</g></svg>')
    (out / f"{name}.svg").write_text(svg, encoding="utf-8")

ROSE, DEEP = LIGHT["sea"], LIGHT["shade"]
# De-Googled: shield with a check mark
feature("feature-private", '<path d="M48,20 L71,28 L71,46 C71,61 61,71 48,76 C35,71 25,61 25,46 L25,28 Z"/>',
        f'<path d="M37,47 L45,55 L60,39" fill="none" stroke="{ROSE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
# Files across profiles: folder with an arrow
feature("feature-files", '<path d="M22,30 A4,4 0 0 1 26,26 L40,26 L46,32 L70,32 A4,4 0 0 1 74,36 L74,66 A4,4 0 0 1 70,70 '
                         'L26,70 A4,4 0 0 1 22,66 Z"/>',
        f'<path d="M36,51 L58,51 M50,43 L58,51 L50,59" fill="none" stroke="{ROSE}" stroke-width="6" stroke-linecap="round" '
        f'stroke-linejoin="round"/>')
# Material 3: Material You colour swatch
feature("feature-material", '<circle cx="48" cy="48" r="25"/>',
        f'<path d="M23,48 A25,25 0 0 0 48,73 L48,48 Z" fill="{ROSE}"/><path d="M48,73 A25,25 0 0 0 73,48 L48,48 Z" fill="{DEEP}"/>')
# Side by side with Island: two little Fujis on the sea
feature("feature-coexist", '<path d="M10,63 L25,45 L30,45 L45,63 Z M47,63 L63,32 L70,32 L86,63 Z"/>',
        ground=f'<rect y="62" width="{TILE}" height="34" fill="{ROSE}"/>')
