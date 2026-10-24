import { Countdown, CountdownTo, Field, Panel, Row } from '@single-studio/core/control'

// The standby screen: what the stream shows when the game isn't on.
//
// Two ways to set the clock, one clock. Both write the same timer, so whichever you start
// replaces whatever was running and the screen never has two (user, 2026-10-22):
//
//   Back at   a time of day - 19:30. Rolls to tomorrow by itself if it has already passed.
//   Back in   a length - 5:00, or 90, or 1:02:03.
//
// "Back at" is the one to reach for if the break might be interrupted: the source is shut
// down whenever its scene is hidden, so a length restarts every time you come back to it,
// while a target time survives that untouched. "Back in" is for when you don't know the
// wall-clock time you are aiming at, which is most unplanned breaks.
//
// The art behind it is the image library's `slides/` group: file pictures there and they
// play, shuffled, nine seconds each, drifting as they go. Nothing to set here.
//
// "Message" is the line over the matchup band - "coming up next", "previous match", whatever
// the segment is. The band is its own browser source (#/source/matchup) rather than part of
// this screen, so the field is named for where it started rather than where it is drawn.
//
// The two logos are the ones in Tournament: this screen shows the same marks rather than
// keeping a second copy of them. Who is playing comes from Teams.
export default function Standby() {
  return (
    <Panel title="Standby" collapsible>
      <Field name="standby.message" label="Message" placeholder="Coming up next" />
      <Field name="standby.label" label="Clock label" placeholder="Resuming" />
      {/* no col-auto on these: both controls already grow their input with their cell, and
          with nothing else on the line to take the slack it would only leave a hole at the
          end and make two matched clocks different sizes (user, 2026-10-23) */}
      <Row>
        <CountdownTo name="standby.resume" label="Back at" />
        <Countdown name="standby.resume" label="Back in" />
      </Row>
    </Panel>
  )
}
