#!/usr/bin/env python3
"""news-image-20261120 — front page for Friday 20 November 2026.

Draws a 1024x1024 newspaper front page with PIL: masthead, region
and field bars, stat chips, an hourly timeline, 16 story cards with
small drawn banner scenes, a dotted world map with 16 pins, the
verdict box, 36 more stories, a date check and a sources footer.

Deterministic: no network, no clock, no randomness. Run:
    python3 build-image.py            # writes entry.png beside this file
The image must stay under 1 MiB and 1024x1024, and two runs must
produce identical bytes.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

# --- my own palette -------------------------------------------------------
INK = (18, 18, 18)
NAVY = (13, 27, 62)
NAVY2 = (24, 44, 92)
RED = (176, 32, 32)
GOLD = (198, 158, 40)
GREEN = (30, 124, 60)
GREY = (96, 96, 96)
DGREY = (64, 64, 64)
LGREY = (206, 206, 206)
PAPER = (255, 255, 255)
CREAM = (250, 245, 234)
TEAL = (14, 90, 96)

# --- fonts ----------------------------------------------------------------
def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def sans(size):
    return _font("DejaVuSans.ttf", size)


def sans_b(size):
    return _font("DejaVuSans-Bold.ttf", size)


def serif(size):
    return _font("DejaVuSerif.ttf", size)


def serif_b(size):
    return _font("DejaVuSerif-Bold.ttf", size)


def mono(size):
    return _font("DejaVuSansMono.ttf", size)


def text_w(f, s):
    return f.getlength(s)


def wrap(text, f, max_w):
    """Split text into lines that fit max_w pixels (word boundaries only)."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(f, trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_center(d, cx, y, s, f, fill):
    d.text((cx, y), s, font=f, fill=fill, anchor="ma")


def draw_left(d, x, y, s, f, fill):
    d.text((x, y), s, font=f, fill=fill, anchor="la")


def draw_right(d, x, y, s, f, fill):
    d.text((x, y), s, font=f, fill=fill, anchor="ra")


# --- the 52 stories --------------------------------------------------------
# Each card: number, region, tag, headline, summary, source, badge, scene, pin.
# Badge: REPORTED (green) unless noted. Pin: (lon, lat) for the map.
CARDS = [
    dict(n=1, region="EUROPE", tag="POLAND",
         headline="Russian missiles land in Poland",
         summary="Two missiles and a suspected drone came down; Poland calls it a deliberate provocation; NATO calls it a grave violation.",
         source="REUTERS", badge="REPORTED", scene="missiles", pin=(19.0, 52.0)),
    dict(n=2, region="EUROPE", tag="KYIV",
         headline="Russian strikes hit three Kyiv bridges",
         summary="3 killed, ~15 injured; follows Ukraine hitting the Crimea Bridge a third time this week.",
         source="REUTERS", badge="REPORTED", scene="bridges", pin=(30.5, 50.5)),
    dict(n=3, region="WORLD", tag="GENOCIDE",
         headline="World Court: Myanmar committed genocide",
         summary="First state held responsible for genocide against the Rohingya; reparations ordered.",
         source="UN NEWS", badge="1ST", scene="court", pin=(4.3, 52.1)),
    dict(n=4, region="WORLD", tag="SELL-OFF",
         headline="AI sell-off drags world markets down",
         summary="S&P 500 -3.7% into correction; Nikkei -5.06% on AI cost worries.",
         source="WSJ", badge="REPORTED", scene="selloff", pin=(-74.0, 40.7)),
    dict(n=5, region="AMERICAS", tag="IPO",
         headline="Anthropic debuts on Nasdaq as ANT",
         summary="$81.3bn raised, largest IPO on record; priced $83, closed $97.17, +17%.",
         source="WSJ", badge="REPORTED", scene="ipo", pin=(-122.4, 37.8)),
    dict(n=6, region="EUROPE", tag="COP31",
         headline="COP31 draft drops fossil fuels",
         summary="Second draft in Antalya omits fossil fuels; talks run past deadline; activists protest.",
         source="CARBON BRIEF", badge="REPORTED", scene="cop31", pin=(30.7, 36.9)),
    dict(n=7, region="MIDDLE EAST", tag="HORMUZ",
         headline="Tankers keep catching fire in Hormuz",
         summary="US blockade; Iran mounts attacks; IEA: largest energy supply shock on record.",
         source="REUTERS", badge="REPORTED", scene="hormuz", pin=(56.3, 26.6)),
    dict(n=8, region="EUROPE", tag="RESET",
         headline="UK and EU sign landmark reset deal",
         summary="Food trade, carbon markets, youth mobility (18-31, 100,000 places a year).",
         source="BBC", badge="REPORTED", scene="reset", pin=(4.35, 50.85)),
    dict(n=9, region="AMERICAS", tag="QUAKE",
         headline="Magnitude 6.7 earthquake hits central Peru",
         summary="Cerro de Pasco; one injured, buildings and roads damaged.",
         source="USGS", badge="REPORTED", scene="quake", pin=(-76.3, -10.7)),
    dict(n=10, region="EUROPE", tag="BORDER",
         headline="Estonia to close Russia border crossings",
         summary="After sabotage attack; from Dec 1, at least six months.",
         source="REUTERS", badge="CLOSED", scene="border", pin=(24.7, 59.4)),
    dict(n=11, region="WORLD", tag="MERCURY",
         headline="BepiColombo reaches Mercury",
         summary="ESA/JAXA spacecraft arrives after an eight-year journey.",
         source="ESA", badge="REPORTED", scene="mercury", pin=(-30.0, -20.0)),
    dict(n=12, region="AMERICAS", tag="PALISADES",
         headline="Jury convicts man who started Palisades Fire",
         summary="Jonathan Rinderknecht found guilty of starting the fire.",
         source="AP", badge="REPORTED", scene="fire", pin=(-118.2, 34.05)),
    dict(n=13, region="AMERICAS", tag="ROUNDUP",
         headline="Judge approves $7.25bn Bayer settlement",
         summary="Missouri court signs off on the Roundup cancer settlement.",
         source="AP", badge="REPORTED", scene="roundup", pin=(-90.2, 38.6)),
    dict(n=14, region="MIDDLE EAST", tag="RIYADH",
         headline="Houthi missile damages Riyadh's tallest tower",
         summary="Windows blown out across 7-8 floors; no injuries reported.",
         source="REUTERS", badge="REPORTED", scene="tower", pin=(46.7, 24.7)),
    dict(n=15, region="WORLD", tag="SUMMIT",
         headline="Trump, Xi and Putin agree nuclear-risk talks",
         summary="First three-way summit in Shenzhen; US-China accord on human oversight of military AI.",
         source="AP", badge="REPORTED", scene="summit", pin=(114.1, 22.5)),
    dict(n=16, region="WORLD", tag="BITCOIN",
         headline="Bitcoin drops near $61,700",
         summary="Lowest since July; third straight day down.",
         source="COINDESK", badge="REPORTED", scene="bitcoin", pin=(139.7, 35.7)),
]

