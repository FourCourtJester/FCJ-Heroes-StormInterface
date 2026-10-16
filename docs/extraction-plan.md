# Extracting the toolchain into its own repo

Notes for a later session (user, 2026-10-09): our Python toolchain replaced the Java builder
FCJH started on, and it is the better pipeline. Worth pulling out into a separate repo, to
open-source later, with FCJH as its first user. **Not now:** after the map pass and Phase 2
settle, so the extraction doesn't stall the interface. Nothing here is decided yet; the open
questions are at the end.

## What we replaced

Ahli's [Galaxy-Observer-UI](https://github.com/Ahli/Galaxy-Observer-UI) (MIT, Christoph
Ahlers, 2019; our copy `references/Galaxy-Observer-UI-HeroesFix`): a Java 21 / Spring Boot
builder with a GUI, made for SC2 and Heroes. It extracts the base UI, compiles archives and
starts replays. Its anchor validator was `TODO` stubs, and it writes MPQ format version 3
(the 208-byte "MPQ v4" header).

Ours, all Python 3.11+ **standard library only** (no install step, no Java):

| | Java builder | Ours |
|---|---|---|
| Archive | MPQ format v3 | MPQ v1, uncompressed: the game accepts it (confirmed 2026-09-25), read back and checked on every build |
| Validation | almost none | a merged GameUI tree, as the game builds it, with errors and warnings (below) |
| Authoring | hand-written XML | generated XML from one config of screen pixels; generated files committed, `--check` for staleness |
| Builds | GUI | one command: generate, stage, validate, pack, deploy; dev and release profiles |
| Loop | restart the client | rebuild at the menu, reopen the replay; `--wait` retries a locked file |
| Base UI | its own extractor | the JamiePhan game-data extract (a git clone, refreshed per patch) |

## Inventory: what's generic, what's FCJH

Line counts as of 2026-10-16 (`tools/`, `design/`). What the generator is and does, as a
user sees it: [generator.md](generator.md).

**Generic already (move nearly as is):**
- `tools/mpq.py` (260): MPQ reader/writer; `list` and `extract` on any archive, zlib/bzip2
  sectors on read. No FCJH references at all.
- `tools/validate.py` (736): the base-UI tree builder (Blizzard's layouts in DescIndex order,
  templates expanded, `file=` overrides applied, hero and battleground mods merged) and every
  check:
  - errors: XML that doesn't parse, missing DescIndex files, undefined constants, missing
    templates or override targets, dead frame references (anchors, animations, state groups,
    `{bindings}`), malformed anchors, edits to Blizzard children that don't exist;
  - warnings: parking anchored-to frames, sides Blizzard re-anchors at runtime, `Visible=false`
    on Blizzard frames, `Fill` without a colour, partial constants, type mismatches.
  - Seams to cut: `DEFAULT_SOURCE`, `MODS` (the JamiePhan path), `OUR_PREFIX = "FCJH_"`, and
    one map-file special case (line ~550). `--show <frame>` prints the merged tree: a
    debugging tool on its own.
- `tools/pack.py` (191): the five steps; dev/release profiles; release refuses a dirty tree, so
  every release is reproducible from its commit; the dev build stamp; `--wait`.
  - Seams: `NAME`, the stamp's text, the Interfaces folder and Variables.txt paths, the `gen`
    import (make generation a hook).
- `tools/make_test_ui.py` (161): the smoke test, a magenta box that tells "the packer broke"
  from "the layout broke". **This is the hello-world example** for the new repo.
- `tools/test_validate.py` (163): breaks a copy of a real interface on purpose, one mistake per
  test. Needs a neutral fixture (below).

**Mixed (split the helpers out of `gen.py`, ~3130 lines):**
- `Units`: px at a screen height to layout units (the 1200-unit reference grid).
- `name()` (constant naming; prefix hard-coded) and the constants-layout writer.
- `dds_bgra`: an uncompressed 32-bit DDS writer. With `offset_polygon` / `convex_sdf` and the
  slant/mask texture code: procedural textures rasterised in pure Python. A small `textures`
  module.
- `desc_index`, `layout_order`, `committed_files`, `stale`, `orphans`, `write`: the
  generated-files machinery (write what changed, refuse stale or orphaned files). Generic.
- `dev_layout`: the build stamp layout.
- Everything else in `gen.py` is FCJH's design: hero rows, plates, panes, pop-ups.

