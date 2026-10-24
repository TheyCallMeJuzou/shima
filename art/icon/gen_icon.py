"""Shima launcher icon generator: one geometry -> SVG layers + Android VectorDrawables.

Adaptive icon canvas is 108x108; visible area ~18..90, safe zone r=33 around (54,54).
Usage: python gen_icon.py <out_dir>   (then legacy.sh <out_dir> for the pre-API-26 PNGs; needs ImageMagick with librsvg)
"""
import math, pathlib, sys

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)

# Palette: sakura + white
SKY, SEA, WAVE = "#FFB7C5", "#C94F7C", "#DB7397"
SUN = "#FFFFFF"
BLOSSOM, BLOSSOM_CENTER = "#FFFFFF", "#EE6F96"
FUJI_BODY, FUJI_CAP, FUJI_SHADE = "#FFEFF3", "#FFFFFF", "#8E2450"
HORIZON = 64.0

def f(v): return f"{v:.2f}".rstrip("0").rstrip(".")
def pts(cmds):
    """cmds: list of (op, [x,y,...]) -> path string"""
    return " ".join(op + " ".join(f(v) for v in vals) for op, vals in cmds)

def affine(cmds, tx=0, ty=0, rot=0, s=1):
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    res = []
    for op, vals in cmds:
        nv = []
        for i in range(0, len(vals), 2):
            x, y = vals[i] * s, vals[i + 1] * s
            nv += [x * c - y * si + tx, x * si + y * c + ty]
        res.append((op, nv))
    return res

def circle(cx, cy, r):   # 4 cubic arcs (kappa), so it survives any tooling
    k = 0.5523 * r
    return pts([("M", [cx + r, cy]), ("C", [cx + r, cy + k, cx + k, cy + r, cx, cy + r]),
                ("C", [cx - k, cy + r, cx - r, cy + k, cx - r, cy]), ("C", [cx - r, cy - k, cx - k, cy - r, cx, cy - r]),
                ("C", [cx + k, cy - r, cx + r, cy - k, cx + r, cy]), ("Z", [])])

# Sakura petal pointing up from origin, notched tip at y=-6
PETAL = [("M", [0, 0]), ("C", [-2.7, -1.1, -3.2, -4.5, -1.3, -6.1]), ("L", [0, -5.1]), ("L", [1.3, -6.1]),
         ("C", [3.2, -4.5, 2.7, -1.1, 0, 0]), ("Z", [])]

def blossom(cx, cy, s, rot):
    petals = " ".join(pts(affine(PETAL, cx, cy, rot + i * 72, s)) for i in range(5))
    return petals, circle(cx, cy, 1.05 * s)

def loose_petal(cx, cy, s, rot):   # a single drifting petal, centred on its own middle
    return pts(affine(affine(PETAL, 0, 3), cx, cy, rot, s))

# --- Mount Fuji (paper-fold, concave flanks) ---
L0, LC, L2 = (49.0, 36.0), (41.0, 57.0), (24.0, 66.0)
R0, RC, R2 = (59.0, 36.0), (67.0, 57.0), (84.0, 66.0)
BASE = 66.0

def quad_x_at_y(p0, c, p2, y):
    a = p0[1] - 2 * c[1] + p2[1]; b = 2 * (c[1] - p0[1]); cc = p0[1] - y
    t = (-b + math.sqrt(b * b - 4 * a * cc)) / (2 * a) if abs(a) > 1e-9 else -cc / b
    if not 0 <= t <= 1: t = (-b - math.sqrt(b * b - 4 * a * cc)) / (2 * a)
    return (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0], t

def split_quad(p0, c, p2, t):   # de Casteljau: returns (first half ctrl, mid point, second half ctrl)
    a = (p0[0] + (c[0] - p0[0]) * t, p0[1] + (c[1] - p0[1]) * t)
    b = (c[0] + (p2[0] - c[0]) * t, c[1] + (p2[1] - c[1]) * t)
    m = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return a, m, b

SUMMIT = [(49, 36), (50.6, 35.1), (52.2, 36.0), (54.3, 34.7), (56.3, 35.9), (57.6, 35.1), (59, 36)]
silhouette = pts([("M", list(L2)), ("Q", [*LC, *L0])] + [("L", list(p)) for p in SUMMIT[1:]] +
                 [("Q", [*RC, *R2]), ("Z", [])])

