import { Field, Panel, ResetButton, Row, Toggle } from '@single-studio/core/control'

// The tournament: the two tabs' words, and who won.
//
// THE SERIES LENGTH is not here. It came over from Teams and moved on again the same day, to a
// Series panel of its own with the map draft (user, 2026-10-27).
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
//
// THE WINNER IS THE SCORES SCREEN'S ONLY. For one afternoon it also marked the latest game's
// map won and added the point; that was scrapped (user, 2026-10-27: "we will scrap any kind of
// automatic stamping of a winner"). A map's result is the Series panel's Blue Win / Red Win,
// and the score is the Teams panel's steppers.
//
// RESET WINNER sits on the section's heading (user, 2026-10-27), so the scores screen can be
// emptied without hunting for the lit button. It asks first, as every reset on this board
// does: it takes the winner off air.
const WINNER = ['toggles.winner.blue', 'toggles.winner.red']

export default function Event() {
  return (
    <Panel title="Tournament" collapsible>
      <Row>
        <Field name="division" label="Left tab" placeholder="Division 1" />
        <Field name="game" label="Right tab" placeholder="Game 3 of 5" />
      </Row>
      <Row>
        <Toggle name="colourblind" label="Colour-blind mode" />
      </Row>

      {/* the rule and its heading wear the Panel title's own classes, so the section reads
          as part of the board rather than as something bolted on */}
      <hr className="border-0 border-t border-slate-700/60" />
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-semibold tracking-wide text-slate-400 uppercase">
          Score Screen Winner
        </span>
        <ResetButton label="winner" paths={WINNER} size="sm" />
      </div>
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
