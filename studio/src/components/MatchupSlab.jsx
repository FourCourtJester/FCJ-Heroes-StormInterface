import { useLayoutEffect, useRef } from 'react'

import { useVelcroValue } from '@single-studio/core'
import { Image, Variable } from '@single-studio/core/source'

import { COLOUR_BLIND_VARS, useColourBlind } from './colourBlind'
import { useVisibleMark } from './marks'
import spec from '../generated/matchup.json'
import './matchupslab.css'

// The matchup slab: the centred composition, explored alongside the bottom band (user,
// 2026-10-25).
//
// WHY IT IS NOT A BAND. The band spends a team container of 576 x 130 on one line of text -
// three times the area the in-game name plate uses for the same thing - and puts 1152 px of
// event branding at the two screen edges, where the eye goes looking for who is playing. So
// this brings the teams to the middle, gives each a logo, and collapses the two arms into
// one lockup underneath.
//
// A TEAM IS A HEXAGON AND A PLATE. The badge is a pointy-top hexagon because this kit is
// already hexagonal - the series pips, the lattice inside every plate, Blizzard's own
// centrepiece in the top bar - and because a plate pointed at both ends is a poor home for a
// logo, which was the complaint. The badge rides over the plate's outer point by a lap, the
// way the game bar's logo plate laps its name plate; butted exactly they meet at one point
// and pinch.
//
// Blue left, red right, as everywhere else in the kit. The names meet across the VS so you
// read "A vs B" straight through the middle, which is why the logos are OUTBOARD - the game
// bar puts them inboard only because Blizzard's hexagon occupies its centre, a constraint
// that does not exist here.
//
// Reading order down the screen: what this is (the kicker), who is playing (the matchup),
// then who is bringing it to you (the lockup) - branding last, not first.

const [SCREEN_W, SCREEN_H] = spec.screen
const { badge, name, unit, vs, kicker, mid, lockup, colours } = spec

// "#5cbcec" -> "92 188 236", so the stylesheet can say rgb(var(--team-rgb) / .58)
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

// a generated box, [x, y, width, height] on the page - the only geometry a style carries
const at = ([left, top, width, height]) => ({ left, top, width, height })

export const SLAB_SCREEN = spec.screen

export const SLAB_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--kicker-flare': `${kicker.flare}px`,
  '--lockup-pad': `${lockup.pad}px`,
  '--unit-point': `${unit.point}px`,
  '--unit-lean': `${unit.lean}px`,
  '--unit-score': `${unit.score}px`,
  '--unit-score-text': `${unit.score_text}px`,
  '--unit-logo': `${unit.logo}px`,
  '--unit-rule': `${unit.rule}px`,
  '--unit-name': `${unit.name}px`,
  '--name-point': `${name.point}px`,
  '--name-text': `${name.text}px`,
  '--name-lines': name.lines,
  '--name-pad': `${name.pad}px`,
  // both caps are DERIVED from their plate's height (tools/obs.py frame_cap), never
  // authored - a cap that is picked by hand drifts off the art it slices
  '--name-cap': `${name.nine_slice.caps}px`,
  '--name-cap-n': name.nine_slice.caps,
  '--unit-cap': `${unit.cap}px`,
  '--unit-cap-n': unit.cap,
  '--vs-text': `${vs.text}px`,
  '--kicker-text': `${kicker.text}px`,
  '--lockup-x': `${lockup.x_text}px`,
  '--lockup-mark': `${lockup.mark}px`,
  '--rim': colours.rim,
  '--rim-w': `${colours.rim_w}px`,
  '--base-top': colours.base_top,
  '--base-bottom': colours.base_bottom,
  '--text': colours.text,
  '--smoke': colours.smoke,
  '--blue-rgb': rgbOf(colours.blue),
  '--red-rgb': rgbOf(colours.red),
}

const SIDES = ['blue', 'red']

/**
 * WRAP, THEN SHRINK - which is the opposite order to the framework's `fit`.
 *
 * `fit` guarantees one line by shrinking, and it is ruthless about it: a 25-character club
 * name measured 23.8px against the 46 it was asked for, 48%, which is what made the old
 * band's container look like a big box with nothing in it. Here the name wraps to
 * `name.lines` at full size first, and only shrinks if it still does not fit - so the common
 * case (a short name, or one that breaks neatly in two) stays big.
 *
 * It steps a pixel at a time from `max` to `min`. That is at most twenty-odd layouts, on a
 * change that happens between games rather than per frame, and it lands on the largest size
 * that fits rather than a size computed from an estimate that could be wrong either way.
 */
