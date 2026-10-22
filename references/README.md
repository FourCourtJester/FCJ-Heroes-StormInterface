# `references/` — the material the tools read

Nothing in this folder is ours and none of it is in git: between them these are a couple of
gigabytes of Blizzard's own files and other people's interfaces. `.gitignore` keeps the lot
out and lets this file through, so the folder arrives empty on a fresh clone with only these
instructions in it.

**You need one of them to build.** The rest are what this project was read off while it was
written, and are worth having for the same reason.

## Required

### `JamiePhan/` — Blizzard's game data (≈ 440 MB)

An automated extract of the Heroes game files: `.StormLayout`, `.StormStyle`, `.galaxy`, the
XML and the text tables. It is the source of truth for anything Blizzard's UI does
([jamiephan/HeroesOfTheStorm_Gamedata](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata)).

```bash
git clone --depth 1 https://github.com/jamiephan/HeroesOfTheStorm_Gamedata references/JamiePhan
```

Three tools read it, all under `references/JamiePhan/mods/`:

| Tool | What it takes |
|---|---|
| `tools/validate.py` | `core.stormmod` and `heroesdata.stormmod` — it rebuilds GameUI's frame tree the way the game does, to check our layouts against it |
| `tools/gen.py` | `heroesdata.stormmod/base.stormdata/triggerlibs/uilib.galaxy` — Blizzard's own script, for things like which heroes use which resource |
| `tools/inspect_card.py` | the hero data the inspect card is built from |

Without it `python tools/gen.py` and `python tools/validate.py` both stop. The build itself
does not need it — `python tools/pack.py --release --no-generate --no-validate` packs the
committed `interface/` as it stands, which is exactly how the GitHub release workflow builds
without any of this.

Refresh it when the game patches:

```bash
git -C references/JamiePhan pull --depth 1
```

`references/JamiePhan/VERSIONS.md` says which game version the extract is at. A patch that
changes Blizzard's layouts can move things under our frames, so re-run `tools/validate.py`
after a refresh.

## Optional — what the interface was read off

| Folder | What | Size |
|---|---|---|
| `AhliObs075/` | **Ahli's observer interface, 0.75** (MIT), unpacked. The nearest thing to a reference implementation: our plates, heroics and inspect card all started from how this does it. |  14 MB |
| `AhliObs.StormInterface` | the same, as the shipped archive |  14 MB |
| `Spazzo/` | **SpazzoObs**, unpacked — a second opinion on anything Ahli does |  33 MB |
| `Galaxy-Observer-UI-HeroesFix/` | [Spazzo's fork](https://github.com/spazzo966/Galaxy-Observer-UI-HeroesFix) of Ahli's builder. Carries its own `baseUI` extraction (useful when JamiePhan is behind a patch) and the MPQEditor our archives were cross-checked against | 1.5 GB |
| `CASCView/` | art pulled straight from the installed client — see below | 981 MB |

Unpack an interface with our own reader, which takes any MPQ:

```bash
python tools/mpq.py extract references/AhliObs.StormInterface references/AhliObs075
python tools/mpq.py list references/AhliObs.StormInterface
```

## CascView — making your own reference material

`CascView.exe` here is **[Ladislav Zezula's CascView](http://www.zezula.net/en/casc/main.html)**,
which opens the CASC storage an installed Blizzard client keeps its files in.

It is worth having because the JamiePhan extract carries the *data* — layouts, styles, script,
text — and not the *art*. When a Blizzard layout names a texture and you need to see it, measure
it, or match its colours, CascView is how you get it out of the game you already have installed:
point it at the Heroes install directory, find the file the layout names, and extract.

`CASCView/` is where that lands here: `Assets/` (textures and icons) and `mods/`, extracted from
the live client. Nothing in the toolchain reads it — it is for looking at, and for the colours
and measurements that end up as numbers in `layout.toml`.

It is also the fallback when the extract is behind the live client: CascView is the client, so
it is never out of date.
