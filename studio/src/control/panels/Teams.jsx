import { Field, ImagePicker, Panel, ResetButton, Row, Stepper, SwapButton } from '@single-studio/core/control'

// Teams: everything about who is on screen, in one panel. The series length is on the
// Tournament panel (user, 2026-10-27: "its, you know, a tournament setting").
//
// A Row shares a line once the board is wide enough and stacks in a slim dock, so each team
// reads as one line - name, logo, games won - and falls apart in order when there is no room
// `sm:col-auto` keeps the WINS stepper at its own width from sm up - it is a fixed 160px
// control, so there is nothing for it to scale into. The logo picker is not: it scales with
// the line and is capped only where the line is tight, which src/css/index.css does by
// breakpoint rather than by a class here.
//
// Leave a logo unset and that side's logo plate goes, the name plate running on to the
// level wing - the no-logo tournament.
//
// Swap and Clear live in the header, so they are reachable while the panel is folded and out
// of the way of the names while it is open (user, 2026-10-23). Both ask before they fire -
// one mis-aimed click here is a wrong scoreboard in front of an audience, with no undo.
//
// Clear leaves the series alone: a new match is new teams at 0-0, but it is usually the same
// best-of, and a format that quietly reset itself between games would be found out on air.
//
// IT DOES CLEAR THE WINNER, which lives on the Tournament panel now (user, 2026-10-23). The
// control moved; what it means did not. A winner belongs to the match that was just played,
// so starting a new one while the last one's result is still lit is the fault worth guarding
// against - and an operator clearing the teams has plainly started a new one. It goes through
// `paths` rather than `names` because it is a toggle: `names` reaches `variables`, and these
// two live under `toggles`. Swap does not take them. It works by cutting its list in half and
// exchanging the pairs, and "won" has no opposite number to exchange with - which side won is
// not a property of a side. Sides are picked before a game and the winner after it, so the
// two do not meet; if you ever do swap after a result, re-pick the winner.
const SIDES = ['blue.name', 'blue.logo', 'blue.wins', 'red.name', 'red.logo', 'red.wins']
const WINNER = ['toggles.winner.blue', 'toggles.winner.red']

export default function Teams() {
  return (
    <Panel
      title="Teams"
      collapsible
      actions={
        <>
          <SwapButton label="Swap sides" names={SIDES} size="sm" />
          <ResetButton label="teams" names={SIDES} paths={WINNER} size="sm" />
        </>
      }
    >
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
