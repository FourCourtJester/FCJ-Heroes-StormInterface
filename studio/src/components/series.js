import spec from '../generated/series.json'

/**
 * The map draft's data, in one place: where each fact lives, and how the cards are read out
 * of it. The board writes these paths, the sources read them, and Teams' swap trades them.
 *
 * EVERYTHING A SIDE DID IS KEYED BY SIDE (user, 2026-10-27: swap sides takes the series), so
 * the framework's SwapButton trades a draft whole - blue's bans become red's - with no
 * mutation of its own. A value saying "blue" could not be swapped; a path saying it can.
 *
 *   toggles.series.hidden.<map>        the map is out of this series: every map is in until
 *                                      the board hides it (user, 2026-10-27)
 *   toggles.series.ban.<side>.<map>    that side banned it
 *   toggles.series.pick.<side>.<map>   that side picked it
 *   toggles.series.won.<side>.<map>    that side won it
 *   variables.series.game.<map>        the game it was picked for: 1, 2, 3...
 *
 * Toggles rather than variables, because a toggle is on or gone: an unbanned map deletes its
 * path rather than holding "no". The game number is the one value with more than two states.
 */
export const MAPS = spec.maps
export const SIDES = ['blue', 'red']

export const HIDDEN = (map) => `toggles.series.hidden.${map}`
export const BAN = (side, map) => `toggles.series.ban.${side}.${map}`
export const PICK = (side, map) => `toggles.series.pick.${side}.${map}`
export const WON = (side, map) => `toggles.series.won.${side}.${map}`
export const GAME = (map) => `variables.series.game.${map}`

/** Every side-keyed path, blue's then red's in the same order - SwapButton's halves. */
export const SWAP_PATHS = SIDES.flatMap((side) =>
  MAPS.flatMap(({ slug }) => [BAN(side, slug), PICK(side, slug), WON(side, slug)]),
)

/**
 * Everything the draft holds, the hidden maps with it: Reset draft brings every map back
 * (user, 2026-10-27). The best-of is not here; it outlives a draft.
 */
export const DRAFT_PATHS = [...SWAP_PATHS, ...MAPS.flatMap(({ slug }) => [GAME(slug), HIDDEN(slug)])]

/**
 * One map's state, read out of the two collections (`toggles.series.*` and
 * `variables.series.game.*`, each keyed by the part after its prefix).
 *
 * `by` is whoever banned or picked it; `won` whoever won it. A map both sides touched is a
 * board mistake - the panel will not make one - and reads as the first side's.
 */
function read(slug, toggles, games) {
  const side = (kind) => SIDES.find((s) => toggles[`${kind}.${s}.${slug}`]) ?? null
  const ban = side('ban')
  const pick = ban ? null : side('pick')
  const game = pick ? Number(games[slug]) || null : null
  return {
    state: ban ? 'ban' : pick ? 'pick' : 'open',
    by: ban ?? pick,
    game,
    won: pick ? side('won') : null,
  }
}

/**
 * The maps to draw, in the order they stand: games played and playing, by game number; then
 * what is still open, in the board's order; then the bans, blue's before red's - the mock the
 * reviewers passed (2026-10-27). A hidden map is not drawn at all.
 *
 * `live` marks the game being played: the highest-numbered pick with no winner yet.
 */
export function draft(toggles, games) {
  const maps = MAPS.filter(({ slug }) => !toggles[`hidden.${slug}`]).map((map) => ({
    ...map,
    ...read(map.slug, toggles, games),
  }))
  const picks = maps.filter((m) => m.state === 'pick').sort((a, b) => (a.game ?? 99) - (b.game ?? 99))
  const open = maps.filter((m) => m.state === 'open')
  const bans = maps.filter((m) => m.state === 'ban').sort((a, b) => SIDES.indexOf(a.by) - SIDES.indexOf(b.by))

  const live = [...picks].reverse().find((m) => !m.won)
  if (live) live.live = true

  return [...picks, ...open, ...bans]
}
