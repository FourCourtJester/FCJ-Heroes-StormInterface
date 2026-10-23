import { Field, ImagePicker, Panel, Row } from '@single-studio/core/control'

// The tournament: the two tabs' words, and the two marks the graphics carry.
//
// The tabs are generic information panels - what goes in them is yours. "Division 1"
// and "Game 3 of 5" are only what they were drawn for.
//
// The tournament's logo goes over Blizzard's hexagon in the game scene and on the right
// arm of the standby band. The broadcaster's own mark sits on the standby band's left arm,
// where the old board had the game's logo (user, 2026-10-22). Leave either unset and that
// arm carries no picture.
export default function Event() {
  return (
    <Panel title="Tournament" collapsible>
      <Row>
        <Field name="division" label="Left tab" placeholder="Division 1" />
        <Field name="game" label="Right tab" placeholder="Game 3 of 5" />
      </Row>
      <Row>
        <ImagePicker name="event.logo" label="Tournament logo" />
        <ImagePicker name="event.broadcaster" label="Broadcaster logo" />
      </Row>
    </Panel>
  )
}