# Snow cap: above a zig-zag snow line
SNOW_Y = 47.5
lx, lt = quad_x_at_y(L0, LC, L2, SNOW_Y); rx, rt = quad_x_at_y(R0, RC, R2, SNOW_Y)
lc1 = split_quad(L0, LC, L2, lt)[0]    # control point of the flank segment summit..snowline (same when reversed)
rc1 = split_quad(R0, RC, R2, rt)[0]
zig_x = [lx + (rx - lx) * i / 8 for i in range(9)]
zig_y = [SNOW_Y, 51.2, 48.0, 52.4, 48.3, 52.6, 48.1, 51.4, SNOW_Y]
zig = list(zip(zig_x, zig_y))
# snowline-left -> up the left flank -> across the summit -> down the right flank -> zig-zag back
cap = pts([("M", [lx, SNOW_Y]), ("Q", [*lc1, *L0])] + [("L", list(p)) for p in SUMMIT[1:]] +
          [("Q", [*rc1, rx, SNOW_Y])] + [("L", list(p)) for p in reversed(zig[1:-1])] + [("Z", [])])

FOLD_TOP, FOLD_BOT = (54.3, 34.7), (58.5, BASE)
shade = pts([("M", list(FOLD_TOP)), ("L", [56.3, 35.9]), ("L", [57.6, 35.1]), ("L", [59, 36]),
             ("Q", [*RC, *R2]), ("L", list(FOLD_BOT)), ("Z", [])])

shadow = pts([("M", [44, BASE]), ("L", [84, BASE]), ("L", [118, 100]), ("L", [78, 100]), ("Z", [])])
SHADOW_GRAD = dict(x1=66, y1=66, x2=88, y2=88, c1="#38000000", c2="#00000000")

# --- Background ---
sky = pts([("M", [0, 0]), ("L", [108, 0]), ("L", [108, HORIZON]), ("L", [0, HORIZON]), ("Z", [])])
sea = pts([("M", [0, HORIZON]), ("L", [108, HORIZON]), ("L", [108, 108]), ("L", [0, 108]), ("Z", [])])
sun = circle(74, 31, 8.5)
b1_petals, b1_center = blossom(33, 33, 1.0, 12)
b2_petals, b2_center = blossom(45.5, 23.5, 0.62, 40)
p1 = loose_petal(26.5, 47, 0.62, -35)
p2 = loose_petal(86, 47.5, 0.55, 55)
p3 = loose_petal(59, 25, 0.5, 20)

def wave(x, y, w):   # two gentle humps
    return f"M{f(x)},{f(y)} q{f(w/4)},{f(-w/5)} {f(w/2)},0 t{f(w/2)},0"
waves = [wave(24, 74, 11), wave(32, 84, 12), wave(55, 78, 9), wave(72, 87, 10)]

BG = [("path", sky, SKY, 1.0), ("path", sun, SUN, 0.95),
      ("path", b1_petals, BLOSSOM, 0.95), ("path", b1_center, BLOSSOM_CENTER, 1.0),
      ("path", b2_petals, BLOSSOM, 0.9), ("path", b2_center, BLOSSOM_CENTER, 1.0),
      ("path", p1, BLOSSOM, 0.85), ("path", p2, BLOSSOM, 0.85), ("path", p3, BLOSSOM, 0.8),
      ("path", sea, SEA, 1.0)] + [("stroke", w, WAVE, 1.0) for w in waves]
FG = [("grad", shadow, SHADOW_GRAD, 1.0), ("path", silhouette, FUJI_BODY, 1.0), ("path", cap, FUJI_CAP, 1.0),
      ("path", shade, FUJI_SHADE, 0.13)]

# Monochrome (themed icons): Fuji with the snow line cut out, plus the sun
band = [(x, y) for x, y in zig[1:-1]]
band_path = pts([("M", [band[0][0], band[0][1]])] + [("L", [x, y]) for x, y in band[1:]] +
                [("L", [x, y + 1.7]) for x, y in reversed(band)] + [("Z", [])])
