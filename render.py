#!/usr/bin/env python3
"""Render the news-image-20261120 v3 entry: one 1024x1024 PNG newspaper
summing up world news of Friday 20 November 2026.

Written from scratch for v3. Every one of the 48 stories happened, or was
first reported, on Friday 20 November 2026 (any time zone). Thursday
stories from v2 (Shenzhen summit, ICJ Myanmar ruling, US Senate Iran vote
51-48, PIF Tower strike, Egypt IMF staff deal, Argentina disability law,
Colombia strike, Gambia mpox, Dakar boat, Sanon verdict, Hegseth Quito
visit, Trump-Iran interview) were removed and replaced with verified
Friday stories. Deterministic: same bytes on every run.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 20, 20)
RED = (176, 30, 30)
BLUE = (30, 70, 140)
GREY = (90, 86, 76)
LINE = (120, 110, 88)
MAP_FILL = (230, 217, 184)
MAP_LINE = (138, 122, 82)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines fitting width."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, fnt, width, suffix="..."):
    """Truncate to a single line that fits width."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + suffix, font=fnt) > width:
        text = text[:-1]
    return text + suffix


# ---------------------------------------------------------------- data
# (number, region, topic, source, headline, body, art, pin lon/lat)
LEADS = [
    (1, "EUROPE", "UKRAINE", "CNN",
     "Russian barrage hits Kyiv",
     "110+ missiles, 400+ drones overnight; 8 killed, 28 hurt. 3 bridges hit; debris falls in Poland.",
     "kyiv", (30, 50)),
    (2, "ASIA", "WEATHER", "IMD",
     "Cyclone Akvan hits India's coast",
     "Landfall near Gopalpur 02:00 UTC, winds to 90 km/h, 300,000 evacuated; 9,341 shelters open.",
     "akvan", (85, 19)),
    (3, "GLOBAL", "MARKETS", "TIMES",
     "AI rout: Nasdaq falls 5.3%",
     "S&P 500 into correction; Anthropic -9% to near $88. Nasdaq -10% on the week; Nikkei -5.1% on Friday.",
     "chart", (-74, 41)),
    (4, "GLOBAL", "CLIMATE", "REUTERS",
     "COP31 draft drops fossil fuels",
     "Final day ends with no deal; talks run into overtime. Panama threatens veto; Turkey lands $26bn+ in deals.",
     "globe", (30, 37)),
]

CARDS = [
    (5, "GLOBAL", "MARKETS", "TIMES",
     "Bitcoin slides to $61,700",
     "Lowest since July as AI rout spreads; third straight daily fall.",
     "bitcoin", (-122, 37)),
    (6, "AMERICAS", "DISASTER", "AP",
     "6.7 quake shakes Peru",
     "Tremor hits Junin at 19:09 local; felt in Lima. No deaths reported.",
     "quake", (-75, -11)),
    (7, "MIDDLE EAST", "GULF", "REUTERS",
     "Houthis threaten Saudi ports",
     "Rebels warn Red Sea ports; civilians told to leave Hodeidah. Brent $92.77.",
     "shield", (47, 25)),
    (8, "EUROPE", "UKRAINE", "EU",
     "EU gives Ukraine 1bn euros in arms aid",
     "Joint arms buying; delivery by end 2027. Part of a 6.6bn euro package.",
     "stars", (4, 51)),
    (9, "AFRICA", "SOUTH AFRICA", "PRETORIA",
     "South Africa mourns Mlambo-Ngcuka, 71",
     "First woman deputy president and ex-UN Women chief dies; no cause given.",
     "71", (28, -26)),
    (10, "OCEANIA", "DIPLOMACY", "CANADA",
     "Australia, Canada and NZ urge ceasefire",
     "Joint APEC statement calls for a permanent, unconditional ceasefire now.",
     "flags", (149, -35)),
    (11, "OCEANIA", "AUSTRALIA", "AFP",
     "AFP foils alleged Sydney car-bomb plot",
     "A 35-year-old charged with terror offences after dawn raids in the south-west.",
     "car", (151, -34)),
    (12, "AMERICAS", "BUSINESS", "REUTERS",
     "Tesla opens first store in Argentina",
     "Model 3 from $40,990 and Model Y from $43,990; market opens to Chinese rivals.",
     "tesla", (-58, -35)),
    (13, "AFRICA", "JUSTICE", "BBC",
     "Nigeria to end jail for attempted suicide",
     "Move to scrap prison terms; campaigners hail a mental-health landmark.",
     "scales", (7, 9)),
    (14, "ASIA", "TECH", "WIRES",
     "TSMC, Samsung halt China chip sales",
     "Advanced AI chips halted under new US export curbs; licences now needed.",
     "chip", (121, 25)),
    (15, "GLOBAL", "FOOTBALL", "SPL",
     "Ronaldo's 986th goal as Al-Ahli win 3-1",
     "He scores, then misses a penalty; Toney converts from the spot in the comeback.",
     "ball", (39, 21)),
    (16, "AMERICAS", "SANCTIONS", "TREASURY",
     "US sanctions 4 Iranians for oil money",
     "Treasury names four men it says handled Iranian oil revenues; out on Friday.",
     "ofac", (-77, 39)),
]

