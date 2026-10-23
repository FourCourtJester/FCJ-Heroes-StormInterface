// import Bans from './panels/Bans'   // shelved until after the first user pass
import Cams from './panels/Cams'
import Event from './panels/Event'
import Options from './panels/Options'
import Standby from './panels/Standby'
import Teams from './panels/Teams'

// The operator's board for the FCJ Heroes broadcast graphics.
//
// Panels live in ./panels, one per file. Buttons write immediately; anything you type stages
// until you save, so a half-typed name never reaches air.
//
// Order is how often a thing changes: teams and bans move between games, the tournament and
// the standby screen between segments, the webcams once a show, and Options is set once and
// left.
//
// Logos and ban portraits come from the studio's own image library - the magnifier on each
// picker opens it. Nothing here needs a file path.
export default function Control() {
  return (
    <>
      <Teams />
      {/* <Bans /> shelved until after the first user pass (user, 2026-10-22) */}
      <Event />
      <Standby />
      <Cams />
      <Options />
    </>
  )
}
