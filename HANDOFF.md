# FCJH — Handoff

Custom `.StormInterface` observer overlay for Heroes of the Storm, for esports/broadcast use.
Written for whoever picks this up next, human or model.

---

## 1. Where things stand

**Build 50** is the current source, **screen-verified on 2026-09-25** — packed by our own
Python toolchain, not the Java builder. See §7 for what it fixed and what it didn't.

**The build toolchain is now ours** (§2). The Java builder turned out to be a byte-for-byte
copy of the source folder into an MPQ archive; `tools/pack.py` does the same in Python, and
Heroes loads the result. The Java wrapper was removed after commit `dde9af7`, which still
holds it. The one thing it did that we don't — frame-path validation — is §7's top item.

The interface currently:

- Strips the stock observer console — hero portrait panel, ability bar, unit-select box,
  talent-select UI, stock top bar art
- Relocates Blizzard's **ten hero cells** into a custom cluster at bottom-centre, one row,
  with portraits, click handling, health bars and death status intact
- Draws a black backing behind the cluster, and a black top bar carving five branding
  regions (team names, series scores, tournament logo) as empty space for OBS
- Shows a **CC marker** on each hero's portrait and CC text on their health bar
- Moves replay controls to the bottom-left corner

### Test ladder (from the original brief)

| | Test | Result |
|---|---|---|
| T0 | One visible change reaches the screen | **PASS** |
| T1 | Hide a Blizzard frame | **PASS** — by parking, not `Visible` |
| T2 | Bind HP for a non-selected hero | **PASS** — inherited via relocated cells |
| T3 | Sum two heroes' HP | **Ruled out** — layouts have no arithmetic |
| T3b | CC state for a non-selected hero | **PASS** |
| T4 | Reparent per-hero panels | **PASS** |

T3's failure means the "pooled team HP bar" is off the table; the brief's five-adjacent-
segments fallback is the design.

---

## 2. The loop

```
python tools/pack.py --wait
```

Packs `src/FCJH.StormInterface/` into an uncompressed **MPQ v1** archive and deploys it as
`Documents/Heroes of the Storm/Interfaces/FCJH.StormInterface`. Takes milliseconds. Flags:
`--no-deploy`, `--name <file>` to deploy under another filename, `--wait` (below).

**The loop, with the client left open** (all confirmed 2026-09-25):

1. Launch Heroes **from the Battle.net app**. Launching by double-clicking a replay goes
   through `HeroesSwitcher`, which has no Battle.net auth token — that is the password prompt
   that never remembers.
2. Open a **current-patch** replay from the in-game Replays tab (§5 for why current-patch).
3. Edit, then `python tools/pack.py --wait`.
4. Leave the replay. **The file is locked while a replay is open** and writable at the main
   menu; `--wait` retries until the lock releases, so the build lands the moment you exit.
5. Reopen the replay. **The game re-reads the interface on every replay load** — no client
   restart.

What `pack.py` checks before writing: every XML file parses (an unbalanced file makes the
game **silently ignore the entire interface** — stock UI, no build stamp, no error), and the
archive reads back identical to the source. What it does **not** check yet: frame paths.

Other tools:

- `python tools/mpq.py list|extract <archive> [dest]` — inspect any `.StormInterface` or
  `.SC2Map`, including Ahli's and Spazzo's (it reads their MPQ v4 archives too).
- `python tools/make_test_ui.py` — smoke test. Deploys a tiny Python-authored interface
  (a magenta box) as `FCJHTest.StormInterface`. If a patch ever breaks loading, this
  separates "the packer broke" from "the layout broke".

**Legacy:** the old PowerShell wrapper around Ahli's Java builder, `tools/build-and-run.ps1`,
is in history at `dde9af7` if its post-patch retry or XML gate ever needs consulting.

---

## 3. Layout, and how to work on it

Everything lives in one file:

```
src/FCJH.StormInterface/Base.StormData/UI/Layout/_FCJH.StormLayout
```

The folder is the archive's file tree, one to one: `pack.py` stores every file under
`src/FCJH.StormInterface/` at the same path inside the archive. `DescIndex.StormLayout` lists
the layouts to load; `DocumentHeader` is binary editor metadata, copied as-is.

