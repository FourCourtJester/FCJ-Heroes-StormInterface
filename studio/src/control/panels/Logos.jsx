import { ImagePicker, Panel, Row, Toggle } from '@single-studio/core/control'

// The marks a show carries: the broadcaster's and the tournament's, a square and a wide of
// each, and the switches for the three places they go on air.
//
// A PANEL OF THEIR OWN (user, 2026-10-26). They were three pickers wedged into the bottom of
// the Tournament panel, beside the tab words and the winner. They are not tournament
// settings - they are the show's furniture, set once at the start of a cast and then left
// alone - and four of them in a row is more than that panel could hold without the division
// and game fields losing their place in it.
//
// TWO PICTURES EACH, square and wide, because one shape cannot do both jobs. The SQUARE one
// goes over Blizzard's hexagon in the game scene, which is a hexagon: an oblong mark in it is
// squashed or cropped. The WIDE one goes in a corner 204 x 50, in the standby band's arms,
// and in the lockup under the matchup - all places a square mark would leave two thirds of
// the room empty.
//
// NEITHER IS REQUIRED. Each graphic takes the shape its hole is drawn for and falls back to
// the other, so an organisation with only one picture still gets a sensible result, and one
// with both gets the right one everywhere (components/marks.js). A mark left unset is drawn
// as nothing at all rather than as an empty lit container.
//
// Tall marks are not a case yet. If one turns up it would want its own slot rather than
// being squeezed into "square" - a 1:3 crest and a 1:1 badge want different holes - but
// nobody has asked for one and a slot nobody fills is a slot everybody wonders about.
//
// `fcjh-picker-free` takes the pickers off the column cap so they scale with the line. Do
// NOT give them a content width: a picker is as wide as the longest key in the image
// library, so sizing by content hands the layout to the operator's filenames.
//
// THE SWITCHES ARE SHOW-WIDE (user, 2026-10-26: "the same toggle will edit
// matchup/draft/game/scoreboard"). One switch per mark, read by the game bar, the matchup,
// the draft and the scores alike, so a broadcaster taken off is off everywhere rather than in
// the one scene somebody remembered.
//
// And the graphics CLOSE UP around what is left. Take the broadcaster off a lockup and the
// tournament's mark centres, taking the x with it; take both off and there is no lockup at
// all. That needs the switch to reach the layout rather than just hide a box, which is why
// marks.js owns it (see useVisibleMark) instead of a `Toggle` wrapping each mark.
//
// THE HEX IS ITS OWN THING. Blizzard's hexagon is the game's own furniture wearing our mark,
// not one of our overlays, so it keeps a switch to itself and is unaffected by taking the
// tournament's marks off.
//
// The colour-blind switch stayed on the Tournament panel: it is not about these pictures.
//
// Logos come from the studio's own image library - the magnifier on each picker opens it.
export default function Logos() {
  return (
    <Panel title="Logos" collapsible>
      <Row>
        <ImagePicker
          name="event.broadcaster"
          label="Broadcaster (square)"
          className="fcjh-picker-free"
        />
        <ImagePicker
          name="event.broadcaster_wide"
          label="Broadcaster (wide)"
          className="fcjh-picker-free"
        />
      </Row>
      <Row>
        <ImagePicker name="event.logo" label="Tournament (square)" className="fcjh-picker-free" />
        <ImagePicker
          name="event.logo_wide"
          label="Tournament (wide)"
          className="fcjh-picker-free"
        />
      </Row>
      <Row>
        <Toggle name="show.broadcaster" label="Broadcaster" />
        <Toggle name="show.tournament" label="Tournament" />
        <Toggle name="show.hex" label="Hex logo" />
      </Row>
    </Panel>
  )
}
