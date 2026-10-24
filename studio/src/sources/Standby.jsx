import { Transition, useTimer } from '@single-studio/core'
import { Scene, Slideshow, Timer, Variable } from '@single-studio/core/source'

import spec from '../generated/standby.json'
import './standby.css'

// The standby screen: what the stream shows when the game isn't on - before the show, between
// games, through a break.
//
// Three things over a slideshow.
//
// The BAND is not here. It is its own source now (#/source/matchup), because this screen is
// background material that stays up for a whole break while the band is something you bring in
// and bring in again (user, 2026-10-23). Lay the two over each other in OBS.
//
// The BUG hangs from the top edge, where that broadcast's countdown hung (apollo/scenes/
// bug-timer, user 2026-10-22). It is a time of day rather than a length, so it survives this
// source being shut down and restarted every time the scene comes back.
//
// The SLIDESHOW plays whatever is filed under `slides/` in the studio's image library, and
// drifts while it plays - see standby.css, which is where that argument is made.
//
// Add to OBS as a Browser source pointed at #/source/standby, 1920 x 1080.

const [SCREEN_W, SCREEN_H] = spec.screen
const { bug, colours } = spec

// the band brings its own; these are the screen's and the bug's
const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--bug-w': `${bug.w}px`,
  '--bug-h': `${bug.h}px`,
  '--bug-taper': `${bug.taper}px`,
  '--stock-top': colours.stock[0],
  '--stock-bottom': colours.stock[1],
  '--text': colours.text,
  '--bug-smoke': colours.bug_smoke,
}

export default function Standby() {
  // No clock on air, no bug - and no fly-in either, which is the point: an empty tab sliding
  // down from the top edge to say nothing is worse than never arriving (user, 2026-10-23).
  //
  // `active`, not the stored value. A timer's record outlives its run: it keeps the operator's
  // entry so the field repopulates after a reload, so `Boolean(record)` is true from the first
  // time anyone types a time until somebody clears it - which is how the bug came to hang there
  // showing a label and an empty clock. `active` is the framework's own answer to this, and it
  // is arithmetic rather than a flag: counting down, or a second past zero, then gone.
  const { active } = useTimer('timers.standby.resume')

  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-standby" style={SCENE_VARS}>
        {/* `slides` is the image library's own group: file art under slides/ and it plays */}
        <Slideshow className="fcjh-slides" group="slides" name="standby.slides" every={9} order="shuffle" />

        {/* A Toggle without an operator: the clock is the switch. Transition gives the
            same four phases a Toggle has, so the bug drops in when the clock starts and
            retracts under the top edge when it runs out, instead of being cut from the DOM
            (user, 2026-10-23). Children stay mounted throughout, which is what lets the exit
            play at all - and costs nothing here, since the bug is positioned and so moves
            nothing around it. */}
        <Transition trigger={active} transition="slide-down" className="fcjh-bug">
          <Variable className="label" name="standby.label" fallback="" />
          <Timer className="time" name="standby.resume" fallback="" />
        </Transition>

      </div>
    </Scene>
  )
}
