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

## The operator's board

Five panels, collapsible, folded on load, in **the running order of a show** rather than by
how often a thing changes (user, 2026-10-23): you come up on the **Standby** screen, you are
on **Webcams**, then the **Teams** and the **Tournament** around the match itself, and
**Help** last.

There is no Options panel. It held a single switch, for the tournament's logo, and a panel of
one switch is a panel you have to open to discover it has nothing in it. Every switch now
sits under the thing it turns on, which is where you are already looking.

### Help

Directions for whoever is running this, on the board rather than in a file they would have to
know to look for (user, 2026-10-23). Three sections: the **image store** and how to reach it,
**browser sources** and how to add them to OBS, and **using this studio** — the OBS collection
to start from, the `slides/` grouping (with the recommended slide size and why), and the
webcam masks, with the collection and the mask files linked.

### The OBS collection

`studio/public/FCJ_Heroes_Esports_v1.0.json`, served at the Pages root and linked from Help
with `download`, so a click saves it instead of rendering JSON in a tab. Import it in OBS
with **Scene Collection → Import**.

Seven scenes — `-- Audio`, `Blank`, `Draft`, `Game`, `Scores`, `Static`, `Webcams` — and all
seven browser sources at 1920 x 1080.

**It started as a dev export**, and everything in it that belonged to one machine has been
taken out (user, 2026-10-23):

- **The browser sources** pointed at `http://localhost:5173/`, which would have been seven
  dead sources for anyone who imported it. All seven now point at the published studio.
- **Three image sources** held screenshots on a personal
  `Heroes of the Storm/Screenshots/` path — backdrops standing in for the game capture while
  the scenes were built. Dropped. Each of those scenes also holds the real
  `Heroes of the Storm` capture, so what is left is correct rather than empty, which the
  edit asserts rather than assumes.
- **The collection's name** was "FCJ Heroes [Dev]", which is the label OBS shows in its
  scene-collection list. Now "FCJ Heroes".
- **`shutdown` is on for the three sources with an entrance** (Draft, Matchup, Scores) and
  `restart_when_active` is gone from all of them, which is the house rule below. Standby
  keeps `shutdown` off: its countdown is driven by the clock, not by loading.

Edited by round-trip rather than by hand. `json.dumps(doc, indent=4, ensure_ascii=False)`
reproduces the original byte for byte, which was checked before the first change, so the
diff on a 79KB file is only what actually moved.

Last, and folded. Everything above it is used every show; this is read once while OBS is being
wired and then never again, so it costs one line of the board to the people who already know.

The browser source list in it is the framework's own `SourceList`, not a list typed out here:
add a source and it appears, which a hand-written one would not. The framework moved that list
out of the board and into the gear menu because "wiring OBS is a once-ever job" and it was
taking up room under the controls — which is an argument against a *permanent* list, not
against one inside a folded panel.

Where things actually are, since the help text has to be right about it: the gear, top right,
holds **Collaborate, Image store, Browser sources, Keyboard shortcuts, Plugins, Start over**.
The magnifier on any image picker opens the same library.

### Two tournament logos

`event.logo` is **square**, `event.logo_wide` is **oblong**, and they are two pictures rather
than one reused because the holes are different shapes (user, 2026-10-23):

| | |
|---|---|
| `event.logo` (square) | Blizzard's hexagon in the game scene. The hole is a hexagon, so an oblong mark is squashed or cropped |
| `event.logo_wide` (wide) | the game scene's top right corner, 204 x 50 — a square mark would waste it |
| `event.broadcaster` | the game scene's top left corner, and the standby band's left arm |

Which one a graphic wants is a property of the hole, not of the show, so the board asks for
both once and each scene takes the one that fits.

### The corner marks

The broadcaster's top left, the tournament's wide logo top right, each on its own switch so
a show can run any combination of the three marks.

**The box is derived from the pips, not typed.** A best of 7 is the longest series, so its
outermost pip reaches further along the band than anything else; the mark starts
`corner_gap` outside that and runs to the screen's own 20px padding. That works out at
**204 x 50** at the moment. Typing the width instead would be a number that silently stops
being true the day the pip count changes.

Each mark takes its own width at that height and binds to its own screen edge, so a narrow
logo sits in the corner rather than drifting in toward the pips — the same rule the scores
lockup needed.

**Not yet seen together with Blizzard's kill feed**, which also lives top left. The marks sit
inside the band's height to stay clear of it, but that is reasoning, not a live check.

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

**To replay the entrance**, tick the source's **Shutdown source when not visible** — that
one on its own (user, 2026-10-23). The entrance runs on mount, and shutting the source down
while its scene is hidden is what makes it mount again, so "Refresh browser when scene
becomes active" has nothing left to do. Without it the band is simply there, which is right
for a scene it never leaves and wrong for one you cut back to.

