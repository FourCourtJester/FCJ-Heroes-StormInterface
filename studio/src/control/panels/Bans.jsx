import { ImagePicker, Panel, Row } from '@single-studio/core/control'

import spec from '../../generated/topbar.json'

// The game's bans, under each team's name. Three tiles a side, the innermost first - the one
// nearest the middle of the screen. A tile with nothing picked shows as an empty slot, so a
// draft can fill as it happens.
//
// Off by default: not every tournament shows bans. The toggle that takes the whole row off -
// tiles and all - is in Options, with the rest of what a broadcast can turn on and off.
//
// The portraits come from the studio's image library. There is no hero roster here: whatever
// you put in the library is what the pickers offer.
const SLOTS = [...Array(spec.bans.tiles_per_side).keys()]

export default function Bans() {
  return (
    <Panel title="Bans" collapsible>
      {SLOTS.map((i) => (
        <Row key={i}>
          <ImagePicker name={`blue.bans.${i}`} label={`Blue ban ${i + 1}`} />
          <ImagePicker name={`red.bans.${i}`} label={`Red ban ${i + 1}`} />
        </Row>
      ))}
    </Panel>
  )
}
