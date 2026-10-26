import { useEffect } from 'react'

// import Bans from './panels/Bans'   // shelved until after the first user pass
import { checkDevCss } from '../studio/devCssGuard'
import Cams from './panels/Cams'
import Event from './panels/Event'
import Help from './panels/Help'
import Logos from './panels/Logos'
import Standby from './panels/Standby'
import Teams from './panels/Teams'

// The operator's board for the FCJ Heroes broadcast graphics.
//
// Panels live in ./panels, one per file. Buttons write immediately; anything you type stages
// until you save, so a half-typed name never reaches air.
//
// Order is the running order of a show, not how often a thing changes (user, 2026-10-23):
// you come up on the standby screen, you are on camera, then the teams and the tournament
// around the match itself.
//
// There is no Options panel any more. It held one switch, for the tournament's logo, and a
// panel of one switch is a panel you have to open to find out it has nothing in it. The
// switches now sit under the thing they turn on, which is where you are already looking.
//
// The marks moved out of Tournament into a Logos panel of their own on 2026-10-26, when
// each of the two gained a second picture. They sit late because they are set once at the
// start of a cast: the running order is what you touch as the show goes, not everything the
// show needs.
//
// Logos and ban portraits come from the studio's own image library - the magnifier on each
// picker opens it. Nothing here needs a file path.
export default function Control() {
  // development only, and it compiles out of the build: a dev server that has auto-restarted
  // can serve CSS that is neither the old file nor the new one, twice on 2026-10-23, and
  // nothing warns. The board is where it is checked because the board is never on air.
  useEffect(checkDevCss, [])

  return (
    <>
      <Standby />
      <Cams />
      <Teams />
      {/* <Bans /> shelved until after the first user pass (user, 2026-10-22) */}
      <Event />
      <Logos />
      <Help />
    </>
  )
}
