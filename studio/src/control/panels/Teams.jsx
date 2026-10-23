import { Field, ImagePicker, Panel, ResetButton, Row, Select, Stepper, SwapButton } from '@single-studio/core/control'

// Teams, and the series they are playing: everything about who is on screen, in one panel.
//
// A Row shares a line once the board is wide enough and stacks in a slim dock, so each team
// reads as one line - name, logo, games won - and falls apart in order when there is no room
// `sm:col-auto` keeps the WINS stepper at its own width from sm up - it is a fixed 160px
// control, so there is nothing for it to scale into. The logo picker is not: it scales with
// the line and is capped only where the line is tight, which src/css/index.css does by
// breakpoint rather than by a class here.
//
// "Series" is the number of pips a side, which is what the graphic draws: a best of five is
// three. Leave a logo unset and that side's logo plate goes, the name plate running on to the
// level wing - the no-logo tournament.
//
// Swap and Clear live in the header, so they are reachable while the panel is folded and out
// of the way of the names while it is open (user, 2026-10-23). Clear takes the six values that
// say who is playing and leaves the series alone: a new match is new teams at 0-0, but it is
// usually the same best-of, and a format that quietly reset itself between games would be
// found out on air. Both ask before they fire - one mis-aimed click here is a wrong scoreboard
// in front of an audience, with no undo.
const TEAMS = ['blue.name', 'blue.logo', 'blue.wins', 'red.name', 'red.logo', 'red.wins']

export default function Teams() {
  return (
    <Panel
      title="Teams"
      collapsible
      actions={
        <>
          <SwapButton label="Swap sides" names={TEAMS} size="sm" />
          <ResetButton label="teams" names={TEAMS} size="sm" />
        </>
      }
    >
      <Select
        name="series.pips"
        label="Series"
        options={[
          { label: 'Best of 3', value: '2' },
          { label: 'Best of 5', value: '3' },
          { label: 'Best of 7', value: '4' },
        ]}
      />
      <Row>
        <Field name="blue.name" label="Blue" placeholder="Blue team" />
        <ImagePicker name="blue.logo" label="Blue logo" />
        <Stepper name="blue.wins" label="Blue wins" className="sm:col-auto" />
      </Row>
      <Row>
        <Field name="red.name" label="Red" placeholder="Red team" />
        <ImagePicker name="red.logo" label="Red logo" />
        <Stepper name="red.wins" label="Red wins" className="sm:col-auto" />
      </Row>
    </Panel>
  )
}
