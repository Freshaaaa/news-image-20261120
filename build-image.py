#!/usr/bin/env python3
"""Draw the news-image-20261120 entry: one page summing up the world news
of Friday 20 November 2026, rendered with PIL so every letter stays crisp
at 1024x1024. No network, no randomness, no clock: the same run always
writes the same bytes.

The page is a newspaper front page: a navy masthead naming the day, BY
REGION and BY FIELD bars computed from the 52 stories, a day-in-numbers
strip, a UTC timeline, 16 story cards (3 big, 13 small) each with a
PIL-drawn banner scene and a REPORTED / CLAIM / FORECAST tag, a dotted
world map with 16 numbered pins beside a THE VERDICT box, a 36-more list
in 3 columns, a DATE CHECK box and a sources footer with a HOW SURE ARE
WE? legend.

The day's three biggest stories lead the page: Russian missiles landing
in Poland, Russian strikes on three Kyiv bridges, and the World Court
holding Myanmar responsible for genocide against the Rohingya. The rest
spans the Anthropic IPO, the AI sell-off, COP31, the Hormuz tanker
fires, the UK-EU reset deal, a 6.7 quake in Peru, Estonia closing its
Russia border, BepiColombo reaching Mercury, the Palisades Fire verdict,
the $7.25bn Roundup settlement, a Houthi missile over Riyadh, the first
three-way Trump-Xi-Putin summit and Bitcoin sliding toward $61,700.

Every story on the page happened, or was first reported, on Friday
20 November 2026, verified against Reuters, AP, AFP, BBC, CNN, WSJ,
UN News, Carbon Brief, Yonhap, USGS, ESA, CoinDesk and Le Monde.
"""
import math
import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24
CW = W - 2 * M  # 976 content width

PAPER = (251, 250, 247)
INK = (17, 17, 19)
BODY = (64, 62, 58)
NAVY = (18, 32, 62)
NAVY_SOFT = (38, 56, 92)
GOLD = (198, 154, 60)
CRIMSON = (166, 25, 46)
GREY = (96, 94, 88)
CARD = (255, 255, 255)
RULE = (208, 202, 188)
PALE = (206, 219, 238)
RED = (178, 34, 34)
TEAL = (14, 120, 120)
ORANGE = (200, 110, 20)
GREEN = (16, 120, 70)
AMBER = (198, 138, 0)
BLUE = (36, 86, 170)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines, none wider than max_w."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, lines, x, y, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def trunc(d, text, font, max_w):
    """Shorten text to fit max_w, cutting at a word boundary + ellipsis."""
    if d.textlength(text, font=font) <= max_w:
        return text
    ell = "…"
    while text and d.textlength(text + ell, font=font) > max_w:
        text = text[:-1].rstrip()
        if " " in text:
            text = text.rsplit(" ", 1)[0]
        else:
            text = text[:-1]
    return text + ell


def vgrad(d, x0, y0, x1, y1, top, bottom, bands=8):
    """Vertical gradient as thin horizontal bands (PIL has no gradient)."""
    for i in range(bands):
        t = i / (bands - 1) if bands > 1 else 0
        col = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        y_a = y0 + (y1 - y0) * i / bands
        y_b = y0 + (y1 - y0) * (i + 1) / bands
        d.rectangle([x0, y_a, x1, y_b], fill=col)


def burst(d, cx, cy, r, col):
    """A starburst (explosion) centred on (cx, cy)."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def star5(d, cx, cy, r, col):
    """A five-pointed star (for the Chinese flag)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def pic_bust(d, cx, table_y, skin, hair, suit, tie):
    """A seated leader, drawn as a bust behind a table: hair cap, head,
    shoulders and a tie sliver. table_y is the top edge of the table."""
    hr = 6
    d.ellipse([cx - hr - 1, table_y - 26, cx + hr + 1, table_y - 14], fill=hair)
    d.ellipse([cx - hr, table_y - 23, cx + hr, table_y - 11], fill=skin)
    d.rounded_rectangle([cx - 12, table_y - 12, cx + 12, table_y],
                        radius=4, fill=suit)
    d.polygon([(cx - 2, table_y - 12), (cx + 2, table_y - 12),
               (cx + 3, table_y - 4), (cx, table_y - 1), (cx - 3, table_y - 4)],
              fill=tie)


def pic_scales(d, cx, cy, s, col):
    """Scales of justice: beam, two pans, central pillar."""
    w = max(2, int(s * 0.06))
    d.line([cx, cy - s * 0.30, cx, cy + s * 0.30], fill=col, width=w)
    d.line([cx - s * 0.38, cy - s * 0.22, cx + s * 0.38, cy - s * 0.22], fill=col, width=w)
    d.ellipse([cx - s * 0.07, cy - s * 0.38, cx + s * 0.07, cy - s * 0.24], fill=col)
    for dx in (-0.38, 0.38):
        d.line([cx + dx * s, cy - s * 0.22, cx + dx * s, cy + s * 0.02], fill=col, width=max(1, w - 1))
        d.polygon([(cx + dx * s - s * 0.16, cy + s * 0.02), (cx + dx * s + s * 0.16, cy + s * 0.02),
                   (cx + dx * s, cy + s * 0.18)], fill=col)
    d.rectangle([cx - s * 0.16, cy + s * 0.30, cx + s * 0.16, cy + s * 0.36], fill=col)


def pic_gavel(d, cx, cy, s, col):
    """A gavel, diagonal, over a sound block."""
    w = max(3, int(s * 0.09))
    d.line([cx - s * 0.30, cy + s * 0.28, cx + s * 0.34, cy - s * 0.30], fill=col, width=w)
    d.line([cx - s * 0.42, cy - s * 0.02, cx - s * 0.06, cy + s * 0.30], fill=col, width=int(w * 1.6))
    d.rectangle([cx - s * 0.30, cy + s * 0.34, cx + s * 0.30, cy + s * 0.42], fill=col)
    d.ellipse([cx + s * 0.30, cy - s * 0.34, cx + s * 0.44, cy - s * 0.20], fill=(255, 210, 60))


def pic_chart_down(d, cx, cy, s, col):
    """Falling bars with a red down-trend arrow."""
    w = max(2, int(s * 0.06))
    bars = [0.42, 0.34, 0.28, 0.18]
    bw = s * 0.16
    x0 = cx - s * 0.40
    for i, h in enumerate(bars):
        x = x0 + i * (bw + s * 0.04)
        d.rectangle([x, cy + s * 0.30 - h * s, x + bw, cy + s * 0.30], fill=col)
    d.line([cx - s * 0.44, cy - s * 0.28, cx + s * 0.10, cy - s * 0.02,
            cx + s * 0.44, cy + s * 0.10], fill=CRIMSON, width=w)
    d.polygon([(cx + s * 0.44, cy + s * 0.10), (cx + s * 0.44, cy - s * 0.10),
               (cx + s * 0.24, cy + s * 0.10)], fill=CRIMSON)


def pic_cyclone(d, cx, cy, s, col):
    """A spiral cyclone: three arcs and a calm eye."""
    for i, (r, a0, a1) in enumerate(((0.44, 20, 300), (0.32, 140, 420), (0.20, 260, 540))):
        d.arc([cx - s * r, cy - s * r, cx + s * r, cy + s * r], start=a0, end=a1,
              fill=col, width=max(3, int(s * 0.09)))
    d.ellipse([cx - s * 0.06, cy - s * 0.06, cx + s * 0.06, cy + s * 0.06], fill=col)

