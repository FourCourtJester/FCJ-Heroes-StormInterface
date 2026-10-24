import { useVelcroValue } from '@single-studio/core'
import { Scene, Variable } from '@single-studio/core/source'

import MatchupBand, { BAND_VARS, SCREEN } from '../components/MatchupBand'
import './draft.css'

// The draft screen: what the broadcast draws over Blizzard's own ban-and-pick screen.
//
// Today it is the standby screen's band and nothing else, wearing the same translucencies it
// wears there (user, 2026-10-23).
//
// THE COVER IS NOT HERE YET, and that is deliberate. Blizzard's draft screen puts the lobby
// chat and the tails of its player columns across the bottom, which a broadcast does not want
// on air, so something has to hide them. Two attempts are in the history and both were wrong
// in the same way: a cover that varies only down the screen. First an opaque band, which sawed
// a straight edge through the hexagon columns and the heroes' legs; then a vertical gradient,
// which softened that edge and changed nothing, because what is behind the cover varies ACROSS
// the screen - columns at both edges, splash art in the middle, chat at the bottom left - and
// no amount of vertical ramp answers a horizontal problem (user, 2026-10-23: "uniform on its
// horizontal axis. This is 100% of the issue").
//
// So the shape has to come from the artwork rather than from a guess. The user is supplying an
// updated chat cover; its geometry gets measured the way the top bar's did, and comes back here
// through layout.toml. studio/README.md keeps what we measured off the reference screenshots in
// the meantime, as the check for whatever arrives.
//
// The band's message board carries the series rather than a message: standby says what is
// coming up, and here there is no question of that - the teams are on screen drafting.
//
// Add to OBS as a Browser source pointed at #/source/draft, 1920 x 1080, over the game capture.

const [SCREEN_W, SCREEN_H] = SCREEN

const SCENE_VARS = {
  ...BAND_VARS,
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
}

// Blizzard's own UI says whose turn it is and how long is left; it never says what the series
// is. `series.pips` is wins needed, which is what the graphic draws - 3 is a best of five.
const BEST_OF = { 2: 'Best of 3', 3: 'Best of 5', 4: 'Best of 7' }

function Series() {
  const pips = useVelcroValue('variables.series.pips')
  const text = BEST_OF[pips]
  return text ? <span>{text}</span> : null
}

export default function Draft() {
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-band-scene fcjh-draft" style={SCENE_VARS}>
        <MatchupBand plate={<Series />} />
      </div>
    </Scene>
  )
}
