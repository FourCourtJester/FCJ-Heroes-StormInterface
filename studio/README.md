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
| `src/sources/Draft.jsx` | The browser source over Blizzard's ban-and-pick screen (`#/source/draft`): the matchup container with the series in its kicker. No cover |
| `src/sources/Scores.jsx` | The browser source over Blizzard's end-of-game screen (`#/source/scores`): a backdrop with a hole where the stats panel is |
| `src/components/MatchupSlab.jsx` | The matchup container — worn by Matchup and Draft, each giving it its own kicker |
| `src/components/MatchupBand.jsx` | The original band, `?band=original` only; Draft still borrows its scene variables |
| `src/control/panels/` | The operator's board — standby, webcams, teams (with the series and each side's wins), tournament, logos, and help |
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

### The Logos panel — two pictures each, four in all

The broadcaster and the tournament each get a **square** and a **wide** picture, on a panel of
their own (user, 2026-10-26). They were three pickers at the bottom of Tournament; they are
not tournament settings, they are the show's furniture, and four of them would have pushed the
tab fields out of their own panel.

| slot | drawn into |
|---|---|
| `event.broadcaster` (square) | — |
| `event.broadcaster_wide` | the game scene's top left corner, the standby band's left arm, the lockups |
| `event.logo` (square) | Blizzard's hexagon in the game scene |
| `event.logo_wide` | the top right corner (204 x 50), the band's right arm, the lockups |

**The waterfall runs both ways, and that is the part to read.** "Wide, then square, then
nothing" is right for a wide hole — a 204 x 50 corner, a 576 x 103 arm, a 297 x 65 lockup mark
— and exactly wrong for Blizzard's hexagon, where a wide mark is the one thing that cannot be
made to work. So each hole says which shape it is drawn for and takes the other only as a
fallback. `components/marks.js` is the whole of it:

```js
const hexMark = useMark('tournament', 'square')   // the hexagon wants the square one
const rightMark = useMark('tournament')            // a corner wants the wide one
```

A fallback is a worse fit, never a broken one. `useMark` hands back the `shape` it found, so
the hexagon can **fill** with a square mark and merely **contain** a wide one — letterboxed
and small, rather than a wordmark cropped to its middle third, which is what `cover` did to it
before.

**Neither picture is required.** An organisation with only one still gets a sensible result
everywhere; one with both gets the right one everywhere. A mark left unset is drawn as nothing
at all, not as an empty lit container.

#### Three switches, and they reach every source

| switch | takes off |
|---|---|
| `show.broadcaster` | every broadcaster mark — game bar corner, band arm, both lockups |
| `show.tournament` | every tournament mark, in the same four places |
| `show.hex` | Blizzard's hexagon, and nothing else |

