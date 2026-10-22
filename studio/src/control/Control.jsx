import Bans from './panels/Bans'
import Event from './panels/Event'
import Series from './panels/Series'
import Teams from './panels/Teams'

// The operator's board for the FCJ Heroes top bar.
//
// Panels live in ./panels, one per file. Buttons write immediately; anything you type
// stages until you save, so a half-typed name never reaches air.
//
// Logos and ban portraits come from the studio's own image library - the magnifier on
// each picker opens it. Nothing here needs a file path.
export default function Control() {
  return (
    <>
      <Teams />
      <Series />
      <Bans />
      <Event />
    </>
  )
}
