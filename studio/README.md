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
| `src/sources/Standby.jsx` | The backdrop between games (`#/source/standby`): a drifting slideshow and the countdown hanging from the top. Fills the screen |
| `src/sources/Matchup.jsx` | The matchup band on its own (`#/source/matchup`), transparent — laid over whatever it belongs on |
| `src/sources/Webcams.jsx` | The browser source over the standby screen (`#/source/webcams`): two frames and two names, no video. Cameras go under it in OBS |
| `src/sources/WebcamSolo.jsx` | The same frame drawn once and centred (`#/source/webcam-solo`), for a scene with one camera |
| `src/sources/Draft.jsx` | The browser source over Blizzard's ban-and-pick screen (`#/source/draft`): the band with the series on it; its cover is still to come |
| `src/sources/Scores.jsx` | The browser source over Blizzard's end-of-game screen (`#/source/scores`): a backdrop with a hole where the stats panel is |
| `src/components/MatchupBand.jsx` | The band itself — worn by Matchup and Draft, and the only place its numbers are read |
| `src/control/panels/` | The operator's board — teams (with the series and each side's wins), bans, tournament, and options (what the broadcast shows at all) |
| `src/generated/` | Written by `tools/obs.py`. Do not edit |
| `src/generated/guide.png` | Every place as an orange outline: add it as an Image source while lining a scene up, then hide it |

## The matchup band

A team container either side of a VS, a message board behind them, a logo arm at each
screen edge. Its shape is the old NGS board (`C:\FourCourtJester\Broadcasts\Heroes`,
`apollo/scenes/scene-afk`, 2018); its language is this kit's, so a container is the game
band's name plate grown up — the same lean, now coming to a point at half height, the same
chrome rim, wash and hex lattice. Its places are in `layout.toml`'s `[standby]`, which is
where it was born.

It lives in `src/components/MatchupBand.jsx` and carries its own numbers, so a scene that
wears it supplies only what goes on its message board. **`#/source/matchup`** is the band
by itself, over nothing; **`#/source/draft`** is the same band with the series on it.

It used to be part of the standby screen and is its own source now (user, 2026-10-23),
because the two are wanted at different times: the standby screen is background material
under several scenes and stays up for a whole break, while the band is something you bring
in, let land, and bring in again later in the cast. One source cannot do both — the band's
entrance runs when the source mounts, so a band welded to the backdrop plays once and never
again.

**To replay the entrance**, tick the source's **Shutdown source when not visible** and
**Refresh browser when scene becomes active**. Without them the band is simply there, which
is right for a scene it never leaves and wrong for one you cut back to.

The marks on the arms come from **Tournament**: the broadcaster's on the left, the
tournament's on the right. Either can be left unset, and nothing is drawn for it.

## The standby screen

A drifting slideshow and a countdown, and nothing else — the band that used to sit on it
is `#/source/matchup` now. Lay the two over each other in OBS when you want both.

Two things it takes from the old broadcast:

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
   at the mask for that lean. On the published site they are under the project's own
   path, not the domain root:
   `https://fourcourtjester.github.io/FCJ-Heroes-StormInterface/masks/cam_mask_left.png`
   (and `..._right.png`); in the repo, `studio/public/masks/`. The solo window uses the
   left one.

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

## The draft screen

Today it is the matchup band and nothing else, wearing the same translucencies it wears
everywhere. `#/source/draft`, 1920 x 1080, over the game capture. (If you want the standby
message on it rather than the series, use `#/source/matchup` instead — they are the same
band.) Its message board carries
the **series** — "Best of 5", from `series.pips` — rather than a message: standby says what is
coming up, and here there is no question of that, the teams are on screen drafting.

### The cover is still to come

Blizzard's draft screen puts the lobby chat and the tails of its player columns across the
bottom, which a broadcast does not want on air. Two attempts at hiding them are in the
history, and both were wrong the same way: **a cover that varies only down the screen.**

1. An opaque band from y 927 with its ends raised — which is what the user's own 2018 cover
   did. In OBS it read as exactly what it was: a straight edge sawing through the hexagon
   columns down each side and through the heroes' legs.
