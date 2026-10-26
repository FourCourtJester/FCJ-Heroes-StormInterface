import { useEffect, useState } from 'react'

import { Transition, useVelcroValue } from '@single-studio/core'
import { Image, Scene, Variable } from '@single-studio/core/source'

import { COLOUR_BLIND_VARS, useColourBlind } from '../components/colourBlind'
import { useVisibleMark } from '../components/marks'
import spec from '../generated/scores.json'
import './scores.css'

// The scores screen: what the broadcast draws over Blizzard's end-of-game Stats screen.
//
// A BACKDROP WITH A HOLE IN IT. One thing on that screen is worth keeping and it is the stats
// panel; everything around it is the caster's own gold, gems and account level, the Leave and
// Rename Replay buttons, the chat and its channel joins - none of which belongs on air (user,
// 2026-10-23: "preserve that stats center box; everything else gets replaced").
//
// Cutting a hole rather than patching the corners is what makes this safe. A patch has an edge
// that falls wherever you put it, across whatever happens to be behind - the mistake the draft
// screen's cover made twice. This edge is Blizzard's own frame, so there is no line of ours to
// notice anywhere.
//
// Standing around the hole: the winning team's name across the top, the tournament's and the
// broadcaster's marks under the panel, and a sky that moves (user, 2026-10-23).
//
// Add to OBS as a Browser source pointed at #/source/scores, 1920 x 1080, over the game
// capture. Nothing goes under it except the game.

const [SCREEN_W, SCREEN_H] = spec.screen
const { panel, winner: win, marks, colours } = spec

// "#5cbcec" -> "92 188 236", so the stylesheet can say rgb(var(--blue-rgb) / .8)
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--panel-x': `${panel.x}px`,
  '--panel-y': `${panel.y}px`,
  '--panel-r': `${SCREEN_W - panel.x - panel.w}px`,
  '--panel-b': `${SCREEN_H - panel.y - panel.h}px`,
  '--win-text': `${win.text}px`,
  '--win-track': `${win.track}px`,
  '--win-glow': `${win.glow}px`,
  '--mark-h': `${marks.h}px`,
  '--mark-w': `${marks.w}px`,
  '--mark-pad': `${marks.pad}px`,
  '--x-text': `${marks.x_text}px`,
  '--x-gap': `${marks.x_gap}px`,
  '--win-mark-h': `${win.mark_h}px`,
  '--win-mark-gap': `${win.mark_gap}px`,
  // its true width at the height the band gives it, so it is never squashed
  '--win-mark-w': `${Math.round(win.mark_h * win.mark_ratio)}px`,
  '--win-mark-rgb': rgbOf(win.mark_colour),
  '--comet-fade': `${spec.sky.comet_fade}px`,
  '--blue-rgb': rgbOf(colours.blue),
  '--red-rgb': rgbOf(colours.red),
  '--star-rgb': rgbOf(colours.text),
  '--rim': colours.rim,
}

// The four pieces of screen left around the hole. Each is a window on the same sky.
const PIECES = ['top', 'bottom', 'left', 'right']

/**
 * The winning team's name, across the top band: white, glowing in that team's colour.
 *
 * WHO WON IS THE OPERATOR'S TO SAY, from the two Winner toggles on the Tournament panel.
 * Blizzard's own screen announces a victory, but from the point of view of whoever's client
 * the replay is, and we cover it anyway. The series score cannot stand in for it either:
 * `wins` is stepped on after the result is called, not before, so reading it here would show
 * the wrong team for as long as it took the operator to reach the stepper.
 *
 * It reads `toggles`, not `variables` - a Toggle writes there, which is also what makes it
 * reach air the moment it is pressed rather than waiting for a save. The two are grouped on
 * the board so only one can be lit; blue is preferred here anyway, so a state that should not
 * happen cannot show two names at once.
 *
 * IT GOES OUT THE WAY IT CAME IN (user, 2026-10-23). A toggle is pressed twice, so the name
 * needs an outro as much as an entrance - returning null on the second press would simply
 * blink it off air. `Transition` keeps it mounted long enough to leave, and because `trigger`
 * runs an out-swap-in cycle on any NEW value, correcting blue to red mid-show plays out and
 * back in rather than swapping the word underneath the glow.
 *
 * `last` is what that costs. A cleared toggle has to animate out in the colour it went on in,
 * and the toggle is already off by then, so the last lit side outlives it by one transition.
 *
 * THE NAME ITSELF CUTS (user, 2026-10-23). A Variable fades its own text when the value
 * changes, which is right in a lower third and wrong inside a band that is already moving:
 * on a blue-to-red correction you would get a cross-fade happening inside a slide, two
 * motions on one piece of text. `transition="cut"` is the framework's own no-op variant -
 * zero duration, opacity held - so the band carries the motion and the words just change.
 *
 * Nothing is shown until a side is lit AND that side has a name, so the band never glows
 * around a blank - and clearing the name plays the outro too, rather than cutting.
 */