The marks on the arms come from **Tournament**: the broadcaster's on the left, the
tournament's on the right. Either can be left unset, and nothing is drawn for it.

The tournament's is the **wide** logo where there is one — wide, then square, then nothing
(user, 2026-10-23), the same waterfall the scores screen uses. An arm is 576 x 103, which is
the shape the wide logo is drawn for; the square one belongs in Blizzard's hexagon and is
only the fallback here. It lives in `MatchupBand`, so **Matchup and Draft both get it** from
the one change. Checked on both sources: wide and square set draws the wide, square alone
draws the square, neither draws nothing.

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

It is drawn as **four windows on one sky**, rather than one shape with a hole, because a
hole wants `evenodd` and that is one more thing to be true in whatever CEF a given OBS
ships. Each piece is clipped to its own band and holds a full-screen sky pushed back by
exactly where that band starts, so all four show the same picture in the same screen
position and a seam has the same pixel on both sides. (Measured: every sky's box reports
(0, 0).) It is also what lets the motion be written once — every copy mounts together, so
they animate in step.

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

### What stands around the hole

Built 2026-10-23, from the brief agreed before the break. The bands left over are 1920 x 205
above the panel and 1920 x 153 below it, and `layout.toml`'s `[scores]` measures the
furniture into them.

**The winner, across the top.** The winning team's name in white, with a three-stage glow in
that team's colour — tight, bloom, and a wide faint one so the bloom has somewhere to end
(user: "Winning team name across the top, white glowing in team color").

Who won is the **operator's to say**, from the two **Winner** toggles under *Score Screen
Winner* on the **Tournament** panel. Nothing else can say it. Blizzard's own screen announces
a victory, but from the point of view of whoever's client the replay is, and we cover it
anyway; and `wins` is stepped on *after* the result is called, so reading the series would
show the wrong team for as long as it took the operator to reach the stepper. Nothing is
drawn unless a side is lit **and** that side has a name, so the glow never surrounds a blank.

It is **a pair of grouped toggles rather than a dropdown** (user, 2026-10-23). Two things
that buys, on the one control here that is used live with a result just called: a `Toggle`
writes **immediately**, where a `Field` or `Select` stages until save — so the name is on air
the instant it is pressed — and the state is readable at a glance instead of by opening a
menu. Measured behaviour: lighting one puts the other out, and pressing the lit one puts it
out too, so "no winner yet" is a state the operator can reach without Reset.

Three things worth knowing about it:

- **It reads `toggles`, not `variables`.** That is where `Toggle` writes, and it is the same
  reason it reaches air without a save. `Scores.jsx` reads `toggles.winner.blue` and
  `toggles.winner.red`.
- **Each lit button wears its own side's colour** (`fcjh-won`, in `src/css/index.css`). The
  framework lights every toggle in one accent and that accent is blue, so a lit "Red" was
  exactly the colour of a lit "Blue" and only the word told them apart. The two values are
  `layout.toml`'s `blue_colour` and `red_colour`, written out in the stylesheet because
  `tools/obs.py` may write pictures and a numbers JSON and nothing else.
- **Clear still takes it, through `paths`.** The control moved to Tournament; what it means
  did not, and a new match must not inherit the last one's result. `names` reaches
  `variables`, so the two toggles go in `ResetButton`'s `paths` instead. Swap does not take
  them at all: it cuts its list in half and exchanges the pairs — it *throws* on an odd list
  (`swap needs an even number of paths to cut in half`) — and which side won is not a
  property of a side, so there is nothing to exchange it with.

**The victory mark**, one either side of the name. Two are drawn and both ship:

| | |
|---|---|
| `laurel` | a crescent branch, nine leaves fanned off an arc — the classic |
| `hex` | a hexagon ring with a six-point sparkle, the lattice motif the plates and bands wear |

`[scores] win_mark` picks one. `?mark=hex` on the source URL overrides it for a side-by-side
look without a rebuild, the same trick the webcams use for `?fill`.

Both are **masks, not pictures**: the SVG is solid white and carries no colour, so the
stylesheet paints it and the same file serves both teams — one drawn shape instead of four,
and nothing to keep in step when a team colour moves. A mask takes no `text-shadow`, so the
bloom is a `drop-shadow` filter on the shape. The mask URLs are literal in the stylesheet and
the spec picks a *class*, because Vite only resolves a `url()` it can see at build time: a
path assembled from the spec at runtime would be left alone and 404 on Pages. Both marks are
small enough that it inlines them as data URIs rather than emitting files — so there is no
win_*.svg in `dist/assets`, which is correct, not a missing asset.