# ---------------- card banners ----------------
# Each banner is a wide scene at the top of its card, built in three
# layers: a vertical sky gradient (thin bands), a background scene
# (skyline, stars, rain, ground), and a foreground pictogram. Original
# drawings, made for this day's stories.

def draw_banner(img, d, x0, y0, x1, y1, kind, accent):
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = int(h * 0.78)
    if kind == "missile":
        # Pre-dawn city under alert: missile trail, burst over rooftops.
        vgrad(d, x0, y0, x1, y1, (60, 50, 70), (140, 90, 70))
        for bx, bw, bh in ((0.00, 0.15, 0.34), (0.17, 0.11, 0.24), (0.30, 0.16, 0.42),
                           (0.48, 0.11, 0.28), (0.61, 0.15, 0.38), (0.78, 0.11, 0.24),
                           (0.91, 0.09, 0.32)):
            d.rectangle([x0 + w * bx, y1 - h * bh, x0 + w * (bx + bw), y1],
                        fill=(30, 26, 40))
        for bx in (0.05, 0.35, 0.66, 0.84):
            for wy in (0.55, 0.70):
                d.rectangle([x0 + w * bx, y1 - h * wy, x0 + w * bx + 4, y1 - h * wy + 5],
                            fill=(255, 210, 110))
        for i in range(6):
            t = i / 5
            tx = x0 + w * (0.12 + t * 0.55)
            ty = cy - h * (0.30 - t * 0.55)
            d.ellipse([tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5], fill=(255, 210, 90))
        burst(d, x0 + w * 0.60, y0 + h * 0.22, int(h * 0.20), (255, 170, 60))
    elif kind == "bridge":
        # Night over the strait: arch, road deck, two explosion bursts.
        vgrad(d, x0, y0, x1, y1, (14, 22, 52), (28, 42, 78))
        for sx, sy in ((0.07, 0.22), (0.18, 0.60), (0.30, 0.16), (0.52, 0.72),
                       (0.66, 0.24), (0.79, 0.58), (0.90, 0.20)):
            d.ellipse([x0 + w * sx - 1.5, y0 + h * sy - 1.5,
                       x0 + w * sx + 1.5, y0 + h * sy + 1.5], fill=(255, 255, 255))
        d.ellipse([x0 + w * 0.55, y0 + 4, x0 + w * 0.55 + 16, y0 + 20], fill=(240, 238, 220))
        d.ellipse([x0 + w * 0.55 + 5, y0 + 2, x0 + w * 0.55 + 21, y0 + 18], fill=(28, 42, 78))
        d.rectangle([x0, y1 - h * 0.30, x1, y1 - h * 0.24], fill=(70, 80, 100))
        d.arc([cx - w * 0.30, y1 - h * 0.62, cx + w * 0.30, y1 - h * 0.10], 180, 360,
              fill=(120, 130, 150), width=3)
        for i in range(5):
            x = cx - w * 0.24 + i * w * 0.12
            d.line([x, y1 - h * 0.30, x, y1 - h * 0.52], fill=(120, 130, 150), width=2)
        burst(d, cx - w * 0.28, y1 - h * 0.48, int(h * 0.22), (255, 180, 60))
        burst(d, cx + w * 0.30, y1 - h * 0.36, int(h * 0.14), (255, 140, 60))
    elif kind == "icj":
        # The Hague: pale stone courthouse, the scales, a crimson 1ST
        # badge - the first state a world court holds liable for genocide.
        vgrad(d, x0, y0, x1, y1, (232, 228, 218), (200, 192, 176))
        for i in range(5):
            x = x0 + w * (0.06 + i * 0.19)
            d.rectangle([x, y1 - h * 0.62, x + w * 0.07, y1], fill=(120, 108, 88))
        d.rectangle([x0, y1 - h * 0.66, x1, y1 - h * 0.60], fill=(120, 108, 88))
        d.polygon([(x0 + w * 0.30, y1 - h * 0.66), (x0 + w * 0.70, y1 - h * 0.66),
                   (cx, y1 - h * 0.92)], fill=(140, 128, 106))
        d.rectangle([x0, y1 - h * 0.14, x1, y1], fill=(90, 80, 64))
        pic_scales(d, cx - w * 0.14, cy - 2, s, NAVY)
        # the 1ST badge sits bottom-left, clear of the confidence pill
        # that lives at the banner's top-right corner
        d.rounded_rectangle([x0 + 6, y1 - 24, x0 + 58, y1 - 5], radius=4, fill=CRIMSON)
        fb = f(SANS_B, 14)
        d.text((x0 + 32 - d.textlength("1ST", font=fb) / 2, y1 - 22),
               "1ST", font=fb, fill=(255, 255, 255))
    elif kind == "chart_down":
        d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
        for i in range(5):
            y = y0 + h * (0.18 + i * 0.16)
            d.line([x0 + 6, y, x1 - 6, y], fill=(220, 216, 206), width=1)
        pic_chart_down(d, cx, cy, s, NAVY)
    elif kind == "ant":
        # Nasdaq, first day: a dark chart with rising green candles.
        d.rectangle([x0, y0, x1, y1], fill=(14, 26, 46))
        for i in range(4):
            y = y0 + h * (0.20 + i * 0.20)
            d.line([x0 + 6, y, x1 - 6, y], fill=(40, 52, 74), width=1)
        tops = [cy + 9, cy + 6, cy + 4, cy + 1, cy - 2, cy - 5]
        pts = []
        for i, top in enumerate(tops):
            bx = x0 + 14 + i * 28
            d.line([bx + 4, top - 3, bx + 4, cy + 11], fill=(40, 200, 120), width=2)
            d.rectangle([bx, top, bx + 9, cy + 11], fill=(40, 200, 120))
            pts.append((bx + 4, top))
        d.line(pts, fill=(80, 230, 140), width=2)
        ef = f(SANS_B, 12)
        d.text((x0 + 6, y0 + 3), "ANT $97.17", font=ef, fill=(255, 255, 255))
    elif kind == "cop31":
        # Antalya: teal sky, globe, red thermometer, sun - and a rotated
        # FOSSIL FUELS CUT stamp across the middle.
        vgrad(d, x0, y0, x1, y1, (120, 200, 190), (40, 140, 140))
        d.ellipse([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
                  fill=(40, 110, 180))
        d.arc([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
              300, 60, fill=(90, 190, 120), width=3)
        d.arc([x0 + w * 0.06, cy - h * 0.34, x0 + w * 0.06 + h * 0.68, cy + h * 0.34],
              120, 250, fill=(90, 190, 120), width=3)
        d.ellipse([x0 + 6, y0 + 3, x0 + 18, y0 + 15], fill=(255, 230, 120))
        tx = x0 + w * 0.78
        d.rectangle([tx - 3, y0 + h * 0.16, tx + 3, y1 - h * 0.22], fill=(255, 255, 255))
        d.rectangle([tx - 3, y0 + h * 0.52, tx + 3, y1 - h * 0.22], fill=(220, 40, 40))
        d.ellipse([tx - 7, y1 - h * 0.26, tx + 7, y1 - h * 0.06], fill=(220, 40, 40))
        stamp = Image.new("RGBA", (140, 26), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rectangle([1, 1, 138, 24], outline=(200, 30, 40, 255), width=2)
        sf = f(SANS_B, 11)
        sd.text(((140 - sd.textlength("FOSSIL FUELS CUT", font=sf)) / 2, 6),
                "FOSSIL FUELS CUT", font=sf, fill=(200, 30, 40, 255))
        stamp = stamp.rotate(-7, expand=True, resample=Image.BICUBIC)
        img.paste(stamp, (int(cx + 8 - stamp.width / 2), int(cy - stamp.height / 2)), stamp)
    elif kind == "tanker":
        # Strait of Hormuz: a tanker on a burning sea, smoke and flame.
        vgrad(d, x0, y0, x1, y1, (200, 120, 60), (90, 40, 30))
        d.rectangle([x0, y1 - h * 0.30, x1, y1], fill=(30, 60, 90))
        for i in range(4):
            x = x0 + w * (0.06 + i * 0.22)
            d.arc([x, y1 - h * 0.30, x + w * 0.14, y1 - h * 0.14], 180, 360,
                  fill=(180, 210, 240), width=2)
        # hull, deck, bridge tower
        d.rectangle([x0 + w * 0.10, y1 - h * 0.52, x0 + w * 0.86, y1 - h * 0.34],
                    fill=(40, 40, 46))
        d.rectangle([x0 + w * 0.70, y1 - h * 0.72, x0 + w * 0.82, y1 - h * 0.52],
                    fill=(200, 200, 210))
        d.rectangle([x0 + w * 0.74, y1 - h * 0.80, x0 + w * 0.78, y1 - h * 0.72],
                    fill=(200, 200, 210))
        # flames and smoke above the midship tank
        burst(d, cx - w * 0.10, y1 - h * 0.62, int(h * 0.20), (255, 200, 60))
        burst(d, cx - w * 0.02, y1 - h * 0.70, int(h * 0.14), (255, 140, 40))
        d.ellipse([cx + w * 0.08, y0 + h * 0.10, cx + w * 0.20, y0 + h * 0.30],
                  fill=(80, 80, 90))
        d.ellipse([cx + w * 0.16, y0 + h * 0.02, cx + w * 0.26, y0 + h * 0.18],
                  fill=(60, 60, 70))
    elif kind == "reset":
        # Brussels: the EU flag and the Union Jack side by side, a gold
        # link joining the two poles - the reset deal.
        vgrad(d, x0, y0, x1, y1, (210, 225, 240), (170, 190, 210))
        # EU flag: blue field, ring of gold stars
        ex0, ey0 = x0 + w * 0.06, y0 + h * 0.16
        ew, eh = w * 0.30, h * 0.52
        d.rectangle([ex0, ey0, ex0 + ew, ey0 + eh], fill=(30, 60, 140))
        for i in range(8):
            ang = -math.pi / 2 + i * math.pi / 4
            sx = ex0 + ew / 2 + ew * 0.30 * math.cos(ang)
            sy = ey0 + eh / 2 + eh * 0.30 * math.sin(ang)
            d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 210, 60))
        d.line([ex0 + ew / 2, ey0 + eh, ex0 + ew / 2, y1 - h * 0.08],
               fill=(60, 60, 70), width=2)
        # Union Jack, simplified: blue field, white saltire, red cross
        ux0, uy0 = x0 + w * 0.60, y0 + h * 0.16
        uw, uh = w * 0.30, h * 0.52
        d.rectangle([ux0, uy0, ux0 + uw, uy0 + uh], fill=(30, 60, 140))
        d.line([ux0, uy0, ux0 + uw, uy0 + uh], fill=(255, 255, 255), width=3)
        d.line([ux0 + uw, uy0, ux0, uy0 + uh], fill=(255, 255, 255), width=3)
        d.line([ux0 + uw / 2, uy0, ux0 + uw / 2, uy0 + uh], fill=(200, 40, 40), width=5)
        d.line([ux0, uy0 + uh / 2, ux0 + uw, uy0 + uh / 2], fill=(200, 40, 40), width=5)
        d.line([ux0 + uw / 2, uy0 + uh, ux0 + uw / 2, y1 - h * 0.08],
               fill=(60, 60, 70), width=2)
        # gold link between the poles
        d.ellipse([cx - 6, cy + 2, cx + 6, cy + 14], outline=GOLD, width=3)
    elif kind == "quake":
        # Central Peru: a cracked road, a tilted house, dust in the air.
        vgrad(d, x0, y0, x1, y1, (190, 170, 140), (150, 125, 95))
        d.rectangle([x0, y1 - h * 0.28, x1, y1], fill=(120, 100, 75))
        # zig-zag crack across the ground
        pts = [(x0 + w * 0.10, y1 - h * 0.28), (x0 + w * 0.30, y1 - h * 0.18),
               (x0 + w * 0.45, y1 - h * 0.30), (x0 + w * 0.62, y1 - h * 0.16),
               (x0 + w * 0.80, y1 - h * 0.28), (x0 + w * 0.95, y1 - h * 0.20)]
        d.line(pts, fill=(40, 32, 24), width=3)
        # tilted house
        hx, hy = cx - w * 0.22, y1 - h * 0.62
        d.rectangle([hx, hy, hx + w * 0.30, y1 - h * 0.28], fill=(210, 180, 130))
        d.polygon([(hx - 4, hy), (hx + w * 0.15, hy - h * 0.16),
                   (hx + w * 0.30 + 4, hy)], fill=(150, 70, 55))
        d.rectangle([hx + w * 0.10, y1 - h * 0.46, hx + w * 0.18, y1 - h * 0.28],
                    fill=(60, 50, 40))
        # dust puffs
        for dx, dy, r in ((0.15, 0.30, 5), (0.55, 0.22, 6), (0.85, 0.34, 4)):
            d.ellipse([x0 + w * dx - r, y0 + h * dy - r,
                       x0 + w * dx + r, y0 + h * dy + r], fill=(230, 220, 200))
    elif kind == "border":
        # Estonia's Russia border: a striped barrier arm, lowered, with
        # a CLOSED sign and a watchtower behind it.
        vgrad(d, x0, y0, x1, y1, (200, 210, 220), (160, 175, 190))
        # watchtower
        tx = x0 + w * 0.78
        d.rectangle([tx - 6, y0 + h * 0.30, tx + 6, y1], fill=(90, 80, 70))
        d.rectangle([tx - 12, y0 + h * 0.18, tx + 12, y0 + h * 0.34], fill=(70, 62, 55))
        d.rectangle([tx - 8, y0 + h * 0.22, tx + 8, y0 + h * 0.30], fill=(200, 220, 240))
        # barrier arm, red-white stripes, lowered across the road
        d.rectangle([x0 + w * 0.06, y1 - h * 0.42, x0 + w * 0.72, y1 - h * 0.30],
                    fill=(255, 255, 255))
        for i in range(6):
            sx = x0 + w * (0.06 + i * 0.11)
            d.rectangle([sx, y1 - h * 0.42, sx + w * 0.055, y1 - h * 0.30],
                        fill=(200, 40, 40))
        d.rectangle([x0 + w * 0.06, y1 - h * 0.30, x0 + w * 0.10, y1], fill=(60, 60, 70))
        # CLOSED sign
        d.rounded_rectangle([cx - 26, y0 + 4, cx + 26, y0 + 16], radius=3, fill=CRIMSON)
        cf = f(SANS_B, 8)
        d.text((cx - d.textlength("CLOSED", font=cf) / 2, y0 + 6),
               "CLOSED", font=cf, fill=(255, 255, 255))
    elif kind == "space":
        # BepiColombo at Mercury: black sky, stars, a cratered grey
        # planet and a small spacecraft with solar wings.
        d.rectangle([x0, y0, x1, y1], fill=(8, 10, 26))
        for sx, sy in ((0.06, 0.20), (0.16, 0.55), (0.28, 0.12), (0.45, 0.62),
                       (0.60, 0.18), (0.74, 0.50), (0.88, 0.24), (0.94, 0.60)):
            d.ellipse([x0 + w * sx - 1, y0 + h * sy - 1, x0 + w * sx + 1, y0 + h * sy + 1],
                      fill=(255, 255, 255))
        # Mercury: grey disc, darker craters
        px, py, pr = x0 + w * 0.30, cy, h * 0.36
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(160, 155, 145))
        for dx, dy, r in ((-0.4, -0.3, 0.12), (0.3, 0.2, 0.15), (-0.1, 0.4, 0.10),
                          (0.45, -0.35, 0.09)):
            d.ellipse([px + dx * pr - r * pr, py + dy * pr - r * pr,
                       px + dx * pr + r * pr, py + dy * pr + r * pr],
                      fill=(120, 115, 108))
        # spacecraft: gold body, two blue solar wings
        sx = x0 + w * 0.72
        d.rectangle([sx - 14, cy - 5, sx - 2, cy + 5], fill=(40, 90, 180))
        d.rectangle([sx + 2, cy - 5, sx + 14, cy + 5], fill=(40, 90, 180))
        d.rectangle([sx - 5, cy - 8, sx + 5, cy + 8], fill=(220, 180, 60))
        d.line([sx - 5, cy, px + pr + 2, cy], fill=(255, 230, 120), width=1)
    elif kind == "gavel":
        # A courtroom: wood tones, gavel over a sound block.
        vgrad(d, x0, y0, x1, y1, (120, 84, 52), (84, 58, 36))
        d.rectangle([x0, y1 - h * 0.16, x1, y1], fill=(60, 40, 24))
        for i in range(4):
            x = x0 + w * (0.10 + i * 0.24)
            d.rectangle([x, y0 + h * 0.12, x + w * 0.10, y1 - h * 0.16], fill=(150, 110, 70))
        pic_gavel(d, cx, cy - 2, s, (250, 240, 220))
    elif kind == "settle":
        # The $7.25bn settlement: a signed document, a pen, a gold seal.
        vgrad(d, x0, y0, x1, y1, (235, 230, 215), (205, 195, 175))
        dx0, dy0 = x0 + w * 0.22, y0 + h * 0.10
        dx1, dy1 = x0 + w * 0.78, y1 - h * 0.08
        d.rectangle([dx0, dy0, dx1, dy1], fill=(255, 255, 255), outline=(150, 140, 120))
        for i in range(4):
            y = dy0 + 8 + i * 7
            d.line([dx0 + 8, y, dx1 - 8, y], fill=(180, 175, 160), width=1)
        # signature squiggle
        d.arc([dx0 + 10, dy1 - 16, dx0 + 34, dy1 - 4], 200, 340, fill=NAVY, width=2)
        d.arc([dx0 + 30, dy1 - 18, dx0 + 52, dy1 - 6], 180, 320, fill=NAVY, width=2)
        # gold seal
        d.ellipse([dx1 - 20, dy0 + 6, dx1 - 6, dy0 + 20], fill=GOLD, outline=(150, 110, 30))
        # pen
        d.line([x0 + w * 0.84, y1 - h * 0.30, x0 + w * 0.94, y0 + h * 0.22],
               fill=(30, 30, 36), width=3)
        d.polygon([(x0 + w * 0.94, y0 + h * 0.22), (x0 + w * 0.96, y0 + h * 0.14),
                   (x0 + w * 0.92, y0 + h * 0.16)], fill=(200, 160, 60))
    elif kind == "tower":
        # Riyadh's tallest tower at dusk: a glass slab, windows blown
        # out across seven floors, a warning glow at the base.
        vgrad(d, x0, y0, x1, y1, (70, 60, 90), (150, 100, 80))
        tx0, tx1 = cx - w * 0.14, cx + w * 0.14
        d.rectangle([tx0, y0 + h * 0.08, tx1, y1], fill=(50, 70, 110))
        d.rectangle([tx0 - 4, y0 + h * 0.02, tx1 + 4, y0 + h * 0.10], fill=(30, 45, 75))
        for r in range(9):
            y = y0 + h * (0.16 + r * 0.085)
            for c in range(4):
                x = tx0 + 4 + c * (tx1 - tx0 - 8) / 4
                lit = (r in (3, 4, 5)) and (c in (1, 2))
                d.rectangle([x, y, x + (tx1 - tx0 - 8) / 4 - 3, y + 5],
                            fill=(20, 20, 26) if lit else (255, 210, 110))
        # neighbouring blocks
        d.rectangle([x0 + w * 0.04, y1 - h * 0.30, x0 + w * 0.18, y1], fill=(40, 36, 52))
        d.rectangle([x0 + w * 0.82, y1 - h * 0.24, x0 + w * 0.96, y1], fill=(40, 36, 52))
        burst(d, cx, y0 + h * 0.42, int(h * 0.12), (255, 170, 60))
    elif kind == "summit":
        # Shenzhen hall in daylight: pale walls so the dark suits read,
        # three flags on poles, three seated leaders behind a cream table
        # with nameplates.
        vgrad(d, x0, y0, x1, y1, (216, 222, 236), (182, 194, 214))
        table_y = y1 - 13
        d.rectangle([x0, table_y, x1, y1], fill=(232, 226, 210))
        d.line([x0, table_y, x1, table_y], fill=GOLD, width=2)
        leaders = [
            ("TRUMP", (240, 205, 170), (240, 210, 110), (30, 30, 36), (200, 40, 40), "us"),
            ("XI", (232, 190, 160), (30, 30, 34), (24, 24, 30), (200, 40, 40), "cn"),
            ("PUTIN", (238, 200, 165), (170, 170, 175), (28, 28, 34), (40, 90, 180), "ru"),
        ]
        for i, (name, skin, hair, suit, tie, flag) in enumerate(leaders):
            fx = cx + (i - 1) * w * 0.27
            fw, fh = 24, 15
            d.line([fx, y0 + 2, fx, table_y], fill=(100, 100, 110), width=2)
            if flag == "us":
                for j in range(5):
                    d.rectangle([fx - fw / 2, y0 + 2 + j * fh / 5,
                                 fx + fw / 2, y0 + 2 + (j + 1) * fh / 5],
                                fill=(178, 34, 34) if j % 2 == 0 else (255, 255, 255))
                d.rectangle([fx - fw / 2, y0 + 2, fx - fw / 2 + fw * 0.45, y0 + 2 + fh * 0.4],
                            fill=(30, 50, 110))
            elif flag == "cn":
                d.rectangle([fx - fw / 2, y0 + 2, fx + fw / 2, y0 + 2 + fh], fill=(222, 40, 40))
                star5(d, fx - fw * 0.22, y0 + 2 + fh * 0.32, 4, (255, 210, 60))
            else:
                for j, c in enumerate([(255, 255, 255), (40, 90, 180), (200, 40, 40)]):
                    d.rectangle([fx - fw / 2, y0 + 2 + j * fh / 3,
                                 fx + fw / 2, y0 + 2 + (j + 1) * fh / 3], fill=c)
            pic_bust(d, fx, table_y, skin, hair, suit, tie)
            fn = f(SANS_B, 7)
            d.text((fx - d.textlength(name, font=fn) / 2, y1 - 11),
                   name, font=fn, fill=NAVY)
    elif kind == "bitcoin":
        # Bitcoin slides: a dark board, a big gold B in a ring, a red
        # arrow falling to the $61,700 line.
        d.rectangle([x0, y0, x1, y1], fill=(16, 20, 34))
        for i in range(4):
            y = y0 + h * (0.20 + i * 0.20)
            d.line([x0 + 6, y, x1 - 6, y], fill=(40, 52, 74), width=1)
        bx, by = cx - w * 0.18, cy
        d.ellipse([bx - 16, by - 16, bx + 16, by + 16], outline=GOLD, width=3)
        bf = f(SANS_B, 20)
        d.text((bx - d.textlength("B", font=bf) / 2, by - 11), "B", font=bf, fill=GOLD)
        d.line([bx - 3, by - 18, bx - 3, by + 18], fill=GOLD, width=2)
        d.line([bx + 3, by - 18, bx + 3, by + 18], fill=GOLD, width=2)
        # falling arrow, right side
        ax0, ay0 = cx + w * 0.10, y0 + h * 0.18
        ax1, ay1 = cx + w * 0.38, y1 - h * 0.18
        d.line([ax0, ay0, ax1, ay1], fill=CRIMSON, width=4)
        d.polygon([(ax1, ay1), (ax1 - 10, ay1 - 2), (ax1 - 2, ay1 - 10)], fill=CRIMSON)
        pf = f(SANS_B, 11)
        d.text((x0 + 6, y0 + 3), "$61,700", font=pf, fill=(255, 255, 255))
    else:
        # fallback: a plain accent scene with the day's number
        vgrad(d, x0, y0, x1, y1, accent, (20, 20, 26))
        pic_cyclone(d, cx, cy, s, (255, 255, 255))

