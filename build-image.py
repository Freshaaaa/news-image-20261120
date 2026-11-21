#!/usr/bin/env python3
"""Draw the news-image-20261120 entry, v2 (top-3 redesign): one page summing
up the world news of Friday 20 November 2026, rendered with PIL so every
letter stays crisp at 1024x1024. No network, no randomness, no clock: the
same run always writes the same bytes.

v2 rebuilds the page the way the top entries do it: FEWER stories, MORE
depth. 25 stories total (3 big heroes + 8 cards + 14 in ALSO ON) instead of
52, a cream paper background, a huge serif masthead with a red sub-headline
naming the day's biggest stories, 6 stat chips, a THE DAY BY HOURS timeline,
3 hero cards with tall, detailed, colourful banner scenes, a dotted world
map with numbered pins, a THE VERDICT box, a DATE CHECK box for stories
deliberately left off, and a sources footer. Every story on the page
happened, or was first reported, on Friday 20 November 2026, verified
against Reuters, AP, AFP, BBC, CNN, WSJ, UN News, Carbon Brief, Yonhap,
USGS, ESA, CoinDesk and Le Monde.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 20
CW = W - 2 * M  # 984 content width

PAPER = (250, 246, 236)
INK = (18, 18, 22)
BODY = (58, 56, 50)
GREY = (110, 106, 96)
NAVY = (16, 28, 56)
NAVY_SOFT = (30, 48, 88)
CRIMSON = (166, 25, 46)
RED = (178, 34, 34)
GOLD = (198, 154, 60)
CARD = (255, 255, 255)
RULE = (196, 188, 172)
PALE = (226, 232, 240)
TEAL = (14, 120, 120)
GREEN = (16, 120, 70)
BLUE = (36, 86, 170)
ORANGE = (200, 110, 20)
AMBER = (198, 138, 0)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
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


def fit_lines(d, text, font, max_w, max_lines, what):
    """Wrap text and assert it fits in max_lines; returns the lines."""
    lines = wrap(d, text, font, max_w)
    assert len(lines) <= max_lines, f"{what} needs {len(lines)} lines, max {max_lines}: {text!r}"
    return lines


def text(d, x, y, s, font, fill, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def rrect(d, box, fill=None, outline=None, width=1, radius=4):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def hline(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def vgrad(d, box, top, bottom):
    """Vertical gradient fill inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def star(d, cx, cy, r, fill):
    """Four-point sparkle."""
    d.polygon([(cx, cy - r), (cx + r * 0.28, cy - r * 0.28),
               (cx + r, cy), (cx + r * 0.28, cy + r * 0.28),
               (cx, cy + r), (cx - r * 0.28, cy + r * 0.28),
               (cx - r, cy), (cx - r * 0.28, cy - r * 0.28)], fill=fill)


def tag(d, x, y, label, bg=GREEN, fg=(255, 255, 255)):
    """Small pill tag (REPORTED / CLAIM / FORECAST). Returns its width."""
    font = f(SANS_B, 10)
    w = int(d.textlength(label, font=font)) + 12
    rrect(d, [x, y, x + w, y + 15], fill=bg, radius=3)
    d.text((x + 6, y + 2), label, font=font, fill=fg)
    return w

