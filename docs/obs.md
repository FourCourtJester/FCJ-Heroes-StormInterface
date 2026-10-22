# OBS: the plan for after the art pass

> **Superseded.** [obs-topbar-handoff.md](obs-topbar-handoff.md) is the one file for the OBS
> work now (2026-10-21): the agreed top bar, every graphic and number, the plan. This one is
> kept for its history; its geometry table is out of date.

Written 2026-10-16, after the user's "start thinking about generating assets to pair both Heroes
and OBS overlays together" and rescoped the same day. Nothing here is built yet. This is the
starting point for the work, not a record of it.

## The rule it rests on

**OBS draws data only, never art** (user, 2026-10-16): only what the game can't know. That's
the team names, team logos, series score, the tournament's name, division and logo, and the
game's bans. **Nothing goes on the bottom part of the UI.** Every plate and frame that data sits
on is the interface's: the name plates now, the rest in the art pass. It all lives in the top bar.

Why the data stays outside the `.StormInterface` (the original brief, §4): a team swap would
otherwise mean rebuilding and reselecting an interface mid-broadcast. The interface can't see
OBS, so there is no in-game fallback for a missing name.

The rider: **the resolution is locked.** Frames anchor to the screen, so a different
resolution moves the plates out from under the OBS layer. 1920 x 1080 is the resolution we
build and test at. Any 16:9 screen gets the same layout scaled (1200 layout units tall), so a
1440p capture only needs every OBS number x 4/3. A non-16:9 window is untested
(docs/history.md item 4).

## Where it goes

Every place is a `kind = "obs"` rect in `layout.toml` (`kind = "ui"` for the name plates: ours,
with OBS's name on them). gen makes their constants, and its padding and overlap checks cover
them. Every number is screen px at 1080p, `[x, y, w, h]`. Red mirrors blue about x 960. The
canvas's Top bar board draws them all (orange dashes), and the Spec board lists them.

| Data | Blue | Red | What goes there |
|---|---|---|---|
| Series score | `blue_score` 400, 0, 64 x 63.3 | `red_score` 1456, 0 | maps won in the series |
| Team name | `blue_name` 470, 0, 214 x 63.3 | `red_name` 1236, 0 | the name, on our plate |
| Team logo | `blue_logo` 690, 0, 64 x 63.3 | `red_logo` 1166, 0 | 8 px clear of the wings' slanted ends |
| Bans | `blue_bans` 576, 67, 108 x 32 | `red_bans` 1236, 67 | the game's bans, under the name, flush with its inner end |
| Division | `division` 794, 67, 96 x 24 (under blue's wing) | | e.g. "Division 1", and the bracket stage if it fits |
| Game count | | `game_count` 1024, 67, 102 x 24 (under red's wing) | e.g. "Game 2 of 5" |
| Tournament logo | `event_logo` 922, 32, 68 x 62 (the hexagon's middle) | | the event's mark, over Blizzard's hexagon |
| Tournament name | `event_name` 810, 164, 300 x 24 (under the clock) | | the event's name |

The geometry:
- The top row (score, name, logo) is one band, the height of the level labels' backplate wings:
  the top edge down to y 63.3, the hexagon's side points. That lets our plates meet the wings.
- The division and game count are as wide as their wing's bottom edge. Blizzard's hexagon sits
  2.75 px left of centre, so the two differ (blue 794-890, red 1024-1126). `division` was
  `bracket` until 2026-10-16.
- Blue's score stays clear of the replay panel (x 14-392).
- The interface's own pieces between them: the level plates (`blue_level` 820, 8 / `red_level`
  1036, 8, 64 wide since 2026-10-19), the talent-lead flame behind the leader's, the hexagon plate (`logo_plate` 892, 0,
  136 x 125) and the clock (906, 128).
- **Proposed, not yet agreed (2026-10-16):** the tournament logo in the hexagon's middle (centre
  956, 63) and its name under the clock, clear of Blizzard's centre banners (y 196).

## Generating the paired layer

The point: **OBS's layer is made from the same numbers as the interface**, so they can't drift
apart. The OBS file never holds hand-typed positions. A change to `layout.toml` moves both.

A proposal, to be decided then: a `tools/obs.py` that gen (or pack) runs, writing an `obs/`
folder:

1. **An alignment guide**: a transparent 1920 x 1080 PNG of every `"obs"` rect as dashed
   orange outlines (the canvas's legend). It goes on top while setting a scene up, hidden
   after. gen already rasterises polygons; a PNG writer is stdlib (`zlib` + `struct`).
2. **The live layer**, one of two ways:
   - **a browser source** (recommended): one generated HTML page at 1920 x 1080, transparent.
     Every piece of data sits absolutely at its `layout.toml` rect, filled from one small
     `obs/match.json` the operator edits between games: names, logo files, scores, bans, the
     tournament's name, division and logo, game N of M. It's one source, positioned once, and
     it can animate a score change;
   - **an OBS scene collection** (JSON import) with an image or text source per rect, each text
     source "read from file". This is native OBS, but its file format is OBS's own and needs
     checking against the version in use.
3. **A preview**: a game-scene board on the canvas, the default view with the OBS layer in
   place, so the pair is reviewed together before it goes live.

The plates under the data are the art pass's, in the interface (gen textures in the top
backplate's chrome). They always show, with or without OBS.

Bans are hero portraits. The browser source would show them from images the operator drops in
`obs/bans/`. Whether any observer frame still holds the draft's bans once the game is on
hasn't been looked for. If one does, the interface could draw them itself, since they're game
data.

## The canvas

`design/canvas_gen.py` redraws the as-built boards from gen's numbers. Brought up to date on
2026-10-16: the top bar's OBS data, the spec rows, the legend and the open list, and a new
**Maps** board (every battleground's minimap place and banners, the banner standard, THE GAP
and THE FLOOR). Rerun it after the art pass, then publish `design/canvas/project/` to the canvas
(https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK); `canvas.json` (the notes, board places and
sizes) is edited by hand from `design/canvas/sizes.json`. Still to come: the art pass's results
on the plates, bars and panes boards, and the game-scene board (step 3 above).
`Stock.dc.html` is hand-annotated (Blizzard's stock UI) and stays as it is.

## Questions for the user, when we get there

- ~~The tournament's places~~: logo in the hexagon; the name in a secondary tab, division
  beside it (user, 2026-10-19; docs/obs-topbar-handoff.md).
- ~~Series score~~: pips, 3 a side for best of 5, one hexagon full / empty (user, 2026-10-19).
- Bans: how many a side in the format used (the rect fits three at 32 px), and portraits or
  names?
- **Fonts for the OBS layer.** The interface uses only Blizzard's fonts, from the game. Using
  those font files outside the game is a licensing question. The options:
  - a close open font (the canvas already uses Barlow Condensed);
  - text pre-rendered from the game: screenshots, so not live.
- The other scenes (draft, break, post-game) are wholly OBS. Do they share these assets? The
  interface may play no part in the draft screen at all; worth a look in a live custom game.

## Order

1. The final pass and the art pass (HANDOFF §7) come first, the name plates and the rest of
   the plates under OBS's data among them.
2. Screenshots of everything for posting.
3. Settle the questions above, then `tools/obs.py`: the guide, then the live layer.
4. Rerun canvas_gen, add the game-scene board, and publish.
5. A live custom game with the OBS layer on, at 1080p, checking every rect against the guide.
