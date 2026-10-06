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
  fountain-ready marker, Abathur clone marker, and Blizzard's in-game heroic panel (icon,
  frame, ready glow, cooldown count and dim; Tracer's Pulse Bomb charge instead of a
  cooldown), with the heroic's **tooltip** on hover. Clicking a plate selects the hero and
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
- **Kill feed** — Blizzard's own, top-left. **Minimap** bottom-centre, **replay controls**
  top-left with a tab when collapsed (replays only). Blizzard's player HUD never shows; its
  talent picker is left to the game: held Ctrl shows it, steady, only in a player's view
  (1-8 keys), not when following from a plate click - as in Ahli's and Spazzo's UIs (§3;
  confirmed 2026-10-06).

Not yet: map objectives (pinned to the right edge on many maps — a per-map pass), the OBS
graphics package, the fight-mode hotkey, and the visual pass that takes the chrome look of
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
src/FCJH.StormInterface/                     the archive's file tree, one to one
  Base.StormData/UI/Layout/
    DescIndex.StormLayout                    GENERATED — every layout, constants first
    FCJH_Constants.StormLayout               GENERATED — layout.toml in layout units
    FCJH_HeroRow.StormLayout                 GENERATED — cells, heroic panels, pop-ups, row packer
    FCJH_StatPanes.StormLayout               GENERATED — the three stat info panes
    FCJH_Inspect.StormLayout                 GENERATED — the inspect card
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

---

## 7. What's next

**Next** (end of the 2026-10-05 session; start here):

Waiting on a look in game: the short inspect card without its resource slot. (Blizzard's
talent picker, left to the game: seen 2026-10-06 never coming up on its own in a player's
view, only on held Ctrl.) Done this session: panes in Blizzard's talent
grid and the inspect skin, hotkeys settled (our panes on Ctrl+1-4; the inspect and death
recap keys tried and dropped), the short card for non-heroes (camp mercenaries purple,
captured ones their team's), hero forms and empty ability slots (item 3). Open items, the
user's pick of order: map objectives and the minimap per map (8), camp timers (13),
anchoring (4), the art pass (7, 12). Item 14 collects what waits on replays with particular
heroes and maps.

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
4. **Anchoring pass**: everything we place is anchored to the screen's LEFT edge with fixed
   offsets (layout.toml is 1080p px), so a window that isn't 16:9 shifts Blizzard's centred
   pieces against ours - the hexagon left its backplate in a 2558 x 1401 window (2026-10-03;
   any 16:9 size is fine: the UI scales with height, 1200 units tall). Anchor each element to
   its nearest edge or the centre (Min / Mid / Max), as Blizzard does.
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
   Bomb meter; his hero plates' intro animation (a smooth slide and fade).
8. **Map objectives - not looked at yet** (user, 2026-10-05). Each map's objective widgets
   (tribute and curse timers, shrine and altar counts, punisher / immortal / golem health,
   payloads, the "spawns in" banners, the core shields) are Blizzard's `MapMechanicPanel`
   (base UI `mapmechanicpanel.stormlayout`) and `ObjectivePanel` (`objectivepanel.stormlayout`),
   with per-map layouts on top. Many are pinned to the screen's right edge, where Blizzard's
   minimap sat; ours is bottom-centre, so they may sit wrong or collide with the kill feed or
   red plates. A per-map pass: load a replay of each map, screenshot each objective's states,
   and decide where each one lives in our layout (and what Ahli does with them). Seen so far:
   only "ALTAR SPAWNS IN 0:27" on Towers of Doom (2026-10-05), right side, mid-height.
   **The user's direction (2026-10-05):**
   - **centre them around the minimap** (bottom-centre), not on the right edge;
   - **even better: a team's objective action spawns on that team's side.** E.g. "cannons
     are firing" (Blackheart's Bay / Towers of Doom style) shows on the side of the team
     firing them - blue's alert left of the minimap, red's right. Neutral alerts (spawn
     timers, "altar spawns in") stay centred.
   - **where a team's alert sits:** at its core health bar's spot - on top of that team's XP
     bar, at the row's inner end by the minimap (`[team_core]` in layout.toml). The core bar
     only shows while the core takes damage, so: core bar hidden -> the alert takes its spot;
     core bar showing -> the alert stacks just above it. One StateGroup per team on the core
     frame's Visible, SetAnchor-ing the alert's Bottom to the core's Top or the XP bar's Top
     (the same `gap`).
   To find out: whether Blizzard's widgets know which team an event belongs to (a team or
   player property, separate blue/red frames, or per-team state groups in the per-map
   layouts) - if they do, anchor each team's frames to its side; if not, look for a sensor
   (the team's score, a team-owned unit or behaviour) to switch the anchor on.
   **Minimap per map** (2026-10-05, saved for this pass): the engine CENTRES each map in the
   minimap square (Towers of Doom draws y ~810-1062, centred on 936), so a map taller than
   ~248 px crosses the bottom padding. A position per map looks doable: each map's mod ships
   its own layouts, loaded only on that map (file="GameUI" frames: Alterac Pass, Battlefield
   of Eternity, Braxis Holdout, Hanamura, Towers of Doom, Warhead Junction; templates of their
   own: Garden, Shrines, Sky Temple, Tomb, Volskaya). An interface can add to a map's file
   (Ahli 0.75 does: `file="Hanamura"` payload bars). So: a tiny frame inside each map's
   layout that, on load, `SetAnchor`s MinimapPanel (`<Action type="SetAnchor" frame=...
   side= relative= pos= offset=/>`); one number per map in layout.toml. Blackheart's Bay,
   Cursed Hollow, Dragon Shire and Haunted Mines ship no UI - they share the default. Test
   first: move it on Braxis only, check Cursed Hollow stays put (proves the file add is
   harmless elsewhere and that a map frame can move the minimap).
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
- map objectives: item 8 above
- the visual pass: the chrome backplate look to the plates, XP/core bars (a mid-height bevel,
  like the player view's core bar; the default UI's core bars: `design/ref_default_core_hp.png`)
  and the info panes (zebra rows, Heroes palette); fountain markers re-angled to the plate
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
13. **Camp timer displays** (user, 2026-10-05, for later) - the mercenary camps' respawn
    timers. Blizzard's own were seen in a 2026-10-05 screenshot (22:12:18): "1:08 / -ELITE- /
    Boss Camp / Player 4" in a stack at the screen's left, mid-height (camp labels in the
    world, or pinned to the screen's edge when the camp is off screen?). To look at: what
    Blizzard shows and where, what Ahli does with them, and whether ours should look and sit
    differently. Goes with the map objectives pass (item 8).
14. **Final pass: every map, every hero** (user, 2026-10-05). The last QA round, with replays
    that cover every map and every hero; the checks that need a particular hero or map collect
    here until then (no replay with them yet):
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
    - **the D.Va and Viking guesses** in `inspect_card.ALSO`;
    - **rows with fewer than five heroes** (a 3v3 or 1v1 replay);
    - **every map**: the map objectives, the minimap per map, camp timers (items 8, 13).

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
