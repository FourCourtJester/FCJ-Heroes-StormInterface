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
info panes, the inspect card, the top bar and the visual-language agenda for the art pass.
Those boards are drawn from the build's own numbers by `design/canvas_gen.py` (it imports
`tools/gen.py`; untracked, like the rest of `design/`): after a layout change, run
`python design/canvas_gen.py` and publish `design/canvas/project/` to the canvas.
**Every build is checked against it.**

In one paragraph: the ten hero cells sit along the bottom (blue 1–5 left of the minimap,
red 6–0 right of it) with portrait, HP, mana and CC; the minimap and its objective widgets
at bottom-centre; team core HP above the cells; a two-line top bar of series score, team
name, logo and level either side of Blizzard's hexagon, with bans, bracket and game count
beneath; Blizzard's own kill feed top-left; replay controls top-left, collapsible; info panes
(talents, KDA/damage, healing, siege) at middle-left on hotkeys; talent pop-ups on the
cells, and a green-plus pop-up on any hero below 25% health (drawn under the talent
pop-up). **Fight mode is not a separate layout** — it is one hotkey that hides a list of
elements (so far: the info pane and the health markers). The top bar and minimap always stay.

**Branding is negative space**: names, logos, scores, bans, bracket and game count are
drawn by OBS over empty regions the interface leaves (§6).

**Status, 2026-10-05: Phase 2 (building the default view) is well along.** Phases 0
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
  the default UI's small inspector would (never while a replay is paused). Hero forms and
  empty slots await the final pass (§7 items 3, 14).