2. A vertical gradient, nothing at y 820 and solid by y 912. It softened that edge and
   changed nothing, because the problem was never the edge. What sits behind the cover
   varies *across* the screen — columns at both edges, splash art in the middle, chat at the
   bottom left — and no vertical ramp answers a horizontal problem (user, 2026-10-23:
   "uniform on its horizontal axis. This is 100% of the issue").

So the shape comes from artwork, not from a guess. The user is supplying an updated chat
cover; its geometry gets measured the way the top bar's did and comes back through
`layout.toml`.

**What we measured off the reference shots**, to check that artwork against when it arrives.
`design/ref_draft_bans.jpg` is a ban with the middle empty; `design/ref_draft_picks.jpg` has
two heroes picked and the splash art in.

| | |
|---|---|
| Player columns | x 14–358 and x 1618–1896, down to y 922 |
| Chat and the rest | from y 927 |
| Picked heroes' art | fills the middle, true black by y 841 — the centre strip's brightest pixel is 0 from y 880 down |
| Top centre | map name and pick timer, flanked by three ban hexes a side |
| The middle | where the game throws "BLUE BAN" and the pick animations — not ours to use |

The old broadcast's own cover
(`C:\FourCourtJester\Broadcasts\Heroes\img\draft\background.png`, served by
`apollo/scenes/bug-cover.pug`) was flat black from y 927 with its ends raised to y 904 and a
notch at x ≈ 120 / 1800 — 927 against our 927, which is how we know the line itself is right
even though a straight one is not what the screen wants.

Both reference shots are 1920 x 1080 JPEGs whose edges carry compression ringing, so treat
every number as ±5px: good enough to check a cover against, not good enough to commit to
`layout.toml`. That should come from the extracted UI under `references/JamiePhan`, the way
the top bar's did.

## The scores screen