# ---------------- data ----------------

# Cards: (number, region, field, topic, verify, accent, banner kind,
#         headline, body, confidence). Headlines: big <= 56 chars, 5-col
#         small <= 42, 4-col small <= 54. Bodies: big <= 86, 5-col <= 60,
#         4-col <= 76. Confidence: REPORTED = confirmed by named sources;
#         CLAIM = one side says it, unverified; FORECAST = a poll, a draft
#         or a schedule (what happens next, not what happened).
CARDS = [
    (1, "EUROPE", "War", "POLAND", "REUTERS", CRIMSON, "missile",
     "Russian missiles land in Poland",
     "Two missiles and a drone came down; Poland calls it a deliberate provocation.",
     "REPORTED"),
    (2, "EUROPE", "War", "KYIV", "REUTERS", CRIMSON, "bridge",
     "Russian strikes hit three Kyiv bridges",
     "3 killed, ~15 injured; follows Ukraine hitting the Crimea Bridge a third time.",
     "REPORTED"),
    (3, "WORLD", "Justice", "GENOCIDE", "UN NEWS", CRIMSON, "icj",
     "World Court: Myanmar committed genocide",
     "First state held liable for genocide against the Rohingya; reparations ordered.",
     "REPORTED"),
    (4, "WORLD", "Markets", "SELL-OFF", "WSJ", NAVY, "chart_down",
     "AI sell-off drags world markets down",
     "S&P 500 -3.7% into correction; Nikkei -5.06%.",
     "REPORTED"),
    (5, "AMERICAS", "Markets", "IPO", "WSJ", NAVY, "ant",
     "Anthropic debuts on Nasdaq as ANT",
     "$81.3bn, the largest IPO on record; closed $97.17, +17%.",
     "REPORTED"),
    (6, "EUROPE", "Climate", "COP31", "CARBON BRIEF", TEAL, "cop31",
     "COP31 draft drops fossil fuels",
     "Second draft omits fossil fuels; talks past deadline.",
     "REPORTED"),
    (7, "MIDDLE EAST", "War", "HORMUZ", "REUTERS", ORANGE, "tanker",
     "Tankers keep catching fire in Hormuz",
     "US blockade; Iran attacks; IEA: record energy shock.",
     "REPORTED"),
    (8, "EUROPE", "Diplomacy", "RESET", "BBC", NAVY_SOFT, "reset",
     "UK and EU sign landmark reset deal",
     "Food trade, carbon markets, youth mobility (ages 18-31).",
     "REPORTED"),
    (9, "AMERICAS", "Society", "QUAKE", "USGS", ORANGE, "quake",
     "Magnitude 6.7 earthquake hits central Peru",
     "Cerro de Pasco; one injured, buildings and roads damaged.",
     "REPORTED"),
    (10, "EUROPE", "Politics", "BORDER", "REUTERS", NAVY, "border",
     "Estonia to close Russia border crossings",
     "After sabotage attack; from Dec 1, at least six months.",
     "REPORTED"),
    (11, "WORLD", "Science", "MERCURY", "ESA", BLUE, "space",
     "BepiColombo reaches Mercury",
     "ESA/JAXA spacecraft arrives after an eight-year journey.",
     "REPORTED"),
    (12, "AMERICAS", "Justice", "PALISADES", "AP", NAVY, "gavel",
     "Jury convicts man who started Palisades Fire",
     "Jonathan Rinderknecht found guilty of starting the fire.",
     "REPORTED"),
    (13, "AMERICAS", "Justice", "ROUNDUP", "AP", NAVY_SOFT, "settle",
     "Judge approves $7.25bn Bayer settlement",
     "Missouri court signs off on the Roundup cancer settlement.",
     "REPORTED"),
    (14, "MIDDLE EAST", "War", "RIYADH", "REUTERS", CRIMSON, "tower",
     "Houthi missile damages Riyadh's tallest tower",
     "Windows blown out across 7-8 floors; no injuries reported.",
     "REPORTED"),
    (15, "WORLD", "Diplomacy", "SUMMIT", "AP", NAVY, "summit",
     "Trump, Xi and Putin agree nuclear-risk talks",
     "First three-way summit; accord on human oversight of military AI.",
     "REPORTED"),
    (16, "WORLD", "Markets", "BITCOIN", "COINDESK", ORANGE, "bitcoin",
     "Bitcoin drops near $61,700",
     "Lowest since July; third straight day down.",
     "REPORTED"),
]

