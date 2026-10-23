import { Transition, useTimer } from '@single-studio/core'
import { Image, Scene, Slideshow, Timer, Variable } from '@single-studio/core/source'

import spec from '../generated/standby.json'
import './standby.css'

// The standby screen: what the stream shows when the game isn't on - before the show, between
// games, through a break.
//
// Three things over a slideshow.
//
// The BAND across the bottom is the "coming up next" board: a team container either side of a
// VS, a message board behind them, a logo arm at each screen edge. Its composition is the old
// NGS board (C:\FourCourtJester\Broadcasts\Heroes, apollo/scenes/scene-afk, 2018) - the user's
// own, and the reason this screen has this shape. Its places are that board's; its language is
// this kit's, so a container is the game band's name plate grown up: the same lean, now coming
// to a point at half height, the same chrome rim, wash and hex lattice.
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
const { band, bug, colours } = spec
const { team, plate, arm } = band

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--band-h': `${band.height}px`,
  '--team-w': `${team.w}px`,
  '--team-h': `${team.h}px`,
  '--team-inset': `${team.inset}px`,
  '--team-bottom': `${team.bottom}px`,
  '--team-point': `${team.point}px`,
  '--team-gap': `${team.gap}px`,
  '--team-cap': `${team.nine_slice.caps}px`,
  '--team-cap-n': team.nine_slice.caps,
  '--plate-w': `${plate.w}px`,
  '--plate-h': `${plate.h}px`,
  '--plate-bottom': `${plate.bottom}px`,
  '--plate-point': `${plate.point}px`,
  '--plate-text': `${plate.text}px`,
  '--plate-row': `${plate.row}px`,
  '--arm-w': `${arm.w}px`,
  '--arm-h': `${arm.h}px`,
  '--arm-bottom': `${arm.bottom}px`,
  '--arm-over': `${arm.over}px`,
  '--arm-pad': `${arm.pad}px`,
  '--arm-taper': `${arm.taper}px`,
  '--bug-w': `${bug.w}px`,
  '--bug-h': `${bug.h}px`,
  '--bug-taper': `${bug.taper}px`,
  '--stock-top': colours.stock[0],
  '--stock-bottom': colours.stock[1],
  '--rim': colours.rim,
  '--text': colours.text,
  '--base-top': colours.base_top,
  '--base-bottom': colours.base_bottom,
  '--smoke': colours.smoke,
  '--bug-smoke': colours.bug_smoke,
}

// "#5cbcec" -> "92 188 236", so the stylesheet can say rgb(var(--team-rgb) / .58). The game
// scene keeps its own copy of this, two lines being cheaper than a module both must import
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

SCENE_VARS['--blue-rgb'] = rgbOf(colours.blue)
SCENE_VARS['--red-rgb'] = rgbOf(colours.red)

const SIDES = ['blue', 'red']

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

        <div className="fcjh-matchup">
          {/* the board first, so the containers sit over it as the old one had them */}
          <div className="fcjh-matchup-plate">
            <Variable name="standby.message" fallback="" fit />
          </div>

          {SIDES.map((side) => (
            <div className={`fcjh-matchup-team ${side}`} key={side}>
              <Variable name={`${side}.name`} fallback="" fit />
            </div>
          ))}

          <div className="fcjh-matchup-vs">
            <span>VS</span>
          </div>

          {/* the broadcaster's mark on the left, the tournament's on the right - the old
              board's arrangement with the game's logo replaced (user, 2026-10-22). Either can
              be left unset, and Image then draws nothing at all rather than an empty box */}
          <div className="fcjh-matchup-arm left">
            <Image name="event.broadcaster" alt="" fit="contain" />
          </div>
          <div className="fcjh-matchup-arm right">
            <Image name="event.logo" alt="" fit="contain" />
          </div>
        </div>
      </div>
    </Scene>
  )
}
