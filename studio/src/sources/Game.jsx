import { useEffect, useLayoutEffect, useRef, useState } from 'react'

import { useVelcroValue } from '@single-studio/core'
import { Image, Scene, Tally, Toggle, Variable } from '@single-studio/core/source'

import { COLOUR_BLIND, useColourBlind } from '../components/colourBlind'
import { useMark } from '../components/marks'
import spec from '../generated/topbar.json'
import './game.css'
import pipBlue from '../generated/pip_blue.svg'
import pipBlueCb from '../generated/pip_blue_cb.svg'
import pipEmpty from '../generated/pip_empty.svg'
import pipRed from '../generated/pip_red.svg'
import pipRedCb from '../generated/pip_red_cb.svg'

// The game scene: what the broadcast draws over a live match. Today that is the top bar - the
// plates over the interface's own, and the data on them - and it is where anything else that
// belongs on the game itself will go.
//
// Every number comes from ../generated/topbar.json, which tools/obs.py writes from the
// interface's layout.toml, so this graphic and the game's UI are drawn from one set of numbers
// and cannot drift apart. How any of it LOOKS is game.css's business, not this file's: a
// `style` here carries a box or a custom property and never a declaration.
//
// Add to OBS as a Browser source pointed at #/source/game, 1920 x 1080, over the game capture.
// The interface draws the places; this draws the plates.
//
// The interface must stay usable with no OBS running (2026-10-22), so nothing here has a
// counterpart in the .StormInterface file: with this source off, the game's top bar is the
// level wings, Blizzard's hexagon and the clock.

const { boxes, clip, colours, name_plate: plate, tabs } = spec
const SIDES = ['blue', 'red']
const PIP = { blue: pipBlue, red: pipRed }
const PIP_CB = { blue: pipBlueCb, red: pipRedCb }   // colour-blind mode's
const [SCREEN_W, SCREEN_H] = spec.screen

// "#5cbcec" -> "92 188 236", so game.css can say rgb(var(--team-rgb) / .58)
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

// every generated number the stylesheet reads, in one place on the scene root
const SCENE_VARS = {
  '--scene-w': `${SCREEN_W}px`,
  '--scene-h': `${SCREEN_H}px`,
  '--band-h': `${spec.band.height}px`,
  '--band-w': `${boxes.band.blue[2]}px`,
  '--pip-row-w': `${boxes.pip_row.blue[2]}px`,
  '--slant': `${spec.band.slant_run}px`,
  '--cap': `${plate.nine_slice.caps}px`,
  '--cap-n': plate.nine_slice.caps,
  '--logo-w': `${plate.logo_plate.width}px`,
  '--logo-lap': `${plate.logo_lap}px`,
  '--pip-margin': `${spec.score_pips.item_margin}px`,
  '--ban-clip-blue': clip.bans.blue,
  '--ban-clip-red': clip.bans.red,
  '--banned-foot': colours.banned_foot,
  '--event-clip': clip.event,
  // the kit's own dark purple, the same pair the plates are filled with
  '--base-top': colours.base_top,
  '--base-bottom': colours.base_bottom,
  '--tab-font': `${tabs.font_px}px`,
  '--tab-text': colours.tab_text,
  '--tab-h': `${boxes.tabs.division[3]}px`,
  '--tab-cap': `${tabs.cap}px`,
  '--tab-cap-n': tabs.cap,
  '--rim': colours.rim,
}

// a generated box, [x, y, width, height] on the page - the only geometry a style carries
const at = ([x, y, width, height]) => ({ left: x, top: y, width, height })

/** A team's name plate, with its logo plate when the tournament has logos. */
function Band({ side }) {
  const logo = useVelcroValue(`variables.${side}.logo`)
  const team = (useColourBlind() ? COLOUR_BLIND : colours)[side]
  const [left, , width] = boxes.band[side]
  return (
    <div
      className={`fcjh-band ${side}`}
      style={{ left, width, '--team-rgb': rgbOf(team), '--logo-clip': clip.logo[side] }}
    >
      <div className="fcjh-name">
        {/* the team line, its own element because the frame's two pseudo-elements are
            already spent (lattice, chrome) - and because a line that is masked and painted
            takes any colour, where one baked into the frame needed a frame per scheme */}
        <i className="fcjh-team-line" />
        <Variable name={`${side}.name`} fallback="" fit />
      </div>
      {logo ? (
        <div className="fcjh-logo">
          <Image name={`${side}.logo`} className="mark" alt="" fit="cover" />
        </div>
      ) : null}
    </div>
  )
}

/**
 * The series score: hexagon pips, filled from the name outward. Index 0 is the pip nearest the
 * name, so blue's row runs right to left and red's left to right (game.css); a shorter series
 * leaves the far end of the row empty.
 */