# Region and field for every story, so the bars are computed from the data.
CARD_REGIONS = {c["n"]: c["region"] for c in CARDS}
CARD_FIELDS = {
    1: "WAR", 2: "WAR", 3: "JUSTICE", 4: "MARKETS", 5: "MARKETS",
    6: "CLIMATE", 7: "WAR", 8: "DIPLOMACY", 9: "SCIENCE", 10: "DIPLOMACY",
    11: "SCIENCE", 12: "JUSTICE", 13: "JUSTICE", 14: "WAR",
    15: "DIPLOMACY", 16: "MARKETS",
}

# The 36 more stories: number, place tag, one-line headline.
MORE = [
    (17, "WASHINGTON", "Iran war powers rejected 51-48."),
    (18, "WASHINGTON", "Trump: no rush on next Iran step."),
    (19, "MOSCOW", "Zelensky calls Putin a killer."),
    (20, "DHAKA", "Violence ahead of Hasina's return."),
    (21, "TEXAS", "Hour-long execution draws scrutiny."),
    (22, "BAGHDAD", "Iraqi forces retake Jurf al-Nasr."),
    (23, "GAZA", "Israeli strikes kill Palestinians."),
    (24, "NEW YORK", "Gupta gets 19+ years in murder plot."),
    (25, "NIGERIA", "Funeral-mourner boat capsizes."),
    (26, "SENEGAL", "Migrant boat capsizes off Senegal."),
    (27, "TOKYO", "Core inflation hits year high."),
    (28, "CALIFORNIA", "Nvidia subpoenaed over China risks."),
    (29, "NEW YORK", "Card giants disclose vendor breaches."),
    (30, "TAIPEI", "TSMC, Samsung pause China chip sales."),
    (31, "BEIJING", "Bloomberg reporter barred from summit."),
    (32, "NEW DELHI", "First Pakistan minister visit since war."),
    (33, "DHAKA", "Awami League calls nationwide protest."),
    (34, "OTTAWA", "2026 budget passes House, 162-151."),
    (35, "VICTORIA", "BC's first Conservative win in a century."),
    (36, "MOUNTAIN VIEW", "Google launches Gemini 4 Neon."),
    (37, "REDMOND", "Nvidia, Microsoft deepen AI partnership."),
    (38, "BINANCE", "Hacker moves ~$600M in Ether."),
    (39, "WASHINGTON", "SEC charges 8 over fake crypto fraud."),
    (40, "WASHINGTON", "US expands military ops in LatAm."),
    (41, "SAN SALVADOR", "Bukele seeks third term after reform."),
    (42, "ABUJA", "Nigeria to end jail for attempted suicide."),
    (43, "NEW YORK", "Race for next UN chief exposes divisions."),
    (44, "BEIJING", "Xi hails 'turnaround' with Australia."),
    (45, "WASHINGTON", "White House replaces cyber chief after outages."),
    (46, "BUENOS AIRES", "Senate approves disability framework."),
    (47, "COPENHAGEN", "Denmark expels Russian attache."),
    (48, "RIYADH", "Saudi air defences down three missiles."),
    (49, "BRUSSELS", "EU adopts \u20ac1bn military aid to Ukraine."),
    (50, "WASHINGTON", "US sanctions four Iranians."),
    (51, "PARIS", "Depardieu, Houellebecq face rape probe."),
    (52, "WASHINGTON", "US loses measles elimination status."),
]