function Winner() {
  const blueWon = useVelcroValue('toggles.winner.blue')
  const redWon = useVelcroValue('toggles.winner.red')
  const blue = useVelcroValue('variables.blue.name')
  const red = useVelcroValue('variables.red.name')

  const won = blueWon ? 'blue' : redWon ? 'red' : ''
  const name = won === 'blue' ? blue : won === 'red' ? red : ''
  const shown = won && name ? won : ''

  const [last, setLast] = useState('blue')
  useEffect(() => {
    if (shown) setLast(shown)
  }, [shown])
  const side = shown || last

  return (
    <div className={`fcjh-scores-winner ${side}`}>
      {/* the band clips and the content moves, which is what makes the name rise OUT of the
          panel's top edge rather than slide across the panel */}
      <Transition trigger={shown} transition="slide-up" className="fcjh-scores-winner-in">
        <i className="fcjh-win-mark left" />
        <Variable name={`${side}.name`} fallback="" fit transition="cut" />
        <i className="fcjh-win-mark right" />
      </Transition>
    </div>
  )
}

/**
 * The tournament's and the broadcaster's marks, under the panel, read as a collaboration:
 * `<broadcaster> x <tournament>` (user, 2026-10-23).
 *
 * THE TOURNAMENT MARK IS THE WIDE ONE WHERE THERE IS ONE: wide, then square, then nothing
 * (user, 2026-10-23). This band is 320 x 96 a side, which is the shape the wide logo is for;
 * the square one is drawn for Blizzard's hexagon and is only the fallback here, for a show
 * that has not been given a wide version.
 *
 * They CLOSE ON THE x rather than sitting apart - the left one right bound, the right one
 * left bound - so the three read as one lockup on the panel's centre line instead of as two
 * logos that happen to share a band.
 *
 * Each is read before it is drawn, which Image alone would not need - it draws nothing for an
 * unset picture. The reason is the layout: an empty box is still a box, so a show with one
 * mark would hang it off to one side with a 320px hole beside it. And the x is only an x when
 * there are two things to join, so with one mark it goes, and the lone mark centres on its
 * own. With neither, the whole band goes.
 */
function Marks() {
  // both marks are wide holes here: a mark box is 297 x 65 (components/marks.js)
  const broadcaster = useVisibleMark('broadcaster')
  const logo = useVisibleMark('tournament')
  const both = Boolean(broadcaster && logo)

  if (!broadcaster && !logo) return null
  return (
    <div className={`fcjh-scores-marks${both ? '' : ' lone'}`}>
      {/* as the winner: the band clips and the inner element drops, so the pair come down
          from under the panel instead of across it */}
      <div className="fcjh-scores-marks-in">
        {broadcaster ? (
          <div className="fcjh-scores-mark left">
            <Image name={broadcaster.name} alt="" fit="contain" />
          </div>
        ) : null}
        {both ? <span className="fcjh-scores-x">&times;</span> : null}
        {logo ? (
          <div className="fcjh-scores-mark right">
            <Image name={logo.name} alt="" fit="contain" />
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function Scores() {
  // colour-blind mode: the winner's glow in the game's colour-blind pair
  const cb = useColourBlind()
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-scores" style={cb ? { ...SCENE_VARS, ...COLOUR_BLIND_VARS } : SCENE_VARS}>
        {/* Four windows on one sky, rather than one shape with a hole in it. A hole wants
            `evenodd`, which is one more thing to be true in whatever CEF a given OBS ships.
            Each piece is clipped to its own band and holds a full-screen sky pushed back to
            the same place, so the four show different parts of one identical picture and the
            seams fall where both sides are already the same. It is also what lets the motion
            be written once: every copy mounts together, so they animate in step. */}
        {PIECES.map((where) => (
          <div key={where} className={`fcjh-scores-fill ${where}`}>
            <div className="fcjh-scores-sky">
              {/* The comets are in a field of their own because the field carries the mask
                  that stops them at the horizon - a comet crossing the lit floor reads as a
                  streak ON the ground (user, 2026-10-23).

                  Their delays are deliberate, not random: a comet must be at the same point
                  in its journey in all four copies, or it would tear at a seam. */}
              <div className="fcjh-comet-field">
                <i className="fcjh-comet one" />
                <i className="fcjh-comet two" />
                <i className="fcjh-comet three" />
              </div>
            </div>
          </div>
        ))}
        <Winner />
        <Marks />
      </div>
    </Scene>
  )
}