function Pips({ side }) {
  const cb = useColourBlind()
  return (
    <Tally
      name={`${side}.wins`}
      of="series.pips"
      src={(cb ? PIP_CB : PIP)[side]}
      empty={pipEmpty}
      alt=""
      className={`fcjh-pips ${side}`}
      itemClassName="fcjh-pip"
      style={at(boxes.pip_row[side])}
    />
  )
}

// Bans are shelved until after the first user pass (user, 2026-10-22) - not deleted. The
// geometry (boxes.bans, clip.bans), the tile art, the rules in game.css and the control panel
// all still exist; only the wiring is out. To put them back, restore this and the block in
// the tree below it, and the two lines in control/Control.jsx and control/panels/Options.jsx.
//
// /** One ban tile: the empty tile is the art, the portrait is clipped to its shape. */
// function BanTile({ side, index, box }) {
//   const picked = useVelcroValue(`variables.${side}.bans.${index}`)
//   return (
//     <div className={`fcjh-ban ${side}`} style={at(box)}>
//       {picked ? (
//         <div className="fcjh-ban-art">
//           <Image name={`${side}.bans.${index}`} alt="" fit="cover" />
//           <div className="fcjh-ban-foot" />
//         </div>
//       ) : null}
//     </div>
//   )
// }
//
// ...and in the tree, between the pips and the tabs:
//
//   {/* bans are optional - not every tournament shows them - so the whole row, tiles and
//       all, hangs off one toggle. The wrapper is the full page: the framework animates it,
//       and a transform on it would otherwise become the containing block for the tiles'
//       absolute coordinates. */}
//   <Toggle name="bans" className="fcjh-layer">
//     {SIDES.map((side) =>
//       boxes.bans[side].map((box, index) => (
//         <BanTile key={`${side}${index}`} side={side} index={index} box={box} />
//       )),
//     )}
//   </Toggle>

/**
 * The division (blue) and game (red) tabs: our art, the operator's words.
 *
 * Each is anchored by its inner edge and grows outward with its words, and the two are then
 * held to one width - whichever needs more - so the pair stay uniform either side of the
 * hexagon. The words are measured, not the tabs: a tab's own width is what we are setting,
 * so measuring it would feed back on itself.
 *
 * A BLANK TAB IS NOT DRAWN (user, 2026-10-23: "Hide tournament tabs if they're blank"). The
 * art does not depend on the words, so an empty one is a lit, framed container with nothing
 * in it - which on air reads as a fault rather than as a field nobody filled. Each goes on
 * its own, so a tournament that numbers its games but has no divisions gets the one tab.
 * This is read here and not in game.css because a stylesheet cannot ask whether its own text
 * is empty - the same reason Band reads the logo.
 */
