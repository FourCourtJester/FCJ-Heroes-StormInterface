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
beneath; the kill feed top-right; replay controls top-left, collapsible; info panes
(talents, KDA/damage, healing, siege) at middle-left on hotkeys; talent pop-ups on the
cells, and a green-plus pop-up on any hero below 25% health (drawn under the talent
pop-up). **Fight mode is not a separate layout** — it is one hotkey that hides a list of
elements (so far: the info pane and the health markers). The top bar and minimap always stay.

**Branding is negative space**: names, logos, scores, bans, bracket and game count are
drawn by OBS over empty regions the interface leaves (§6).

**Status, 2026-09-30: Phase 2 (building the default view) is well along.** Phases 0
(toolchain) and 1 (probing the unknowns) are done. Built, and confirmed in game unless noted:

- **Hero row** — Blizzard's *in-game* top-bar cells, slanted and interlocking, scaled
  (`[hero_row] scale`, 1.5125 since 2026-09-30 — that size not yet seen in game): portrait,
  health, resource bar in Blizzard's per-hero colours, CC text and icon, death timers
  (per-Viking ones in each third), Viking bars in thirds, Rexxar's bar full height (Misha's
  hidden), fountain-ready marker, Abathur clone marker, and Blizzard's in-game heroic panel
  (icon, frame, ready glow, cooldown count and dim; Tracer's Pulse Bomb charge instead of a
  cooldown), with the heroic's **tooltip** on hover (2026-10-02; Tracer's has no name line yet).
  Clicking a plate selects the hero and locks the camera, as in the default UI.
- **Team XP** along each row's top edge and **core HP** above it, cut to the slant; hidden
  until a team's first hero loads; rows pack toward the minimap with fewer than five heroes
  (untested).
- **Top bar** — Blizzard's hexagon and clock on our generated chrome backplate (`[top_backplate]`),
  team levels, Blizzard's talent-advantage flame when a team is a tier ahead.
- **Pop-ups** on the plates — the talent just picked, and a green plus when a hero drops to
  25% (once per dip, gone after ~4 s or at death or above 30%).
- **Info panes** — talents, KDA/damage, healing, structures/XP: one at a time on
  `Ctrl+Shift+1-4`, each with an X; the leader in each column softly highlighted.
- **Inspect card** — the selected unit's portrait, name/player/level, fountain, bars, buffs,
  abilities, talents and stats; shows exactly when the default UI's small inspector would
  (which is never while a replay is paused). The abilities are Blizzard's own command card
  laid over the card (talent actives on top; mount, abilities, trait below), so their
  tooltips, cooldowns and per-hero contents are the game's (2026-10-02, not yet seen in game).
- **Kill feed** top-right, **minimap** bottom-centre, **replay controls** top-left with a tab
  when collapsed (replays only). Blizzard's player HUD and talent picker never show.

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

1. **Inspect card: DONE bar a last look (2026-10-05, evening QA rounds; 3d11ae9, 7332a10,
   97fdd7a and the 90% build after).** Seen and approved in game: hero name centred in the
   title band, player name and level (16, set 2 low in their band), team-coloured edge,
   Blizzard's inspector art as the background (now permanent, at 90% so the game shows
   through; its border under the contents - over them it muted the bars), one padding (`PAD`
   10) everywhere measured inside the edge, the card cut to fit (583 units, 525 px; gen
   refuses a layout.toml size that disagrees), the fountain as the first buff with its
   countdown (the sensor's `CooldownLabel`, as Blizzard's console does) and Blizzard's
   tooltip while it cools down, abilities spread across the card with the talent actives
   nested over the gaps (Q/W first; rows 0.87 of the button spacing apart, a honeycomb -
   "looks HOT"), talents spread across with visible empty-tier boxes (outlines pixel-exact:
   `inspect_card.line`), stats in three related rows.
   **Still to see:** the thin screen-wide lines and stray health/resource/stat tooltips -
   Blizzard's own inspect box, held on screen by its drag constraint however it was parked
   (in screenshots since 10-02). Its contents, and the unused pieces of our card's copy, are
   now hidden every frame (`FCJH_Hidden`); check the lines are gone, with the card open and
   shut. Also: the fountain art is a bit stretched (Blizzard's; left as is); line the card up
   with the screen's left edge (the user's last item for it).

   **All panels** (the info panes and the card, user 2026-10-05):
   - the flat black needs punching up: look at the default UI's panel backgrounds and title
     bars and re-use Blizzard's assets;
   - the number panels (damage and the other stats) need a colour pass for both teams,
     combined with that background work, for readability.
2. **Command card polish** - does each button read cleanly; **talent-granted abilities** (the
   top row, dynamic buttons 30-35): seen 2026-10-05 on Sonya (screenshot `Screenshot2026-10-05
   11_16_54.jpg`), they sit in place but draw oversized art behind them - an orange flame frame
   round the first (a cooldown count, 17) and a large faded portrait behind the second. The
   same kind of leftover 120-unit art the main buttons had before each piece was resized (§3,
   "The inspect card's abilities"): find which parts of a dynamic button draw it (its overlay
   panel, a talent-active glow or backing) and size them to the button; they should then sit
   in the top row like the other buttons (item 1). The mount button
   (Blizzard's bookend art; Ahli widens it to 82);
   whether the empty top row should collapse. Keys Blizzard draws, left to right: Z, Q, W, E,
   R, D (seen 2026-10-03).
3. **Card swaps** - heroes whose command card changes mid-game. Abathur's Symbiote swaps the
   card to Symbiote's buttons, some in slots we park, so it shows gaps (seen 2026-10-05). The
   user expects others do the same; candidates to check: D.Va (mech / pilot), the Lost
   Vikings, Ragnaros (Molten Core), Medivh (Raven Form), Greymane (Worgen), Tychus (Odin),
   Abathur's Ultimate Evolution clone, vehicles (Dragon Knight, Garden Terror, Triglav). Find
   which slots each uses, then decide what we park.
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

How the heroic tooltips work: `tools/gen.py`, the comment above `HEROIC_TIPS`.

**Open:**
- map objectives: item 8 above
- the visual pass: the chrome backplate look to the plates, XP/core bars (a mid-height bevel,
  like the player view's core bar; the default UI's core bars: `design/ref_default_core_hp.png`)
  and the info panes (zebra rows, Heroes palette); fountain markers re-angled to the plate
- wireframes for the nameplates / XP / core HP: the canvas now draws the build as it is
  (2026-09-30); the art pass designs over those boards
- the OBS package (names, logos, scores, bans, bracket, game count)
- fight-mode hotkey; our own hotkeys (Blizzard's 1-8 and Ctrl+1/2 are "observe player N")
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

## 8. Original brief

`~/Downloads/hots-observer-interface-brief.md`, outside the repo. The operating model is a
**solo observer/commentator** who also talks: anything mid-fight is one keypress, and the
default view must look right untouched. Since tested: the top bar *can* be displaced, and
per-hero CC for non-selected heroes *is* readable.