function useWrapThenShrink(plateRef, { max, min, lines }) {
  useLayoutEffect(() => {
    const plate = plateRef.current
    if (!plate) return undefined

    const measure = () => {
      const el = plate.querySelector('.ss-variable')
      if (!el) return
      let size = max
      el.style.fontSize = `${size}px`
      while (size > min) {
        const line = parseFloat(getComputedStyle(el).lineHeight)
        // offsetHeight, NOT scrollHeight. scrollHeight on this element reads about 11px
        // over the laid-out height - measured 107 against an offsetHeight of 96 for two
        // 47.84px lines - so comparing it shrank a name that already fitted, all the way
        // down until it collapsed onto one line, which is the exact behaviour this hook
        // exists to avoid. One pixel of slack on top, since a fractional line height
        // rounds against us.
        if (el.offsetHeight <= line * lines + 1) break
        size -= 1
        el.style.fontSize = `${size}px`
      }
    }

    measure()
    // the name arrives after the room connects, and changes between games: watch for both
    const mo = new MutationObserver(measure)
    mo.observe(plate, { childList: true, subtree: true, characterData: true })
    return () => mo.disconnect()
  })
}

/**
 * A team as ONE CONTAINER (user, 2026-10-25) - the alternative to the badge-and-plate pair.
 *
 * WHY. The hexagon arrangement reads as a bulge, a shaft and a taper, mirrored and
 * converging on the middle; four passes of tuning sharpened it rather than fixing it, and
 * flattening the outer edge made it worse by removing the symmetry that was holding it
 * together. Putting everything inside one shape removes the silhouette entirely, because
 * there is nothing left protruding from anything.
 *
 * WHAT IS IN IT, outward to inward: the series score, a parallelogram for the logo (the game
 * scene's logo plate, in this kit's lean), then the name running in to the VS. The container
 * keeps the name plate's own edges - flat outside, pointed in.
 *
 * The score lands here almost by accident, which is the nice part: the space between the
 * logo and the outer border was going spare (user, 2026-10-25), and a score retrofitted
 * after the geometry had set would have meant moving everything.
 */
function TeamUnit({ side }) {
  const logo = useVelcroValue(`variables.${side}.logo`)
  const teamName = useVelcroValue(`variables.${side}.name`)
  const blueWins = useVelcroValue('variables.blue.wins')
  const redWins = useVelcroValue('variables.red.wins')
  // NO NAME, OR NO GAMES PLAYED, NO SCORE (user, 2026-10-27): a nameless team's 0 is a number
  // about nobody, and 0 - 0 is a series that has not started. Absent wins count as 0.
  const score = Boolean(teamName) && Number(blueWins || 0) + Number(redWins || 0) > 0
  const plate = useRef(null)
  useWrapThenShrink(plate, { max: name.text, min: name.min, lines: name.lines })

  // anchored at the VS end; the far end is wherever its contents reach
  const anchor = {
    top: unit.top,
    height: unit.h,
    [side === 'blue' ? 'right' : 'left']: unit.inner,
  }

  return (
    <div className={`fcjh-unit ${side}`} style={anchor}>
      {/* no score, no number - but THE PANEL STAYS (user, 2026-10-27: "The size changes
          again when we have non zero scores"), so the band is one length whatever it holds */}
      <div className="fcjh-unit-score">
        {score ? <Variable name={`${side}.wins`} fallback="0" /> : null}
      </div>
      {/* The parallelogram. Its own panel even when empty: it is what the score counts
          against, and a gap there would leave the score floating at the container's end.

          `cover`, as the game scene's logo plate does it (user, 2026-10-25): the mark fills
          the plate and the slant clips what hangs over, rather than being contained in the
          straight-sided rectangle inside it.

          NO LOGO, NO PANEL - it does not hold its space (user, 2026-10-25, and again
          2026-10-27: "we can shrink based upon the fact we have no team logo"). The container
          is anchored at the VS end and sized by what is in it, so a team without a logo simply
          gets a shorter band rather than one with a dark gap where a mark should be. The
          score's panel is the one that holds its space. */}
      {logo ? (
        <div className="fcjh-unit-logo">
          <Image name={`${side}.logo`} alt="" fit="cover" />
        </div>
      ) : null}
      <div ref={plate} className="fcjh-unit-name">
        <Variable name={`${side}.name`} fallback="" />
      </div>
    </div>
  )
}