MORE_REGIONS = {
    17: "AMERICAS", 18: "AMERICAS", 19: "EUROPE", 20: "ASIA",
    21: "AMERICAS", 22: "MIDDLE EAST", 23: "MIDDLE EAST", 24: "AMERICAS",
    25: "AFRICA", 26: "AFRICA", 27: "ASIA", 28: "AMERICAS",
    29: "AMERICAS", 30: "ASIA", 31: "ASIA", 32: "ASIA", 33: "ASIA",
    34: "AMERICAS", 35: "AMERICAS", 36: "AMERICAS", 37: "AMERICAS",
    38: "WORLD", 39: "AMERICAS", 40: "AMERICAS", 41: "AMERICAS",
    42: "AFRICA", 43: "WORLD", 44: "ASIA", 45: "AMERICAS",
    46: "AMERICAS", 47: "EUROPE", 48: "MIDDLE EAST", 49: "EUROPE",
    50: "AMERICAS", 51: "EUROPE", 52: "AMERICAS",
}
MORE_FIELDS = {
    17: "POLITICS", 18: "POLITICS", 19: "DIPLOMACY", 20: "POLITICS",
    21: "JUSTICE", 22: "WAR", 23: "WAR", 24: "JUSTICE",
    25: "SOCIETY", 26: "SOCIETY", 27: "MARKETS", 28: "MARKETS",
    29: "MARKETS", 30: "MARKETS", 31: "DIPLOMACY", 32: "DIPLOMACY",
    33: "POLITICS", 34: "POLITICS", 35: "POLITICS", 36: "SCIENCE",
    37: "MARKETS", 38: "MARKETS", 39: "JUSTICE", 40: "WAR",
    41: "POLITICS", 42: "SOCIETY", 43: "DIPLOMACY", 44: "DIPLOMACY",
    45: "POLITICS", 46: "POLITICS", 47: "DIPLOMACY", 48: "WAR",
    49: "POLITICS", 50: "DIPLOMACY", 51: "JUSTICE", 52: "SOCIETY",
}

REGION_ORDER = ["ASIA", "EUROPE", "MIDDLE EAST", "AFRICA", "AMERICAS", "WORLD"]
FIELD_ORDER = ["DIPLOMACY", "JUSTICE", "CLIMATE", "MARKETS",
               "WAR", "POLITICS", "SOCIETY", "SCIENCE"]

STATS = [
    ("$81.3bn", "Anthropic record IPO"),
    ("6.7", "Peru earthquake magnitude"),
    ("$7.25bn", "Bayer Roundup settlement"),
    ("-3.7%", "S&P 500 into correction"),
    ("100,000", "UK-EU youth places a year"),
    ("$61,700", "Bitcoin low since July"),
]

TIMELINE = [
    ("01:40", "Peru quake: 6.7"),
    ("06:00", "Bitcoin nears $61,700"),
    ("09:00", "ICJ: Myanmar genocide"),
    ("12:30", "COP31 drops fossil fuels"),
    ("14:30", "ANT debuts, $97.17"),
    ("16:10", "UK-EU reset deal signed"),
    ("19:20", "Poland: missiles land"),
]

VERDICT_TITLE = "THE VERDICT \u2014 POLAND \u00b7 NATO"
VERDICT_LINES = [
    "Two missiles and a drone land in Poland.",
    "Warsaw calls it a deliberate provocation.",
    "NATO calls it a grave violation.",
]

DATECHECK_LEFT = ("LEFT OUT \u2014 FIRST REPORTED ON OTHER DAYS: Crimea Bridge, "
                  "second strike, Wed 18 Nov \u00b7 Anthropic IPO priced $83, "
                  "Thu 19 Nov \u00b7 Hormuz tanker fires, an IRGC claim from "
                  "4 Nov \u00b7 BepiColombo launched, Oct 2018")
DATECHECK_NOTYET = ("NOT YET: COP31 closing text (talks run past deadline) \u00b7 "
                    "Estonia's border closure (from 1 Dec) \u00b7 the next Iran "
                    "step (Trump: 'see what happens after January 1')")
DATECHECK_NOTE = ("NOTE: This page covers only Friday 20 November 2026. Every "
                  "story here happened, or was first reported, on that day.")

FOOTER_SOURCES = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 CNN \u00b7 WSJ \u00b7 "
                  "UN News \u00b7 Carbon Brief \u00b7 Yonhap \u00b7 USGS \u00b7 ESA \u00b7 "
                  "CoinDesk \u00b7 Le Monde")
FOOTER_COVERAGE = "All 52 stories happened, or were first reported, on Fri 20 Nov 2026."
FOOTER_SURE = ("HOW SURE ARE WE?  REPORTED = confirmed by named sources \u00b7 "
               "CLAIM = one side says, unverified \u00b7 FORECAST = poll, draft or schedule")

# --- banner scenes ----------------------------------------------------------
# Each scene paints a small illustration into a (x0, y0, x1, y1) box.
# Simple geometric drawings, one per story, all my own.

def _stars(d, x0, y0, x1, y1, n, seed):
    """A few deterministic star dots (positions from a tiny LCG)."""
    a = seed
    for _ in range(n):
        a = (a * 1103515245 + 12345) & 0x7FFFFFFF
        sx = x0 + 4 + (a % max(1, (x1 - x0 - 8)))
        a = (a * 1103515245 + 12345) & 0x7FFFFFFF
        sy = y0 + 3 + (a % max(1, (y1 - y0 - 6)))
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(255, 255, 220))


def _flames(d, x0, y0, x1, y1):
    """Orange flame tongues rising from the bottom of the box."""
    base = y1 - 2
    for i, (fx, fh, col) in enumerate([(0.18, 20, (255, 120, 20)),
                                       (0.42, 28, (255, 80, 10)),
                                       (0.66, 22, (255, 140, 30)),
                                       (0.86, 16, (255, 100, 15))]):
        cx = x0 + (x1 - x0) * fx
        d.polygon([(cx - 7, base), (cx, base - fh), (cx + 7, base)], fill=col)
        d.ellipse([cx - 4, base - fh + 4, cx + 4, base - fh + 12], fill=(255, 200, 60))