**FCJH-only, with generic knowledge inside:**
- `tools/maps.py` (3026): FCJH's per-map placements. What generalises, as a "map kit":
  - `MAP_IDS` (every battleground's `libCore_gv_mAPMapStringID`, with where each was read);
  - `on_map()` (the DataRefFrame and When test);
  - the placer pattern (a frame in a map's own panel, one unconditioned state);
  - the objective-keyed glide (relative Anchor controller, Visibility latch);
  - `Node`, the frame-override tree that writes each path once.
- `tools/inspect_card.py` (1149): FCJH's card. Generic inside it: reading hero, unit and
  ability data from the JamiePhan extract (`hero_units`, the forms table, `CardLayouts`
  slots).
- `design/canvas_gen.py` (1064), `design/render_png.py`: as-built wireframe boards from the
  generator. The idea is generic (a layout's boxes drawn from its own config); the code is
  FCJH's boards.

**The knowledge, maybe the most valuable part:** the layout rules learned the hard way, all
confirmed in game. Among them:
- `Visible=false` doesn't stick on Blizzard frames;
- relative Anchor keys count from the layout anchor;
- leaving a state undoes its actions;
- DefaultState is the fallback;
- a nine-slice can't draw shorter than its art;
- `Rotation` is degrees clockwise.

They live in HANDOFF §3 and in Claude's memory (`storminterface-layout-rules`, `-build-loop`,
`-map-specificity`). Write them up as the new repo's guide, checked against the validator's
warnings: each warning should link to its rule.

## Shape of the new repo (a sketch)

```
<name>/                  (a package; stdlib only)
  mpq.py                 archive read/write, CLI
  base_ui.py             the merged GameUI tree (from validate.py)
  validate.py            the checks, prefix and paths from the project config
  pack.py                stage / validate / pack / deploy, profiles, --wait, a generate hook
  units.py               px <-> units
  textures.py            DDS writer, polygon/SDF rasteriser
  generated.py           desc_index, committed/stale/orphan files
  layout.py              Node (override tree), anchor and constant helpers
  maps.py                map ids, on_map, placer, glide (the map kit)
  gamedata.py            JamiePhan readers (heroes, units, abilities, forms)
examples/hello/          the magenta-box interface (make_test_ui)
tests/                   validator tests on a neutral fixture
docs/                    the layout rules; the JamiePhan setup; the dev loop
```

A project would declare itself in one file (its `pyproject.toml` or its own toml): archive
name, source folder, frame prefix, JamiePhan path, the game's Interfaces and Variables.txt
paths, and an optional generate step. FCJH's `layout.toml` stays FCJH's.

## How to do it, in order

1. **Cut the seams inside FCJH first.** Replace the hard-coded names (`NAME`, `OUR_PREFIX`,
   `DEFAULT_SOURCE`, `MODS`, the stamp, `name()`'s prefix) with one project config, and make
   generation a hook pack.py calls. FCJH keeps building the same, byte for byte. Check that
   with the round trip: same archive contents before and after.
2. **Move the generic code into a package inside FCJH** (`tools/<name>/`), FCJH's tools
   importing it. Still one repo, so nothing breaks while the boundary settles.
3. **Make a neutral fixture.** build50 is FCJH's design: rebuild the validator tests on the
   hello-world interface plus small purpose-made layouts. Then the tests don't ship FCJH.
4. **Split the repo with its history** (`git filter-repo` on the package's paths, which keeps
   blame), then FCJH depends on it: a git submodule, a pinned `pip install git+...`, or
   vendored. Decide when we get there.
5. **Docs and examples:** the rules guide, setup (the JamiePhan clone; Variables.txt), the
   loop, hello-world. Then CI running the tests.

## Licensing and what must never ship

- No Blizzard data in the repo: JamiePhan stays a clone the user makes (`references/` is
  gitignored here). Tests must not need it, or must skip without it.
- Blizzard art, fonts and textures are used by reference (`@UI/...` paths), never copied: keep
  it that way.
- **`DocumentHeader`:** a binary we copy, not author (editor metadata, format not decoded).
  Find out where ours came from before shipping it. Better: work out the format and write it.
- Ahli's builder is MIT: we took ideas, not code. Credit it in the README anyway. Spazzo's
  and Ahli's interfaces are references only; copy nothing from them.
- Our repo is MIT (Shaun Delaney, 2026); the new one would match, unless the user says
  otherwise.

## Open questions for the user

- Its name, and whose GitHub it lives under.
- Heroes only, or SC2 too? The Java builder did both. Our validator knows Heroes' mods; SC2
  would need its own base UI source.
- Do the map kit and the game-data readers belong in it, or stay FCJH's?
- PyPI, or git installs only?
- When: after Phase 2, or after the first FCJH release?
