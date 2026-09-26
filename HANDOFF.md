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
**https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK** — the stock UI annotated, the
proposed default view at 1920×1080, and a spec table giving each element's position and
how sure we are the game allows it. **Every build is checked against it.**

In one paragraph: the ten hero cells sit along the bottom (blue 1–5 left of the minimap,
red 6–0 right of it) with portrait, HP, mana and CC; the minimap and its objective widgets
at bottom-centre; team core HP above the cells; a two-line top bar of series score, team
name, logo and level either side of Blizzard's hexagon, with bans, bracket and game count
beneath; the kill feed top-right; replay controls top-left, collapsible; info panes
(talents, KDA/damage, healing, siege) at middle-left on hotkeys; talent pop-ups on the
cells, and a green-plus pop-up on any hero below 25% health (drawn under the talent
pop-up). **Fight mode is not a separate layout** — it is one hotkey that hides a list of
elements (so far: the info pane and the health markers). The top bar and minimap always stay.

**Branding is negative space**: names, logos, scores, bans, bracket and game count are
drawn by OBS over empty regions the interface leaves (§6).

**Phase 0 (foundation) is done**: the toolchain, `layout.toml`, generated layouts,
dev/release profiles, and an in-game wireframe overlay. The source holds no overlay
elements yet. Next is Phase 1 (§7).

---

## 2. The loop

```
python tools/pack.py --wait
```

One command: **generate → stage → validate → pack → deploy.**

1. **generate** — `tools/gen.py` rewrites the committed generated layouts from `layout.toml`
2. **stage** — `src/FCJH.StormInterface/` is copied to `build/<profile>/`. A dev build adds
   the build stamp and the wireframe overlay there, and only there
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
layout.toml                                  every placement number, in wireframe PIXELS
tools/gen.py                                 turns it into layouts
src/FCJH.StormInterface/                     the archive's file tree, one to one
  Base.StormData/UI/Layout/
    DescIndex.StormLayout                    GENERATED — every layout, constants first
    FCJH_Constants.StormLayout               GENERATED — layout.toml in layout units
    FCJH_*.StormLayout                       hand-written, one per concern (from Phase 2)
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
  an automated extract of Heroes game data, currently **2.55.17.97650**. The validator's
  source of truth. Refresh with `git -C references/JamiePhan pull --depth 1`.
- **`references/Galaxy-Observer-UI-HeroesFix/`** — Spazzo's fork of Ahli's (retired) builder.
  Its `tools/plugins/mpq/MPQEditor.exe` is an independent check of our archives
  (`MPQEditor.exe e <mpq> * <dest> /fp`).
- **`references/AhliObs.StormInterface/`, `references/Spazzo/`** — two mature observer
  interfaces, unpacked. Ahli's is MIT. Most techniques here came from reading them.

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

---

## 6. Design decisions worth not relitigating

**Relocate Blizzard's hero cells; don't rebuild them.** No bindable "icon for this player's
hero" exists; relocated cells bring portraits, HP, click handling and death state, and
survive new heroes. Spazzo's per-hero textures are why his files run to 13,000 lines.

**Inherit bindings; never reconstruct them.** Put new frames *inside* the frame that owns the
binding — the CC sensor lives inside each cell's `HeroStatus`, so it always matches the
portrait above it. The mana bar should follow the same pattern.

**Use Blizzard's CC plate, not a rebuilt one.** A hand-built label rendered nothing; the
engine's element is self-managing.

**Branding is negative space**, drawn by OBS. The interface can't see OBS, so there is no
in-game fallback for missing names or logos.

**Don't resize the portraits.** The 165-unit frame and its texture coordinates are chosen
together; anything matching the visible slot anchors to the cell.

**Fight mode = a hotkey that hides a list, not a layout.** The agreed default view already
is the old fight-mode cluster. Pooled team HP is dropped: layouts have no arithmetic, and
five segments would duplicate the hero row. If plates read too small, widen them.

---

## 7. What's next

**Phase 1 — the unknowns, before building anything they could change.** Probes live in
`src/dev/` (dev builds only). Results so far, all 2026-09-25 on Garden of Terror:

- ✅ **Calibration:** every wireframe box landed exactly where the canvas puts it — the
  0.9 px/unit conversion is confirmed on screen.
- ✅ **Minimap** (`FCJH_Minimap.StormLayout`, shipped): Blizzard's minimap is a fixed
  438-unit square and the engine fits each map inside it, centred — no map detection needed
  to size it. At bottom-centre, hanging 59 units off-screen, Garden sits inside its wireframe
  box. Still to check: a *tall* map. **Map objective widgets are not on the minimap** — they
  live in `MapMechanicPanel`, filled by each battleground's own mod; per-map work happens there.
