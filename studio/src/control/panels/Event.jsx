import { Field, Panel, Row, Select, Toggle } from '@single-studio/core/control'

// The tournament: the two tabs' words, the series length, and who won.
//
// THE SERIES came over from Teams (user, 2026-10-27: "its, you know, a tournament setting"),
// under the tabs ("Let's put it under Left/Right tab").
// It is the number of pips a side, which is what the graphic draws: a best of five is three.
// Clearing the teams still leaves it alone.
//
// The tabs are generic information panels - what goes in them is yours. "Division 1" and
// "Game 3 of 5" are only what they were drawn for. Leave either blank and that tab is not
// drawn at all, rather than showing as an empty lit container.
//
// THE MARKS ARE NOT HERE any more. The broadcaster's and the tournament's logos, and the
// three switches that put them on air, moved to a Logos panel of their own on 2026-10-26,
// when each of the two gained a second picture: four pickers is more than this panel could
// hold without the tab fields losing their place in it. They were never tournament settings
// anyway - they are the show's furniture.
//
// The colour-blind switch stayed, because it is about neither the marks nor one graphic.
//
// THE WINNER is a pair of grouped toggles rather than a dropdown, so exactly one can be lit.
// Two reasons it earns the room: it is the one control on this board that goes to air the
// instant it is pressed - a Toggle writes immediately where a Field stages until save - and
// at the moment it is used, live with a result just called, the state has to be readable at
// a glance rather than by opening a menu. Neither lit is the resting state, and it is
// reachable: pressing the lit one turns it off again.
//
// `fcjh-won` paints each lit button its own side's colour. The framework lights every toggle
// in one accent, which happens to be blue, so a lit "Red" looked exactly like a lit "Blue"
// and only the word told them apart.
export default function Event() {
  return (
    <Panel title="Tournament" collapsible>
      <Row>
        <Field name="division" label="Left tab" placeholder="Division 1" />
        <Field name="game" label="Right tab" placeholder="Game 3 of 5" />
      </Row>
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
        <Toggle name="colourblind" label="Colour-blind mode" />
      </Row>

      {/* the rule and its heading wear the Panel title's own classes, so the section reads
          as part of the board rather than as something bolted on */}
      <hr className="border-0 border-t border-slate-700/60" />
      <span className="text-sm font-semibold tracking-wide text-slate-400 uppercase">
        Score Screen Winner
      </span>
      <Row>
        <Toggle name="winner.blue" group="winner" className="fcjh-won blue">
          Blue
        </Toggle>
        <Toggle name="winner.red" group="winner" className="fcjh-won red">
          Red
        </Toggle>
      </Row>
    </Panel>
  )
}
