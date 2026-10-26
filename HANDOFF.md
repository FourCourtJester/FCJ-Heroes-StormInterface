# FCJH — Handoff

Custom `.StormInterface` observer overlay for Heroes of the Storm, for esports/broadcast use.
Written for whoever picks this up next, human or model.

---

## 1. Where things stand

**Fresh start, 2026-09-25.** The first attempt (builds 1–50) proved nearly every technique
we need but drifted, because no one had drawn the target screen. It is archived, not lost:
build 50 lives in git history and as the validator's test fixture
(`tests/fixtures/build50/`). Everything it taught is in §3 and §6.

**The design is agreed** and lives in a canvas of to-scale wireframes:
**https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK** — the stock UI annotated, then the
build as it stands: the default view at 1920×1080, the spec table, the plate anatomy, the
info panes, the inspect card, the top bar, every map's minimap and banners, and the
visual-language agenda for the art pass.
Those boards are drawn from the build's own numbers by `design/canvas_gen.py` (it imports
`tools/gen.py`; it's tracked, the rest of `design/` isn't): after a layout change, run
`python design/canvas_gen.py` and publish `design/canvas/project/` to the canvas.
**Every build is checked against it.**

In one paragraph: the ten hero cells sit along the bottom (blue 1–5 left of the minimap,
red 6–0 right of it) with portrait, HP, mana and CC; the minimap and its objective widgets
at bottom-centre; team core HP above the cells; a two-line top bar of series score, team
name, logo and level either side of Blizzard's hexagon, with bans, division and game count
beneath; Blizzard's own kill feed top-left; replay controls top-right; four operator keys, Ctrl+Shift+R/C/I/N, toggle the replay controls,
chat, inspect card and player names (layout.toml `[toggles]`); info panes
(talents, KDA/damage, healing/siege/XP, XP contribution) at middle-left on hotkeys; talent pop-ups on the
cells, and a green-plus pop-up on any hero below 25% health (drawn under the talent
pop-up). **There is no fight mode** (user, 2026-10-16: the spec has moved past it) - the
default view is the old fight-mode cluster, and the operator's toggles hide what needs hiding.
The top bar and minimap always stay.

