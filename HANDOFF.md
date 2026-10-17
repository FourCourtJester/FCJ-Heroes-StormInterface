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
(talents, KDA/damage, healing, siege) at middle-left on hotkeys; talent pop-ups on the
cells, and a green-plus pop-up on any hero below 25% health (drawn under the talent
pop-up). **There is no fight mode** (user, 2026-10-16: the spec has moved past it) - the
default view is the old fight-mode cluster, and the operator's toggles hide what needs hiding.
The top bar and minimap always stay.

**OBS draws data only, never art** (user, 2026-10-16): team names, logos, series score, the
tournament's name, division and logo, and the game's bans, on plates the interface draws.
Nothing on the bottom UI. Its places are `kind = "obs"` rects in `layout.toml` (§6, docs/obs.md).

**Status, 2026-10-16: Phase 2 (building the default view) is all but done** - every map passed, every hero seen; the final pass, the art pass and OBS are left (§7). Phases 0
(toolchain) and 1 (probing the unknowns) are done. Built, and confirmed in game unless noted:

- **Hero row** — Blizzard's *in-game* top-bar cells, slanted and interlocking, scaled to fit
  the screen's 20 px padding (`[hero_row] scale = "fit"`, 1.5561): portrait, health,
  resource bar in Blizzard's per-hero colours, CC text and icon, death timers (per-Viking
  ones in each third), Viking bars in thirds, Rexxar's bar full height (Misha's hidden),
  the **fountain** (the inspect card's: Blizzard's buff slot leaning with the plate, dark
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

Not yet: the OBS graphics package and the visual pass that takes the chrome look of
the top bar to the plates, bars and panes. §7 has the open list.

---

## 2. The loop

```
python tools/pack.py --wait
```

One command: **generate → stage → validate → pack → deploy.**

1. **generate** — `tools/gen.py` rewrites the committed generated layouts from `layout.toml`
2. **stage** — `src/FCJH.StormInterface/` is copied to `build/<profile>/`. A dev build adds
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
each box in its legend colour was removed 2026-10-05). `--release` is exactly what `src/` holds: it refuses
while `src/`, `layout.toml` or `tools/` have uncommitted changes, so every release is
reproducible from its commit, and writes `dist/v<version>/FCJH.StormInterface`
(`--deploy` to also install it). GitHub releases ship that file.

### Tools

| Command | What |
|---|---|
| `python tools/pack.py --wait` | The loop above |
| `python tools/gen.py [--check]` | Regenerate; `--check` fails if a generated file is stale or hand-edited |
| `python tools/validate.py [--show <frame path>]` | Validate `src/`; `--show` prints the merged tree under any frame |
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
src/FCJH.StormInterface/                     the archive's file tree, one to one
  Base.StormData/UI/Layout/
    DescIndex.StormLayout                    GENERATED — every layout, constants first
    FCJH_Constants.StormLayout               GENERATED — layout.toml in layout units
    FCJH_HeroRow.StormLayout                 GENERATED — cells, heroic panels, pop-ups, row packer
    FCJH_StatPanes.StormLayout               GENERATED — the three stat info panes
    FCJH_Inspect.StormLayout                 GENERATED — the inspect card
    FCJH_Maps.StormLayout                    GENERATED — each map's minimap place, panel, team alerts
    FCJH_*.StormLayout                       hand-written, one per concern (top bar, hidden
                                             HUD, talents pane, kill feed, minimap, replay)
  _Assets/Textures/FCJH_*.dds                GENERATED — slanted bars, masks, the top backplate
src/dev/                                     dev-only layouts (none now; packed into dev builds only)
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

**Open, in the user's order:**
1. **The final pass** - item 14 below: the last forms, blue's unseen banners, the odd cases.
2. **The art pass** - items 7 and 12 below, and the visual pass: the chrome backplate look to
   the plates, XP/core bars (a mid-height bevel, like the player view's core bar; the default
   UI's core bars: `design/ref_default_core_hp.png`) and the info panes (zebra rows, Heroes
   palette; the numbers panes need a better visual - docs/history.md item 1). The canvas draws
   the build as it is (`design/canvas_gen.py`); the art pass designs over those boards.
3. **Screenshots of everything for posting**, then **the OBS overlay** to pair with the
   interface (docs/obs.md). Per-map shots: docs/maps.md. Show-off shots, with how to stage
   them, are marked **A show-off shot** in docs/blizzard-fixes.md's "Made" list (first:
   Abathur's clone on the inspect card).
- Also open: rewinding a replay upsets pop-ups and latches (final polish - the product
  is for live games); rows with fewer than five heroes (a 3v3 or 1v1 replay).