# ---------------------------------------------------------------- banners
def banner_poland(d, x0, y0, x1, y1):
    """Polish field at dusk: orange horizon, silhouetted trees, a road with
    flashing red/blue emergency lights and a rising smoke plume."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, [x0, y0, x1, y0 + int(h * 0.62)], (44, 38, 78), (214, 122, 52))
    # sun low on the horizon
    d.ellipse([x0 + w - 52, y0 + int(h * 0.30), x0 + w - 20, y0 + int(h * 0.30) + 32],
              fill=(255, 196, 90))
    # silhouetted tree line
    hy = y0 + int(h * 0.62)
    for tx, th in [(8, 26), (34, 18), (58, 30), (88, 20), (120, 26), (150, 18),
                   (180, 28), (210, 20), (240, 26), (268, 18), (296, 24)]:
        d.polygon([(x0 + tx, hy), (x0 + tx + 9, hy - th), (x0 + tx + 18, hy)],
                  fill=(28, 24, 40))
    # field
    d.rectangle([x0, hy, x1, y1], fill=(52, 44, 30))
    # road diagonal
    d.polygon([(x0 + int(w * 0.42), y1), (x0 + int(w * 0.58), y1),
               (x0 + int(w * 0.52), hy), (x0 + int(w * 0.46), hy)], fill=(38, 36, 40))
    d.line([(x0 + int(w * 0.50), y1), (x0 + int(w * 0.49), hy)],
           fill=(220, 200, 120), width=2)
    # smoke plume (small, soft grey puffs)
    for i, (sx, sy, sr) in enumerate([(0.30, 0.34, 9), (0.33, 0.26, 11),
                                      (0.37, 0.19, 8), (0.40, 0.13, 6)]):
        d.ellipse([x0 + int(w * sx) - sr, y0 + int(h * sy) - sr,
                   x0 + int(w * sx) + sr, y0 + int(h * sy) + sr],
                  fill=(130, 126, 128) if i % 2 == 0 else (148, 144, 146))
    # emergency lights: red and blue glows with halos
    for cx, cy, col, halo in [(0.60, 0.78, (255, 60, 50), (255, 120, 110)),
                              (0.72, 0.80, (70, 130, 255), (130, 170, 255))]:
        px, py = x0 + int(w * cx), y0 + int(h * cy)
        d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=halo)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))


def banner_kyiv(d, x0, y0, x1, y1):
    """River bridge at night: dark sky, city lights on both banks, an arched
    bridge over a dark river, smoke rising with an orange glow at its base."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, [x0, y0, x1, y0 + int(h * 0.55)], (10, 14, 34), (52, 44, 78))
    # stars at fixed positions
    for sx, sy in [(0.06, 0.10), (0.16, 0.22), (0.28, 0.08), (0.44, 0.16),
                   (0.58, 0.06), (0.72, 0.18), (0.86, 0.08), (0.94, 0.24),
                   (0.36, 0.28), (0.66, 0.30)]:
        star(d, x0 + int(w * sx), y0 + int(h * sy), 3, (255, 244, 200))
    # moon
    d.ellipse([x0 + w - 46, y0 + 10, x0 + w - 22, y0 + 34], fill=(240, 232, 200))
    # city skylines on both banks
    hy = y0 + int(h * 0.55)
    for bx, bw, bh in [(0, 26, 34), (28, 18, 46), (48, 30, 28), (80, 20, 40),
                       (w - 100, 24, 38), (w - 74, 18, 50), (w - 54, 28, 30),
                       (w - 24, 22, 42)]:
        d.rectangle([x0 + bx, hy - bh, x0 + bx + bw, hy], fill=(16, 16, 28))
        for wy in range(hy - bh + 6, hy - 4, 10):
            for wx in range(x0 + bx + 4, x0 + bx + bw - 4, 9):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 206, 110))
    # river
    d.rectangle([x0, hy, x1, y1], fill=(22, 34, 62))
    d.line([(x0, hy + 12), (x1, hy + 12)], fill=(90, 120, 170), width=1)
    d.line([(x0 + 20, hy + 26), (x1 - 30, hy + 26)], fill=(70, 100, 150), width=1)
    # arched bridge
    bx0, bx1 = x0 + int(w * 0.30), x0 + int(w * 0.72)
    d.arc([bx0, hy - 34, bx1, hy + 26], start=180, end=360, fill=(200, 190, 160), width=4)
    d.line([(bx0, hy - 4), (bx1, hy - 4)], fill=(200, 190, 160), width=4)
    for i in range(9):
        cx = bx0 + int((bx1 - bx0) * i / 8)
        top = hy - 4 - int(30 * math.sin(math.pi * i / 8))
        d.line([(cx, top), (cx, hy - 4)], fill=(180, 170, 140), width=2)
    # bridge lights
    for i in range(9):
        cx = bx0 + int((bx1 - bx0) * i / 8)
        d.ellipse([cx - 2, hy - 8, cx + 2, hy - 4], fill=(255, 220, 130))
    # smoke plume with orange glow at the base (small, soft puffs)
    sx = x0 + int(w * 0.52)
    d.ellipse([sx - 11, hy - 18, sx + 11, hy + 2], fill=(255, 140, 50))
    for i, (ox, oy, sr) in enumerate([(-3, -26, 8), (3, -38, 10), (-2, -50, 7), (4, -60, 5)]):
        d.ellipse([sx + ox - sr, hy + oy - sr, sx + ox + sr, hy + oy + sr],
                  fill=(118, 114, 120) if i % 2 == 0 else (138, 134, 140))