def _stamp(d, box, text, color):
    """A rubber-stamp label: red-bordered box with bold red text."""
    x0, y0, x1, y1 = (int(v) for v in box)
    f = sans_b(12)
    tw = text_w(f, text)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    bx0 = int(cx - tw / 2 - 6)
    bx1 = int(cx + tw / 2 + 6)
    by0 = int(cy - 9)
    by1 = int(cy + 9)
    d.rectangle([bx0, by0, bx1, by1], outline=color, width=2)
    d.text((cx, cy), text, font=f, fill=color, anchor="mm")


def paint_scene(d, kind, x0, y0, x1, y1):
    bw, bh = x1 - x0, y1 - y0
    if kind == "missiles":
        d.rectangle([x0, y0, x1, y1], fill=(16, 22, 44))
        _stars(d, x0, y0, x1, y1, 8, 11)
        for i, hh in enumerate([14, 22, 10, 18, 12]):
            bx = x0 + 6 + i * (bw - 12) // 5
            d.rectangle([bx, y1 - hh, bx + (bw - 12) // 5 - 3, y1], fill=(38, 44, 70))
        d.line([x0 + bw * 0.55, y0 + 6, x0 + bw * 0.78, y0 + bh * 0.62],
               fill=(255, 140, 40), width=2)
        d.line([x0 + bw * 0.72, y0 + 4, x0 + bw * 0.92, y0 + bh * 0.55],
               fill=(255, 180, 80), width=2)
        d.ellipse([x0 + bw * 0.76, y0 + bh * 0.58, x0 + bw * 0.76 + 5,
                   y0 + bh * 0.58 + 5], fill=(255, 220, 120))
    elif kind == "bridges":
        d.rectangle([x0, y0, x1, y1], fill=(20, 30, 66))
        _stars(d, x0, y0, x1, y1, 10, 23)
        d.arc([x0 + 8, y0 + 4, x1 - 8, y0 + bh + 22], 180, 360, fill=(150, 160, 200), width=3)
        d.line([x0 + 4, y1 - 8, x1 - 4, y1 - 8], fill=(120, 130, 170), width=2)
        d.ellipse([x0 + bw * 0.30, y0 + 10, x0 + bw * 0.30 + 6, y0 + 16], fill=(255, 150, 50))
        d.ellipse([x0 + bw * 0.62, y0 + 14, x0 + bw * 0.62 + 5, y0 + 19], fill=(255, 180, 70))
    elif kind == "court":
        d.rectangle([x0, y0, x1, y1], fill=(232, 222, 200))
        d.polygon([(x0 + bw * 0.30, y0 + 4), (x0 + bw * 0.70, y0 + 4),
                   (x0 + bw * 0.50, y0 + 14)], fill=(250, 246, 238))
        for i in range(4):
            cx = x0 + bw * (0.32 + i * 0.12)
            d.rectangle([cx, y0 + 15, cx + 5, y1 - 4], fill=(250, 246, 238))
        d.rectangle([x0 + bw * 0.26, y1 - 5, x0 + bw * 0.74, y1 - 2], fill=(120, 100, 70))
        d.line([x0 + bw * 0.86, y0 + 8, x0 + bw * 0.86, y0 + 26], fill=(90, 70, 40), width=2)
        d.line([x0 + bw * 0.78, y0 + 12, x0 + bw * 0.94, y0 + 12], fill=(90, 70, 40), width=2)
        d.polygon([(x0 + bw * 0.76, y0 + 12), (x0 + bw * 0.80, y0 + 12),
                   (x0 + bw * 0.78, y0 + 18)], fill=(90, 70, 40))
        d.polygon([(x0 + bw * 0.92, y0 + 12), (x0 + bw * 0.96, y0 + 12),
                   (x0 + bw * 0.94, y0 + 18)], fill=(90, 70, 40))
    elif kind == "selloff":
        d.rectangle([x0, y0, x1, y1], fill=(238, 238, 236))
        pts = [(x0 + 6, y0 + 8), (x0 + bw * 0.30, y0 + 12),
               (x0 + bw * 0.48, y0 + 22), (x0 + bw * 0.68, y0 + 18),
               (x0 + bw * 0.86, y0 + 30), (x1 - 6, y0 + bh - 8)]
        d.line(pts, fill=(176, 32, 32), width=3)
        d.polygon([(x1 - 12, y0 + bh - 12), (x1 - 2, y0 + bh - 12), (x1 - 7, y0 + bh - 2)],
                  fill=(176, 32, 32))
        for px, py in pts:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(176, 32, 32))
    elif kind == "ipo":
        d.rectangle([x0, y0, x1, y1], fill=(226, 242, 226))
        pts = [(x0 + 6, y0 + bh - 10), (x0 + bw * 0.30, y0 + bh - 16),
               (x0 + bw * 0.52, y0 + bh - 12), (x0 + bw * 0.72, y0 + 14),
               (x1 - 6, y0 + 8)]
        d.line(pts, fill=(30, 124, 60), width=3)
        d.polygon([(x1 - 12, y0 + 4), (x1 - 2, y0 + 4), (x1 - 7, y0 + 12)],
                  fill=(30, 124, 60))
        d.text((x0 + 6, y0 + 4), "ANT $97.17", font=sans_b(11), fill=(20, 90, 40))
    elif kind == "cop31":
        d.rectangle([x0, y0, x1, y1], fill=(228, 240, 224))
        d.rectangle([x0, y0 + bh - 12, x1, y1], fill=(120, 170, 110))
        _stamp(d, (x0 + bw * 0.18, y0 + 4, x0 + bw * 0.82, y0 + 26),
               "FOSSIL FUELS", (176, 32, 32))
    elif kind == "hormuz":
        d.rectangle([x0, y0, x1, y1], fill=(14, 44, 60))
        d.rectangle([x0, y0 + bh - 12, x1, y1], fill=(10, 30, 44))
        d.rectangle([x0 + bw * 0.12, y0 + bh - 22, x0 + bw * 0.88, y0 + bh - 12],
                    fill=(30, 34, 40))
        d.rectangle([x0 + bw * 0.60, y0 + bh - 32, x0 + bw * 0.72, y0 + bh - 22],
                    fill=(30, 34, 40))
        _flames(d, x0 + bw * 0.20, y0 + 2, x0 + bw * 0.55, y0 + bh - 20)
    elif kind == "reset":
        d.rectangle([x0, y0, x1, y1], fill=(30, 60, 140))
        cx, cy, r = x0 + bw * 0.30, y0 + bh * 0.52, 13
        for k in range(12):
            import math
            a = 2 * math.pi * k / 12
            d.ellipse([cx + r * math.cos(a) - 1, cy + r * math.sin(a) - 1,
                       cx + r * math.cos(a) + 1, cy + r * math.sin(a) + 1],
                      fill=(255, 215, 0))
        d.line([x0 + bw * 0.62, y0 + 4, x1 - 6, y0 + bh - 4], fill=(255, 255, 255), width=3)
        d.line([x1 - 6, y0 + 4, x0 + bw * 0.62, y0 + bh - 4], fill=(255, 255, 255), width=3)
        d.line([x0 + bw * 0.62, y0 + 4, x1 - 6, y0 + bh - 4], fill=(200, 30, 30), width=1)
        d.line([x1 - 6, y0 + 4, x0 + bw * 0.62, y0 + bh - 4], fill=(200, 30, 30), width=1)
    elif kind == "quake":
        d.rectangle([x0, y0, x1, y1], fill=(240, 238, 230))
        pts = [(x0 + 4, y0 + bh * 0.45)]
        a = 7
        x = x0 + 4
        while x < x1 - 4:
            a = (a * 1103515245 + 12345) & 0x7FFFFFFF
            x += 6 + (a % 7)
            a = (a * 1103515245 + 12345) & 0x7FFFFFFF
            pts.append((x, y0 + bh * 0.45 + (a % 21) - 10))
        d.line(pts, fill=(40, 40, 40), width=2)
        d.line([(x0 + bw * 0.55, y0 + bh - 4), (x0 + bw * 0.62, y0 + bh - 14),
                (x0 + bw * 0.58, y0 + bh - 20), (x0 + bw * 0.68, y0 + bh - 26)],
               fill=(150, 90, 40), width=2)
    elif kind == "border":
        d.rectangle([x0, y0, x1, y1], fill=(226, 226, 226))
        d.rectangle([x0, y0 + bh - 8, x1, y1], fill=(120, 120, 120))
        yb = y0 + bh * 0.42
        for i in range(8):
            col = (200, 30, 30) if i % 2 == 0 else (250, 250, 250)
            d.rectangle([x0 + 6 + i * (bw - 12) // 8, yb,
                         x0 + 6 + (i + 1) * (bw - 12) // 8, yb + 7], fill=col)
        d.rectangle([x0 + 10, yb + 7, x0 + 14, y1 - 8], fill=(60, 60, 60))
        d.rectangle([x1 - 14, yb + 7, x1 - 10, y1 - 8], fill=(60, 60, 60))
    elif kind == "mercury":
        d.rectangle([x0, y0, x1, y1], fill=(8, 8, 16))
        _stars(d, x0, y0, x1, y1, 12, 41)
        cx, cy, r = x0 + bw * 0.68, y0 + bh * 0.55, 15
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 120, 50))
        d.ellipse([cx - 8, cy - 4, cx - 2, cy + 2], fill=(170, 95, 40))
        d.ellipse([cx + 2, cy + 4, cx + 8, cy + 10], fill=(170, 95, 40))
        d.ellipse([x0 + bw * 0.18, y0 + 8, x0 + bw * 0.18 + 4, y0 + 12], fill=(255, 255, 255))
        d.line([x0 + bw * 0.18, y0 + 10, cx - r - 2, cy - 4], fill=(180, 180, 180), width=1)
    elif kind == "fire":
        d.rectangle([x0, y0, x1, y1], fill=(24, 12, 8))
        _flames(d, x0, y0 + 4, x1, y1)
        d.rectangle([x0, y0 + bh - 6, x1, y1], fill=(10, 10, 10))
    elif kind == "roundup":
        d.rectangle([x0, y0, x1, y1], fill=(238, 230, 210))
        for i in range(3):
            cx = x0 + bw * (0.24 + i * 0.16)
            d.rectangle([cx, y0 + 12, cx + 6, y1 - 6], fill=(250, 246, 238))
        d.rectangle([x0 + bw * 0.18, y0 + 8, x0 + bw * 0.66, y0 + 12], fill=(120, 100, 70))
        d.rectangle([x0 + bw * 0.74, y0 + 10, x0 + bw * 0.90, y0 + 16], fill=(110, 70, 30))
        d.line([x0 + bw * 0.82, y0 + 16, x0 + bw * 0.94, y0 + 28], fill=(110, 70, 30), width=3)
    elif kind == "tower":
        d.rectangle([x0, y0, x1, y1], fill=(52, 40, 72))
        d.rectangle([x0, y0 + bh * 0.55, x1, y1], fill=(30, 24, 48))
        tx = x0 + bw * 0.42
        d.rectangle([tx, y0 + 4, tx + bw * 0.16, y1], fill=(24, 22, 34))
        for r in range(5):
            for c in range(2):
                wx = tx + 3 + c * (bw * 0.16 - 8) // 2 + (bw * 0.16 - 8) // 4
                wy = y0 + 8 + r * 7
                col = (255, 220, 120) if (r + c) % 2 == 0 else (200, 200, 200)
                d.rectangle([wx, wy, wx + 3, wy + 3], fill=col)
        d.polygon([(tx + bw * 0.02, y0 + 16), (tx + bw * 0.10, y0 + 10),
                   (tx + bw * 0.14, y0 + 18)], fill=(240, 240, 240))
    elif kind == "summit":
        d.rectangle([x0, y0, x1, y1], fill=(236, 234, 228))
        flags = [((200, 30, 30), "US"), ((200, 30, 30), "CN"), ((240, 240, 240), "RU")]
        for i, (col, lab) in enumerate(flags):
            fx = x0 + bw * (0.14 + i * 0.28)
            d.rectangle([fx, y0 + 6, fx + bw * 0.20, y0 + 22], fill=col, outline=(120, 120, 120))
            if lab == "US":
                d.rectangle([fx, y0 + 6, fx + bw * 0.09, y0 + 13], fill=(30, 60, 140))
                d.line([fx, y0 + 14, fx + bw * 0.20, y0 + 14], fill=(255, 255, 255), width=1)
            elif lab == "CN":
                d.ellipse([fx + 3, y0 + 9, fx + 7, y0 + 13], fill=(255, 215, 0))
            else:
                d.rectangle([fx, y0 + 11, fx + bw * 0.20, y0 + 16], fill=(30, 60, 140))
                d.rectangle([fx, y0 + 16, fx + bw * 0.20, y0 + 22], fill=(200, 30, 30))
            d.text((fx + 2, y0 + 25), lab, font=sans_b(8), fill=DGREY)
    elif kind == "bitcoin":
        d.rectangle([x0, y0, x1, y1], fill=(16, 22, 44))
        cx, cy, r = x0 + bw * 0.30, y0 + bh * 0.52, 14
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 180, 40))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(180, 130, 20), width=2)
        d.text((cx, cy - 9), "B", font=sans_b(16), fill=(120, 80, 10), anchor="ma")
        d.text((x0 + bw * 0.52, y0 + 6), "$61,700", font=sans_b(13), fill=(240, 200, 80))
        d.text((x0 + bw * 0.52, y0 + 22), "LOWEST SINCE JULY", font=sans_b(8), fill=(180, 180, 180))
    else:
        d.rectangle([x0, y0, x1, y1], fill=(220, 220, 220))


