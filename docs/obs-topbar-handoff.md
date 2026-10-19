# OBS top bar: the agreed design, ready to build

Written 2026-10-18, after three mock passes the user signed off ("Yes thats great"). Nothing
here is built into the interface yet. This is the fast track for doing that. It supersedes the
top-bar parts of [obs.md](obs.md) where they differ.

## Where the design lives

Everything in `design/obs/` is untracked, the same as `design/canvas/`.

- `design/obs/mock_pass3.py` makes everything else: run it with `python -I`. It needs Chrome
  and the screenshot `Screenshot2026-10-18 13_30_46.jpg`.
- `pass3.png` and `pass3.html`: the approved mock.
- `kit/`: the name plate as a web component, ready for OBS:
  - `namebar.css`: its header has the markup;
  - `frame_blue.svg`, `frame_red.svg`;
  - `lattice_blue.svg`, `lattice_red.svg`.

All numbers are screen px at 1080p. Red mirrors blue about x 960. The lean is
`HeroCell.lean` = 0.54, and the band is 63.3 tall. The slant's run across the band,
D = 0.54 × 63.3, is 34.18.

## What changed from obs.md

**The rule changes.** The team name plate is now OBS art, not the interface's. This is the
one exception to "OBS draws data only": only OBS knows whether a tournament has team logos.
With no OBS running, the interface shows no name plates, just the wings, the tabs and the
ban tiles.

| Thing | Agreed design |
|---|---|
| Series score | No cell. Hexagon pips with no plate: pointy-top, r = 25.3 (80% of the band), 43.9 wide, 5 apart. The first pip's edge is 14 px off the name plate's outer slant. They fill from the name outward. Best of 5 = 3 a side, best of 7 = 4 (blue's fourth ends at ~252, clear of the kill feed and the replay panel). One hexagon is authored, in a full and an empty state; OBS draws as many as the series needs (user, 2026-10-19: more than 3 is the operator's call). |
| Name plate | The OBS nine-slice (below). The box is fixed: blue left 440, width 374 (top 440 → 779.8, the wing's end); red left 1106. Name text is 24 px at most and shrinks to fit 12 px inside the slants. |
| Team logo | Optional, inside the name plate's box: a fixed 109.5 px plate at the inner end. Its rim laps the name plate's to make one seam, at top x ≈ 707. Without a logo, the name plate runs on to the wing. |
| Level wings (interface) | 20 px shorter each. The level plates are 64 wide (were 80): blue `[820, 8, 64, 50]`, red `[1036, 8, 64, 50]`. The wings follow, via `wing_margin`. |
| Division / game count | The tab hangs from the wing: y 63.3 → 100.3 (flush with the bans' bottom). Its outer side is the name/logo seam carried down the lean, so the slants line up. Its inner side is 5 px off Blizzard's hexagon. The tab is interface art (stock fill, 2 px rim, no top edge); OBS draws the words only, 14 px. |
| Bans | Optional, a toggle. Three tiles, 32 px parallelograms on a 38 px pitch. They sit at y 68.3 → 100.3 (5 below the band). The innermost tile's outer x is the seam minus 5. Banned tiles get a 4 px red foot. Their size, and slanted versus square, get their own pass when we build them (user, 2026-10-19). |
| Tournament | Its logo goes over Blizzard's Nexus hexagon (centre 956, 63); a hexagon mask for OBS comes later. The tournament name is dropped from under the clock; it goes in a secondary tab, likely the tournament name on the left and the division on the right (user, 2026-10-19). The tabs are generic information panels: what goes in them is up to the operator. |
| Font | Metronic for Blizzard Bold is a cut of Metronic Pro (Mostardesign): a style from $25, the family $329. Check the licence covers broadcast use. The mock uses Saira Semi Condensed. |

## The name plate kit

- **Frame (nine-slice).** `frame_<team>.svg` is 100 × 63.3: a 40 px cap, a 20 px stretch
  and a 40 px cap. It holds only the rim (2.5 px inside), the sheen (the top half) and the
  team line (y 58.3–61.3, inset 3). CSS applies it with
  `border-image: … 0 40 fill / 0 40px / stretch`.
- **Behind the frame**, as CSS on `.fcjh-band`:
  - a clip-path parallelogram;
  - the base `#3b2d52 → #2a1f3c` (top to bottom);
  - the team glow along the band, from the inner end to the outer:
    .92 / .58 at 22% / .32 at 50% / .58 at 80% / .95;
  - the lattice in `::before`, masked .7 / .25 / .4.

  The outer end was lit to just under the wing's outer edge: brightness ~157 against ~170
  for blue, ~124 against ~130 for red.
- **Logo.** `.fcjh-logo` is `flex: 0 0 109.5px` with a -36.68 px margin on its inner side
  (D + rim), so the two rims coincide. It has a dark window, rgba(13,10,20,.5), inset 5 px
  along and 6 px top and bottom, and the mark is 46 px. Leave the div out when there's no logo.

## To build

1. `layout.toml`:
   - ~~the level rects (above)~~ and ~~`blue_talent_lead` / `red_talent_lead`, to the shaved
     wings~~: done 2026-10-19, the wings end at 779.8 / 1140.2;
   - `blue_name` / `red_name` → `kind = "obs"`, at the box above;
   - `blue_logo` / `red_logo` inside it;
   - drop `blue_score` / `red_score`; add pip rects;
   - `blue_bans` / `red_bans`, `division` and `game_count`, to the numbers above;
   - drop `event_name`.

   Then check that the wings regenerate to end at ~779.8 / 1140.2.
2. Interface art:
   - drop our name plate frames;
   - add the division and game tabs;
   - add the empty ban tiles. Settle their size and shape first, and they need a way to be
     hidden, since bans are a toggle.
3. Update `docs/obs.md`: the rule's exception, and the table.
4. Update the canvas's Top bar and Spec boards.
5. ~~Settle "best of five"~~: 3 pips a side (user, 2026-10-19), one hexagon in full and empty.
