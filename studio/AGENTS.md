# Working in this studio

For anyone — person or agent — building a show here. This is a
[Single Studio](https://fourcourtjester.github.io/Single-Studio/) project: an
operator's board that runs as a dock inside OBS, and one browser source per graphic.

## What to edit, and what not to

|                               |                                                                   |
| ----------------------------- | ----------------------------------------------------------------- |
| `src/studio/config.js`        | **Start here.** `STUDIO_NAME` and `STUDIO_ID`.                    |
| `src/sources/`                | One file per graphic. Every `.jsx` here becomes a browser source. |
| `src/control/`                | The operator's board. `Control.jsx` composes `panels/`.           |
| `src/mutations/`              | How the show's data changes.                                      |
| `src/css/`                    | Tailwind, and your own CSS.                                       |
| `src/studio/studio.js`        | Wiring. You should not need to touch it.                          |
| `src/studio/velcro.worker.js` | The store, and where plugins are registered.                      |

**Only graphics belong in `src/sources`.** Anything else there turns up in the
operator's list and in OBS. Shared pieces go in `src/components`.

## Running it

```bash
npm install
npm run dev      # the printed URL; the header menu lists every graphic's OBS URL
npm run build
```

## The rules that are not obvious

**A value that means "nothing" deletes its path.** `undefined`, `null`, `false` and
`''` all remove the key rather than storing it. So a mutation writing
`{ 'variables.x': false }` leaves `variables.x` absent, and a `<Variable>` reading it
renders its fallback rather than the word "false". This is deliberate — absent and
empty are the same thing on air — and it is the single most common surprise. Store a
string if you need to tell them apart.

**Graphics render nothing until their value has loaded.** A browser source set to
unload when hidden is rebuilt every time its scene returns, and painting a fallback
on mount would flash it on air. `fallback` is for a path that has loaded and is
genuinely empty, not for "not yet".

**A mutation may not wait.** No `fetch`, no timers, no promises inside one — it runs
inside a single transaction. Anything with a wait belongs in the worker's `onReady`,
which then calls a mutation with the result. `ctx.ask()` to a plugin is the one
exception, because a command does not wait.

**`STUDIO_ID` is where the show is filed.** Changing it starts an empty show. It is
not a label; `STUDIO_NAME` is.

## Adding a plugin

A plugin brings the outside world in — a game, a spreadsheet, a scoring feed.
Install it, register it in `src/studio/velcro.worker.js`, and write a handler with
one method per event you care about:

```js
import { rocketLeague, RocketLeagueHandler } from '@single-studio/plugin-rocket-league'

class MyShow extends RocketLeagueHandler {
  onScore({ blue, orange }) {
    this.mutate('set', { 'variables.home.score': blue, 'variables.away.score': orange })
  }
}

createVelcroHost({ name: STUDIO_ID, mutations, plugins: [rocketLeague(MyShow)] })
```

The operator sets addresses and credentials on the board, under **Plugins** — those
belong to the machine, not to the build, so do not hard-code them.

To have one plugin drive another — a goal cutting OBS to the replay —
`this.ask('obs', 'scene', { name: 'Replay' })`.

## Before you say a change is done

```bash
npm run build
```

and open the graphic you changed. A studio has no test suite of its own by default;
the thing that catches mistakes here is looking at the source in a browser at the
size OBS will run it.

Check it at **1920×1080**, not at whatever size the window happens to be. A graphic
that is correct in a narrow browser and wrong on air has cost somebody a broadcast.

## Where the answers are

- [Getting started](https://fourcourtjester.github.io/Single-Studio/getting-started) — the tour, and every component with an example
- [Component reference](https://fourcourtjester.github.io/Single-Studio/api) — generated from the source, so it is never out of date
- [Your own data](https://fourcourtjester.github.io/Single-Studio/data) — mutations, collections, and what the store is
- [Plugins](https://fourcourtjester.github.io/Single-Studio/plugins) — using one, and writing one
