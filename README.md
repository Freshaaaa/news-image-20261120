# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Freshaaaa/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Freshaaaa/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

One image that sums up the world news of **Friday 20 November 2026** — a
newspaper front page drawn with PIL (deterministic, no network, no clock).

- **Masthead** names the day: "Friday 20 November 2026", 25 stories, 6 regions, 8 fields.
- **11 cards** lead with Russian missiles landing in Poland, strikes on three Kyiv bridges, and the World Court holding Myanmar responsible for genocide — plus the Anthropic IPO, the AI sell-off, COP31, Hormuz, the UK-EU reset, a 6.7 quake in Peru, Estonia's border closure and BepiColombo at Mercury.
- **14 more stories**, a day-by-hours timeline, a dotted world map with 11 pins, a THE VERDICT box, a DATE CHECK and a sources footer with a HOW SURE ARE WE? legend. Every card carries a REPORTED / CLAIM / FORECAST tag.

## Run

```sh
python3 build-image.py   # renders entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copies it to out/entry.png
```

## Bounty

[news-image-20261120 on make.fun](https://make.fun/c/news-image-20261120)
