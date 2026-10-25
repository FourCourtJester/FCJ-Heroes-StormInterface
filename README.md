# FCJ Heroes

A free observer interface for Heroes of the Storm, made for casting and tournament
broadcasts, plus the broadcast graphics that go with it.

All ten heroes sit along the bottom of the screen around the minimap, and a slim top bar
leaves most of the screen for the game. Info panes with the match's numbers open on demand,
and Blizzard's ability tooltips stay available when you inspect a hero. It uses Blizzard's
own fonts and art, so it looks at home in the game.

**What are you here for?**

| I want to... | Go to |
|---|---|
| **Watch or cast games with the interface** | [The interface](#the-interface) |
| **Run a broadcast in OBS** | [The broadcast studio](#the-broadcast-studio) |
| **Change it, build it, or build on it** | [For developers](#for-developers) |

---

## The interface

The `.StormInterface` file you load in Heroes, for watching replays and observing live games.

### Install

1. Download the latest `.StormInterface` file from
   **[Releases](https://github.com/FourCourtJester/FCJ-Heroes-StormInterface/releases/latest)**.
2. Put it in `Documents\Heroes of the Storm\Interfaces\`. Make the `Interfaces` folder if
   it isn't there.
3. In Heroes, pick it from the interface drop-down under **Settings → Observer**.
4. Open a replay, or observe a game.

It's laid out for **1920 × 1080**. Its labels come in every language Heroes ships.

### Hotkeys

| Key | What it does |
|---|---|
| `Ctrl+1` | Talents pane |
| `Ctrl+2` | Kills, deaths and damage |
| `Ctrl+3` | Healing |
| `Ctrl+4` | Siege |
| `Ctrl+Shift+I` | Show or hide the inspect card (the selected hero) |
| `Ctrl+Shift+N` | Show or hide player names over the heroes |
| `Ctrl+Shift+C` | Show or hide chat |
| `Ctrl+Shift+R` | Show or hide the replay controls |
| `Ctrl+E` | Hide or show the whole HUD, top plate included |
| `Ctrl+Shift+E` | Hide or show everything but the top plate |

Only one pane is open at a time: opening one closes whichever is open.

---

## The broadcast studio

Graphics for streaming the game in OBS: team names, logos and the series score over the top
bar, plus a standby screen, the draft, a matchup band, webcam frames and an end-of-game
scores screen. It's an
[operator's board](https://fourcourtjester.github.io/FCJ-Heroes-StormInterface/#/) that
runs in your browser. No install and no server.

1. In OBS, add the board as a custom browser dock (**Docks → Custom Browser Docks**) with
   this address:
   `https://fourcourtjester.github.io/FCJ-Heroes-StormInterface/#/`
2. The quickest start is the ready-made OBS collection: the board's **Help** panel links
   it. Import it with **Scene Collection → Import** and every scene and source is there.
   Or add graphics one at a time: the board's menu lists every graphic's browser-source
   address with a copy button. Add them as **Browser** sources at 1920 × 1080.
3. Fill in the teams and the tournament on the board. The graphics update live.

Run the board in OBS on the machine that streams. Your show's data and images are stored
there.

The graphics line up with the interface's top bar, so use the two together. The details are
in [studio/README.md](studio/README.md).

---

## For developers

Everything technical is in **[docs/development.md](docs/development.md)**: how the repo fits
together, building and releasing the interface, running the studio, and the tools.

- [HANDOFF.md](HANDOFF.md): where the project stands, and the rules learned the hard way
- [AGENTS.md](AGENTS.md): working notes for AI coding agents
- [docs/generator.md](docs/generator.md): a guide to the Python generator that builds the
  interface

---

## Credits

- **[Ahli](https://github.com/Ahli/Galaxy-Observer-UI)** (AhliObs) and **[Spazzo](https://github.com/spazzo966/Galaxy-Observer-UI-HeroesFix)**
  (SpazzoObs): the observer interfaces this one learned from.
- **[Jamie Phan](https://github.com/jamiephan/HeroesOfTheStorm_Gamedata)**: the extracted
  game data every layout is checked against.
- Heroes of the Storm, its art and its fonts belong to Blizzard Entertainment. This is a fan
  project, not made or endorsed by Blizzard.

If it's useful to you, you can support it through
[GitHub Sponsors](https://github.com/sponsors/FourCourtJester) or
[Ko-fi](https://ko-fi.com/fourcourtjester).

MIT licence. See [LICENSE](LICENSE).