function Tabs() {
  const refs = { division: useRef(null), game: useRef(null) }
  const said = {
    division: useVelcroValue('variables.division'),
    game: useVelcroValue('variables.game'),
  }
  const shown = [
    ['division', tabs.division],
    ['game', tabs.game_count],
  ].filter(([which]) => said[which])

  useLayoutEffect(() => {
    const tabs_ = Object.values(refs).map((r) => r.current).filter(Boolean)
    // On its own a tab takes its own width. Clearing the property matters as much as setting
    // it: the survivor keeps its inline --tab-w when its partner goes blank, so without this
    // a lone "Game 3 of 5" would sit in the width "Championship Division" asked for.
    if (tabs_.length < 2) {
      tabs_.forEach((el) => el.style.removeProperty('--tab-w'))
      return
    }
    const measure = () => {
      const widths = tabs_.map((el) => {
        // the span Variable renders, not the box around it: it is flex: none, so its width is
        // the words' own and cannot be pushed about by the width we are setting
        const words = el.querySelector('.fcjh-tab-words > *')
        if (!words) return 0
        const cs = getComputedStyle(el)
        return words.getBoundingClientRect().width + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)
      })
      const w = Math.ceil(Math.max(...widths))
      if (!w) return // nothing has arrived yet; leave the tabs at their natural width
      tabs_.forEach((el) => el.style.setProperty('--tab-w', `${w}px`))
    }
    measure()
    // the words turn up after the room connects, and change between games: watch for both
    const mo = new MutationObserver(measure)
    tabs_.forEach((el) =>
      mo.observe(el, { childList: true, subtree: true, characterData: true }),
    )
    return () => mo.disconnect()
  })

  return (
    <div className="fcjh-tab-layer">
      {shown.map(([which, spec_]) => (
        <div
          key={which}
          ref={refs[which]}
          className={`fcjh-tab ${which}`}
          style={{
            '--tab-anchor': `${spec_.anchor}px`,
            '--words-l': `${spec_.text_inset[0]}px`,
            '--words-r': `${spec_.text_inset[1]}px`,
          }}
        >
          <div className="fcjh-tab-words">
            <Variable name={which} fallback="" title={spec_.example} />
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * Whether there is anything to play the entrance over.
 *
 * The trigger is the scene loading - OBS is set to shut this source down when its scene is
 * hidden, so coming back mounts it afresh. But mounting is not the same moment as the show's
 * values arriving: they come from this machine's own document a beat later, and without this
 * the sequence would play across an empty bar and the words would pop in after it.
 *
 * So the animations start paused (game.css) and are let go either when a team name turns up
 * or after a short wait - because a show with no names in it yet is still a show, and the
 * graphic must never be stuck invisible waiting for one.
 */
function useReady(wait = 600) {
  const blue = useVelcroValue('variables.blue.name')
  const red = useVelcroValue('variables.red.name')
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (ready) return undefined
    if (blue || red) {
      setReady(true)
      return undefined
    }
    const timer = setTimeout(() => setReady(true), wait)
    return () => clearTimeout(timer)
  }, [blue, red, ready, wait])

  return ready
}

export default function Game() {
  // Which picture each hole takes. The two corners are wide holes and the hexagon is not, so
  // the hexagon asks for the square one first - see components/marks.js.
  const hexMark = useMark('tournament', 'square')
  const leftMark = useMark('broadcaster')
  const rightMark = useMark('tournament')
  const ready = useReady()
  const cb = useColourBlind()
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className={`fcjh-scene${ready ? ' ready' : ''}${cb ? ' cb' : ''}`} style={SCENE_VARS}>
        {/* order is paint order: the tabs and the pips slide out from UNDER the bands, so
            they are drawn first and the bands cover them until they arrive */}
        <Tabs />
        {SIDES.map((side) => (
          <Pips key={side} side={side} />
        ))}
        {SIDES.map((side) => (
          <Band key={side} side={side} />
        ))}
        {/* a straight line along each level wing's foot, from the band to the hexagon: it is
            the game's wing, always there, so it does not wait for the show or come in */}
        {SIDES.map((side) => (
          <i key={side} className="fcjh-level-rim" style={at(boxes.level_rim[side])} />
        ))}
        {/* The tournament logo in Blizzard's hexagon - THE ONE HOLE THAT WANTS THE SQUARE
            picture, and so the one place the waterfall runs the other way (user,
            2026-10-26). An oblong mark here is squashed or cropped, which is why the wide
            one exists as a separate picture at all.

            `cover` for a square mark: the clip path is the hexagon, so the mark is meant to
            fill it and be cut by it. `contain` for a wide one, which only gets here when a
            show has no square mark at all - letterboxed and small is a poor fit, cropping a
            wordmark to its middle third is a broken one. */}
        <Toggle name="show.hex" className="fcjh-layer">
          <div
            className={`fcjh-event${hexMark ? ' has-mark' : ''}`}
            style={at(boxes.event)}
          >
            {hexMark ? (
              <Image
                name={hexMark.name}
                alt=""
                fit={hexMark.shape === 'square' ? 'cover' : 'contain'}
              />
            ) : null}
          </div>
        </Toggle>

        {/* THE TWO CORNER MARKS: the broadcaster's top left, the tournament's WIDE logo top
            right (user, 2026-10-23). The switches are the show-wide ones - the same paths the
            matchup, the draft and the scores read - so a mark taken off is off everywhere
            (user, 2026-10-26).

            These two keep a `Toggle` wrapper where the lockups do not: a corner box is alone
            against its screen edge, so nothing moves when it empties, and the wrapper is what
            fades it rather than cutting it.

            The room is what a best of 7 leaves - its outermost pip reaches further than
            anything else on the band - so obs.py derives the box from the pip row instead of
            carrying a typed width that would quietly stop being true. Each mark binds to its
            own screen edge, so the pair sit IN the corners rather than drifting toward the
            middle when a logo is narrow.

            Worth knowing: Blizzard's own kill feed also lives top left. These sit inside the
            band's height to stay clear of it, but the two have not been seen together in a
            live game yet. */}
        <Toggle name="show.broadcaster" className="fcjh-layer">
          <div className="fcjh-corner left" style={at(boxes.corner.left)}>
            {leftMark ? <Image name={leftMark.name} alt="" fit="contain" /> : null}
          </div>
        </Toggle>
        <Toggle name="show.tournament" className="fcjh-layer">
          <div className="fcjh-corner right" style={at(boxes.corner.right)}>
            {rightMark ? <Image name={rightMark.name} alt="" fit="contain" /> : null}
          </div>
        </Toggle>
      </div>
    </Scene>
  )
}