- **Kill feed** — Blizzard's own, top-left. **Minimap** bottom-centre, placed per map with
  each map's objective panel round it and a team's alerts stacked on its side (§7 item 8;
  Towers of Doom passed QA on the per-map system 2026-10-06, the rest a first pass; since
  2026-10-09 every map can be told apart from load by Blizzard's map id - §7 "Next"). **Replay controls**
  top-left with a tab when collapsed (replays only). Blizzard's player HUD never shows; its
  talent picker is left to the game: held Ctrl shows it, steady, only in a player's view
  (1-8 keys), not when following from a plate click - as in Ahli's and Spazzo's UIs (§3;
  confirmed 2026-10-06).

Not yet: the OBS graphics package, the fight-mode hotkey, and the visual pass that takes the chrome look of
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
`+` meaning uncommitted changes — and tints every wireframe box on screen in its legend
colour (white: ours, orange: OBS space, teal: on demand), so each element can be built
against where it is meant to land. `--release` is exactly what `src/` holds: it refuses
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
src/dev/                                     dev-only probes (empty now; packed into dev builds)
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
- **Open:** Abathur's Symbiote swaps the card to Symbiote's buttons, some of them in slots we
  park (gaps) - §7 item 3, card swaps; the mount reads as Blizzard draws it.

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

**Branding is negative space**, drawn by OBS. The interface can't see OBS, so there is no
in-game fallback for missing names or logos.

**Plates are Blizzard's in-game top-bar cell, not the observer's.** Its art, sizes and
stacking are rebuilt in `tools/gen.py` (`HeroCell`) and only scaled; the portrait crop is
worked out from the cell's shape. The user wants that look (their screenshots are in `design/`).

**Fight mode = a hotkey that hides a list, not a layout.** The agreed default view already
is the old fight-mode cluster. Pooled team HP is dropped: layouts have no arithmetic, and
five segments would duplicate the hero row. If plates read too small, widen them.

**Art is sized for 1440p and scaled down at 1080p** (user, 2026-10-06), not the other way
round. Every generated texture is its frame's size on a 2560 x 1440 screen (`gen.py
ART_HEIGHT`; sizes needn't be powers of two), so it's 1:1 there and drawn at 75% at 1080p.
Layout numbers stay 1080p px, the resolution we test at; any 16:9 screen gets the same layout
(1200 units tall). Not yet looked at in 1440p: the inspect card's edge lines are worked out to
land on whole pixels at 1080p (`inspect_card.line`), so at 1440p they may come out 2-3 px.

---

## 7. What's next

**Next (2026-10-09, end of night; start here).** The map pass: the four working maps and
Dragon Shire are DONE (items 3-4; Dragon Shire's knight on either team's side, blue's mirrored);
Blackheart's Bay DONE 2026-10-12 (chests banner, either team's cannon, the plates' carried
doubloons); Garden of Terror DONE 2026-10-12 (the seed banners, the Terrors on the summoning
team's side; blue's Terrors still unseen). The banner protocols' recheck PASSED on all five
(2026-10-12). Alterac Pass DONE 2026-10-14 (everything below seen and approved in one pass). Hanamura
Temple DONE for now 2026-10-14 (user: "for today, it's good to go"; its split is a Later).
**Next: the rest of the newer maps' QA** (item 4).
For each, screenshots of: the map id at load
(the diagnostic, now just that line), each banner as it comes up, anything hanging off the
minimap's bottom. Hero test rosters come from the tracker in item 14 ("not seen yet").

**Recheck after the banner protocols (2026-10-12, d2604a6 and after; §3 "Banners"): PASSED (user,
2026-10-12: "all the banner generation on the other maps seem solid", every map before Alterac).
Not recorded: whether a replay showed blue's curse; check it if one does.** What was checked:
- **Mines, shrines, seeds, curse:** the banner holds its width while the count runs, down to single
  digits. A narrow count leaves a wider space before it.
- **Dragon Knight:** both bars are on the standard tip now, red's 3 units (about 3 px) left and
  blue's 2 units out.
- **Curse, red:** 3 units left.
- **Curse, blue:** now the mirror, never seen. The raven is flipped at the outer end with its glow
  around it, the words read toward the tip, and the bar runs from the raven to blue's inner edge.
- **Cannons and Terrors:** unchanged, position for position.

1. **Look in game at what's built but unseen** (build 2026-10-09 evening):
   - **Haunted Mines: DONE (user, 2026-10-09).** The two views and the glide (once only), the
     skull counts' line back (it was clipped under its panel: Unclipped), skulls and counts 2 px
     lower and 4 px in, the "Needed" plaque 28 px in the gap between the maps (the bar art
     stretched whole: a squeezed nine-slice loses its corners), riding with the minimap; centred
     in the gap 2026-10-12 (6 px up, by measure then eye). The
     surface sits ~20 px left of centre in Blizzard's art at launch: left as is (user: it
     lasts two minutes).
   - Cursed Hollow: the tribute and curse banners now FADE in without sliding - check both
     land on their spots every time, the curse on red's side and (if a replay has one) on blue's.
2. **Banners stay put - check on each map in the pass:** every bar's bottom on the one place
   (`[map_alerts] above_core`), the tip on the plates' inner edge, with and without the core
   bar, and the intros (tribute, curse, zerg, mines) not shifting them. By the code they can't
   move with the minimap: all 90 banner anchors and stack moves are to the screen (checked
   2026-10-09). Any banner whose sides a STATE moves must stay fade-only (`maps.FADE_ONLY`).
3. **The four working maps, map by map (map-id tech) - ALL DONE (2026-10-09):**
   - **Haunted Mines** - DONE (above).
   - **Cursed Hollow - DONE (user, 2026-10-09):** id read in game (`CursedHollow`), banners
     correct, the tribute and curse fading in. It's the BASELINE (user): `[minimap] bottom` is
     its place, so it keeps no `own_place`; the other older maps get their own. Changing
     `[minimap] bottom` moves Cursed Hollow and the ARAM maps.
   - **Braxis Holdout - DONE (user, 2026-10-09):** id `BraxisHoldout`; its zerg banner slides
     in (only the tribute and curse are fade-only). Its zerg HUD compacted (maps.py
     BEACON_ICONS / ZERG_WORDS / ON_AIR):
     - the %s centred in their hexagons;
     - the dishes against each hexagon's lower outer edge, 4 px down, anchored to the hexagons
       (BossDuelLeftFrame/BossHudLeft, /BossHudRight), so they follow the HUD;
     - the electric line hidden (Alpha 0), kept as the signal: the script shows blue's pair
       (Link1-2) while BLUE holds both beacons, red's (3-4) while red does. A state on it shows
       "on air" rings in that team's colour over both dishes (FCJH_OnAirBlue/Red): a breathing
       ring on the dish's border and a wave rolling out from it (Storm_UI_GenFX_RingGlow,
       tinted). Tried first and dropped: the line along the map's bottom edge, then a beam from
       each dish into its hexagon (Rotation works: degrees clockwise, about the middle);
     - "BEACON PROGRESS" and the wave's "Enemy Zerg" above the bar, on Blizzard's "Allied
       Zerg" row; the HUD 20 px lower (`[minimap.panel_nudge] braxis_holdout = 24`);
     - its map 18 px down onto the floor (`[minimap.nudge] braxis_holdout = 18`); the mechanics
       panel no longer goes under the minimap.
   - **THE FLOOR, every map (user, 2026-10-09):** no map's visual bottom edge (its art's
     outline, not the texture box or unit icons) may sit lower than Cursed Hollow's: y ~1065
     at 1080p (`[minimap] floor`). Haunted Mines is within it; Braxis sits on it.
   - **Towers of Doom - DONE (user, 2026-10-09):** id `TowersOfDoom` read in game; nothing to
     adjust. Its map's visual bottom ~1066, on the floor; the blue/red line between the bell
     markers sits just under it, on the screen's minimum edge (user: fine as is).
4. **Dragon Shire - DONE (user, 2026-10-09):** id `DragonShire` read in game; its map's bottom
   ~1060, inside the floor, at the shared place (no own_place - nothing to move).
   - The shrines' countdown is the neutral banner on red's side (maps.py SHRINE_*, laid out
     from its left end as the mines'); the Dragon Knight replaces it from the same spot
     (DRAGON_PARTS), its timer up on the name's row, ~12 px before the % (DRAGON_TIMER).
   - The knight on its team's side, like the curse (user, 2026-10-09; blue's confirmed in game):
     blue's on blue's spot, mirrored - head flipped at the outer end, "% timer" from there,
     "DRAGON KNIGHT" at the inner end, its health draining from the right (knight_side). Told
     by blue's moon and star both still lit: the script stops setting them once the knight is
     up, and the markers' hidden panel doesn't stop a When reading them. Red's knight after a
     blue one went back to red's layout, draining as before (user, 2026-10-09). Blue's backing
     flipped (our copy, TextureCoords); its fill can't be - a status bar ignores TextureCoords -
     so it's widened and cut to the mirrored lean by a mask of ours (knight_mask), its outer end
     overshooting the backing as red's does (Blizzard's own). DONE (user, 2026-10-09).
   - The shrine markers (moon, star) up from off the screen, their team line level with Towers'
     at ~1070 (`[minimap.panel_nudge] dragon_shire = -29`); the stars clear the map's flanks.
   **Blackheart's Bay - DONE (user, 2026-10-12):** id `BlackheartsBay` read in game; its map's
   bottom tab ~1056, inside the floor, at the shared place.
   - The doubloon counts' team line up to ~1070, level with Towers' (`[minimap.panel_nudge]
     blackhearts_bay = -30`; they'd been cut off by the screen's edge).
   - "Chests have spawned" is the neutral banner on red's side (maps.py CHEST_*), with the full
     intro: its bar is a nine-slice from the frame's left, as the cannon's, so the bar grow has
     a left end to move (Blizzard's is a fixed-width image anchored at its right only - nothing
     grew, 2026-10-12).
   - The cannon on the firing team's side (cannon_side, told by Team1ShotCounter's Visible):
     red's Blizzard's layout, blue's mirrored - our flipped cannon at the outer end, the pips
     running right from it, our copy of the words and count. Fade-only (FADE_ONLY).
   - The plates' carried box shows the doubloons (item 7's note; gen.py `carry_box`).
   **Garden of Terror: DONE (user, 2026-10-12).** Its id `HauntedWoods` read in game.
   - The seed counts' team line 29 up (`[minimap.panel_nudge] garden_of_terror = -29`).
   - "Seed spawning in" and "Gather the seed!" are neutral banners on red's side (`seed_banner`
     on `left_banner`; they're templates of the map's own file, so they're overridden through
     PARTS and hang off our spot). They restate their box's size: the template's 600 x 140 was
     centred on the box.
   - The Terrors' health is on the summoning team's side (`team_banner`, told by its ACTIVE seed
     count): blue's is Blizzard's way round, red's the mirror. **Blue's not seen yet** - blue never
     summoned in the test replay; look next time.
   **Alterac Pass: DONE, every item closed (user, 2026-10-14: "That looks great!", then on the
   clean build 0c07030: "Everything can be marked off for alterac").** Its id `AlteracPass` read in game. One Blizzard
   frame (`AVMechanicContainer`) shows the prisoners countdown, then the cage fight, then the
   cavalry's health. Measured at Blizzard's place (all four modes seen there, both teams' cavalry).
   - It hangs off a carrier of ours (`maps.av_carrier`). The first build (caa5687) put the
     prisoners and cage on red's spot and the cavalry on its team's; seen in game, all four landed
     (tips 1167 / 755, brackets 930), and the carrier move worked both ways.
   - **Redone (user, 2026-10-12, having watched it a few times): the prisoners and the cage stay
     above the minimap, at Blizzard's place; once the cage is won its outro plays there and the
     cavalry appears on its team's side.** The carrier sits at Blizzard's place; on `TeamWins`
     1 or 2 it jumps to that team's spot 0.6 s on (`AV_HANDOFF_S`: Blizzard's cage bars are
     gone and the cavalry plate shows then), by a relative Anchor controller with gen.py's
     `FCJH_MAP_AV_<TEAM>_DX/_DY`; `TeamWins` 0 resets it. Checked:
     - the cage's outro above the minimap, then the cavalry on the winner's side. If it jumps
       before the outro, `TeamWins` is set before "MechanicDone" and the delay needs raising;
     - the next prisoners back above the minimap (if not, `TeamWins` doesn't return to 0);
     - the hexagon jumps with it at 0.6 s (a cut, not a slide).
     **Seen (user, 2026-10-13):** the outro above the minimap and then the jump "looks like a
     staggered movement; not quite polished", and when blue's cavalry died the slain banner went
     back above the minimap (the script resets `TeamWins` and sends "Hide" 5 s after
     "CavalrySlain"). Now (`maps.av_parkers`): the banner is parked off-screen from the win until
     it lands on the winner's spot at 0.6 s, and from "CavalrySlain" until the next round's
     "Show": no outro above the minimap and no slain line. Seen (2026-10-14).
   - **Both teams capturing lit only one half of the cage's hexagon** (Blizzard's, seen in Ahli's
     too; user, 2026-10-13): it lights "who's winning", whoever channelled first. Now
     (`maps.av_both_lit`): with both bars capturing (`TopBarCaptured` and `BottomBarCaptured` "10"
     or "11"), our copies of both lit halves and glows draw over Blizzard's darkened half. Seen (2026-10-14).
     If a copy shows outside a capture (after the win, say), the bars' states outlive it.
   - The neutral banner sat 10 px lower (user, 2026-10-13); since 2026-10-14 it's placed by THE
     GAP (Hanamura below; `maps.py above`) - 10 px back up, unseen. The cavalry's jump allows for
     it (gen.py), so only the neutral moves.
   - **The cage bars broke (user, 2026-10-13, against the default UI):** in Blizzard's, the fill
     and its timer move while the team-coloured backing stands the bar's length; in ours the
     backing slid along with the fill. Cause: `Unclipped` on the frame (to draw past its panel on
     red's spot) took the clipping from inside it. Fixed: no `Unclipped`. Instead the panel strip
     is widened (`AV_PANEL_GROW` right, 200 left), and the carrier and flag alerts are placed back
     from its new right. The cavalry's plate and fill-up slide in under masks too: check
     they don't show outside the bar.
   - **Then the bars drew cut short (user, 2026-10-13):** no timers, no red stub, the fill's end
     off. A diagnostic (coloured strips spanning each frame on the bars' chain) showed the bars'
     strip (`ProgressBarsContainer`) 891 units wide: Blizzard anchors its Left and Right to two
     different points (art Mid -210, +218) with Width 463, and ours resolved each side as its
     anchor -/+ half the width, so the bars started far left under the mask. Fixed
     (`maps.av_bars`): both sides on one point, Mid +4, which centres 463 on Blizzard's span.
     **Seen and approved** (user: "looks good"), matching the default UI at the same times.
     Lesson: a Width with Left and Right on DIFFERENT points isn't centred between them.
   - **Technical limitation (user, 2026-10-12: "not the end of the world"): not mirrored.**
     Blizzard's animations slide its parts: the hexagon 373 left when the cage starts, the cage
     bars and the cavalry's fill-up in from the left. Each slide counts from its layout anchor, so
     no state can mirror them. Blue's cavalry is Blizzard's way round, which is blue's mirror; red's
     keeps the hexagon at the inner end. Accepted as is (user, 2026-10-14: everything marked off).
     If it's ever wanted: restate those animations for red and flip the cage's `ProgressBar`s
     (the `$this` anchor trick, untested - no Blizzard bar fills right to left).
   - **The camp alerts (`NotificationFrame1`/`2`) go to the side their event names (user,
     2026-10-13):** Alliance's (EventID 11/12) on blue's, Horde's (21/22) on red's, on that side's
     stack - a slot up for the cavalry there, and alert 2 a slot up for alert 1 there. Each hangs
     off a carrier of ours (`maps.camp_slot`, states keyed on its EventID) so Blizzard's intro
     still slides. Art kind `CAMP` measured off the default UI (`ALERT_ART`). Seen (2026-10-14). Technical
     limitation: not mirrored on blue's side (one frame serves both teams; the intro's relative
     slide would undo a state's mirror), so blue's hexagon is at its inner end.
     Earlier they were pinned where Blizzard's banner sits between rounds (seen stacking over it).
     **Seen in the default UI's everyone view (user, 2026-10-13):** they
     are for observers and they stack. Their words are blue's player's ("Allies capturing enemy
     camp" = blue capturing). Ours name the side (user): "Alliance capturing Horde camp", "Horde
     retook their camp" and so on (`maps.camp_words`). The team comes from the alert's EventID; the
     English words only gate the kind and the language. The placement was seen working
     (2026-10-14), the words weren't: the first build drew a label of ours over Blizzard's, hidden
     by Visible - ours drew nothing (its Style bound to Blizzard's label's) and Blizzard's stayed
     up. Now the side names are written into Blizzard's own label (its EventID states already
     colour it); once written the words stop matching, so nothing loops. Nothing added to the
     alerts' template (`AVNotificationFrameTemplate`) reached them, so the states sit on each
     alert (`NotificationFrame1`/`2`). Written into Blizzard's label it worked, then reverted on
     a later alert (the script rewrites the label; a state already entered doesn't act again).
     Now Blizzard's label is hidden for good and ours, in its style, takes the words by the event
     alone (any language gets ours in English); until a state runs it mirrors Blizzard's words
     (after a replay seek one alert showed no state had run). CONFIRMED (user, 2026-10-14): both
     teams' words, several rounds, after a fast-forward to 8:37; the diagnostic line is gone.
     The cavalry-slain line ("All Allied/Enemy Cavalry Slain", in the banner itself) had the same
     player's wording, but it never shows now: the banner is parked from "CavalrySlain" (above).
   **Hanamura Temple: DONE for now (user, 2026-10-14: "for today, it's good to go").** id `Hanamura` read in game (Spazzo's, as
   guessed). Its map's bottom was ~1047, 18 px above the floor: now 18 px down onto it
   (`[minimap.nudge]`, user 2026-10-14: "Minimap looks good").
   **No per-side alerts here (user, 2026-10-14):** the countdown ("Payload spawns in"), the
   payload's push status and the shots ("Shots remaining") take turns in one place above the
   minimap and animate as one, so all three stay Blizzard's, there. Tried and dropped: the
   countdown on red's side and the shots on their team's - blue's shots came out clipped (the
   intro slides the icon 198 right, past the frame's edge). "CONTESTED!" above the hexagon
   instead of under it (the escort counts there are hidden while contested): seen and approved
   (user: "Contested looks good"), and blue's shots ("shots remaining looks good").
   **The objective never moved:** a 26 px panel nudge did nothing (the hexagon stayed at ~798,
   which I misread as moved), and the minimap's 18 px move left it behind (user: "you didn't
   bring the alert with you"). Its frames hang off each panel's MinimapProxyFrame, which
   Blizzard ties to the minimap by `$parent/$parent/$parent` - and that never followed. Now tied
   by the full path (`maps.proxy_lines`, `proxy=True`), as everything that does follow is.
   **THE GAP (user, 2026-10-14: "standardize that gap between maps"):** every neutral objective
   above the minimap sits `[minimap] alert_gap` (10 px) over the drawn map's top tip. Each such
   map has a measure (`maps.py above`: px over the tip, at a known panel move); gen.py's
   `panel_nudges` moves its panels to the gap. Alterac: measured 0 at 10 down (its cage's
   hexagon on the tip), so it goes back up 10 (unseen). Hanamura: ESTIMATED from the template
   (35 over at 0), so 25 down - measure it from the next screen and fix `above`. Every newer
   map left gets a measure (and `proxy` if its frames hang off the proxy) in its QA.
   Red's shots never fired in the test replay. A spawn's flick (neutral, blue +1, neutral) was
   seen in the default UI too; most likely Cassia at the payload's edge as it spawned (user,
   2026-10-14) - left as is. If it recurs with no one near, suspect the validator's state left
   from the previous payload (hide the status ~0.25 s after it shows).
   **Later (user, 2026-10-14): come back and split the objective into its parts** - the
   countdown, the push status and the shots, each placed by the banner protocols (the countdown
   neutral on red's side, the shots on their team's, blue's mirrored), instead of Blizzard's one
   spot above the minimap. Why it was left: Blizzard animates the three as one unit in one place,
   so pulled apart they didn't look good. What we learned: the countdown is Towers' alert
   template and moved fine; the shots' intro slides the icon box 198 right of its layout place,
   past the frame's right edge, which clips it (Unclipped on BackgroundImage and NotificationIcon
   fixes that); the shots' art then runs 274 left of the placed edge to 246 right of it, bar
   bottom 28 over the box's (off one blue screen; never committed -
   these numbers are the record). The countdown on red's side was 95114db.
   Next try, if wanted (2026-10-14, ~75-85%): not copies (the status's validator gets its unit
   from the script only) but Alterac's way - each team's shots frame on a carrier on its side,
   a parker hiding the status's outro; the unknown is the script's cue for the hand-off.
   Also: THE GAP's measure here is still ESTIMATED (`above`) - measure it off any screen of the status.
   Roster played (user, 2026-10-14): blue Azmodan, Cassia, Lunara, Tassadar, Yrel; red Medivh,
   Deathwing, Abathur, Samuro, D.Va.
   **Tomb of the Spider Queen (done, user 2026-10-15: "I think that's that"):** id `Crypts`
   read in game. The gem counts (`CryptPanel`, hung off the minimap's bottom, no proxy) at
   ~1030, as Garden's. The minimap 29 down (40 cut off its bottom marker - a building's, ~1036
   at 0; the floor now counts the map's own markers). The Webweavers' banner (`SoulEaterFrame`,
   one frame for both teams, neutral) and the egg timer (`SoulCageCooldownFrame`, shown after
   the Webweavers die) at THE GAP over the minimap, as maps.py `gap_parts` (a part placed on its
   own, its panel kept to its nudge). Its art is drawn ~21 px left of its square's centre: the
   minimap 18 px right (maps.py `across`, its panels taken back - only the map moves).
   The Webweavers' hexagons (user's plan A): Blizzard's own set per team
   (`SoulEaterModeBlueFrame` / `RedFrame`, the summoner's shown) on that team's side, in the dead
   space between the drawn minimap and the plates - from the gem counts' line (1071) up the
   minimap's height, each 40 px further out, centred between the minimap's side and the plates'
   edge then 10 px out (maps.py WEAVER_*, gen.py places them). Seen on fb854f0, both teams
   (red's centres 1109 / 1149 / 1189, blue's 805 / 765 / 725). Their health image must stay
   clipped: the script drains it by shrinking its frame (Unclipped there kept it full; fixed in
   6c52e5e, drain seen). Clicking them can't pan the camera (no click events in the script, no
   unit behind them; the user let it go).
   **Warhead Junction (done, user 2026-10-15: "I think that's all for this map"):** id
   `Warhead Junction` (with the space) read in game. Drawn centred (no `across`); its outline's
   tip, its lowest part, 1043 -> the floor: [minimap.nudge] 22, seen at 1065 (1b0dea6). The nuke
   counters (`SC2Panel/Team1TerrazineFrame` blue, `Team2` red - hung off the minimap's bottom
   either side of its tip, cut off at the screen's bottom at Blizzard's place) 50 px out and up
   (maps.warhead_counters): seen clear of the map, icons ~815-870 / ~1040-1100 down to ~1062;
   then 2 more up (cd1e81b, unseen) for their team strips, uncovered by the lift, to end on the
   floor. The warheads' banner (`TerrazineEruptionFrame`: the countdown, then how many are left)
   moved as Blizzard draws it to red's bottom slot - a neutral banner, no copied words (user);
   its box is the English countdown's, so the other text's tip lands off red's plates by its
   length (1b0dea6; not screenshotted). Its other SC2Panel parts (NukeSiloFrame, TerrazineBuffFrame)
   not seen on screen.
   **The minimap's tooltip - OFF, every map (user, 2026-10-15: "Just hide it or disable it";
   seen gone on 08eeb21).** Hovering a named minimap icon (a watch tower, a fort, Tomb's Spider
   Altar) showed Blizzard's `MinimapPanel/MinimapPanelTooltip` at ~1332-1467 x, ~800-850 y,
   stranded by its `$parent` anchors when we move the panel. Not stoppable at the source (no
   tooltip frame named: the name showed anyway, clamped elsewhere; the minimap with tooltip
   hover off: no change); the box is see-through instead (FCJH_Minimap.StormLayout).
   **Volskaya Foundry - DONE (user, 2026-10-15: "perfect. mark it done!").** Id `Volskaya`
   read in game; minimap 7 down to the floor (a1f60ca). The toast (`VolskayaToastContainer`,
   maps.TOAST): our banners' font, a sentence before its count while counting
   (VOLSKAYA_UNLOCKS_IN, every language), the bar out to the sentence and centred on the screen
   in every language (6ff536a: the bar's right end hangs from the Mid of a hidden copy of the
   words shown, anchored by its Left only - half their width out). CONTESTED over the capture
   hex, hidden in overtime from the robot's frame (a `<When>` naming a script-built frame built
   AFTER the watcher never fires; the script builds capture panel, toast, overtime, robot in that
   order). The robot (`VolskayaRobotHealthSlideout`) a team banner (maps.robot_layout): blue's
   fill its own bar copy (FCJH_BlueHealthBar - the progress bar mirrors only its mask layer),
   the timer over the %, pilot and gunner beside the robot (THE GAP). Its outro is Blizzard's
   own animation, the same in default - left alone. SetAnchor relative="$this" doesn't take:
   name frames by path.
   **Battlefield of Eternity - in QA (2026-10-15, bot game).** Id `BattlefieldOfEternity` read in
   game (9f4d45f). Minimap 16 down to the floor (60558ea, unseen). One panel (`BossDuelPanel`)
   above the minimap, its three phases taking turns there as Hanamura's do: the countdown
   ("Immortals spawning"), the fight (BossDuelLeft/RightFrame, Braxis's zerg template) and the
   winner's Immortal pushing (BossLaningFrame, one frame recoloured per team - a team's, but kept
   there with the other two, as Hanamura's payload). "IMMORTALS FIGHTING" moved above the bars as
   Braxis's (user: "like the other maps"); the fight's numbers set to THE GAP (`above=(13, 0)`,
   29d57e6); the lane frame 22 down so its hexagon meets the same line (a30f3a5). The panel 9 right: Blizzard draws its boxes 8 px left of centre (the map itself is centred). All unseen.
   **Then the rest of the newer maps' QA
   (Shrines, Sky Temple). Any map could get a two-view or other per-map behaviour the same way
   (`launch_cut`/`opens`, `on_map`).
5. **The diagnostic - trimmed to the map id (user, 2026-10-09);** remove `maps.diag` and
   `FCJH_DiagMapId` once every map's id is confirmed in game (MAP_IDS' GAME sources).
6. **Inspect card, intermittent (user, 2026-10-09):** on hero inspects only, now and then the
   ability BORDERS keep showing after the card hides. Not pinned down yet: next time, a
   screenshot of it. Lead (unconfirmed): the only border-like art that can show without a
   unit is ours, the empty-slot frames under Q W E R (`FCJH_EmptySlot*`,
   `inspect_card.command_panel`). They live in Blizzard's command card, not on the card, and a
   button with no unit is Cleared (alpha 0) but our frames aren't. So if the card hides while
   the gate (`FCJH_Gate`) is still "Hero", the command card stays on screen and only those
   frames show. Suspects for the gate missing it: the engine hiding our TargetInfoFrame
   itself (an inspected hero dying?) while Blizzard's parked one still reads visible.
   Likely fix: move the empty slots onto the card (they hide with it; the command card
   draws over the card, so the buttons still cover them), hero-only via `shape()`.
   **Later, a simplification (user, 2026-10-09):** treat this and the resource tooltip
   refresh (item 14) as one problem.
   - **One controller.** Blizzard's hidden inspector is the single source of truth (round 9),
     and everything of ours derives from it.
   - **No second opinions:**
     - our card is a TargetInfoFrame, so the game can show or hide it by itself;
     - the gate copies state onto pieces (by SetProperty and SetAnchor) instead of having
       them follow it.
   - **One missing input: a swap signal.** The inspector stays visible across a hero swap, so
     nothing reruns the tooltip states. A swap state is needed, closed -> open, like Blizzard's
     per-target rebuild.
   - **Prove the swap signal with a diagnostic first.** Does a label's text change alone rerun
     a group? That is memory rule 26, unverified.
   - **Keep the command card and its tooltips.** They are the commentators' only live ability
     data (user).
7. **Parked:** the resource tooltip refresh; blue's curse mirror (unseen).
8. **Later: extract the toolchain into its own repo** for open-sourcing (user, 2026-10-09) -
   the plan, inventory and open questions in [docs/extraction-plan.md](docs/extraction-plan.md).
   After the map pass and Phase 2.

**Earlier next** (end of the 2026-10-05 session):

Waiting on a look in game: the short inspect card without its resource slot. (Blizzard's
talent picker, left to the game: seen 2026-10-06 never coming up on its own in a player's
view, only on held Ctrl.) Done this session: panes in Blizzard's talent
grid and the inspect skin, hotkeys settled (our panes on Ctrl+1-4; the inspect and death
recap keys tried and dropped), the short card for non-heroes (camp mercenaries purple,
captured ones their team's), hero forms and empty ability slots (item 3), Towers of Doom's
alerts (item 8), and (2026-10-06) the plate fountain on the health bar's outline at the outer
end with blue's heroic mirrored to the inner end (§1). Unchecked from that: blue's heroic
tooltip hover after its move, the end of blue's narrowed bars (Blizzard's short-bar art is
shaped for a heroic on the left), and whether the inspect card's fountain shows the same thin
unmasked line the plate's did (its icon is drawn 45 in a 40 mask box). Open items, the
user's pick of order: the art pass (7, 12). Anchoring (4) built 2026-10-06; its non-16:9
test waits for the final pass (14). Every map's minimap, panel and team alerts (8) built 2026-10-06, a first
pass to fine-tune with test maps (user): Towers of Doom and Cursed Hollow DONE (2026-10-06);
next Braxis, Haunted Mines, Hanamura and on - each map's neutral banners move to red's column
as it's QA'd. Later, not now (user): the older maps' minimap jitter (item 8). Camp timers (13) dropped. Item 14 collects what
waits on replays with particular heroes and maps.

Confirmed in game by then: heroic tooltips on every plate (Varian's level-4 heroic, Tracer's
Pulse Bomb with its title line), heroic cooldown counts, click-to-follow (needs the game's
camera lock, **L**, on - observers can toggle it; a day of bisecting 2026-10-05 ended there),
Tracer's charge meter (Blizzard's art), talent and heal pop-ups (pane-sized; heal 2 px
smaller; on the plate's top edge - the user will judge that from viewers' feedback), the
inspect card with Blizzard's command card on it (tooltips, cooldowns, Tracer's count centred),
and the card's talent tooltips on both teams (2026-10-05). How those tooltips finally held:
Blizzard's WHOLE top-bar talent panel as the root
(`template="TalentsOverviewPanel/TalentsOverviewTopBarTemplate"`), our overrides on top - as
the plates' heroic-tooltip copies are built. Assembled from parts (a CleanTalentsPanelTemplate
whose `HeroTalentsPanelContainer` we re-templated in our own declaration), the rows kept
Blizzard's icon places and sizes (`inspect_card.talent_tips`).

1. **Inspect card: DONE (2026-10-05, evening QA rounds through f1496c6).** Seen and approved
   in game: hero name centred in the title band, player name and level (16, set 2 low in their
   band), team-coloured edge, Blizzard's inspector art as the background (permanent, 90%; its
   border under the contents), one padding (`PAD` 10) everywhere inside the edge, the card cut
   to fit (583 units, 525 px; gen refuses a layout.toml size that disagrees), the fountain as
   the first buff with its countdown and tooltips ("Healing Fountain Available" while ready),
   abilities spread across the card with the talent actives nested over the gaps (a honeycomb),
   talents spread across with pixel-exact empty-tier boxes (`inspect_card.line`), stats in
   three related rows, the Vikings' portrait on its own crop, no X (clicking off closes it),
   mirror matches (a team sensor, `team_sense`), and no stray lines or tooltips (Blizzard's
   inspect box contents hidden every frame, `FCJH_Hidden`). Left: placement (item 9).

   **All panels - DONE 2026-10-05 (through d716d10), seen in game:**
   - every pane wears the inspect card's look (Blizzard's inspector art, background 10%
     darker): one template, `FCJH_Constants/FCJH_PaneSkin` from `inspect_card.pane_skin`, at
     priority 400 under the rows. Blizzard's own pane backdrop (`obs_talents_bg`, one picture
     with the hexes and the blue-to-red blend) was tried, turned top to bottom, and scrapped.
   - the talents pane has Blizzard's row grid (`obs_talents_top`, 1130 x 60: blue's 565 on
     the left, red's mirrored) behind its rows, 2 above the first row as Blizzard hangs it;
     portraits and talents fitted into its boxes (heroic tiers 4 and 7 at 46). The pane's box
     didn't change.
   - **Later: the numbers panes (KDA, healing, structures) need a better visual** - fine for
     now (user). Their colour pass for both teams goes with it. Blizzard's stats grid art
     (`obs_stats_top`: a portrait box and five column cells per row, blue left, red right)
     and the leader underlines (`obs_stats_leader_blue/red`) are candidates (seen on a dev art board
     at native size, since removed: obs_stats_top is 1130 wide like the talents grid).
2. **Command card polish - DONE (2026-10-05).** Talent-granted abilities seen clean in the
   honeycomb on Sonya (level 16) and Chromie (a talent-granted ability, user): the morning's
   oversized art behind them (flame frame, faded portrait; `Screenshot2026-10-05 11_16_54.jpg`)
   went with the honeycomb's per-piece sizing. The mount button and the top row's layout were
   settled by the honeycomb too.
3. **Card swaps - researched 2026-10-05; forms built, awaiting QA.** What the data says:
   - **There's no swap to follow for an observer.** Blizzard has no per-hero command card
     layout; one CommandPanel shows the card of the unit it follows, and each form is a unit
     with its own card (`CardLayouts` in the unit data, buttons placed by named Slot:
     Ability1-3 = Q W E (00-02), Heroic = R (03), Mount = Z (04), Trait = D (05), Hearth = 13,
     talent actives 30-35; the slot-to-button map is the engine's). An observer's card follows
     the SELECTED unit: selecting Abathur shows Abathur's card even mid-Symbiote (the
     Symbiote is a unit of its own, `AbathurSymbiote`, the player steers). The "gap" in the
     user's Abathur screenshot (09:45:55) is his own card: Abathur has NO E (Ability3).
   - **Forms built:** units of their own that our hero check and player matchers didn't
     know - Medivh's Raven (`HeroMedivhRaven`), Deathwing's Dragonflight
     (`DeathwingDragonflightUnit`), Alexstrasza's Dragonqueen (`HeroAlexstraszaDragon`),
     Ragnaros's Molten Core (`RagnarosBigRag`), plus Greymane's Worgen, Valeera stealthed and
     Deathwing's World Breaker - `inspect_card.FORMS`, paired with their hero every way
     (which unit the plate shows meanwhile is unknown). To QA: each form shows the tall card
     with its player's portrait and talents, and its own buttons.
   - **Empty slots - built 2026-10-05, awaiting QA:** Blizzard's empty-slot frame
     (EmptyDynamicButtonImageTemplate, 80 alpha) under Q W E R at the buttons' frame-art size
     (`command_panel` empties): a button covers its own; Abathur's missing E shows the empty
     frame, the row unchanged (user's pick). No Z or D just isn't there (the row's ends).
   - Not in FORMS: D.Va and the Vikings (already in ALSO); Tychus's Odin (no morph or unit
     card of its own found - likely the same unit); Abathur's clone (likely a copy of the
     cloned hero's unit, so it would match that hero's player - unchecked); Samuro's images
     and Jaina's elemental (summons: the short card).
4. **Anchoring pass - BUILT 2026-10-06; the non-16:9 test is in the final pass (14) - the user
   stays at 1080p until then.** Until then everything we
   placed was anchored to the screen's top-left with 1080p offsets, so a window that isn't
   16:9 shifted Blizzard's centred pieces against ours (the hexagon left its backplate in a
   2558 x 1401 window, 2026-10-03). The game is always 1200 units tall; the width follows the
   window. Now, as Ahli and Spazzo do (and the user's previous UI: top-middle and
   bottom-middle), big pieces anchor to the screen and what sits on them to the piece
   (`gen.py ANCHORS`; the constants are offsets from each rect's anchor):
   - **top-centre**: our backplate (Blizzard's hexagon is centred); the team levels hang off
     the backplate, the advantage flames off the levels;
   - **bottom-centre**: the minimap and everything on the plates: the cells, XP and core
     bars, the row packer, the map alerts, the heroic tooltip rows' top, and the inspect card
     (in line with blue's row, user). They share the screen point (`gen.py PLATES_AT`), so
     they still move together. The first pass hung them off two bare row frames at the
     screen's root (`FCJH_BlueRow` / `FCJH_RedRow`). The frames sat right, but the cells
     inside Blizzard's observer panel came out twice their height and 40 px high. Anchor to
     the screen or a sibling, never to one of our frames in another branch (memory rule 22);
   - **left edge**: the info panes, [screen] padding in (user: they line up with the card at
     1080p); **right edge, middle**: the replay box and its tab; top right: the dev stamp.
   At 16:9 nothing moved (gen's `check_anchoring`, and every anchor in the XML resolved before
   and after: none off by a unit). Wider, the centred pieces stay together round the middle,
   the panes and replay box keep to their edges. Narrower than 16:9 isn't supported (the rows
   are sized to fill 16:9; they'd run off a 16:10 screen). To check in a non-16:9 window: the
   hexagon on its backplate, the rows round the minimap, the card on blue's row, plate clicks
   and heroic tooltips still working. The user expects to iterate on how it feels.
5. **Study Ahli's other panels** (user watched a broadcast on his UI, 2026-10-03) - not to
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
6. Tried and undone: hiding Blizzard's observer talent row plainly (71181f7, undone in
   d279ecc) - plate clicks stopped following heroes. The row stays held shown and spread.
7. Art pass, after the functionality: Ahli's Tracer ammo bar (20 segments) and round Pulse
   Bomb meter; his hero plates' intro animation (a smooth slide and fade). And the death
   timers' end (user, 2026-10-09): in a player's view, Blizzard's own death timer flashes as
   it comes to an end - find how (the player HUD's layout: its animation or StateGroup on the
   respawn countdown) and give our plates' death timers the same for the observer.
   And the plates' carried box (gen.py `carry_box`, user 2026-10-12): Blackheart's doubloons /
   the Spider Queen's gems in the fountain's slot one step up the slant, the count over the
   icon, hidden at 0, on CARRY_MAPS only. Working and its borders now continue the fountain's
   (`CARRY_SLIDE = 4`, confirmed on Zul'jin, 2026-10-12); parked for the art pass - the coin is
   a touch big for its window, and the strip could grow further up the slant.
8. **Map objectives and the minimap per map - BUILT 2026-10-06, a first pass; the user will
   fine-tune with test maps that cover every map.** All of it is `tools/maps.py`, written by gen
   into `FCJH_Maps.StormLayout` (it replaced the hand-written `FCJH_MapAlerts`; its docstring
   says how a map's UI works). **The user's direction (2026-10-05/06):** centre the objectives
   round the minimap, not on the right edge; a team's alert goes on that team's side (blue left
   of the map, red right), neutral ones stay centred; a team's alert sits at its core bar's spot
   (on the XP bar at the row's inner end, stepping up onto the core bar while that shows); "if
   all alerts fall to the sides of the minimap, and they grow/jump as to not be on top of each
   other, then we're set". **Later (2026-10-06, Cursed Hollow):** no neutral banner at the top
   middle (it sits too high, worse on tall maps) - neutral alerts go in RED's column, right of
   the map, as Towers of Doom's do; red shares the space. The minimap is exempt from the 20 px
   padding rule: a map's team counters may sit on its bottom edge. Every map alert sits
   `[map_alerts] lift` (10 px) higher than its bar, clear of the talent/health pop-ups off the
   plates (superseded by the standard below). **Every banner's art lands in the same place on every map** (Blizzard's banners are
   one art; landing alike is what reads as one, user): across, red's starts where red's row
   does and blue's ends where blue's does (`[hero_row] red_left` / `blue_right`, the plates'
   distance from the map); up, on the shared slots. A banner whose parts hang below its art
   gets edited, not raised (the tribute's countdown, below).
   **The banner standard (user, 2026-10-09)** - `maps.ALERT_ART`, one `Art` per Blizzard banner
   layout (not per map: the NotificationFrameTemplate is Towers', Alterac's and Hanamura's; the
   centre banners are the older maps' and Braxis's): every banner is placed by its BAR, one
   Blizzard bar art. Every bar's bottom sits in ONE place on every map, `[map_alerts]
   above_core` (10 px, user) over the core bar's top - never moving, core bar shown or not (the core
   bar is taller than any pop-up), and ignoring what hangs under the bar: the banners draw over
   the plates' pop-ups (user). Stacked banners are one step apart: the tallest art that can
   stack (one sharing a column, any map) plus `STACK_GAP` (`step`: Towers' 117 + 8 = 125 units;
   user, twice: Blizzard's 30-unit gap left too much dead space, and sizing for the tribute's
   143, alone in its column, spread Towers' pair further). The
   first banner to show keeps its slot (user). Growth runs outward from the plates' inner edge;
   a banner Blizzard lays out from its hexagon end gets re-laid from its inner end, as the red
   curse. Blue's banners are MIRRORED (user): Blizzard draws one banner for both sides, its
   hexagon at the right end - blue's inner end, over blue's core bar - so blue's take
   Blizzard's own NotificationFrameLeftTemplate anchors (`maps.MIRROR`): hexagon outward. The
   blue curse (centre banner, Blizzard's layout) needs the same - unseen yet. Each layout's bar is measured once off a 1080p screenshot (`bar_up`: its bar's bottom
   over the edge its frame is placed by - Towers 20, the tribute 24, Braxis 0); gen prints the
   unmeasured (Hanamura's ICON art). No per-map banner nudge exists.
   **How a map's UI works** (game files): each map's panel is a template built at runtime in
   GameUI's `MapMechanicPanel` - the newer maps' in their own layout file, created by the map's
   script; the older five's (Cursed Hollow, Blackheart's Bay, Haunted Mines, Garden, Dragon
   Shire) in core `MapMechanicPanelTemplate`, on every map, hidden at load and shown by the
   map's script. Scripts find parts by NAME: move and restyle (`file="<map's file>"`), never
   rename or drop. A map's layout file loads only on that map. Blizzard moves its own minimap
   per map that way too (a `MinimapPanel` override in the file: Braxis -35, Battlefield +75,
   Hanamura +80, Warhead 0 and the map 30 right in its panel; 35 elsewhere).
   **The three parts:**
   - **The minimap per map:** each map draws with its bottom on the padding line (1060 at
     1080p, level with the plates' bottom). How tall a map draws: the opaque part of its
     `CustomMiniMap` texture, read from the map archives in Battle.net's cache (the
     battlegrounds aren't in the game's storage; our `mpq.py` reads them), fitted 380 px wide
     (Towers of Doom, measured: ~380 x 252, y 810-1062; the model gives 260 tall). Tall maps
     rise (Haunted Mines 380 px tall, top at 680); wide ones sink (Braxis 224 px). Moved from
     load, no jitter (2026-10-09): a newer map by a placer inside its own panel
     (`maps.placer`); an older map by **Blizzard's map id** (`maps.id_placers`, below) once it has
     `own_place=True` - until then it shares `[minimap] bottom`. `[minimap.nudge]` in
     layout.toml, px per map, for fine-tuning; `[minimap.panel_nudge]` moves only the panel's
     parts (both px, + lowers). The ARAM maps (no panel) keep `[minimap] bottom`.
   - **Each map's panel on our minimap:** every part Blizzard placed from the screen's
     bottom-right corner (where its minimap was) is restated from our minimap's corner, at the
     same distance as it stood from Blizzard's minimap on that map (`maps.on_minimap`). So the
     timers, counters, health bars and neutral banners sit round our minimap as they sat round
     Blizzard's, follow it per map, and the right-edge strips (Alterac, Volskaya, Garden's
     terror bar) stop clipping minimap-placed parts (Volskaya's capture hex). Towers of Doom's
     strip stays put (all it holds that matters is ours; its town health is drawn from the top).
   - **Team alerts:** a generic stack per side (`maps.stack_states`): an alert's slot is how
     many alerts before it in its side's column are showing; the bottom slot is the XP bar, or
     the core bar while that shows; 147 units a slot. Towers of Doom (now through it: Raven no
     longer lands on the tunnels) and Hanamura's "attacking" pair (one frame per team, to
     everyone - `AttackingCoreFrame_Order` blue, `_Chaos` red; placed by its icon box, art
     412 units, unmeasured). Other maps' alerts are neutral (timers, "spawns in") or blue-left /
     red-right halves of one HUD - checked in the files; none is per team. An alert whose art
     hangs off its frame's top-right (`maps.Alert box=`) is placed by our own spot frame
     (`FCJH_<name>Spot`): the spot takes the stack slot, the frame becomes the art's box on it
     (children draw only inside their parent's box). `followers` ride along on the same spot.
   **To check in game, map by map** (with item 14's test maps): the map's bottom on the padding
   line (nudge it if not), and when it moves (at load, or when its panel first shows - Sky
   Temple's and Tomb's start hidden); the panel's timers and counters above the map, not over the
   plates or the alert stacks; Volskaya's capture hex showing; Warhead's map centred; Hanamura's
   "attacking" alert on the attacking team's side, its art clear of the map; Blackheart's Bay
   placed at all (its panel is shown by its own script - unchecked). Then ARAM keeps the default.
   **Done:** Towers of Doom (2026-10-06; DONE again 2026-10-09 on the banner standard: bars on
   the fixed place with and without the core bar, blue's mirrored, the stack's spacing - user:
   "not likely to adjust them again"); Cursed Hollow (2026-10-06, below; its minimap and counters
   seen right after the no-jitter change); Volskaya Foundry (2026-10-15, under item 4 above).
   **Towers of Doom, as approved (2026-10-06):** altar countdown and towers upgrading on red's
   side, tunnels on blue's (kept balanced, user). "Cannons are firing": the script shows RAVEN's
   alert for blue's capture and NECRO's for red's (only the Your/Enemy text is per viewer), to
   each team's players only - player views show them, hidden 5 s later by our timer. The
   town-capture pair (Allies / The Enemy captured <town>) is viewer-relative, players-only:
   parked; OUR town alerts stand in, in every view - "Blue / Red team captured a town", from the
   observer-only "BroadcastToD<blue>v<red>" events the script sends our plates'
   ObserverHeroOverviewPanel (blue's count up = blue took it; ~1 s late, with the new town's
   spawn). **No free-view cannon alert is possible:** nothing an observer's UI receives marks an
   altar capture. The towns' shot counts show at the minimap's bottom corners.
   **Cursed Hollow, as approved (2026-10-06):** minimap nudged 20 px down, its panel 25 px up
   (`panel_nudge`), so the tribute counters sit on the map's bottom corners. Tribute spawning /
   collect the tribute (neutral, one frame) in red's column. The curse (one `CurseFrame` for
   either team, timer parts anchored to the tribute frame's) goes on the cursed team's side:
   which team, from its text - `maps.cursed_side`, one state per language, matched on the
   LITERAL words (`Text="@Param/Value/..."` never matches). Red's is laid out from its left end
   (our `FCJH_CurseText` label, Blizzard's art had dead space there); blue's keeps Blizzard's
   layout from the right. **Red's curse seen and approved; blue's not seen yet** (no replay with
   it - item 14). The tribute's countdown hung under its hexagon onto the XP bar: it's now in
   the bar after the words, as Towers' "Altars activate in: 0:24" (`maps.tribute_count`) -
   our words per language ("Tribute Spawns In:", `TRIBUTE_SPAWNS_IN`, found by matching
   Blizzard's literal words), from the bar's left end like the red curse's, the count one space
   after them (`TRIBUTE_COUNT_SPACE` -1 units: the labels pad ~8 px, measured), Blizzard's count
   hidden; "Collect the Tribute" stays Blizzard's (no count then - the script hides it).
   The curse's countdown the same way (approved 2026-10-06): Blizzard's in the raven head
   hidden, ours after the words (`CURSE_COUNT`; red's flows right from our words, the hexagon
   after it; blue's sits where Blizzard ends the words, they end before it), with a colon
   where that language's Towers "Altars activate in:" has one (`CURSE_COLONS`, its own label;
   Chinese takes "："; blue's "Equipo azul maldito" is both Spanishes', left without). Blue's
   count, like blue's curse, not yet seen (item 14).
   **Map-specific tech - SOLVED 2026-10-09 (the breakthrough).** The older five's panels are
   Blizzard's core ones, on every map, hidden at load - no panel tells them apart, and the
   first one shows at the first objective (the old jitter). **Blizzard's map id does, from
   load:** a `DataRefFrame` reading the script variable `libCore_gv_mAPMapStringID` (Spazzo's
   way), tested with `<When type="Property" frame="..." StringValue="HauntedMines"/>`. Read on
   screen: `HauntedMines`, `BraxisHoldout`. In code:
   - `maps.MAP_IDS` - every map's id and where it's from (read in GAME, Blizzard's SCRIPT, or
     SPAZZO only - read a SPAZZO one with the diagnostic's "map id" row before relying on it).
     Odd ones: Garden `HauntedWoods`, Tomb `Crypts`, Sky Temple `ControlPoints`, Warhead
     `Warhead Junction` (a space).
   - `maps.id_placers` - the reader and each map's state group, at GameUI level: **always
     shown** (the same inside HM's hidden core panel never fired). DefaultState on the
     unconditioned state (memory rule 27).
   - `maps.on_map(key)` - the condition, for any other per-map state.
   - **Converting an older map is one line:** `own_place=True` on its entry; its
     `[minimap.nudge]` then applies (gen refuses one without). Converted: Haunted Mines.
   - Can't: a map-only layout file of our own (ours load everywhere); Galaxy scripts (not
     an interface component, and replays re-simulate them). Newer maps keep their panel
     placers (proven); the map id would work for them too.
   **Haunted Mines - two views (2026-10-09; the launch view and the glide seen working - user: "Glide worked great"):** at load only the
   surface (`launch_cut` -8: the surface's bottom 8 px above the drawn map's middle, the mines'
   top 35 below - measured), its bottom on the padding line (`[minimap.launch_nudge]`), the
   mines under the screen. When the mines first open (the script shows `SkullModeFrame`) the
   minimap glides up over 1 s (`maps.glide`, eased) to the whole map on the line
   (`[minimap.nudge]` 34), and stays: the glide raises `FCJH_Opened`, which stops later openings
   replaying it. The skull counts ride with the minimap; the "Needed" plaque is fixed to the
   screen for the whole-map view. **A relative Anchor controller counts from the frame's LAYOUT
   anchor, not from a state's SetAnchor** - the first glide stopped 125 px high (memory rule
   28); its keys now run launch-minus-shared to place-minus-shared. The same rule made the
   tribute's and the curse's intros fade-only (`maps.FADE_ONLY`): `cursed_side` moves their
   sides, and a paused slide would have held them on red's spot.
   **Braxis Holdout (in QA, 2026-10-09):** the zerg wave banner at the standard place (art
   measured, `HOLDOUT_BOX`); the panel above the map 4 lower (`[minimap.panel_nudge]`). The
   beacon dishes (Blizzard pinned them under its own minimap, off our screen) are re-anchored
   from the screen, not moved with their frame (moving `RadarDishModeFrame` hid them - a frame
   draws only inside its box): at 90% (Width/Height), beside Leoric's and Nova's plates
   (`maps.BEACON_*`, `FCJH_MAP_BEACON_*`; the arrows are in Blizzard's dish art - Top points
   up, Bottom down). The electric line between them (`HoldOutLink1-4`, its own frames) is
   stretched from dish to dish under them (its ends fade, ~17% each), along the map's bottom
   edge, and under the MINIMAP: Braxis's placer sets the whole `MapMechanicPanel` to
   renderPriority 511, under the minimap's default (`Map.fix`; only on Braxis, where the
   placer exists). Line approved by eye (user: "this is the way"); its last 2 px down and the
   rest of Braxis still to check: the minimap from 0:00, nothing else under the map.
   **Lessons for every map:** (1) a right-edge strip clips anything moved out of it: Unclipped,
   or move the strip. (2) Read the script for who each alert is sent to - one can look
   viewer-relative ("Your cannons") and be one frame per TEAM. (3) A player view (1-8) shows
   alerts sent to that player's team; the free observer view doesn't. (4) An alert's art can
   hang off a child, not its frame (Hanamura's icon box): move the child.
9. **Viewport padding** (user, 2026-10-05). One more size pass on our hero plates, to set
   the screen's base padding: the gap between the plates and the screen's edges becomes the
   margin for everything. Then the replay box (top-left), the inspect card and the info panes
   (left column), and the rest of what we place respect that same margin - one number in
   layout.toml that they're all laid out from, rather than each element's own offsets. Goes
   with the anchoring pass (item 4) and the card's last item (line it up with the left edge).
   **Inspect placement** (user, 2026-10-05): the card's BOTTOM-LEFT corner sits on the blue
   plates' TOP-LEFT corner, that padding above it - the card grows up from the plates, its
   left edge in line with theirs. Laid out from the plates' rect and the padding (not its own
   `[element.inspect]` x/y), so it follows any plate resize; this settles the card's
   "line it up with the left edge" item.
   **Built 2026-10-05, 20 px experiment, awaiting in-game QA:** `[screen] padding = 20`;
   `[hero_row] scale = "fit"` (gen.py fit_hero_scale: 1.5561, XP bars 21 px from the sides,
   bottom at 1060); panes and inspect at x 20; the replay's frame at 14, 14 so its glass art
   (6 px inside the frame, `art_inset`) lands on 20 - seen in game; its collapsed tab at 20,
   20; inspect's y from `above = "blue_xp"`; gen.py check_padding refuses anything closer
   (top bar, minimap and kill feed exempt). Kill feed: back to Blizzard's own, top-left
   (FCJH_KillFeed removed; user: moved right, Blizzard's rows grow rightward so multi-kills
   ran off the screen, and they can't be right-aligned); seen in game: no clash with the
   replay box, and it sits ~20 px from the side on its own. The user's verdict
   (2026-10-05): the plates stay this size, so maps may be no wider than Towers of Doom
   (fine in game, ~380 px drawn). Blizzard's 394 px square caps every map at about that
   anyway, inside the plates' 415 px gap. Open, map by map (with item 8): HEIGHT. The
   square is centred at y ~936 and hangs off the bottom, so a tall map may cross the bottom
   padding or the screen's edge.
10. **Hotkeys for the inspect card and a death recap - DROPPED (user, 2026-10-05).** Built
    and tried: Ctrl+I switched the card off and on (a ToggleControl the card's gate also
    watched, as Ahli's Ctrl+C) - the user didn't like it; Ctrl+D as a Shortcut on Blizzard's
    death recap toast (`ConsoleUIContainer/HeroDeathStunFrame/DeathRecapButton`) did nothing -
    the toast likely never shows for an observer. Both removed outright; the card follows the
    selection only. Found while testing: holding Ctrl in a player's view brings up Blizzard's
    talent picker (game hotkey QuickHeroTalentTreeSelection = Control) - left to the game, see
    §3 "Blizzard's talent picker".
11. **A non-hero inspect card - built 2026-10-05, awaiting QA.** For minions, mercenaries,
    bosses, buildings: a SHORT card (`inspect_card` SHIFT / H_SHORT: 249 units, 224 px, bottom
    still on the plates) - name, the team's name on the band, health, buffs, stats. No portrait
    (Blizzard's unit picture is 112 x 49, too small to blow up: user's call), fountain,
    abilities (command card parked), talents or resource bar (none of them have one, user).
    - **hero or not:** `hero_check` - the selected unit against the hero units (game data
      plus ALSO's forms), FCJH_IsHero, read by the gate (`card()`); `shape()` moves the card's
      top and the rows, both ways. The first try keyed it to the plates' matchers and some
      heroes got the short card at a match's start for a while (user, 2026-10-05). If a hero
      still shows blank (no portrait or talents) early on, the plates' matchers are slow too.
    - **edge widths:** each side as many units as make 2 px there (`line`); the right side was
      a flat 2 units, 1.8 px, rounded to 1 (user, 2026-10-05).
    - **edge:** every unit's edge is now the team sensor's (`unit_team`): blue, red, or
      `[element.inspect] neutral_colour` (a lighter purple, user) for neither team - it replaced
      the player packs' own edge. Seen 2026-10-05: camp mercenaries purple, a captured
      camp's red or blue as they march down the lane (user).

How the heroic tooltips work: `tools/gen.py`, the comment above `HEROIC_TIPS`.

**Open:**
- map objectives and the minimap per map: item 8 above, built - fine-tuning in game
- the visual pass: the chrome backplate look to the plates, XP/core bars (a mid-height bevel,
  like the player view's core bar; the default UI's core bars: `design/ref_default_core_hp.png`)
  and the info panes (zebra rows, Heroes palette)
- wireframes for the nameplates / XP / core HP: the canvas now draws the build as it is
  (2026-09-30); the art pass designs over those boards
- the OBS package (names, logos, scores, bans, bracket, game count)
- fight-mode hotkey (our panes hold Ctrl+1-4; the game's Ctrl+1-8 are also "observe player N")
- rewinding a replay upsets pop-ups and latches — final polish (the product is for live games)
- rows with fewer than five heroes (needs a 3v3 or 1v1 replay)

**Settled as impossible:** jumping to one Lost Viking from the plate (Blizzard's per-Viking
targets in its in-game bar are ping buttons with selection off).

**Phase 1 (2026-09-25), condensed** — each is now a rule in §3 or a feature above: the
0.9 px/unit calibration; the minimap as a fixed square the engine fits maps into; the
`ToggleControl` hide hotkey; resource bars bound inside `HeroStatus` and coloured from
Blizzard's own hero table; talent-lead tiers compared as one-digit labels; talent picks via
`TalentTierState="TierSelected"`, watched by full path from outside the icons; our own
`HeroTalentsPanel` instance for the talents pane (the engine fills it, tooltips and all);
validator animation elements don't run in observer cells, so the heal sensor reads Blizzard's
health percent label instead. The round-by-round notes are in git history (`a0180f9` and the
commits around it).

---
12. **Ahli's death animation on the nameplate** (user, 2026-10-05: "a nice touch", not to
    copy) - his plate does something when its hero dies. For the art pass (item 7): study
    what it does, then design our own.
13. **Camp timer displays: DROPPED** (user, 2026-10-06: no clear place for them on our
    screen). Blizzard's own stay as they are - seen 2026-10-05 as "1:08 / -ELITE- / Boss Camp
    / Player 4" in a stack at the screen's left, mid-height.
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
    - **forms** (item 3): Medivh's Raven, Deathwing in Dragonflight and as World Breaker,
      Alexstrasza's Dragonqueen, Ragnaros in Molten Core, Greymane's Worgen, Valeera
      stealthed - each gets the TALL card with its player's portrait, talents and name, and
      its own buttons. If one gets the short card or no player, look at which unit the plate
      shows meanwhile (`inspect_card.FORMS`);
    - **empty slots** (item 3): Abathur shows Blizzard's empty frame where E would be; on any
      hero, no faint outline peeking round Q W E R (else resize `command_panel`'s empties);
      Deathwing in flight with no Z or D reads fine;
    - **Abathur's clone** (Ultimate Evolution) and **Samuro's images**: which card and player
      they get;
    - **Deathwing's heroic after level 10 - ask other players (user, 2026-10-06).** His plate's
      heroic is Cataclysm, his kit heroic, counted by our own reader (`gen.py
      KIT_HEROIC_COOLDOWNS`). At 10 he picks an active talent, pressed on 1, which Blizzard's
      observer slot then follows. Ask casters and players which they want on the plate after
      10: Cataclysm, the level-10 ability, or both;
    - **the D.Va and Viking guesses** in `inspect_card.ALSO`;
    - **rows with fewer than five heroes** (a 3v3 or 1v1 replay);
    - **every map**: the map objectives, the minimap per map (item 8; the jitter is solved -
      map id, 2026-10-09), and each SPAZZO-only map id read on the diagnostic;
    - **Cursed Hollow, blue cursed** (item 8): the banner on blue's side, left of the map,
      ending at the map's edge, its text and timer inside the art - not yet seen (user,
      2026-10-06: red's looks great);
    - **resource tooltip names** (inspect card) - REVERTED to 2026-10-06's (user, 2026-10-09)
      after three tries. **The lookup is right; only the refresh is wrong (user, 2026-10-09,
      on the reverted card):** every hero's name is correct the first time the card opens
      (Morales, Zarya, Gazlowe included); swap to another hero with the card left open and the
      tooltip keeps the first hero's name (everything else on the card follows the swap). The
      "Rage" seen earlier was a swap from Hogger. Confirmed on a second map (user). So the fix
      is a refresh on swap, nothing else. Blizzard's default UI
      names them right (user checked: Scrap, Energy) - it rebuilds its card per target. Facts:
      the bars' tooltip comes from Blizzard's TooltipStates, set only when the regen line comes
      or goes; the names live on the unit ACTORS (VitalNames Energy). Tried and failed: (1) a
      per-unit StateGroup on UnitStatusFrame0 setting a label the format frames read - everyone
      Mana; (2) the format frames reading the game's TargetInfoFrame @UnitVitalName - right on
      the first card, stale on a swap; (3) (1) plus per-hero states on each bar re-applying the
      Tooltip on a swap - still not working (the A/B/C diagnostic lines were never read back).
      Next time: start from a diagnostic and read it before building anything;
    - **a live custom game with observers**: the game binds Ctrl+1-8 to "Observe Player 9-16"
      (gamehotkeys.txt) - check our panes' Ctrl+1-4 still win with observer slots filled. Also
      O / Ctrl+O lock the camera to the commentator's / a referee's (their tooltips still
      marked "???"; a lobby slot can be made Referee) - worth a try for casters;
    - **a non-16:9 window** (item 4), last: the user stays at 1080p until then. The game's
      resolution is in `Documents/Heroes of the Storm/Variables.txt` (`width`, `height`,
      `windowwidth`, `windowheight`, `displaymode`, `windowstate`; 1920 x 1080, displaymode 0 at
      2026-10-06; `windowstate=1` is maximised - on 2026-10-09 a maximised window on a bigger
      monitor ran the game at 2558 x 1401 unnoticed: check screenshots' size) -
      Claude puts it back to 1080p afterwards, with the game closed.
15. **The Lost Vikings' nameplate in player view - look at it later** (user, 2026-10-09). In a
    player's view TLV's nameplate seems to be a three-slice, one per Viking, each with its own
    click handler. Worth studying for ours: how Blizzard splits one plate into three clickable
    parts (find it in JamiePhan's layouts), and whether our plates could use it.

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
