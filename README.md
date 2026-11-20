# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/firtualz/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One 1024×1024 PNG that tells the world's day in pictures: 40 stories
(3 illustrated leads, 9 illustrated panels, 28 one-liners) plus a stats strip
and a world map with numbered pins. Every story happened or was first
reported on Friday 20 November 2026.

## How it was built

- `render.py` draws everything with Pillow (shapes and fonts only, no images
  or AI generation). It fails if any text overflows its box or the story
  count is not 40. Run `python3 render.py` to regenerate `entry.png` and
  `entry.png.b64` (deterministic).
- `main.py` (Python, stdlib only) decodes `entry.png.b64` to
  `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). The image bytes are
  stored as base64 text so the repository is plain UTF-8 files.

Facts come from reports dated 20 November 2026 (Reuters, AP, AFP, IMD, ICJ,
UN News, Le Monde and others); contested claims are attributed. Coverage
window for this version: 00:00–05:00 UTC, 20 November 2026.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
