import { Panel, Row, Select, Stepper, SwapButton } from '@single-studio/core/control'

// The series score, as hexagon pips either side of the bar. "Series" sets how many
// pips a side, which is what the graphic draws; the value is that number, so a best
// of five is three.
export default function Series() {
  return (
    <Panel title="Series">
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
        <Stepper name="blue.wins" label="Blue wins" />
        <Stepper name="red.wins" label="Red wins" />
      </Row>
      <SwapButton label="Swap sides" names={['blue.name', 'blue.logo', 'blue.wins', 'red.name', 'red.logo', 'red.wins']} />
    </Panel>
  )
}
