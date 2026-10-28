import { useVelcroValue } from '@single-studio/core'
import { Scene } from '@single-studio/core/source'

import { BAND_VARS, SCREEN } from '../components/MatchupBand'
import MatchupSlab, { SLAB_VARS } from '../components/MatchupSlab'

// The matchup band with the series on its plate: over Blizzard's ban-and-pick screen, and
// under the series screen's cards.
//
// MATCHUP-DRAFT, not Draft (user, 2026-10-27): it is the band on two scenes now, the draft's and
// the map series', so it is named for what it is. Matchup is the same band with the Standby
// message on its plate, for the standby screen.
//
// It is the matchup source's container - score, logo and name a side, the VS, the lockup -
// in the same place (user, 2026-10-27: "we redesigned the Matchup band in OBS; we now need to
// set it up in the Draft scene as well"). One component, so a change to the matchup is a
// change here too. Its places clear Blizzard's player columns (x 14-358 and 1618-1896, down
// to y 922): the lockup runs x 449-1471 and the kicker sits over the splash art's black.
//
// The kicker carries the series rather than a message: standby says what is coming up, and
// here there is no question of that - the teams are on screen drafting.
//
// The entrance is the container's (matchupslab.css), so Matchup and Draft come in alike.
//
// No cover: dropped on 2026-10-26 ("users can use their own covers"); studio/README.md keeps
// why the two attempts were wrong.
//
// Add to OBS as a Browser source pointed at #/source/matchup-draft, 1920 x 1080: over the game
// capture on the draft scene, and cropped and scaled under the cards on the series scenes
// (content/guides/obs.md).

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

export default function MatchupDraft() {
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-band-scene" style={{ ...SLAB_VARS, ...SCENE_VARS }}>
        <MatchupSlab unit kicker={<Series />} />
      </div>
    </Scene>
  )
}
