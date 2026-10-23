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
the numbers as JSON (`topbar.json`, `standby.json`, `webcam.json`) and the parts as
SVG and PNG - pictures and numbers only; every rule and every piece of markup is
written by hand here. A nudge to the interface
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
| `src/sources/Game.jsx` | The browser source over a live match (`#/source/game`): 1920 x 1080, over the game capture. Today that is the top bar |
| `src/sources/Standby.jsx` | The browser source between games (`#/source/standby`): 1920 x 1080, filling the screen. A drifting slideshow, the "coming up next" band across the bottom, and the countdown hanging from the top |
| `src/sources/Webcams.jsx` | The browser source over the standby screen (`#/source/webcams`): two frames and two names, no video. Cameras go under it in OBS |
| `src/sources/WebcamSolo.jsx` | The same frame drawn once and centred (`#/source/webcam-solo`), for a scene with one camera |
| `src/control/panels/` | The operator's board — teams (with the series and each side's wins), bans, tournament, and options (what the broadcast shows at all) |
| `src/generated/` | Written by `tools/obs.py`. Do not edit |
| `src/generated/guide.png` | Every place as an orange outline: add it as an Image source while lining a scene up, then hide it |

## The standby screen

Its shape is the old NGS board (`C:\FourCourtJester\Broadcasts\Heroes`,
`apollo/scenes/scene-afk`, 2018) rebuilt here: a team container either side of a VS,
a message board behind them, a logo arm at each screen edge. Those are that board's
places, carried over in `layout.toml`'s `[standby]`; the language is this kit's, so a
container is the game band's name plate grown up - the same lean, now coming to a
point at half height, the same chrome rim, wash and hex lattice.

Two things it takes from that broadcast beyond the composition:

- **The slides drift.** A picture bigger than the frame crawls across it over a
  minute while each slide is only on screen for nine seconds, so you see a slice of a
  long slow move rather than a freeze-frame. That framing is a 1.3 zoom, which is also
  the sharpness floor: **file slides at 2560 x 1440 or better**, or the drift pans
  across an upscale.
- **The countdown is a bug at the top**, not furniture in the middle, and it is left
  out entirely when no clock is running. The board offers two ways to set it — **Back
  at** (a time of day) and **Back in** (a length) — and they write the same timer, so
  starting one replaces the other and the screen never has two. Prefer "Back at" for a
  break that might be interrupted: the source is shut down whenever its scene is
  hidden, so a length restarts every time you cut back to it, while a target time
  survives that untouched.

What the operator sets: the message and the clock in **Standby**, who is playing in
**Teams**, and the two marks in **Tournament** - the tournament's logo on the right
arm, the broadcaster's own on the left, where that board had the game's logo. Either
arm can be left empty, and each mark is centred in its arm with clear air on every
side - it never touches the edges or the diagonal.

`design/standby/mock.py` is the earlier exploration of the backdrop question
(slideshow versus a transparent page over an OBS Media Source) and draws the centred
plate this band replaced. It is kept for that argument, not as a picture of the
screen.

## The webcams

A browser source of **borders**, not of video. OBS puts each camera underneath and
this lays the chrome and the name over it, which is what lets a camera be nudged,
scaled or swapped without any art being re-cut. The windows hang in the standby
screen's free middle — under its countdown bug, over its band — so the two sources
stack without either having to move. That free space is read off `[standby]` rather
than typed, and the generator asserts that both layouts fit in it.

Two layouts, each its own browser source: the pair at `#/source/webcams` (848 x 477
each, 80px apart) and a single centred window at `#/source/webcam-solo` (1024 x 576).
Both are exactly 16:9. They are separate sources rather than a switch because the
choice belongs to an OBS scene, not to the show — a desk segment and a solo-host
segment may both be loaded, and a toggle would change them together.

Per camera, in OBS:

1. put the camera under the source and size it to the window — `cam` and `solo` in
   `src/generated/webcam.json`, or line it up by eye against `src/generated/guide.png`,
   which outlines all three;
2. add **Filters → Image Mask/Blend**, mode **Alpha Mask (Alpha Channel)**, pointed
   at the mask for that lean — `/masks/cam_mask_left.png` or
   `/masks/cam_mask_right.png` on the published site, `studio/public/masks/` in the
   repo. The solo window uses the left one.

**There are two masks, not three.** They are drawn at 1024 x 576, the largest window
there is, and OBS scales one onto whichever window you are filling. That works
because the chamfer is a fraction of the box rather than a fixed run, so every window
is the same *shape* and the solo one is the pair's enlarged — not the pair's with
bigger corners cut off it. The frames are SVG and scale for the same reason, which is
why there is no separate solo frame either.