/** A team: the hexagon badge with its logo, and the name plate it laps. */
function Team({ side }) {
  const logo = useVelcroValue(`variables.${side}.logo`)
  const plate = useRef(null)
  useWrapThenShrink(plate, { max: name.text, min: name.min, lines: name.lines })

  return (
    <>
      <div ref={plate} className={`fcjh-slab-name ${side}`} style={at(name[side])}>
        {/* NO `fit` HERE, deliberately. `fit` guarantees one line by shrinking: it renders
            its own `whitespace-nowrap` span with an inline font-size, and on a 25-character
            club name in this plate it measured 23.8px - 48% of the 46 it was asked for. That
            is the complaint this whole composition is answering, upside down: the box was
            never too big, the text was being crushed to stay on one line. Wrapping to two
            keeps it big and readable (user, 2026-10-25). */}
        <Variable name={`${side}.name`} fallback="" />
      </div>
      {/* no logo, no badge - an empty hexagon is a lit frame around nothing, and the plate
          reads perfectly well on its own (the game bar does the same with its logo plate) */}
      {logo ? (
        <div className={`fcjh-slab-badge ${side}`} style={at(badge[side])}>
          {/* COVER, not contain: the mark fills the hexagon and the clip cuts it to shape
              (user, 2026-10-25), rather than sitting in a square inside it */}
          <Image name={`${side}.logo`} alt="" fit="cover" />
        </div>
      ) : null}
    </>
  )
}

/**
 * The broadcaster's and the tournament's marks, under the matchup, as one lockup - the
 * scores screen's `<broadcaster> x <tournament>`, brought here to replace the two arms.
 *
 * The tournament mark is the WIDE one where there is one: wide, then square, then nothing,
 * the same waterfall the rest of the kit uses.
 */
function Lockup({ where }) {
  // wide holes, both of them (components/marks.js)
  const broadcaster = useVisibleMark('broadcaster')
  const logo = useVisibleMark('tournament')
  const both = Boolean(broadcaster && logo)

  if (!broadcaster && !logo) return null
  return (
    <div className={`fcjh-slab-lockup${both ? '' : ' lone'}`} style={at(where)}>
      {broadcaster ? (
        <div className="fcjh-slab-mark left">
          <Image name={broadcaster.name} alt="" fit="contain" />
        </div>
      ) : null}
      {both ? <span className="fcjh-slab-x">&times;</span> : null}
      {logo ? (
        <div className="fcjh-slab-mark right">
          <Image name={logo.name} alt="" fit="contain" />
        </div>
      ) : null}
    </div>
  )
}

// THE KICKER IS THE SCENE'S. Matchup gives it the standby message; Matchup Draft gives it the series,
// since the teams are on screen drafting and "what is coming up" has no answer there.
const MESSAGE = <Variable name="standby.message" fallback="" fit />

export default function MatchupSlab({ unit: asUnit = false, kicker: says = MESSAGE }) {
  // colour-blind mode: the team washes in the game's pair, as the band's
  const cb = useColourBlind()

  return (
    <div className={`fcjh-slab${asUnit ? ' as-unit' : ''}`} style={cb ? COLOUR_BLIND_VARS : undefined}>
      {/* The same smoke as the kicker, behind the row: it fills the gaps the plates and
          the VS leave, so the three read as one shape instead of three near each other.

          Both of these hang off whichever team shape is in play - the plate is 110 tall and
          the container 140, so one set of numbers cannot serve both (user, 2026-10-25). */}
      <div className="fcjh-slab-mid" style={at(asUnit ? unit.mid : mid)} />

      <div className="fcjh-slab-kicker" style={at(asUnit ? unit.kicker : kicker.box)}>
        {says}
      </div>

      {SIDES.map((side) =>
        asUnit ? <TeamUnit key={side} side={side} /> : <Team key={side} side={side} />,
      )}

      <div className="fcjh-slab-vs" style={at(asUnit ? unit.vs : vs.box)}>
        <span>VS</span>
      </div>

      <Lockup where={asUnit ? unit.lockup : lockup.box} />
    </div>
  )
}
