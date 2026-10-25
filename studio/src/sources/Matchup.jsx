import { Scene, Variable } from '@single-studio/core/source'

import MatchupBand, { BAND_VARS, SCREEN } from '../components/MatchupBand'
import MatchupSlab, { SLAB_VARS } from '../components/MatchupSlab'

// The matchup band, on its own, over nothing.
//
// It used to live on the standby screen. It is a source of its own because the two are wanted
// at different times (user, 2026-10-23): the standby screen is background material under
// several scenes and stays up for as long as a break lasts, while the band is a thing you
// bring in, let land, and bring in again later in the cast. One source cannot do both - the
// band's entrance plays when the source mounts, so a band welded to the backdrop plays once
// and never again.
//
// Add to OBS as a Browser source pointed at #/source/matchup, 1920 x 1080, over whatever it
// belongs on - the standby screen, the draft screen, a webcam scene.
//
// TO REPLAY THE ENTRANCE, tick the source's **Shutdown source when not visible** (user,
// 2026-10-23: that one, not "Refresh browser when scene becomes active"). The animation runs
// on mount, and shutting the source down while its scene is hidden is what makes it mount
// again; without it the band is simply there, which is the right behaviour for a scene it
// never leaves and the wrong one for a scene you cut back to.
//
// Its message board carries `standby.message` - the Standby panel's "Message" field, which is
// named for where it used to live rather than where it is drawn.

const [SCREEN_W, SCREEN_H] = SCREEN

// WHICH COMPOSITION. `?band=` on the source URL picks one, so they can be looked at side by
// side while the shape is being decided (user, 2026-10-25) - the same trick the webcams use
// for `?fill`. The losers get deleted once it is settled; this switch is scaffolding, not a
// feature.
//
//   (nothing)  the original bottom band
//   slab       hexagon badge + name plate a side - the best so far
//   unit       one container a side: score, logo, name
const BAND = new URLSearchParams(window.location.search).get('band')
const SLAB = BAND === 'slab' || BAND === 'unit'

const SCENE_VARS = {
  ...BAND_VARS,
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
}

export default function Matchup() {
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-band-scene" style={SLAB ? { ...SLAB_VARS, ...SCENE_VARS } : SCENE_VARS}>
        {SLAB ? (
          <MatchupSlab unit={BAND === 'unit'} />
        ) : (
          <MatchupBand plate={<Variable name="standby.message" fallback="" fit />} />
        )}
      </div>
    </Scene>
  )
}