- **To do (user, 2026-10-16):** a pass on the panes and the inspect card to make them
  Heroes-like (Blizzard's menu panel: blur, translucency, chrome border), and a colour, font
  and art pass on the numbers panes (docs/polish-research.md, "Decisions from the question round").
- **Parked:** blue's curse mirror (unseen; item 14).
- **Later:** extract the toolchain into its own repo for open-sourcing (user, 2026-10-09) -
  [docs/generator.md](docs/generator.md) says what it is, [docs/extraction-plan.md](docs/extraction-plan.md)
  how to split it out.
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
  - **quests** (checked 2026-10-03): Ahli's talent pane has two kinds. (a) A column for a
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

7. **The art pass**, after the functionality: Ahli's Tracer ammo bar (20 segments) and round Pulse
   Bomb meter (the meter on the plate built 2026-10-16, not seen yet); his hero plates' intro animation (a smooth slide and fade). And the death
   timers' end (user, 2026-10-09): in a player's view, Blizzard's own death timer flashes as
   it comes to an end - find how (the player HUD's layout: its animation or StateGroup on the
   respawn countdown) and give our plates' death timers the same for the observer.
   And the plates' carried box (gen.py `carry_box`, user 2026-10-12): Blackheart's doubloons /
   the Spider Queen's gems in the fountain's slot one step up the slant, the count over the
   icon, hidden at 0, on CARRY_MAPS only. Working and its borders now continue the fountain's
   (`CARRY_SLIDE = 4`, confirmed on Zul'jin, 2026-10-12); parked for the art pass - the coin is
   a touch big for its window, and the strip could grow further up the slant.
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
   build 57474cd (the straight meter left of the badge and the bare ring right of it are
   diagnostics, to come out). Next: contrast (docs/polish-research.md). Seen fine in 5c38a32: the heroic badges 6 in from the cell's end (gen
   `HEROIC_CLEAR`). The chrome's shadows are to be revisited later (user).
   **TEMPORARY:** Blizzard's kill feed is hidden for testing (FCJH_Hidden, `FCJH_KeepHidden`'s
   KillLogPanel controller; user, 2026-10-16). Take it out before release.

   Diagnostics: the respawn, hearthstone and portrait ones are read and gone (2026-10-16);
   `onfire_diagnostics` stays until a known on-fire replay.
   The intro waits for the user's OBS plan. The items as the user gave them:
   - **The plates closer to the player's in-game top bar.** Played as a player, Blizzard's
     plates feel far more polished than the observer's; find out what we can copy (the
     player HUD's layouts in JamiePhan - their animations and StateGroups);
   - **Split plates for heroes with more than one unit** (Rexxar and Misha, the Lost
     Vikings). The player's top bar slices their boxes much better than the observer view:
     when Misha dies, only her part of the portrait darkens, and her death timer sits
     centred on it. Today Misha's bar is hidden and Rexxar's runs full height; the Vikings'
     bars and timers are in thirds. See item 15 too (Blizzard's three-slice Vikings plate);
   - **Death timers flash white under 5 s**, like the player view's (the same as the
     death-timer note above - find Blizzard's animation);
   - **Ahli's death animation** - a skull animation, then the countdown (item 12);
   - **A frame round each team's row of plates**: silver-grey metallic like the top bar's
     edges, about 3 px, slanted where the plates slant, to cover the gaps and overflows
     between heroes;
   - **An intro animation for the elements, to pair with OBS** (more from the user later;
     Ahli's plates slide and fade in, above).
12. **Ahli's death animation on the nameplate** (user, 2026-10-05: "a nice touch", not to
    copy) - his plate does something when its hero dies: a skull animation, then the
    countdown (user, 2026-10-16). For the art pass (item 7): study what it does, then design
    our own.
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
    - **rows with fewer than five heroes** (a 3v3 or 1v1 replay);
    - **every map**: the map objectives, the minimap per map (docs/maps.md; the jitter is solved -
      map id, 2026-10-09; every map id read in game by 2026-10-15);
    - **Cursed Hollow, blue cursed** (docs/maps.md): the banner on blue's side, left of the map,
      ending at the map's edge, its text and timer inside the art - not yet seen (user,
      2026-10-06: red's looks great);
    - **Infernal Shrines, blue's Punisher** (user, 2026-10-15: the bots never got one - a human
      replay): on blue's side, mirrored - the icon at the outer end, the backing flipped, the fill
      draining from the right, the % at the outer end (`maps.punisher_side`);
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
16. **Static banners hidden - revisit AFTER the final pass (user, 2026-10-15).** Word-only
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
    Left as they were, brief: Volskaya's 2 s point toast, Towers' 5 s tunnels notice.

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
