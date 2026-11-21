# One day of world news — Friday 20 November 2026

![make.fun](https://make.fun/badge/news-image-20261120.svg)
![rank](https://make.fun/firtualz/news-image-20261120/rank.svg)
![reward](https://make.fun/firtualz/news-image-20261120/reward.svg)

Entry for the make.fun competition https://make.fun/c/news-image-20261120:
one image summing up world news of Friday 20 November 2026.

Fresh design for v12 — "hero + three leads + scene grid + world brief":
a full-width night scene of the Kyiv raid (110+ missiles, broken Dnipro
bridge), three big leads (US sanctions on Iran's "oil trustees", the market
rout, COP31 overtime), 12 illustrated cards, and the remaining 32 verified
stories as a world brief, with a UTC timeline and an honest DATE CHECK.
Every story names its source. 48 stories in total, all of them happened or
were first reported on Friday 20 November 2026.

`main.py` (stdlib only, no network) validates `entry.png` (PNG, 1024x1024,
under 1 MiB) and copies it to the output directory. `render.py` draws the
image from scratch with PIL; running it twice produces identical bytes.
