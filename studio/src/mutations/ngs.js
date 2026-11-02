import { HIDDEN, MAPS } from '../components/series'

// The Nexus Gaming Series (user, 2026-10-29), through @single-studio/plugin-ngs. The plugin
// fetches and src/studio/velcro.worker.js writes what came back under variables.ngs; this is
// the one step that reaches the show's own paths.
//
//   variables.ngs.season      the season's number
//   variables.ngs.divisions   [{ key, name }], the league's order
//   variables.ngs.maps        the season's map pool, by name
//   variables.ngs.matches     the chosen division's unplayed matches, each whole, with its
//                             round named (roundName: "Round 2", "Semifinals")
//   variables.ngs.problem     the last fetch's trouble, gone once one works
//
// NEVER A SCORE. The plugin carries none, and Load leaves the wins and the draft alone: the
// score is the operator's, kept on the Teams panel.

// the Series panel's best-of holds pips a side: a best of five is three
const PIPS = { 3: '2', 5: '3', 7: '4' }

export const ngs = {
  /**
   * The chosen match onto the board, pressed once before going live. It fetches nothing:
   * everything it writes came with the division.
   *
   * Home is blue and away red. A side the playoffs have not filled yet is TBD, and a team
   * without a logo writes no logo, so our own empty plate shows.
   *
   * The two tabs get the league and season, "Nexus Gaming Season 22", and the division and
   * round, "Division Heroic: Round 2" (user, 2026-11-02). The best-of goes to the Series panel,
   * and the maps outside the season's pool are hidden there and the rest shown - if the
   * season has been fetched, since without it there is no pool to go by.
   *
   * `mutate('ngs:load', { id })`
   */
  'ngs:load'(ctx, { id } = {}) {
    const match = (ctx.read('variables.ngs.matches') ?? []).find((one) => one.id === id)
    if (!match) return
    const season = match.season ?? ctx.read('variables.ngs.season')

    const pairs = {
      'variables.blue.name': match.home?.name ?? 'TBD',
      'variables.blue.logo': match.home?.logo ?? null,
      'variables.red.name': match.away?.name ?? 'TBD',
      'variables.red.logo': match.away?.logo ?? null,
      'variables.division': season ? `Nexus Gaming Season ${season}` : 'Nexus Gaming',
      'variables.game': [`Division ${match.divisionName}`, match.roundName].filter(Boolean).join(': '),
    }
    if (PIPS[match.bestOf]) pairs['variables.series.pips'] = PIPS[match.bestOf]

    const pool = ctx.read('variables.ngs.maps')
    if (Array.isArray(pool) && pool.length) {
      for (const { slug, name } of MAPS) pairs[HIDDEN(slug)] = pool.includes(name) ? null : true
    }

    ctx.write(Object.entries(pairs))
  },
}
