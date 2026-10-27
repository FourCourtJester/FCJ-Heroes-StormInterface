# Developing FCJ Heroes

The technical reference: how the repo fits together, how to build and release, and where
things are. The [README](../README.md) is for people using the interface or the studio;
[HANDOFF.md](../HANDOFF.md) is where the project stands and why.

## Three veins, one repo

| Vein | Where | What it makes |
|---|---|---|
| **The interface** | `interface/` | `FCJ v<version>.StormInterface`, the file casters select in Heroes. Shipped as a GitHub release, per version tag |
| **The broadcast graphics** | `studio/` | A [Single Studio](https://github.com/FourCourtJester/Single-Studio) app: an operator's board in an OBS dock and a browser source per graphic. Published to GitHub Pages on every push that touches it |
| **The generator** | `tools/` | Python that writes both from `layout.toml` — the interface's layouts and textures, and the studio's parts and numbers |

They are one repo because they are one set of numbers. `layout.toml` places the hero plates
*and* the broadcast's name plates; `python tools/gen.py` writes both halves, and `--check`
fails if either has gone stale. Nothing has to be kept in step by hand.

## Where each is published - one channel, one job

| Channel | Serves | Nothing else |
|---|---|---|
| **GitHub Releases** | The `.StormInterface` file, one per version tag `v<version>` (`.github/workflows/release.yml`) | No studio build, no docs, no studio notes |
| **GitHub Pages** | The OBS studio: the operator's board and its browser sources (`.github/workflows/pages.yml`, on pushes to `main` that touch `studio/`) | No interface file |
| **An API folder** *(planned)* | Markdown for other developers, read in the repo | - |

CI never generates: the Blizzard extract isn't in the repo, so the committed output is what
ships. GitHub renames a release's asset with dots for spaces (`FCJ.v1.0.2.StormInterface`).

## The interface

Requires Python 3.11+ (standard library only).

```
python tools/pack.py --wait
```

Generates, validates, packs and deploys a dev build to the Heroes `Interfaces` folder.
Pick `FCJ Dev.StormInterface` from the interface drop-down under Settings → Observer.

Launch Heroes from the Battle.net app and open a replay from the in-game Replays tab.
After a rebuild, leave the replay and reopen it — no client restart needed.

To move or resize anything, change its pixels in `layout.toml` and rebuild.

`python tools/pack.py --release` builds the shipping file, `dist/v<version>/FCJ v<version>.StormInterface`,
from committed sources only. To release, bump `[meta] version` in `layout.toml`, write
`docs/releases/v<version>.md` - the interface's changes only, never the studio's - commit, and
push the tag `v<version>`; the Release workflow builds and publishes it with those notes, and
fails if the file is missing.

The generator's own guide is [generator.md](generator.md).

## The studio

Requires Node 22+, only to develop it: Pages builds it in CI, and the interface's loop never
touches it.

```
cd studio
npm install
npm run dev
```

[studio/README.md](../studio/README.md) covers the graphics and the board;
[studio/AGENTS.md](../studio/AGENTS.md) covers Single Studio's rules.
**Nothing in `studio/src/generated/` is written by hand** — `tools/obs.py` writes it.

## Where things are

| Path | What |
|---|---|
| `layout.toml` | Every placement, in screen pixels at 1920×1080, from the wireframe |
| `interface/FCJH.StormInterface/` | Interface source; the archive's file tree, one to one |
| `studio/` | The broadcast graphics; `studio/README.md` is its own start |
| `studio/src/generated/` | Written by `tools/obs.py`, never by hand |
| `tools/obs.py` | The broadcast parts and numbers from `layout.toml` |
| `tools/pack.py` | Generate, stage, validate, pack, deploy (dev or `--release`) |
| `tools/gen.py` | Generated layouts and textures from `layout.toml`; `--check` for staleness |
| `tools/words.py` | Our on-screen words, in every language Heroes ships |
| `tools/inspect_card.py` | The inspect card, written by `gen.py` (reads hero data from JamiePhan) |
| `tools/validate.py` | Check layouts against Blizzard's base UI; `--show <frame>` prints the merged tree |
| `tools/test_validate.py` | Validator tests, against the archived build 50 in `tests/fixtures/` |
| `tools/mpq.py` | MPQ reader/writer; `list` / `extract` any archive |
| `tools/make_test_ui.py` | Smoke test: a minimal Python-authored interface |
| `design/canvas_gen.py` | Regenerates the wireframe canvas's as-built boards from `gen.py` |
| `docs/` | Reference notes: maps, OBS, Blizzard fixes, Single Studio reports, history |

The agreed design is a canvas of to-scale wireframes:
https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK

## Base UI reference

`references/JamiePhan` — shallow clone of
[jamiephan/HeroesOfTheStorm_Gamedata](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata),
an automated extract of Heroes game data (xml, txt, galaxy, `.StormLayout`, `.StormStyle`).
It is the source of truth for Blizzard's current UI. Currently at game version
**2.57.0.98304**. Refresh with:

```
git -C references/JamiePhan pull --depth 1
```

Note: the repo's stated 4-hourly automation appeared stalled as of August 2026 (last commit
2026-07-24), but it was still one patch ahead of the local client extraction under
`references/Galaxy-Observer-UI-HeroesFix/baseUI`.

`references/` is gitignored, and [references/README.md](../references/README.md) is what
arrives there instead: the one extract the tools need, the interfaces this project was
read off, and CascView for pulling art straight out of the installed client.

## Other observer interfaces

- **Galaxy Observer UI for Heroes** by *Spazzo* —
  https://github.com/spazzo966/Galaxy-Observer-UI-HeroesFix (fork of Ahli's builder; source
  of the MPQEditor used to cross-check our archives)
- **AhliObs** by *Ahli* (MIT) and **SpazzoObs** — mature observer interfaces, unpacked under
  `references/`, for "how does anyone do X"

## Directories

Interface files: `Documents\Heroes of the Storm\Interfaces` (on the maintainer's machine,
under OneDrive: `C:\Users\highb\OneDrive\Documents\Heroes of the Storm\Interfaces`).

StarCraft II Map Editor:
```
C:\Program Files (x86)\StarCraft II\StarCraft II Editor_x64.exe
```
