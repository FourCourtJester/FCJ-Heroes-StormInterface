# OBS: the plan for after the art pass

Written 2026-10-16 (user: "after our final art pass ... return to our canvas documents, update
them to our current art/positioning, and start thinking about generating assets to pair both
Heroes and OBS overlays together. Most notably, for the game scene, the elements we theorized
ages ago"). Nothing here is built yet. This is the starting point for the work, not a record
of it.

## The rule it rests on

From the original brief (§4): **the interface renders game-derived information. OBS renders
everything static.** Branding (team names, logos, the event's marks) never goes in the
`.StormInterface`. Otherwise every team swap means rebuilding and reselecting an interface
mid-broadcast. The interface's job is to **leave the space empty**, and it can't see OBS, so
there is no in-game fallback for a missing name.

The rider: **the resolution is locked.** Frames anchor to the screen, so a different
resolution moves the empty space out from under the OBS layer. 1920 x 1080 is the resolution
we build and test at. Any 16:9 screen gets the same layout scaled (1200 layout units tall), so
a 1440p capture only needs every OBS number x 4/3. Our art is drawn at 1440p and drawn at 75%
at 1080p (HANDOFF §6). A non-16:9 window is untested (docs/history.md item 4).

## The game scene: the elements theorized and never built

Laid out in the top-bar OBS pass (2026-09-30, f3556df / 3a77bb7) and kept in `layout.toml` as
`kind = "obs"` rects. The interface makes their constants and leaves them empty. Every number
is screen px at 1080p, `[x, y, w, h]`. Red mirrors blue about x 960:

| Element | Blue | Red | What goes there |
|---|---|---|---|
| Series score | `blue_score` 400, 0, 64 x 63.3 | `red_score` 1456, 0 | maps won in the series |
| Team name | `blue_name` 470, 0, 214 x 63.3 | `red_name` 1236, 0 | the name, on a plate (below) |
| Team logo | `blue_logo` 690, 0, 64 x 63.3 | `red_logo` 1166, 0 | the logo, 8 px clear of the wings' slanted ends |
| Bans | `blue_bans` 576, 67, 108 x 32 | `red_bans` 1236, 67 | the draft's bans, under the name, flush with its inner end |
| Bracket | `bracket` 794, 67, 96 x 24 (under blue's wing) | | e.g. "Upper final" |
| Game count | | `game_count` 1024, 67, 102 x 24 (under red's wing) | e.g. "Game 2 of 5" |

The geometry, as settled then:
- The top row (score, name, logo) is one band, the height of the level labels' backplate wings:
  the top edge down to y 63.3, the hexagon's side points. That lets their art meet the wings'.
- The bracket and game count are as wide as their wing's bottom edge. Blizzard's hexagon sits
  2.75 px left of centre, so the two differ (blue 794-890, red 1024-1126).
- Blue's score stays clear of the replay panel (x 14-392).
- The interface's own pieces between them: the level plates (`blue_level` 800, 8 / `red_level`
  1040, 8), the talent-lead flame behind the leader's, the hexagon plate (`logo_plate` 892, 0,
  136 x 125) and the clock (906, 128).

The hexagon's middle stays the game's (Blizzard's hexagon art over our plate). Whether an
event's mark goes in it is an open question (below).

**One loose end in the config:** `blue_name` and `red_name` are `kind = "ui"` ("the plate is
ours; OBS draws the name on it"), but no name plate has ever been drawn. The spec board still
says "no name plate drawn yet". Decide which side draws it:
- **OBS** (the brief's rule: it's static art): the plate becomes part of the paired assets
  below, and the rects become `"obs"`;
- **the interface**: a gen texture in the top backplate's chrome, so it matches the wings
  exactly. It would always show, named or not.

My lean is OBS draws it, generated from the same numbers and colours. That gives one look and
no in-game plate sitting empty when OBS is off.

Other game-scene ideas from the brief and canvases that OBS could carry, none designed:
- a caster or player camera;
- a lower third (caster names, a sponsor);
- a ticker.
They need space the interface doesn't use. The free regions are:
- the left edge between the kill feed and the info panes;
- the right edge under the replay box, which hides on Ctrl+Shift+R;
- the bottom corners outside the hero rows, held off by `[screen] padding`.
Any of them gets a `kind = "obs"` rect first, so gen's padding and overlap checks cover it.

## Generating the paired assets

The point: **OBS's layer is made from the same numbers as the interface**, so they can't drift
apart. The OBS file never holds hand-typed positions. A change to `layout.toml` moves both.

A proposal, to be decided then: a `tools/obs.py` that gen (or pack) runs, writing an `obs/`
folder:

1. **An alignment guide**: a transparent 1920 x 1080 PNG of every `"obs"` rect as dashed
   orange outlines (the canvas's legend). It goes on top while setting a scene up, hidden
   after. gen already rasterises polygons; a PNG writer is stdlib (`zlib` + `struct`).
2. **The backing art** for each rect, in the top backplate's look, so OBS's pieces read as
   part of the bar:
   - the chrome rim, sheen and hexagon lattice;
   - each team's colour fading to the stock dark, from `[top_backplate]`'s colours.
   Rasterised by gen's own code, at 1440p (as the interface's art), into PNGs. The name plate,
   score and logo frames, ban slots, bracket and game-count plates.
3. **The live layer**, one of two ways:
   - **a browser source** (recommended): one generated HTML page at 1920 x 1080. Every element
     sits absolutely at its `layout.toml` rect, filled from one small `obs/match.json` the
     operator edits between games: names, logo files, scores, bans, bracket, game N of M.
     It's one source, positioned once, and it can animate a score change;
   - **an OBS scene collection** (JSON import) with an image or text source per rect, each text
     source "read from file". This is native OBS, but its file format is OBS's own and needs
     checking against the version in use.
4. **A preview**: the canvas's game-scene board (below) drawn with the OBS layer in place, so
   the pair is reviewed together before it goes live.

Bans are hero portraits. The browser source would show them from images the operator drops in
`obs/bans/`. Whether any observer frame still holds the draft's bans once the game is on
hasn't been looked for. If one does, the interface could draw them itself, since they're
game data.

## The canvases to bring up to date

`design/canvas_gen.py` redraws the as-built boards from gen's numbers. Rerun it after the art
pass, then publish `design/canvas/project/` to the canvas
(https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK). What's stale now:
- **The legend note** in `canvas.json` (hand-written) still says build 92518e6, 2026-09-30.
- **The spec board's rows**, written in canvas_gen.py by hand:
  - "Map objectives - Over the minimap - not started" (every map is done; docs/maps.md);
  - "Seen at 1.375; this +10% not yet" on the plates;
  - "Check in Towers of Doom" on core HP;
  - the name-plate line above.
  Go through every row against HANDOFF §1.
- **No board for the maps.** A generated "Maps, as built" board is the natural one to add: each
  battleground's minimap place and objective panel from `maps.py`'s placers. THE FLOOR and
  THE GAP are drawn as lines.
- **The art pass's results**: the Visual board (the visual language) is the art pass's brief.
  After it, the plates, bars and panes boards show the new art (the boards draw the build's
  own textures where they can).
- **A new board: the game scene**, the default view with the OBS layer (step 4 above). It's the
  one OBS works from.
- `Stock.dc.html` is hand-annotated (Blizzard's stock UI) and stays as it is.

## Questions for the user, when we get there

- The name plate: OBS or the interface (above)?
- Series score: a number, or pips (won / to win, from "best of N")?
- Bans: how many a side in the format used (the rect fits about three at 32 px), and portraits
  or names?
- The hexagon: Blizzard's own art, or the event's logo over it?
- **Fonts for the OBS layer.** The interface uses only Blizzard's fonts, from the game. Using
  those font files outside the game is a licensing question. The options:
  - a close open font (the canvas already uses Barlow Condensed);
  - text pre-rendered from the game: screenshots, so not live.
- The other scenes (draft, break, post-game) are wholly OBS. Do they share these assets? The
  interface may play no part in the draft screen at all; worth a look in a live custom game.
- A caster camera or lower third on the game scene: where (the free regions above)?

## Order

1. The final pass and the art pass (HANDOFF §7) come first; the OBS art copies the art pass's
   look.
2. Screenshots of everything for posting.
3. Settle the questions above, then `tools/obs.py`: the guide, then the backings, then the live
   layer.
4. Rerun canvas_gen, add the maps and game-scene boards, and publish.
5. A live custom game with the OBS layer on, at 1080p, checking every rect against the guide.
