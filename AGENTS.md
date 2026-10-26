# Working in this repo

For AI coding agents. People start at the [README](README.md); the technical reference is
[docs/development.md](docs/development.md).

## Start here

1. **[HANDOFF.md](HANDOFF.md)** - §1 is where things stand, §7 what's next. It is the
   project's memory: read it before changing anything, and log what you do in it.
2. **[docs/development.md](docs/development.md)** - how the three veins fit together, the
   paths, the build and release.
3. Working in `studio/`? **[studio/AGENTS.md](studio/AGENTS.md)** has Single Studio's rules.

## The rules

- **Numbers live in `layout.toml`.** Placements are screen pixels at 1920×1080. Change the
  number, then regenerate; never hand-convert to layout units.
- **Generated files are committed and never hand-edited.** `tools/gen.py` writes the
  interface's generated layouts and textures; `tools/obs.py` writes `studio/src/generated/`.
  `python tools/gen.py --check` fails if either is stale.
- **The studio owns the broadcast.** Python may generate assets and a numbers JSON for it,
  nothing else - no generated CSS or markup.
- **Blizzard is the source of truth.** `references/JamiePhan` is the current game's UI and
  data. Reuse and reposition Blizzard's own widgets rather than rebuilding them, and use
  Blizzard's fonts and art, never custom ones.
- **CI never generates.** The Blizzard extract isn't in the repo, so what is committed is
  what ships. Generate and validate locally before a release tag.
- **One channel per intent.** Releases ship the `.StormInterface`, Pages ships the studio,
  and the planned API folder is markdown for developers. Don't cross them.

## The loop

```
python tools/gen.py
python tools/gen.py --check
python tools/validate.py              # 0 errors is the bar; note the warning count
python -m unittest discover -s tools
python design/canvas_gen.py           # keeps the wireframe canvas's as-built boards current
python tools/pack.py --wait           # dev build, deployed to the game's Interfaces folder
```

HANDOFF §2 is the loop in full and §5 the game's traps (the interface locked while a replay
is open, out-of-patch replays dropping the selection). The user
tests in game and in OBS at 1080p; an agent can only check the studio in a browser, so say
so rather than claiming something works on air.

## Releasing

Bump `[meta] version` in `layout.toml`, write `docs/releases/v<version>.md` (the interface's
changes only - never the studio's), regenerate, commit, then push the tag `v<version>`. `.github/workflows/release.yml` checks the tag matches the version, packs the
committed `interface/` and publishes the release.

## Logs to keep

- [docs/blizzard-fixes.md](docs/blizzard-fixes.md) - every Blizzard UI shortcoming fixed, or
  that couldn't be
- [docs/single-studio-reports.md](docs/single-studio-reports.md) - framework behaviour to
  raise upstream with Single Studio