# 36 more stories: (number, region, field, city, headline). Headlines are
# rewritten short (city names are not repeated in them) so every item fits
# its column whole at 10pt - the build asserts zero truncation.
MORE = [
    (17, "AMERICAS", "Politics", "WASHINGTON", "Iran war powers rejected 51-48."),
    (18, "AMERICAS", "Politics", "WASHINGTON", "Trump: no rush on next Iran step."),
    (19, "EUROPE", "Diplomacy", "MOSCOW", "Zelensky calls Putin a killer."),
    (20, "ASIA", "Politics", "DHAKA", "Violence ahead of Hasina's return."),
    (21, "AMERICAS", "Justice", "TEXAS", "Hour-long execution draws scrutiny."),
    (22, "MIDDLE EAST", "War", "BAGHDAD", "Iraqi forces retake Jurf al-Nasr."),
    (23, "MIDDLE EAST", "War", "GAZA", "Israeli strikes kill Palestinians."),
    (24, "AMERICAS", "Justice", "NEW YORK", "Gupta gets 19+ years in murder plot."),
    (25, "AFRICA", "Society", "NIGERIA", "Boat of funeral mourners capsizes."),
    (26, "AFRICA", "Society", "SENEGAL", "Migrant boat capsizes off Senegal."),
    (27, "ASIA", "Markets", "TOKYO", "Core inflation hits year high."),
    (28, "AMERICAS", "Markets", "CALIFORNIA", "State subpoenas Nvidia over China."),
    (29, "AMERICAS", "Markets", "NEW YORK", "Card giants disclose vendor breaches."),
    (30, "ASIA", "Markets", "TAIPEI", "TSMC, Samsung pause China chip sales."),
    (31, "ASIA", "Diplomacy", "BEIJING", "Bloomberg reporter barred from summit."),
    (32, "ASIA", "Diplomacy", "NEW DELHI", "First Pakistan minister visit since war."),
    (33, "ASIA", "Politics", "DHAKA", "Awami League calls nationwide protest."),
    (34, "AMERICAS", "Politics", "OTTAWA", "2026 budget passes House, 162-151."),
    (35, "AMERICAS", "Politics", "VICTORIA", "BC's first Conservative win in a century."),
    (36, "AMERICAS", "Science", "MOUNTAIN VIEW", "Google launches Gemini 4 Neon."),
    (37, "AMERICAS", "Science", "REDMOND", "Nvidia, Microsoft deepen AI partnership."),
    (38, "WORLD", "Markets", "BINANCE", "Hacker moves ~$600M in Ether in two days."),
    (39, "AMERICAS", "Markets", "WASHINGTON", "SEC charges 8 over fake crypto fraud."),
    (40, "AMERICAS", "War", "WASHINGTON", "US expands military ops in LatAm."),
    (41, "AMERICAS", "Politics", "SAN SALVADOR", "Bukele seeks third term after reform."),
    (42, "AFRICA", "Justice", "ABUJA", "Nigeria to end jail for attempted suicide."),
    (43, "WORLD", "Diplomacy", "NEW YORK", "Race for next UN chief exposes divisions."),
    (44, "ASIA", "Diplomacy", "BEIJING", "Xi hails 'turnaround' with Australia."),
    (45, "AMERICAS", "Politics", "WASHINGTON", "Cyber chief replaced after outages."),
    (46, "AMERICAS", "Politics", "BUENOS AIRES", "Senate approves disability framework."),
    (47, "EUROPE", "Diplomacy", "COPENHAGEN", "Denmark expels Russian attache."),
    (48, "MIDDLE EAST", "War", "RIYADH", "Air defences down three Houthi missiles."),
    (49, "EUROPE", "Diplomacy", "BRUSSELS", "EU adopts €1bn military aid to Ukraine."),
    (50, "AMERICAS", "Diplomacy", "WASHINGTON", "US sanctions four Iranians."),
    (51, "EUROPE", "Justice", "PARIS", "Depardieu, Houellebecq face rape probe."),
    (52, "AMERICAS", "Society", "WASHINGTON", "US loses measles elimination status."),
]