def badge(d, x1, y, text, color):
    """Small tag badge, right-aligned at x1, top at y. Returns its left edge."""
    f = sans_b(9)
    tw = text_w(f, text)
    bx0 = x1 - tw - 12
    d.rounded_rectangle([bx0, y, x1, y + 14], radius=3, fill=color)
    d.text(((bx0 + x1) / 2, y + 7), text, font=f, fill=PAPER, anchor="mm")
    return bx0


# --- dotted world map ---------------------------------------------------------
# Land mask as (col_start, col_end) spans per row; 64 cols (lon -180..180),
# 20 rows (lat 80..-60). A rough equirectangular world, good enough for dots.
LAND_SPANS = [
    [(2, 4), (8, 14), (20, 22), (40, 62)],
    [(1, 5), (7, 16), (19, 23), (31, 34), (36, 63)],
    [(1, 4), (6, 17), (20, 22), (31, 36), (37, 63)],
    [(5, 18), (30, 39), (40, 62)],
    [(6, 19), (30, 39), (40, 62)],
    [(7, 19), (30, 34), (36, 42), (43, 60), (57, 58)],
    [(8, 18), (10, 14), (30, 33), (36, 42), (45, 47), (50, 56), (57, 58)],
    [(11, 15), (29, 40), (38, 43), (45, 47), (49, 53)],
    [(13, 16), (29, 41), (46, 47), (49, 53), (52, 55)],
    [(18, 22), (30, 41), (50, 53), (52, 57)],
    [(18, 24), (30, 40), (52, 57)],
    [(18, 24), (31, 40), (52, 56)],
    [(18, 23), (31, 39), (52, 58)],
    [(19, 23), (31, 38), (52, 59)],
    [(19, 22), (32, 37), (52, 59)],
    [(19, 22), (32, 36), (53, 58)],
    [(20, 22), (54, 57)],
    [(20, 21), (62, 63)],
    [(20, 21)],
    [(20, 21)],
]
LAND = set()
for _r, _spans in enumerate(LAND_SPANS):
    for _a, _b in _spans:
        for _c in range(_a, _b + 1):
            LAND.add((_c, _r))


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    """Equirectangular projection into the map box (lon -180..180, lat 80..-60)."""
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (80.0 - lat) / 140.0 * mh
    return x, y


