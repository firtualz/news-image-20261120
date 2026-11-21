#!/usr/bin/env python3
"""Render the news-image-20261120 entry: one 1024x1024 front page that sums
up Friday 20 November 2026 in 48 stories. Drawn from scratch with Pillow;
every story was checked against reporting dated 20 Nov 2026 (or labelled
with its real day where it is Thursday news kept as a small dated card).

Usage: python3 render.py V-A   (variants V-A .. V-E, see VARIANTS below)
Writes entry-<variant>.png next to this file.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 222)
PAPER = (252, 248, 235)
INK = (26, 26, 26)
GREY = (90, 86, 76)
RED = (178, 38, 30)
NAVY = (31, 58, 95)
BLUE = (46, 92, 168)
AMBER = (176, 118, 20)
GREEN = (46, 125, 70)
TEAL = (14, 130, 130)
PURPLE = (110, 70, 150)
BROWN = (140, 82, 40)
LINE = (180, 170, 140)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = FD + "DejaVuSerif-Bold.ttf"
SERIF_R = FD + "DejaVuSerif.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start, width):
    """Largest font size (<= start) at which text fits in width."""
    size = start
    while size > 8:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= width:
            return fnt
        size -= 1
    return font(path, 8)


REGION_COLOR = {
    "EUROPE": BLUE, "MIDDLE EAST": BROWN, "ASIA": RED, "AMERICAS": PURPLE,
    "AFRICA": GREEN, "OCEANIA": TEAL, "GLOBAL": NAVY,
}

# ---------------------------------------------------------------- stories
# n: number on the page. tag: CONFIRMED or CLAIM + source.
# art: key into the small illustration drawn for the panel/card.
# pin: (lon, lat) for the map, or None.
STORIES = {
    1: dict(region="ASIA", field="WEATHER", tag="CONFIRMED", src="IMD",
            pin=(84.9, 19.3), art="cyclone",
            title="Cyclone Akvan hits India's coast; 300,000 evacuated",
            ctitle="Cyclone Akvan hits India's coast",
            ltitle="Cyclone Akvan hits India's coast",
            lbody=("Landfall near Gopalpur 02:00 UTC, winds to 90 km/h. "
                   "300,000 evacuated; 9,341 shelters open."),
            body=("Landfall near Gopalpur 02:00 UTC, winds 70-80 km/h, gusting 90. "
                  "Odisha opened 9,341 shelters; 423 teams out; 69 trains cancelled."),
            short="Landfall near Gopalpur, winds to 90 km/h; 300,000 evacuated, 9,341 shelters open."),
    2: dict(region="EUROPE", field="UKRAINE", tag="CONFIRMED", src="CNN",
            pin=(30.5, 50.5), art="kyiv",
            title="Massive Russian barrage hits Kyiv; debris falls in Poland",
            ctitle="Huge barrage hits Kyiv; debris in Poland",
            ltitle="Russian barrage hits Kyiv",
            lbody=("110+ missiles, 400+ drones overnight; 8 killed, 28 hurt. "
                   "3 bridges hit; debris falls in Poland."),
            body=("110+ missiles, 400+ drones overnight; at least 8 killed, 28 hurt; "
                  "3 Dnipro bridges hit. 3 Russian objects entered Poland; NATO jets up."),
            short="110+ missiles, 400+ drones; 8 killed; 3 bridges hit; Russian objects land in Poland."),
    3: dict(region="GLOBAL", field="CLIMATE", tag="CONFIRMED", src="REUTERS",
            pin=(30.7, 36.9), art="cop31",
            title="COP31 draft drops fossil fuels; Panama threatens veto",
            ctitle="COP31 draft drops fossil fuels",
            ltitle="COP31 draft drops fossil fuels",
            lbody=("Final-day text omits fossil fuels; Panama threatens veto. "
                   "About 120,000 registered."),
            body=("Final-day text in Antalya omits coal, oil and gas; the $120bn adaptation "
                  "target is cut too. About 120,000 registered; talks run into Saturday."),
            short="Final-day text omits fossil fuels; Panama threatens veto; talks run into Saturday."),
    4: dict(region="GLOBAL", field="MARKETS", tag="CONFIRMED", src="TIMES",
            pin=(-74.0, 40.7), art="chart",
            title="Anthropic slides as Nasdaq falls 5.3% in worst week",
            ctitle="Anthropic slides; Nasdaq falls 5.3%",
            ltitle="Anthropic slides as Nasdaq falls",
            lbody="AI star down ~9% to near $88. Nasdaq -5.3% on Friday; -10% on the week.",
            body=("AI star down about 9% to near $88, close to its $83 IPO price. Nasdaq "
                  "down 10% on the week; Nikkei -5.1% on Friday; Nvidia -14% in a day."),
            short="AI star down ~9% to near $88. Nasdaq -10% on the week; Nikkei -5.1% on Friday."),
    5: dict(region="MIDDLE EAST", field="IRAN", tag="CONFIRMED", src="AXIOS",
            pin=(-77.0, 38.9), art="desk",
            title="Trump defers Iran decision to next year: 'I am not rushing'",
            ctitle="Trump defers Iran decision to next year",
            ltitle="Trump defers Iran decision",
            lbody="'We will see what happens after January 1,' he tells Axios and Reuters.",
            body=("No new major strikes in 2026, he tells Axios and Reuters: 'We will see "
                  "what happens after January 1.' Senate said no to war limits 51-48 on Thursday."),
            short="'We will see what happens after January 1,' he tells Axios and Reuters."),
    6: dict(region="GLOBAL", field="GAMES", tag="CONFIRMED", src="TAKE-TWO",
            pin=(-74.0, 40.7), art="game",
            title="GTA VI makes $3.79bn in a day - biggest launch ever",
            ctitle="GTA VI makes $3.79bn in a day",
            ltitle="GTA VI makes $3.79bn in a day",
            lbody="32.5m units sold; Sensor Tower had put it at $2.36bn. Beats GTA V's $800m day.",
            body=("Take-Two reports 32.5m units sold before release day ended; Sensor Tower "
                  "had put it at $2.36bn. It beats GTA V's $800m first day in 2013."),
            short="32.5m units sold; Sensor Tower had put it at $2.36bn. Beats GTA V's $800m day."),
    7: dict(region="MIDDLE EAST", field="GULF", tag="CONFIRMED", src="REUTERS",
            pin=(46.7, 24.7), art="tower",
            title="Houthis threaten Saudi ports a day after Riyadh tower hit",
            ctitle="Houthis threaten Saudi ports",
            ltitle="Houthis threaten Saudi ports",
            lbody="Rebels warn Red Sea ports; civilians told to leave Hodeidah. Brent $92.77.",
            body=("Rebels warn Red Sea ports and airlines; the coalition tells civilians "
                  "to leave Hodeidah. Brent $92.77. Iran says two tankers hit mines - unconfirmed."),
            short="Rebels warn Red Sea ports; civilians told to leave Hodeidah. Brent $92.77."),
    8: dict(region="EUROPE", field="UKRAINE", tag="CONFIRMED", src="EU",
            pin=(4.35, 50.85), art="shield",
            title="EU gives Ukraine 1bn euros in arms aid",
            body="Joint arms buying, delivery by end 2027; part of a 6.6bn euro package."),
    9: dict(region="AFRICA", field="SOUTH AFRICA", tag="CONFIRMED", src="PRETORIA",
            pin=(28.2, -25.7), art="candle",
            title="South Africa mourns Mlambo-Ngcuka, 71",
            body="First woman deputy president and ex-UN Women chief dies; no cause given."),
    10: dict(region="OCEANIA", field="DIPLOMACY", tag="CONFIRMED", src="CANADA",
            pin=(149.1, -35.3), art="dove",
            title="Australia, Canada and NZ urge ceasefire",
            body="Joint APEC statement calls for a permanent, unconditional ceasefire now."),
    11: dict(region="OCEANIA", field="AUSTRALIA", tag="CONFIRMED", src="AFP",
            pin=(151.2, -33.9), art="siren",
            title="AFP foils alleged Sydney car-bomb plot",
            body="A 35-year-old charged with terror offences after dawn raids in the south-west."),
    12: dict(region="AMERICAS", field="BUSINESS", tag="CONFIRMED", src="REUTERS",
            pin=(-58.4, -34.6), art="car",
            title="Tesla opens first store in Argentina",
            body="Model 3 from $40,990 and Model Y from $43,990; market opens to Chinese rivals."),
    13: dict(region="AFRICA", field="ECONOMY", tag="CONFIRMED", src="IMF",
            pin=(31.2, 30.0), art="coins",
            title="Egypt's final IMF review; $2.3bn at stake",
            body="Staff deal on the $8bn programme; board vote needed before 15 Dec for the payout."),
    14: dict(region="GLOBAL", field="FOOTBALL", tag="CONFIRMED", src="SPL",
            pin=(39.2, 21.5), art="ball",
            title="Ronaldo's 986th goal as Al-Ahli win 3-1",
            body="He scores, then misses a penalty; Toney converts from the spot in the comeback."),
    15: dict(region="ASIA", field="JUSTICE", tag="CONFIRMED", src="ICJ",
            pin=(4.3, 52.1), art="gavel",
            title="ICJ: Myanmar committed genocide (Thu)",
            body="Judges rule 9-6 on the 2017 crackdown; kept small, it was Thursday's news."),
    16: dict(region="AMERICAS", field="SANCTIONS", tag="CONFIRMED", src="TREASURY",
            pin=(-77.0, 38.9), art="stamp",
            title="US sanctions 4 Iranians over oil money",
            body="Treasury names four men it says handled Iranian oil revenues; out on Friday."),
}

# The nine fixed picture cards; each variant adds the three lead stories
# it does not use as leads, for 12 cards in all.
FIXED_CARDS = [8, 9, 10, 11, 12, 13, 14, 15, 16]

# Also-on list: (place, text). Items 17-49 on the page.
ALSO = [
    ("Senate", "rejects Iran war-powers limits 51-48 (Thu)"),
    ("Shenzhen", "Trump-Xi-Putin summit, 70 min, no breakthrough (Thu)"),
    ("Riyadh", "Houthi missile hits PIF Tower, floors damaged (Thu)"),
    ("Hormuz", "Iran says 2 tankers hit mines - CLAIM, not confirmed (Thu)"),
    ("Hormuz", "tanker strike and fire reported at sea (UKMTO)"),
    ("France", "parliament adopts contested police shooting law"),
    ("Brussels", "UK-EU Brexit review summit opens"),
    ("London", "EU-UK youth mobility: ages 18-31, 100,000 places a year"),
    ("Frankfurt", "ECB board race: Boone and Brunnermeier"),
    ("Berlin", "students march against rearmament"),
    ("Buenos Aires", "Senate passes disability framework 71-0"),
    ("Bogota", "street protests against the government"),
    ("Banjul", "Gambia declares mpox outbreak"),
    ("Dakar", "dozens missing after migrant boat capsizes off Senegal"),
    ("Tunis", "activist Bensedrine jailed for 5 years"),
    ("Conakry", "Guinea-Burkina Faso tensions; RTB broadcaster banned"),
    ("Kinshasa", "fighting in east DR Congo despite truce"),
    ("Abidjan", "Cote d'Ivoire raises mining royalties to 9.5%"),
    ("Abuja", "Atiku loses court case on Tinubu eligibility"),
    ("Nairobi", "record KCSE school exams end"),
    ("Shenzhen", "Xi meets Albanese: 'complete turnaround' in ties"),
    ("Miami", "jury convicts Sanon in Haiti president killing"),
    ("Quito", "Hegseth lands in Ecuador on anti-drugs tour"),
    ("Dhaka", "UN Assembly president visits Rohingya refugees"),
    ("New York", "Indian man jailed 19+ years in US over Sikh plot"),
    ("Washington", "Trump replaces US cyber chief"),
    ("Melbourne", "AFL draft: a deep class headlines"),
    ("Doha", "India A thrash Nepal by 306 runs"),
    ("Bengaluru", "Bengaluru FC 2-0 Mumbai City, top of ISL"),
    ("London", "Price survives match darts into Grand Slam semis"),
    ("Munich", "Bayern held 1-1 by Koln"),
    ("Doha", "Morocco hit Fiji 6-0 at the U-17 World Cup"),
]

TIMELINE = [
    ("Overnight", "Russian barrage hits Kyiv; 3 bridges damaged"),
    ("~02:00 UTC", "Cyclone Akvan crosses the coast at Gopalpur"),
    ("~06:00 UTC", "Nikkei closes -5.1%; Kospi -5.2%"),
    ("~13:30 UTC", "COP31 draft drops fossil fuels; Panama threatens veto"),
    ("~18:00 UTC", "EU adopts 1bn euros in military aid for Ukraine"),
    ("Evening", "Nasdaq -5.3%; worst week since March 2020"),
]

DATE_CHECK = ("Left out on purpose (wrong day): Kenya Ebola last patient 11 Nov - Wales beat "
              "the All Blacks 14 Nov - Anthropic IPO debut 19 Nov - Shenzhen summit 19 Nov - "
              "ICJ Myanmar ruling 19 Nov. All stories here happened or were first reported "
              "Fri 20 Nov 2026. CLAIM = one side's account, not independently confirmed.")

SOURCES = ("Sources: IMD, Reuters, CNN, ISW, AP, AFP, EU Council, ICJ, IMF, US Treasury, "
           "Take-Two, Sensor Tower. Original drawings. Times are UTC unless stated.")

# Variant lead orders. Cards = FIXED_CARDS + the leads not used, in story order.
VARIANTS = {
    "V-A": [1, 2, 3, 4],
    "V-B": [2, 1, 5, 3],
    "V-C": [1, 3, 4, 2],
    "V-D": [1, 2, 6, 4],
    "V-E": [2, 3, 1, 7],
    # R-* use the same lead orders, rendered after the legibility revision
    # (bigger lead type, shorter lead bodies); the duel reads them separately
    # so the running V-* duel is not disturbed.
    "R-A": [1, 2, 3, 4],
    "R-B": [2, 1, 5, 3],
    "R-C": [1, 3, 4, 2],
    "R-D": [1, 2, 6, 4],
    "R-E": [2, 3, 1, 7],
}

# ---------------------------------------------------------------- art
# Small flat illustrations, drawn with Pillow primitives only. Each takes
# (draw, x, y, w, h) and draws inside that box.

def _sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def art_cyclone(d, x, y, w, h):
    _sky(d, x, y, w, h, (168, 200, 225), (226, 232, 235))
    cx, cy = x + w * 0.5, y + h * 0.42
    for r, col in [(46, (90, 110, 140)), (36, (240, 244, 248)),
                   (26, (90, 110, 140)), (16, (240, 244, 248))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=5)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(178, 38, 30))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 18),
               (x + w * 0.6, y + h - 26), (x + w * 0.3, y + h - 14)],
              fill=(70, 110, 90))
    for i in range(5):
        d.line([(x + 8 + i * 16, y + h - 34), (x + 4 + i * 16, y + h - 22)],
               fill=(120, 150, 190), width=2)
    d.rectangle([x + w - 52, y + h - 30, x + w - 8, y + h - 12], fill=RED)
    d.text((x + w - 50, y + h - 29), "300k", font=font(SANS_B, 11), fill=(255, 255, 255))


def art_kyiv(d, x, y, w, h):
    _sky(d, x, y, w, h, (40, 48, 70), (120, 110, 110))
    for i, bh in enumerate([52, 70, 46, 62, 40]):
        bx = x + 6 + i * (w - 12) // 5
        bw = (w - 12) // 5 - 4
        d.rectangle([bx, y + h - 22 - bh, bx + bw, y + h - 22], fill=(30, 32, 44))
        for wy in range(3):
            d.rectangle([bx + 3, y + h - 22 - bh + 6 + wy * 14, bx + bw - 3,
                         y + h - 22 - bh + 12 + wy * 14], fill=(240, 200, 90))
    d.polygon([(x, y + h - 22), (x + w * 0.5, y + h - 40), (x + w, y + h - 22),
               (x + w, y + h), (x, y + h)], fill=(60, 70, 100))
    d.line([(x, y + h - 30), (x + w, y + h - 30)], fill=(240, 240, 240), width=3)
    d.line([(x + w * 0.2, y + h - 30), (x + w * 0.2, y + h - 22)], fill=(240, 240, 240), width=2)
    d.line([(x + w * 0.55, y + h - 30), (x + w * 0.55, y + h - 22)], fill=(240, 240, 240), width=2)
    d.line([(x + w * 0.85, y + h - 30), (x + w * 0.85, y + h - 22)], fill=(240, 240, 240), width=2)
    for sx, sy, ex in [(0.12, 0.10, 0.30), (0.55, 0.06, 0.72), (0.80, 0.14, 0.92)]:
        d.line([(x + w * sx, y + h * sy), (x + w * ex, y + h * (sy + 0.22))],
               fill=(255, 170, 60), width=3)
        d.ellipse([x + w * ex - 4, y + h * (sy + 0.22) - 4,
                   x + w * ex + 4, y + h * (sy + 0.22) + 4], fill=(255, 200, 90))
    d.ellipse([x + w - 30, y + 8, x + w - 8, y + 30], outline=(255, 255, 255), width=2)
    d.text((x + w - 28, y + 12), "PL", font=font(SANS_B, 10), fill=(255, 255, 255))


def art_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, (190, 215, 190), (240, 238, 220))
    cx, cy, r = x + w * 0.5, y + h * 0.42, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 150, 200))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(31, 58, 95), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(70, 130, 70), width=7)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 110, fill=(70, 130, 70), width=7)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(31, 58, 95), width=1)
    d.ellipse([cx - r + 6, cy - r + 6, cx - r + 20, cy - r + 18], fill=(70, 130, 70))
    d.ellipse([cx + 2, cy + 8, cx + 18, cy + 22], fill=(70, 130, 70))
    d.rectangle([x + 8, y + h - 26, x + w - 8, y + h - 8], fill=(31, 58, 95))
    d.text((x + 12, y + h - 25), "35% clean power by 2035", font=font(SANS_B, 11),
           fill=(255, 255, 255))
    d.line([(x + w - 34, y + 6), (x + w - 10, y + 6)], fill=RED, width=5)
    d.text((x + 8, y + 6), "NO FOSSIL FUELS IN TEXT", font=font(SANS_B, 10), fill=RED)


def art_chart(d, x, y, w, h):
    _sky(d, x, y, w, h, (245, 240, 225), (235, 225, 205))
    d.line([(x + 8, y + 8), (x + 8, y + h - 24)], fill=INK, width=2)
    d.line([(x + 8, y + h - 24), (x + w - 8, y + h - 24)], fill=INK, width=2)
    frac = [(0.08, 0.18), (0.28, 0.26), (0.45, 0.22), (0.62, 0.44), (0.78, 0.58), (0.92, 0.80)]
    pts = [(x + w * fx, y + h * fy) for fx, fy in frac]
    d.line(pts, fill=RED, width=4, joint="curve")
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4], fill=RED)
    if h >= 50:
        d.text((x + 12, y + h - 22), "NASDAQ -5.3%  NIKKEI -5.1%",
               font=font(SANS_B, 11), fill=RED)


def art_desk(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 210, 225), (235, 232, 222))
    d.rectangle([x + w * 0.3, y + h * 0.3, x + w * 0.7, y + h * 0.62], fill=(31, 58, 95))
    d.rectangle([x + w * 0.2, y + h * 0.62, x + w * 0.8, y + h * 0.72], fill=(120, 90, 50))
    d.rectangle([x + w * 0.24, y + h * 0.72, x + w * 0.32, y + h - 8], fill=(90, 65, 35))
    d.rectangle([x + w * 0.68, y + h * 0.72, x + w * 0.76, y + h - 8], fill=(90, 65, 35))
    d.ellipse([x + w * 0.42, y + h * 0.12, x + w * 0.58, y + h * 0.3], fill=(240, 210, 180))
    d.text((x + 8, y + 6), "JAN 1", font=font(SANS_B, 16), fill=RED)
    d.text((x + w - 40, y + h - 24), "2027", font=font(SANS_B, 13), fill=NAVY)


def art_game(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 30, 50), (90, 60, 130))
    for i in range(6):
        d.rectangle([x + 10 + i * 16, y + h - 30, x + 22 + i * 16, y + h - 14],
                    fill=(240, 200, 60))
    d.polygon([(x + w * 0.58, y + 14), (x + w * 0.82, y + 14), (x + w * 0.94, y + 34),
               (x + w * 0.70, y + 34)], fill=(178, 38, 30))
    d.text((x + w * 0.60, y + 17), "VI", font=font(SANS_B, 14), fill=(255, 255, 255))
    d.text((x + 8, y + 4), "$3.79bn", font=font(SANS_B, 12), fill=(255, 255, 255))


def art_tower(d, x, y, w, h):
    _sky(d, x, y, w, h, (225, 200, 170), (240, 225, 200))
    d.rectangle([x + w * 0.42, y + 6, x + w * 0.58, y + h - 6], fill=(90, 100, 120))
    for i in range(5):
        wy = y + 8 + i * (h - 16) // 5
        d.rectangle([x + w * 0.44, wy, x + w * 0.56, wy + max(3, (h - 16) // 5 - 4)],
                    fill=(240, 200, 90))
    d.polygon([(x + w * 0.42, y + 6), (x + w * 0.5, y - 2), (x + w * 0.58, y + 6)],
              fill=(60, 70, 90))
    d.line([(x + w * 0.1, y + 20), (x + w * 0.4, y + 34)], fill=(255, 170, 60), width=3)
    if h >= 50:
        d.text((x + 8, y + h - 20), "BRENT $92.77", font=font(SANS_B, 11), fill=INK)


def art_shield(d, x, y, w, h):
    _sky(d, x, y, w, h, (210, 220, 240), (240, 240, 235))
    cx, cy = x + w * 0.5, y + h * 0.5
    s = min(1.0, h / 64.0)
    hw, hh = 22 * s, 27 * s
    d.polygon([(cx, cy - hh), (cx + hw, cy - hh * 0.6), (cx + hw, cy + hh * 0.25),
               (cx, cy + hh), (cx - hw, cy + hh * 0.25), (cx - hw, cy - hh * 0.6)],
              fill=BLUE)
    d.polygon([(cx, cy - hh), (cx + hw, cy - hh * 0.6), (cx + hw, cy + hh * 0.25),
               (cx, cy + hh), (cx - hw, cy + hh * 0.25), (cx - hw, cy - hh * 0.6)],
              outline=(255, 220, 60), width=2)
    if h >= 50:
        d.text((cx - 11, cy - 12), "1bn", font=font(SANS_B, 12), fill=(255, 255, 255))


def art_candle(d, x, y, w, h):
    _sky(d, x, y, w, h, (235, 228, 215), (245, 240, 228))
    d.rectangle([x + w * 0.44, y + h * 0.4, x + w * 0.56, y + h - 12], fill=(250, 248, 240),
                outline=GREY)
    d.ellipse([x + w * 0.47, y + h * 0.22, x + w * 0.53, y + h * 0.38], fill=(240, 180, 60))
    d.text((x + 6, y + 4), "71", font=font(SANS_B, 12), fill=GREY)


def art_dove(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 225, 235), (240, 244, 245))
    d.ellipse([x + w * 0.3, y + h * 0.42, x + w * 0.62, y + h * 0.66], fill=(255, 255, 255),
              outline=GREY)
    d.ellipse([x + w * 0.58, y + h * 0.34, x + w * 0.74, y + h * 0.52], fill=(255, 255, 255),
              outline=GREY)
    d.polygon([(x + w * 0.72, y + h * 0.42), (x + w * 0.88, y + h * 0.46),
               (x + w * 0.72, y + h * 0.52)], fill=(240, 180, 60))
    d.polygon([(x + w * 0.34, y + h * 0.44), (x + w * 0.2, y + h * 0.2),
               (x + w * 0.48, y + h * 0.4)], fill=(255, 255, 255), outline=GREY)
    d.text((x + 8, y + 6), "AUS - CAN - NZ", font=font(SANS_B, 10), fill=NAVY)


def art_siren(d, x, y, w, h):
    _sky(d, x, y, w, h, (235, 220, 210), (245, 240, 230))
    d.rectangle([x + w * 0.2, y + h * 0.45, x + w * 0.8, y + h * 0.62], fill=NAVY)
    d.rectangle([x + w * 0.42, y + h * 0.32, x + w * 0.58, y + h * 0.45], fill=RED)
    d.ellipse([x + w * 0.26, y + h * 0.62, x + w * 0.36, y + h * 0.72], fill=INK)
    d.ellipse([x + w * 0.64, y + h * 0.62, x + w * 0.74, y + h * 0.72], fill=INK)
    d.text((x + 8, y + 6), "AFP", font=font(SANS_B, 12), fill=RED)


def art_car(d, x, y, w, h):
    _sky(d, x, y, w, h, (220, 230, 235), (242, 242, 238))
    d.polygon([(x + w * 0.2, y + h * 0.6), (x + w * 0.32, y + h * 0.38),
               (x + w * 0.62, y + h * 0.38), (x + w * 0.78, y + h * 0.6)],
              fill=(178, 38, 30))
    d.rectangle([x + w * 0.16, y + h * 0.58, x + w * 0.84, y + h * 0.72], fill=(178, 38, 30))
    d.ellipse([x + w * 0.26, y + h * 0.68, x + w * 0.38, y + h * 0.8], fill=INK)
    d.ellipse([x + w * 0.62, y + h * 0.68, x + w * 0.74, y + h * 0.8], fill=INK)
    d.text((x + 8, y + 6), "1st STORE", font=font(SANS_B, 10), fill=NAVY)


def art_coins(d, x, y, w, h):
    _sky(d, x, y, w, h, (235, 228, 200), (245, 240, 225))
    r = max(6, min(16, int(h * 0.30)))
    for i, (cx, cy) in enumerate([(0.35, 0.55), (0.5, 0.45), (0.65, 0.55)]):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r, y + h * cy + r],
                  fill=(220, 180, 60), outline=(150, 110, 20), width=2)
    if h >= 50:
        d.text((x + w * 0.5 - 8, y + h * 0.45 - 7), "$", font=font(SANS_B, 13), fill=(120, 85, 10))
        d.text((x + 8, y + 6), "$2.3bn", font=font(SANS_B, 12), fill=NAVY)


def art_ball(d, x, y, w, h):
    _sky(d, x, y, w, h, (210, 235, 200), (240, 244, 235))
    cx, cy, r = x + w * 0.5, y + h * 0.5, max(8, min(22, int(h * 0.35)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=INK, width=2)
    k = r / 22.0
    d.polygon([(cx, cy - 8 * k), (cx + 8 * k, cy - 2 * k), (cx + 5 * k, cy + 8 * k),
               (cx - 5 * k, cy + 8 * k), (cx - 8 * k, cy - 2 * k)], fill=INK)
    if h >= 50:
        d.text((x + 8, y + 6), "986", font=font(SANS_B, 13), fill=RED)


def art_gavel(d, x, y, w, h):
    _sky(d, x, y, w, h, (225, 215, 200), (242, 238, 228))
    d.rectangle([x + w * 0.3, y + h * 0.3, x + w * 0.7, y + h * 0.48], fill=(120, 90, 50))
    d.rectangle([x + w * 0.47, y + h * 0.48, x + w * 0.53, y + h * 0.82], fill=(90, 65, 35))
    d.rectangle([x + w * 0.3, y + h * 0.82, x + w * 0.7, y + h * 0.9], fill=(120, 90, 50))
    d.text((x + 8, y + 6), "9-6", font=font(SANS_B, 13), fill=NAVY)


def art_stamp(d, x, y, w, h):
    _sky(d, x, y, w, h, (235, 225, 215), (245, 240, 230))
    d.rectangle([x + w * 0.28, y + h * 0.2, x + w * 0.72, y + h * 0.8], fill=(250, 248, 240),
                outline=RED, width=2)
    d.ellipse([x + w * 0.36, y + h * 0.3, x + w * 0.64, y + h * 0.58], outline=RED, width=2)
    d.text((x + w * 0.42, y + h * 0.38), "X4", font=font(SANS_B, 12), fill=RED)
    d.text((x + 8, y + 6), "OFAC", font=font(SANS_B, 11), fill=NAVY)


ART = {"cyclone": art_cyclone, "kyiv": art_kyiv, "cop31": art_cop31,
       "chart": art_chart, "desk": art_desk, "game": art_game, "tower": art_tower,
       "shield": art_shield, "candle": art_candle, "dove": art_dove,
       "siren": art_siren, "car": art_car, "coins": art_coins, "ball": art_ball,
       "gavel": art_gavel, "stamp": art_stamp}

# Coarse continent outlines (lon, lat), schematic only.
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
           (-80, 73), (-70, 62), (-55, 52), (-60, 47), (-65, 44), (-70, 42),
           (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-97, 16),
           (-94, 17), (-86, 13), (-83, 9), (-79, 9), (-81, 13), (-90, 14),
           (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-124, 40), (-124, 49),
           (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    "SA": [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
           (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
           (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35), (-52, -32),
           (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
           (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
           (-77, 8)],
    "AF": [(-6, 35), (-10, 31), (-17, 15), (-17, 12), (-12, 8), (-8, 5), (-4, 5),
           (0, 6), (6, 4), (9, 4), (9, -1), (12, -5), (13, -10), (12, -17),
           (16, -28), (20, -35), (28, -33), (33, -26), (35, -22), (40, -15),
           (40, -10), (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (43, 12),
           (40, 15), (38, 18), (37, 22), (35, 28), (33, 31), (30, 31), (25, 32),
           (20, 32), (15, 32), (11, 34), (10, 37), (0, 36)],
    "EUAS": [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50), (2, 51),
             (5, 53), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64), (13, 68),
             (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 68), (50, 69),
             (55, 68), (60, 69), (65, 69), (70, 72), (75, 73), (80, 73), (85, 74),
             (90, 75), (95, 76), (100, 77), (105, 77), (110, 74), (115, 73),
             (120, 73), (125, 72), (130, 71), (135, 71), (140, 72), (145, 72),
             (150, 70), (155, 69), (160, 69), (165, 66), (170, 66), (178, 65),
             (178, 62), (170, 60), (162, 58), (158, 53), (156, 51), (150, 59),
             (142, 59), (142, 55), (140, 50), (138, 45), (135, 43), (132, 43),
             (130, 42), (128, 38), (126, 35), (122, 32), (120, 28), (118, 25),
             (115, 22), (110, 20), (108, 18), (106, 10), (104, 9), (103, 7),
             (100, 7), (98, 10), (95, 15), (93, 18), (91, 22), (89, 22), (87, 21),
             (85, 19), (83, 17), (80, 13), (78, 8), (76, 10), (74, 15), (72, 20),
             (70, 23), (68, 25), (66, 25), (64, 25), (62, 25), (60, 25), (58, 26),
             (56, 27), (54, 27), (52, 28), (50, 29), (48, 30), (47, 30), (44, 29),
             (42, 29), (40, 31), (38, 31), (36, 36), (34, 36), (32, 36), (30, 36),
             (27, 37), (26, 38), (23, 36), (22, 37), (20, 39), (19, 42), (18, 44),
             (15, 44), (13, 45), (12, 44), (10, 44), (8, 44), (6, 43), (3, 42),
             (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    "AU": [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
           (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
           (153, -32), (153, -27), (150, -23), (146, -19), (142, -11), (142, -15),
           (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
           (118, -20)],
}

# ---------------------------------------------------------------- layout
M = 14  # outer margin


def draw_header(d, total):
    d.text((M, 6), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=font(SANS_B, 13), fill=RED)
    right = "%d STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM THIS FRIDAY" % total
    d.text((W - M - d.textlength(right, font=font(SANS_B, 13)), 6), right,
           font=font(SANS_B, 13), fill=INK)
    title = "Friday 20 November 2026"
    fnt = fit_font(d, title, SERIF, 74, W - 2 * M)
    d.text((M, 26), title, font=fnt, fill=INK)
    d.line([(M, 104), (W - M, 104)], fill=INK, width=2)


def draw_timeline(d, y):
    d.rectangle([M, y, M + 92, y + 34], fill=RED)
    d.text((M + 6, y + 3), "THE DAY", font=font(SANS_B, 12), fill=(255, 255, 255))
    d.text((M + 6, y + 17), "IN UTC", font=font(SANS_B, 12), fill=(255, 255, 255))
    x = M + 100
    slot_w = (W - M - x) // 6
    for i, (when, what) in enumerate(TIMELINE):
        sx = x + i * slot_w
        d.text((sx + 2, y + 1), when, font=font(SANS_B, 11), fill=RED)
        for j, ln in enumerate(wrap(d, what, font(SANS, 10), slot_w - 8)):
            d.text((sx + 2, y + 14 + j * 11), ln, font=font(SANS, 10), fill=INK)
        if i < 5:
            d.line([(sx + slot_w - 2, y + 2), (sx + slot_w - 2, y + 32)], fill=LINE)
    return y + 40


def tag_line(d, x, y, width, story):
    """Numbered region tag line; returns y after the line."""
    col = REGION_COLOR[story["region"]]
    n = str(story["n"])
    fnum = font(SANS_B, 12)
    nw = d.textlength(n, font=fnum) + 10
    d.ellipse([x, y - 1, x + nw - 2, y + 13], fill=col)
    d.text((x + 5, y), n, font=fnum, fill=(255, 255, 255))
    ftag = font(SANS_B, 9)
    src = "%s \u00b7 %s" % (story["tag"], story["src"])
    sw = d.textlength(src, font=font(SANS, 9))
    tag = "%s \u00b7 %s" % (story["region"], story["field"])
    avail = width - nw - 4 - sw - 8
    while d.textlength(tag, font=ftag) > avail and len(tag) > 4:
        tag = tag[:-2]
    if d.textlength("%s \u00b7 %s" % (story["region"], story["field"]), font=ftag) > avail:
        tag += "\u2026"
    d.text((x + nw + 4, y + 1), tag, font=ftag, fill=col)
    d.text((x + width - sw, y + 2), src, font=font(SANS, 9), fill=GREY)
    return y + 16


def card_tag(d, x, y, width, story):
    """Two-line tag for the small cards: badge + region, then attribution."""
    col = REGION_COLOR[story["region"]]
    n = str(story["n"])
    fnum = font(SANS_B, 11)
    nw = d.textlength(n, font=fnum) + 9
    d.ellipse([x, y - 1, x + nw - 2, y + 12], fill=col)
    d.text((x + 4, y), n, font=fnum, fill=(255, 255, 255))
    ftag = font(SANS_B, 8)
    tag = "%s \u00b7 %s" % (story["region"], story["field"])
    avail = width - nw - 4
    while d.textlength(tag, font=ftag) > avail and len(tag) > 4:
        tag = tag[:-2]
    if d.textlength("%s \u00b7 %s" % (story["region"], story["field"]), font=ftag) > avail:
        tag += "\u2026"
    d.text((x + nw + 3, y + 1), tag, font=ftag, fill=col)
    d.text((x, y + 13), "%s \u00b7 %s" % (story["tag"], story["src"]),
           font=font(SANS, 8), fill=GREY)
    return y + 24


def draw_lead(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    ART[story["art"]](d, x + 1, y + 1, w - 2, 130)
    ty = tag_line(d, x + 6, y + 134, w - 12, story)
    title = story.get("ltitle") or story["title"]
    fhead = None
    lines = []
    for size in (24, 22):
        fhead = font(SANS_B, size)
        lines = wrap(d, title, fhead, w - 12)
        if len(lines) <= 2:
            break
    lines = lines[:2]
    lh = fhead.size + 2
    for j, ln in enumerate(lines):
        d.text((x + 6, ty + j * lh), ln, font=fhead, fill=INK)
    by = ty + len(lines) * lh + 4
    fbody = font(SANS, 12)
    body = story.get("lbody") or story["body"]
    for j, ln in enumerate(wrap(d, body, fbody, w - 12)[:3]):
        d.text((x + 6, by + j * 14), ln, font=fbody, fill=(50, 48, 44))


def draw_card(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    ART[story["art"]](d, x + 1, y + 1, w - 2, 32)
    ty = card_tag(d, x + 5, y + 34, w - 10, story)
    title = story.get("ctitle") or story["title"]
    fhead = font(SANS_B, 13)
    lines = wrap(d, title, fhead, w - 10)[:3]
    for j, ln in enumerate(lines):
        d.text((x + 5, ty + j * 15), ln, font=fhead, fill=INK)
    by = ty + len(lines) * 15 + 2
    fbody = font(SANS, 10)
    body = story.get("short") or story["body"]
    for j, ln in enumerate(wrap(d, body, fbody, w - 10)[:3]):
        d.text((x + 5, by + j * 11), ln, font=fbody, fill=(50, 48, 44))


def draw_map(d, x, y, w, h, pins):
    d.text((x, y), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=RED)
    d.text((x, y + 15), "Schematic map - not to scale", font=font(SANS, 9), fill=GREY)
    mx, my, mw, mh = x, y + 30, w, h - 52
    d.rectangle([mx, my, mx + mw, my + mh], fill=(214, 228, 238), outline=LINE)
    def proj(lon, lat):
        px = mx + (lon + 170) / 360.0 * mw
        py = my + (75 - lat) / 130.0 * mh
        return (px, py)
    for poly in CONTINENTS.values():
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(232, 223, 200),
                  outline=(185, 175, 145))
    d.ellipse([proj(167, -45)[0] - 2, proj(167, -45)[1] - 2,
               proj(167, -45)[0] + 2, proj(167, -45)[1] + 2], fill=(232, 223, 200))
    d.ellipse([proj(174, -41)[0] - 2, proj(174, -41)[1] - 2,
               proj(174, -41)[0] + 2, proj(174, -41)[1] + 2], fill=(232, 223, 200))
    placed = []
    for n in pins:
        s = STORIES[n]
        if not s.get("pin"):
            continue
        px, py = proj(*s["pin"])
        for dx, dy in placed:
            if abs(px - dx) < 12 and abs(py - dy) < 12:
                px += 12
                py -= 8
        placed.append((px, py))
        col = REGION_COLOR[s["region"]]
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline=(255, 255, 255))
        t = str(n)
        d.text((px - d.textlength(t, font=font(SANS_B, 9)) / 2, py - 6), t,
               font=font(SANS_B, 9), fill=(255, 255, 255))
    ly = my + mh + 5
    lx = x
    for region, col in [("Europe", BLUE), ("Mid East", BROWN), ("Asia", RED),
                        ("Americas", PURPLE), ("Africa", GREEN), ("Oceania", TEAL)]:
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=col)
        t = region
        d.text((lx + 11, ly - 1), t, font=font(SANS, 9), fill=INK)
        lx += 11 + d.textlength(t, font=font(SANS, 9)) + 8


def draw_also(d, x, y, w, h):
    d.text((x, y), "ALSO ON FRIDAY 20 NOVEMBER", font=font(SANS_B, 13), fill=RED)
    rows = 16
    rh = (h - 22) // rows
    fitem = font(SANS, 11)
    fnum = font(SANS_B, 11)
    col_w = w // 2
    per_col = (len(ALSO) + 1) // 2
    for i, (place, text) in enumerate(ALSO):
        col = i // per_col
        row = i % per_col
        ix = x + col * col_w
        iy = y + 22 + row * rh
        num = str(17 + i)
        d.text((ix, iy), num, font=fnum, fill=RED)
        nw = d.textlength(num, font=fnum) + 5
        d.text((ix + nw, iy), place + ": ", font=fnum, fill=INK)
        pw = d.textlength(place + ": ", font=fnum)
        line = text
        cut = False
        while d.textlength(line, font=fitem) > col_w - nw - pw - 4 and " " in line:
            line = line.rsplit(" ", 1)[0]
            cut = True
        if cut:
            line += "\u2026"
        d.text((ix + nw + pw, iy), line, font=fitem, fill=(50, 48, 44))


def render(variant):
    leads = VARIANTS[variant]
    cards = sorted(FIXED_CARDS + [n for n in (1, 2, 3, 4, 5, 6, 7) if n not in leads])
    total = len(leads) + len(cards) + len(ALSO)
    for n in leads + cards:
        STORIES[n]["n"] = n
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_header(d, total)
    y = draw_timeline(d, 112)
    lw = (W - 2 * M - 3 * 8) // 4
    for i, n in enumerate(leads):
        draw_lead(d, M + i * (lw + 8), y, lw, 280, STORIES[n])
    y += 280 + 8
    cw = (W - 2 * M - 5 * 8) // 6
    ch = 140
    for r in range(2):
        for c in range(6):
            n = cards[r * 6 + c]
            draw_card(d, M + c * (cw + 8), y + r * (ch + 8), cw, ch, STORIES[n])
    y += 2 * ch + 8 + 6
    bot_h = 222
    draw_map(d, M, y, 330, bot_h, leads + cards)
    draw_also(d, M + 342, y, W - 2 * M - 342, bot_h)
    y += bot_h + 6
    d.rectangle([M, y, M + 92, y + 32], fill=RED)
    d.text((M + 6, y + 9), "DATE CHECK", font=font(SANS_B, 12), fill=(255, 255, 255))
    fdc = font(SANS, 11)
    lines = wrap(d, DATE_CHECK, fdc, W - 2 * M - 100)
    for j, ln in enumerate(lines[:2]):
        d.text((M + 100, y + 3 + j * 13), ln, font=fdc, fill=INK)
    y += 36
    d.text((M, y), SOURCES, font=font(SANS, 9), fill=GREY)
    return img


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "V-A"
    out = "entry-%s.png" % variant
    img = render(variant)
    img.save(out, optimize=True)
    print(out, img.size, "bytes:", __import__("os").path.getsize(out))