NUMBERS = [
    ("$81.3bn", "Anthropic's record IPO"),
    ("6.7", "Peru earthquake magnitude"),
    ("$7.25bn", "Bayer Roundup settlement"),
    ("-3.7%", "S&P 500 into correction"),
    ("100,000", "UK-EU youth places a year"),
    ("$61,700", "Bitcoin's low since July"),
]

# the day in UTC
UTC_TIMELINE = [
    ("01:40", "Peru quake: 6.7"),
    ("06:00", "Bitcoin nears $61,700"),
    ("09:00", "ICJ: Myanmar genocide"),
    ("12:30", "COP31 drops fossil fuels"),
    ("14:30", "ANT debuts, $97.17"),
    ("16:10", "UK-EU reset deal signed"),
    ("19:20", "Poland: missiles land"),
]

# (number, lat, lon) for the map pins — one per card
PINS = [
    (1, 52.2, 21.0), (2, 50.45, 30.52), (3, 52.08, 4.32), (4, 35.7, 139.7),
    (5, 40.7, -74.0), (6, 36.9, 30.7), (7, 26.5, 56.3), (8, 50.85, 4.35),
    (9, -10.7, -76.3), (10, 59.4, 24.7), (11, 49.87, 8.65), (12, 34.05, -118.24),
    (13, 38.63, -90.2), (14, 24.71, 46.68), (15, 22.55, 114.06), (16, 1.35, 103.8),
]