- ✅ **Hide hotkey:** a `ToggleControl` with `<Shortcut val="Control+Shift+W"/>` whose
  OnShown/OnHidden animation fades a target — works (the dev overlay toggle). This is the
  fight-mode hide-list mechanism.
- ✅ **Resource bars:** a `UnitStatusEnergyBar` inside a cell's `HeroStatus` binds to that
  cell's hero — bars appeared only for resource heroes (none for Sonya, Illidan). Open:
  confirm it drains mid-game; colour — Blizzard colours per resource type with separate
  templates (`StandardEnergy`, `BrewEnergy`, `FuryEnergy`, …), so ours are all mana-blue.
- ❌ **Talent-lead flame, as is:** `PartyFramePanel` is hidden for observers (a probe marker
  inside it never rendered), so `TeamTalentAdvantageFrame` can't show. Next: can a StateGroup
  read a level label's text? If so, generate the tier comparison ourselves from
  `Team1/2LevelLabel` and play Blizzard's flame cutscene in our own frame. A team leads when
  it has reached a talent tier (4, 7, 10, 13, 16, 20) the other hasn't: blue leads iff, for
  some tier T, blue ≥ T and red < T — six `GreaterThan`/`LessThan` conditions per team.

**Round 2 results (build `19:18:07`):** StateGroups **read label text** (A→B at level 2) but
compare it **as text** (C never showed at 10: "10" < "9"). Resource bars **drain** — confirmed.
Chen's bar did **not** turn yellow (cause unknown). Icon gallery: #1 blue heart, #2 person +
plus, **#4 white plus — the user's pick**, #7 purple boxed plus; #3/#5/#6 don't exist.

**Round 3 (build `21:11:13`):** tier probe rebuilt in two stages — level text → one-digit
tier label (30 generated states per team), then compare tier digits, where text and number
order agree. Colour split into three checks (static BrewEnergy on blue bars / runtime
SetProperty FuryEnergy on red bars / a "CHEN" label via `Unit="HeroChen"`). Health icon is
now #4 (`Storm_UI_Play_RandomHero_Button_Icon_Active_Healer`) tinted green with `<Color>`.

**Round 3 results (build `21:11:13`):** ✅ **Talent-tier lead works** — tiers 0/0 → EVEN at
the start; blue 3 vs red 4 → tiers 0/1 → RED LEADS. ✅ Static `ColorStyle` renders (blue bars
yellow); ✅ runtime `SetProperty ColorStyle` works (red bars orange). ❌ A unit check owned by a
child frame (`frame="$parent" Unit="HeroChen"`) never matched. ❌ Health icon never showed.

**Round 4 (build `21:17:15`):** resource colour uses **Blizzard's own hero→colour table**,
`HeroResourceStates` in `targetinfopanelunitstatustemplate.stormlayout:257` (Yellow=BrewEnergy:
Auriel, Chen, Morales, Valeera; Orange=FuryEnergy: Sonya, Junkrat, Gazlowe; Pink=DivaEnergy:
D.Va, Zarya, Volskaya gunner; DeathwingEnergy: Deathwing; Normal=StandardEnergy: everyone
else), placed like Blizzard's — the StateGroup **on the unit-status frame itself**, no
`frame=` on the When, and a condition-less "Normal" state as the fallback. Health element now
has `VisibleToOwner/Ally/Enemy` (unit-status elements hide by viewer relation otherwise).

**Round 4 results (build `21:17:15`):** ✅ **Per-hero resource colour works** with Blizzard's
table on `HeroStatus` (Sonya orange, Auriel yellow, mana heroes blue). ✅ Tier lead still
correct. ❌ Health icon: nothing on Sonya at ~10% or on dead heroes, even with
`VisibleToOwner/Ally/Enemy`. **Round 5 (build `21:23:27`)** adds a control element per cell
using `TargetLifeFull` (yellow plus, lower down): yellow pluses at game start = the element
runs and the 25% check is at fault; none = validator elements don't run in observer cells.

**Round 5 result:** ❌ no yellow pluses even at full health — **validator anim elements do not
run in observer cells.** The critical-health icon is parked; leads: read a property off the
cell's `HealthBar` in a StateGroup (property name unknown — probe several), or piggyback a
Blizzard low-health effect that works for observers. Answered probes (level, mana, health)
were removed from `src/dev/`; they're in history at `a0180f9`.

**Talent pop-ups — research done, probe deployed (build `21:31:34`, `FCJH_Probe_Talent`):**
- The top-bar talent rows, `ObserverHeroOverviewPanel/TalentsOverview/TalentOverview/
  HeroTalentsPanelContainer/PlayerFrame0..9`, are **anchored to the hero cells in Blizzard's
  own layout** (`PlayerFrame0` → `Team1HeroOverview/HeroOverview1` … `PlayerFrame9` →
  `Team2HeroOverview/HeroOverview5`, `talentsoverviewpanel.stormlayout:1842+`). The
  player-to-cell mapping is Blizzard's, and the rows follow the cells when we move them.
