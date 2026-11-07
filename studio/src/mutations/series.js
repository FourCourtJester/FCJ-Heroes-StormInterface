import { BAN, GAME, OPEN, PICK, SIDES, WON } from '../components/series'

// The map draft (user, 2026-10-27). The paths are in ../components/series.js, which says why
// they are keyed by side.
//
// WHO WON A MAP IS PRESSED ON THE BOARD, and only there (series:win). The Score Screen Winner
// used to stamp the latest game's map and add the point as well; that was scrapped after the
// user asked people (2026-10-27: "we will scrap any kind of automatic stamping of a winner").

// The paths each one writes are gathered in an object, so a map's clears and its new marks
// cannot write the same path twice, and handed over as the [path, value] pairs ctx.write takes.

const games = (ctx) => ctx.collect('variables.series.game')

export const series = {
  /**
   * Ban or pick a map for a side, or take that back: a second press on the same button undoes
   * it, like the framework's grouped toggles.
   *
   * One map holds one thing. Marking it clears whatever it held, so a map is never banned by
   * one side and picked by the other - and a map that stops being a pick loses its game number
   * and its result with it, rather than keeping a winner nobody can see.
   *
   * A NEW PICK TAKES THE NEXT GAME NUMBER, one past the highest there is, because picks happen
   * in the order the games are played. The panel's game number corrects it if not.
   *
   * `mutate('series:mark', { map: 'cursed-hollow', side: 'blue', as: 'pick' })`
   */
  'series:mark'(ctx, { map, side, as }) {
    const at = as === 'ban' ? BAN(side, map) : PICK(side, map)
    const on = !ctx.read(at)

    const pairs = {}
    for (const s of SIDES) {
      pairs[BAN(s, map)] = null
      pairs[PICK(s, map)] = null
    }

    const keepsGame = on && as === 'pick' && SIDES.some((s) => ctx.read(PICK(s, map)))
    if (!keepsGame) {
      pairs[GAME(map)] = null
      for (const s of SIDES) pairs[WON(s, map)] = null
    }

    if (on) {
      pairs[at] = true
      if (as === 'pick' && !keepsGame) {
        const played = Object.entries(games(ctx))
          .filter(([slug]) => slug !== map)
          .map(([, n]) => Number(n) || 0)
        pairs[GAME(map)] = String(Math.max(0, ...played) + 1)
      }
    }

    ctx.write(Object.entries(pairs))
  },

  /**
   * A side won a map, or take that back: the two Wins under a map are one group, so a map has
   * one winner and a second press on the lit one clears it, as the framework's grouped toggles do.
   *
   * WINNING MINIMISES THE MAP ON THE BOARD (user, 2026-10-29): the game is over, and the
   * operator has the next map to work on. Only the board's block folds - the card stays on
   * the screen with its result. Taking a win back leaves the block as it is.
   *
   * `mutate('series:win', { map: 'cursed-hollow', side: 'blue' })`
   */
  'series:win'(ctx, { map, side }) {
    const at = WON(side, map)
    const on = !ctx.read(at)

    const pairs = {}
    for (const s of SIDES) pairs[WON(s, map)] = null
    if (on) {
      pairs[at] = true
      pairs[OPEN(map)] = null
    }

    ctx.write(Object.entries(pairs))
  },
}