# display offsets (dx, dy) for pins that would overlap at their true spot;
# a thin leader line is drawn from the true spot to the nudged pin.
PIN_OFF = {
    1: (-2, 12), 2: (-8, 4), 3: (-14, -4), 6: (10, 4),
    8: (-4, 10), 10: (12, -4), 11: (6, -6),
}

# dotted world map: landmasses as lon/lat ellipses (centre lon, centre lat,
# half-width lon, half-height lat); a dot is drawn for every grid cell
# whose centre falls inside one of them.
LANDMASSES = [
    (-100, 47, 58, 20), (-152, 64, 18, 8), (-86, 14, 12, 7), (-42, 73, 14, 9),
    (-60, -14, 19, 27), (14, 53, 26, 15), (-2, 54, 4, 5), (17, 3, 31, 32),
    (47, -19, 3, 8), (48, 30, 18, 12), (70, 45, 30, 18), (115, 42, 35, 20),
    (78, 21, 11, 11), (103, 13, 11, 9), (114, -2, 24, 5), (134, -25, 19, 11),
    (141, -5, 9, 4), (139, 37, 4, 6), (172, -41, 4, 6),
]


def _on_land(lon, lat):
    for clon, clat, hlon, hlat in LANDMASSES:
        if ((lon - clon) / hlon) ** 2 + ((lat - clat) / hlat) ** 2 <= 1:
            return True
    return False


# region and field counts, computed from the story data (never hand-counted)
REGION_ORDER = ["ASIA", "EUROPE", "MIDDLE EAST", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]
FIELD_ORDER = ["Diplomacy", "Justice", "Climate", "Markets", "War", "Culture",
               "Politics", "Society", "Science"]
_rc = Counter([c[1] for c in CARDS] + [m[1] for m in MORE])
_fc = Counter([c[2] for c in CARDS] + [m[2] for m in MORE])
REGIONS = [(r, _rc[r]) for r in REGION_ORDER if _rc[r]]
FIELDS = [(fld, _fc[fld]) for fld in FIELD_ORDER if _fc[fld]]

