# The generator: what it is, how to use it, what it makes

Written 2026-10-16 so the toolchain can be pulled out into its own repo later without
re-deriving it (user). How to split it out is in [extraction-plan.md](extraction-plan.md);
this file is the user's guide.

## What it is

A **Python toolchain that builds a Heroes of the Storm `.StormInterface` from a spec in screen
pixels.** It replaced Ahli's Java/Spring builder (Galaxy-Observer-UI) on 2026-09-25. Python 3.11+
(it needs `tomllib`; 3.13 in use), standard library only, no install step.

It does five things, in one command:

1. **generates** the arithmetic or repetitive layouts (and textures) from `layout.toml`;
2. **stages** the interface's file tree into `build/<profile>/`;
3. **validates** every layout against Blizzard's own UI tree, so mistakes the game would
   silently ignore stop the build instead;
4. **packs** it into the MPQ archive the game reads, then reads that archive back and compares
   it file by file;
5. **deploys** it into the game's `Interfaces` folder, waiting out the game's lock if a replay
   is open.

The design idea underneath: **numbers live in one config, in pixels, and everything else is
worked out from them.** A placement is never typed twice, never hand-converted to layout units,
and the generated files are checked in, so a diff shows exactly what a number change did.

## What you need

- **Python 3.11+** and **git** (the dev stamp and release checks ask git about the tree).
- **The JamiePhan game-data clone** at `references/JamiePhan`
  (`git clone --depth 1 https://github.com/jamiephan/HeroesOfTheStorm_Gamedata references/JamiePhan`).
  It's Blizzard's current UI and data, extracted. The validator builds its UI tree from it, and
  the inspect card's generator reads hero, unit and ability data from it. `references/` is
  gitignored: no Blizzard data is ever committed.
- **Heroes of the Storm**, for the deploy step and for testing. The interface is selected in
  both `Variables.txt` files (HANDOFF §5).

## How to use it

```bash
python tools/pack.py --wait
```

That's the everyday loop: generate, stage, validate, pack, deploy. Then leave the replay and
reopen it. The game re-reads the interface on every replay load, so the client never has to
restart. `--wait` retries while the game holds the file (it's locked only while a replay or
match is open).

The other commands:

| Command | What it does |
|---|---|
| `python tools/gen.py` | Rewrites the generated files and lists what changed. |
| `python tools/gen.py --check` | Exits 1 if a generated file is stale or was edited by hand. |
| `python tools/validate.py [dir]` | Validates an interface tree (default `src/FCJH.StormInterface`). |
| `python tools/validate.py --show <frame path>` | Prints a frame as the game would merge it: Blizzard's definition, every template and override applied. Run it before guessing what a frame is anchored to. |
| `python tools/pack.py --no-deploy` | Builds without installing. |
| `python tools/pack.py --release [--deploy]` | Builds the release (below). |
| `python tools/mpq.py list\|extract <archive> ...` | Reads any MPQ, including Blizzard's battleground archives. |
| `python tools/make_test_ui.py [--wait]` | Deploys a magenta box: tells "the packer broke" from "the layout broke". |
| `python tools/test_validate.py` | The validator's own tests: each breaks a copy of a real interface in one way. |
| `python design/canvas_gen.py` | Redraws the wireframe canvas boards from the same numbers (below). |

**Profiles.**
- **Dev** (the default) adds a build stamp on screen, top left: `FCJH DEV <version> <commit>[+] <time>`.
  The `+` means uncommitted changes. A stale stamp means the game is showing a cached build.
  Any `src/dev/*.StormLayout` (experiments, probes) is added too. None of this is ever committed
  into `src/` or shipped.
- **`--release`** is exactly what `src/` holds. It refuses while `src/`, `layout.toml` or
  `tools/` have uncommitted changes, so every release can be rebuilt from its commit. It writes
  `dist/v<version>/FCJH.StormInterface`, and installs it only with `--deploy`. Releases ship
  that file.

## What you edit

| File | Holds |
|---|---|
| `layout.toml` | Every number that places something on screen, in **1080p pixels**, plus look settings (colours, sizes, hotkeys). Sections: `[screen]` (size, the padding everything respects), `[minimap]` and its per-map nudges, `[element.*]` rects (`kind = "ui" / "obs" / "demand"`: drawn by us, left empty for OBS, or on demand), `[hero_row]`, `[talent_popup]`, `[heal_popup]`, `[top_backplate]`, `[team_xp]`, `[team_core]`, `[map_alerts]`, `[toggles]`, `[info_pane]`, `[dev]`. |
| `tools/gen.py` | The design: how the plates, bars, panes and top bar are built from those numbers. Also the shared machinery (units, constants, textures, the generated-files bookkeeping). |
| `tools/maps.py` | Each battleground: its minimap's place, its objective panel's parts, its banners. Measured art sizes are kept here, beside their reasons. |
| `tools/inspect_card.py` | The inspect card, including what it reads from the game data (hero units, forms, command-card slots, resource names). |
| `src/FCJH.StormInterface/.../FCJH_*.StormLayout` (the non-generated ones) | Hand-written XML for one-off structure: the top bar, the hidden HUD, the talents pane, the minimap, the replay box, the toggles. They map one to one onto Blizzard's files. |

