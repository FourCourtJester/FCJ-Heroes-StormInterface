# FCJ Heroes — the broadcast studio

The OBS half of [FCJ Heroes](../README.md): the plates that sit over the observer
interface's top bar, and the data on them. Built on
[Single Studio](https://github.com/FourCourtJester/Single-Studio) — an operator's board
in an OBS custom browser dock, one browser source per graphic, no server.

```bash
npm install
npm run dev
```

The board opens at the printed URL; its header menu lists every graphic's
browser-source URL with a copy button. Published to GitHub Pages on every push that
touches this folder, so the live board is at
`https://fourcourtjester.github.io/FCJ-Heroes-StormInterface/#/`.

## Why it lives in the interface's repo

Both halves are drawn from one file. `layout.toml` holds the numbers the game UI is
built from, and `tools/obs.py` turns the same numbers into `src/generated/` here:
`topbar.json`, the name plate's CSS, and the parts as SVG. A nudge to the interface
moves the broadcast graphics with it, in the same commit, and `python tools/gen.py
--check` fails if either has gone stale.

**Nothing in `src/generated/` is written by hand.** Change `layout.toml` (or
`tools/obs.py`) and run `python tools/gen.py`.

## The rule

OBS draws the data *and the plates under it* (2026-10-22). The interface keeps only
the places, so it stays usable with no OBS running: with this source off, the game's
top bar is the level wings, Blizzard's hexagon and the clock, and nothing hangs off
them. See `docs/obs-topbar-handoff.md` in the repo root.

## What's here

| Path | What |
|---|---|
| `src/sources/TopBar.jsx` | The browser source: 1920 x 1080, over the game capture |
| `src/control/panels/` | The operator's board — teams, series, bans, tournament |
| `src/generated/` | Written by `tools/obs.py`. Do not edit |
| `src/generated/guide.png` | Every place as an orange outline: add it as an Image source while lining a scene up, then hide it |

## Still open

- **Nothing has been seen in OBS yet**, only measured in a browser.
- **Ban portraits**: the pickers offer whatever is in the studio's image library, and
  nothing fills that library with hero portraits — 90-odd of them — yet.
- **The ban tiles' size and shape** were never settled: slanted as they are, or square.
- **The font**: Saira Semi Condensed, fetched from Google Fonts at load. Blizzard's own
  is a cut of Metronic Pro, whose licence would need checking for broadcast use.
- **The other scenes** — draft, break, post-game — are not started.
