import { useVelcroValue } from '@single-studio/core'

/**
 * The broadcaster's and the tournament's marks, and which one a hole should take.
 *
 * TWO PICTURES EACH, a square and a wide (user, 2026-10-26). An organisation is asked for
 * both once, on the Logos panel, and every graphic then takes whichever fits the hole it is
 * drawing into - because which one is wanted is a property of the hole, not of the show.
 *
 * THE WATERFALL RUNS BOTH WAYS, which is the part worth reading. "Wide, then square, then
 * nothing" is right for a wide hole - a corner 204 x 50, an arm, a lockup mark - and exactly
 * wrong for Blizzard's hexagon, where a wide mark is the thing that cannot be made to work.
 * So a hole says which shape it would rather have and gets the other only as a fallback.
 *
 * A fallback is a worse fit, never a broken one: `shape` comes back with the mark so the hole
 * can soften its treatment. The hexagon fills with a square mark and merely contains a wide
 * one, rather than cropping a wordmark to its middle third.
 *
 * Nothing is the third outcome and a real one. A show with no tournament mark draws no
 * tournament mark, rather than an empty lit container.
 */
const SLOTS = {
  broadcaster: { square: 'event.broadcaster', wide: 'event.broadcaster_wide' },
  tournament: { square: 'event.logo', wide: 'event.logo_wide' },
}

/**
 * Is this mark on air at all? ONE SWITCH PER MARK, ACROSS EVERY SOURCE (user, 2026-10-26:
 * "the same toggle will edit matchup/draft/game/scoreboard"). The game bar, the matchup, the
 * draft and the scores all read the same path, so a broadcaster taken off is taken off
 * everywhere rather than in the one scene somebody remembered.
 *
 * Blizzard's hexagon is NOT governed by the tournament switch. It is its own thing (user,
 * 2026-10-26) - a mark worn by the game's own furniture rather than one of ours - so it has
 * `show.hex` to itself and is unaffected by taking the tournament's marks off the overlay.
 *
 * Off by default, as every toggle here is.
 *
 * @param {'broadcaster'|'tournament'|'hex'} which
 */
export function useShown(which) {
  return Boolean(useVelcroValue(`toggles.show.${which}`))
}

/**
 * The mark a hole should draw: null when there is no picture for it OR when the mark is
 * switched off.
 *
 * THIS IS WHAT MAKES A LOCKUP CLOSE UP. The framework's source `Toggle` keeps its children
 * mounted while it is off, hidden rather than removed - deliberately, so that a graphic laid
 * out around it does not move as it comes and goes. That is the wrong behaviour for a pair of
 * marks meeting at an x: taking the broadcaster off should CENTRE the tournament's mark and
 * take the x with it (user, 2026-10-26), not leave a hole where the other one was.
 *
 * So anything whose layout answers to a mark asks here and renders nothing, and only the
 * fixed boxes - the game bar's two corners, the hexagon - keep a `Toggle` wrapper, where the
 * box is alone in its corner and the fade is worth having.
 *
 * @param {'broadcaster'|'tournament'} which
 * @param {'wide'|'square'} prefer - the shape this hole is drawn for
 */
export function useVisibleMark(which, prefer = 'wide') {
  // both unconditionally: a hook cannot be called behind an if
  const shown = useShown(which)
  const mark = useMark(which, prefer)
  return shown ? mark : null
}

/**
 * The PICTURE a hole should draw, ignoring whether the mark is on air. For a site that gates
 * visibility itself with a `Toggle`, so the box can fade rather than vanish.
 *
 * @param {'broadcaster'|'tournament'} which
 * @param {'wide'|'square'} prefer - the shape this hole is drawn for
 * @returns {{name: string, shape: 'wide'|'square'} | null}
 */
export function useMark(which, prefer = 'wide') {
  const slots = SLOTS[which]
  // both are read every time: a hook cannot be called conditionally, and the pair is what
  // the waterfall is choosing between anyway
  const square = useVelcroValue(`variables.${slots.square}`)
  const wide = useVelcroValue(`variables.${slots.wide}`)

  const first = prefer === 'square' ? 'square' : 'wide'
  const second = first === 'wide' ? 'square' : 'wide'
  const set = { square, wide }

  for (const shape of [first, second]) {
    if (set[shape]) return { name: slots[shape], shape }
  }
  return null
}