def banner_hague(d, x0, y0, x1, y1):
    """Courthouse with columns and pediment, scales of justice in front, and
    a big red 1ST badge top-right."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, [x0, y0, x1, y1], (226, 232, 240), (196, 204, 216))
    # courthouse
    cx0, cx1 = x0 + int(w * 0.12), x0 + int(w * 0.88)
    base = y0 + int(h * 0.82)
    d.polygon([(cx0, y0 + int(h * 0.30)), (x0 + w // 2, y0 + int(h * 0.08)),
               (cx1, y0 + int(h * 0.30))], fill=(240, 238, 230))
    d.rectangle([cx0, y0 + int(h * 0.30), cx1, y0 + int(h * 0.38)], fill=(228, 224, 212))
    for i in range(5):
        px = cx0 + 14 + i * int((cx1 - cx0 - 28) / 4)
        d.rectangle([px, y0 + int(h * 0.38), px + 12, base], fill=(248, 246, 238))
        d.rectangle([px - 2, y0 + int(h * 0.38) - 4, px + 14, y0 + int(h * 0.38)], fill=(220, 216, 204))
    d.rectangle([cx0 - 8, base, cx1 + 8, base + 8], fill=(210, 206, 194))
    d.rectangle([cx0 - 14, base + 8, cx1 + 14, y1], fill=(168, 162, 150))
    # scales of justice (gold) in front centre-left
    sx, sy = x0 + int(w * 0.34), y0 + int(h * 0.62)
    d.line([(sx, sy - 26), (sx, sy + 12)], fill=(178, 134, 40), width=3)
    d.line([(sx - 26, sy - 22), (sx + 26, sy - 22)], fill=(178, 134, 40), width=3)
    d.line([(sx - 26, sy - 22), (sx - 26, sy - 8)], fill=(178, 134, 40), width=2)
    d.line([(sx + 26, sy - 22), (sx + 26, sy - 8)], fill=(178, 134, 40), width=2)
    d.polygon([(sx - 36, sy - 8), (sx - 16, sy - 8), (sx - 26, sy + 4)], fill=(198, 154, 60))
    d.polygon([(sx + 16, sy - 8), (sx + 36, sy - 8), (sx + 26, sy + 4)], fill=(198, 154, 60))
    d.ellipse([sx - 5, sy - 32, sx + 5, sy - 22], fill=(198, 154, 60))
    # big red 1ST badge
    bx, by, br = x0 + w - 34, y0 + 30, 26
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=CRIMSON)
    d.ellipse([bx - br, by - br, bx + br, by + br], outline=(255, 255, 255), width=2)
    d.text((bx, by), "1ST", font=f(SANS_B, 15), fill=(255, 255, 255), anchor="mm")


def banner_selloff(d, x0, y0, x1, y1):
    """Dark chart, red candles and a falling red line."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(14, 20, 34))
    for gy in range(y0 + 12, y1 - 6, 14):
        d.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(38, 48, 68), width=1)
    pts = [(0.06, 0.30), (0.20, 0.38), (0.34, 0.34), (0.48, 0.52),
           (0.62, 0.60), (0.76, 0.72), (0.90, 0.82)]
    for i, (fx, fy) in enumerate(pts):
        cx, cy = x0 + int(w * fx), y0 + int(h * fy)
        d.rectangle([cx - 5, cy - 8, cx + 5, cy + 8], fill=(214, 48, 48))
        d.line([(cx, cy - 13), (cx, cy + 13)], fill=(214, 48, 48), width=2)
    d.line([(x0 + int(w * fx), y0 + int(h * fy)) for fx, fy in pts],
           fill=(255, 90, 80), width=3)