They live in `studio/public/`, which ships as-is, so a broadcaster can fetch them from
the site. Everything else the generator writes goes to `src/generated/` and is bundled;
a mask nobody imports would never have reached the build at all.

Step 2 is not optional. The windows are cut at the plates' angle — a corner taken
back over 120px, so the cut edge matches every other slant in the kit, and the same
run at either size so it never scales with the box — and a camera left as a rectangle
pokes its corners out past the chrome. A full parallelogram at either height would slant
far enough to throw away most of a face, which is why it is a chamfer rather than a lean.

**Nothing here animates, and nothing should.** These frames have to sit on camera
sources underneath them in OBS, and OBS cannot move those in step, so any motion
slides a frame off its camera for as long as it lasts. A name bar may fade, since it
sits over the smoke rather than over the picture; no frame may move.

Names come from the **Webcams** panel; left and right are as the viewer sees them,
and the solo source shows whoever is in the left slot. The name sits at the outer
edge of each bar and the handle at the inner one, so the pair mirrors. A side with
neither a name nor a handle shows its window and no bar.

**`?fill`** paints the windows a flat colour — `#/source/webcams?fill` — so the frames
can be photographed with no camera behind them. It is a URL flag rather than a switch
on the board because a switch can be left on, and on air a filled window is an opaque
rectangle over somebody's face.

The bars are darker than the standby band's smoke (0.8 against 0.5), which is what
makes the two match rather than differ: the band sits at the bottom of that screen
under the full weight of its vignette, and these sit mid-screen where it has barely
started.

## Still open

- **Testing**: the user tests in OBS at 1080p, the broadcast's settings; Claude checks
  in a browser at 1920 x 1080.
- **Ban portraits**: the pickers offer whatever is in the studio's image library, and
  nothing fills that library with hero portraits — 90-odd of them — yet.
- **The ban tiles' size and shape** were never settled: slanted as they are, or square.
- **The font**: Saira Semi Condensed, fetched from Google Fonts at load. Blizzard's own
  is a cut of Metronic Pro, whose licence would need checking for broadcast use.
- **The standby screen's slides** come from the image library's `slides/` group, and the
  library is empty bar two throwaway gradients added while testing (`slides/one`,
  `slides/two` — delete them from the library when real art arrives). Dropping a folder
  named `slides` on the library files the lot in one motion. Note that **files are added
  on the machine running OBS**: a picture dropped on a producer's laptop has bytes that
  live only there, and the slideshow leaves those out rather than playing a blank.
- **The other scenes** — draft, post-game — are not started, but both have their
  reference shot measured:

  **Draft.** `design/ref_draft_bans.jpg` (a ban, empty middle) and
  `design/ref_draft_picks.jpg` (two heroes picked, splash art in). Blizzard's player
  columns run x 14–358 and x 1618–1896, down to y ≈ 922. The picked heroes' art fills
  the middle but fades to true black by y ≈ 841 — measured, not eyeballed: the centre
  strip's brightest pixel is 0 from y 880 down. So **a full-width band below y ≈ 925
  clears everything in both states**, leaving about 155px — enough for the standby
  band's 130px containers. The top centre is the map name and the pick timer, flanked
  by three ban hexes a side; the middle is where the game throws "BLUE BAN" and the
  pick animations, so it is not ours to use.

  The old NGS broadcast solved the same problem and landed on the same line: its chat
  cover (`C:\FourCourtJester\Broadcasts\Heroes\img\draft\background.png`, served by
  `apollo/scenes/bug-cover.pug`) is a 1920 x 1080 PNG, transparent except for **flat
  black from y 927 to the bottom**, with the far left and right raised to y ≈ 904 and a
  notch at x ≈ 120 / 1800. The raised wings are what swallow the player columns' tails;
  the flat middle is the chat and whatever else bleeds through. Two independent
  measurements, 927 against our 925, which is as close to confirmation as this gets.

  So the draft scene is two layers: a cover of that shape, and our band on top of it.

  **Post-game.** `design/ref_endgame_stats.jpg`; the panel to cut around is roughly
  x 337–1583, y 203–920.

  All four references are 1920 x 1080 JPEGs. Their edges carry compression ringing, so
  treat every number above as ±5px — good enough to place a band, not good enough to
  commit to `layout.toml`. That should come from the extracted UI under
  `references/JamiePhan`, the way the top bar's did, with these as the check.
