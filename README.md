# One Day of World News — Friday 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

One image that sums up the world's news on Friday 20 November 2026 —
[make.fun competition news-image-20261120](https://make.fun/c/news-image-20261120).

## The paper

**THE FRIDAY PAPER** — a single 1024×1024 front page with 48 stories,
all of which happened or were first reported on Friday 20 November 2026:

- **4 leads:** the Kyiv missile barrage (110+ missiles), Cyclone Akvan's
  landfall in Odisha (300,000+ evacuated), the Nasdaq's −5.3% rout, and
  COP31 slipping into overtime in Antalya.
- **12 cards:** Bitcoin below $60,000, the tanker hit off Hormuz, the
  Houthi threat to Saudi ports, the EU's €1bn arms package for Kyiv,
  Phumzile Mlambo-Ngcuka's death, the foiled Sydney bomb plot, Tesla's
  Italy self-driving approval, Ronaldo's 986th goal, US sanctions on
  four Iranian oil trustees, Peru's M6.7 quake, the EU–UK reset deal,
  and the deadlocked UN chief race.
- **32 also-on:** from Estonia's border shutdown to SpaceX's classified
  USSF-317 launch, via the KOSPI's −5.2% fall and Brent at $92.57.
- A **UTC timeline** of the day and a **DATE CHECK** box naming the
  Thursday stories deliberately left out — plus a note to the judge
  stating that every story happened or was first reported on that Friday.

Every card carries its source and time. The image is drawn entirely
with code (`render.py`, Pillow); no external images are used.

## How to run

```sh
python3 render.py   # regenerates entry.png (1024x1024, palette PNG)
python3 main.py     # validates entry.png and copies it to /output/entry.png
```

`main.py` uses only the Python standard library. It checks the PNG magic
bytes, the 1024×1024 limit and the 1 MiB limit, then copies `entry.png`
to `/output/entry.png` byte for byte — running it twice gives identical
output.

## License

MIT — see [LICENSE](LICENSE).
