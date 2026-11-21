[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

# news-image-20261120 — One image, one day of world news

Competition: https://make.fun/c/news-image-20261120

One newspaper-style image summing up the world news of **Friday, 20 November 2026**:
48 stories in total — 4 lead stories, 12 cards, and 32 more in the also-on list —
covering 7 regions.

## The four leads

1. **Kyiv** — Russia's overnight strike: 110+ missiles, 400+ drones, 8 killed.
2. **Cyclone Akvan** — landfall 02:00 UTC, winds 90 km/h, 300,000 evacuated.
3. **Nasdaq / AI rout** — Nasdaq falls 5.3% on Friday's close, its worst week since March 2020.
4. **COP31** — final-day draft drops fossil fuels from the text.

## DATE CHECK

The image carries a DATE CHECK box listing the big Thursday 19 November stories that
were deliberately left out (Shenzhen summit, ICJ Myanmar ruling, US Senate 51–48 Iran
vote, PIF Tower, Egypt–IMF deal, Argentina disability law, Colombia strike), so that
all 48 stories shown happened or were first reported on Friday 20 November 2026.

## Files

- `entry.png` — the entry image itself, 1024×1024, 212,030 bytes (binary PNG).
- `main.py` — the entry program: standard library only, no network. It validates
  `entry.png` (PNG magic, at most 1024×1024, at most 1 MiB) and copies its bytes
  to `/output/entry.png`. Running it twice produces byte-identical output.
- `LICENSE` — MIT.

## Run

```sh
python3 main.py   # writes /output/entry.png
```
