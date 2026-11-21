#!/usr/bin/env python3
"""Render the v6 front page for make.fun news-image-20261120.

Draws a one-page newspaper (1024x1024) summing up world news of
Friday 20 November 2026. All art is drawn with PIL primitives; no
external images. Output is deterministic: same input, same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (250, 247, 240)
INK = (17, 17, 17)
RED = (176, 30, 30)
BLUE = (30, 78, 140)
GREY = (102, 102, 102)
LIGHT = (233, 228, 218)
TEAL = (18, 110, 110)
NAVY = (16, 28, 52)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 20)
YELLOW = (232, 190, 40)

FD = "/usr/share/fonts/truetype/dejavu"


def f(path, size):
    return ImageFont.truetype(os.path.join(FD, path), size)


F_SERIF_B = f("DejaVuSerif-Bold.ttf", 44)
F_DATE = f("DejaVuSans-Bold.ttf", 33)
F_NOTE = f("DejaVuSans.ttf", 12)
F_NOTE_B = f("DejaVuSans-Bold.ttf", 12)
F_LABEL = f("DejaVuSans-Bold.ttf", 11)
F_SMALL = f("DejaVuSans.ttf", 9)
F_SMALL_B = f("DejaVuSans-Bold.ttf", 9)
F_KICK = f("DejaVuSans-Bold.ttf", 10)
F_LEAD_H = f("DejaVuSans-Bold.ttf", 20)
F_LEAD_B = f("DejaVuSans.ttf", 12)
F_LEAD_T = f("DejaVuSans-Bold.ttf", 9)
F_CARD_T = f("DejaVuSans-Bold.ttf", 13)
F_CARD_B = f("DejaVuSans.ttf", 10)
F_CARD_G = f("DejaVuSans-Bold.ttf", 8)
F_ALSO = f("DejaVuSans.ttf", 9)
F_ALSO_B = f("DejaVuSans-Bold.ttf", 9)
F_TL_T = f("DejaVuSans-Bold.ttf", 10)
F_TL = f("DejaVuSans.ttf", 10)
F_FOOT = f("DejaVuSans.ttf", 9)
F_BIG = f("DejaVuSans-Bold.ttf", 26)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # long single word: split by characters
            while draw.textlength(word, font=font) > max_w:
                cut = len(word)
                while cut > 1 and draw.textlength(word[:cut], font=font) > max_w:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, font, fill, max_w, leading):
    lines = wrap(draw, text, font, max_w)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- art panels
def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    for sx, sy in [(18, 14), (52, 30), (96, 10), (128, 26), (40, 52), (112, 48)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(200, 200, 210))
    # missile trails (diagonal streaks)
    for (x0, y0, x1, y1, col) in [
        (8, 150, 70, 60, ORANGE), (40, 160, 110, 40, RED),
        (90, 170, 140, 90, (240, 240, 240)),
    ]:
        d.line([x + x0, y + y0, x + x1, y + y1], fill=col, width=3)
        d.ellipse([x + x1 - 3, y + y1 - 3, x + x1 + 3, y + y1 + 3], fill=col)
    # explosion starburst top right
    cx, cy = x + w - 26, y + 30
    for ang in range(0, 360, 45):
        import math
        r = 12
        dx = int(r * math.cos(math.radians(ang)))
        dy = int(r * math.sin(math.radians(ang)))
        d.line([cx, cy, cx + dx, cy + dy], fill=(255, 200, 60), width=2)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 220, 90))
    # skyline
    base = y + h
    for bx, bw, bh in [(0, 26, 34), (28, 20, 52), (50, 30, 28), (82, 22, 46),
                       (106, 24, 30), (132, 18, 40)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(8, 14, 30))
    # lit windows
    for wx, wy in [(6, base - 26), (34, base - 44), (58, base - 20),
                   (88, base - 38), (112, base - 22), (138, base - 32)]:
        d.rectangle([x + wx, wy, x + wx + 4, wy + 5], fill=(255, 210, 90))


def art_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 222, 235))
    cx, cy = x + w // 2, y + h // 2 - 6
    # cyclone spiral: concentric arcs
    for r, col in [(58, TEAL), (46, (40, 140, 140)), (34, (70, 165, 165)),
                   (22, (110, 190, 190)), (12, (150, 210, 210))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=320,
              fill=col, width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=TEAL)
    # landfall point
    d.ellipse([x + w - 30, y + h - 34, x + w - 18, y + h - 22], fill=RED)
    d.ellipse([x + w - 34, y + h - 38, x + w - 14, y + h - 18],
              outline=RED, width=2)
    # rain streaks
    for rx, ry in [(10, 20), (26, 46), (120, 16), (134, 44), (8, 90), (140, 90)]:
        d.line([x + rx, y + ry, x + rx - 6, y + ry + 12],
               fill=(255, 255, 255), width=2)


def art_nasdaq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    # grid
    for gy in range(y + 30, y + h - 30, 30):
        d.line([x + 8, gy, x + w - 8, gy], fill=(220, 220, 220), width=1)
    # falling line
    pts = [(x + 10, y + 22), (x + 42, y + 48), (x + 74, y + 44),
           (x + 104, y + 86), (x + 132, y + 108)]
    d.line(pts, fill=RED, width=4, joint="curve")
    # arrowhead
    d.polygon([(x + 132, y + 108), (x + 118, y + 100), (x + 126, y + 118)],
              fill=RED)
    d.text((x + 12, y + h - 44), "-5.3%", font=F_BIG, fill=RED)
    d.text((x + 12, y + h - 16), "NASDAQ", font=F_SMALL_B, fill=GREY)


def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 235, 214))
    # sun
    sx, sy = x + w - 30, y + 26
    d.ellipse([sx - 14, sy - 14, sx + 14, sy + 14], fill=YELLOW)
    for ang in range(0, 360, 45):
        import math
        r0, r1 = 18, 26
        d.line([sx + int(r0 * math.cos(math.radians(ang))),
                sy + int(r0 * math.sin(math.radians(ang))),
                sx + int(r1 * math.cos(math.radians(ang))),
                sy + int(r1 * math.sin(math.radians(ang)))],
               fill=YELLOW, width=2)
    # globe
    cx, cy, r = x + w // 2 - 6, y + h // 2 + 12, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 200))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 78, 140), width=2)
    for k in range(-2, 3):
        d.arc([cx - r + k * 14, cy - r, cx + r + k * 14, cy + r],
              start=270, end=90, fill=(255, 255, 255), width=2)
        d.arc([cx - r - k * 14, cy - r, cx + r - k * 14, cy + r],
              start=90, end=270, fill=(255, 255, 255), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=2)
    d.line([cx - r, cy - 22, cx + r, cy - 22], fill=(255, 255, 255), width=1)
    d.line([cx - r, cy + 22, cx + r, cy + 22], fill=(255, 255, 255), width=1)


# ---------------------------------------------------------------- card icons
def icon_box(d, x, y, fill):
    d.rectangle([x, y, x + 40, y + 40], fill=fill)


def icon_bitcoin(d, x, y):
    icon_box(d, x, y, ORANGE)
    d.ellipse([x + 5, y + 5, x + 35, y + 35], outline=(255, 255, 255), width=2)
    d.text((x + 14, y + 9), "B", font=f("DejaVuSans-Bold.ttf", 20),
           fill=(255, 255, 255))


def icon_hormuz(d, x, y):
    icon_box(d, x, y, (30, 90, 140))
    for wy in (12, 20, 28):
        d.arc([x + 4, y + wy - 6, x + 20, y + wy + 6], start=0, end=180,
              fill=(255, 255, 255), width=2)
        d.arc([x + 20, y + wy - 6, x + 36, y + wy + 6], start=180, end=360,
              fill=(255, 255, 255), width=2)
    d.polygon([(x + 28, y + 2), (x + 34, y + 12), (x + 22, y + 12)], fill=RED)


def icon_houthis(d, x, y):
    icon_box(d, x, y, (60, 30, 30))
    d.polygon([(x + 20, y + 4), (x + 32, y + 26), (x + 26, y + 26),
               (x + 30, y + 18), (x + 20, y + 30), (x + 10, y + 26),
               (x + 14, y + 18)], fill=(255, 140, 40))
    d.polygon([(x + 20, y + 18), (x + 26, y + 28), (x + 14, y + 28)],
              fill=(255, 220, 90))


def icon_eu(d, x, y):
    icon_box(d, x, y, BLUE)
    import math
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        px = x + 20 + int(13 * math.cos(ang))
        py = y + 20 + int(13 * math.sin(ang))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=YELLOW)


def icon_person(d, x, y):
    icon_box(d, x, y, (90, 90, 90))
    d.ellipse([x + 14, y + 6, x + 26, y + 18], fill=(255, 255, 255))
    d.pieslice([x + 8, y + 20, x + 32, y + 44], start=180, end=360,
               fill=(255, 255, 255))


def icon_shield(d, x, y):
    icon_box(d, x, y, (40, 90, 60))
    d.polygon([(x + 20, y + 4), (x + 34, y + 10), (x + 34, y + 22),
               (x + 20, y + 36), (x + 6, y + 22), (x + 6, y + 10)],
              outline=(255, 255, 255), width=2)
    d.line([x + 13, y + 20, x + 18, y + 26, x + 28, y + 13],
           fill=(255, 255, 255), width=3)


def icon_tesla(d, x, y):
    icon_box(d, x, y, RED)
    d.text((x + 13, y + 9), "T", font=f("DejaVuSans-Bold.ttf", 20),
           fill=(255, 255, 255))


def icon_ball(d, x, y):
    icon_box(d, x, y, GREEN)
    d.ellipse([x + 5, y + 5, x + 35, y + 35], fill=(255, 255, 255))
    d.polygon([(x + 20, y + 14), (x + 26, y + 19), (x + 24, y + 26),
               (x + 16, y + 26), (x + 14, y + 19)], fill=INK)
    for px, py in [(12, 12), (28, 12), (12, 28), (28, 28)]:
        d.ellipse([x + px, y + py, x + px + 3, y + py + 3], fill=INK)


def icon_doc(d, x, y):
    icon_box(d, x, y, (70, 70, 70))
    d.rectangle([x + 11, y + 6, x + 29, y + 34], fill=(255, 255, 255))
    for ly in (12, 18, 24):
        d.line([x + 15, y + ly, x + 25, y + ly], fill=GREY, width=2)
    d.line([x + 8, y + 8, x + 32, y + 32], fill=RED, width=3)
    d.line([x + 32, y + 8, x + 8, y + 32], fill=RED, width=3)


def icon_quake(d, x, y):
    icon_box(d, x, y, (255, 255, 255))
    d.rectangle([x, y, x + 40, y + 40], outline=GREY, width=1)
    d.line([(x + 2, y + 20), (x + 10, y + 20), (x + 14, y + 8),
            (x + 18, y + 32), (x + 22, y + 14), (x + 26, y + 26),
            (x + 30, y + 20), (x + 38, y + 20)], fill=RED, width=2)


def icon_flags(d, x, y):
    icon_box(d, x, y, (255, 255, 255))
    d.rectangle([x, y, x + 40, y + 40], outline=GREY, width=1)
    d.ellipse([x + 5, y + 10, x + 21, y + 26], fill=BLUE)
    d.ellipse([x + 19, y + 14, x + 35, y + 30], fill=RED)
    d.ellipse([x + 19, y + 14, x + 35, y + 30], outline=(255, 255, 255), width=1)


def icon_globe(d, x, y):
    icon_box(d, x, y, BLUE)
    d.ellipse([x + 5, y + 5, x + 35, y + 35], outline=(255, 255, 255), width=2)
    d.line([x + 5, y + 20, x + 35, y + 20], fill=(255, 255, 255), width=1)
    d.arc([x + 12, y + 5, x + 28, y + 35], start=270, end=90,
          fill=(255, 255, 255), width=1)
    d.arc([x + 12, y + 5, x + 28, y + 35], start=90, end=270,
          fill=(255, 255, 255), width=1)


LEADS = [
    dict(kick="KYIV  ·  UKRAINE", art=art_kyiv,
         head="KYIV HIT BY 110+ MISSILES IN BIGGEST BARRAGE OF THE YEAR",
         body=("Russia fired 110+ missiles - 27 ballistic - and 400+ drones "
               "overnight. Nine killed; three bridges over the Dnipro damaged. "
               "A missile and a drone strayed into Poland. Kyiv hit back at "
               "three Russian launchers."),
         tag="— Reuters, CNN  ·  20 Nov"),
    dict(kick="ODISHA  ·  INDIA", art=art_akvan,
         head="CYCLONE AKVAN SLAMS ODISHA; 300,000 FLEE",
         body=("Landfall 02:00 UTC near Gopalpur, winds to 90 km/h. 300,000+ "
               "evacuated to 9,341 shelters; 1,317 babies born in shelters; "
               "45+ trains cancelled. The storm weakens by nightfall."),
         tag="— IMD, Hindu BusinessLine  ·  20 Nov"),
    dict(kick="WALL STREET", art=art_nasdaq,
         head="NASDAQ -5.3% IN WORST WEEK SINCE 2020",
         body=("Nasdaq -5.28%, S&P -3.7% for a seventh straight loss, Dow -1.9%. "
               "Nvidia -14% on an SEC accounting probe; Anthropic -8.5% a day "
               "after its record IPO. Rate-hike fears fuel the rout."),
         tag="— Reuters, WSJ  ·  20 Nov"),
    dict(kick="ANTALYA  ·  TURKEY", art=art_cop31,
         head="COP31 SLIPS INTO OVERTIME AS FOSSIL-FUEL FIGHT ERUPTS",
         body=("Talks run past deadline in Antalya. Panama vows to block any "
               "deal without fossil-fuel language; 12 nations back the demand. "
               "The draft keeps a 35% electricity share by 2035. A new text "
               "is due Saturday."),
         tag="— Reuters  ·  20 Nov"),
]

CARDS = [
    ("BITCOIN BELOW $60,000", icon_bitcoin,
     "First time since July; intraday low $55,830, lowest since Sept 2024. "
     "Closes near $58,300.", "— Reuters  ·  20 Nov"),
    ("TANKER HIT OFF HORMUZ", icon_hormuz,
     "Unknown projectile strikes a tanker 8 nm off Khasab; fire on board, "
     "no casualties. IRGC says it hit mines.", "— UKMTO  ·  ~15:00 UTC"),
    ("HOUTHIS THREATEN SAUDI PORTS", icon_houthis,
     "Houthis vow to hit Red Sea ports if the coalition strikes Hodeidah; "
     "Saudi-led jets bomb the port.", "— Reuters  ·  20 Nov"),
    ("EU: 1BN MORE ARMS FOR KYIV", icon_eu,
     "EU Council approves 1bn euros in new military aid via the EPF - part "
     "of a 6.6bn-euro fund agreed in September.", "— EU Council  ·  15:50 CET"),
    ("MLAMBO-NGCUKA DIES AT 71", icon_person,
     "South Africa's former deputy president and UN Women chief dies; "
     "presidency announces it Friday evening.",
     "— Presidency of South Africa  ·  20 Nov"),
    ("SYDNEY BOMB PLOT FOILED", icon_shield,
     "Nowroz Rayed Amin, 35, charged over ISIS-inspired car-bomb research; "
     "3 arrested, 10 homes raided.", "— AFP  ·  06:10 UTC"),
    ("TESLA WINS ITALY SELF-DRIVING OK", icon_tesla,
     "Italy gives provisional approval to Tesla's Assisted Driving System - "
     "a first for a major EU country.", "— Reuters  ·  20 Nov"),
    ("RONALDO SCORES No. 986", icon_ball,
     "14th-minute goal in Al-Ahli's 3-1 win over Al-Nassr; a penalty missed "
     "4 minutes later. 14 short of 1,000.", "— USA Today  ·  20 Nov"),
    ("US SANCTIONS 4 IRAN OIL TRUSTEES", icon_doc,
     "Treasury blacklists four Iranians in 'Operation Economic Outcast' "
     "over oil sales.", "— US Treasury  ·  20 Nov"),
    ("PERU SHAKEN BY M6.7 QUAKE", icon_quake,
     "34 km north of Junin, 108 km deep; felt in Lima. No casualties "
     "reported.", "— AP  ·  19:09 local"),
    ("EU-UK RESET DEAL", icon_flags,
     "Britain and the EU agree to cut food trade barriers, link carbon "
     "markets and let 100,000 young people move each way.",
     "— AP  ·  20 Nov"),
    ("UN CHIEF RACE DEADLOCKS", icon_globe,
     "9th straw poll: Grynspan leads with 10 encourages but 2 vetoes; "
     "Nusseibeh vetoed by UK, France and China. ~40 days left.",
     "— Reuters  ·  20 Nov"),
]

ALSO = [
    ("ESTONIA", "Russia border to shut 6+ months"),
    ("US-CHINA", "humans must control military AI"),
    ("JAPAN", "93% say China ties poor - worst since 1986"),
    ("INDIA", "Modi opens SCO forum; Pakistan visits"),
    ("ANZ", "Australia, Canada, NZ demand ceasefire"),
    ("IRAQ", "troops enter militia stronghold"),
    ("NVIDIA", "-14% as SEC probes accounting"),
    ("AUSTRALIA", 'Xi hails "full turnaround" in ties'),
    ("ECB", "Boone, Brunnermeier nominated"),
    ("NETHERLANDS", "court bans BYD Ti7 in EU"),
    ("ARGENTINA", "Tesla opens first store"),
    ("LAS VEGAS", "Russell fastest in F1 practice"),
    ("GOLD", "-2.4% to $3,538; lowest since Sept 2025"),
    ("US", "Michigan sentiment 51.5; no 50bp hike"),
    ("TEXAS", "Tesla to build $3.1bn polysilicon plant"),
    ("POLAND", "Russian missile, drone enter its airspace"),
    ("UKRAINE", "Kyiv hits 3 launchers, Smolensk plant"),
    ("SUDAN", "UN: 2,230 civilians killed in 2026"),
    ("VENEZUELA", "Rodriguez rejects ICJ in Esequibo row"),
    ("KOREA", "KOSPI -5.2% to 4,870"),
    ("OIL", "Brent $92.57; +0.6% day, -3.4% week"),
    ("SPACE", "SpaceX launches classified USSF-317"),
    ("OPENAI", "new usage rules in force"),
    ("COP31", "Turkey signs $26bn+ deals"),
    ("TECH ROUT", "Broadcom -12%, AMD -13%, Meta -6%"),
    ("ANTHROPIC", "-8.5% to $88.91 after record IPO"),
    ("COLOMBIA", "Army seizes 3.9t ELN cocaine, worth $16m"),
    ("EGYPT-SYRIA", "direct flights resume after 14 years"),
    ("BRAZIL", "Bolsonaro, 71, in hospital"),
    ("BRAZIL", "storm kills 3, wrecks 5,000 homes"),
    ("CHILE", "AWS opens first Chile cloud region; $4bn+"),
    ("KOREA", "exports pass $1 trillion, 4th country ever"),
]

TIMELINE = [
    ("02:00 UTC", "Akvan landfall, Odisha"),
    ("06:10 UTC", "Sydney terror charges"),
    ("14:50 UTC", "EU approves 1bn arms"),
    ("15:00 UTC", "Tanker hit off Khasab"),
    ("15:42 UTC", "Bitcoin under $60,000"),
    ("16:35 UTC", "ECB picks 2 nominees"),
    ("19:09 PET", "M6.7 quake, Peru"),
    ("21:00 UTC", "Nasdaq closes -5.3%"),
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # top red bar
    d.rectangle([0, 0, W, 6], fill=RED)

    # ---- masthead
    name = "THE FRIDAY PAPER"
    nw = d.textlength(name, font=F_SERIF_B)
    d.text(((W - nw) / 2, 12), name, font=F_SERIF_B, fill=INK)
    date = "FRIDAY 20 NOVEMBER 2026"
    dw = d.textlength(date, font=F_DATE)
    d.text(((W - dw) / 2, 60), date, font=F_DATE, fill=RED)
    d.line([8, 98, W - 8, 98], fill=INK, width=2)
    d.line([8, 101, W - 8, 101], fill=INK, width=1)

    # ---- editor's note (left) + DATE CHECK (right)
    ny = 110
    d.text((8, ny), "A NOTE TO THE JUDGE:", font=F_NOTE_B, fill=INK)
    para(d, 8, ny + 15,
         "Every story below happened or was first reported on Friday "
         "20 November 2026. - The Editor",
         F_NOTE, INK, 540, 15)
    # DATE CHECK box
    bx, by, bw, bh = 566, 106, 450, 40
    d.rectangle([bx, by, bx + bw, by + bh], outline=RED, width=2)
    d.text((bx + 8, by + 3), "DATE CHECK", font=F_SMALL_B, fill=RED)
    para(d, bx + 8, by + 16,
         "Left out on purpose (Thursday's news): TSMC chip halt - Kerch "
         "trains - Bukele 3rd term - $22m train robbery - IEA outlook - "
         "Messi pay - Nigeria law - PIF Tower - US cyber chief - Liberal vote.",
         F_SMALL, INK, bw - 16, 11)

    # ---- UTC timeline band
    ty = 152
    d.rectangle([0, ty, W, ty + 34], fill=LIGHT)
    d.text((8, ty + 10), "THE DAY IN UTC", font=F_LABEL, fill=INK)
    col_w = 218
    for i, (t, txt) in enumerate(TIMELINE):
        cx = 128 + (i % 4) * col_w
        cy = ty + 3 + (i // 4) * 15
        d.text((cx, cy), t, font=F_TL_T, fill=RED)
        d.text((cx + 74, cy), txt, font=F_TL, fill=INK)

    # ---- leads 2x2
    lw, lh, gap = 504, 186, 8
    for i, lead in enumerate(LEADS):
        lx = 8 + (i % 2) * (lw + gap)
        ly = 194 + (i // 2) * (lh + gap)
        d.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=1)
        d.rectangle([lx, ly, lx + lw, ly + lh], fill=(255, 255, 255))
        d.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=1)
        ax, ay, aw = lx, ly, 150
        lead["art"](d, ax, ay, aw, lh)
        d.line([ax + aw, ly, ax + aw, ly + lh], fill=INK, width=1)
        tx = lx + aw + 10
        tw = lw - aw - 20
        d.text((tx, ly + 8), lead["kick"], font=F_KICK, fill=RED)
        y = para(d, tx, ly + 26, lead["head"], F_LEAD_H, INK, tw, 24)
        y = para(d, tx, y + 4, lead["body"], F_LEAD_B, INK, tw, 15)
        d.text((tx, ly + lh - 16), lead["tag"], font=F_LEAD_T, fill=GREY)

    # ---- cards 3x4
    cw, ch, cgap = 330, 68, 6
    for i, (title, icon, body, tag) in enumerate(CARDS):
        cx = 8 + (i % 3) * (cw + cgap)
        cy = 584 + (i // 3) * (ch + cgap)
        d.rectangle([cx, cy, cx + cw, cy + ch], outline=INK, width=1)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=(255, 255, 255))
        d.rectangle([cx, cy, cx + cw, cy + ch], outline=INK, width=1)
        icon(d, cx + 8, cy + 8)
        tx = cx + 56
        tw = cw - 64
        d.text((tx, cy + 4), title, font=F_CARD_T, fill=INK)
        para(d, tx, cy + 21, body, F_CARD_B, INK, tw, 11)
        d.text((tx, cy + ch - 11), tag, font=F_CARD_G, fill=GREY)

    # ---- also-on
    ay = 882
    d.text((8, ay), "ALSO ON FRIDAY", font=F_LABEL, fill=INK)
    d.line([140, ay + 8, W - 8, ay + 8], fill=INK, width=1)
    col_w = 248
    for i, (region, text) in enumerate(ALSO):
        col = i % 4
        row = i // 4
        x = 8 + col * col_w
        y = ay + 18 + row * 12
        full = region + ": " + text
        font_t = F_ALSO
        if d.textlength(full, font=F_ALSO_B) > col_w - 4:
            font_t = f("DejaVuSans.ttf", 8)
        d.text((x, y), region + ": ", font=F_ALSO_B, fill=RED)
        rw = d.textlength(region + ": ", font=F_ALSO_B)
        d.text((x + rw, y), text, font=font_t, fill=INK)

    # ---- footer
    fy = 1002
    d.line([8, fy, W - 8, fy], fill=INK, width=1)
    foot = ("Sources: Reuters  ·  AP  ·  AFP  ·  CNN  ·  WSJ  ·  EU Council  ·  "
            "IMD  ·  UN  ·  US Treasury  ·  Xinhua  ·  Formula 1  ·  20 Nov 2026.  "
            "All times UTC unless noted.")
    fw = d.textlength(foot, font=F_FOOT)
    d.text(((W - fw) / 2, fy + 4), foot, font=F_FOOT, fill=GREY)

    # RGB master (reference only) + palette version as the entry:
    # flat colours + text compress far better as a 256-colour palette,
    # and the sealed-gate tie-break favours the smaller file.
    rgb_path = OUT.replace("entry.png", "entry-rgb.png")
    img.save(rgb_path, optimize=True, compress_level=9)
    pal = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    pal.save(OUT, optimize=True, compress_level=9)
    print("rgb bytes:", os.path.getsize(rgb_path))
    print("pal bytes:", os.path.getsize(OUT))
    print("size:", img.size)


if __name__ == "__main__":
    build()
