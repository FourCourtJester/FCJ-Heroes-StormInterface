# OBS: everything for the build

The one file for the OBS work: the rule, the agreed top bar, every generated graphic and number,
what to build and in what order. Agreed 2026-10-18 after three mock passes (user: "Yes thats
great"), settled further 2026-10-19, gathered here 2026-10-21. The band's **places** are in the
build since 2026-10-22 (layout.toml `[top_bar]`, "To build" item 1); **none of its art is, and
none of it will be** - the plates are OBS's, so the interface stays usable without it (the
rule, 2026-10-22).
[obs.md](obs.md) is the earlier plan, kept for its history; where they differ, this file wins.

## The rule

**OBS draws data only** (user, 2026-10-16): only what the game can't know. That's the team
names and logos, the series score, the tournament's name, division and logo, and the game's
bans. **Nothing goes on the bottom part of the UI.**

**And OBS draws the plates under it too** (user, 2026-10-22: "the interface needs to be usable
without OBS, so building in-game art for OBS elements when we can't guarantee any will draw
upon them is not useful"). The name plates, the division and game tabs and the ban tiles are
all the OBS layer's art. The interface keeps their **places** - layout.toml `[top_bar]`,
`gen.top_bar_geometry` - so the two line up exactly, and draws none of them: with no OBS
running the top bar is the level wings, Blizzard's hexagon and the clock, and nothing hangs
off them. That is the point: a plate nothing may ever fill is a plate in the way.

This overrules the earlier split, where everything but the name plate was the interface's
(the name plate's own reason, 2026-10-18, still holds: only OBS knows whether a tournament has
team logos, and the plate's shape depends on it). The two tabs were built in game on
2026-10-22 and taken straight back out (18dcde6, then reverted) - the geometry they were drawn
from is what stays.

Why the data stays outside the `.StormInterface`: a team swap would otherwise mean rebuilding
and reselecting an interface mid-broadcast. The interface can't see OBS, so there's no
in-game fallback for a missing name.

**The resolution is locked.** Frames anchor to the screen, so a different resolution moves the
plates out from under the OBS layer. Every number here is screen px at 1920 × 1080. Any 16:9
screen gets the same layout scaled (1200 layout units tall), so a 1440p capture takes every
number × 4/3. A non-16:9 window is untested (docs/history.md item 4).

## The geometry

**Where these numbers live (2026-10-22):** `layout.toml` `[top_bar]` holds the few the band is
really drawn from - its height, the name plate's outer edge, the name/logo seam, the pips' size,
gap, offset and count, the ban tiles' size, pitch and insets, the tabs' clearance off the
hexagon - and `tools/gen.py` `top_bar_geometry` works every box and polygon out from them
(`top_bar_rects` puts them among layout.toml's rects, all "obs"). So the interface's places and
the OBS layer's have one source and can't drift apart: the band's inner end meets the level
wings' ends, the two plates share one seam, the tabs follow Blizzard's hexagon. The table below
is the design; the build is where the numbers come from.

Red mirrors blue about x 960. The lean is `HeroCell.lean` = 0.54 across per px down, and the
band (the top row) is 63.3 tall, the level wings' height. The slant's run across the band,
D = 0.54 × 63.3, is 34.18.

| Thing | Agreed design |
|---|---|
| Series score | No cell. Hexagon pips with no plate: pointy-top, r = 25.3 (80% of the band), 43.9 wide, 5 apart, centred at y 30.65. The first pip's edge is 14 px off the name plate's outer slant. They fill from the name outward. Best of 3 = 2 a side, best of 5 = 3, best of 7 = 4 (blue's fourth ends at ~245, clear of the kill feed and the replay panel at x 14–392). One hexagon, in full and empty states; OBS draws as many as the series needs (user, 2026-10-19: more than 3 is the operator's call). Blue's centres: 413.8, 364.9, 316.1, 267.2. |
| Name plate | OBS's nine-slice (below). The box is fixed: blue left 440, width 374 (its top runs 440 → 779.8, the wing's end); red left 1106. The name is 24 px at most and shrinks to fit 12 px inside the slants. |
| Team logo | Optional, inside the name plate's box: a fixed 109.5 px plate at the inner end. Its rim laps the name plate's to make one seam, at top x ≈ 707. The mark is 46 px. Without a logo, the name plate runs on to the wing. |
| Level wings (interface) | 20 px shorter each. The level plates are 64 wide: blue `[820, 8, 64, 50]`, red `[1036, 8, 64, 50]` (done 2026-10-19; the wings end at 779.8 / 1140.2). |
| Division / game count | A tab hung from the wing, y 63.3 → 100.3 (flush with the bans' bottom). Its outer side is the name/logo seam carried down the lean, so the slants line up; its inner side is 5 px off Blizzard's hexagon. The tab is OBS's art, as the rest of the band is since 2026-10-22 (stock fill, 2 px rim, no top edge - it was the interface's until then); its words are 14 px, centred at (825.2, 81.8) blue and (1091.6, 81.8) red. The tabs are generic information panels: what goes in them is the operator's call. |
| Bans | Optional, a toggle. Three tiles a side, 32 px parallelograms on a 38 px pitch, the band's lean, y 68.3 → 100.3 (5 below the band). The innermost tile's outer x is the seam minus 5 (blue's top 706.9 → 738.9). A banned hero's portrait is desaturated, with a 4 px red foot. Size, and slanted versus square, get their own pass when built (user, 2026-10-19). |
| Tournament | Its logo goes over Blizzard's Nexus hexagon (centre 957.25, 63.3); `event_mask.png` masks it to that hexagon. The tournament name leaves the clock: it goes in a secondary tab, likely the name on the left and the division on the right (user, 2026-10-19). |
| Font | The mock uses Saira Semi Condensed (Google Fonts, open). Blizzard's in-game font, Metronic for Blizzard Bold, is a cut of Metronic Pro (Mostardesign): a style from $25, the family $329; check the licence covers broadcast use before using it. |

## The graphics

All generated by **`design/obs/mock_pass3.py`** (run `python -I design/obs/mock_pass3.py`) from
`layout.toml` through gen's `top_bar_geometry` (it adjusted the name and logo in code until
2026-10-22; it adjusts nothing now, and what it writes is byte for byte the approved kit). Edit
the script, never its output. It needs Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`) to render
the mock PNG. The game screenshot it first cropped from is gone; it reuses the crops it saved
(`bg_top.png`, `ban0–5.png`).

**`design/obs/` is untracked**, like `design/canvas/`: it's only on this machine.

### `design/obs/kit/`: the parts for OBS

| File | What it is |
|---|---|
| `topbar.json` | **Every number in this file, as data**: the band, colours, name plate boxes, logo plate, pip centres for each side (index 0 nearest the name), ban tile polygons (index 0 innermost), tab polygons and text centres, the event hexagon. The thing to build the OBS layer from. |
| `namebar.css` | The name plate as a web component for a browser source. Its header comment has the markup: one `.fcjh-band` per team, a `.fcjh-name`, and a `.fcjh-logo` left out when there's no logo. |
| `frame_blue.svg`, `frame_red.svg` | The name plate's frame, a nine-slice, 100 × 63.3: 40 px cap, 20 px stretch, 40 px cap. Only the rim (2.5 px in), the sheen (top half) and the team line (y 58.3–61.3, inset 3). |
| `lattice_blue.svg`, `lattice_red.svg` | The hex lattice behind the plate, as the backplate's. |
| `pip_blue.svg`, `pip_red.svg` | A won score pip: team colour, rim, a soft shadow and a highlight. 53.9 × 60.6 with a 5 px pad for the shadow, so the hexagon's centre is the SVG's centre. |
| `pip_empty.svg` | A pip not yet won: dark at 60%, rim and shadow. |
| `event_mask.png` | Blizzard's hexagon, white, on a clear 1920 × 1080 sheet: an OBS image mask for the tournament logo. |
| `guide.png` | Every place above as an orange outline on a clear 1920 × 1080 sheet (name plates, logo plates, Bo7's four pips a side, ban tiles, tabs, the hexagon). Put it on top while lining up a scene, hide it after. |

### `design/obs/`: the mocks

- `pass3.png`, `pass3.html`: the approved mock (pass 3), with the nine-slice explained and the
  plate at several widths.
- `pass2.*`, `firstpass.*`: the earlier passes, for the record.
- `backplate.png`: the interface's top backplate as built, from gen.
- `bg_top.png`: the game's top 200 px at 1080p (2026-10-18, before the wings were shortened).
- `ban0–5.png`: hero portrait stand-ins for the ban tiles.

## The name plate kit, in detail

- **Frame.** CSS applies it with `border-image: url(frame_<team>.svg) 0 40 fill / 0 40px / stretch`.
- **Behind the frame**, CSS on `.fcjh-band`:
  - a clip-path parallelogram (top 0 → width − D, bottom D → width);
  - the base `#3b2d52 → #2a1f3c`, top to bottom;
  - the team glow along the band, inner end to outer: .92 / .58 at 22% / .32 at 50% / .58 at
    80% / .95;
  - the lattice in `::before`, masked .7 / .25 / .4.

  The outer end is lit to just under the wing's outer edge: brightness ~157 against ~170 for
  blue, ~124 against ~130 for red.
- **Logo.** `.fcjh-logo` is `flex: 0 0 109.5px` with a −36.68 px margin on its inner side
  (D + rim), so the two rims coincide. Its dark window, rgba(13,10,20,.5), is inset 5 px along
  and 6 px top and bottom.
- **Colours.** Blue `#5cbcec`, red `#e75c79` (the plates' health colours), rim `#dfe3ed`,
  stock `#221930 → #170f20`, dark `#0d0a14`, the name in Blizzard's light cyan
  `#cbe8ff → #ffffff`, tab text `#cbe8ff`, the banned foot `#c8323c`.

## The live layer (proposed)

**OBS's layer comes from the same numbers as the interface**, so they can't drift apart; a
change to `layout.toml` moves both. The plan, to be decided when we start:

- **A browser source** (recommended): one generated HTML page at 1920 × 1080, transparent, every
  piece at its place from `topbar.json`, filled from one small `match.json` the operator edits
  between games: names, logo files, series score and format, bans, tournament name, division
  and logo, game N of M. One source, positioned once, and it can animate a score change. Ban
  portraits from images the operator drops in a folder.
- **Or an OBS scene collection** (JSON import), an image or text source per place, text "read
  from file". Native OBS, but its file format needs checking against the version in use.
- Either way, `mock_pass3.py`'s kit code moves into `tools/obs.py`, run by gen, writing an
  `obs/` folder, so the kit regenerates with the interface.
- The aim is a **whole OBS scene collection**, other scenes too: see the questions.

## To build

1. **`layout.toml` - done 2026-10-22.** The hand-written OBS rects are gone; `[top_bar]` holds
   the numbers and `tools/gen.py` derives the rest (above). What now reaches the constants, all
   `obs`: `blue_name` / `red_name` `[440, 0, 374, 63.3]` / `[1106, ...]` (the plate is OBS's own
   art), `blue_logo` / `red_logo` `[704.5, 0, 109.5, 63.3]` / `[1106, ...]` lapping it,
   `blue_pips` / `red_pips` `[245.3, 5.3, 190.4, 50.6]` / `[1484.3, ...]` (a best of 7's four),
   `blue_bans` / `red_bans` `[630.9, 68.3, 108, 32]` / `[1181.1, ...]`, `division`
   `[741.2, 63.3, 167.7, 37]` and `game_count` `[1004, 63.3, 174.9, 37]` (not a mirror: the
   hexagon isn't centred), and `event_logo` as it was. Gone: `blue_score` / `red_score` (the
   pips have no plate) and `event_name` (the name has left the clock). Checked: every number
   `mock_pass3.py` writes is unchanged, so the agreed design is exactly what the build holds.
2. **Interface art: none** (user, 2026-10-22; see the rule). The band is OBS's to draw, the
   interface's only part in it is the places. For the record, what this item used to hold:
   our own name plate frames (there were none to drop - the plates were never drawn, only
   reserved), the division and game tabs (built 2026-10-22, reverted the same day) and the
   empty ban tiles with a way to hide them. The ban tiles' size and shape still want their
   pass (user, 2026-10-19) - now a question for the OBS layer, and their polygons are already
   in the geometry (`top_bar_geometry`'s `bans`).
3. `tools/obs.py` and the live layer (above).
4. The canvas: the Top bar and Spec boards, and a game-scene board with the OBS layer in place.
5. A live custom game with the OBS layer on, at 1080p, checking every place against `guide.png`.

## Open questions

- Bans: how many a side in the format used (the tiles fit three), and portraits or names?
- Fonts: Saira Semi Condensed (open), Barlow Condensed (the canvas's), or Metronic if the
  licence allows.
- The other scenes (draft, break, post-game) are wholly OBS. Do they share these assets? The
  interface may play no part in the draft at all; worth a look in a live custom game.
- Whether any observer frame still holds the draft's bans once the game is on. If one does,
  the interface could draw them itself, as game data.