One switch per mark rather than one per scene (user, 2026-10-26: "the same toggle will edit
matchup/draft/game/scoreboard"), so a broadcaster taken off is off everywhere rather than in
the one scene somebody remembered. They replace `corner.broadcaster`, `corner.tournament` and
the old `tournament`, which were per-corner; **the old toggle state does not carry over**, so
all three start off.

**The hexagon is not governed by the tournament switch.** It is the game's own furniture
wearing our mark rather than one of our overlays, so it keeps a switch to itself and is
unaffected by taking the tournament's marks off the broadcast (user, 2026-10-26: "Hex is
special since it's its own thing").

**The graphics close up around what is left.** Take the broadcaster off a lockup and the
tournament's mark centres, taking the x with it; take both off and there is no lockup at all.

That last part is why the switch is read in `marks.js` rather than by wrapping each mark in a
`Toggle`. The framework's source `Toggle` **keeps its children mounted while it is off**,
hidden rather than removed — deliberately, so a graphic laid out around it does not move as it
comes and goes. Exactly right for a fixed box, exactly wrong for a pair of marks meeting at an
x. So anything whose layout answers to a mark calls `useVisibleMark` and renders nothing,
while the two corners and the hexagon keep their `Toggle` wrapper, where the box is alone
against a screen edge and the fade is worth having.

**Why slots rather than detecting the aspect ratio.** Measuring an uploaded image was the
obvious alternative and it is worse in three ways. The asset store keeps no dimensions — an
entry is `{key, kind, hash, name, size, type, addedAt}` — so it means loading and measuring,
which is async, and the scores screen measures and animates on mount. Plenty of logos are
square files with a wide wordmark in transparent padding, so the file's ratio lies and only
reading the alpha bounding box would tell the truth — which a canvas cannot do for an image
added by URL from another host. And detection picks the treatment, never the artwork: it
cannot make a wide mark work in a hexagon. A slot is the organisation saying which picture is
which, once, which is the thing detection was trying to guess.

**Tall marks are not a case yet.** A 1:3 crest and a 1:1 badge want different holes, so one
would want its own slot rather than being squeezed into "square" — but nobody has asked, and a
slot nobody fills is a slot everybody wonders about.

### The corner marks

The broadcaster's top left, the tournament's wide logo top right. They are on the show-wide
switches above — `show.broadcaster` and `show.tournament` — rather than switches of their own,
so a mark is not on in one scene and off in another.

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

## The matchup slab

The matchup, replacing the bottom band — agreed as the direction on 2026-10-25, and since
2026-10-26 **what the source draws with no flag at all**, so a browser source is just
`#/source/matchup` with nothing to forget.

| URL | what it draws |
|---|---|
| `#/source/matchup` | **the one container a side** — score, logo, name. The default |
| `?band=slab` | hexagon badge + name plate a side |
| `?band=original` | the bottom band this replaced |

**SETTLED, 2026-10-26: the container is the matchup band.** "We're done with the matchup
band, so any unit vs slab convo is resolved" (user). `?band=slab` is a dead end kept only for
reference and can go whenever someone is tidying; the sections below on what was wrong with
the earlier shapes are history now rather than open questions.

One thing to know before deleting: Draft wears the container too since 2026-10-27, but
`Draft.jsx` still takes `BAND_VARS` and `SCREEN` from `MatchupBand`, so retiring the original
band means moving those first.

Note that the original band is now the one that needs asking for — `?band=original`, where it
used to be what you got by leaving the flag off.

### Where it sits, and how big

**Bottom-anchored, centred horizontally.** The lowest painted pixel sits `[screen] padding`
— 20px — above the bottom edge, the same margin the hero rows stop at, so the band and the
interface keep one edge (user, 2026-10-26). There is no `centre_y` any more: `tools/obs.py`
derives the row's centre line from that bottom edge, the row's height and the lockup under it,
so changing a size moves nothing on screen.

Each composition derives its **own** centre line, because they are not the same depth — the
container is 113 tall against the slab badge's 178. One shared line put the slab's lockup 16px
off the bottom of the screen; centred, that difference had been split top and bottom where
nobody saw it. The unit composition carries its own VS box for the same reason.

The anchor is measured on the **fullest** case, with the lockup under the row. Without one the
band rides higher rather than sliding down to fill the gap — deliberately, because a band that
repositions itself when somebody adds or clears a tournament logo would move on air.

**It has come down to 73% of its drawn size,** in three passes of ten (user, 2026-10-26). The
container is **542 x 102** a side, from 746 x 140.

The **tournament marks are exempt** from the second pass onward — "tournament logos dont have
to adhere to this" — so `lockup`, `lockup_mark`, `lockup_pad` and `lockup_x` are the sizes
they were and the marks hold their presence while the band tightens around them. They now span
about 673px against a 468px kicker, which is the exemption doing what it was asked to.

The third pass was made once before and reverted, because the nine-slice cap was authored and
could not follow the band down — see the section below. With the frames generated per plate it
is an ordinary number change, and the only thing that does not scale with the band now is the
rim: it is a true `rim_width` at every height, so it reads a little heavier here (2.45% of the
height) than it did at 140 (1.79%).

### The frames are generated per plate

**A plate's chrome is cut for that plate's height, and its nine-slice cap is derived, never
authored.** This is what lets the band be sized freely — and be authored on more than one page
(user, 2026-10-26: "we're trying to create a system here").

Two things draw a plate's point, and they do not scale alike:

- the **silhouette** is a `clip-path`, run `lean x h/2` over rise `h/2`. Both follow the
  height, so the angle is `atan(lean)` — **28.37°, at every size**;
- the **chrome** is a `border-image` cap, painted **1:1 horizontally** (the painted width and
  the slice are the same number) and **squashed vertically** to the element. Its point keeps
  the art's fixed run while its rise becomes `h/2`, so its angle is `atan(2 x point / h)` —
  which equals the clip's only at the height the art was cut for.

So one shared file cannot serve plates of different heights. `tools/obs.py` cuts one per
consumer and `frame_cap` derives each cap as `point + 2 x rim_width`, rounded up:

| file | height | cap |
|---|---|---|
| `frame_matchup.svg` | `[standby] team_h` — the original band | 44 |
| `frame_plate.svg` | the slab composition's name plate | 30 |
| `frame_unit.svg` | the container composition | 36 |

Add a plate at a new height and it wants its own file and its own derived cap; that is the
whole of the system. **Nothing about a cap belongs in `layout.toml`.**

**Why this exists.** The cap used to be `name_cap`, authored by hand, and it was the one
number in `[matchup]` that could not be scaled. Three 10% passes walked it 44 → 40 → 36 → 32,
under the 35.1px point it was slicing, so the slice cut the diagonal and the leftover slope
was stretched the length of the bar (user, 2026-10-26: "The drawing is completely wrong now").
The silhouette stayed right the entire time — which is exactly why it read as the plates
changing rather than a number being wrong. Nothing caught it because `matchup_frame_svg`
asserted its cap held its point using the **standby's** numbers, which never moved.

`tools/test_obs.py` now checks every committed frame: cut for the height it serves, cap
holding its point with room for the rim, and the spec handing out the cap the art was cut
with. It has been confirmed to fail on the original bug rather than merely passing.

Both spellings of a query work — `/?band=unit#/source/matchup` or
`#/source/matchup?band=unit`. The app is hash-routed, so `location.search` is empty in the
second, and reading only that served the original band without a word (user, 2026-10-26). The
flags are read once at load: changing one in the address bar needs a reload, which is what a
browser source does anyway.

**`?band=slab` is the one to come back to** if the container is ever abandoned. It was the
best of the earlier attempts because the
hexagon-and-plate silhouette has a problem that four passes of tuning could not fix: a bulge
(the badge, 190 wide against a 110 plate), a shaft (the plate), and a taper (the inner
point), mirrored and converging on the middle. It reads as a key, and less charitably than
that (user, 2026-10-25). Flattening the outer edge made it worse, not better, by removing the
one thing keeping the shape symmetric — which is usually the shape saying the arrangement is
wrong rather than the details.

Its numbers are `layout.toml`'s `[matchup]`, worked out into boxes by `matchup_spec` and read
by `src/components/MatchupSlab.jsx`.

### What was wrong with the band

Two things, both measured rather than felt:

- A team container is **576 x 130 carrying one line of text**, where the in-game name plate
  carries the same thing in 374 x 63 — three times the area for identical content.
- The two logo arms spend **1152px, 60% of the screen's width**, on event branding at the
  extreme edges, while the teams get the middle. The eye goes to the edges and finds a
  tournament logo where it expected to find out who is playing, which is what the pushback
  was about.

So the teams come to the centre and take a logo, and the two arms collapse into the one
`<broadcaster> x <tournament>` lockup the scores screen already uses.

### The one-container team (`?band=unit`)

One shape a side holding everything that team is, instead of a hexagon badge standing beside
a plate (user, 2026-10-25: "the one container idea might be best"). Outward to inward: the
**series score**, a **parallelogram for the logo**, then the **name** running in to the VS.
The container is **pointed at both ends**, the outer one mirroring the inner, so nothing
protrudes from it — which is the entire point.

The score lands here almost by accident, and that is the nice part: the space between the
logo and the outer border was going spare (user's suggestion), and a score retrofitted after
the geometry had set would have meant moving everything.

**The logo fills its plate**, `fit="cover"` with the slant clipping the overflow, exactly as
the game scene's logo plate does it (user, 2026-10-25). Contained inside the parallelogram's
straight-sided rectangle instead, the mark sat in the middle of a panel with the shear's
worth of empty slope either side.

**And it only takes room if there is one.** No logo, no panel — not an empty one holding its
place (user, 2026-10-25). That is why the container has no width of its own: it is anchored
by its **inner** edge and sized by its contents, so a team without a logo simply gets a
shorter band. Anchoring at the VS end is what keeps the middle of the graphic still while the
two sides differ. Measured with blue carrying a logo and red not: blue 142–888 (746 wide),
red 1032–1558 (526), a difference of **220** — exactly the panel — with both inner edges
unmoved.

**Two geometry traps, both the same trap.** A sheared or tapered shape's usable area is not
its bounding box:

| shape | bounding box | actually usable |
|---|---|---|
| hexagon badge (slab) | 190 x 220 | an 110px square |
| logo parallelogram (unit) | 220 x 140 | 116 x 112 if the mark is *contained* |

The parallelogram leans by `lean x height` = 75.6, and that comes off the width *twice over* —
once deciding how wide the panel has to be before it reads as a plate rather than a diagonal
strip, and again deciding how much room is left inside it. At 180 wide the logo got 76px.

**The slant runs the game's way.** The first cut had it mirrored (user, 2026-10-25). Checked
against `frame_svg` rather than by eye: its plate is `0,0  w-d,0  w,h  d,h`, so the top edge
is the left-shifted one and the left edge runs **down and right**. Blue takes that, red is
its mirror — as in the game bar.

**Both ends are points, and that is why it needs no special-casing.** The slab's plate was
flattened on the outside to meet the hexagon's vertical edge; this arrangement has no
hexagon, so there is nothing for a flat edge to match and the shape goes back to symmetric.
A band that ends on a straight cut with a point at the other end reads as something gone
wrong — "looks like a mask issue" (user, 2026-10-25).

Being symmetric pays for itself three times over: **one** clip serves both sides (only the
wash and the row's direction differ), **both** ends take the frame's own nine-slice cap
rather than one needing a hand-rolled rim, and the cap art is a point, which is what the
frame was drawn for in the first place.

The score is inset past the outer point so the clip does not take a bite out of the digit.
The cap has 44px to hold a 37.8px point plus 2.5px of rim — 42.8 of the 44, so the container
cannot get much taller before `[standby] team_cap` has to grow with it.

**Known rough edge:** the kicker and the `mid` panel are still positioned against the *name
plate's* box, which is the slab's geometry. The container is taller (140 against 110), so on
this variant the kicker overlaps its top by about 15px instead of sitting on it. It wants
re-hanging off the container before this arrangement is judged finished.

### The shape

A team is **a hexagon badge and a name plate**. The hexagon is not a new shape: the series
pips are pointy-top hexagons, the lattice inside every plate is a hex weave, and Blizzard's
own centrepiece in the top bar is a hexagon. A plate pointed at both ends is a poor home for
a logo, which was the complaint; a hexagon is a good one.

**The plate's outer edge is flat, and it butts the hexagon** (user, 2026-10-25: "flatten the
outer edges of the nameplates to match the vertical edge of the team logo hexagons"). A
pointy-top hexagon runs straight down each side between h/4 and 3h/4 — exactly h/2 of it — so
`matchup_spec` gives the plate that height rather than a typed one, and the two meet edge to
edge with nothing overhanging. Measured: the badge's right edge and the plate's left edge are
both 447.77, and both span y 445–555.

Deriving the height matters more than it looks: a typed 120 would have stopped matching the
moment the badge was resized, and the badge has already been resized once.

Only the inner end, facing the VS, keeps its point. **Only that end gets a frame cap**, too:
the frame is the band's double-pointed nine-slice, so drawing both caps put a chevron of rim
across the flat edge where the hexagon is already drawing one. Two rims against each other
read as one doubled border, so the leading edge gives way — the kit's own rule, carried over
from the game plates.

The flat edge also bought the name room. The padding is asymmetric now (the flat side needs
only its own air, the pointed side needs the point as well), which widened the text box from
339 to 374 and took "Northwind Esports Academy" from 39px to **43**.

**Logos outboard, names meeting across the VS**, so you read "A vs B" straight through the
middle. The game bar puts its logo plate *inboard* only because Blizzard's hexagon occupies
its centre; that constraint does not exist here, and copying it would be inheriting someone
else's problem. The VS gets a hexagon of its own, which gives the middle weight now that the
lens flare is gone.

Reading order down the screen is **what this is, who is playing, who is bringing it to you**
— the kicker, the matchup, then the branding. Branding last, not first.

The kicker sits on **a plate of its own**: the old band's message board brought back (user,
2026-10-25: "the previous iteration of a edge-slant translucent box will work just fine
here"), in plain smoke rather than team colour so it recedes.

**One slant a side, flaring down.** Not a point at half height like the band's board — the
left edge runs down-left and the right edge down-right (user, 2026-10-25), so the plate opens
outward as it descends and lands on the matchup instead of tapering away from it. The flare
is the kit's lean over the plate's height (41.04 at 76 tall), so the bottom edge is
`kicker_w + 2 x flare`. Its box is the *wider*, bottom width and the top corners are cut in;
`kicker_w` in `layout.toml` is the top edge.

**It is attached, not spaced.** The plate's bottom edge *is* the name plates' top edge, both
at y 440, and `.fcjh-slab-mid` carries the same smoke on down behind the row at the plate's
bottom width. That fills the gaps the pointed plates and the VS leave between them, so the
kicker, the plates and the VS read as one shape rather than three things stacked near each
other. The effect is quiet by design — the plates cover most of it, and what it changes is
the gaps.

The lockup came up to a **12px** gap with 14px of padding inside its own box, so it reads as
the foot of the unit. The padding grows the box rather than squeezing the marks, which stay
at their full 72.

### Wrap, then shrink

`src/components/MatchupSlab.jsx`'s `useWrapThenShrink`, and the reason it exists:

**The framework's `fit` guarantees one line by shrinking.** It renders its own
`whitespace-nowrap` span with an inline font-size, and on a 25-character club name in this
plate it measured **23.8px against the 46 it was asked for — 48%**. That is the band's
complaint upside down: the container was never too big for its content, the content was being
crushed to half size to stay on one line.

So the name wraps to `name_lines` at full size first, and only shrinks if it still does not
fit, a pixel at a time down to `name_min`. Measured: "Tempo Storm Esports" sits at the full
**46px** over two lines, and "Northwind Esports Academy" shrinks only as far as **39px** —
not to the floor.

**Measure `offsetHeight`, not `scrollHeight`.** On this element `scrollHeight` reads about
11px over the laid-out height — 107 against an offsetHeight of 96 for two 47.84px lines — so
comparing it shrank a name that already fitted, and kept going until the text collapsed onto
one line, which is precisely the behaviour the hook exists to avoid.

### The plate's frame

**The shape is a clip, the frame is an overlay**, which is the band's own arrangement. The
first cut asked the nine-slice to do both with a 44px border on all four sides: on a 120px
plate that leaves 32px of content box, so the text was overflowing its own box and only
looked right because it was centred. Horizontal-only border (`border-image-width: 0 cap`), as
the band does it, and the plate keeps its full height for two lines.

The team wash is a **background layer, not a `::before`**: on a pseudo-element it was clipped
to the content box and drew as a hard rectangle inside the frame, ignoring the plate's points.
It is strongest at the **inner** end, so the two teams meet in their own colours across the
VS — strongest at the outer end just doubles up on the badge, which already carries the
colour.

### The badge chrome

Generated, not approximated: `hex_chrome_svg` draws the hexagon with the plates' own sheen
over its top half and their rim round all six sides, and the fill, wash and glow stay in CSS
behind it — exactly the arrangement `frame_svg` uses for the plates.

**It is not a nine-slice**, despite that being the obvious instinct. A nine-slice stretches a
straight middle and a hexagon has none, so slicing one shears its slants. It is drawn at the
size it is used at, which is also why the VS has a file of its own: scaling the badge's down
to 116px would thin its rim with it, and a thin rim beside a thick one is hard to unsee.

**No team line.** The plates carry a bar of team colour and the game bar's logo plate
deliberately does not, because "a bar of team colour under a team's own logo says nothing the
logo doesn't" (user, 2026-10-22). This is a logo plate, so the same holds — and it means one
file serves both teams, the colour arriving from the CSS behind it.

**The logo covers the badge and the hexagon clips it** (user, 2026-10-25) — `fit="cover"`
at the badge's full size, bleeding under the rim, which is why the badge carries no padding.

It went the other way first, and the detour is worth keeping because the geometry behind it
is still true: **a hexagon's usable area is not its bounding box**. Giving the logo the badge
minus padding had a square placeholder's top and bottom corners cut off by the taper, so it
was sized instead to the largest centred square that genuinely fits — inset the hexagon by
the padding (its apothem is W/2, so an inset of p scales it by (W/2 - p)/(W/2)) and solve
`s = 2WH / (H + 2W)`. That is correct for a mark that must sit *inside* the shape, and it is
also why the badge grew from 184 to 220: the square was only 87px, which read small, and 220
takes it to 110. Covering makes the square moot, but the badge size it argued for is the one
that stayed.

The badge is **1.83x the name plate's height** as drawn. Taller starts to overpower it.

### Still to do on it — moot

**This list is about the slab, which lost.** Kept for the reasoning, not as work:


- **The badge is sized against a placeholder square.** Most team crests are round or
  near-round, and a circle uses that inscribed square far better than a hard-edged square
  does, so it wants a look against real artwork before the size is final.
- **No series pips.** Scores were not a priority (user, 2026-10-23), but the pip art already
  exists from the game bar and the natural slot is outboard of each badge — which would
  widen the slab, so it wants deciding before the geometry sets.
- **Draft gets its own version** rather than sharing this one (user, 2026-10-25), which is
  what freed the composition from the bottom edge in the first place.

## The matchup band

A team container either side of a VS, a message board behind them, a logo arm at each
screen edge. Its shape is the old NGS board (`C:\FourCourtJester\Broadcasts\Heroes`,
`apollo/scenes/scene-afk`, 2018); its language is this kit's, so a container is the game
band's name plate grown up — the same lean, now coming to a point at half height, the same
chrome rim, wash and hex lattice. Its places are in `layout.toml`'s `[standby]`, which is
where it was born.

It lives in `src/components/MatchupBand.jsx` and carries its own numbers, so a scene that
wears it supplies only what goes on its message board. **`#/source/matchup`** is the band
by itself, over nothing. (Since 2026-10-27 the draft screen wears the container instead -
see [The draft screen](#the-draft-screen).)

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
only the fallback here. Checked on both sources: wide and square set draws the wide, square alone
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

It is the matchup container and nothing else (user, 2026-10-27: "we redesigned the Matchup
band in OBS; we now need to set it up in the Draft scene as well") - the same `MatchupSlab`,
in the same places, so a change to the matchup is a change here too. `#/source/draft`,
1920 x 1080, over the game capture. Those places clear Blizzard's player columns (x 14-358
and 1618-1896, down to y 922): the lockup runs x 449-1471.

The one difference is the **kicker**: Matchup's carries the standby message, Draft's the
**series** — "Best of 5", from `series.pips` — since standby says what is coming up, and here
there is no question of that, the teams are on screen drafting. No series set, empty kicker.
(If you want the standby message here instead, use `#/source/matchup`.)

### The cover — scrapped

**Dropped on 2026-10-26: "users can use their own covers."** Two attempts are in the history
and both were wrong the same way; the reasoning is kept below because it is the useful part,
not because a third attempt is planned.


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

**The victory mark**: a laurel branch either side of the name, in **laurel green**
(`[scores] win_mark_colour`, #2f8f4e). A hexagon version was drawn alongside it, shown, and
dropped unused (user, 2026-10-25: "Just go laurels"), so there is no longer a choice to
configure — the branch is the mark.

The green is light enough to read against the nebula; a true bottle green goes to mud on that
backdrop. **The glow stays the winning team's colour**, not the leaves': it is what ties the
branches to the name they frame, and a green glow on green leaves would just be a blur.

It is a **mask, not a picture**: the SVG is solid white and carries no colour, so one drawn
shape serves both teams and the colour is a one-line change rather than a redraw. A mask
takes no `text-shadow`, so the bloom is a `drop-shadow` filter on the shape. The mask URL is
literal in the stylesheet because Vite only resolves a `url()` it can see at build time — a
path assembled from the spec at runtime would be left alone and 404 on Pages. It is small
enough that Vite inlines it as a data URI rather than emitting a file, so there is no
win_laurel.svg in `dist/assets`, which is correct, not a missing asset.

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

**Not done: the electricity off the blue tiles** — the one the user filed as "harder".

**It was built on 2026-10-26 and scrapped the same day**, so read this before building it
again. The attempt drew it the way the rest of this sky is drawn: an SVG sprite of four
frames, stepped with `steps(4, end)`, bursting for 0.3s every 7.5s. On air it read as
**"noise on an old video tape"** (user) — which is what sparse white-cored flecks cut at
0.075s a frame look like, whatever they are shaped like. The fault was the *stepping*, not
the drawing: hard cuts between scattered small marks is television static, and the eye names
it that before it sees any lightning.

If it is picked up again, the lead is the other half of the source. `lightning1-4.dds` is the
flicker that failed; **`storm_ui_home_nexus_fx_tilelighting.dds` (1812 x 304) is a sweep along
the floor** — one travelling light, continuous rather than cut, which is the opposite motion
and would not read as static. A slow sweep that lights tile edges as it passes is probably the
effect that was wanted all along.

The raw material, either way: `storm_ui_home_nexus_lightning1-4.dds` (648 x 432, four frames)
and `storm_ui_home_nexus_fx_tilelighting.dds`, both under `references/`.

## Colour-blind colours

The game's colour-blind option turns the interface's red a peachy orange and its blue a touch
cyan (HANDOFF, the in-game half). A browser source can't read the game's options, so the
operator says: **Tournament → Colour-blind mode** (user, 2026-10-25; renamed from "colours"
on 2026-10-26, since it switches the art as well). Off is the resting
state.

- **The colours are the interface's own.** `tools/obs.py` writes
  `src/generated/colourblind.json` with the same rule the interface uses
  (`gen.colour_blind_cfg`: each team colour keeps its saturation and value and takes the hue
  of Blizzard's colour-blind pair), so OBS and the game can't disagree.
- **The hex lattice carries no colour at all.** There is one `lattice.svg`, drawn in white,
  and every stylesheet uses it as a **mask** and paints it in `--team-rgb` — so it follows
  whatever colours it is given, not just the two modes (user, 2026-10-25: "ensure all the hex
  mesh's are colorable by arbitrary colors that we provide").

  It was a coloured SVG per team, then per team *per mode* once colour-blind arrived: four
  files for two schemes, and a fifth the moment anyone wanted a third. A mask has no such
  arithmetic. The fade that used to be a black mask over a coloured image is now the colour
  itself — same alphas in a `linear-gradient` of the team colour — which frees the mask slot
  for the mesh and gives an identical result.

  Because `--team-rgb` already switches with the mode, the lattice needs **no colour-blind
  rule whatsoever** now; those were deleted along with the four files.

- **The frames carry no team colour either.** The only coloured thing in one was the team
  line along the bottom of a name plate, and that is now its own art (`frame_line_{side}.svg`,
  white) on its own element, masked and painted in `--team-rgb` (user, 2026-10-25).

  It needs `mask-border` — `-webkit-mask-box-image` in Chromium, which is what OBS runs —
  rather than a plain `mask-image`, for the same reason the frame needs `border-image`: the
  line is sheared, so stretching it whole would flatten the shear at the ends. Caps hold, the
  middle stretches.

  It also wanted an element of its own, because the plate's two pseudo-elements were already
  spent on the lattice and the chrome. That is the one markup change in this.

  With the line gone, `frame_{side}.svg` carries nothing team-specific, so **the logo plate
  now uses the same file** and `frame_logo_{side}.svg` is retired along with both `_cb`
  frames: four files down to two, and those two differ only by which way they lean.

- **The pips are the exception, and it is not ours to fix.** `pip_{team}_cb.svg` survives
  because the framework's `Tally` draws its marks from a `src` URL and takes no children and
  no render prop — so a pip's colour has to be in the file. Converting them would mean
  replacing `Tally` and losing its counting, filling and transitions. Filed upstream as
  entry 4 of `docs/single-studio-reports.md`.
- **One hook**, `src/components/colourBlind.js`: `useColourBlind()` reads
  `toggles.colourblind` (a `Toggle` writes to `toggles`, so it goes to air without a save).
  A scene root wears `cb` while it is on, and its stylesheet swaps the URLs; the washes and
  glows come from `COLOUR_BLIND` / `COLOUR_BLIND_VARS` in place of the spec's colours.
- **Covered:** the game bar (plates, lattices, team lines, pips), the matchup band on standby
  and the draft, the matchup slab in both its shapes (`?band=slab`, `?band=unit`; its root
  takes `COLOUR_BLIND_VARS`, 2026-10-25), the scores screen's winner glow. Browser-checked
  with the toggle on: every one reads the pair from `colourblind.json` (92 216 236 /
  231 131 92). Webcams and standby carry no team colour. **Left out on purpose:** the board's
  own lit Winner buttons (`fcjh-won`), which are the operator's, not the broadcast's.

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

- ~~**The Game scene's logos**~~ — settled 2026-10-26: the adjustment was a dark backing
  behind a mark in Blizzard's hexagon, for logos with a transparent ground. Built; see "the
  tournament's logo" in `game.css`.
- **Testing**: the user tests in OBS at 1080p, the broadcast's settings; Claude checks
  in a browser at 1920 x 1080. **Claude's image library is empty**, and that is not a
  neutral fixture: anything whose width comes from library content - every `<select>` of
  asset keys - measures far narrower here than on a real show. It hid a picker bug on
  2026-10-23 that the user saw at once; one realistic key (35 characters) was the whole
  difference. Inject one before trusting a width measurement. See
  `docs/single-studio-reports.md` entry 2.
- ~~**Ban portraits**~~ and ~~**the ban tiles' shape**~~ — **scrapped until a further design
  pass** (user, 2026-10-26). The panel was already shelved; it stays shelved, and nobody
  needs to go looking for 90-odd hero portraits in the meantime.
- ~~**The font**~~ — settled 2026-10-26: Saira Semi Condensed stays. It is fetched from
  Google Fonts at load. (Blizzard's own is a cut of Metronic Pro, whose licence would need
  checking if that ever changes.)
- ~~**The standby screen's slides**~~ — settled 2026-10-26: the arrangement is right as it
  is. They come from the image library's `slides/` group; dropping a folder named `slides`
  on the library files the lot in one motion. Two throwaway test gradients are still in
  there (`slides/one`, `slides/two`) — delete them when real art arrives. Note that **files
  are added on the machine running OBS**: a picture dropped on a producer's laptop has bytes
  that live only there, and the slideshow leaves those out rather than playing a blank.

- **The scores screen's tile electricity** is the one piece of its brief not built; see
  "What stands around the hole" above for the frames already extracted for it.

  All four references are 1920 x 1080 JPEGs. Their edges carry compression ringing, so
  treat every number above as ±5px — good enough to place a band, not good enough to
  commit to `layout.toml`. That should come from the extracted UI under
  `references/JamiePhan`, the way the top bar's did, with these as the check.
