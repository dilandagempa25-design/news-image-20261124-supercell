[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/dilandagempa25-design/news-image-20261124-supercell/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/dilandagempa25-design/news-image-20261124-supercell/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# THE WORLD IN ONE DAY — Tuesday 24 November 2026

A classic broadsheet front page that sums up 24 November 2026's world news in one
1024×1024 image, generated entirely by a dependency-free Python program.

**Lead story — Strait of Hormuz:** Iran's Revolutionary Guard says three oil tankers
struck mines in the Strait of Hormuz late Monday despite a US escort (unconfirmed by
US Central Command); the US Treasury sanctioned more than two dozen Iranian exchange
houses over "shadow banking", and Tehran ruled out talks with Washington until its
seven conditions are met. The lead is illustrated with a drawn tanker, escort ship
and mines.

**Also on the front page:**

- **Nvidia Brings Back Huang** — Jensen Huang reinstated as CEO less than a week
  after saying he would retire, reportedly after President Trump intervened; shares
  jumped about 31%.
- **China Launches Shenzhou-24** — two Chinese astronauts plus Pakistani astronaut
  Zeeshan Ali, the first foreign astronaut to board the Tiangong station.
- **Riyadh Tower Struck Again** — a Houthi strike hit Riyadh's tallest tower for the
  second time in a week, injuring 11.
- **Libya Condemns Benghazi Strike** — Libya's Presidential Council condemned
  Ukraine's drone attack on Russian ships in Benghazi; Russia and Ukraine traded
  accusations at the UN Security Council.
- **EU Plans 22nd Russia Package** — about 60 more banks and crypto networks
  targeted, pending approval by all 27 member states.
- **North Korea Expels Swiss Envoy** — Pyongyang demanded closure of Switzerland's
  new diplomatic office and ordered the senior Swiss diplomat to leave.
- **ICJ Rohingya Ruling Affirmed** — fourteen countries affirmed the ICJ decision on
  Myanmar's genocide of the Rohingya; Malaysia will return more than 6,500 refugees.
- **Markets at the close** — S&P 500 7,237.17 (+4.73%), Nasdaq 24,089.56 (+6.51%),
  DAX 25,337.27 (+2.15%), FTSE 100 10,480.82 (+1.30%), Brent $86.7 (−2.99%),
  Gold $3,620.4 (−0.85%).

All stories verified against the day's reporting — no invented news.

## How it works

`main.py` uses only the Python standard library. It loads pre-rendered glyph
bitmaps from `glyphs.bin` (produced at build time by `make_glyphs.py`, which uses
Pillow and is not needed at run time), draws the whole page with its own raster
helpers, and encodes the PNG with `zlib`. Output is deterministic: same bytes on
every run.

## How to run

```sh
python3 main.py
```

Stdlib only, writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
