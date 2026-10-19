#!/usr/bin/env python3
"""Compose the Egregore mark: a generated tree-of-life node graph, ringed by a
deterministic zodiac wheel. Ring geometry, glyphs and packets are drawn here so
they are exact by construction rather than left to an image generator."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = 2                      # supersample factor
W = H = 800 * S            # logical 800x800
C = (W // 2, H // 2)

CYAN = (53, 230, 255)
MAGENTA = (255, 53, 200)
AMBER = (255, 154, 60)
GREEN = (77, 255, 158)
GLYPH_COLOURS = [CYAN, MAGENTA]

R_TICK = 372 * S
R_OUT = 350 * S
R_IN = 292 * S
R_GLYPH = 321 * S
R_TREE = 292 * S

SIGNS = "\u2648\u2649\u264a\u264b\u264c\u264d\u264e\u264f\u2650\u2651\u2652\u2653"
NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def polar(r, deg):
    a = math.radians(deg - 90.0)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def ring(d, r, colour, width):
    d.ellipse([C[0] - r, C[1] - r, C[0] + r, C[1] + r], outline=colour, width=width)


# ---- crisp layer -----------------------------------------------------------
crisp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(crisp)

ring(d, R_OUT, CYAN + (210,), 3 * S)
ring(d, R_IN, CYAN + (170,), 2 * S)
ring(d, R_TICK - 6 * S, MAGENTA + (140,), 2 * S)

for i in range(360):
    r1 = R_TICK - (16 * S if i % 30 == 0 else 9 * S if i % 10 == 0 else 4 * S)
    d.line([polar(r1, i), polar(R_TICK, i)],
           fill=(CYAN if i % 30 == 0 else (110, 120, 140)) + (200,), width=1 * S)

for i in range(12):
    a = i * 30
    d.line([polar(R_IN, a), polar(R_OUT, a)],
           fill=(80, 92, 112, 170), width=1 * S)

font_size = int(44 * S)
font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", font_size)
label_font = ImageFont.truetype("/usr/share/fonts/truetype/NotoSansMono-Regular.ttf", int(9 * S))

for i, ch in enumerate(SIGNS):
    a = i * 30 + 15
    x, y = polar(R_GLYPH, a)
    col = GLYPH_COLOURS[i % 2]
    d.text((x, y), ch, font=font, fill=col + (255,), anchor="mm")

# packets: determinstic spokes leaving the tree for the ring
for i, (a, r0, r1, col) in enumerate([
    (12, 258, 300, AMBER), (43, 262, 330, CYAN), (77, 255, 288, AMBER),
    (118, 260, 340, CYAN), (149, 252, 296, AMBER), (186, 264, 336, GREEN),
    (214, 258, 300, AMBER), (247, 260, 344, CYAN), (281, 253, 292, AMBER),
    (312, 262, 338, CYAN), (343, 256, 302, AMBER), (81, 264, 348, MAGENTA),
]):
    p0, p1 = polar(r0 * S, a), polar(r1 * S, a)
    d.line([p0, p1], fill=col + (170,), width=1 * S)
    for k, t in enumerate((0.55, 0.78, 1.0)):
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        s = (2.6 - k * 0.6) * S
        d.rectangle([x - s, y - s, x + s, y + s], fill=col + (255 - k * 55,))

# ---- ground + glow ---------------------------------------------------------
base = Image.new("RGB", (W, H), (0, 0, 0))
glow = crisp.filter(ImageFilter.GaussianBlur(7 * S))
base = ImageChops.add(base, glow.convert("RGB"))
base.paste(crisp, (0, 0), crisp)

# ---- the generated tree ----------------------------------------------------
tree = Image.open("assets/tree-source.jpeg").convert("RGB")
tw = int(556 * S)
th = int(tw * tree.height / tree.width)
tree = tree.resize((tw, th), Image.LANCZOS)

mask = Image.new("L", (tw, th), 0)
md = ImageDraw.Draw(mask)
cx, cy = tw / 2, th / 2
fade_in, fade_out = R_TREE * 0.80, R_TREE
steps = 90
for k in range(steps):
    r = fade_out * (1 - k / steps)
    alpha = 255 if r <= fade_in else int(255 * (1 - (r - fade_in) / (fade_out - fade_in)))
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)

base.paste(tree, (C[0] - tw // 2, C[1] - th // 2), mask)

# ---- scanlines + downscale -------------------------------------------------
scan = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(scan)
for y in range(0, H, 4 * S):
    sd.line([(0, y), (W, y)], fill=26, width=1 * S)
base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, scan)

out = base.resize((W // S, H // S), Image.LANCZOS)
out.save("assets/egregore.png")
print("wrote assets/egregore.png", out.size)