ALSO = [
    (17, "Tallinn", "Estonia shuts Russia border from Dec 1"),
    (18, "Kerch", "rail traffic resumes on bridge after strikes"),
    (19, "Washington", "US, China agree human control of military AI"),
    (20, "Hormuz", "Iran says 2 tankers hit mines - CLAIM"),
    (21, "Hormuz", "tanker strike and fire reported at sea"),
    (22, "Paris", "Senate adopts 'licence to kill' police law, 205-110"),
    (23, "Brussels", "UK-EU Brexit review summit opens"),
    (24, "London", "EU-UK youth mobility: ages 18-31, 100,000"),
    (25, "Frankfurt", "Boone, Brunnermeier named ECB picks"),
    (26, "Berlin", "students march against rearmament"),
    (27, "San Salvador", "Bukele seeks third term after charter change"),
    (28, "US", "robbery suspects charged over $22m train heists"),
    (29, "Paris", "IEA: Hormuz shock is largest energy shock on record"),
    (30, "Miami", "Messi tops MLS pay list again"),
    (31, "Tunis", "activist Bensedrine sentenced to 5 years"),
    (32, "New York", "race for next UN chief splits big powers"),
    (33, "Baghdad", "Iraqi forces to deploy in Hezbollah stronghold"),
    (34, "Abidjan", "Cote d'Ivoire to raise mining royalties 9.5%"),
    (35, "Abuja", "court rejects Atiku bid to amend Tinubu suit"),
    (36, "Nairobi", "record KCSE exams end; 1.05m candidates"),
    (37, "Tokyo", "93% of Japanese see China ties as poor"),
    (38, "New Delhi", "Pakistan minister visits India for SCO forum"),
    (39, "Ottawa", "Liberals' budget passes House, 162-151"),
    (40, "Dhaka", "UNGA chief visits Rohingya camps"),
    (41, "New York", "Gupta jailed 19+ years over NY murder plot"),
    (42, "Washington", "Trump replaces US cyber chief"),
    (43, "Melbourne", "AFL draft night two: 65 picks made"),
    (44, "Doha", "India A thrash Nepal by 306 runs; Nepal 26 all out"),
    (45, "Bengaluru", "Bengaluru FC 2-0 Mumbai City, top of ISL"),
    (46, "London", "Price edges Springer 16-15 into darts semis"),
    (47, "Munich", "Bayern held 1-1 by Koln; Kane hurt"),
    (48, "Doha", "Morocco hit Fiji 6-0 at the U-17 World Cup"),
]

TIMELINE = [
    ("Overnight", "Russian barrage hits Kyiv; 3 bridges damaged"),
    ("~02:00 UTC", "Cyclone Akvan crosses the coast at Gopalpur"),
    ("~06:00 UTC", "Nikkei closes -5.1%"),
    ("~15:00 UTC", "COP31 talks go into overtime"),
    ("Evening", "EU adopts 1bn euros in military aid for Ukraine"),
    ("Late", "Nasdaq -5.3%; worst week since March 2020"),
]

