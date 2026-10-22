import { Field, ImagePicker, Panel, Row } from '@single-studio/core/control'

// The tournament: the two tabs' words and the logo over Blizzard's hexagon.
//
// The tabs are generic information panels - what goes in them is yours. "Division 1"
// and "Game 3 of 5" are only what they were drawn for.
export default function Event() {
  return (
    <Panel title="Tournament">
      <Row>
        <Field name="division" label="Left tab" placeholder="Division 1" />
        <Field name="game" label="Right tab" placeholder="Game 3 of 5" />
      </Row>
      <ImagePicker name="event.logo" label="Tournament logo" />
    </Panel>
  )
}