The rule of thumb: **Python for anything arithmetic or repetitive, hand-written XML for
one-off structure.** The user of FCJH never edits XML at all; they change `layout.toml`, or
describe the effect wanted.

## What it produces

In `src/FCJH.StormInterface/` (committed, each generated file headed "GENERATED ... Do not
edit by hand"):

- **`FCJH_Constants.StormLayout`**: every `layout.toml` rect as layout-unit constants,
  `FCJH_<NAME>_L/_T/_R/_B/_W/_H`. Each one is an offset from the anchor point its piece hangs
  from (top-centre, bottom-centre, an edge, or the piece it sits on; `gen.ANCHORS`), so a
  window that isn't 16:9 keeps things together.
- **`FCJH_HeroRow`, `FCJH_StatPanes`, `FCJH_Inspect`, `FCJH_Maps.StormLayout`**: the generated
  layouts (the plates and their pop-ups, the stat panes, the inspect card, every map's UI).
- **`DescIndex.StormLayout`**: the load order. Constants come first, then every layout in the
  folder.
- **`_Assets/Textures/FCJH_*.dds`**: procedural textures, rasterised in pure Python as
  uncompressed 32-bit DDS. These are the slanted bars and their masks, the portrait masks,
  the plate hit areas, the top backplate and Dragon Knight's mirrored mask. They're drawn at
  their **1440p** size and scaled down at 1080p. Most are named by a hash of their content,
  because the game caches textures by path across replay reloads; gen deletes the superseded
  ones.

Then `build/<profile>/` (the staged tree, plus the dev stamp in a dev build) and the archive:
an uncompressed **MPQ v1** `FCJH.StormInterface`, deployed to
`Documents/Heroes of the Storm/Interfaces/` or written to `dist/v<version>/`.

Beside the build, from the same numbers: **the wireframe canvas.** `design/canvas_gen.py`
imports gen and draws the as-built boards (the default view, the spec table, the plate
anatomy, the panes, the inspect card, the top bar) into `design/canvas/project/*.dc.html`.
Those are published to the canvas artifact. Every build is checked against it.

## The numbers it works in

- **Layout units are not pixels.** The game lays out on a grid 1200 units tall, so at 1080p
  1 unit = 0.9 px on both axes (the screen is 2133 x 1200 units). `layout.toml` is in pixels
  and `gen.Units` converts. Nothing is converted by hand.
- **Derived numbers** (`gen.derive`): the hero rows' scale (`"fit"`: as large as the padding
  allows), their top and outer edges, and any rect placed `above` another, are all worked out
  at load. They're never stored.
- **Checks that refuse a build:**
  - gen refuses anything closer to the screen's edge than `[screen] padding` (`check_padding`);
  - gen refuses anchoring that would move a piece at 16:9 (`check_anchoring`);
  - gen refuses an inspect-card size in `layout.toml` that disagrees with the card's own layout;
  - gen refuses a map nudge without its map's own placer;
  - the validator refuses a hotkey that is one of Blizzard's in-game keys, or that two of
    ours share.

## The validator, in one paragraph

`tools/validate.py` rebuilds the GameUI frame tree the way the game does:
- Blizzard's layouts from JamiePhan, in DescIndex order;
- templates expanded;
- every `file="..."` override applied;
- every hero and battleground mod merged.

It then checks what our files contribute.

**Errors** stop the build:
- XML that doesn't parse (the game drops the whole interface);
- a missing DescIndex file;
- an undefined `#Constant`;
- a template or override that names nothing;
- any frame reference that resolves to nothing (anchors, animation and StateGroup targets,
  `{bindings}`);
- a malformed anchor;
- a hotkey clash;
- an edit to a Blizzard child that doesn't exist. The game would silently create an empty
  frame instead. That's why every frame we add carries the `FCJH_` prefix.

**Warnings** cover what is legal but has cost builds before:
- parking a frame that others anchor to;
- anchoring a side Blizzard re-anchors at runtime;
- `Visible=false` on a Blizzard frame;
- `Fill` without a colour;
- a constant inside a longer value;
- type mismatches.

The Java builder's equivalent was `TODO` stubs.

## What's FCJH's and what's generic

Generic, or nearly:
- `mpq.py`, `validate.py`, `pack.py`, `make_test_ui.py`, `test_validate.py`;
- from `gen.py`:
  - `Units`;
  - the constant writer;
  - the DDS writer and polygon rasteriser;
  - the generated-files bookkeeping (`committed_files`, `stale`, `orphans`, `write`,
    `desc_index`, `layout_order`);
  - the dev stamp.

FCJH's design, with reusable knowledge inside:
- `maps.py`'s map kit:
  - every battleground's map id;
  - `on_map`;
  - the placer;
  - the glide;
  - `Node`, the override tree;
  - the banner builders;
- `inspect_card.py`'s game-data readers.

[extraction-plan.md](extraction-plan.md) has the inventory, the seams to cut (hard-coded
names, paths and the `FCJH_` prefix) and the order to do it in.

**The knowledge that goes with it** is maybe worth more than the code: the layout rules learned
the hard way, all confirmed in game (HANDOFF §3, and the memory notes
`storminterface-layout-rules`, `-build-loop`, `-map-specificity`). The new repo's guide
should be those rules, each validator warning linked to its rule.