**OBS draws the data AND the plates under it** (user, 2026-10-22, superseding "data only,
never art" of 2026-10-16): team names, logos, series score, the tournament's name, division
and logo, and the game's bans. Nothing on the bottom UI. The interface keeps only the
**places** - `kind = "obs"` rects in `layout.toml` (§6, docs/obs.md) - so with no OBS running
the top bar is the level wings, Blizzard's hexagon and the clock, and nothing hangs off them
empty. That is why the division and game tabs were built in game on 2026-10-22 and reverted
the same day.

**Status, 2026-10-18: Phase 2 (building the default view) is all but done** - every map passed, every hero seen, the polish phase under way (§7 item 7); the final pass, the art pass and OBS are left (§7). Phases 0
(toolchain) and 1 (probing the unknowns) are done. Built, and confirmed in game unless noted:

- **Hero row** — Blizzard's *in-game* top-bar cells, slanted and interlocking, scaled to fit
  the screen's 20 px padding (`[hero_row] scale = "fit"`, 1.5561): portrait, health,
  resource bar in Blizzard's per-hero colours, CC text and icon, death timers (per-Viking
  ones in each third), Viking bars in thirds, Rexxar's bar full height (Misha's hidden),
  the **fountain** (after the inspect card's buff slot, our own frame and mask at the plate's lean, dark
  purple backdrop, bright when ready, dimmed with its countdown on cooldown; on the health
  bar's black outline at the plate's OUTER end - blue left, red right; `fountain_rect`),
  Abathur clone marker, and Blizzard's in-game heroic panel at the plate's INNER end (blue
  bottom right - the mirror of Blizzard's red - red bottom left; bars narrow from its side;
  icon, frame, ready glow, cooldown count and dim; Tracer's Pulse Bomb charge instead of a
  cooldown), with the heroic's **tooltip** on hover. Settled with the user 2026-10-06 over
  seven rounds of screenshots (the canvas plate board draws it from gen.py). Clicking a plate selects the hero and
  follows it (with the game's camera lock, **L**, on).
- **Team XP** along each row's top edge and **core HP** above it, cut to the slant; hidden
  until a team's first hero loads; rows pack toward the minimap with fewer than five heroes
  (untested: §7 item 14).
- **Top bar** — Blizzard's hexagon and clock on our generated chrome backplate (`[top_backplate]`),
  team levels, Blizzard's talent-advantage flame when a team is a tier ahead.
- **Pop-ups** on the plates — the talent just picked, and a green plus when a hero drops to
  25% (once per dip, gone after ~4 s or at death or above 30%).
- **Info panes** — talents (in Blizzard's observer talent grid), KDA/damage, healing,
  structures/XP: one at a time on `Ctrl+1-4` (Blizzard's own panes lose Ctrl+1/2), each
  with an X, in the inspect card's skin; the leader in each column softly highlighted.
- **Inspect card** — for a hero: portrait, name/player/level, fountain, bars, buffs,
  Blizzard's own command card (tooltips, cooldowns, charges; empty Q W E R slots framed),
  talents (with tooltips) and stats. For anything else, a short card: name, team, health,
  buffs, stats. Edge in the unit's team colour (purple for neither team). Shows exactly when
  the default UI's small inspector would (never while a replay is paused). Medivh's Raven and
  D.Va seen right; the other forms are in the final pass (§7 item 14).
- **Kill feed** — Blizzard's own, top-left. **Minimap** bottom-centre, placed per map with
  each map's objective panel round it and a team's banners on its side; every map passed
  2026-10-15/16, told apart from load by Blizzard's map id ([docs/maps.md](docs/maps.md)). **Replay controls**
  in the top-right corner, [screen] padding in (red's row until 2026-10-16), 231 px with its
  four buttons evenly spaced; Ctrl+Shift+R slides them out to the right (Blizzard's
  Ctrl+Shift+O is taken by the game), leaving a tab flush in the corner (replays only). Hiding
  the timeline (the chevron, or Ctrl+T) keeps the box's top in place; it can't be made to
  start hidden. All confirmed in game 2026-10-16 - DONE. **Operator toggles** (layout.toml
  `[toggles]`, 2026-10-16): Ctrl+Shift+R replay controls, Ctrl+Shift+C chat, Ctrl+Shift+I
  inspect card, Ctrl+Shift+N player names over the heroes - none a Blizzard key (validate.py
  checks; I slides the card off screen to the left). All four confirmed in game 2026-10-16 - DONE. Blizzard's player HUD never shows; its
  talent picker is left to the game: held Ctrl shows it, steady, only in a player's view
  (1-8 keys), not when following from a plate click - as in Ahli's and Spazzo's UIs (§3;
  confirmed 2026-10-06).

Not yet: the visual pass that takes the chrome look of the top bar to the plates, bars and
panes. **The broadcast graphics are their own vein of this repo** (2026-10-22): `studio/` is a
[Single Studio](https://github.com/FourCourtJester/Single-Studio) app - an operator's board in
an OBS dock, a browser source per graphic - and `tools/obs.py` writes its parts and numbers
into `studio/src/generated/` from the same `layout.toml` the interface comes from. The top
OBS band's **places** are in the build since 2026-10-22 - layout.toml `[top_bar]`, every box
derived by gen's `top_bar_geometry`, so the interface and the OBS layer can't drift apart.
docs/obs-topbar-handoff.md has the rule.

**The studio builds and runs (2026-10-23).** Node is installed; `npm run dev --prefix studio`
serves the board and every graphic. It is on **Single Studio 0.13.0** (core and
provider-supabase), which is additive on the control side - nothing of ours broke. Seven
browser sources now:

| | |
|---|---|
| `#/source/game` | the top bar over a live match |
| `#/source/standby` | between games: a drifting slideshow and a countdown bug |
| `#/source/matchup` | the "coming up next" band on its own, transparent |
| `#/source/draft` | the same band over Blizzard's ban-and-pick screen, with the series on it |
| `#/source/scores` | over Blizzard's end-of-game Stats screen: a moving sky with the panel showing through, the winner's name above it and the two marks below |
| `#/source/webcams` | two camera frames, borders only |
| `#/source/webcam-solo` | the same frame once, centred |

The matchup band and the webcam frames are rebuilt from the user's own 2018 NGS broadcast
(`C:\FourCourtJester\Broadcasts\Heroes`) - its composition, this kit's language. The band is
its own source rather than part of the standby screen because the two are wanted at different
times: the backdrop stays up for a whole break, while the band is brought in, lands, and is
brought in again later in the cast. The operator's board is five collapsible panels, folded
on load, in the running order of a show: **Standby, Webcams, Teams, Tournament, Help** (user,
2026-10-23). The Options panel is gone - it held one switch, and the switches now sit under
the marks they turn on. Help is the directions for whoever is wiring OBS, on the board rather
than in a file they would have to know to look for.

**`studio/README.md` is the detail** - every scene, every number, how a camera and its OBS
mask go together, and what is still open. Read it before touching `studio/`. Two rules there
that cost time to learn: `/studio` owns the whole broadcast package (`tools/obs.py` may write
pictures and a numbers JSON and nothing else), and nothing in the webcam sources may animate,
because OBS cannot move the cameras underneath them in step.

**`docs/single-studio-reports.md`** is a running log of framework behaviour we had to work
around, for filing upstream against Single Studio. Three entries so far, all measured.

**`three-veins` shipped as 1.0.2** (2026-10-23): pushed, merged to `main` by PR #1 (merge
ea6f493) and released by CI. The broadcast half is on `main` and on Pages; the branch is
spent, and the next broadcast work starts from `main`.
**Testing (2026-10-23):** the user tests in OBS, at 1080p, the broadcast's settings;
Claude checks in a browser at 1920x1080.

§7 has the interface's open list; the broadcast half's is at the end of `studio/README.md`.

---

## 2. The loop

```
python tools/pack.py --wait
```

One command: **generate → stage → validate → pack → deploy.**

1. **generate** — `tools/gen.py` rewrites the committed generated layouts from `layout.toml`,
   and `tools/obs.py` the broadcast studio's parts under `studio/src/generated/` (one set of
   numbers, both halves; `gen.py --check` fails on either being stale)
2. **stage** — `interface/FCJH.StormInterface/` is copied to `build/<profile>/`. A dev build adds
   the build stamp there, and only there (the wireframe overlay was removed 2026-10-05)
3. **validate** — `tools/validate.py` on the staged tree; an error stops the build
4. **pack** — an uncompressed MPQ v1 archive, read back and compared file by file
5. **deploy** — `Documents/Heroes of the Storm/Interfaces/FCJH.StormInterface`

**With the client left open** (all confirmed 2026-09-25):

1. Launch Heroes **from the Battle.net app**. Double-clicking a replay goes through
   `HeroesSwitcher`, which has no auth token — that is the password prompt that never remembers.
2. Open a **current-patch** replay from the in-game Replays tab (§5).
3. Edit, then `python tools/pack.py --wait`.
4. Leave the replay. The file is **locked while a replay is open** and writable at the main
   menu; `--wait` retries, so the build lands the moment you exit.
5. Reopen the replay. **The game re-reads the interface on every replay load.**

**Profiles.** Dev (the default) shows a build stamp — `FCJH DEV <version> <commit>[+] <time>`,
`+` meaning uncommitted changes — and nothing else (the wireframe overlay that tinted
each box in its legend colour was removed 2026-10-05). `--release` is exactly what `interface/` holds: it refuses
while `interface/`, `layout.toml` or `tools/` have uncommitted changes, so every release is
reproducible from its commit, and writes `dist/v<version>/FCJH.StormInterface`
(`--deploy` to also install it), zlib-compressed by sector as Spazzo's is (10.7 -> ~1 MB; dev
stays raw; a compressed release loads a replay fine, user 2026-10-21). GitHub releases ship that file and nothing else of ours: push a tag `v<version>`
(it must match `[meta] version`) and `.github/workflows/release.yml` builds it from the tag
with `--no-generate --no-validate` (gen and validate need the JamiePhan extract, which isn't in
the repo, so run both locally first: the committed `interface/` is what ships) and publishes it.
`.gitattributes` checks `interface/` out LF on every clone, so GitHub's build is byte for byte the
local `--release` (checked from a fresh clone, 2026-10-21). GitHub adds its own source zips to every release; they can't be removed.

### Tools

| Command | What |
|---|---|
| `python tools/pack.py --wait` | The loop above |
| `python tools/gen.py [--check]` | Regenerate; `--check` fails if a generated file is stale or hand-edited |
| `python tools/validate.py [--show <frame path>]` | Validate `interface/`; `--show` prints the merged tree under any frame |
| `python tools/test_validate.py` | 19 validator tests against the build 50 fixture |
| `python tools/mpq.py list\|extract <archive>` | Inspect any archive, including Ahli's and Spazzo's |
| `python tools/make_test_ui.py` | Smoke test: a magenta box as `FCJHTest.StormInterface`, to tell "packer broke" from "layout broke" |

**The validator** rebuilds the GameUI frame tree the way the game does — Blizzard's layouts
from the JamiePhan extract in DescIndex order, templates expanded, `file=` overrides applied
— and checks what our files contribute. Errors: unparseable XML (the game silently drops the
*whole* interface), undefined constants, missing templates or override targets, frame
references that resolve to nothing, malformed anchors, and edits to Blizzard children that
don't exist (the game silently creates an empty frame). Warnings: parking a frame others
anchor to, anchoring a side Blizzard re-anchors at runtime, `Visible=false` on Blizzard
frames, `Fill` without `AdjustmentColor`, partial constants, type mismatches. The Java
builder it replaced checked far less — its anchor validator was `TODO` stubs.

---

## 3. Authoring

**The user never touches XML.** Their surfaces are `layout.toml`, the wireframe canvas, and
the game. Describe effects, not diffs; verify with screenshots.

```
layout.toml                                  every placement number and look setting, in PIXELS
tools/gen.py                                 turns it into layouts and textures
tools/inspect_card.py                        the inspect card (reads hero data from JamiePhan)
tools/maps.py                                each battleground: minimap place, panel, team alerts
interface/FCJH.StormInterface/                     the archive's file tree, one to one
  Base.StormData/UI/Layout/
    DescIndex.StormLayout                    GENERATED — every layout, constants first
    FCJH_Constants.StormLayout               GENERATED — layout.toml in layout units
    FCJH_HeroRow.StormLayout                 GENERATED — cells, heroic panels, pop-ups, row packer
    FCJH_StatPanes.StormLayout               GENERATED — the three numbers info panes
    FCJH_Inspect.StormLayout                 GENERATED — the inspect card
    FCJH_Maps.StormLayout                    GENERATED — each map's minimap place, panel, team alerts
    FCJH_*.StormLayout                       hand-written, one per concern (top bar, hidden
                                             HUD, talents pane, kill feed, minimap, replay)
  _Assets/Textures/FCJH_*.dds                GENERATED — slanted bars, masks, the top backplate
interface/dev/                                     dev-only layouts (none now; packed into dev builds only)
```

- **Layout units are not pixels.** The game lays out on a 1200-unit-tall grid, so at 1080p
  **1 unit = 0.9 px** on both axes (the screen is 2133 × 1200 units). Build 50 proved it:
  slots set 102 units apart measured ~92 px. `layout.toml` holds pixels straight off the
  wireframe; `gen.py` converts. Never hand-convert.
- Every element becomes constants `FCJH_<NAME>_L/_T/_R/_B/_W/_H`, edges measured from the
  screen's top-left — anchor them to `$GameUI` with `pos="Min"`. Hero cells are
  `FCJH_HERO_1` … `FCJH_HERO_0`.
- **Generated files are committed** and carry a do-not-edit header; `gen.py --check` catches
  hand edits. Hand-written XML for one-off structure (it maps one to one onto Blizzard's and
  Ahli's files); Python generation for anything arithmetic or repetitive.
- **Frames we add carry the `FCJH_` prefix.** The validator relies on it: an unprefixed child
  that doesn't exist in Blizzard's tree is an error, because the game would silently create
  an empty frame. Constants are global across all files, so ours are `FCJH_` too.
- Split layouts by concern, not one file.

### Banners: two protocols, no hand copies (user, 2026-10-12)

Every map banner is made by one of two builders in `tools/maps.py`. A new map only supplies its
measured constants. If a banner needs something the builders can't do, extend the builder rather
than writing a per-map copy.

- **Neutral banners** sit on red's side and go through **`left_banner`**. It lays the banner out
  from the bar's tip at red's plates: the words come first, then the count, then the hexagon.
- **Team banners** (curse, Dragon Knight, Terrors, cannons) appear on the owning team's side and go
  through **`team_banner`**. The layout is written once, in red's terms, as distances out from the
  tip (`Side`).
  - Red's side is a left banner.
  - Blue's side is a right banner: the mirror, with the tip at blue's inner edge and the art
    flipped at the outer end. Flipped copies come from `flipped_copy`, used when Blizzard holds the
    image by one side.
  - Where blue can't be a plain mirror, `Side.pick` says so beside the reason. For example, a
    status bar's fill won't flip, and text still reads left to right.
- **Tips:** the tip is each spot's inner edge. The bar image starts `BAR_TIP_IN` (3) past it. All
  banners use the same art.
- **No banner changes size while it counts.** Each count sits right-aligned in a slot as wide as
  the game's own sizing text ("8:88", or "88" for bare seconds), and the art hangs off the slot.
  Width varies only with the language.

### Rules learned the hard way (all confirmed in game)

- **Park, don't hide.** `Visible=false` does not stick on Blizzard panels; move the frame
  off-screen, pinning all four anchors.
- **Parking a frame drags anything anchored TO it.** `HeroPortraitImage` anchors to
  `IconFrame`; parking `IconFrame` sent all ten portraits off-screen for three builds. Hide
  such frames with `Alpha 0`. (The validator now warns.)
- **Render order follows the frame TREE; `RenderPriority` only sorts siblings.** Frames added
  to `GameUI` paint above everything in `UIContainer`. To sit behind a Blizzard frame, inject
  beside it inside its own hierarchy.
- **The base UI binds no player to the hero cells** — the engine fills them by ordinal
  position. Addressing heroes by `PlayerId` is a different axis. Inherit, never rebuild (§6).
- **Blizzard StateGroups can `SetAnchor` at runtime**, overriding our anchors (e.g.
  `HeroDeathTimeLabel`). The validator warns.
- **`#Constant` substitutes only as a whole attribute value.** `Fill` reads `AdjustmentColor`
  (`A,R,G,B`), not `Color`.
- **`ObserverTopPanel` is load-bearing for the portraits** — park only its art.
- **Duplicate frame names are everywhere** (`PartyFramePanel` has its own `Team1HeroOverview`).
  Confirm ownership by displacing a frame, not by matching a name.
- **Hidden frames don't run their animations**, and a StateGroup is **not reliably
  re-evaluated when an animation flips a frame it watches**. Timers live on visible frames;
  never make a state transition *wait* on an animation-driven flag (nine heal pop-up rounds).
- **To follow a Blizzard frame's visibility, park it (+ Alpha 0), don't force it hidden** —
  a looping Visibility animation also erases the signal (the inspect card follows the default
  UI's inspector this way).
- **A paused replay opens no inspector.** Clicking a unit while paused selects nothing new, so
  the inspect card can't appear; a selection made before pausing stays. Test inspect unpaused
  (an evening went on a "regression" that was this, 2026-10-02).
- **Restating a Blizzard StateGroup by name overrides it** (Rexxar's bar, `HeightOverride`).
- **`IgnoreParentAlpha` doesn't reach through an Alpha-0 ancestor several levels up.** To lift
  a piece out of a Blizzard panel, keep the panel at full alpha and fade its other pieces leaf by
  leaf. The observer talent row also starts hidden (`CleanTalentsPanelTemplate` Visible false)
  and the game keeps it so: a looping Visibility animation on an always-shown ancestor plus
  `Batch false` makes it draw (Tracer's meter, `talent_row_lifts`).
- **Property conditions take `operator=`** (`LessThan`, `NotEqual`...), but label text still
  compares as text; the heal sensor matches the health percent string by string.
- **In the observer, selection is what locks the camera to a hero.** Keep Blizzard's click
  behaviour on the plates.
- **Tooltips come from Blizzard's own tooltip-bearing frames**, and only in their own layout:
  - the game's observer talent row never gives tooltips; our OWN copy of it does
    (`TalentsOverviewTopBarTemplate`), but an icon moved outside its player's box gives none —
    move the box (`HeroTalentsPanelPlayerFrame`, by its Left anchor), not the icon;
  - an icon can be re-sized in place (Width/Height) and still give its tooltip;
  - a faded icon still answers the mouse: fade AND switch mouse and tooltip off (`muted`);
  - a frame with mouse off but tooltips on still swallows tooltips under it;
  - an ability icon (ours, or the row's `UnitStatusAbil`) showed none;
  - a plain frame can carry text: `<Tooltip val="@Button/Tooltip/..."/>`; Ahli composes
    headers with a `TextFormatFrame` (`FormatText` + `Replacement`) bound as `{.../@Text}`.

**Blizzard's talent picker can't be hidden while Ctrl is held** (2026-10-06, a morning of
tries). In a player's view (1-8) held Ctrl opens it (`FloatingCombatUnitSelectionPanel/
UnitStatusFrame0/HeroTalentTreeSelectionPanel`, the frame Ahli moves above his hero card) and
the engine re-asserts it every frame: a Visibility loop, Fade loops on it and on its parent,
parking it (it came back on screen at the top-left), stopping its Show animation, parking or
fading its parts, and emptying its template each lost, and fighting it made it FLICKER. Ahli
0.75 and Spazzo leave it be and it sits steady while Ctrl is down. So do we now (FCJH_Hidden;
seen steady 2026-10-06, and only in a player's view from the 1-8 keys - following a hero
from a plate click never shows it).
The diagnostic that settled it: marker squares stuck inside the frame (IgnoreParentAlpha) plus
latches on each suspect's Visible - a quick flick needs latches, not screenshots.

### The inspect card's abilities: Blizzard's command card (2026-10-02..05)

The card's ability rows are Blizzard's own command card (`ConsoleUIContainer/CommandPanel`),
borrowed as Ahli does for his hero card: real tooltips, cooldowns, charges, talent actives
and the right R for every hero, with no per-hero tables. Code: `tools/inspect_card.py`
(`command_switch`, `command_anchors`, `command_panel`, `placed`, `tracer_charge`). What it
took, all seen in game:

- **Same container, one step under it.** The card lives in `ConsoleUIContainer` at
  RenderPriority 600, the command card at Blizzard's 610. At 650 in GameUI the card drew over
  the buttons and its back took their mouse.
- **Never hide it; park it.** One frame (`FCJH_CommandShown`) holds `CommandPanel` shown with a
  looping Visibility animation (the game shows and hides the HUD as it likes). The card's gate
  moves it onto the card when the card opens and off screen (9999) when it shuts. Showing and
  hiding it with two loops, one per side, never showed it: a stopped loop seems to keep its
  last value.
- **Size by Width/Height, not opposite anchors.** Blizzard's templates set 1060 x 190 (panel)
  and 120 x 120 (buttons), and those beat Left+Right / Top+Bottom anchors: anchored on four
  sides, the buttons stayed full size. `placed()`: Top/Left anchors, Bottom/Right tied to
  `$this`, explicit Width/Height (Ahli's way).
- **Every piece drawn for 120 units needs resizing** (Ahli's numbers): button 52, icon
  (`NormalImage`) inset 5, frame art (`GameButtonDefaultBorder`) 68 - it has no size of its own
  and takes its texture's - glows 60, `IconBackground` inset 5 (only the ability buttons
  00-03 and 05 have one), charge badge 20 and ring 30, the cooldown count in our
  `FCJH_HeroicCooldown` style, hotkey letters off (they piled onto the icons). Each button's
  hero-specific panel (`HeroSpecificCommandCardPanel`; `ButtonSpecificOverlayPanel` on the
  dynamic buttons) is 120 x 120 too and is sized to the button.
- **Layout, Blizzard's order:** top row the dynamic buttons 30-35 (talent actives); bottom
  row 04, 00, 01, 02, 03, 05 = Z Q W E R D (seen in game), 47 apart so the hexagons
  interlock. Put away (parked, faded, mouse off): hearth 13, spare 15, `MiddleFill`, the
  empty-slot art, targeting prompts, tutorial arrows.
- **The mount (04) is one wide "bookend" piece** (83 x 54) whose art is anchored to its
  edges: it gets its own 56 x 36 shape, centred in its row, and only its hotkey letter put
  away. Squeezed to 52 x 52 with our 68-unit frame art it read far too big.
- **Tracer's R is her own hero file's meter**, not the button's art: overridden by name in
  her layout (`file="Tracer"` `TracerPulseBombChargeButtonOverrideFrame`) at the button's
  size, the "0%" label off and the count centred (ChargesLabel anchored on all four sides to
  her meter's background, our cooldown style - seen 2026-10-05, matching her other buttons).
  The validator loads every hero mod so such overrides are checked.
- **Two Blizzard panels hang off the command card** - `ControlGroupPanel` and the console's
  own `HeroSpecificCommandCardPanel` - and go wherever it goes (parked with it).
- **Forms and gaps:** the card follows the SELECTED unit and never swaps (Abathur in Symbiote
  keeps his own, as in Ahli's and Spazzo's). His "gap" is his own missing E, now Blizzard's empty
  frame over a dark hexagon (`command_panel` empties). Forms: docs/history.md item 3, §7 item 14.

### Practices

- **Keep the build stamp.** A stale stamp means a cached interface; nothing else on screen is
  evidence.
- **Displace, don't guess.** After two unexplained builds, move each suspect somewhere obvious.
- **Colour a frame garishly before concluding it doesn't render.**
- **One change per build.** Stacked unverified builds produce an unattributable mess.
- **`python tools/validate.py --show <path>`** before guessing what a frame is anchored to.

---

## 4. Reference material

- **`references/JamiePhan/`** — shallow clone of
  [jamiephan/HeroesOfTheStorm_Gamedata](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata),
  an automated extract of Heroes game data, currently **2.57.0.98304**. The validator's
  source of truth. Refresh with `git -C references/JamiePhan pull --depth 1`.
- **`references/Galaxy-Observer-UI-HeroesFix/`** — Spazzo's fork of Ahli's (retired) builder.
  Its `tools/plugins/mpq/MPQEditor.exe` is an independent check of our archives
  (`MPQEditor.exe e <mpq> * <dest> /fp`).
- **`references/AhliObs.StormInterface/`, `references/Spazzo/`** — two mature observer
  interfaces, unpacked. Ahli's is MIT. Most techniques here came from reading them.
- **`references/AhliObs075/`** — Ahli's 0.75, the version the user runs and our visual
  benchmark ("Heroes-like": polished, familiar; don't drift far from it). It's minified:
  pretty-print before reading. Worth taking from it: his hero card's abilities are Blizzard's
  own `CommandPanel` (native tooltips, talent actives 1-5, the right R for every hero);
  `TextFormatFrame` tooltips; Tracer's segmented ammo bar and round Pulse Bomb meter (Blizzard
  templates, `_ColoredManaBars` / `_BottomLeft`).

`references/` is gitignored. Key base-UI files, under
`references/JamiePhan/mods/core.stormmod/base.stormdata/ui/layout/ui/`:

| File | What's in it |
|---|---|
| `gameui.stormlayout` | The root frame tree and most handles |
| `stormobserverpanel.stormlayout` | Observer top bar, hero cells, team containers, core HP, levels |
| `partyframe.stormlayout` | Player HUD top bar — has `TeamTalentAdvantageFrame`, the talent-lead flame (line 3268) |
| `unitstatus.stormlayout` | World nameplates, CC validators, buff/debuff element |
| `heroconsole.stormlayout` | Bottom-left portrait/stats cluster |
| `talentsoverviewpanel.stormlayout` | Talent tier grid |

---

## 5. Environment gotchas

**Interface selection lives in TWO files**: `Documents/Heroes of the Storm/Variables.txt` and
`.../Accounts/<id>/Variables.txt`, keys `observerinterface=` and `replayinterface=`, full
filename with extension. Edit only while Heroes is closed — it rewrites both on exit (it
blanked the top-level keys and kept the account file's on 2026-09-25). Set both.

**Out-of-patch replays wipe the selection** via a client version switch — five times so far.
Keep a current-patch replay; an AI-vs-AI custom lobby you observe produces one.

**File lock**: the selected interface is locked while a replay (presumably a match) is open.

**Resolution is locked to 1920×1080** in the top-level `Variables.txt` (backup
`Variables.txt.res-bak`). `layout.toml` assumes it.

**Screenshots** land in `Documents/Heroes of the Storm/Screenshots/` and can be read directly.
Ask for one rather than a description.

**Crosshairs in screenshots are the game's, not ours**: thin lines right across the screen,
one horizontal and one vertical, meeting where the mouse was (the cursor itself isn't
captured). It's Heroes' own mouse-tracking aid (user, 2026-10-06). Don't hunt for them in
our layouts.

---

## 6. Design decisions worth not relitigating

**Relocate Blizzard's hero cells; don't rebuild them.** No bindable "icon for this player's
hero" exists; relocated cells bring portraits, HP, click handling and death state, and
survive new heroes. Spazzo's per-hero textures are why his files run to 13,000 lines.

**Inherit bindings; never reconstruct them.** Put new frames *inside* the frame that owns the
binding — the CC sensor lives inside each cell's `HeroStatus`, so it always matches the
portrait above it; the resource bar and heal sensor do the same. (The heroic tooltip can't:
its talent icons only give tooltips inside Blizzard's own talent-row copy — see §3.)

**Use Blizzard's CC plate, not a rebuilt one.** A hand-built label rendered nothing; the
engine's element is self-managing.

**Branding is OBS's data on our plates.** OBS draws only what the game can't know (names,
logos, score, the tournament, bans) and never art (user, 2026-10-16); the interface draws every
plate it sits on. The interface can't see OBS, so there is no in-game fallback for missing names
or logos.

**Plates are Blizzard's in-game top-bar cell, not the observer's.** Its art, sizes and
stacking are rebuilt in `tools/gen.py` (`HeroCell`) and only scaled; the portrait crop is
worked out from the cell's shape. The user wants that look (their screenshots are in `design/`).

**No fight mode** (user, 2026-10-16: the spec has moved past it; it was once a hotkey that
hid a list). The agreed default view already is the old fight-mode cluster, and the
operator's toggles (`[toggles]`) do the hiding. Pooled team HP is dropped: layouts have no arithmetic, and
five segments would duplicate the hero row. If plates read too small, widen them.

**Art is sized for 1440p and scaled down at 1080p** (user, 2026-10-06), not the other way
round. Every generated texture is its frame's size on a 2560 x 1440 screen (`gen.py
ART_HEIGHT`; sizes needn't be powers of two), so it's 1:1 there and drawn at 75% at 1080p.
Layout numbers stay 1080p px, the resolution we test at; any 16:9 screen gets the same layout
(1200 units tall). Not yet looked at in 1440p: the inspect card's edge lines are worked out to
land on whole pixels at 1080p (`inspect_card.line`), so at 1440p they may come out 2-3 px.

---

## 7. What's next

**1.0 (user, 2026-10-21).** A test build went to volunteers 2026-10-20 (v0.1.0, b28ee86, the
kill feed back on); their feedback is 1.0.x for a while - `[meta] version` 1.0.0, 1.0.1 (the translations), now 1.0.2 (the art pass: bevelled
plates, the numbers panes - user, 2026-10-23: "Let's prepare for a new interface release
with this"), a patch
number per fix batch, each one a `pack.py --release` from a commit. Work is on `main` (its
history is python-toolchain's, which stays as it was). GitHub:
https://github.com/FourCourtJester/FCJ-Heroes-StormInterface (public; pushed in
batches, when the user says; `.github/FUNDING.yml` for the Sponsor button: GitHub Sponsors
and Ko-fi).

**To confirm (user, tonight of 2026-10-23): the interface drop-down is under Settings ->
Observer** ("I think") - README's install step 3 and docs/development.md say so; correct both
if not.

**The XP Contribution pane - built, seen in game and good (user, 2026-10-25) (user, 2026-10-25: "Let's look at that
experience breakdown panel, and see if we can re-arrange our info panes to accomodate").**
Still four panes on the same keys: Ctrl+3 is now HEALING · SIEGE DAMAGE · EXPERIENCE (by hero:
SELF, HEALING, SIEGE DMG, XP), and Ctrl+4 is XP CONTRIBUTION, the only pane by team, not by
hero - each team's band with its TOTAL, then a row per source: HEROES, MERCENARIES, MINIONS,
PASSIVE, STRUCTURES, in Blizzard's words from the popup (`UI/XPContribution/*`). The numbers
are Blizzard's popup's own: hidden labels on the top panel,
`PartyFramePanel/PartyFrameTopPanel/Team<1|2>XPInfoFrame/PropertyBindLabels/<Hero|Mercenary|Minion|Passive|Structure|Total>AmountLabel`
under `UIContainer/ConsoleUIContainer` (core partyframe.stormlayout, popup at :2869, labels at
:3158), which trigger `libUIUI_gt_UIPartyFrameXPContributionPercentage` (uilib.galaxy:15611)
writes every ~3 s to `PlayerGroupAll()`. Ours bind their text, as the plates already bind
`PartyFramePanel`'s pet death timers (gen.py `xp_pane`, `XP_SOURCES`; style
`FCJH_XpSource`). The stats panes widened 477 -> 549 units (~65 px) for Ctrl+3's four big
columns; the titles now ScaleToPreventTruncation. The HUD key (FCJH_Toggles) fades the XP
pane where it faded siege's. **Check:** the numbers fill in an observed replay at all (the
binding to a hidden, script-written label is unseen for observers); they read empty until a
team's first hero reaches 100 XP (Blizzard's script waits for it), so blank at 0:00 is
expected; blue and red the right way round (Team1 = blue); Russian's long rows ("Убийства
героев") fit; Ctrl+3's 4 columns and the wider box against what's beside it. If the numbers
never fill, the fallback is per-hero XP only (Ctrl+3 keeps it). If the user would rather keep
Ctrl+3 as it was, the XP pane can go on Ctrl+5 instead (one hotkey in layout.toml; the box
already fits).

**For 1.0.3 too: the inspect card on its team's side (a suggestion, user, 2026-10-23: "blue
where it is now, red for a mirror across the way").** A blue hero's card stays at
`[element.inspect]` (left column, above blue's row); a red hero's mirrors it on the right
edge, above red's row. To work out: what signal moves it - the card's edge colour is already
picked by team (blue, red, `neutral_colour`), so that same switch may be able to drive the
anchors - and where a neutral unit's card goes (left, as now, unless told otherwise). Check the
mirror against the replay box (top-right) and red's map alerts, which the replay box was
once narrowed to clear; the `--check`/validate overlap checks should catch a collision.

**Done for 1.0.3, seen in game and good (user, 2026-10-25): the pause box moved (user, 2026-10-24: "if we can move
the 'paused the game' notification, we should"; custom games are "99% of esports").** Blizzard's
`SystemAlertPanel` ("X paused the game. (N remaining)", a purple box) sat at the top centre,
over the logo plate and clock. Now 40 px under the clock (box top 200), centred on 958.5:
`layout.toml` `[element.system_alert]`, the frame in `FCJH_TopBar`. Look untouched. First under
the centre banners (284); seen in game 2026-10-25 (replays can be paused too) and "waaay too far
down", so moved up - it now overlaps a centre banner while both show. docs/blizzard-fixes.md
has it.

**Bug from a streamer's cast, found (user's vod screenshots, 2026-10-24): pop-ups outlive
Ctrl+E.** The streamer's words were "the icon for the event stays and replaces the icon that
would have been the hero icon". What happened: Ctrl+E (hide all UI - for everyone, us too,
whatever gamehotkeys.txt's `ReplayRestart` label says) went while the level-13 **talent
pop-ups** were up; they stayed over the hidden plates, **stretched to about a plate's width**
(the "replaces the hero icon"), then faded. A second Ctrl+E later was clean. The user confirmed
the **heal pop-ups** do the same. Normal pop-ups are their right 40-unit squares (screenshot,
same game), so the size is part of the bug, not `talent_popup_size`.
Cause: `FCJH_TalentPopups` and `FCJH_HealPopups` (FCJH_HeroRow) are **direct children of
`GameUI`**, outside the containers Ctrl+E hides, so a pop-up plays its `Pop` animation out
(Visibility true until `end`) anchored to plates that are hidden. Fix: hide both containers
whenever the plates are. The flip side: anything of ours at the `GameUI` root survives Ctrl+E,
so the user's idea - Ctrl+E (or our own **Ctrl+Shift+E**) hiding only *some* of our pieces -
is a matter of placing them. Taking over Ctrl+E itself needs a test that an interface can
rebind it; Ctrl+Shift+E needs validate's free-key check.

**Done for 1.1, seen in game and good (user, 2026-10-25: "Ctrl/shift+e is good"): the HUD keys are ours (user, 2026-10-25: "ctrl-shift-e our
'hide all but the top plate'", "ctrl-e still hides everything (including the top plate)",
"ensure that those icons dont bleed thru, or anything else really").** Blizzard's
`ToggleHUD`/`ToggleFullHUD` lose their keys (FCJH_Replay) and ours take them
(`[toggles] hud`/`hud_lower`, FCJH_Toggles): `FCJH_HudToggle` (Ctrl+E) fades and hides the
whole `ObserverHeroOverviewPanel`, top plate included; `FCJH_HudLowerToggle` (Ctrl+Shift+E)
and Ctrl+E both drive `FCJH_HudWatch`, a StateGroup OR (states All / Lower / Shown) that plays
one paused animation, `FCJH_HideLower`, forward or back. It hides the rows and the map panels
(Fade + Visibility) and, Fade only, everything the engine or a gate shows: XP tracks and
frames, core bars, talents overview, heroic tips, the inspect card, command card, talent tips,
both pop-up containers at the GameUI root, and the four panes. Left out, as with Blizzard's
keys: chat, the kill feed, the replay box and its tab, the pause box. Note that OBS plates still
draw over a hidden top plate. Blizzard had them the other way round (their Ctrl+E kept the
team names). Validate notes Ctrl+E is gamehotkeys' ReplayRestart, which the layout key has
always beaten. **Untested in game**, and three things to watch: that the watcher's states
re-evaluate on a ToggleControl's Visible; that the Shown state's reverse-play at load is a
no-op; and a zero-hero team's XP bar (RowPacker's Heroes0 sets Alpha 0, which the Fade's
reverse restores to 255 after a hide and show - rare).
**The game's end, the same bug (user, 2026-10-25: "after the game, a health notification
bleeds thru", Screenshot 21_14_55):** a heal pop-up, stretched to a plate's width, over red's
side of the "RED TEAM WINS!" splash. Blizzard hides its plates for the splash; the pop-ups at
the GameUI root don't follow. `FCJH_HudWatch` now has two states ahead of the keys' - Blizzard's
`GameOverSplash` (`$GameUI/UIContainer`) or `EndOfGameAwardsPanel` showing - that hide all
`FCJH_HideLower` hides. **Untested in game**; watch that nothing is hidden at load (the
splash has no `Visible` of its own in the extract, so the engine must hide it until the end),
and that a rewind from the end brings the HUD back.

**Rexxar's whole-plate death: done for 1.1, seen in game (vod, 2026-10-24; user, 2026-10-25: "looks fine now").** A dead
Rexxar greyed his slice and Misha's (Colorize white / alpha 180) while every other dead
portrait sank into Blizzard's dark shadow, so he read "faded", not dead. That shadow is the
game's code on the observer portrait (no layout state draws it); measured off the vod, the
same heroes dead were 0.27-0.36 of their live brightness with the hue kept. So a dead Rexxar's
slices now multiply by `555555` (gen.py `slice_overlay`, `rexxar_dead`; `Color`, as
`FCJH_ChargeDim`'s black), his state first so it beats Misha's own. A lone dead Misha keeps
her grey (user: "properly convey'd"). **His timer goes back to the plate's centre** while he's
dead (`FCJH_RexxarTimer`, its own StateGroup so the slices' art states don't replay), on his
slice's -16 otherwise; Misha's own stays on hers. **Check:** that `Color` darkens a
`ColorAdjustMode None` image in game (if the slices go black or don't change, that's why), and
the darkness beside a normal dead plate.

**Colour-blind mode, in game: done for 1.1, to see in game (vod, 2026-10-24: Blizzard's
on-fire effect went yellow, "the red team ... wasn't"; user, 2026-10-25: "top plate,
nameplates, borders (ie - inspect)").** Blizzard switches on `<When type="Option"
colorblind="True"/>`; its colour-blind Ally is `1487e9` and Hostile `fe8a0e`
(`ColorBlindColors`, `gameuidata.xml:1103`), now `[colour_blind] blue`/`red`. The rule
(gen.py `colour_blind()`): each team-coloured piece keeps its own saturation and value and
takes the colour-blind hue, so red goes a peachy orange and blue barely moves. Every piece is
a `FCJH_ColourBlind` StateGroup (gen.py `colour_blind_states()`), an Off state putting the
normal values back, as SetProperty persists:
- the top backplate and both core fills: `_CB` textures swapped in (`FCJH_TopBar`, hand-written).
  **A Texture SetProperty on a `UnitStatusShieldedHealthBar` is untested** - if the core
  fill doesn't turn, that's why;
- red's plate art (`FCJH_TeamBg`) and red's talent squares (pop-ups and the inspect card):
  Blizzard's art Colorized to the orange (`[colour_blind] plates`, `plate_light`/`plate_dark`
  - add "blue" there if blue's should move too);
- the inspect card's team edge: its AdjustmentColor.

The stat panes (Ctrl+2-4), built after: the TEAMS bands and the row stripes and their lines
take the colour-blind hue (gen.py `colour_blind_fill`, an AdjustmentColor state on each fill);
the totals swap to `FCJH_StatTotal_*CB` styles (FontStyles.StormStyle, hand-written, colours by
the same rule). The values can't be restyled by a state - the lead animations set their style
on every best-value event - so each has a twin label, `FCJH_ValueCB` in the `_CB` style, styled
by the same animations (gold when leading, either way), and the option picks which shows. Both
teams, as the top plate. Not done: the death timers (Blizzard's styles). Glows are Blizzard's
own. Test with Rexxar's and the Vikings' slices in it.

**Seen in game (user, 2026-10-25), and the fixes, to see again.** Orange: the top bar, the
core bars, the inspect card's edge, the stat panes' backgrounds. Still red: the Ctrl+1 grid,
the inspect's talent squares, red's plate health bars. Fixed:
- the Colorize (red's plate art, talent pop-ups, inspect squares) set three properties in one
  SetProperty; now one per action on `$this` (gen.py `colorize_cb`), as the dead slices'
  Colorize, which works. If the plate art was already orange, that's no harm;
- the Ctrl+1 grid's red half (`FCJH_GridRed*`, hand-written `FCJH_InfoPane`) gets the same;
- red's health bars (and the Vikings' and Rexxar's): Blizzard's style for them
  (`ObserverPanelOverviewHealth`) points its Colorblind values at ColorSpecs that don't
  exist, so in colour-blind mode they switch to the core bars' style
  (`ObserverPanelCoreHealth`, its Chaos the core bar's orange). **A ColorStyle SetProperty on a
  health bar is unproven** (the resource bar's is the precedent).
For comparison: Blizzard's default UI tints none of its top bar or panes in colour-blind mode
(only the inspect's health bar); Ahli tints all red to orange and blue to a green-blue.

**Seen again (user, 2026-10-25): health bars and inspect squares orange, the toggle on/off
mid-game clean, Alterac's banners too; the inspect's orange "muted" beside blue, Ctrl+1 still
red.** So, round 3:
- **Ahli's colours, not Blizzard's** (seen in game and good, with Ctrl+1's squares, user
  2026-10-25; user: "If the standard for the last decade was Ahli's
  values, then we should accept them"). His textures keep saturation and brightness and turn
  the hue ~30 deg: red to orange (15-30), blue to cyan (176-197). `[colour_blind]` is now his
  heroic border's `ff672b` / `23defc`, and blue joins `plates`: blue's plate art, squares,
  grid and health bars turn cyan too (Order's core style is cyan 66def0, hue 188). Every
  generated piece follows; the hand-written FontStyles `_CB` twins and the Ctrl+1 pane's
  values were recomputed by the same rule (hand-copied - redo them if `[colour_blind]` changes).
- **Ctrl+1's red was Blizzard's talent squares** (`CustomTalentTreeIconBorder1-7`,
  `obs_talents_highlight_<team>`), not our grid: each row's seven now Colorized.
- **The squares brighter**: their own pair, `square_light` / `square_dark` (0.6 / 0.9; Ahli's
  orange square is ff9666), for the pop-ups, the inspect and Ctrl+1.

**The studio half, done for 1.1 (checked in a browser, not yet in OBS):** OBS can't read the
game's options, so it's the operator's toggle, **Tournament → Colour-blind colours**
(`toggles.colourblind`). `tools/obs.py` `colour_blind_files()` writes `colourblind.json` from
the same `gen.colour_blind_cfg`, and `_cb` twins of every SVG with a team colour (frames'
team line, lattices, pips); `studio/src/components/colourBlind.js` is the one hook. The game
bar, the matchup band (standby, draft) and the scores glow switch; the matchup slab doesn't
yet (studio/README "Colour-blind colours").

**Quest progress: what the other UIs show (vod, 2026-10-24).** Valla's Creed of the Hunter
seemed to show no buff and no stack counter on its talent's tooltip - the user then found it
("wasn't looking in the right place") but kept the note: compare how Blizzard's default,
Ahli and Spazzo show quest stacks and buffs, and whether ours reads as clearly.

**Chat sits in the lower middle (both testers, 2026-10-24, had to drag it off the minimap
and banners).** Blizzard's `ChatDisplay` hangs off `ChatBarAnchorFrame` (core
`ui/gameui.stormlayout:1091`: 830 down, centre -350) and the draggable `ChatBarDragButton`.
The drag is saved per account as a **screen position** - `Accounts/<id>/Variables.txt`
`chatpositionx`/`chatpositiony` - which an interface can't write. The user won't override
players' preferences: a default move is fine only if a drag still wins and nothing of ours
carries into a game without us. Tests (bot game): read the x/y, load a game with ours, exit,
read again; drag it and read again; a build with the anchor moved somewhere obvious (does
the anchor or the saved position win?); and with the game closed, back up the file and
delete the two lines (a "never dragged" player). Whatever they show, the guide gets a
suggested place to drag it.

**The XP bar as the core bar's companion (a suggestion, relayed by the user, 2026-10-24).**
The team-long XP bar (`[team_xp]`, 8 px high, the row's ~546 px) is "too long". The idea: make
it a companion to the core's health bar (213 x 24 px, at the row's inner end) - the remaining
width, the same height - so shorter but taller, at the cost of a little height off the bottom
bars. A before-and-after pair of screenshots first, to get more opinions.

**Inspect on both sides:** one request so far (the 1.0.3 note above); screenshots from a dev
build before deciding.

**Alterac Pass: the keeps' shields on the core bars - built, seen in game and fine (user,
2026-10-24/25).** Each keep alive is one `WarchiefAlive` stack on its team's core (coregeneraldata
`WarchiefAlive`, armour 20 a stack, max 3; the map's script adds one per keep at the gates and
takes one off as each keep's town hall falls) - so the count is keeps **alive**, 3 -> 0, not
reversed. Blizzard draws it as three shield pips on the core's bar (alteracmechanics.stormlayout
`HealthBarShieldContainerTemplate`, `@UI/Storm_UI_HUD_WCAV_HealthBarShield(Inside)`, the map's
own `SourceHas{3,2,1,0}WarchiefsAlive` validators), but only on the player HUD's core bars and
the in-world core, never the observer's top-panel cores. Ours, in FCJH_TopBar.StormLayout
(hand-written): Blizzard's template copied as `FCJH_AVShieldTemplate`, three on each core frame
(`FCJH_AVShield1-3`), shield 3 at the inner end (toward the minimap) emptying first, the insides in the core's UnitStatusColor Primary / PrimaryLight as Blizzard's;
`FCJH_AVKeeps` (a UnitStatusValidatorAnimElement on the four validators) shows them and sets the
insides. Hidden until a count state fires, which only happens on Alterac - Ahli 0.75's way in an
every-map interface (its `CoreOverviewTemplate`, `undo="false"` on the show). **Check:** the
shields on Alterac only and no errors on other maps; they empty one by one as keeps fall, on the
right team; the colour against our bar (Primary may not be quite our `[team_core]`); before
the gates open the count may read 0 (three empty shields).
**Seen in game (user, 2026-10-25): centred, they covered the core's number** ("27290 / 27290",
which grows from the bar's inner end). Now a row from the bar's **outer end**, a little smaller
(20 px boxes), clear of the number: `[team_core] av_shield`, `av_shield_in`,
`av_shield_overlap`. **Seen (user, 2026-10-25): clear of the number, but tight inside the
border** ("move them outside the bar borders, or ... more margin"): now a row **past** the bar's
outer end, outside its chrome line, the one nearest the bar (3) emptying first (`av_shield_out`
replaces `av_shield_in`). **Seen in game and fine (user, 2026-10-25) - DONE.** **Banners don't move when the core bar shows** - by design
(user, 2026-10-09, docs/maps.md): every banner's bar sits `[map_alerts] above_core` over where
the core bar's top is, shown or not; the Alterac screenshot has the 10 px. **But Alterac's
cavalry is now the exception** (user, 2026-10-25: "much more low hanging artwork than the
others"): its hexagon and blades hung 20 px under its bracket on red (over the core bar's number),
its hammers 25 px on blue (21_06_31), so both spots are placed by the deeper, 25 px higher, the
bars level (`maps.AV_BELOW`). **Seen in game and kept, always higher (user, 2026-10-25): "its
higher up, but it doesnt go higher than the minimap top edge"** - that was the worry; a lift only
while the core bar shows (on Alterac, only once a keep falls) was offered and not needed.

**The official release filename (user, 2026-10-21): `FCJ v<version>.StormInterface`**
(pack.py's `RELEASE_NAME`, from 1.0.1; 1.0.0 shipped as `FCJH.StormInterface`), in Ahli's
style (`AhliObs 0.75`; spaces load fine, Spazzo's is `SpazzoObsv40`). `--release --deploy`
installs it under that name, beside the dev build's `FCJH.StormInterface`, which keeps its
fixed name so the everyday loop overwrites one file. **Settled (user, 2026-10-23):** releases
keep this naming (FCJ vX).

**Every word of ours in every language (1.0.1, 2026-10-21; user: "lets flesh out the
translations").** Our own on-screen words live in `tools/words.py` (`WORDS`, keyed
`FCJH/<key>`; code keeps the English and asks `words.ref(english)` for the key), which gen.py
writes into each language's GameStrings: the inspect card's heads, team line and clone note,
CLONE, the stats panes' titles, column heads and team bands, the replay tab, Towers' town
alert, Alterac's camp alerts. Blizzard's own words wherever the game has them (the key beside
each); the Towers, Alterac and clone-note sentences are put together by hand from Blizzard's
names, **for a native speaker to check** (marked HAND). Labels shrink to fit
(ScaleToPreventTruncation), so long words fit; unseen in game outside English. A new word:
add it to `WORDS`, use `words.ref`.

**The road to release (user, 2026-10-16): "We're done maps. We're almost done heroes."** Warhead's
nuke counters closed the maps (e966a07). Left, in order: the last few heroes, then a final
visual polish, then screenshots of everything for posting.
Plan for 2026-10-17 (user): human replays to catch the blue-side cases never seen (Punisher,
Terrors, curse - blue never summoned in the test replays); while those come, the TO DO list
and the hero-specific items. Once maps and heroes are done it's all polish - visual work.
Once the user's happy with that: an OBS overlay to pair with the interface. Then done.

Finished work is out of this file: the map system and the map pass, map by map, in
[docs/maps.md](docs/maps.md); every other done or dropped item in
[docs/history.md](docs/history.md) (its item numbers are the old §7's). What we fixed for
Blizzard and what we added is in [docs/blizzard-fixes.md](docs/blizzard-fixes.md); the
generator itself in [docs/generator.md](docs/generator.md); the OBS plan in [docs/obs.md](docs/obs.md).

**Publishing, one channel per intent (user, 2026-10-23: "As long as we have it all
seperated out into their intents"):** Pages serves the OBS studio; Releases serve the
`.StormInterface` files; a markdown API folder for other developers comes later. docs/development.md's
"Where each is published" table. **1.0.2 shipped 2026-10-23:** three-veins merged to `main` (PR #1, merge commit ea6f493),
tag `v1.0.2`, the release built by CI (1,269,328 bytes, as the local `--release`; GitHub
names the asset `FCJ.v1.0.2.StormInterface`, dots for spaces, as it did 1.0.1's). **Pages
was still "Deploy from a branch"** - it served the README through Jekyll; the user switched it to
"GitHub Actions" and re-ran the Pages workflow (18:03 UTC): the site now serves the studio.
**The broadcast pass merged 2026-10-23** (PR #2, merge commit 1673335): Pages redeployed in
about 20 s, and the OBS collection is live at the site root. Browser-checked only; the user
tests it in OBS tonight.

**The three-vein reorganisation (2026-10-22), on `main` since 1.0.2 (2026-10-23); the
studio's list below is still open.** The repo now holds three veins: the interface (`interface/`, was `src/`), the
broadcast graphics (`studio/`, a Single Studio app) and the generator that writes both
(`tools/`), joined at `layout.toml`. The user's call (2026-10-22): one repo, three veins,
"give people the different avenues of accessing the parts they want" - a release for the
`.StormInterface`, Pages for the board, the folder for anyone who wants the files.

*Done and checked:* the rename and its sweep (`gen.py`, `pack.py`, `validate.py`,
`.gitattributes`, `release.yml`, the docs), and the interface loop end to end - `gen --check`
clean, validator 0 errors, 19 tests, `pack.py` built and deployed. `tools/obs.py` writes
`studio/src/generated/` and `gen.py --check` fails if it is stale.

*Built and run (2026-10-22, later the same day):* Node 24.22.1 went on, the studio installs
and builds clean, and both halves were driven in a browser - the board writes, the graphic
draws, and the pips, bands and tabs land within 0.04 px of `topbar.json`. The source is
`studio/src/sources/Game.jsx` (`#/source/game`), named for the scene rather than the top bar.
`npm run dev` could not be checked here (see below). Since 2026-10-23 the user tests in OBS.

**To resume, before merging:**
1. ~~Install Node, build it~~ - done. `npm run build` is clean; `npm run preview` serves it.
2. **`npm run dev` is unverified**: in the agent's embedded browser it fails with "Failed to
   fetch a worker script" (the SharedWorker that holds all state), so sources render nothing.
   The production build on `npm run preview` is clean in the same browser, so it looks like a
   dev-mode plus embedded-Chromium problem rather than the app - but it wants checking in real
   Chrome before anyone trusts the dev loop.
3. Test outputs: driven with names, a series score and the tabs' words; logos and bans still
   want the image library filling (no hero portraits anywhere yet).
4. ~~See it in OBS~~ - the user tests in OBS at 1080p (2026-10-23).
5. ~~Switch Pages to "GitHub Actions"~~ - done 2026-10-23, after the merge.
6. ~~Then merge~~ - merged 2026-10-23 (PR #1).

*Known gaps:* nothing fills the studio's image library with hero portraits (90-odd) for the
bans; the ban tiles' size and shape were never settled; the font is fetched from Google Fonts
at load.

**Open, in the user's order:**
1. **The final pass** - item 14 below. The forms and blue's banners are done, the odd cases
   ignored (user, 2026-10-19: "nothing right now is broken that I'm aware of"); the blue/red
   lines are final as they are (user, 2026-10-19). Left: a live game with observers (the kill feed is back on, 2026-10-20),
   a non-16:9 window.
   **The user's list of what's left (2026-10-19; the slicing tomorrow):** our own angled fountain / map-mechanic
   container borders (BUILT 2026-10-19, to check: `slot_frame` / `slot_mask` at 0.54, a mask
   drawn per team; the fountain and the carry box both; EDGE_INSET +2 for ~2.5 px to the edge all
   the way down, CARRY_LEAN = the slot's, so its sides run straight on. 23_16_14: the masking was
   uneven (Blizzard's square HealingWell icon reached the rim on one side only), so now our own
   `fountain_icon` fills the slot (Blizzard's blue, its pale cross upright, not italic); the carry
   box's backdrop and icon were under the portrait (511/512), now 525/526/527). 23_25_09: still
   no backdrop, and in Blizzard's behaviour icon template the icon wandered ~40 px off its box
   (red's off the screen's edge), so the carry box is ours too, built as the fountain: our mask,
   backdrop and frame, the map's own icon (`CARRY_ICONS`, the behaviour's InfoIcon per map), and
   Blizzard's behaviour icon only as the sensor and the count (`FCJH_CarrySensor`). The plus 2 px
   in at each end ("a little stretched"). The row's outer slanted ends left ~1-1.5 px more
   black by the outer plates' fountains than a seam does (outline `inside` 1 vs the seam's 1.5;
   user, 23_25_09): `[row_frame] end_inside = 1.5` now takes the line 1.5 px over the plates
   along the two ends only (`inside = 1.5` throughout moved the outset and with it every XP,
   core and inspect constant, so rejected). The rest was pixel snapping (23_42_43, measured: the teams equal,
   both teams' outer two plates ~1 px more): the plates are 135.9 px apart, so each fountain rounds to
   another whole pixel; `fountain_lines` lays each slanted line beside a fountain `[row_frame] fountain_gap`
   (1.5) px from that fountain as drawn (`drawn`). The carry box down a rim (`CARRY_RIMS`) so it shares the
   fountain's border (it was ~2 px of black above it). Then both 1 px down (flush with the portrait's
   bottom) and 1 px in (red's `EDGE_INSET` 5; blue's lean does it, but plate 2 snaps back), 23_58_11.
   Still: blue's black reads denser than red's (summed darkness ~1.45 vs ~1.08 px; blue's line 2-3 px
   wide, red's 3) - edge to edge ~0.15 px more on blue (00_03_02). Left as is: "all square" (user,
   2026-10-20; blue's `fountain_gap` ~1.3 would even it if it's ever raised). Open: the
   multi-unit nameplate slicing (item 15: the Vikings, Rexxar and Misha);
   a pass on the number-heavy panes. The chrome is done as far as the user knows.
   - **A centering pass on every minimap** (user, 2026-10-18: "100% convinced some are still
     off center compared to our generated UI"): each map's minimap against the rows' gap and
     the generated chrome, measured off a screenshot per map (docs/maps.md has each map's place).
     The method (user, 2026-10-19): "midpoint" is our UI's, the rows' inner chrome edges
     (958.5 px on 14_36_51, the rows then 1 px off: red_left 1167 against blue_right 752's
     mirror 1168; now 1168, so ~959). Each map centred between our plates on its art's
     outline and its mechanic's UI markers, by its `across` (tools/maps.py).
   - **The centering pass, built (2026-10-19, not seen yet):** every map measured by its two
     core swirls' outer outline (one per team, placed symmetrically; the map's ends on most),
     pixel rows through each swirl's middle, against the midpoint 959 (read 959 on the new
     build's 15_19_31: blue 704 / red 1214 at y 965). Flood fills, mirror and half-turn fits
     misled (terrain, point symmetry, background leaks); the camera box's border reads dark,
     not to be taken for the outline. Shots 14_51_53 .. 15_21_14. Each map's `across` set:
     | map | swirls' outline | centre | `across` |
     |---|---|---|---|
     | Alterac Pass | 782 / 1152 | 967 | -8 |
     | Battlefield of Eternity | 775 / 1144 | 959.5 | 0 |
     | Blackheart's Bay | 774 / 1144 | 959 | 0 |
     | Braxis Holdout | ~770 / 1138 | 954 | 5 |
     | Cursed Hollow | 765 / 1130 | 947.5 | 11 |
     | Dragon Shire | 776 / 1142 | 959 | 0 |
     | Garden of Terror | 765 / 1152 | 958.5 | 0 |
     | Hanamura Temple | 777 / 1142 | 959.5 | 0 |
     | Haunted Mines (top level) | 789 / 1087 | 938 | 21 |
     | Infernal Shrines | 772 / 1148 | 960 | -1 |
     | Sky Temple | 771 / 1159 | 965 | -6 |
     | Tomb of the Spider Queen (at 18) | 797 / 1115 | 956 | 21 |
     | Towers of Doom | 769 / 1153 | 961 | -2 |
     | Volskaya Foundry | 777 / 1143 | 960 | -1 |
     | Warhead Junction | 778 / 1130 | 954 | 5 |
     Haunted Mines by its top level (user): its mines below drew at ~961, so now ~982.
     Alterac's cavalry hand-off is now worked from its moved minimap (gen.py); Tomb's
     Webweaver stack's dead space from its drawn middle 958 (WEAVER_MINIMAP_PX). The user's
     check: the whole roster again; then the blue/red lines (below).
   - **The confirm pass (2026-10-19, built, not seen yet)** - docs/maps.md, end: Cursed Hollow
     placed by its id (its `across` never applied) and its tribute counts mirrored, clear of
     the map; Sky Temple 7 px up to the floor; Tomb's Webweavers on the plates' slant; the
     carry box back on the fountain's slant. Volskaya's gap: rim or dark band? (user's call).
   - **Confirm pass 2 (2026-10-19, 16_05_56 .. 16_10_04, built, not seen yet)** - docs/maps.md, end:
     Cursed Hollow's ravens mirrored and its lines flipped the way round every other map's,
     meeting at ~959 (tribute_extra); Garden's lines to ~959, red's plants and count on blue's
     mirror (seeds_extra); Bay's coin numbers 13 up into the coins (doubloons_extra); Tomb's red
     gem, count and number on blue's mirror (GEM_RED). Tomb's Webweavers approved.
   - **Confirm pass 3 (2026-10-19, 21_57_37 .. 22_00_17, seen on pass 4)** - docs/maps.md,
     end. Seen good: Garden, Tomb's Webweavers (angles; the banner gone), the pane border (no
     bright patch). Built: Cursed Hollow's blue line 13 units further in; Bay's coin numbers
     centred on their coins; Tomb's numbers centred on their vials and 6 up to Bay's floor; red's
     fountain and carry box 2 units nearer the plate's edge (EDGE_INSET 4.5 -> 2.5, blue's gap).
     Blizzard's slot art leans ~0.6, not 0.54: the gap still grows ~2 px down the two boxes -
     the art pass's to recut (our own slot frame at 0.54).
   - **Confirm pass 4 (2026-10-19, 22_10_41 .. 22_12_10, seen 22_19_37; the carry box not yet)** - docs/maps.md, end.
     Seen good: Tomb's numbers. Cursed Hollow's blue line never moved: clipped by its own frame
     at ~949.5 (every move since pass 2 hidden); now Unclipped, ending at red's start. Tomb's
     lines met at ~955 under a map centred ~958.75: both 4 units right, the gems, counts and
     numbers held (GEM_LINES). The carry box (Bay, Tomb) "bleeds into the chrome" on both
     teams (~1 px off the edge): CARRY_LEAN 0.66 -> 0.56, 2 units in (~3 px, the fountain's top).
     Cursed Hollow: DONE (user, 2026-10-19, on 25e67ef).
     Seen good (22_19_37): Tomb's line fudge. The fountain icons differ left to right: the
     masks (blue the heroic's Ult_Bg, red Blizzard's buff mask; a mask can't be mirrored), not
     this pass. The carry box's gap at CARRY_LEAN 0.56: ACCEPTED for now (user, 2026-10-19).
     Slot angles and the icon: ACCEPTED as they are (user, 2026-10-19); our own cut
     (a slot frame at 0.54, a mask mirrored per team) goes to the art pass.
   - **The blue/red lines under the mechanics' counts** (user, 2026-10-19): out to their
     farthest, the plates' inner ends (~752 / ~1168), "so we have most flexibility for the
     containers". Each map's panel sets its own (Blizzard's TeamHighlight-style backgrounds,
     e.g. Mines' Team1Background / Team2Background); on the shots ~813-1107 (Warhead) to
     ~780-1140 (Mines, Dragon Shire). FINAL as they are (user, 2026-10-19): not extended.
   - **Left of the map questions (user, 2026-10-19):** Volskaya's gap (the user checks it), then
     one last map-centric QA round, which finalises the minimap centering.
   - **THE GAP from the backplate (user, 2026-10-19):** a neutral banner's backplate bottom 10 px
     over the map's top tip, not its hexagon; exceptions (single-banner morphs, art against the
     grain) by eye. Volskaya: the toast 17 px down (its backplate 27 px off on 22_28_11); the
     capture point stays by its hexagon (22_29_08, "positioned correctly"). Seen good on 87fa94f.
     The other maps get checked against it in the QA round.
   - **The last map QA round (2026-10-19, 22_33_04 .. 22_49_28, on 0cea729):** nothing obvious
     (user); every minimap centred (Cursed Hollow 777.5 / 1140.5). By the backplate rule: Braxis
     fine (~12); Volskaya's capture point and Hanamura's payload exceptions (single morphing
     banners); Dragon Shire has no neutral banner; Alterac 13 px down (23 -> 10), Battlefield 11
     down (21 -> 10; maps.py `above`). Seen on 87fa94f: Alterac, Battlefield and Volskaya's toast
     good - DONE (user, 2026-10-19). The map QA round is closed.
   - **The pane border's halves (2026-10-19): DONE, seen good on pass 3 (21_57_37 ..).** each side was a whole nine-slice
     squeezed into half the height, so both halves ended in the art's end cap at the middle,
     stacked "doubly as bright" (user). Now each half is a whole side clipped at the middle
     (inspect_card.py tab_border, `UpperHalf` / `LowerHalf`). Closed (user, 2026-10-23): no
     bright patch seen on the inspect card either.
   - **The user's answers (2026-10-19, evening):**
     - the top bar shrink (1284a7a): DONE, on trust ("as long as everything fits");
     - on fire: DONE - red seen, blue and colourblind run the same code; revisit on feedback;
     - Tracer's Pulse Bomb meter and 20-segment ammo bar: seen, fine;
     - the carried box's coin: fine as it is; revisit only if people complain;
     - our own on-fire marker: dropped (Blizzard's flames are cutscene models, not art we can
       redraw);
     - the chrome backplate look on the plates: yes, for the art pass;
     - the plates' intro slide and fade: still to do (it doesn't exist yet);
     - word-only map banners: gone for good (item 16, closed). Tomb's "Red/Blue Webweavers
       summoned" hidden too (maps.py, `SoulEaterFrame` alpha 0; seen gone on pass 3);
     - OBS: 3 pips a side, one hexagon in full and empty; the tournament name in a secondary
       tab, division beside it; the ban tiles get their own pass (docs/obs-topbar-handoff.md).
2. **The art pass** - items 7 and 12 below, and the visual pass: the chrome backplate look to
   the plates, our own fountain/carry slot (built 2026-10-19, item 1), XP/core bars (a mid-height bevel, like the player view's core bar; the default
   UI's core bars: `design/ref_default_core_hp.png`) and ~~the info panes (zebra rows, Heroes
   palette; the numbers panes need a better visual - docs/history.md item 1)~~ - **the numbers
   panes DONE (user, 2026-10-23, 78644dc: "I think I can work with this")**. The canvas draws
   the build as it is (`design/canvas_gen.py`); the art pass designs over those boards.
   **Parked (user, 2026-10-23: "Keep them on the list, but we wont do anything about them
   now"):** the chrome backplate look on the bottom hero plates, and the plates' intro slide
   and fade (Ahli's). Both are interface items, not OBS.
   **First pass built (2026-10-23), for the user to see in game:**
   - **Bevels:** the XP and core fills are lit from above as Blizzard's core bar - a light lip,
     a ramp down with a soft step at mid-height, a dark foot (gen.py `bevel_texture`,
     layout.toml `[bar_bevel]`). The fills stretch only across, so the shade holds at any
     value; the XP bar now says `Tiled false` too, as the core bar did.
   - **The numbers panes' rows:** a stripe behind every row in its team's tint, two shades
     alternating, a thin team-colour line under each - Blizzard's score screen
     (`Screenshot2026-10-22 21_27_16`) - from layout.toml `[info_pane.rows]` (gen.py
     `row_stripes`), opaque enough to read over a bright map. Red's team band moved from crimson
     toward that screen's maroon; the numbers lightened to its tints (FontStyles `FCJH_StatValue_*`
     9cbcf4 / eda4b8: full team colour read dark on dark, `Screenshot2026-10-23 12_24_59`).
     Those tints first showed as dark blue and red (`Screenshot2026-10-23 12_30_35`): the row's
     team colour multiplies into a label that doesn't say `IgnoreParentColor`, as Blizzard's own
     score label does. Ours does now. Seen in game: the bevels on both bars, the stripes. The
     talents pane keeps Blizzard's observer grid. ~~Not yet: the score screen's shaded column
     groups (Blizzard's `BGSeparatorImage1-3`, which our rows hide), the
     leaders' glow in place of our lit box.~~ Not needed: gold leaders (below) closed it.
   - **The stats panes narrowed (user, 2026-10-23: "The column widths are a bit too
     generous").** Columns are sized to the widest number, not shares of the box: a count is
     60 units (XX.YY, about 48 px in the value font), a big number 84 (XXX,XXX in the totals
     font), at least 24 apart (gen.py `STAT_WIDTHS`, `STAT_GAP`). The three stats panes are 496
     units (446 px, from 546), the KDA pane's need; the talents pane keeps the full box.
     Headings may run left into the gap. K/D/A are Blizzard's Kills/Deaths/Assists now (long
     in German and French: "KILLBETEILIGUNGEN"). Siege became **Minion Damage** (Blizzard's
     `MinionDamage`, siege less structures; Siege counted the structures twice beside the
     structures column). If the user meant merc camps, Blizzard's `CreepDamage` is that score.
     Checked against Tab (`Screenshot2026-10-23 12_48_34`): XP matches all ten; Minion +
     Structures is Tab's Siege for five, short for the rest by what Siege also counts - laning
     mercs and summons (StormDamage's score array: Abathur's locusts, Misha). Red's structures
     read 0 all game; Tab's Siege leaves red at most 3,691 outside minions, so it is likely
     real (to re-check on a replay where red pushes). The leader box was the IgnoreParentColor
     bug too (grey-brown, `Screenshot2026-10-23 12_47_40`); it says it now, a little stronger.
     Second replay against Tab (`Screenshot2026-10-23 12_52_23`, `12_52_44`, `12_52_52`):
     every player's K/D/A, hero damage, self healing, healing, minions + structures (less
     mercs and summons, as above), XP and every leader box match; red's structures are not 0
     there. Wrong, fixed: the KILLS band read the other team's kills - it summed
     TeamTakedowns, which Blizzard credits to the dead player's team; it sums the kills now.
     Not ours: the healing bands read 1-2 under the rows' sum (Healing is a fixed-point score,
     the rows round each value). Dead live: **SHIELDING** - Blizzard reports
     ProtectionGivenToAllies only at game over (gamelib.galaxy EventBasedAwardsDataReport);
     shields count in Healing during the game (Medivh's 6,569).
     **Then dropped (user, 2026-10-23: "Drop shielding, and the minion/structure split, and
     i'll re-evaluate"):** Ctrl+3 is SELF HEALING · HEALING, two columns; Ctrl+4 is SIEGE
     DAMAGE · EXPERIENCE - Blizzard's whole SiegeDamage, Tab's number. The split can't be made
     right: MinionDamage misses mercs, summons and some heroes' own siege (Johanna, Hanzo,
     Gul'dan tag SiegeDamage only), a layout can't subtract, and an interface can't change
     game data. The pane key is `siege` now (layout.toml [info_pane] hotkeys). The two-column panes keep the
     shared width, so their gaps are wide - re-evaluated with the tightening below: fine.
     **Portraits as tall as the stripe (user, 2026-10-23: "Tab has taller portraits seperated
     out by their bottom accent lines"):** the numbers panes' portraits fill each stripe from
     its top to the accent line (50 units, 89 wide at Blizzard's 100:56), uncropped, with
     Tab's right-edge fade (Storm_UI_InGame_Leader_ScoreInset_PortraitFade). Was the talent
     pane's 90 x 33 crop at row offset 10. Geometry: stat_geometry()["portrait"].
     **Tightened (user, 2026-10-23: "Remove BLUE/RED from the headers / Anchor the portraits
     to the left edge / Remove some of the whitespace the portraits have", and "a row of
     emptiness from the end of blue list to the start of red header"):** no team names in
     the bands (FCJH_StatTeam_* styles gone); the portrait sits on the left border, the first
     column 4 units after it (STAT_PORTRAIT_GAP); STAT_TEAM_GAP 0, so red's band follows
     blue's last stripe. Stats panes 496 -> 455 units. Last change of this pass; the user
     re-evaluates.
     **Leaders in gold (user, 2026-10-23: "Instead of a highlighted area for column leaders,
     how about we just use a yellow/gold color"):** the FCJH_Lead box is gone; the leader's
     number swaps to FCJH_StatValue_Lead (Blizzard's ColorGold, fed600) on the best-value
     events, by the Style controller Blizzard's own label uses.
     **The numbers panes are DONE (user, 2026-10-23, 78644dc: "I think I can work with this.
     Let's mark these off the list then").**
   - **Plate bevels - DONE (user, 2026-10-23, d8b21f2: "Great. Mark that off then!"); the
     mask work too (3a7a84c: "Looks good. We'll mark that as mask work"). Every alternate
     resource (Brew, Fury, D.Va, Deathwing, Rage; segmented or not) is FCJH_Resource's
     ColorStyle over the one PLATE_FILL, so it carries the bevel and mask. Revert point was
     27500be (user, 2026-10-23: "Make a
     note that if it looks bad, we'll revert to this state, but yeah, if blizzard has some
     available bevels specifically for health and mana, lets do it").** Blizzard's top-bar
     fills carry next to no bevel (HealthFill: a 1-texel white lip top and bottom over a faint
     e1-f5 ramp; ManaFill: a 4-row db-f8 ramp). The one bevelled bar fill in the client is
     `UI/HealthBar` (UI_HealthBar_Bar_01, 16 x 11 greyscale: ff at the top ramping to 8b, a
     c6 foot; no Heroes layout uses it). No mana-specific bevel exists in what's extracted
     (Probius's EnergyBar art isn't in references/CASCView), so the one fill serves both:
     gen.py `PLATE_FILL` on the health bar, the resource bar, the Vikings and Misha, stretched
     (`Tiled` false on index 0 - tiled, its 11 rows would cut off in the 8-tall bar and repeat
     in the 14-tall one), with Blizzard's own fill variant (HealthFill{_Sm}{_Narrow}{_Right},
     ManaFill{_Narrow}{_Right}) as its AlphaMaskTexture for the slanted ends. Expect the bars
     a shade darker (the ramp averages ~0.75 against the old ~0.92).
     **Round 2 (user, 13_35_43: "mask damage"):** Blizzard's fills as masks are 8 (mana 4)
     texels tall and their rows wrap into each other - the top row's tip cut upright, a tail
     off the bottom row past the slant. The masks are now ours (gen.py `plate_bar_masks`):
     the plates' lean at 1440p size, as the Vikings', one per bar, team and narrow state.
     **Round 3 (user, 13_44_48: "quite jagged... Only Vikings doenst have the jaggedness"):**
     the Vikings' margin too - the health and resource bars' frames run PLATE_MARGIN (4) past
     the slant at both ends, the masks padded clear to match (gen.py `padded_slant_mask`).
     The fill's 0 and 100% move out with it, as the Vikings'.
     **Then toned 10% (user: "too much of a stretch from the top to bottom"):** PLATE_FILL is
     now ours, Blizzard's rows (`BLIZZARD_HEALTHBAR_ROWS`) with each row's distance below
     white x `PLATE_BEVEL` 0.9 - the lit top kept, the darkest row 8b -> 97.
3. **Screenshots of everything for posting**, then **the OBS overlay** to pair with the
   interface (docs/obs.md). Per-map shots: docs/maps.md. Show-off shots, with how to stage
   them, are marked **A show-off shot** in docs/blizzard-fixes.md's "Made" list (first:
   Abathur's clone on the inspect card).
- Also open: rewinding a replay upsets pop-ups and latches (final polish - the product
  is for live games); rows with fewer than five heroes (a 3v3 or 1v1 replay). Both IGNORED
  (user, 2026-10-19).
- **To do (user, 2026-10-16):** a pass on the panes and the inspect card to make them
  Heroes-like (Blizzard's menu panel: blur, translucency, chrome border), and ~~a colour, font
  and art pass on the numbers panes~~ (DONE 2026-10-23, 78644dc) (docs/polish-research.md,
  "Decisions from the question round").
- **Ideas to come back to (user, 2026-10-21):**
  - Dragon Shire: a graphic for whoever is controlling the Dragon Knight. **First pass built
    (2026-10-21), for the user's evaluation:** Volskaya's pilot seat over the knight's bar,
    beside the dragon's head (as our Volskaya seats beside the robot), in the knight's team colour,
    the driver's face in it (`maps.knight_pilot`). Who's driving: each
    cell's `FCJH_Vehicle` sensor (gen.py `vehicle_sensor`; Blizzard's UsingVehicle behaviour,
    Ahli's recipe), one more per Viking. Seen in game: placement and sensor work; the face,
    cropped from the plate's wide art, did not ("Crop didnt go well"). **Second pass:**
    Blizzard's own seat portrait, as its Volskaya seats show (libvlsk's SetPilotPortrait via
    uilib's KillLogGetPortraitPathforUnit): the hero's square `ui_targetportrait_hero_*`, each
    Viking their own, in Blizzard's mask. A script picks it there; ours is a per-hero table
    (gen.py `SEAT_PORTRAITS`, from Jamie Phan's hero data and Ahli's list) - **a new hero needs
    adding to it.** Seen in game on red (Genji, Ana): "looks good!". Not yet seen: a blue
    driver, a Viking driving.
  - A driver's plate read "STASIS" (UsingVehicle's parent is StormStasisRemoved). **DONE
    (user, 2026-10-23: "KNIGHT / PROTECTOR / TERROR is confirmed"):** the vehicle's word in its place, by map - KNIGHT, PROTECTOR (its
    gunner too: the sensor can't tell the seats apart), TERROR (any other vehicle, so Garden
    classic too, its map id unseen) - Blizzard's names cut short (user: "Knight" and
    "Protector" is probably our best bet with "Terror"). gen.py `VEHICLE_WORDS`; Blizzard's
    stasis icon stays in the portrait. In every language, from Blizzard's own names there
    (user: "We *should* translate them"); gen.py now writes our GameStrings (`game_strings`).
  - D.Va: a "PILOT" status on her plate while she's out of the mech - any status effect
    overrides it, and it goes when she's back in the mech.
- **Vikings' and Misha's timers and skulls (2026-10-21, user: "Vikings look brilliant"):**
  each on its portrait slice's middle, 1 unit low (digits sit high in a label's box), the
  skull on the number, the number held 1.5 s then faded in. Misha's number is back, on her
  slice (dropped 2026-09-30), hidden while Rexxar is dead.
- **Parked:** blue's curse mirror (unseen; item 14).
- ~~**Later:** extract the toolchain into its own repo~~ **Dropped (user, 2026-10-23):** the
  three veins keep the toolchain here (`tools/`); [docs/extraction-plan.md](docs/extraction-plan.md)
  is kept for the record.
- **Study Ahli's other panels** (user watched a broadcast on his UI, 2026-10-03) - not to
  replace ours, but for implementation tricks and visuals:
  - his custom inspect (`_BottomLeft`) and his custom panes - talents, XP and the rest
    (`_LeaderPanelBottom`, his restyle of Blizzard's Tab stats panel, `HeroLeaderPanel`);
  - **death recap**: a streamer opened one for a hero who'd just died. It's Blizzard's, a tab
    of the same Tab panel (`HeroLeaderPanel/HeroLeaderPanelContainer/TabControl/
    DeathRecapContainerFrame/DeathRecapPanel`, base UI `deathrecap.stormlayout`; the button
    that opens it is wired in `gameui.stormlayout` ~734). Spazzo ships a fix for its
    alignment (`references/Spazzo/.../RecapAlignmentFix.StormLayout`); Ahli hides its
    buttons inside his leader panel. Worth a feature of ours: a death recap on demand.
  - **quests** (checked 2026-10-03) - **DONE (user, 2026-10-23):** quest progress shows on
    our talents pane and the inspect card. Ahli's talent pane has two kinds. (a) A column for a
    hero's BASELINE quests (the trait kind, not a talent pick): two slots, `BaseQuestIcon0/1`
    (`UnitStatusBaselineQuestIcon`) in a `ParentCenteredFrame`, so one quest sits centred and
    two sit side by side - straight from Blizzard's own leader panel (`heroleaderpanel`
    ~920). (b) TALENT quests (a level-1 quest or any other) show on the talent's own icon:
    a progress bar, a stack count ("12/40") and a done image, switched by the icon's
    `QuestProgress` property (`QuestInProgress` / `ProgressUntracked` / finished) - so two
    quest talents are just two icons each with their own bar. Blizzard's talent-row icons
    carry the same bar and label (`talentsoverviewpanel` ~828), so our talents pane and the
    inspect card can show quest progress the same way.

**Settled as impossible:** jumping to one Lost Viking from the plate (Blizzard's per-Viking
targets in its in-game bar are ping buttons with selection off); D.Va's mech and Rexxar's Misha
from their plates (docs/blizzard-fixes.md).

**The numbered items still open** (their numbers kept; the rest are in docs/history.md):

7. **The art pass**, after the functionality: ~~Ahli's Tracer ammo bar (20 segments) and round
   Pulse Bomb meter~~ seen, fine (user, 2026-10-19); his hero plates' intro animation (a smooth
   slide and fade) - not built yet. ~~And the death
   timers' end~~ DONE (user, 2026-10-18): they flash as the player view's, on Blizzard's own
   HeroRespawnAnim keys (`gen.style_flash`).
   And the plates' carried box (gen.py `carry_box`, user 2026-10-12): Blackheart's doubloons /
   the Spider Queen's gems in the fountain's slot one step up the slant, the count over the
   icon, hidden at 0, on CARRY_MAPS only. Working and its borders now continue the fountain's
   (`CARRY_SLIDE = 4`, confirmed on Zul'jin, 2026-10-12). The coin a touch big for its window:
   left as it is (user, 2026-10-19: "good enough for now", revisit if people complain).
   **The polish phase - the user's first pass (2026-10-16; "there might be more"; not all at
   once).** Research done (2026-10-16): docs/polish-research.md - feasibility, approach, tests
   and questions for each. **Test build 9720882 deployed (2026-10-16), not seen yet**, with
   defaults picked for the questions (docs/polish-research.md, "Tonight's test build", which
   has the checklist):
   - the skull, the respawn flash and glow;
   - the event squares (which cell gets the respawn events);
   - thumbnails of the party cell's three portraits (for the split plates);
   - the chrome row frame (`[row_frame]`; the rows now sit 2 px higher, scale 1.5507), with
     seams between plates and under the XP bar, and the core bar's own line (`[team_core]`);
   - the on-fire squares (a second row), ammo segments, the talents pane's quest column.

   **The next test build (2026-10-16), not seen yet:** the leader-panel quest overlay
   (`FCJH_QuestPanel`, f5ab192) is out: its icons never drew and it leaked faded portraits.
   Our own quest icons are back, Blizzard's 68 whole so the quest ring shows; the tooltips
   are still blank until Tab (unsolved). The pane border's sides are in halves, the lower
   flipped, so the bottom half mirrors the top (seen 6804bbd: much cleaner). Tracer's plate
   dial is the gold frame's height (35 x 39), its tick ring only, with no dark disc: opaque it
   covered the badge and bars, and half see-through (6804bbd) it was lost in the icon. Its
   fill never drew (6f5a93d at 29%: nothing, user): the observer bar restyled circular. Now
   a fresh dial from her HUD's own template (`FCJH_PulseBombDial`, as Ahli's), with a whole
   ring of our own for full charge, where the template hides its fill. That fill drew all
   along, lost against her orange icon: seen on the dark disc at 56% in the diagnostics
   build 57474cd. Now the disc is back dimmed (gen `PULSE_DIAL_DISC_ALPHA` 140, the user's
   pick of three), the icon showing through; the diagnostics are out. Seen bf31cf2: the ring
   builds but doesn't pop, and it stands over the badge (user, 2026-10-17). Now the disc at
   200, the charge count in the middle (as the inspect card's), the dial 0.8 of the gold
   frame's height (`PULSE_DIAL_SCALE`). Seen e153492: fits the frame, the count (56, as the
   card's) left of the dial, and a 100% animation the user liked (the template's: at full it
   hides the disc and plays its ready ping). Now as the inspect card's dial (user): the disc
   opaque, the count centred on it. Seen 5bc2824 (29%): the count reads; the dark hexagon
   (the disc) to go (user). Now the ring and count over the icon, the disc see-through. Seen
   d0438cc: the template's ready ping plays at full despite our hiding it (its own animation
   fades and grows it), and the user wants it kept; the tick ring barely shows over the art.
   Now no tick ring: the count, hidden at 0 (a Text StateGroup), and a 20% black dim in the
   icon's shape over the heroic while charging (25% after dfb3ffd), off at full on the template's events
   (`FCJH_ChargeDim`, gen `PULSE_DIAL_DIM_ALPHA`). **DONE (user, 2026-10-19, on 5819c62):
   dim until ready, gone at 100; the count right, gone at 0.** Seen fine in 5c38a32: the heroic badges 6 in from the cell's end (gen
   `HEROIC_CLEAR`). The chrome's shadows are to be revisited later (user).
   **The test build of 2026-10-18 (5819c62), seen 2026-10-19:**
   - the quest icons, try 4 (docs/blizzard-fixes.md, "Quest tooltips blank until Tab"):
     Blizzard's Tab panel type of our own again (`FCJH_QuestPanel`, FCJH_InfoPane), parked off
     the screen; each row's `BaseQuestIcon0` anchored onto our row's quest cell
     (`FCJH_QuestCell0-9`). **FAILED:** no quests showed in the talent pane, and a faint white
     line ran the pane's height just right of the portraits (~x 131 px), discolouring the
     red/blue row lines where it crossed. Taken out (the code is in 5819c62);
   - ~~the top chrome bright~~ DONE (user: "Bright top bar chrome is good"): `[top_backplate]
     rim` is the bottom's flat silver, and the row frame and core bars take that one line;
   - the plates' bars fill the plate's bottom (1df8a76): down to 59, health 11 tall, mana 10,
     energy 6. Seen: the bars' ends' angle "definitely off now. Not by much" - below.
   **The test build of 2026-10-19 (b07a109), seen 2026-10-19:** the hexagon's rim one width all
   round - DONE (user: "hexagon looks crisp"). The bars' ends masked to the lean - still off
   (user), so reverted, with the heroic drop that went with them (below). Quest try 4 out - the
   white line stayed: ten short pieces at x ~132, one per row, so a row's own piece.
   **The test build after it, not seen yet:**
   - **the plates' bars at Blizzard's sizes again** (user: "If we can't match the angles, we
     should revert bar sizes so the angles match"): health 8 tall, mana 7, energy 4, the
     no-resource bar 14, to 53 as before 1df8a76; no masks; the heroic back on the cell's
     bottom (its foot on the resource bar's again). The cell's bottom ~10 px is empty again;
   - **Blizzard's slot 0 on the quest cell** (`TalentTreeIcon0`, every row, FCJH_InfoPane): it
     hangs 30 left of talent 1 (talentsoverviewpanel.stormlayout:138), so it sat under the
     portrait until the talents moved a cell right - likely the white line. Placed on the quest
     cell as a test: if it shows the default quest, that's our quest icon; if it's an empty box,
     hide it;
   - the on-fire squares big and blinking (still unread; no on-fire replay promised).
   Seen afea2b1 (user): the bars stay at Blizzard's sizes for now ("We'll leave our hero bars
   like this for now"); the white line still there. It sits at the pane's 22 + the grid's
   first slice's end 124 = 131.4 px: the slice was cut at talent 1's cell edge and took a
   sliver of its border. Now ended 2 short (122), the bridge from there. Seen: still there.
   **The test build 2696582, seen 2026-10-19:** the white line gone in every row with the grid's
   bridges hidden (portraits hidden in rows 0/5 and moved in 1/6 changed nothing), so it was
   the bridges: a 4-texel slice (118-122) stretched 15 times, its first texel blurred into the
   brighter one beside it. Now one texel column (120). Slot 0, given a real icon this time,
   still shows nothing on the quest cell: Blizzard's custom row template has no slot 0. Out.
   **Not seen yet:** the bridges back on one texel column - the line from portrait to talent 1
   back, no white line.
   - **the quest icons back** (the rows' own `FCJH_BaseQuestIcon`, as before try 4): the right
     quest per hero, its tooltip and count still Blizzard's blank/stuck ones.
   **dc32c98, seen 2026-10-19:** the quest icons' talent border back on heroes with a quest
   (`FCJH_QuestBorder`) - DONE (user: Nova's border climbs to the top; Murky's climbs; Uther's
   level 1 too; the white line stays gone). Blue's icons on `HeroTalentTooltip` as a test:
   Murky's showed the last talent hovered, Nova's an empty box - the box doesn't matter, the
   icon must be one that writes (docs/blizzard-fixes.md). Reverted.
   **Quest tooltips, tries 5-8 failed** (2026-10-19; docs/blizzard-fixes.md). Scrapped: rebuilt
   one piece at a time in a separate test interface, `interface/tests/FCJH_QTest.StormInterface` (deleted
   2026-10-19, user: it never ships; in git before that)
   (`python tools/pack.py interface/tests/FCJH_QTest.StormInterface --name FCJH_QTest.StormInterface --wait`),
   one change per build; `FCJH_QuestTest` is out of FCJH. **Step 1 fills** (7be15cc): an
   untouched copy of Blizzard's leader panel, Control+Shift+Q. **Step 2 fills** (5d1ae3f):
   opened Ahli's way (on from load, faded and slid in), no Show event. **Step 3 blank**
   (f2696bb): the quest icons lifted out of the panel to the top of the screen don't draw.
   **Step 3b blank** (9f2e09c): the same lift, Unclipped; the "!" column is left empty, so
   the icons move but don't draw. **Step 4 fills** (58476c4): icons kept in their row, 150 px
   left, draw and fill (tooltips a little hard to keep up). **Step 5** (048e0f7): also 30
   up, cut at the row's edge - the row clips. **Step 6** (ad64c31): the row's batched
   TalentsContainerFrame un-batched - still cut. **Step 7** (9c04a2f): that frame grown 60
   above and below the row - still cut. **Step 8 draws whole** (270d4a4): the whole chain
   under the row Unclipped - each link clips, every one must be freed. **Step 9** (c104af4):
   the far lift again, to a line above the panel - drawn, no tooltips (outside the player's
   box, §3). **Step 10** (6d04cc2): `spread` from the row to the icon - still no tooltips.
   Lifting icons is a dead end for tooltips (as `talent_row_lifts` found). **Step 11**
   (35d160b): back to step 2, the rows moved 200 up as a block - cut at the panel's top, but
   a moved row inside it keeps its quest tooltips. **Step 12** (787f7f4): rows Unclipped
   - drawn above the panel, but no tooltips there; the mouse answers only inside the panel's
   box. **Step 13** (8ceaed0): the box (HeroLeaderPanelContainer) 400 taller instead -
   **every row's quest tooltip works** where the box covers it. **Step 14** (53ff05f): the
   panel's background at Alpha 0 - tooltips kept. **Step 15** (a8a9657): the hexagons,
   border and close button at Alpha 0 too - tooltips kept. **Step 16** (0081cda): the
   team scores at Alpha 0 - tooltips kept. **Step 17** (25369e1): each row's background,
   portrait and names at Alpha 0 - tooltips kept. **Step 18** (9373f9e): the talents
   and column numbers too - tooltips kept; portraits and faint column bands stayed. **Step
   19** (8579d61): those at Alpha 0 too - "yes, both. nothing else visible". **Into FCJH - DONE**
   (96c8996, user, 2026-10-19: "you did it mate"): the cut-down copy on the ctrl-1 talents pane (`FCJH_QuestPanel`), its rows on
   ours by handle (`FCJH_TalentRow0-9`), its icons on our quest cells (`FCJH_QuestCell0-9`);
   our own quest icons gone; the quest tooltips fill without Tab. Spazzo's nameplate quests are his own per-hero behaviour icons, no tooltips (a
   fallback only; see blizzard-fixes).
   Blizzard's kill feed was hidden for testing 2026-10-16..20 (FCJH_Hidden, a KillLogPanel
   controller in `FCJH_KeepHidden`); back on for the volunteer test build (user, 2026-10-20).
   It was hidden because its portraits read as ours under the panes - one for the testers.

   Diagnostics: the respawn, hearthstone and portrait ones are read and gone (2026-10-16);
   `onfire_diagnostics` (gone since: read 2026-10-19, below) - seven squares over each plate's
   portrait, one per event of Blizzard's on-fire frame, lit (blinking, 20 s) when it fires -
   orange Embers, red Inferno, grey End, blue Ally, dark red Enemy, light blue Left, light red
   Right. Read which ones light, then it goes.
   **Read 2026-10-19 (dc32c98, user, a replay where red had heroes on fire):** orange, red, grey
   and light red all lit; blue and light blue never (blue never went on fire). So Embers,
   Inferno, End and Right reach an observer; Left should too (untested). Ally/Enemy go to the
   hero's own team/its enemies only (uilib.galaxy libUIUI_gf_UIOnFireSetOnFireType), not
   expected. Blizzard sends each level change (Embers/Inferno/End) together with its side
   (Left/Right) to the same cell, yet the user saw orange on one hero and pink on the next:
   the row of seven (10 + 26 x 7 = 188 units) is wider than a plate, so its end lands on the
   neighbour's portrait - a "dark red" on Hogger's far left was likely a neighbour's square.
   Next: a blue hero on fire for Left (user trying another replay), then the squares out and a
   real on-fire marker from Embers/Inferno/End.
   **6420bd3, seen 2026-10-19:** squares out, Blizzard's own flames (`onfire_flames` in gen.py)
   on each plate - they play for an observer ("kinda looks goofy but it did emit": red flames
   over Sgt. Hammer's plate, spilling past its top edge). Next: our own, from there.
   **Blizzard's leader-panel glow** (`@UI/Storm_UI_InGame_Leader_OnFire_Glow`, the Tab panel's
   on-fire art), faded in by Embers/Inferno and out by End, with a white square lit by the same
   events: the square lit every time, the glow never read - Blizzard's template whole (002c699),
   one image at 529 (e6fa651), additive at 700 (8e7b3e9), four strips: bare, + team fill,
   + additive, + unclipped and pulse (11e618a). **Test 1 (1c4f33b, seen 2026-10-19):** square
   and strips out, the glow always on, no fire logic, Blizzard's alias on each plate's left
   half, the file itself on the right. User: "i think both are there, hard to tell"; against
   an older shot of the same plates, a soft white mound rises from the bottom of each half.
   So it always drew: it's just faint (near-white, mostly 10-60% opaque, over a portrait), and
   fainter still at Embers 200 or under a team fill. Both routes load it.
   **Test 2 (0c9803c, seen 2026-10-19; user: "ill just let you figure this one out"):**
   Blizzard's flames back, always on (Inferno), one variant per plate, left to right on both
   teams. All drew, team colours right where they have them: (1) the top-bar flames shrunk to
   the portrait - thin wisps over the face; (2) the same at Blizzard's size, NOT Unclipped,
   in a portrait-sized parent - clipped: a team-coloured rim round the portrait, flames inside
   (so a parent does cut a cutscene off); (3) the kill feed's flames - a white hexagon, no
   use; (4) the overhead bar's - big, orange on both teams, spilling well above; (5) 6420bd3's
   control - spills. **Chosen: (2)**, on every plate, back on the fire events (Embers/Inferno
   bookmarks, End plays Blizzard's dying-out then hides at 5 s).
   **Fitting it (c4beaec - 68486eb, all seen 2026-10-19).** Inferno on Hogger: "the red outline
   is *mostly* good" - the top ~2 px low, the right edge off the plate's slant. Odd/even plates
   on the cutscene's Left / Right side filters (ae9319d): they're two models, Left
   (Storm_UI_Hud_PartyFrame_OnFire) for Blizzard's left team, Right (its _Enemy mirror) for the
   right; the wrong one slants against the plate ("the criss cross pattern is at odds"), so each
   team takes its own. Squashed onto the face only (5c63562): "height looks good"; widened x 1.45
   (73b5814): "flames look the same" - the rim is one 3D model, no separate sides to place, so
   both were dropped. Back to Blizzard's box, shrunk ~1 px (8c907de) and raised 2 px (54d5d72):
   a 2 px glow line under the energy bar stayed put at 1048-1049 - the glow running on down,
   cut off at the clip, not the rim's edge; clipping at 52.5 units (68486eb, y ~1046) took it
   out. User: "great. i think we can call that square". Final: Blizzard's box x 0.986, top
   -8.6 units, left -28.8 (blue) / -32.5 (red), clip at 52.5, on the fire events, every plate.
   **Seen on real fires (e945f98, Braxis, red, 2026-10-19):** Embers and Inferno "both look
   good and fade out just fine". **DONE (user, 2026-10-19):** blue and colourblind run the same
   code, so taken as done; revisit on feedback. No on-fire marker of our own (the flames are
   cutscene models).
   The intro waits for the user's OBS plan. The items as the user gave them:
   - **The chrome's slant against Blizzard's art** (user, 2026-10-17): the row frame's slants
     don't gel with the art's: the portraits' edges, the heroic badges, the fountain icons and
     the resource bars' ends. The portraits can't change, so the chrome follows them. Ours
     lean `HeroCell.OVERLAP / H` (30 / 61 = 0.492 across per down, `row_frame_shape`,
     `row_frame_seams`). A first read of the seam between plates 2 and 3 on 00_09_39 gives
     about 0.48; not yet measured: each piece of art's own slant (a 3x zoom of the blue row,
     x 40-440, y 950-1080, shows them). Measure each, pick the one the eye follows (likely
     the portrait edge), then re-cut the frame. Also: **the chrome shadows out** (user: they
     don't land in good places).
     Measured 2026-10-18: Blizzard's art agrees on ~0.54 (the native frame's dividers 0.55 on
     design/ref_ingame_topbar_ults.png, the bar fills' ends 0.55-0.57, the badges 0.54-0.58);
     only ours was off. Now one lean, `HeroCell.LEAN` 0.54, turning on the health bar's middle
     (`LEAN_PIVOT` 42, so the bars' ends keep their place under the seams), the pitch kept:
     the row frame, seams, XP and core bars, the portraits' mask, the fountain's and carried
     box's edge, the pop-ups, the Vikings' timers, the backplate's wings and the Webweavers.
     The fit scale fell 1.5507 -> 1.5459 (the steeper top corners reach further out; cells
     95 -> 94 tall). The plates' click masks keep the old cut (hit areas only). The shadows:
     the chrome's dark band (the backplate rim ramp's `5b637f` stop) part way down each seam;
     the row frame and core chrome are now one flat silver, and since 2026-10-18 the top
     backplate's too: one `[top_backplate] rim`, which the row frame takes (the old ramp is
     in its comment). Seen 2026-10-18 (cffee7f): the portraits gone (blue) / half cut (red) -
     a shadowed variable in portrait_mask, fixed f35dae5. Also seen on a light map: Blizzard's
     health backing's nine-slice end poked a dark strip ~4 px out of the row frame on the end
     plates (always there, hidden on dark maps) - pulled 3 units in (f35dae5). The Mortar
     Punisher's head breaking out of its hexagon is Blizzard's one image (the hexagon is in
     it; ShrineHud is an empty frame) - placement unchanged. **DONE (user, 2026-10-19: "No more
     lingering questions about punishers and hexagons").** The lean: seen right on the chrome;
     the bars' ends drifted with the taller bars (masked 2026-10-19, above).
   - **A ready ring for every heroic** (user, 2026-10-17): Tracer's ready ping, the expanding
     gold ring at full charge, made the user want the same whenever any heroic comes off
     cooldown. Notes in docs/polish-research.md ("A ready ring for every heroic").
   - **The plates closer to the player's in-game top bar.** Played as a player, Blizzard's
     plates feel far more polished than the observer's; find out what we can copy (the
     player HUD's layouts in JamiePhan - their animations and StateGroups);
   - **Split plates for heroes with more than one unit** (Rexxar and Misha, the Lost
     Vikings). **Portraits and bars DONE (user, 2026-10-21, e101687: "i think we're good").**
     Blizzard's player-bar slices over the portrait, each greyed while its unit is dead
     (`slice_overlay`); the Vikings' three bars slanted and masked (`viking_bars`,
     `viking_masks`, `viking_span`), Blizzard's separator on each seam and the far end (a mask's
     edge draws hard in game however it's feathered); the slice diagnostics are gone. Misha's
     bar stays hidden, Rexxar's full height. **The Vikings' per-slice rings DONE (user,
     2026-10-21, ed32947: "TLV looks great"):** the plate's death ring, bursts and respawn glow
     on each Viking's portrait slice only, down to the bar backing (`slice_rings`,
     `slice_ring`), off their own party-cell timers and `HeroAlmostRespawnedHero{n}`.
     **Misha's DONE too (user, 2026-10-23: "Misha's and TLV's death rings are good now")**
     (`FCJH_SliceRingMisha`, hidden while Rexxar is dead). See item 15;
   - ~~**Death timers flash white under 5 s**~~ DONE (user, 2026-10-18; above);
   - ~~**Ahli's death animation**~~ DONE (item 12; seen again 2026-10-19: the skull, red ring,
     flashing count and gold rim at 5 all good);
   - **A frame round each team's row of plates**: silver-grey metallic like the top bar's
     edges, about 3 px, slanted where the plates slant, to cover the gaps and overflows
     between heroes;
   - **An intro animation for the elements, to pair with OBS** (more from the user later;
     Ahli's plates slide and fade in, above).
12. ~~**Ahli's death animation on the nameplate**~~ **DONE (user, 2026-10-18: "Seems
    brilliant", on 8d6261f).** Blizzard's player-view skull animation (`gen.death_skull`),
    its plate-shaped art our own (`gen.plate_ring`: Blizzard's rang only the portrait, at
    their slant): the red border and bursts zoom onto the plate, the border held 1 s past
    Blizzard's; then the countdown, and the gold respawn glow pulsing at the end.
14. **Final pass: every map, every hero** (user, 2026-10-05). The last QA round, with replays
    that cover every map and every hero; the checks that need a particular hero or map collect
    here until then (no replay with them yet):
    - **Heroes seen in game - the tracker (user, 2026-10-09). Update it after every replay; the
      user's own list is the source (a reconstruction from chat logs missed 15).** 91
      heroes (Cho and Gall counted apart; Xal'atath the newest); ALL 91 seen (2026-10-14):
      - **In the user's replays across 4 maps (user's list, 2026-10-09; 39):** Illidan, Stitches, Probius, Brightwing, Tychus, Fenix, Anub'arak, Tyrael, Zagara, Rehgar, Uther, Murky, Zarya, Gazlowe, Nova, Zeratul, Sgt. Hammer, Lt. Morales, Hogger, Leoric, Deathwing, Alexstrasza, Ragnaros, Greymane, Valeera, Samuro, D.Va, Chen, Medivh, Auriel, Chromie, Sonya, Johanna, Rexxar, The Lost Vikings, Tracer, Varian, Xal'atath, Abathur.
        (The user's list also had "Varion" beside Varian - read as a typo; ask if not.)
      - **Named in earlier sessions, not in those replays (7):** Blaze, Diablo, Jaina, Li Li, Lúcio, Maiev, Xul.
      - **The form checks below can be done in those replays:** Medivh, Deathwing,
        Alexstrasza, Ragnaros, Greymane, Valeera, Samuro, D.Va, the Vikings, Tychus are all in them.
      - **Dragon Shire's roster, played (user, 2026-10-12: the roster below was the one used; 10):**
        Cho, Gall, Dehaka, Qhira, The Butcher, Kel'Thuzad, Nazeebo, Genji, Ana, Junkrat.
      - **Blackheart's Bay's roster, played (user, 2026-10-12; 10):** Muradin, Thrall,
        Kael'thas, Valla, Whitemane, Arthas, Zul'jin, Gul'dan, Alarak, Stukov.
      - **Garden of Terror's roster, played (user, 2026-10-12; 10):** Garrosh, Malthael, Li-Ming,
        Hanzo, Anduin, E.T.C., Kerrigan, Sylvanas, Mephisto, Malfurion.
      - **Alterac Pass's roster, played (user, 2026-10-12; 10):** blue Artanis, Kharazim,
        Falstad, Mei, Tyrande; red Imperius, Mal'Ganis, Raynor, Orphea, Deckard.
      - **Hanamura Temple's roster, played (user, 2026-10-14; 10):** blue Azmodan, Cassia, Lunara,
        Tassadar, Yrel (the last five unseen); red Medivh, Deathwing, Abathur, Samuro, D.Va.
      - **Next rosters:** for the form checks below (no hero is unseen now).
    - **forms** (docs/history.md item 3): Medivh's Raven SEEN (user, 2026-10-16, Hanamura: the tall card, his
      player, and his own buttons - Raven Form's cancel on the mount slot). D.Va SEEN (user, 2026-10-16): the pilot gets the tall
      card with her buttons; the self-destructing mech the tall card at 1 hp, invulnerable (the
      game's own unit, fine); her plate's click selects only the pilot, so does nothing while
      she's in the mech (Blizzard's, docs/blizzard-fixes.md). Samuro's images and Abathur's
      Evolved Monstrosity get the SHORT card (team, health, stats) - right: they aren't heroes,
      and the short card tells an image from Samuro. Deathwing SEEN (user, 2026-10-16: good)
      in Dragonflight and in World Breaker form (one of his two ground forms: from
      Dragonflight he lands as Destroyer or, with the World Breaker button, as World Breaker -
      a buff, `DeathwingWorldbreakerForm`, on the same `HeroDeathwing` unit, so the card's
      match holds and only the buttons are left: World Breaker's read Lava Burst and Earth
      Shatter, Destroyer's Incinerate and Onslaught).
      Alexstrasza's Dragonqueen, Ragnaros in Molten Core, Greymane's Worgen and Valeera
      stealthed SEEN (user, 2026-10-16: all good). Each form gets the TALL card with its player's portrait, talents and name, and
      its own buttons. If one gets the short card or no player, look at which unit the plate
      shows meanwhile (`inspect_card.FORMS`). The user is 99% sure the card already picks the
      right player in every form (2026-10-16), so only the buttons are left to check. Ahli's
      and Spazzo's command cards don't swap either (Abathur in Symbiote keeps his own;
      docs/blizzard-fixes.md), so matching theirs is fine. `HeroValeeraStealthed` and
      `HeroDeathwingWorldBreaker` aren't units in the game data: guesses, harmless (World Breaker
      is a buff, above - the guess can go in a tidy);
    - **empty slots**: Abathur's missing E shows Blizzard's empty frame over the buttons' own
      dark hexagon (added 2026-10-16, 5f78047, after the bare frame read as a hole; confirmed 2026-10-16);
      on any hero, no faint outline peeking round Q W E R (else resize `command_panel`'s
      empties); Deathwing in flight with no Z or D reads fine;
    - **Abathur's clone** (Ultimate Evolution): the short card for Samuro's images (seen
      2026-10-16 - right). The clone is a unit of the copied ally's type, and the card only
      changes when someone clicks it (Abathur stays selected as he burrows). Before d309816 it
      showed the ally's player and talents (BlackoutCR's on a Falstad clone of Budokai's). Now
      it shows Abathur's player and a CLONE note where the talents go, keyed off
      `UltimateEvolutionBuff` (inspect_card.clone_sensor) - seen right 2026-10-16; since
      4fa66d8 the portrait is the copied ally's (the clone wears their skin) - seen right 2026-10-16, with no
      talent tooltips on the clone and the real heroes' cards unaffected.
      A paused replay showed stale stats on the card (0% / 100%, 20% / 110% running). A
      show-off shot: how to stage it is in docs/blizzard-fixes.md (the inspect card's entry);
    - **Deathwing's heroic after level 10 - ask other players (user, 2026-10-06).** His plate's
      heroic is Cataclysm, his kit heroic, counted by our own reader (`gen.py
      KIT_HEROIC_COOLDOWNS`). At 10 he picks an active talent, pressed on 1, which Blizzard's
      observer slot then follows. Ask casters and players which they want on the plate after
      10: Cataclysm, the level-10 ability, or both (the user may enlist help, 2026-10-16);
    - **the D.Va and Viking guesses** in `inspect_card.ALSO` SEEN (user, 2026-10-16): D.Va's pilot
      and mech, and each Viking (Olaf, Baleog, Erik), get the tall card - the player, the
      talents, each Viking's own health;
    - ~~**rows with fewer than five heroes** (a 3v3 or 1v1 replay)~~: ignored (user, 2026-10-19);
    - **every map**: the map objectives, the minimap per map (docs/maps.md; the jitter is solved -
      map id, 2026-10-09; every map id read in game by 2026-10-15);
    - **Cursed Hollow, blue cursed** (docs/maps.md): the banner on blue's side, left of the map,
      ending at the map's edge, its text and timer inside the art - not yet seen (user,
      2026-10-06: red's looks great);
    - ~~**Infernal Shrines, blue's Punisher**~~ DONE (user, 2026-10-18: "works as intended", and
      2026-10-19: "Blue punishers are seen", on
      23ecda4 - its hexagons at their own width since e973927): on blue's side, mirrored - the icon
      at the outer end, the backing flipped, the fill draining from the right, the % at the outer
      end (`maps.punisher_side`);
    - **a live custom game with observers**: the game binds Ctrl+1-8 to "Observe Player 9-16"
      (gamehotkeys.txt) - check our panes' Ctrl+1-4 still win with observer slots filled. Also
      O / Ctrl+O lock the camera to the commentator's / a referee's (their tooltips still
      marked "???"; a lobby slot can be made Referee) - worth a try for casters;
    - **a non-16:9 window** (docs/history.md item 4), last: the user stays at 1080p until then. The game's
      resolution is in `Documents/Heroes of the Storm/Variables.txt` (`width`, `height`,
      `windowwidth`, `windowheight`, `displaymode`, `windowstate`; 1920 x 1080, displaymode 0 at
      2026-10-06; `windowstate=1` is maximised - on 2026-10-09 a maximised window on a bigger
      monitor ran the game at 2558 x 1401 unnoticed: check screenshots' size) -
      Claude puts it back to 1080p afterwards, with the game closed.
15. **The Lost Vikings' nameplate in player view - look at it later** (user, 2026-10-09). In a
    player's view TLV's nameplate seems to be a three-slice, one per Viking, each with its own
    click handler. Worth studying for ours: how Blizzard splits one plate into three clickable
    parts (find it in JamiePhan's layouts), and whether our plates could use it.
16. **Static banners hidden - CLOSED (user, 2026-10-19): they stay gone.** "Word-only map
    banners that don't actually have any function other than to say that the mechanic has
    spawned, they all need to disappear." Tomb's "Red/Blue Webweavers summoned"
    (`SoulEaterFrame`) hidden with them (the summoner's hexagons say it). Was: revisit after the
    final pass (user, 2026-10-15). Word-only
    banners that sit up until the objective is taken, saying what the objective markers on the
    minimap already say, are hidden (54eaed2, e48326a). Once the final pass's screenshots are in,
    look again at whether any should come back, or come back as something that counts:
    - Infernal Shrines' "Shrine active" (`ShrineActiveFrame`, alpha 0 by PARTS; Blizzard's
      script re-sets that mode every 0.25 s, the likely flicker);
    - Cursed Hollow's "Collect the Tribute" (`tribute_count`: the art and words faded while
      the count is hidden);
    - Garden of Terror's "Gather the seed!" (`GatherTheSeedsFrame` parked above the screen;
      `seed_banner(False)` builds it again);
    - Sky Temple's "Capture the Temples" (`temple_banner`: the art and words faded while the
      count is hidden - the same frame as the countdown).
    Left as they were, brief: Volskaya's 2 s point toast (it counts), Towers' 5 s tunnels and
    towers-upgrading notices (in the alert stack: hiding them by alpha would leave a gap).
    Approved as kept (user, 2026-10-19: "they actually serve purposes"; Volskaya's and
    Hanamura's are one shared alert).

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