def draw_map(d, mx, my, mw, mh):
    step_x, step_y = 7, 7
    dot_r = 1.6
    x = mx + 3
    while x < mx + mw - 2:
        y = my + 3
        while y < my + mh - 2:
            col = int((x - mx) / mw * 64)
            row = int((y - my) / mh * 20)
            if (col, row) in LAND:
                d.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r],
                          fill=(120, 130, 150))
            y += step_y
        x += step_x

# --- page sections ------------------------------------------------------------
def count_bars():
    """Count stories by region and field from the data (must total 52)."""
    regions = {r: 0 for r in REGION_ORDER}
    fields = {f: 0 for f in FIELD_ORDER}
    for n, r in CARD_REGIONS.items():
        regions[r] += 1
    for n, f in CARD_FIELDS.items():
        fields[f] += 1
    for n, r in MORE_REGIONS.items():
        regions[r] += 1
    for n, f in MORE_FIELDS.items():
        fields[f] += 1
    assert sum(regions.values()) == 52, regions
    assert sum(fields.values()) == 52, fields
    return regions, fields


def draw_masthead(d):
    d.rectangle([0, 0, W, 66], fill=NAVY)
    d.rounded_rectangle([MARGIN, 8, MARGIN + 76, 62], radius=4, fill=PAPER)
    draw_center(d, MARGIN + 38, 12, "NOV 20", sans_b(19), RED)
    draw_center(d, MARGIN + 38, 38, "FRI \u00b7 2026", sans_b(10), INK)
    draw_left(d, 112, 8, "Friday 20 November 2026", serif_b(32), PAPER)
    draw_left(d, 112, 46,
              "The world, one page. Everything here happened \u2014 or was "
              "first reported \u2014 on that day.", sans(12), (198, 203, 220))
    draw_right(d, W - MARGIN, 10,
               "52 STORIES \u00b7 6 REGIONS \u00b7 8 FIELDS \u00b7 16 CARDS \u00b7 ONE PAGE",
               sans_b(10), GOLD)
    draw_right(d, W - MARGIN, 28, "ONE DAY \u00b7 ONE PAGE", sans_b(10), GOLD)
    return 66