- Trigger (Ahli, `_LeaderPanelNotifications.StormLayout`): each `UnitStatusTalentIcon`'s
  animation state `TalentTierState` becomes `TierSelected` when picked; a hidden flag frame
  latches it to fire once; the picture is a binding to the icon's own `IconImage` texture.
  Ahli also uses runtime `Action type="ApplyTemplate"` into rotating notification slots.
- The probe pops each picked talent's icon for 4 s below the stock top-bar cell.
- **Result: ✅ works for all ten heroes** (build `21:43:00`), including load-time level-1
  picks. Getting there: pop-ups *inside* talent icons never draw (clipped) → built outside
  and watching the icons from outside; **`<Handle>`s added to the icons resolved for only
  one player** → full paths from `$GameUI` work for all.

**Info pane (Talents) — solved, probe `FCJH_Probe_TalentPanel`:**
- Moving Blizzard's bottom talent table failed three ways: it's clipped to its parent
  (`Unclipped` needed), its rows hang off wide grid art (`TalentGridImage`), and its panel has
  a fixed `Height` 410 — **a fixed-size frame anchored on both sides is CENTRED between the
  anchors, not stretched**, and clips its children to that.
- Our own table of images bound to Blizzard's talent icons showed the data but **can't have
  tooltips** — those belong to Blizzard's `UnitStatusTalentIcon` frame type.
- ✅ **What works: our OWN instance of Blizzard's panel** — `FCJH_TalentPanel`, type
  `HeroTalentsPanel`, template `TalentsOverviewPanel/CleanTalentsPanelTemplate`, rows from
  `HeroTalentsPanelContainerTemplate`. **The engine fills it** (portraits, "?" tiers, picks,
  **tooltips**), and as our frame it has none of the bottom panel's problems. Blue stacked
  over red; red rows un-mirrored by giving their portrait + seven tier icons blue's anchors.
- The pane is widened 382 → **530 px** (`layout.toml`) to fit Blizzard's native rows.
  To do: backdrops for empty tier slots, a pane title, the Ctrl hotkey, the canvas update.
- Validator fix: Blizzard writes paths with backslashes too (`Foo\Bar`); both now resolve.

Superseded round 1–2 notes (kept for the record):

- `FCJH_Probe_Icons` — a numbered column of Blizzard heal-looking textures on the right
  (score-screen healing icons, the healer role icon, `HealingDisplay`, `Restore`, a boost
  plus) for the user to pick the critical-health icon from.

- `FCJH_Probe_Level` — markers A (`Text="1"`), B (`GreaterThan 1`), C (`GreaterThan 9`, shows
  at level 10 only if comparisons are numeric) watching blue's level label. Decides the flame.
- `FCJH_Probe_Mana` — resource bars under the stock top-bar heroes; Chen's should be
  brew-yellow via `When Unit="HeroChen"` → `SetProperty ColorStyle`. Also check they drain.
  If colour works, a generator maps every hero from game data (`CustomUnitStatusFrame` on
  each `CUnit`: `HeroUnitStatusFrameYellowEnergy` = brew, `...OrangeEnergy` = fury, …).
- `FCJH_Probe_Health` — **new feature idea (user, 2026-09-25): a green-plus pop-up on a
  hero's plate at critical health**, reusing the talent pop-up slot. A
  `UnitStatusValidatorAnimElement` inside each cell's `HeroStatus` with Blizzard's own
  `TargetLifeLT25Percent` validator (also 30/33/35/40/50% exist; no 20%) fires an event when
  true and `NoState` otherwise. Watch: does it also sit on dead heroes (0% life)?
  **Decided:** the talent pop-up draws *above* the health plus (talent choices matter more);
  both share the slot, the talent one on a higher render priority. **Fight mode hides the
  health markers** — they join the hide list with the info pane.
- **Talent pop-ups:** read how Ahli wires his first (no launch needed).
- **Info pane:** can Blizzard's 1035-wide talent table be re-laid out with teams stacked?

**Phase 2 — build the default view one element at a time**, each checked by screenshot
against the canvas: hero row → minimap → top bar → info pane → kill feed → replay tab →
pop-ups → fight hotkey.

**Carried over from build 50, to solve again in Phase 2:** its health bars were cut into short
slanted segments — prime suspect `HeroStatus`'s `ImageMaskFrame` (`AlphaMaskTexture
@UI/obs_bar_player_blue`, drawn for a 134 px bar, `stormobserverpanel.stormlayout:270`); and
its CC text sat half behind the bar row.

---

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
