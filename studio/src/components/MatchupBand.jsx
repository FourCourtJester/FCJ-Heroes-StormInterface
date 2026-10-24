import { useVelcroValue } from '@single-studio/core'
import { Image, Variable } from '@single-studio/core/source'

import spec from '../generated/standby.json'
import './matchup.css'

// The matchup band: a team container either side of a VS, a message board behind them, and a
// logo arm at each screen edge.
//
// Shared by the standby screen and the draft screen. It carries its own numbers - they come
// from layout.toml's [standby], which is where this band was born and still belongs - so a
// scene that wears it needs to know nothing about its geometry. Spread BAND_VARS into the
// scene's own style and render <MatchupBand>.
//
// `plate` is what goes on the message board, because that is the one part the two scenes do
// not agree on: standby says what is coming up, the draft says what is being played for.
// Everything else - who, in which colour, under which marks - is the show's, and identical.

const { band, colours } = spec
const { team, plate, arm } = band

// the screen the band is measured against, for a scene that has no numbers of its own
export const SCREEN = spec.screen

// "#5cbcec" -> "92 188 236", so the stylesheet can say rgb(var(--team-rgb) / .58)
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

export const BAND_VARS = {
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
  '--rim': colours.rim,
  '--base-top': colours.base_top,
  '--base-bottom': colours.base_bottom,
  '--smoke': colours.smoke,
  '--blue-rgb': rgbOf(colours.blue),
  '--red-rgb': rgbOf(colours.red),
}

const SIDES = ['blue', 'red']

export default function MatchupBand({ plate: plateContent }) {
  // wide, then square, then nothing - see the arms below
  const wide = useVelcroValue('variables.event.logo_wide')
  const square = useVelcroValue('variables.event.logo')
  const tournament = wide ? 'event.logo_wide' : square ? 'event.logo' : ''

  return (
    <div className="fcjh-matchup">
      {/* the board first, so the containers sit over it as the old one had them */}
      <div className="fcjh-matchup-plate">{plateContent}</div>

      {SIDES.map((side) => (
        <div className={`fcjh-matchup-team ${side}`} key={side}>
          <Variable name={`${side}.name`} fallback="" fit />
        </div>
      ))}

      <div className="fcjh-matchup-vs">
        <span>VS</span>
      </div>

      {/* The broadcaster's mark on the left, the tournament's on the right - the old board's
          arrangement with the game's logo replaced (user, 2026-10-22). Either can be left
          unset, and Image then draws nothing at all rather than an empty box.

          The tournament's is the WIDE one where there is one: wide, then square, then
          nothing (user, 2026-10-23), the same waterfall the scores screen uses. An arm is
          576 x 103, which is the shape the wide logo is drawn for; the square one belongs in
          Blizzard's hexagon and is only the fallback here. */}
      <div className="fcjh-matchup-arm left">
        <Image name="event.broadcaster" alt="" fit="contain" />
      </div>
      <div className="fcjh-matchup-arm right">
        {tournament ? <Image name={tournament} alt="" fit="contain" /> : null}
      </div>
    </div>
  )
}