def banner_ant(d, x0, y0, x1, y1):
    """Dark chart, green rising candles, ANT $83 in gold."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 26, 22))
    for gy in range(y0 + 12, y1 - 6, 14):
        d.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(34, 56, 44), width=1)
    pts = [(0.08, 0.78), (0.22, 0.70), (0.36, 0.74), (0.50, 0.58),
           (0.64, 0.46), (0.78, 0.34), (0.90, 0.22)]
    for i, (fx, fy) in enumerate(pts):
        cx, cy = x0 + int(w * fx), y0 + int(h * fy)
        d.rectangle([cx - 5, cy - 8, cx + 5, cy + 8], fill=(34, 180, 100))
        d.line([(cx, cy - 13), (cx, cy + 13)], fill=(34, 180, 100), width=2)
    d.line([(x0 + int(w * fx), y0 + int(h * fy)) for fx, fy in pts],
           fill=(120, 230, 160), width=3)
    d.text((x0 + 8, y0 + 5), "ANT", font=f(SANS_B, 16), fill=(255, 255, 255))
    d.text((x1 - 8, y0 + 5), "$83", font=f(SANS_B, 14), fill=(255, 206, 90), anchor="ra")


def banner_cop31(d, x0, y0, x1, y1):
    """Globe and thermometer on pale green, with a rotated red
    FOSSIL FUELS CUT stamp."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(222, 236, 224))
    # globe
    gx, gy, gr = x0 + int(w * 0.26), y0 + int(h * 0.52), 24
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(56, 130, 200))
    d.ellipse([gx - 14, gy - 16, gx + 2, gy - 2], fill=(90, 170, 90))
    d.ellipse([gx - 4, gy + 6, gx + 16, gy + 18], fill=(90, 170, 90))
    d.ellipse([gx + 8, gy - 18, gx + 18, gy - 6], fill=(120, 190, 110))
    # thermometer
    tx = x0 + int(w * 0.62)
    d.rounded_rectangle([tx - 5, y0 + 10, tx + 5, y0 + h - 18], radius=5,
                        fill=(255, 255, 255), outline=(150, 150, 150), width=1)
    d.ellipse([tx - 10, y0 + h - 26, tx + 10, y0 + h - 6], fill=RED)
    d.rectangle([tx - 2, y0 + 16, tx + 2, y0 + h - 16], fill=RED)
    d.text((tx + 14, y0 + 8), "°C", font=f(SANS_B, 11), fill=RED)
    # rotated stamp, kept inside the banner
    stamp = Image.new("RGBA", (120, 20), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([2, 2, 117, 17], outline=RED, width=2)
    sd.text((60, 10), "FOSSIL FUELS CUT", font=f(SANS_B, 9), fill=RED, anchor="mm")
    stamp = stamp.rotate(8, expand=True, resample=Image.BICUBIC)
    d._image.paste(stamp, (x0 + int(w * 0.30), y0 + 6), stamp)


def banner_hormuz(d, x0, y0, x1, y1):
    """Burning tanker at sea: dark water, orange flames, black smoke."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, [x0, y0, x1, y0 + int(h * 0.55)], (30, 34, 52), (90, 60, 44))
    d.rectangle([x0, y0 + int(h * 0.55), x1, y1], fill=(16, 28, 48))
    # tanker hull
    hy = y0 + int(h * 0.62)
    d.polygon([(x0 + 18, hy), (x0 + w - 18, hy), (x0 + w - 34, hy + 18),
               (x0 + 34, hy + 18)], fill=(40, 40, 46))
    d.rectangle([x0 + int(w * 0.55), hy - 22, x0 + int(w * 0.68), hy], fill=(52, 52, 58))
    # flames
    for fx, fh, fw in [(0.30, 26, 12), (0.40, 34, 14), (0.50, 22, 10), (0.62, 30, 12)]:
        px = x0 + int(w * fx)
        d.polygon([(px - fw, hy), (px - fw // 2, hy - fh), (px, hy - fh - 8),
                   (px + fw // 2, hy - fh), (px + fw, hy)], fill=(255, 140, 40))
        d.polygon([(px - fw // 2, hy), (px - 2, hy - fh + 8), (px + fw // 2, hy)],
                  fill=(255, 210, 90))
    # smoke
    for i, (sx, sy, sr) in enumerate([(0.40, 0.28, 12), (0.46, 0.18, 15), (0.52, 0.10, 11)]):
        d.ellipse([x0 + int(w * sx) - sr, y0 + int(h * sy) - sr,
                   x0 + int(w * sx) + sr, y0 + int(h * sy) + sr],
                  fill=(70, 66, 70) if i % 2 == 0 else (92, 88, 92))
    # wave lines
    d.line([(x0 + 10, y1 - 12), (x1 - 10, y1 - 12)], fill=(70, 100, 140), width=2)


def banner_ukeu(d, x0, y0, x1, y1):
    """EU flag (blue, circle of yellow stars) beside the Union Jack."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(238, 238, 232))
    fw, fh = int(w * 0.44), int(h * 0.62)
    fy = y0 + (h - fh) // 2
    # EU flag
    ex = x0 + 8
    d.rectangle([ex, fy, ex + fw, fy + fh], fill=(0, 51, 153))
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx = ex + fw // 2 + int(fw * 0.30 * math.cos(a))
        sy = fy + fh // 2 + int(fh * 0.30 * math.sin(a))
        star(d, sx, sy, 3, (255, 204, 0))
    # Union Jack (simplified)
    ux = x1 - 8 - fw
    d.rectangle([ux, fy, ux + fw, fy + fh], fill=(1, 33, 105))
    d.line([(ux, fy), (ux + fw, fy + fh)], fill=(255, 255, 255), width=6)
    d.line([(ux + fw, fy), (ux, fy + fh)], fill=(255, 255, 255), width=6)
    d.line([(ux, fy), (ux + fw, fy + fh)], fill=(200, 16, 46), width=2)
    d.line([(ux + fw, fy), (ux, fy + fh)], fill=(200, 16, 46), width=2)
    d.rectangle([ux + fw // 2 - 4, fy, ux + fw // 2 + 4, fy + fh], fill=(255, 255, 255))
    d.rectangle([ux, fy + fh // 2 - 4, ux + fw, fy + fh // 2 + 4], fill=(255, 255, 255))
    d.rectangle([ux + fw // 2 - 2, fy, ux + fw // 2 + 2, fy + fh], fill=(200, 16, 46))
    d.rectangle([ux, fy + fh // 2 - 2, ux + fw, fy + fh // 2 + 2], fill=(200, 16, 46))


def banner_peru(d, x0, y0, x1, y1):
    """Cracked dry ground with a red seismograph zigzag."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(214, 196, 160))
    # ground crack
    d.line([(x0 + 8, y1 - 8), (x0 + int(w * 0.30), y0 + int(h * 0.55)),
            (x0 + int(w * 0.45), y1 - 14), (x0 + int(w * 0.70), y0 + int(h * 0.45)),
            (x1 - 10, y1 - 6)], fill=(90, 66, 40), width=3)
    # seismograph paper strip
    d.rectangle([x0 + 10, y0 + 8, x1 - 10, y0 + int(h * 0.42)], fill=(255, 255, 255),
                outline=(160, 150, 130), width=1)
    pts = []
    xs = [0.05, 0.15, 0.25, 0.32, 0.40, 0.48, 0.55, 0.62, 0.70, 0.78, 0.86, 0.95]
    ys = [0.22, 0.22, 0.22, 0.10, 0.36, 0.06, 0.38, 0.22, 0.22, 0.22, 0.22, 0.22]
    for fx, fy in zip(xs, ys):
        pts.append((x0 + 10 + int((w - 20) * fx), y0 + 8 + int((h * 0.42 - 8) * fy)))
    d.line(pts, fill=RED, width=2)
    d.text((x0 + 12, y0 + int(h * 0.42) + 4), "6.7", font=f(SANS_B, 13), fill=RED)


def banner_estonia(d, x0, y0, x1, y1):
    """Red-white striped barrier across a road, CLOSED sign."""
    w, h = x1 - x0, y1 - y0
    vgrad(d, [x0, y0, x1, y1], (200, 208, 216), (150, 158, 168))
    # road
    d.rectangle([x0, y0 + int(h * 0.62), x1, y1], fill=(70, 70, 76))
    d.line([(x0, y0 + int(h * 0.80)), (x1, y0 + int(h * 0.80))],
           fill=(230, 220, 100), width=2)
    # barrier posts
    d.rectangle([x0 + 14, y0 + int(h * 0.30), x0 + 22, y0 + int(h * 0.62)], fill=(60, 60, 66))
    d.rectangle([x1 - 22, y0 + int(h * 0.30), x1 - 14, y0 + int(h * 0.62)], fill=(60, 60, 66))
    # striped barrier bar
    by0, by1 = y0 + int(h * 0.30), y0 + int(h * 0.46)
    for i in range(8):
        sx = x0 + 22 + i * (w - 44) // 8
        ex = x0 + 22 + (i + 1) * (w - 44) // 8
        d.rectangle([sx, by0, ex, by1], fill=(255, 255, 255) if i % 2 == 0 else RED)
    d.rectangle([x0 + 22, by0, x1 - 22, by1], outline=(120, 120, 120), width=1)
    # CLOSED sign
    sw = 74
    sx0 = x0 + (w - sw) // 2
    rrect(d, [sx0, y0 + int(h * 0.52), sx0 + sw, y0 + int(h * 0.52) + 18],
          fill=(255, 255, 255), outline=RED, width=2, radius=3)
    d.text((sx0 + sw // 2, y0 + int(h * 0.52) + 9), "CLOSED", font=f(SANS_B, 11),
           fill=RED, anchor="mm")


def banner_mercury(d, x0, y0, x1, y1):
    """Dark space, cratered orange Mercury, a small spacecraft with panels."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(10, 12, 26))
    for sx, sy in [(0.08, 0.16), (0.20, 0.08), (0.34, 0.22), (0.48, 0.10),
                   (0.62, 0.20), (0.76, 0.08), (0.88, 0.18), (0.14, 0.34),
                   (0.94, 0.36), (0.56, 0.32)]:
        star(d, x0 + int(w * sx), y0 + int(h * sy), 2, (255, 255, 255))
    # Mercury
    mx, my, mr = x0 + int(w * 0.68), y0 + int(h * 0.58), 26
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(206, 132, 60))
    for cx, cy, cr in [(-12, -8, 6), (6, 4, 8), (-4, 12, 5), (12, -12, 4), (0, -2, 3)]:
        d.ellipse([mx + cx - cr, my + cy - cr, mx + cx + cr, my + cy + cr],
                  fill=(178, 108, 44))
    # spacecraft
    sx, sy = x0 + int(w * 0.24), y0 + int(h * 0.34)
    d.rectangle([sx - 16, sy - 4, sx + 16, sy + 4], fill=(120, 140, 180))
    d.rectangle([sx - 8, sy - 12, sx + 8, sy + 12], fill=(200, 210, 225))
    d.polygon([(sx + 8, sy - 6), (sx + 20, sy), (sx + 8, sy + 6)], fill=(220, 200, 90))
    d.line([(sx - 30, sy), (sx - 16, sy)], fill=(255, 220, 130), width=2)
    d.text((x0 + 8, y0 + 6), "BEPICOLOMBO", font=f(SANS_B, 10), fill=(255, 255, 255))


BANNERS = {
    "poland": banner_poland, "kyiv": banner_kyiv, "hague": banner_hague,
    "selloff": banner_selloff, "ant": banner_ant, "cop31": banner_cop31,
    "hormuz": banner_hormuz, "ukeu": banner_ukeu, "peru": banner_peru,
    "estonia": banner_estonia, "mercury": banner_mercury,
}

# ---------------------------------------------------------------- data
HEROES = [
    dict(num="1", place="POLAND", field="EUROPE", banner="poland",
         head="Russian missiles land in Poland",
         summ="Two missiles and a suspected drone came down; Poland calls it a "
              "deliberate provocation; NATO calls it a grave violation.",
         src="REUTERS"),
    dict(num="2", place="KYIV", field="EUROPE", banner="kyiv",
         head="Russian strikes hit three Kyiv bridges",
         summ="3 killed, ~15 injured; follows Ukraine hitting the Crimea "
              "Bridge a third time this week.",
         src="REUTERS"),
    dict(num="3", place="THE HAGUE", field="WORLD", banner="hague",
         head="World Court: Myanmar committed genocide",
         summ="First state held responsible for genocide against the Rohingya; "
              "reparations ordered.",
         src="UN NEWS"),
]

SMALL = [
    dict(num="4", place="WORLD", field="SELL-OFF", banner="selloff",
         head="AI sell-off drags world markets down",
         summ="S&P 500 -3.7% into correction; Nikkei -5.06% on AI cost worries.",
         src="WSJ"),
    dict(num="5", place="NEW YORK", field="IPO", banner="ant",
         head="Anthropic debuts on Nasdaq as ANT",
         summ="$81.3bn raised, largest IPO on record; priced $83, closed $97.17, +17%.",
         src="WSJ"),
    dict(num="6", place="ANTALYA", field="COP31", banner="cop31",
         head="COP31 draft drops fossil fuels",
         summ="Second draft omits fossil fuels; talks run past deadline; activists protest.",
         src="CARBON BRIEF"),
    dict(num="7", place="HORMUZ", field="MIDDLE EAST", banner="hormuz",
         head="Tankers keep catching fire in Hormuz",
         summ="US blockade; Iran mounts attacks; IEA: largest energy supply shock on record.",
         src="REUTERS"),
    dict(num="8", place="BRUSSELS", field="RESET", banner="ukeu",
         head="UK and EU sign landmark reset deal",
         summ="Food trade, carbon markets, youth mobility (18-31, 100,000 places a year).",
         src="BBC"),
    dict(num="9", place="PERU", field="QUAKE", banner="peru",
         head="Magnitude 6.7 earthquake hits central Peru",
         summ="Cerro de Pasco; one injured, buildings and roads damaged.",
         src="USGS"),
    dict(num="10", place="ESTONIA", field="BORDER", banner="estonia",
         head="Estonia to close Russia border crossings",
         summ="After sabotage attack; from Dec 1, at least six months.",
         src="REUTERS"),
    dict(num="11", place="MERCURY", field="SPACE", banner="mercury",
         head="BepiColombo reaches Mercury",
         summ="ESA/JAXA spacecraft arrives after an eight-year journey.",
         src="ESA"),
]

CHIPS = [
    ("$81.3bn", "raised by Anthropic, the largest IPO on record"),
    ("-3.7%", "S&P 500 falls into correction"),
    ("6.7", "Peru earthquake magnitude"),
    ("$7.25bn", "Bayer Roundup settlement"),
    ("100,000", "UK-EU youth places a year"),
    ("$61,700", "Bitcoin low since July"),
]

TIMELINE = [
    ("01:40", "Peru quake 6.7"),
    ("06:00", "Bitcoin $61,700"),
    ("09:00", "ICJ genocide"),
    ("12:30", "COP31 draft"),
    ("14:30", "ANT debuts"),
    ("16:10", "UK-EU deal"),
    ("19:20", "Poland missiles"),
]

ALSO_ON = [
    ("LOS ANGELES", "Jury convicts man who started Palisades Fire."),
    ("MISSOURI", "Judge approves $7.25bn Roundup settlement."),
    ("RIYADH", "Houthi missile hits tallest tower."),
    ("SHENZHEN", "Trump, Xi and Putin agree nuclear-risk talks."),
    ("MARKETS", "Bitcoin drops near $61,700, lowest since July."),
    ("WASHINGTON", "Senate blocks Iran war-powers vote, 51-48."),
    ("WASHINGTON", "Trump: no rush on next Iran step."),
    ("DHAKA", "Violence ahead of Hasina's return."),
    ("BAGHDAD", "Iraqi forces enter Jurf al-Nasr."),
    ("NEW YORK", "Nikhil Gupta sentenced to 19+ years."),
    ("TOKYO", "Japan core inflation hits year high."),
    ("CALIFORNIA", "State subpoenas Nvidia over China risks."),
    ("BEIJING", "TSMC and Samsung pause chip sales to China."),
    ("OTTAWA", "Canada budget passes House, 162-151."),
]

# lon/lat for the 11 card pins on the map
PINS = [
    (19, 52), (30, 50), (4, 52), (-74, 41), (-122, 37), (30, 37),
    (56, 26), (4, 51), (-76, -10), (25, 59), (8, 50),
]

# ---------------------------------------------------------------- layout
def draw_masthead(d, y):
    """Top line, huge serif date, date box, red sub-headline."""
    text(d, M, y, "THE WORLD IN ONE PICTURE", f(SANS_B, 12), CRIMSON)
    text(d, W - M, y, "25 STORIES  ·  EVERY ONE FROM FRIDAY 20 NOVEMBER",
         f(SANS_B, 12), GREY, anchor="ra")
    y += 22
    text(d, M, y, "Friday 20 November 2026", f(SERIF, 58), INK)
    # date box, right
    bx0, bx1 = W - M - 96, W - M
    by0, by1 = y + 2, y + 58
    d.rectangle([bx0, by0, bx1, by1], outline=INK, width=2)
    text(d, (bx0 + bx1) // 2, by0 + 4, "NOVEMBER 2026", f(SANS_B, 10), INK, anchor="ma")
    text(d, (bx0 + bx1) // 2, by0 + 16, "20", f(SERIF, 26), INK, anchor="ma")
    text(d, (bx0 + bx1) // 2, by1 - 14, "FRIDAY", f(SANS_B, 10), INK, anchor="ma")
    y += 60
    text(d, M, y, "Russian missiles land in Poland  ·  Kyiv bridges hit  ·  "
         "World Court finds genocide  ·  Anthropic's record IPO",
         f(SERIF_I, 15), CRIMSON)
    y += 26
    hline(d, M, W - M, y, fill=INK, width=2)
    return y + 8


def draw_chips(d, y):
    cw = CW // 6
    for i, (num, label) in enumerate(CHIPS):
        x0 = M + i * cw
        text(d, x0 + 4, y, num, f(SANS_B, 24), CRIMSON)
        lines = fit_lines(d, label, f(SANS, 10), cw - 10, 2, f"chip {num}")
        yy = y + 28
        for ln in lines:
            text(d, x0 + 4, yy, ln, f(SANS, 10), BODY)
            yy += 12
        if i < 5:
            d.line([(x0 + cw - 2, y + 2), (x0 + cw - 2, y + 48)], fill=RULE, width=1)
    return y + 52


def draw_timeline(d, y):
    text(d, M, y, "THE DAY BY HOURS", f(SANS_B, 11), INK)
    y += 16
    x0, x1 = M + 6, W - M - 6
    hline(d, x0, x1, y + 4, fill=GREY, width=1)
    n = len(TIMELINE)
    for i, (tm, label) in enumerate(TIMELINE):
        cx = x0 + int((x1 - x0) * i / (n - 1))
        d.ellipse([cx - 4, y, cx + 4, y + 8], fill=CRIMSON)
        d.ellipse([cx - 4, y, cx + 4, y + 8], outline=(255, 255, 255), width=1)
        # first label left-anchored, last right-anchored, middles centred
        anchor = "ma"
        if i == 0:
            anchor = "la"
            cx = max(cx, x0)
        if i == n - 1:
            anchor = "ra"
            cx = min(cx, x1)
        text(d, cx, y + 10, tm, f(SANS_B, 10), INK, anchor=anchor)
        text(d, cx, y + 22, label, f(SANS, 9), BODY, anchor=anchor)
    return y + 34


def draw_hero(d, x0, y0, w, card):
    """One big hero card: tall banner, kicker, headline, summary, source."""
    h = 236
    x1 = x0 + w
    rrect(d, [x0, y0, x1, y0 + h], fill=CARD, outline=RULE, width=1, radius=2)
    bh = 110
    BANNERS[card["banner"]](d, x0 + 1, y0 + 1, x1 - 1, y0 + bh)
    d.rectangle([x0 + 1, y0 + bh, x1 - 1, y0 + bh + 2], fill=RULE)
    tag(d, x1 - 78, y0 + bh - 22, "REPORTED", bg=GREEN)
    yy = y0 + bh + 8
    text(d, x0 + 10, yy, f"{card['num']}  ·  {card['place']}  ·  {card['field']}",
         f(SANS_B, 11), CRIMSON)
    text(d, x1 - 10, yy, card["src"], f(SANS_B, 10), GREY, anchor="ra")
    yy += 16
    lines = fit_lines(d, card["head"], f(SERIF, 21), w - 20, 2, f"hero {card['num']}")
    for ln in lines:
        text(d, x0 + 10, yy, ln, f(SERIF, 21), INK)
        yy += 24
    yy += 2
    lines = fit_lines(d, card["summ"], f(SANS, 12), w - 20, 3, f"hero summ {card['num']}")
    for ln in lines:
        text(d, x0 + 10, yy, ln, f(SANS, 12), BODY)
        yy += 15
    return h


def draw_small(d, x0, y0, w, card):
    """One small card: short banner, kicker, headline, summary, source."""
    h = 128
    x1 = x0 + w
    rrect(d, [x0, y0, x1, y0 + h], fill=CARD, outline=RULE, width=1, radius=2)
    bh = 52
    BANNERS[card["banner"]](d, x0 + 1, y0 + 1, x1 - 1, y0 + bh)
    tag(d, x1 - 78, y0 + bh - 20, "REPORTED", bg=GREEN)
    yy = y0 + bh + 6
    text(d, x0 + 8, yy, f"{card['num']}  ·  {card['place']}  ·  {card['field']}",
         f(SANS_B, 9), CRIMSON)
    text(d, x1 - 8, yy, card["src"], f(SANS_B, 8), GREY, anchor="ra")
    yy += 13
    lines = fit_lines(d, card["head"], f(SERIF, 14), w - 16, 2, f"small {card['num']}")
    for ln in lines:
        text(d, x0 + 8, yy, ln, f(SERIF, 14), INK)
        yy += 17
    lines = fit_lines(d, card["summ"], f(SANS, 10), w - 16, 2, f"small summ {card['num']}")
    for ln in lines:
        text(d, x0 + 8, yy, ln, f(SANS, 10), BODY)
        yy += 12
    return h

# ---------------------------------------------------------------- bottom
CONTINENTS = [  # (lon, lat, rlon, rlat) ellipses approximating land
    (-100, 45, 38, 20), (-42, 72, 12, 7), (-60, -15, 16, 24),
    (15, 52, 16, 9), (20, 2, 20, 26), (90, 50, 48, 17),
    (108, -2, 14, 8), (134, -25, 14, 9),
]


def _lonlat_to_xy(mx0, my0, mw, mh, lon, lat):
    return (mx0 + (lon + 180) / 360.0 * mw,
            my0 + (75 - lat) / 130.0 * mh)


def draw_map(d, x0, y0, w, h):
    """Dotted world map (grid-sampled continent ellipses) + numbered pins."""
    x1, y1 = x0 + w, y0 + h
    d.rectangle([x0, y0, x1, y1], fill=(16, 28, 56))
    step = 7
    gx = x0 + 4
    while gx < x1 - 4:
        gy = y0 + 4
        while gy < y1 - 4:
            lon = (gx - x0) / w * 360.0 - 180
            lat = 75 - (gy - y0) / h * 130.0
            for clon, clat, rlon, rlat in CONTINENTS:
                if ((lon - clon) / rlon) ** 2 + ((lat - clat) / rlat) ** 2 <= 1:
                    d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(150, 160, 180))
                    break
            gy += step
        gx += step
    for i, (lon, lat) in enumerate(PINS, start=1):
        px, py = _lonlat_to_xy(x0, y0, w, h, lon, lat)
        px, py = int(px), int(py)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=CRIMSON)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], outline=(255, 255, 255), width=1)
        d.text((px, py), str(i), font=f(SANS_B, 8), fill=(255, 255, 255), anchor="mm")
    return h


def draw_also_on(d, x0, y0, w, h):
    text(d, x0, y0, "ALSO ON FRIDAY 20 NOVEMBER", f(SANS_B, 11), INK)
    y = y0 + 16
    col_w = (w - 14) // 2
    half = (len(ALSO_ON) + 1) // 2
    for col in range(2):
        cx = x0 + col * (col_w + 14)
        yy = y
        for city, story in ALSO_ON[col * half:(col + 1) * half]:
            full = f"{city} — {story}"
            lines = fit_lines(d, full, f(SANS, 9), col_w, 2, f"also-on {city}")
            for ln in lines:
                # bold the city part on the first line
                if ln == lines[0]:
                    text(d, cx, yy, city, f(SANS_B, 9), INK)
                    rest = ln[len(city):]
                    text(d, cx + d.textlength(city, font=f(SANS_B, 9)), yy,
                         rest, f(SANS, 9), BODY)
                else:
                    text(d, cx, yy, ln, f(SANS, 9), BODY)
                yy += 11
            yy += 2
    return h


def draw_verdict(d, x0, y0, w, h):
    x1 = x0 + w
    d.rectangle([x0, y0, x1, y0 + h], fill=NAVY)
    text(d, x0 + 12, y0 + 10, "THE VERDICT  —  POLAND  ·  NATO", f(SANS_B, 11),
         (255, 255, 255))
    yy = y0 + 30
    lines = fit_lines(d, "Two missiles and a drone land in Poland. Warsaw calls it a "
                      "deliberate provocation. NATO calls it a grave violation.",
                      f(SANS, 12), w - 24, 4, "verdict")
    for ln in lines:
        text(d, x0 + 12, yy, ln, f(SANS, 12), (235, 238, 245))
        yy += 16
    yy += 6
    hline(d, x0 + 12, x1 - 12, yy, fill=(90, 110, 150), width=1)
    yy += 8
    text(d, x0 + 12, yy, "HOW SURE ARE WE?", f(SANS_B, 10), (255, 206, 90))
    yy += 14
    for label, desc in [("REPORTED", "confirmed by named sources"),
                        ("CLAIM", "one side says, unverified"),
                        ("FORECAST", "poll, draft or schedule")]:
        text(d, x0 + 12, yy, label, f(SANS_B, 9), (255, 255, 255))
        text(d, x0 + 92, yy, desc, f(SANS, 9), (200, 208, 220))
        yy += 13
    return h


def draw_date_check(d, y):
    h = 44
    rrect(d, [M, y, W - M, y + h], outline=CRIMSON, width=2, radius=2)
    text(d, M + 10, y + 6, "DATE CHECK", f(SANS_B, 11), CRIMSON)
    msg = ("In the headlines today, but NOT Friday's news, so left off this page: "
           "Crimea Bridge, second strike, Wed 18 Nov  ·  Anthropic IPO priced $83, "
           "Thu 19 Nov  ·  Hormuz tanker fires, an IRGC claim from 4 Nov  ·  "
           "BepiColombo launched, Oct 2018.")
    lines = fit_lines(d, msg, f(SANS, 11), CW - 120, 2, "date check")
    yy = y + 6
    for ln in lines:
        text(d, M + 108, yy, ln, f(SANS, 11), BODY)
        yy += 14
    return y + h


def draw_footer(d, y):
    msg = ("Every story here happened, or was first reported, on Friday 20 November "
           "2026. Sources: Reuters · AP · AFP · BBC · CNN · WSJ · UN News · Carbon "
           "Brief · Yonhap · USGS · ESA · CoinDesk · Le Monde.")
    lines = fit_lines(d, msg, f(SANS, 9), CW, 1, "footer")
    text(d, M, y, lines[0], f(SANS, 9), GREY)
    return y + 14


# ---------------------------------------------------------------- main
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 6
    y = draw_masthead(d, y)
    y = draw_chips(d, y)
    y = draw_timeline(d, y)
    y += 6
    # 3 hero cards
    gap = 12
    hw = (CW - 2 * gap) // 3
    for i, card in enumerate(HEROES):
        draw_hero(d, M + i * (hw + gap), y, hw, card)
    y += 236 + 8
    # 8 small cards: 2 rows of 4
    sw = (CW - 3 * gap) // 4
    for row in range(2):
        for col in range(4):
            card = SMALL[row * 4 + col]
            draw_small(d, M + col * (sw + gap), y + row * (128 + 8), sw, card)
    y += 2 * 128 + 8
    # bottom row: map + also-on + verdict
    y += 6
    text(d, M, y, "WHERE IT HAPPENED", f(SANS_B, 11), INK)
    y += 16
    bh = 184
    draw_map(d, M, y, 270, bh)
    draw_also_on(d, M + 282, y, 440, bh)
    draw_verdict(d, M + 734, y, CW - 734, bh)
    y += bh + 8
    y = draw_date_check(d, y)
    y += 8
    y = draw_footer(d, y)
    assert y <= H, f"page overflows: bottom y={y} > {H}"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    assert size <= 1048576, f"entry.png {size} bytes exceeds 1 MiB"
    print(f"wrote {out} ({size} bytes)")


if __name__ == "__main__":
    main()
