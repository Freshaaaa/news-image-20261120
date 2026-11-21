# news-image-20261120

[![news-image-20261120](https://img.shields.io/badge/make.fun-news--image--20261120-blue)](https://make.fun/c/news-image-20261120)
[![entry](https://img.shields.io/badge/entry-entry.png-green)](entry.png)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

One image that sums up the world news of **Friday 20 November 2026** — a
newspaper front page drawn with PIL (deterministic, no network, no clock).

- **Masthead** names the day: "Friday 20 November 2026", 52 stories, 6 regions, 8 fields.
- **16 cards** lead with Russian missiles landing in Poland, strikes on three Kyiv bridges, and the World Court holding Myanmar responsible for genocide — plus the Anthropic IPO, the AI sell-off, COP31, Hormuz, the UK-EU reset, a 6.7 quake in Peru, Estonia's border closure, BepiColombo at Mercury, the Palisades Fire verdict, the $7.25bn Roundup settlement, a Houthi missile over Riyadh, the first Trump-Xi-Putin summit and Bitcoin near $61,700.
- **36 more stories**, a UTC timeline, a dotted world map with 16 pins, a THE VERDICT box, a DATE CHECK and a sources footer with a HOW SURE ARE WE? legend. Every card carries a REPORTED / CLAIM / FORECAST tag.

## Run

```sh
python3 build-image.py   # renders entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copies it to out/entry.png
```

## Bounty

[news-image-20261120 on make.fun](https://make.fun/c/news-image-20261120)
