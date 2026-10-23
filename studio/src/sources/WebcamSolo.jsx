import { useVelcroValue } from '@single-studio/core'
import { Scene, Variable } from '@single-studio/core/source'

import spec from '../generated/webcam.json'
import './webcams.css'

// The one-camera frame: the same border, drawn once and centred.
//
// A separate browser source rather than a switch on the two-camera one, because the choice
// belongs to an OBS scene and not to the show: a desk segment and a solo-host segment are two
// scenes that may both be loaded, and a toggle would change them together. Put this source in
// the scene that has one camera and the pair in the scene that has two (user, 2026-10-23).
//
// It shows whoever is in the LEFT slot on the board, so a solo host is just the left cam with
// nobody beside them - there is no third name to keep in step.
//
// Add to OBS as a Browser source pointed at #/source/webcam-solo, 1920 x 1080, over the
// standby source, with the camera underneath it and Filters -> Image Mask/Blend ->
// Alpha Mask (Alpha Channel) pointed at /masks/cam_mask_left.png - the same mask the pair
// uses, scaled up. Every window is the same shape, so there is only one per lean.

const [SCREEN_W, SCREEN_H] = spec.screen
const { cam, solo, plate, colours } = spec
const [CHAMFER_W, CHAMFER_H] = cam.chamfer_pct

// see Webcams.jsx: a URL flag, not a board switch
const FILL = new URLSearchParams(
  window.location.search + '&' + window.location.hash.split('?')[1],
).has('fill')

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--solo-w': `${solo.w}px`,
  '--solo-h': `${solo.h}px`,
  '--solo-top': `${solo.top}px`,
  '--solo-left': `${solo.left}px`,
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
  '--plate-smoke': colours.plate_smoke,
}

export default function WebcamSolo() {
  const name = useVelcroValue('variables.cam.left.name')
  const social = useVelcroValue('variables.cam.left.social')

  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className={`fcjh-cams${FILL ? ' fill' : ''}`} style={SCENE_VARS}>
        <div className="fcjh-cam solo">
          <div className="fcjh-cam-window" />

          {name || social ? (
            <div className="fcjh-cam-plate">
              <Variable className="who" name="cam.left.name" fallback="" fit />
              <Variable className="at" name="cam.left.social" fallback="" fit />
            </div>
          ) : null}
        </div>
      </div>
    </Scene>
  )
}
