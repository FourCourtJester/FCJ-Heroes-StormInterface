import { useVelcroValue } from '@single-studio/core'
import { Image, Scene, Variable } from '@single-studio/core/source'

import { useVisibleMark } from './marks'
import spec from '../generated/series.json'
import webcam from '../generated/webcam.json'
import frameLeft from '../generated/cam_frame_left.svg'
import frameRight from '../generated/cam_frame_right.svg'
import '../sources/series.css'

/**
 * The series screen's top half, for a number of cameras: the frames, the names in them and the
 * two marks. Each count is its own source (SeriesTwoCams, SeriesOneCam, SeriesNoCams) - the
 * choice belongs to an OBS scene, whose camera captures sit under these frames, so a switch on
 * the board would change every scene at once (user, 2026-10-27).
 *
 *   two    a camera each side, and between them the tournament's mark over the
 *          broadcaster's, joined by an x
 *   one    the camera on the RIGHT, and the same lockup in the left one's place (user,
 *          2026-10-27: "same vertical stack, but we can put it where the left webcam used to
 *          be")
 *   none   the same lockup lying down, the broadcaster's left and the tournament's right
 *          as on the scores screen, above the cards by the matchup band's distance below them
 *          (user, 2026-10-27: "the *only* scene where we'll go back to horizontal with the X")
 *
 * THE MARKS ANSWER TO THE LOGOS PANEL'S SWITCHES, as every other source's do (user,
 * 2026-10-27): a mark switched off, or with no picture, is not drawn. With two cameras the
 * pair are a lockup and close up as every other collaboration does (user, 2026-10-27: "the
 * same waterfall logic as all the other logo collaborations") - one mark alone takes the
 * middle and the x goes with its partner. Every count wears one lockup; only its direction
 * and its place change.
 *
 * The frames are the webcams' own art, scaled: every window is the same 16:9 shape, so the
 * webcams' masks fit these cameras too - /masks/cam_mask_left.png on the left one,
 * cam_mask_right.png on a right one.
 *
 * `?fill` paints the windows for a screenshot, as the webcams' does.
 */
const [SCREEN_W, SCREEN_H] = spec.screen
const { cam, colours, marks } = spec
const [CHAMFER_W, CHAMFER_H] = cam.chamfer_pct

const FILL = new URLSearchParams(
  window.location.search + '&' + window.location.hash.split('?')[1],
).has('fill')

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--cam-w': `${cam.w}px`,
  '--cam-h': `${cam.h}px`,
  '--cam-top': `${cam.top}px`,
  '--chamfer-w': CHAMFER_W,
  '--chamfer-pw': `${CHAMFER_W}%`,
  '--chamfer-ph': `${CHAMFER_H}%`,
  '--plate-h': `${cam.plate_h}px`,
  '--name': `${cam.name}px`,
  '--social': `${cam.social}px`,
  '--text': colours.text,
  '--plate-smoke': webcam.colours.plate_smoke,
}

/** A camera's frame. `slot` is whose name it carries - the Webcams panel's left or right. */
function Cam({ slot, x, flip }) {
  // nobody named, no strip, as the webcams' bar
  const name = useVelcroValue(`variables.cam.${slot}.name`)
  const social = useVelcroValue(`variables.cam.${slot}.social`)

  return (
    <div className={`fcjh-scam${flip ? ' flip' : ''}`} style={{ left: `${x}px` }}>
      <div className="fcjh-scam-window">
        {name || social ? (
          <div className="fcjh-scam-plate">
            <Variable className="who" name={`cam.${slot}.name`} fallback="" fit />
            <Variable className="at" name={`cam.${slot}.social`} fallback="" fit />
          </div>
        ) : null}
      </div>
      <img src={flip ? frameRight : frameLeft} alt="" />
    </div>
  )
}

/**
 * The marks' lockup. With cameras, the tournament's over the broadcaster's, between two
 * windows or in the left one's place beside one: the scores screen's pair stood on end (user,
 * 2026-10-27: "add the 'X' between them, but vertically"). With none, `row`, it lies down as
 * the scores screen's does - broadcaster left, tournament right, as the matchup band's arms.
 *
 * A fixed box each side of the x, so the x sits on its middle whatever shape the two marks are, and each picture closes on it: the top one bottom bound, the bottom one top
 * bound. Alone, a mark has nothing to close on, so it centres on the middle itself. Wide
 * first, as every wide hole asks (components/marks.js); a square mark is the fallback.
 */
function Lockup({ at, row }) {
  const tournament = useVisibleMark('tournament', 'wide')
  const broadcaster = useVisibleMark('broadcaster', 'wide')
  const [first, second] = row ? [broadcaster, tournament] : [tournament, broadcaster]
  const both = Boolean(first && second)

  if (!first && !second) return null
  return (
    <div
      className={`fcjh-series-lockup${row ? ' row' : ''}${both ? '' : ' lone'}`}
      style={{
        left: `${at.cx}px`,
        top: `${at.cy}px`,
        '--lockup-w': `${at.w}px`,
        '--lockup-h': `${at.h}px`,
        '--x-text': `${at.x_text}px`,
        '--x-gap': `${at.x_gap}px`,
      }}
    >
      {first ? (
        <div className="fcjh-series-lockup-mark first">
          <Image name={first.name} alt="" fit="contain" />
        </div>
      ) : null}
      {both ? <span className="fcjh-series-x">&times;</span> : null}
      {second ? (
        <div className="fcjh-series-lockup-mark second">
          <Image name={second.name} alt="" fit="contain" />
        </div>
      ) : null}
    </div>
  )
}

/** @param {{ cams: 0 | 1 | 2 }} props */
export default function SeriesTop({ cams }) {
  const at = marks[String(cams)]

  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className={`fcjh-series${FILL ? ' fill' : ''}`} style={SCENE_VARS}>
        {cams === 2 ? <Cam slot="left" x={cam.left} /> : null}
        {/* one camera is the solo host, who is the left slot on the board wherever the frame
            stands - the same as the solo webcam - so there is no third name to keep in step */}
        {cams >= 1 ? <Cam slot={cams === 2 ? 'right' : 'left'} x={cam.right} flip /> : null}
        <Lockup at={at.lockup} row={cams === 0} />
      </div>
    </Scene>
  )
}