(`src/` was `builds/` until 2026-09-25 — the old name was forced by the Java builder's
project database. `builds/FCJH.SC2Map` is a blank StarCraft II map from July, likely left by
the builder's `--compileRun` launching SC2; not part of the interface.)

The file's header comment carries eight rules, all learned the hard way and all confirmed in
game. Read them before editing. The three that caused the most damage:

- **Parking a frame drags anything anchored TO it.** `HeroPortraitImage` anchors to
  `IconFrame`; parking `IconFrame` sent all ten portraits off-screen and cost three builds
  of "the icons don't render". When something you want depends on a frame's geometry, hide
  it with `<Alpha val="0"/>` instead of moving it.
- **Render order follows the frame TREE; `RenderPriority` only sorts siblings.** Frames this
  interface adds to `GameUI` paint above *everything* in `UIContainer`, whatever priority is
  set. To put something behind a Blizzard frame, inject it *beside* that frame inside their
  hierarchy — that is how the cluster backing works.
- **The base UI binds no player to the hero cells.** No `PlayerId`, no slot, no index — the
  engine fills them by ordinal position, so the hero-to-cell mapping does not exist in XML
  and cannot be reconstructed. Four builds were lost tuning offsets against this. See §6.

### Practices that worked

- **Keep the build stamp.** `BUILD_STAMP` renders top-left. If the number on screen is stale,
  the game loaded a cached interface and nothing else you're looking at is evidence.
- **Displace, don't guess.** When two builds fail to explain a symptom, move each suspect
  frame somewhere obvious and see which one carries the content. Frame names are duplicated
  all over this codebase — a name match is not proof.
- **Colour a frame garishly before concluding it doesn't render.** The top bar "wasn't
  rendering" for several builds; it was black on a dark scene the whole time.
- **Never edit this file by line-number surgery.** It orphaned two `</Frame>` tags and broke
  the interface silently. Use string-anchored edits.
- **One change per build where possible.** Four stacked unverified builds produced a mess
  nobody could attribute.

---

## 4. Reference material

- **`references/JamiePhan/`** — shallow clone of
  [jamiephan/HeroesOfTheStorm_Gamedata](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata),
  an automated extract of Heroes game data. Currently game version **2.55.17.97650**. This is
  the source of truth for frame names and paths. Refresh with
  `git -C references/JamiePhan pull --depth 1`.
- **`references/Galaxy-Observer-UI-HeroesFix/`** — Spazzo's fork of Ahli's builder. Contains
  the legacy builder jar (`dev/compile-spring-boot.jar`), an older local base-UI extraction,
  and Ladik's `tools/plugins/mpq/MPQEditor.exe` — which is all the Java builder uses to write
  archives. Handy as an independent check of our packer's output (`MPQEditor.exe e <mpq> *
  <dest> /fp`).
- **`references/AhliObs.StormInterface/`, `references/Spazzo/`** — two mature observer
  interfaces, unpacked. Ahli's is MIT. Invaluable for "how does anyone do X" — most
  techniques here were found by reading these.

`references/` is gitignored.

Key base-UI files, all under
`references/JamiePhan/mods/core.stormmod/base.stormdata/ui/layout/ui/`:

| File | What's in it |
|---|---|
| `gameui.stormlayout` | The root frame tree and most handles |
| `stormobserverpanel.stormlayout` | Observer top bar, hero cells, team containers |
| `unitstatus.stormlayout` | World nameplates, CC validators, buff/debuff element |
| `heroconsole.stormlayout` | Bottom-left portrait/stats cluster |
| `talentsoverviewpanel.stormlayout` | Talent tier grid |

---

## 5. Environment gotchas

**Interface selection lives in TWO files**, and both matter:

```
Documents/Heroes of the Storm/Variables.txt
Documents/Heroes of the Storm/Accounts/<id>/Variables.txt
```

Keys are `observerinterface=` and `replayinterface=`, each taking the full filename
including the `.StormInterface` extension. Only edit them while Heroes is closed — the game
rewrites both on exit. Observed 2026-09-25: on exit it **blanked the top-level keys** and
kept the account file's, so the account file is the one that persists. Setting both is
still the safe routine.

**Out-of-patch replays wipe the selection.** Watching a replay from an older patch forces a
client version switch, and that switch clears these keys. Symptom: next launch shows stock
UI. This happened five times (it had happened again by 2026-09-25). Keep a current-patch
replay to hand: a custom lobby of AI vs AI with you observing produces one, and exercises
the live observer path too.

**File lock.** Heroes locks the *selected* interface file while a replay (and presumably a
match) is open; at the main menu, or with Heroes closed, it can be overwritten. Presumably
only the selected file is locked — an unselected one was overwritten with Heroes running,
though not confirmed mid-replay.

**Resolution is locked to 1920×1080** via `width`/`height`/`windowwidth`/`windowheight` in
the top-level `Variables.txt`. The layout's pixel constants assume it. Backup at
`Variables.txt.res-bak`.

**Screenshots** land in `Documents/Heroes of the Storm/Screenshots/` and can be read
directly. Ask for one rather than a verbal description — it catches things neither party
thought to look for.

---

## 6. Design decisions worth not relitigating

**Relocate Blizzard's hero cells; don't rebuild them.** There is no bindable "icon for
whichever hero this player picked". Spazzo's kit hardcodes a texture per hero and switches
with state groups, which is why his files run to 13,000 lines. Relocating Blizzard's cells
gets portraits, health bars, click handling and death status already wired, and they survive
new hero releases. The cost is less styling freedom.

**Inherit bindings; never reconstruct them.** The CC sensor lives *inside* each cell's
`HeroStatus`, so it shares whatever unit the engine gave that cell and always matches the
portrait above it. An earlier version addressed heroes by `PlayerId` in a parallel layer;
that is a different axis from slot ordinal, the two agree in a normal 5v5 and diverge in a
scrambled custom lobby, and no offset reconciles them.

**Use Blizzard's CC plate, not a rebuilt one.** A hand-built animated label rendered nothing
at all. The engine's element is already styled and self-managing. Its label and backing are
hidden with `Alpha` and only the icon is shown, centred on the portrait, with the state text
on the health bar. Trade-off: the engine owns its visibility, so no custom animation.

**Branding is negative space.** Team names, series scores and tournament logos are never
rendered by the interface — it carves the regions and leaves them empty for OBS to composite
underneath. Otherwise every team swap means rebuilding and reselecting an interface file
mid-broadcast. The captions currently in those regions are placement guides and come out
before air.

**Don't resize the portraits.** Blizzard's 165-unit frame and its texture coordinates are
chosen together to crop the face. Forcing the width to match the slot mangles the art
(tried in build 49, reverted in 50). Anything that must match the visible slot anchors to
the **cell**, not the portrait.

---

## 7. Outstanding

**Verified in build 50** (2026-09-25, screenshots):

- ✅ Outer heroes no longer clipped — all ten portraits fully visible
- ✅ Objective hexagon appears between the teams, timer beneath it (`Unclipped` was the fix)
- ✅ A dead hero reads as an empty rail; portrait greys with the respawn timer
- ✅ CC marker icon shows on the portrait
- ❌ **Health bars are not sized or aligned to their slots.** On each team the outermost fill
  is long (~115px) and the inner four show only ~40px, even at full HP pre-game; the dark
  rails merge into one continuous strip, so slot edges are invisible. Bars do track HP. Two
  builds have now missed on this, so the next step is diagnostic, not a fix: paint
  alternating garish rail colours per slot and see where each cell really sits. Working
  theory (unconfirmed): Blizzard's inner bar keeps its fixed 134 width regardless of our
  anchors, overflows into neighbours, and their opaque rails paint over the overflow.
- ⚠️ The CC state text (e.g. `UNSTOPPABLE`) is half hidden — its top half sits behind the
  bar row.

**Toolchain, to finish dropping Java:**

- **Frame-path validator** against the JamiePhan extract. The Java builder resolved every
  frame reference offline; we currently only check that the XML parses. Start with the easy
  checks (constants defined, templates exist, top-level paths exist in the base UI), then
  `$parent`/`$this`/`$handle` resolution and template merging.
- **Watcher**: rebuild on save with `--wait`. The lock behaviour makes this straightforward.
- **Generation**, starting with the hand-computed slot constants (`L1_L`…`R5_R`).

**Known remaining on screen:** talent tier `?` markers at the top. They're tied to
`ObserverTopPanel`, which is **load-bearing for the hero portraits** — parking that panel
kills the icons, so it needs surgical treatment rather than removal.

**Not started:**

- Fight mode as a *mode*. The toggle machinery was built and then removed when the cluster
  became default-on. The pattern that works:
  `ToggleControl + Shortcut → StateGroup → SendEvent → Animation`. Mutual exclusion is
  structural — a StateGroup has one active state — which is what the brief's §8.1 wants.
  Note fight mode should **move** the existing cells rather than draw a second cluster;
  there is only one set and a frame has one position.
- Art pass. Masking is well supported (`AlphaMaskTexture` / `ImageMaskTexture`, ~93 uses in
  the base UI), so parallelogram and hex cuts are achievable, and Blizzard's own angled
  masks can be referenced for free. Mask a bar as three pieces — angled cap, stretchable
  middle, angled cap — or an angled edge shears when the frame stretches.
- Radial pulse on the CC marker. A `Dimension` controller on a loop, roughly eight lines.
- Stat pane (brief §8.3), lowest priority.

---

## 8. Original brief

The session brief lives outside the repo at `~/Downloads/hots-observer-interface-brief.md`.
Worth reading for intent — the operating model is a **solo observer/commentator** who also
talks, so anything used mid-fight must be one keypress, and the default view must look right
untouched.

Two of its assumptions have since been tested and corrected: the top bar *can* be displaced
(the "it can't be hidden" recollection was overstated), and per-hero CC for non-selected
heroes *is* readable, which the brief flagged as the pivotal unknown.