def draw_bar_row(d, y, label, names, counts, ncols):
    """One labelled bar row: small label left, name+count columns spread out."""
    h = 24
    draw_left(d, MARGIN, y + 6, label, sans_b(9), GREY)
    x0, x1 = 118, W - MARGIN
    slot = (x1 - x0) / ncols
    for i, name in enumerate(names):
        cx = x0 + slot * (i + 0.5)
        draw_center(d, cx, y + 1, name, sans_b(9), GREY)
        draw_center(d, cx, y + 11, str(counts[name]), sans_b(15), INK)
    d.line([MARGIN, y + h, W - MARGIN, y + h], fill=LGREY, width=1)
    return y + h


def draw_stats(d, y):
    h = 28
    x0, x1 = MARGIN, W - MARGIN
    slot = (x1 - x0) / len(STATS)
    for i, (num, cap) in enumerate(STATS):
        cx = x0 + slot * (i + 0.5)
        if i:
            d.line([x0 + slot * i, y + 4, x0 + slot * i, y + h - 4], fill=LGREY, width=1)
        draw_center(d, cx, y + 2, num, sans_b(15), INK)
        draw_center(d, cx, y + 17, cap, sans(8), GREY)
    d.line([MARGIN, y + h, W - MARGIN, y + h], fill=LGREY, width=1)
    return y + h


def draw_timeline(d, y):
    h = 42
    draw_left(d, MARGIN, y + 2, "THE DAY BY HOURS", sans_b(9), INK)
    line_y = y + 24
    d.line([MARGIN, line_y, W - MARGIN, line_y], fill=LGREY, width=2)
    slot = (W - 2 * MARGIN) / len(TIMELINE)
    f_time, f_lab = sans_b(9), sans(9)
    for i, (t, lab) in enumerate(TIMELINE):
        cx = MARGIN + slot * (i + 0.5)
        d.ellipse([cx - 4, line_y - 4, cx + 4, line_y + 4], fill=RED)
        draw_center(d, cx, y + 10, t, f_time, DGREY)
        draw_center(d, cx, line_y + 7, lab, f_lab, INK)
    d.line([MARGIN, y + h, W - MARGIN, y + h], fill=RED, width=2)
    return y + h


def draw_card(d, card, x, y, cw, ch):
    d.rectangle([x, y, x + cw, y + ch], outline=LGREY, width=1, fill=PAPER)
    bh = 34
    paint_scene(d, card["scene"], x + 1, y + 1, x + cw - 1, y + bh)
    badge_col = RED if card["badge"] in ("1ST", "CLOSED") else GREEN
    if card["badge"] == "1ST":
        f = sans_b(9)
        tw = text_w(f, "1ST")
        d.rounded_rectangle([x + 4, y + 4, x + 4 + tw + 12, y + 18], radius=3, fill=RED)
        d.text((x + 4 + (tw + 12) / 2, y + 11), "1ST", font=f, fill=PAPER, anchor="mm")
    else:
        badge(d, x + cw - 4, y + 4, card["badge"], badge_col)
    hy = y + bh + 4
    head = "%02d \u00b7 %s \u00b7 %s" % (card["n"], card["region"], card["tag"])
    draw_left(d, x + 6, hy, head, sans_b(10), RED)
    draw_right(d, x + cw - 6, hy, card["source"], sans_b(9), GREY)
    ty = hy + 14
    hl = wrap(card["headline"], sans_b(13), cw - 12)
    assert len(hl) <= 2, "headline too long: %r -> %r" % (card["headline"], hl)
    for line in hl:
        draw_left(d, x + 6, ty, line, sans_b(13), INK)
        ty += 14
    sl = wrap(card["summary"], sans(10), cw - 12)
    assert len(sl) <= 3, "summary too long: %r -> %r" % (card["summary"], sl)
    for line in sl:
        draw_left(d, x + 6, ty, line, sans(10), DGREY)
        ty += 11
    return y + ch


