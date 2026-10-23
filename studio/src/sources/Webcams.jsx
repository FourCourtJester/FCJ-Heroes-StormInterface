import { useVelcroValue } from '@single-studio/core'
import { Scene, Variable } from '@single-studio/core/source'

import spec from '../generated/webcam.json'
import './webcams.css'

// The webcam frames: two borders and two names, and nothing else.
//
// This source draws no video. OBS puts each camera UNDERNEATH it and this lays the chrome and
// the name over the top (user, 2026-10-22), which is what lets a camera be nudged, scaled or
// swapped for a different one without any art being re-cut. It is its own browser source so it
// can sit over the standby screen in OBS, and its windows hang in that screen's free middle -
// under the countdown bug, over the band - so the two stack without either having to move.
//
// Add to OBS as a Browser source pointed at #/source/webcams, 1920 x 1080, over the standby
// source. Then, per camera:
//
//   1. put the camera under this source and size it to the window (the places are below, and
//      ../generated/guide.png draws them if you would rather line it up by eye);
//   2. add Filters -> Image Mask/Blend, "Alpha Mask (Alpha Channel)", and point it at
//      /masks/cam_mask_left.png or /masks/cam_mask_right.png - they ship with the site,
//      drawn at the largest window, and OBS scales them onto whichever one you are
//      filling.
//
// Step 2 is not optional. The windows are cut at the plates' angle, so a camera left as a
// rectangle pokes its corners out past the chrome.

const [SCREEN_W, SCREEN_H] = spec.screen
const { cam, plate, colours } = spec
const [CHAMFER_W, CHAMFER_H] = cam.chamfer_pct

// `?fill` paints the windows a flat colour so the frames can be screenshotted with no camera
// behind them (user, 2026-10-23). A URL flag and not a board switch on purpose: a switch could
// be left on, and on air a filled window is an opaque rectangle over somebody's face.
const FILL = new URLSearchParams(
  window.location.search + '&' + window.location.hash.split('?')[1],
).has('fill')

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--cam-w': `${cam.w}px`,
  '--cam-h': `${cam.h}px`,
  '--cam-top': `${cam.top}px`,
  '--cam-left': `${cam.left}px`,
  '--cam-right': `${cam.right}px`,
  '--chamfer-pw': `${CHAMFER_W}%`,
  '--chamfer-ph': `${CHAMFER_H}%`,
  '--plate-h': `${plate.h}px`,
  '--plate-gap': `${plate.gap}px`,
  '--plate-pad': `${plate.pad}px`,
  '--plate-point': `${plate.point}px`,
  '--name': `${plate.name}px`,
  '--social': `${plate.social}px`,
  '--rim': colours.rim,
  '--text': colours.text,
  '--smoke': colours.smoke,
  '--plate-smoke': colours.plate_smoke,
}


const SIDES = ['left', 'right']

function Cam({ side }) {
  // nobody named, no bar: an empty smoke bar under a window says less than nothing, and a
  // stylesheet cannot ask whether its own text is empty
  const name = useVelcroValue(`variables.cam.${side}.name`)
  const social = useVelcroValue(`variables.cam.${side}.social`)

  return (
    <div className={`fcjh-cam ${side}`}>
      {/* the window is a hole: the frame is drawn round it and the camera shows through
          from the OBS source beneath */}
      <div className="fcjh-cam-window" />

      {name || social ? (
        <div className="fcjh-cam-plate">
          <Variable className="who" name={`cam.${side}.name`} fallback="" fit />
          <Variable className="at" name={`cam.${side}.social`} fallback="" fit />
        </div>
      ) : null}
    </div>
  )
}

export default function Webcams() {
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className={`fcjh-cams${FILL ? ' fill' : ''}`} style={SCENE_VARS}>
        {SIDES.map((side) => (
          <Cam key={side} side={side} />
        ))}
      </div>
    </Scene>
  )
}