DATE_CHECK = (
    "Left out on purpose (wrong day): Shenzhen summit 19 Nov - ICJ Myanmar ruling 19 Nov - "
    "US Senate Iran vote 51-48, 19 Nov - Houthi hit on Riyadh PIF Tower 19 Nov - Egypt IMF staff "
    "deal 18 Nov - Argentina disability law 19 Nov - Colombia strike 19 Nov. "
    "All 48 stories here happened or were first reported Fri 20 Nov 2026. "
    "CLAIM = one side's account, not independently confirmed."
)
SOURCES = ("Sources: IMD, Reuters, CNN, AP, AFP, BBC, EU, US Treasury, UN News, IEA, USGS. "
           "Original drawings. Times are UTC unless stated.")

# ---------------------------------------------------------------- art
def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 48, 74))
    for bx, bw, bh in [(8, 34, 62), (48, 26, 84), (80, 30, 58), (116, 28, 76),
                       (150, 34, 52), (190, 26, 68)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(16, 16, 22))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            for wx in range(x + bx + 6, x + bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 200, 60))
    for sx, sy, ex, ey in [(20, 8, 70, 52), (90, 4, 140, 48), (160, 10, 205, 55)]:
        d.line([x + sx, y + sy, x + ex, y + ey], fill=(255, 140, 40), width=3)
        d.ellipse([x + ex - 4, y + ey - 4, x + ex + 4, y + ey + 4],
                  fill=(255, 200, 80))
    d.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], outline=(255, 255, 255),
              width=2)
    d.text((x + w - 24, y + 9), "PL", font=F_SANS_B(9), fill=(255, 255, 255))


def art_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 208, 228))
    cx, cy = x + w // 2, y + h // 2 - 6
    for r, col in [(52, (90, 140, 190)), (40, (60, 110, 170)),
                   (28, (40, 90, 150)), (16, (220, 230, 240))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(176, 30, 30))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 22),
               (x, y + h - 14)], fill=(90, 140, 80))
    for rx in range(x + 12, x + w - 8, 26):
        d.line([rx, y + h - 30, rx - 6, y + h - 18], fill=(120, 160, 200),
               width=2)
    d.rectangle([x + w - 52, y + h - 20, x + w - 4, y + h - 4],
                fill=(176, 30, 30))
    d.text((x + w - 48, y + h - 19), "300k", font=F_SANS_B(11),
           fill=(255, 255, 255))


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    pts = [(x + 8, y + 18), (x + 45, y + 30), (x + 80, y + 26),
           (x + 120, y + 48), (x + 160, y + 44), (x + 195, y + 72),
           (x + w - 10, y + h - 14)]
    d.line(pts, fill=(176, 30, 30), width=4)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(176, 30, 30))
    d.text((x + 10, y + 6), "-5.3%", font=F_SANS_B(20), fill=(176, 30, 30))


def art_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(208, 232, 200))
    cx, cy, r = x + w // 2, y + h // 2 - 8, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 150, 200))
    d.ellipse([cx - 30, cy - 22, cx - 8, cy - 2], fill=(70, 160, 90))
    d.ellipse([cx + 4, cy + 6, cx + 30, cy + 26], fill=(70, 160, 90))
    d.ellipse([cx + 12, cy - 26, cx + 28, cy - 10], fill=(70, 160, 90))
    d.rectangle([x, y, x + w, y + 16], fill=(176, 30, 30))
    d.text((x + 6, y + 2), "NO FOSSIL FUELS IN TEXT", font=F_SANS_B(10),
           fill=(255, 255, 255))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(30, 70, 140))
    d.text((x + 6, y + h - 17), "35% ELECTRICITY SHARE BY 2035",
           font=F_SANS_B(10), fill=(255, 255, 255))


