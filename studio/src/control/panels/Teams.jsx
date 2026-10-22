import { Field, ImagePicker, Panel, Row } from '@single-studio/core/control'

// A team's name and its logo. Leave the logo unset and that side's logo plate goes:
// the name plate runs on to the level wing, which is the no-logo tournament.
export default function Teams() {
  return (
    <Panel title="Teams">
      <Row>
        <Field name="blue.name" label="Blue" placeholder="Blue team" />
        <ImagePicker name="blue.logo" label="Blue logo" className="md:col-auto" />
      </Row>
      <Row>
        <Field name="red.name" label="Red" placeholder="Red team" />
        <ImagePicker name="red.logo" label="Red logo" className="md:col-auto" />
      </Row>
    </Panel>
  )
}
