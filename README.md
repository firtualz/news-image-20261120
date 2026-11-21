# news-image-20261120 — Friday 20 November 2026

One image that sums up Friday 20 November 2026: 48 stories, 7 regions,
every one of them happened or was first reported on that day.

## What's on the page

- **4 lead stories, drawn:** Cyclone Akvan makes landfall near Gopalpur
  (300,000 evacuated); Russia's overnight missile barrage on Kyiv, with
  debris falling in Poland; COP31's final day in Antalya (draft drops fossil
  fuels, Panama threatens a veto); Anthropic slides as the Nasdaq falls 5.3%.
- **12 picture cards:** Trump defers the Iran decision to next year, GTA VI's
  $3.79bn launch day, Houthi threats to Saudi ports, EU arms aid for Ukraine,
  South Africa mourning Phumzile Mlambo-Ngcuka, the Australia–Canada–NZ
  ceasefire call, the foiled Sydney car-bomb plot, Tesla's first Argentina
  store, Egypt's IMF review, Ronaldo's 986th goal, the ICJ Myanmar ruling
  (Thursday, kept as a small dated card), and US sanctions on four Iranians.
- **A map** ("Where it happened"), **32 more stories** in the "Also on Friday"
  list, a **"The day in UTC" timeline**, and a **DATE CHECK** box that names
  the big stories deliberately left out because they broke on an earlier day
  (Kenya's last Ebola patient, 11 Nov; Wales beating the All Blacks, 14 Nov;
  Anthropic's IPO debut, 19 Nov; the Shenzhen summit, 19 Nov; the ICJ ruling,
  19 Nov).

Every card carries a CLAIM / CONFIRMED tag and its source. Claims that rest
on one side only (for example Iran's report of tankers hitting mines in the
Strait of Hormuz) are labelled CLAIM, not presented as fact.

## How it was built

`render.py` draws the page from scratch with Pillow: the layout, the small
illustrations, the schematic world map and all the text. `main.py` (standard
library only) decodes `entry.png.b64` to the output directory,
deterministically, with no network. Five variants were rendered (different
lead combinations) and the winner was picked by blind two-way judge duels
against the final top-5 images of the 17 November edition; see
`duels-nemotron.jsonl`.

## Files

- `entry.png.b64` — the entry image (1024×1024 PNG, base64 text)
- `main.py` — the entrypoint (decodes entry.png.b64 to /output/entry.png)
- `render.py` — draws the image; `python3 render.py V-A` re-renders variant A
- `LICENSE` — MIT

## Sources

IMD, Reuters, CNN, ISW, AP, AFP, EU Council, ICJ, IMF, US Treasury,
Take-Two, Sensor Tower. All figures are as reported on 20 November 2026.