A **backdrop with a hole in it**, over Blizzard's end-of-game Stats screen. One thing on
that screen is worth keeping and it is the stats panel; everything around it is the
caster's own gold, gems and account level, the Leave and Rename Replay buttons, the chat
and its channel joins — none of which belongs on air (user, 2026-10-23: "preserve that
stats center box; everything else gets replaced").

Cutting a hole rather than patching the corners is what makes it safe. A patch has an edge
that falls wherever you put it, across whatever happens to be behind — the mistake the
draft cover made twice. This edge is Blizzard's own frame, so there is no line of ours to
notice anywhere.

The hole is `[scores]` in `layout.toml`: x 335, y 205, 1250 x 722. Blizzard's frame
measures x 337–1583, y 207–924 off `design/ref_endgame_stats.jpg`, and the hole is a shade
larger so their frame and its glow survive rather than being clipped by ours. A JPEG, so
±2px; the real numbers want the extracted UI, as the top bar's did.

It is drawn as four pieces rather than one shape with a hole, because a hole wants
`evenodd` and that is one more thing to be true in whatever CEF a given OBS ships. Each
piece paints the whole screen's gradient and is shifted to its own place in it, so the
seams land where the colour is already identical on both sides.

### The backdrop

`src/backgrounds/nexus.webp` — Blizzard's own Nexus home-screen plate, the purple nebula
with the lit grid floor:

```
mods/heroes.stormmod/base.stormassets/assets/textures/storm_ui_homescreenbackground_nexus.dds
```

1920 x 1200, cropped to 1080 from the top and saved as WebP (68 KB against 135 KB as JPEG).
Its horizon glow sits at y 932 — five pixels below the stats panel's bottom edge — so the
panel reads as standing on the lit floor rather than floating over it. That is luck rather
than design, but it is the reason this crop and not another.

Worth knowing if you go looking for it again: **the home screen is not that file.** The game
composites seventeen textures over it — scrolling stars, light rays, looping lightning, a
tile-lighting sweep — which is why no single asset matches a screenshot and why it isn't in
the press kit. They are all extracted under `references/` as `storm_ui_home_nexus_*` if we
ever want the drift; the plate alone is what we use.

It lives in `src/` and not `public/` because the **page** uses it: Vite fingerprints it and
rewrites the URL against the right base, which a `public/` path would not survive on Pages.
`public/` is for files a human downloads, like the OBS masks.

### Still to build on it (user, 2026-10-23)

Agreed before a break, not started. Today there are no names, no series and no marks — just
the backdrop and the hole. The room available, measured:

| | |
|---|---|
| Top band | 1920 x 205 |
| Bottom band | 1920 x 153 |
| Side columns | 335 x 722, each |

**1. Announce the winner.** The winning team's name **across the top**, in white with a glow
in that team's colour. The top band is the 205px above the panel.

The open question is how the graphic knows who won. Blizzard's own screen says "HANAMURA
TEMPLE VICTORY", but that is from the point of view of whoever's client it is, and we cover
it anyway — so the operator has to say. Simplest is a three-way on the board (blue / red /
nobody), which also gives a clean "nobody" for the moment before the result is called.
Deriving it from `blue.wins` / `red.wins` is tempting and wrong: those are the series, and
they are usually updated after the call rather than before it.

**2. The tournament and broadcaster marks**, centred under the scores — the bottom band.
Both already exist on the board, in **Tournament**: `event.logo` and `event.broadcaster`,
the same two the matchup band's arms use. Nothing new to set.

**3. Motion.** The screen is space, so it should drift. In rough order of effort:

- twinkling stars
- comets
- space dust / nebulae floating across
- harder: electricity arcing off the blue tiles

**We already have the art for most of this.** The 23 layers the game composites over the
Nexus plate are extracted under `references/` and are exactly these effects:

```
storm_ui_home_nexus_fx_star.dds          40 x 40, the twinkle sprite
storm_ui_home_nexus_fx_starpattern.dds   144 x 200
storm_ui_home_nexus_starsright.dds       1240 x 828, the scrolling field
storm_ui_home_nexus_fx_constellation.dds 352 x 316
storm_ui_home_nexus_fx_bg_cloudbase.dds  724 x 724, and _bg_cloud2 736 x 512 — the dust
storm_ui_home_nexus_fx_bgbeams.dds       480 x 300
storm_ui_home_nexus_fx_lightrays.dds     284 x 288
storm_ui_home_nexus_lightning1-4.dds     648 x 432, four frames — the tile electricity
storm_ui_home_nexus_fx_tilelighting.dds  1812 x 304, a sweep along the floor
```

The game drives them with scrolling UVs and fade loops; in CSS that is `background-position`
on a repeating layer and `@keyframes` on opacity, which is the same idea with less ceremony.
The lightning is four frames, so it wants stepping rather than tweening.

Motion is safe **here** specifically: nothing is registered to this backdrop. That is not
true of the webcam frames, which must never move because OBS cannot move the cameras under
them in step.

## If the board comes up unstyled

Serif text, no dark theme, buttons as bare words — or any rule of yours that measures as
though it were never written. **It is the dev server, not your code.** It happened twice on
2026-10-23: once a hot update applied half of a two-part edit, once the whole Tailwind
utility layer went missing after Vite auto-restarted on a `vite.config.js` mtime change that
was not a change at all.

The board now says so itself. `src/studio/devCssGuard.js` probes for a Tailwind utility on
mount and, if it is missing, drops a red banner across the top and logs the cure. It runs on
the control board only — never on a source, so it can never reach air — and
`import.meta.env.DEV` compiles it out of the build entirely.

The cure is a **restart**, not a reload:

```bash
npm run dev:fresh
```

which clears Vite's dependency cache first. Plain `npm run dev` usually suffices.

Before you go reading your own files, run `npm run build` and look at `dist/assets/*.css`. If
the built CSS has `.flex` in it, the code is fine and only the running server is wrong — that
one check would have saved an hour across the two occasions. `docs/single-studio-reports.md`
entry 3 has both in full.

## Still open

- **NEXT: hide the tournament tabs when they're blank** (user, 2026-10-23: "Hide tournament
  tabs if they're blank"). The division (blue) and game (red) tabs in `sources/Game.jsx`
  (`Tabs()`) draw their art whatever the words, so an empty one shows as a bare tab. Hide
  each on its own; the pair are held to one width, so a lone tab should take its own.
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

- **Post-game** is not started. `design/ref_endgame_stats.jpg`; the panel to cut around is
  roughly x 337–1583, y 203–920.

  All four references are 1920 x 1080 JPEGs. Their edges carry compression ringing, so
  treat every number above as ±5px — good enough to place a band, not good enough to
  commit to `layout.toml`. That should come from the extracted UI under
  `references/JamiePhan`, the way the top bar's did, with these as the check.