The laurel **computes its own viewBox**. The first cut fixed it at 64x104 and the outer
leaves were simply clipped off, which read on screen as a thin upright frond rather than a
laurel. Every ellipse's true extent is worked out in `laurel_svg` — exact, from the rotated
radii, not sampled — and the box is whatever contains them, which also makes the ratio in the
spec the real one so the mark is never squashed at a given height.

**The two marks under the panel**, as a collaboration: `<broadcaster> x <tournament>`
(user, 2026-10-23).

The tournament mark is the **wide one where there is one**: `event.logo_wide`, then
`event.logo`, then nothing (user, 2026-10-23). This band is 320 x 96 a side, which is the
shape the wide logo is for; the square one is drawn for Blizzard's hexagon and is only the
fallback here, for a show that has not been given a wide version. All three legs checked:

| set | drawn |
|---|---|
| wide and square | **wide** |
| square only | **square** |
| neither | the broadcaster alone, no x, centred on 960 |

They **close on the x** rather than sitting apart: the left one right bound, the right one
left bound, so the three read as one lockup on the panel's centre line. Each box is a fixed
320 x 96 with 10px of padding a logo may not cross, as on the arms, which keeps the lockup
symmetric about 960 whatever shape the two logos are. Measured: the x spans 947–973, centre
**960**, which is the panel's centre.

MISMATCHED SHAPES are the case this exists for, so they are the case to test — a matched pair
proves nothing here. Both checked, with the x on 960 each time:

| left | right | gap to the x |
|---|---|---|
| oblong 600x120 (drawn 300 wide) | square 160x160 (76 wide) | 44 / 44 |
| tall 120x320 (29 wide) | wordmark 600x120 (300 wide) | 44 / 44 |

Equal gaps whatever the widths, which is the point: the x holds the centre and each logo
closes on it. The visual *mass* is then deliberately lopsided when the two shapes differ a
lot — 29px against 300px in the second row — because what is centred is the join, not the
group. Centring the group instead would move the x off 960.

Two dials, both in `[scores]`: logos are drawn at `mark_h` minus the padding (96 - 20 = 76px
tall) and capped at `mark_w` minus the padding (320 - 20 = 300px wide), so anything wider
than about 4:1 is width-limited rather than height-limited.

Inside the box the picture takes **its own width at the band's height**, and that is what
makes "right bound" mean anything. Stretched to the full 320 with `object-fit: contain`
letterboxing it, a square logo sits in the middle of its own box with transparent air either
side — so it floats away from the x however the box is aligned. A wide placeholder hid this;
a round one showed it at once.

Each mark is gated on its value before being drawn, which `Image` alone would not need — it
draws nothing for an unset picture. The reason is the layout: an empty box is still a box. So
with **one** mark the x goes too (an x is only an x when there are two things to join) and the
lone mark centres on its own; with **neither**, the whole band goes.

**The two bands animate in** (user, 2026-10-23): the winner rises out of the panel's top
edge, the marks drop out of its bottom edge, 620ms, the marks 120ms behind so the name leads.

The trick is that **the band clips and an inner element moves**. The middle of this screen is
a hole with Blizzard's graphic showing through it, so anything that simply slid would travel
*across* the panel. With `overflow: hidden` on the band and the transform on a child, the
content comes out of the panel's own edge. Measured a third of the way in: the winner at
+56.6px still rising, the marks at −94.6px still falling.

**The winner also goes out the way it came in** (user, 2026-10-23), because it is a toggle
and a toggle gets pressed twice — returning `null` on the second press would blink the name
off air. That one is the framework's `Transition` rather than our own keyframes, since the
motion has to run backwards too: `--ss-shift` is the whole band, so the name leaves through
the panel edge instead of fading where it stands. Measured on the second press: `ss-exiting`,
translateY 205px, the full height of the band.

`Transition`'s `trigger` runs an **out, swap, in** cycle on any new value, so correcting blue
to red mid-show plays out and back in rather than swapping the word underneath the glow.

**The name itself cuts** (user, 2026-10-23): `transition="cut"` on the `Variable`. A Variable
fades its own text when the value changes, which is right in a lower third and wrong inside a
band that is already moving - on a blue-to-red correction you would get a cross-fade running
inside a slide, two motions on one piece of text. `cut` is the framework's own no-op variant,
`--ss-duration: 0s` with opacity held, so the band carries the motion and the words just
change.

That is what `last` in `Winner()` is for. A cleared toggle has to animate out in the colour
it went on in, and the toggle is already off by the time the outro runs, so the last lit side
has to outlive it by one transition. Without it the glow would snap to the wrong colour — or
to none — halfway out.