LEFT_OUT = ("Crimea Bridge, second strike, Wed 18 Nov · Anthropic IPO priced "
            "$83, Thu 19 Nov · Hormuz tanker fires, an IRGC claim from 4 Nov · "
            "BepiColombo launched, Oct 2018")
NOT_YET = ("COP31 closing text (talks run past deadline) · Estonia's border "
           "closure (from 1 Dec) · the next Iran step (Trump: 'see what happens "
           "after January 1')")
NOTE = ("This page covers only Friday 20 November 2026. Every story here "
        "happened, or was first reported, on that day.")

CONF_COLOUR = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": BLUE}
VERDICT = [
    "Two missiles and a drone land in Poland.",
    "Warsaw calls it a deliberate provocation.",
    "NATO calls it a grave violation.",
]
LEGEND = ("HOW SURE ARE WE? REPORTED = confirmed by named sources · CLAIM = "
          "one side says, unverified · FORECAST = poll, draft or schedule")

# ---------------- card drawing ----------------

def draw_card(img, d, card, x, y, w, h, big):
    num, region, field, topic, verify, accent, kind, headline, body, conf = card
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE)
    d.rectangle([x, y, x + w, y + 3], fill=accent)
    if big:
        bh = 48
        hs, ts, bs, vs = 18, 12, 13, 10
    else:
        bh = 34
        hs, ts, bs, vs = 13, 10, 11, 8
    draw_banner(img, d, x + 1, y + 4, x + w - 1, y + 3 + bh, kind, accent)
    # confidence pill, top-right of the banner (art is kept clear of it)
    cf = f(SANS_B, 8 if big else 7)
    pw = d.textlength(conf, font=cf) + 10
    ph = 13 if big else 12
    px1 = x + w - 5
    d.rounded_rectangle([px1 - pw, y + 6, px1, y + 6 + ph], radius=5,
                        fill=CONF_COLOUR[conf])
    d.text((px1 - pw + 5, y + 6 + (ph - (8 if big else 7)) // 2),
           conf, font=cf, fill=(255, 255, 255))
    ty = y + 3 + bh + 4
    ftag = f(SANS_B, ts)
    fv = f(SANS, vs)
    # tag + verify must both fit: drop the region, then shorten the verify
    # to its first source, rather than ever showing a truncated "…"
    tag = f"{num:02d} · {region} · {topic}"
    vt = verify
    gap = 6
    avail = w - 14
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        tag = f"{num:02d} · {topic}"
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        vt = verify.split(" · ")[0]
    if d.textlength(tag, font=ftag) + gap + d.textlength(vt, font=fv) > avail:
        vt = ""
    d.text((x + 9, ty), tag, font=ftag, fill=accent)
    if vt:
        d.text((x + w - 9 - d.textlength(vt, font=fv), ty + (ts - vs) // 2),
               vt, font=fv, fill=GREY)
    hy = ty + ts + 4
    fh = f(SANS_B, hs)
    for ln in wrap(d, headline, fh, w - 18)[:2 if big else 3]:
        d.text((x + 9, hy), ln, font=fh, fill=INK)
        hy += hs + 1
    fb = f(SANS, bs)
    by = hy + (2 if big else 1)
    for ln in wrap(d, body, fb, w - 18)[:2]:
        d.text((x + 9, by), ln, font=fb, fill=BODY)
        by += bs


# ---------------- page sections ----------------

def draw_header(d, y):
    hh = 68
    d.rectangle([M, y, M + CW, y + hh], fill=NAVY)
    bx0, bx1 = M + 12, M + 108
    d.rectangle([bx0, y + 10, bx1, y + hh - 10], fill=(255, 255, 255))
    fn = f(SANS_B, 20)
    d.text((bx0 + (bx1 - bx0 - d.textlength("NOV 20", font=fn)) / 2, y + 14),
           "NOV 20", font=fn, fill=NAVY)
    fs = f(SANS_B, 12)
    d.text((bx0 + (bx1 - bx0 - d.textlength("FRI · 2026", font=fs)) / 2, y + 38),
           "FRI · 2026", font=fs, fill=CRIMSON)
    d.text((M + 120, y + 10), "Friday 20 November 2026",
           font=f(SERIF, 30), fill=(255, 255, 255))
    d.text((M + 120, y + 46),
           "The world, one page. Everything here happened — or was first reported — on that day.",
           font=f(SANS, 11), fill=PALE)
    total = len(CARDS) + len(MORE)
    cnt = f"{total} STORIES · {len(REGIONS)} REGIONS · {len(FIELDS)} FIELDS · 16 CARDS · ONE PAGE"
    fc = f(SANS_B, 10)
    d.text((M + CW - 12 - d.textlength(cnt, font=fc), y + 15), cnt, font=fc, fill=GOLD)
    d.text((M + CW - 12 - d.textlength("ONE DAY · ONE PAGE", font=fc), y + 32),
           "ONE DAY · ONE PAGE", font=fc, fill=(255, 255, 255))
    return y + hh


def draw_numbers(d, y):
    """Day-in-numbers strip: big navy number on top, small description below."""
    d.rectangle([M, y, M + CW, y + 29], fill=(255, 255, 255), outline=RULE)
    n = len(NUMBERS)
    seg = CW / n
    fn = f(SANS_B, 13)
    fv = f(SANS, 10)
    for i, (num, desc) in enumerate(NUMBERS):
        cx = M + seg * i + seg / 2
        d.text((cx - d.textlength(num, font=fn) / 2, y + 1), num, font=fn, fill=NAVY)
        d.text((cx - d.textlength(desc, font=fv) / 2, y + 16), desc, font=fv, fill=BODY)
        if i:
            d.line([M + seg * i, y + 3, M + seg * i, y + 27], fill=RULE, width=1)
    return y + 30


def draw_strip(d, y, items, name_font_size=9, val_font_size=11, name_is_bold=True):
    """A labelled horizontal strip: (label, value) pairs separated by rules."""
    n = len(items)
    seg = CW / n
    fn = f(SANS_B if name_is_bold else SANS, name_font_size)
    fv = f(SANS_B, val_font_size)
    for i, (label, val) in enumerate(items):
        cx = M + seg * i + seg / 2
        d.text((cx - d.textlength(label, font=fn) / 2, y), label, font=fn, fill=GREY)
        d.text((cx - d.textlength(val, font=fv) / 2, y + name_font_size + 2),
               val, font=fv, fill=INK)
        if i:
            d.line([M + seg * i, y + 2, M + seg * i, y + name_font_size + val_font_size + 5],
                   fill=RULE, width=1)
    return y + name_font_size + val_font_size + 5


def draw_timeline(d, y, items):
    d.text((M, y), "THE DAY BY HOURS", font=f(SANS_B, 10), fill=GREY)
    y0 = y + 12
    seg = CW / len(items)
    d.line([M, y0 + 3, M + CW, y0 + 3], fill=RULE, width=1)
    ft = f(SANS_B, 10)
    fe = f(SANS, 10)
    for i, (t, txt) in enumerate(items):
        cx = M + seg * i + seg / 2
        d.ellipse([cx - 3.5, y0, cx + 3.5, y0 + 7], fill=NAVY)
        d.text((cx - d.textlength(t, font=ft) / 2, y0 + 10), t, font=ft, fill=NAVY)
        d.text((cx - d.textlength(txt, font=fe) / 2, y0 + 21), txt, font=fe, fill=BODY)
    return y0 + 31


def draw_map_verdict(d, y, h):
    """Dotted world map (left) with 16 numbered pins, and THE VERDICT box
    (right) - the Poland missile incident in three lines, dark navy."""
    mw = 600
    vw = CW - mw - 16
    vx = M + mw + 16
    d.text((M, y), "WHERE IT HAPPENED — 16 PINS, ONE PER CARD",
           font=f(SANS_B, 10), fill=GREY)
    d.text((vx, y), "THE VERDICT — POLAND · NATO",
           font=f(SANS_B, 10), fill=GREY)
    y0 = y + 12
    y1 = y0 + h
    d.rectangle([M, y0, M + mw, y1], fill=(235, 240, 246), outline=RULE)
    lon_lo, lon_hi, lat_lo, lat_hi = -180, 180, -56, 84
    ncols, nrows = 122, 48
    step_lon = (lon_hi - lon_lo) / ncols
    step_lat = (lat_hi - lat_lo) / nrows
    for r in range(nrows):
        lat = lat_hi - (r + 0.5) * step_lat
        for c in range(ncols):
            lon = lon_lo + (c + 0.5) * step_lon
            if _on_land(lon, lat):
                px = M + (lon - lon_lo) / (lon_hi - lon_lo) * mw
                py = y0 + (lat_hi - lat) / (lat_hi - lat_lo) * (y1 - y0)
                d.ellipse([px - 1.2, py - 1.2, px + 1.2, py + 1.2],
                          fill=(150, 162, 174))
    for num, lat, lon in PINS:
        px = M + (lon - lon_lo) / (lon_hi - lon_lo) * mw
        py = y0 + (lat_hi - lat) / (lat_hi - lat_lo) * (y1 - y0)
        if num in PIN_OFF:
            dx, dy = PIN_OFF[num]
            qx, qy = px + dx, py + dy
            d.line([px, py, qx, qy], fill=CRIMSON, width=1)
            px, py = qx, qy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=CRIMSON,
                  outline=(255, 255, 255), width=2)
        d.text((px - 2 if num < 10 else px - 4.5, py - 4.5),
               str(num), font=f(SANS_B, 8), fill=(255, 255, 255))
    d.rectangle([vx, y0, vx + vw, y1], fill=NAVY)
    fv = f(SANS, 11)
    for i, ln in enumerate(VERDICT):
        d.text((vx + 10, y0 + 2 + i * 11), ln, font=fv, fill=(255, 255, 255))
    return y1


def draw_list(d, y, h):
    d.text((M, y), "36 MORE STORIES", font=f(SANS_B, 11), fill=INK)
    y0 = y + 14
    cols, rows = 3, 12
    cw = (CW - 2 * 16) / cols
    fc = f(SANS_B, 10)
    ft = f(SANS, 10)
    bad = []
    for i, (num, region, field, city, headline) in enumerate(MORE):
        col, row = i % cols, i // cols
        x = M + col * (cw + 16)
        yy = y0 + row * 10
        ctext = f"{num:02d} · {city} "
        cw_city = d.textlength(ctext, font=fc)
        shown = trunc(d, headline, ft, cw - cw_city)
        if shown != headline:
            bad.append((num, headline, shown))
        d.text((x, yy), ctext, font=fc, fill=INK)
        d.text((x + cw_city, yy), shown, font=ft, fill=BODY)
    if bad:
        print("LIST TRUNCATES (fix the headlines):")
        for num, orig, shown in bad:
            print(f"  #{num}: {orig!r} -> {shown!r}")
    assert not bad, f"{len(bad)} list items truncate mid-word"
    return y0 + rows * 10


def draw_date_check(d, y, width):
    lines = []
    fb = f(SANS, 11)
    for prefix, text in (("LEFT OUT — FIRST REPORTED ON OTHER DAYS: ", LEFT_OUT),
                         ("NOT YET: ", NOT_YET),
                         ("NOTE: ", NOTE)):
        for ln in wrap(d, prefix + text, fb, width - 20):
            lines.append(ln)
    print(f"date check lines: {len(lines)}")
    assert len(lines) <= 5, f"date check wraps to {len(lines)} lines"
    h = 14 + 11 + 12 * len(lines) + 10
    d.rectangle([M, y, M + CW, y + h], fill=(254, 248, 236), outline=GOLD)
    d.text((M + 10, y + 6), "DATE CHECK", font=f(SANS_B, 11), fill=CRIMSON)
    yy = y + 20
    for i, ln in enumerate(lines):
        fill = CRIMSON if ln.startswith("LEFT OUT") else INK
        if ln.startswith("NOT YET"):
            fill = NAVY
        d.text((M + 10, yy), ln, font=fb, fill=fill)
        yy += 12
    return y + h


def draw_footer(d, y):
    d.text((M, y),
           "Sources: Reuters · AP · AFP · BBC · CNN · WSJ · UN News · Carbon Brief · Yonhap · USGS · ESA · CoinDesk · Le Monde",
           font=f(SANS, 9), fill=GREY)
    d.text((M, y + 12),
           "All 52 stories happened, or were first reported, on Fri 20 Nov 2026.",
           font=f(SANS, 9), fill=GREY)
    d.text((M, y + 24), LEGEND, font=f(SANS, 9), fill=GREY)
    return y + 33

# ---------------- build ----------------

def build():
    assert len(CARDS) == 16 and len(MORE) == 36
    assert sum(n for _, n in REGIONS) == 52 and sum(n for _, n in FIELDS) == 52
    assert [c[0] for c in CARDS] + [m[0] for m in MORE] == list(range(1, 53))
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 12
    y = draw_header(d, y)
    y += 2
    y = draw_strip(d, y, [(r.upper(), str(n)) for r, n in REGIONS])  # BY REGION
    y += 2
    y = draw_strip(d, y, [(fld.upper(), str(n)) for fld, n in FIELDS])  # BY FIELD
    y += 3
    y = draw_numbers(d, y)
    y += 2
    y = draw_timeline(d, y, UTC_TIMELINE)
    y += 2
    # cards: row 1 = 3 big; row 2 = 5 small; rows 3-4 = 4 small
    big_w = (CW - 2 * 6) // 3
    x = M
    for card in CARDS[:3]:
        draw_card(img, d, card, x, y, big_w, 140, True)
        x += big_w + 6
    y += 140 + 6
    row2_w = (CW - 4 * 6) // 5
    x = M
    for card in CARDS[3:8]:
        draw_card(img, d, card, x, y, row2_w, 108, False)
        x += row2_w + 6
    y += 108 + 6
    row_w = (CW - 3 * 6) // 4
    for row_cards in (CARDS[8:12], CARDS[12:16]):
        x = M
        for card in row_cards:
            draw_card(img, d, card, x, y, row_w, 108, False)
            x += row_w + 6
        y += 108 + 6
    y -= 6
    y += 3
    y = draw_map_verdict(d, y, 36)
    y += 3
    y = draw_list(d, y, 108)
    y += 2
    y = draw_date_check(d, y, CW)
    y += 1
    y = draw_footer(d, y)
    print(f"final y after footer: {y} (canvas {H})")
    assert y <= H, f"layout overflows: footer ends at {y}"
    return img


if __name__ == "__main__":
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