def draw_cards(d, y):
    cw, ch, gx, gy = 236, 114, 10, 6
    for row in range(4):
        for col in range(4):
            card = CARDS[row * 4 + col]
            x = MARGIN + col * (cw + gx)
            draw_card(d, card, x, y + row * (ch + gy), cw, ch)
    return y + 4 * ch + 3 * gy


def draw_map_section(d, y):
    """Dotted world map with 16 pins (left) and the verdict box (right)."""
    draw_left(d, MARGIN, y, "WHERE IT HAPPENED \u2014 16 PINS, ONE PER CARD",
              sans_b(10), INK)
    map_y = y + 14
    map_h = 80
    map_x, map_w = MARGIN, 640
    draw_map(d, map_x, map_y, map_w, map_h)
    f_pin = sans_b(8)
    for card in CARDS:
        px, py = lonlat_to_xy(card["pin"][0], card["pin"][1],
                              map_x, map_y, map_w, map_h)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=PAPER, width=1)
        d.text((px, py), str(card["n"]), font=f_pin, fill=PAPER, anchor="mm")
    vx0, vx1 = 676, W - MARGIN
    d.rectangle([vx0, map_y, vx1, map_y + map_h], fill=NAVY)
    draw_left(d, vx0 + 10, map_y + 7, VERDICT_TITLE, sans_b(11), PAPER)
    ty = map_y + 26
    for line in VERDICT_LINES:
        draw_left(d, vx0 + 10, ty, line, sans(10), (225, 228, 236))
        ty += 14
    return map_y + map_h


def draw_more(d, y):
    draw_left(d, MARGIN, y, "36 MORE STORIES", sans_b(11), INK)
    y += 16
    col_w = 320
    f_pre, f_txt = sans_b(9), sans(9)
    for r in range(12):
        for c in range(3):
            idx = r * 3 + c
            n, place, text = MORE[idx]
            x = MARGIN + c * (col_w + 8)
            pre = "%d \u00b7 %s " % (n, place)
            total = pre + text
            # Nothing may truncate mid-word: the whole line must fit its column.
            assert text_w(f_pre, pre) + text_w(f_txt, text) <= col_w, \
                "36-more line too wide: %r" % total
            d.text((x, y + r * 11), pre, font=f_pre, fill=INK, anchor="la")
            d.text((x + text_w(f_pre, pre), y + r * 11), text, font=f_txt,
                   fill=DGREY, anchor="la")
    return y + 12 * 11


def draw_datecheck(d, y):
    """Red-bordered box: what was left out, what is not yet, and the note."""
    f_lab, f_txt = sans_b(10), sans(9)
    inner_w = W - 2 * MARGIN - 16
    left_lines = wrap(DATECHECK_LEFT, f_txt, inner_w)
    notyet_lines = wrap(DATECHECK_NOTYET, f_txt, inner_w)
    note_lines = wrap(DATECHECK_NOTE, f_txt, inner_w)
    box_h = 12 + (len(left_lines) + len(notyet_lines) + len(note_lines)) * 11 + 6
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=RED, width=2)
    ty = y + 6
    draw_left(d, MARGIN + 8, ty, "DATE CHECK", f_lab, RED)
    ty += 14
    for line in left_lines:
        draw_left(d, MARGIN + 8, ty, line, f_txt, INK)
        ty += 11
    for line in notyet_lines:
        draw_left(d, MARGIN + 8, ty, line, f_txt, INK)
        ty += 11
    for line in note_lines:
        draw_left(d, MARGIN + 8, ty, line, f_txt, DGREY)
        ty += 11
    return y + box_h


def draw_footer(d, y):
    f = sans(9)
    draw_left(d, MARGIN, y, FOOTER_SOURCES, f, GREY)
    draw_left(d, MARGIN, y + 10, FOOTER_COVERAGE, f, GREY)
    draw_left(d, MARGIN, y + 20, FOOTER_SURE, f, GREY)
    return y + 30


def build(out_path):
    regions, fields = count_bars()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = draw_masthead(d)
    y = draw_bar_row(d, y + 2, "BY REGION", REGION_ORDER, regions, 6)
    y = draw_bar_row(d, y + 1, "BY FIELD", FIELD_ORDER, fields, 8)
    y = draw_stats(d, y + 1)
    y = draw_timeline(d, y + 2)
    y = draw_cards(d, y + 4)
    y = draw_map_section(d, y + 4)
    y = draw_more(d, y + 4)
    y = draw_datecheck(d, y + 4)
    y = draw_footer(d, y + 2)
    assert y <= H, "page overflow: bottom y=%d > %d" % (y, H)
    img.save(out_path, format="PNG")
    data = open(out_path, "rb").read()
    assert len(data) <= 1048576, "entry.png too big: %d bytes" % len(data)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (out_path, len(data), digest))
    return digest


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png")
    build(target)