def art_small(d, kind, x, y, w, h):
    """Tiny pictogram strip for cards (h ~ 34)."""
    if kind == "bitcoin":
        d.rectangle([x, y, x + w, y + h], fill=(245, 200, 80))
        d.text((x + 6, y + 4), "B  $61,700", font=F_SANS_B(16), fill=(120, 70, 0))
    elif kind == "quake":
        d.rectangle([x, y, x + w, y + h], fill=(210, 190, 160))
        d.line([x + 10, y + h - 4, x + 50, y + 8, x + 90, y + h - 8,
                x + 130, y + 6], fill=(120, 60, 20), width=3)
        d.text((x + w - 46, y + 4), "6.7", font=F_SANS_B(16), fill=(120, 60, 20))
    elif kind == "shield":
        d.rectangle([x, y, x + w, y + h], fill=(232, 220, 190))
        d.polygon([(x + w // 2, y + 4), (x + w // 2 + 16, y + 10),
                   (x + w // 2 + 16, y + 22), (x + w // 2, y + 30),
                   (x + w // 2 - 16, y + 22), (x + w // 2 - 16, y + 10)],
                  fill=(30, 70, 140))
        d.text((x + 8, y + 8), "RED SEA", font=F_SANS_B(11), fill=(90, 60, 20))
    elif kind == "stars":
        d.rectangle([x, y, x + w, y + h], fill=(30, 70, 140))
        for k in range(8):
            import math
            a = k * 3.14159 / 4
            px, py = x + w // 2 + int(22 * math.cos(a)), y + h // 2 + int(11 * math.sin(a))
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 220, 60))
        d.text((x + 6, y + 8), "EU", font=F_SANS_B(14), fill=(255, 255, 255))
    elif kind == "71":
        d.rectangle([x, y, x + w, y + h], fill=(60, 90, 60))
        d.text((x + 6, y + 2), "71", font=F_SANS_B(22), fill=(255, 255, 255))
        d.text((x + 44, y + 10), "PRETORIA", font=F_SANS_B(10),
               fill=(220, 230, 220))
    elif kind == "flags":
        d.rectangle([x, y, x + w, y + h], fill=(220, 235, 245))
        d.text((x + 6, y + 6), "AUS - CAN - NZ", font=F_SANS_B(13),
               fill=(30, 70, 140))
    elif kind == "car":
        d.rectangle([x, y, x + w, y + h], fill=(200, 210, 225))
        d.rectangle([x + 45, y + 6, x + w - 45, y + 15], fill=(176, 30, 30))
        d.rectangle([x + 12, y + 15, x + w - 12, y + 25], fill=(176, 30, 30))
        for wx in (x + 28, x + w - 48):
            d.ellipse([wx, y + 23, wx + 12, y + 33], fill=(20, 20, 20))
        d.text((x + 6, y + 4), "AFP", font=F_SANS_B(11), fill=(176, 30, 30))
    elif kind == "tesla":
        d.rectangle([x, y, x + w, y + h], fill=(225, 235, 245))
        d.rectangle([x + 55, y + 5, x + w - 55, y + 15], fill=(200, 40, 40))
        d.rectangle([x + 12, y + 15, x + w - 12, y + 25], fill=(200, 40, 40))
        for wx in (x + 28, x + w - 48):
            d.ellipse([wx, y + 23, wx + 12, y + 33], fill=(20, 20, 20))
        d.text((x + 6, y + 4), "1st STORE", font=F_SANS_B(11),
               fill=(30, 70, 140))
    elif kind == "scales":
        d.rectangle([x, y, x + w, y + h], fill=(235, 225, 200))
        d.line([x + w // 2, y + 4, x + w // 2, y + 28], fill=(90, 60, 20),
               width=3)
        d.line([x + w // 2 - 22, y + 10, x + w // 2 + 22, y + 10],
               fill=(90, 60, 20), width=3)
        d.polygon([(x + w // 2 - 30, y + 26), (x + w // 2 - 14, y + 26),
                   (x + w // 2 - 22, y + 12)], outline=(90, 60, 20))
        d.polygon([(x + w // 2 + 14, y + 26), (x + w // 2 + 30, y + 26),
                   (x + w // 2 + 22, y + 12)], outline=(90, 60, 20))
    elif kind == "chip":
        d.rectangle([x, y, x + w, y + h], fill=(40, 45, 60))
        d.rectangle([x + w // 2 - 16, y + 6, x + w // 2 + 16, y + 28],
                    fill=(90, 200, 140))
        for px in range(x + w // 2 - 12, x + w // 2 + 13, 8):
            d.line([px, y + 2, px, y + 6], fill=(180, 180, 180), width=2)
            d.line([px, y + 28, px, y + 32], fill=(180, 180, 180), width=2)
    elif kind == "ball":
        d.rectangle([x, y, x + w, y + h], fill=(240, 240, 235))
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=(20, 20, 20),
                  width=2)
        d.polygon([(cx, cy - 7), (cx + 7, cy - 2), (cx + 4, cy + 7),
                   (cx - 4, cy + 7), (cx - 7, cy - 2)], fill=(20, 20, 20))
        d.text((x + w - 40, y + 6), "986", font=F_SANS_B(14), fill=(20, 20, 20))
    elif kind == "ofac":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.rectangle([x + 6, y + 6, x + w - 6, y + h - 6], outline=(176, 30, 30),
                    width=3)
        d.text((x + 10, y + 8), "OFAC  x4", font=F_SANS_B(13),
               fill=(176, 30, 30))


ART = {"kyiv": art_kyiv, "akvan": art_akvan, "chart": art_chart,
       "globe": art_globe}


# ---------------------------------------------------------------- map
CONTINENTS = {
    "namerica": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73),
                 (-60, 62), (-55, 47), (-70, 42), (-75, 35), (-80, 25),
                 (-90, 21), (-97, 16), (-105, 20), (-115, 30), (-125, 40),
                 (-125, 49), (-140, 60), (-165, 60)],
    "samerica": [(-80, 10), (-70, 12), (-60, 5), (-50, 0), (-40, -5),
                 (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-65, -40),
                 (-70, -50), (-70, -20), (-75, -15), (-80, -5)],
    "europe": [(-10, 36), (0, 36), (10, 38), (20, 40), (28, 36), (30, 42),
               (20, 45), (10, 45), (0, 44), (-5, 43), (-9, 43), (-10, 48),
               (0, 50), (5, 53), (8, 57), (18, 56), (21, 55), (28, 60),
               (30, 65), (25, 70), (15, 70), (5, 60), (-5, 58)],
    "africa": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
               (35, 28), (40, 15), (48, 11), (51, 12), (48, 0), (40, -10),
               (35, -20), (30, -30), (20, -35), (15, -30), (12, -18),
               (9, -5), (9, 4), (-8, 5), (-15, 11)],
    "asia": [(30, 36), (35, 42), (45, 40), (50, 45), (60, 50), (70, 55),
             (80, 60), (90, 65), (100, 70), (120, 72), (140, 72), (160, 70),
             (178, 65), (170, 60), (160, 55), (150, 60), (140, 50),
             (130, 45), (127, 40), (122, 32), (115, 25), (108, 20),
             (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15),
             (77, 8), (72, 20), (65, 25), (58, 28), (52, 28), (48, 30),
             (42, 36), (36, 36)],
    "oceania": [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32),
                (137, -35), (140, -38), (145, -38), (150, -37), (153, -27),
                (150, -22), (146, -19), (142, -15), (140, -17), (135, -12),
                (130, -13), (125, -14), (120, -20), (113, -22)],
}


def draw_map(d, x0, y0, w, h, pins):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 232, 214),
                outline=LINE)
    def proj(lon, lat):
        return (x0 + (lon + 170) / 360 * w, y0 + (75 - lat) / 130 * h)
    for poly in CONTINENTS.values():
        d.polygon([proj(lo, la) for lo, la in poly], fill=MAP_FILL,
                  outline=MAP_LINE)
    for num, (lon, lat) in pins:
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=BLUE,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=F_SANS_B(9))
        d.text((px - tw / 2, py - 6), t, font=F_SANS_B(9),
               fill=(255, 255, 255))

# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top strip
    d.text((10, 3), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=F_SANS_B(11), fill=RED)
    right = "48 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM THIS FRIDAY"
    d.text((W - 10 - d.textlength(right, font=F_SANS_B(11)), 3), right,
           font=F_SANS_B(11), fill=INK)
    d.line([10, 20, W - 10, 20], fill=LINE, width=1)

    # masthead
    title = "Friday 20 November 2026"
    tf = F_SERIF_B(62)
    d.text(((W - d.textlength(title, font=tf)) / 2, 24), title, font=tf,
           fill=INK)
    d.line([10, 94, W - 10, 94], fill=INK, width=2)

    # timeline strip
    ty = 98
    d.rectangle([10, ty, 118, ty + 40], fill=RED)
    d.text((16, ty + 12), "THE DAY\nIN UTC", font=F_SANS_B(11),
           fill=(255, 255, 255))
    cell_w = (1014 - 122) // 6
    for i, (when, what) in enumerate(TIMELINE):
        cx = 122 + i * cell_w
        d.text((cx + 2, ty + 2), when, font=F_SANS_B(11), fill=RED)
        for j, ln in enumerate(wrap(d, what, F_SANS(11), cell_w - 6)):
            d.text((cx + 2, ty + 16 + j * 13), ln, font=F_SANS(11), fill=INK)
        if i:
            d.line([cx - 1, ty, cx - 1, ty + 40], fill=LINE, width=1)
    d.line([10, 140, W - 10, 140], fill=LINE, width=1)

    # leads
    col_w = (1004 - 3 * 8) // 4
    for i, (num, region, topic, src, head, body, art, pin) in enumerate(LEADS):
        x = 10 + i * (col_w + 8)
        y = 142
        ART[art](d, x, y, col_w, 118)
        ky = y + 122
        d.ellipse([x, ky, x + 16, ky + 16], fill=BLUE)
        t = str(num)
        d.text((x + 8 - d.textlength(t, font=F_SANS_B(10)) / 2, ky + 2), t,
               font=F_SANS_B(10), fill=(255, 255, 255))
        d.text((x + 20, ky + 2), "%s \u00b7 %s" % (region, topic),
               font=F_SANS_B(10), fill=INK)
        conf = "CONFIRMED \u00b7 " + src
        d.text((x + col_w - d.textlength(conf, font=F_SANS(9)), ky + 3),
               conf, font=F_SANS(9), fill=GREY)
        hy = ky + 22
        for j, ln in enumerate(wrap(d, head, F_SERIF_B(22), col_w)[:3]):
            d.text((x, hy + j * 26), ln, font=F_SERIF_B(22), fill=INK)
        nlines = len(wrap(d, head, F_SERIF_B(22), col_w)[:3])
        by = hy + nlines * 26 + 4
        for j, ln in enumerate(wrap(d, body, F_SANS(12), col_w)[:3]):
            d.text((x, by + j * 15), ln, font=F_SANS(12), fill=INK)
        d.rectangle([x, y, x + col_w, 418], outline=LINE, width=1)

    # cards (two rows of six)
    card_w = (1004 - 5 * 6) // 6
    for row in range(2):
        for i in range(6):
            num, region, topic, src, head, body, art, pin = \
                CARDS[row * 6 + i]
            x = 10 + i * (card_w + 6)
            y = 424 + row * 138
            art_small(d, art, x, y, card_w, 34)
            ky = y + 38
            d.ellipse([x, ky, x + 13, ky + 13], fill=BLUE)
            t = str(num)
            d.text((x + 6.5 - d.textlength(t, font=F_SANS_B(9)) / 2, ky + 1),
                   t, font=F_SANS_B(9), fill=(255, 255, 255))
            d.text((x + 17, ky + 1), "%s \u00b7 %s" % (region, topic),
                   font=F_SANS_B(9), fill=INK)
            d.text((x, ky + 14), "CONFIRMED \u00b7 " + src, font=F_SANS(8),
                   fill=GREY)
            hy = y + 64
            for j, ln in enumerate(wrap(d, head, F_SANS_B(13), card_w)[:2]):
                d.text((x, hy + j * 16), ln, font=F_SANS_B(13), fill=INK)
            by = hy + 32
            for j, ln in enumerate(wrap(d, body, F_SANS(10), card_w)[:3]):
                d.text((x, by + j * 12), ln, font=F_SANS(10), fill=INK)
            d.rectangle([x, y, x + card_w, y + 132], outline=LINE, width=1)
    d.line([10, 698, W - 10, 698], fill=LINE, width=1)

    # bottom: map + also-on
    d.text((10, 702), "WHERE IT HAPPENED", font=F_SANS_B(14), fill=RED)
    d.text((10, 718), "Schematic map - not to scale", font=F_SANS(9),
           fill=GREY)
    # nudge clustered pins apart (dx, dy in pixels)
    nudge = {3: (0, -4), 15: (-8, 6), 16: (8, 10), 11: (8, -8)}
    pins = [(n, lo, la) + nudge.get(n, (0, 0)) for (n, lo, la, _, _) in
            [(c[0], c[7][0], c[7][1], 0, 0) for c in CARDS] +
            [(l[0], l[7][0], l[7][1], 0, 0) for l in LEADS]]
    mx0, my0, mw, mh = 10, 732, 320, 180
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(238, 232, 214),
                outline=LINE)
    def proj(lon, lat):
        return (mx0 + (lon + 170) / 360 * mw, my0 + (75 - lat) / 130 * mh)
    for poly in CONTINENTS.values():
        d.polygon([proj(lo, la) for lo, la in poly], fill=MAP_FILL,
                  outline=MAP_LINE)
    for num, lon, lat, dx, dy in pins:
        px, py = proj(lon, lat)
        px, py = px + dx, py + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=BLUE,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        d.text((px - d.textlength(t, font=F_SANS_B(8)) / 2, py - 5), t,
               font=F_SANS_B(8), fill=(255, 255, 255))
    lx = 10
    for label, col in [("Europe", BLUE), ("Mid East", (140, 90, 40)),
                       ("Asia", RED), ("Americas", (40, 120, 60)),
                       ("Africa", (20, 90, 60)), ("Oceania", (0, 130, 130))]:
        d.rectangle([lx, 930, lx + 8, 938], fill=col)
        d.text((lx + 11, 928), label, font=F_SANS(9), fill=INK)
        lx += 11 + d.textlength(label, font=F_SANS(9)) + 8

    # also-on list
    ax = 338
    d.text((ax, 702), "ALSO ON FRIDAY 20 NOVEMBER", font=F_SANS_B(15),
           fill=RED)
    col1 = ALSO[:16]
    col2 = ALSO[16:]
    for col_i, col in enumerate((col1, col2)):
        cx = ax + col_i * 340
        for j, (num, city, text) in enumerate(col):
            yy = 722 + j * 14
            d.text((cx, yy), str(num), font=F_SANS_B(11), fill=RED)
            line = "%s: %s" % (city, text)
            line = fit_one_line(d, line, F_SANS(10),
                                (340 - 24) if col_i == 0 else (1014 - cx - 24))
            d.text((cx + 24, yy), line, font=F_SANS(10), fill=INK)
    d.line([10, 946, W - 10, 946], fill=LINE, width=1)

    # date check
    d.rectangle([10, 948, 118, 986], fill=RED)
    d.text((16, 961), "DATE CHECK", font=F_SANS_B(11), fill=(255, 255, 255))
    for j, ln in enumerate(wrap(d, DATE_CHECK, F_SANS(10), 1014 - 126)):
        d.text((126, 950 + j * 12), ln, font=F_SANS(10), fill=INK)
    for j, ln in enumerate(wrap(d, SOURCES, F_SANS(9), 1004)):
        d.text((10, 990 + j * 12), ln, font=F_SANS(9), fill=GREY)
    return img


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out, exist_ok=True)
    img = render()
    img.save(os.path.join(out, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