MONO = [("evenodd", silhouette + " " + band_path, "#FF000000", 1.0), ("path", circle(74, 31, 7), "#FF000000", 1.0)]

# --- Writers ---
def argb_to_svg(c):   # #AARRGGBB -> (rgb, opacity)
    if len(c) == 9: return "#" + c[3:], int(c[1:3], 16) / 255
    return c, 1.0

def svg(layers, size=108, extra=""):
    defs, body = [], []
    for i, (kind, d, paint, alpha) in enumerate(layers):
        if kind == "grad":
            g = paint; (c1, o1), (c2, o2) = argb_to_svg(g["c1"]), argb_to_svg(g["c2"])
            defs.append(f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" x1="{g["x1"]}" y1="{g["y1"]}" x2="{g["x2"]}" y2="{g["y2"]}">'
                        f'<stop offset="0" stop-color="{c1}" stop-opacity="{o1:.3f}"/><stop offset="1" stop-color="{c2}" stop-opacity="{o2:.3f}"/></linearGradient>')
            body.append(f'<path d="{d}" fill="url(#g{i})"/>')
        elif kind == "stroke":
            body.append(f'<path d="{d}" fill="none" stroke="{paint}" stroke-width="1.6" stroke-linecap="round" stroke-opacity="{alpha}"/>')
        else:
            rgb, o = argb_to_svg(paint)
            rule = ' fill-rule="evenodd"' if kind == "evenodd" else ""
            body.append(f'<path d="{d}" fill="{rgb}" fill-opacity="{o * alpha:.3f}"{rule}/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 108 108">'
            f'<defs>{"".join(defs)}</defs>{extra}{"".join(body)}</svg>\n')

def vector(layers, comment):
    needs_aapt = any(k == "grad" for k, *_ in layers)
    ns = ' xmlns:aapt="http://schemas.android.com/aapt"' if needs_aapt else ""
    lines = [f'<?xml version="1.0" encoding="utf-8"?>', f'<!-- {comment} Generated by art/icon/gen_icon.py, do not edit by hand. -->',
             f'<vector xmlns:android="http://schemas.android.com/apk/res/android"{ns}',
             '    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">']
    for kind, d, paint, alpha in layers:
        if kind == "grad":
            g = paint
            lines += [f'    <path android:pathData="{d}">', '        <aapt:attr name="android:fillColor">',
                      f'            <gradient android:type="linear" android:startX="{g["x1"]}" android:startY="{g["y1"]}" '
                      f'android:endX="{g["x2"]}" android:endY="{g["y2"]}" android:startColor="{g["c1"]}" android:endColor="{g["c2"]}"/>',
                      '        </aapt:attr>', '    </path>']
        elif kind == "stroke":
            lines.append(f'    <path android:pathData="{d}" android:strokeColor="{paint}" android:strokeWidth="1.6" android:strokeLineCap="round"/>')
        else:
            a = f' android:fillAlpha="{alpha:g}"' if alpha < 1 else ""
            rule = ' android:fillType="evenOdd"' if kind == "evenodd" else ""
            lines.append(f'    <path android:pathData="{d}" android:fillColor="{paint}"{a}{rule}/>')
    lines.append('</vector>')
    return "\n".join(lines) + "\n"

(out / "shima-icon-background.svg").write_text(svg(BG), encoding="utf-8")
(out / "shima-icon-foreground.svg").write_text(svg(FG), encoding="utf-8")
(out / "shima-icon-monochrome.svg").write_text(svg(MONO), encoding="utf-8")
(out / "shima-icon-full.svg").write_text(svg(BG + FG, 432), encoding="utf-8")
(out / "ic_launcher_background.xml").write_text(vector(BG, "Shima launcher icon background: sakura sky, white sun, blossoms, rose sea."), encoding="utf-8")
(out / "ic_launcher_foreground.xml").write_text(vector(FG, "Shima launcher icon foreground: paper-fold Mount Fuji with long shadow."), encoding="utf-8")
(out / "ic_launcher_monochrome.xml").write_text(vector(MONO, "Shima launcher icon monochrome layer (Android 13 themed icons)."), encoding="utf-8")
print("ok", out)