The glow survives the clip. The name is 72px in a 108px line box inside a 205px band, so the
glyphs have about 76px of air each side and the widest shadow is 66px.

**The sky moves.** Two star fields at different scales twinkling at different rates, three
large soft dust clouds, and three comets crossing on a long 23s cycle — mostly absent,
because a sky with a comet in it every few seconds is a screensaver rather than a backdrop.

It was turned up on 2026-10-23, because the first pass was motion on paper only: the twinkle
swung .55–1 against a plate that already has stars painted into it, and the dust moved 26px
over 90s, which is 0.29px a second — below the speed at which anything reads as moving. Now
.25–1, dust alphas roughly doubled, and ±34px over 48s.

**The comets stop at the horizon.** The lit grid floor starts at the panel's bottom edge, and
a comet crossing it reads as a streak lying *on the ground* rather than one in the sky. They
are **masked, not timed out**: ending the keyframes early would fix one comet on one path,
while a gradient mask on the comet field fades anything approaching the floor whatever its
path, and stays true if the paths change. Measured: opaque to 747px, fully transparent by
**927px**, which is the panel's bottom edge read from the same number the hole is cut with.

It is **drawn, not photographed**. The game composites 23 textures over this same plate and
they are all extracted under `references/`, but gradients cost nothing, scale to any size,
and keep more Blizzard binaries out of a public Pages build — and the effects wanted are
stars, dust and streaks, which is what gradients are good at.

Every layer exists in all four copies and **must stay in step**: they mount together, so
nothing in them may be random or depend on where its piece sits, or the same star would be
in two states either side of a seam. That is why the comet delays are written out.

**Not done: the electricity off the blue tiles** — the one the user filed as "harder". The
raw material is there if we want it: `storm_ui_home_nexus_lightning1-4.dds` (648 x 432, four
frames, so it wants stepping rather than tweening) and `storm_ui_home_nexus_fx_tilelighting.dds`
(1812 x 304, a sweep along the floor), both under `references/`.

## Colour-blind colours

The game's colour-blind option turns the interface's red a peachy orange and its blue a touch
cyan (HANDOFF, the in-game half). A browser source can't read the game's options, so the
operator says: **Tournament → Colour-blind colours** (user, 2026-10-25). Off is the resting
state.

- **The colours are the interface's own.** `tools/obs.py` writes
  `src/generated/colourblind.json` with the same rule the interface uses
  (`gen.colour_blind_cfg`: each team colour keeps its saturation and value and takes the hue
  of Blizzard's colour-blind pair), so OBS and the game can't disagree.
- **The art that carries a team colour has a `_cb` twin** there too: `frame_{team}_cb.svg`
  (the team line), `lattice_{team}_cb.svg` and `pip_{team}_cb.svg`. The logo frame and the
  ban tiles carry no team colour and have none.
- **One hook**, `src/components/colourBlind.js`: `useColourBlind()` reads
  `toggles.colourblind` (a `Toggle` writes to `toggles`, so it goes to air without a save).
  A scene root wears `cb` while it is on, and its stylesheet swaps the URLs; the washes and
  glows come from `COLOUR_BLIND` / `COLOUR_BLIND_VARS` in place of the spec's colours.
- **Covered:** the game bar (plates, lattices, team lines, pips), the matchup band on standby
  and the draft, the scores screen's winner glow. **Not yet:** the matchup slab
  (`MatchupSlab.jsx`), and the board's own lit Winner buttons (`fcjh-won`), which are the
  operator's, not the broadcast's.

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

- **NEXT: the Game scene's logos** — "some slight adjustments to make for Game regarding
  logos" (user, 2026-10-23), left for last and never spelled out. Needs the user to say what
  the adjustment is.
- **Testing**: the user tests in OBS at 1080p, the broadcast's settings; Claude checks
  in a browser at 1920 x 1080. **Claude's image library is empty**, and that is not a
  neutral fixture: anything whose width comes from library content - every `<select>` of
  asset keys - measures far narrower here than on a real show. It hid a picker bug on
  2026-10-23 that the user saw at once; one realistic key (35 characters) was the whole
  difference. Inject one before trusting a width measurement. See
  `docs/single-studio-reports.md` entry 2.
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

- **The scores screen's tile electricity** is the one piece of its brief not built; see
  "What stands around the hole" above for the frames already extracted for it.

  All four references are 1920 x 1080 JPEGs. Their edges carry compression ringing, so
  treat every number above as ±5px — good enough to place a band, not good enough to
  commit to `layout.toml`. That should come from the extracted UI under
  `references/JamiePhan`, the way the top bar's did, with these as the check.
