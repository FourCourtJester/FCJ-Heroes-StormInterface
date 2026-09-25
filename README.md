# FCJH — FourCourtJester Heroes observer interface

A custom `.StormInterface` observer overlay for Heroes of the Storm, for esports and
broadcast use. It strips the stock observer console, relocates Blizzard's ten hero cells
into one row at bottom-centre, and carves a top bar whose branding regions are left empty
for OBS to fill.

**Start with [HANDOFF.md](HANDOFF.md)** — current state, the dev loop, the layout rules
learned the hard way, and what's outstanding.

## Quick start

Requires Python 3 (standard library only).

```
python tools/pack.py --wait
```

Packs `src/FCJH.StormInterface/` into an MPQ archive and deploys it to the Heroes
`Interfaces` folder. Select it by setting `observerinterface=` and `replayinterface=` to
`FCJH.StormInterface` in **both** `Variables.txt` files (see HANDOFF §5), with Heroes closed.

Launch Heroes from the Battle.net app and open a replay from the in-game Replays tab.
After a rebuild, leave the replay and reopen it — no client restart needed.

| Path | What |
|---|---|
| `src/FCJH.StormInterface/` | Interface source; the archive's file tree, one to one |
| `tools/pack.py` | Validate, pack, deploy |
| `tools/validate.py` | Check layouts against Blizzard's base UI; `--show <frame>` prints the merged tree |
| `tools/test_validate.py` | Validator tests |
| `tools/mpq.py` | MPQ reader/writer; `list` / `extract` any archive |
| `tools/make_test_ui.py` | Smoke test: a minimal Python-authored interface |

## Base UI reference

`references/JamiePhan` — shallow clone of
[jamiephan/HeroesOfTheStorm_Gamedata](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata),
an automated extract of Heroes game data (xml, txt, galaxy, `.StormLayout`, `.StormStyle`).
Currently at game version **2.55.17.97650**. Refresh with:

```
git -C references/JamiePhan pull --depth 1
```

Note: the repo's stated 4-hourly automation appeared stalled as of August 2026 (last commit
2026-07-24), but it was still one patch ahead of the local client extraction under
`references/Galaxy-Observer-UI-HeroesFix/baseUI`.

`references/` is gitignored.

## References

- **Galaxy Observer UI for Heroes** by *Spazzo* —
  https://github.com/spazzo966/Galaxy-Observer-UI-HeroesFix (fork of Ahli's builder; source
  of the MPQEditor used to cross-check our archives)
- **AhliObs** by *Ahli* (MIT) and **SpazzoObs** — mature observer interfaces, unpacked under
  `references/`, for "how does anyone do X"

## Directories

Interface files:
```
C:\Users\highb\OneDrive\Documents\Heroes of the Storm\Interfaces
```

StarCraft II Map Editor:
```
C:\Program Files (x86)\StarCraft II\StarCraft II Editor_x64.exe
```
