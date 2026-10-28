import { Scene } from '@single-studio/core/source'

import Sky from '../components/Sky'
import spec from '../generated/scores.json'

// The scores screen's moving sky, whole: no hole, nothing on it (user, 2026-10-27: "the Score
// animated background, but you know, minus the giant hole in the middle").
//
// Made for the series screen, and drawn as plainly as that so it can go under anything else.
//
// Add to OBS as a Browser source pointed at #/source/backdrop, 1920 x 1080, at the bottom of
// the scene - content/guides/obs.md has the series scenes.

const [SCREEN_W, SCREEN_H] = spec.screen

export default function Backdrop() {
  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div style={{ position: 'relative', width: SCREEN_W, height: SCREEN_H, overflow: 'hidden' }}>
        <Sky />
      </div>
    </Scene>
  )
}
