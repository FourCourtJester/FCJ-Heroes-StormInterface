import { Field, ImagePicker, Panel, Row, Toggle } from '@single-studio/core/control'

// The tournament: the two tabs' words, the marks the graphics carry, which of them are on
// air, and who won.
//
// The tabs are generic information panels - what goes in them is yours. "Division 1" and
// "Game 3 of 5" are only what they were drawn for. Leave either blank and that tab is not
// drawn at all, rather than showing as an empty lit container.
//
// TWO TOURNAMENT LOGOS, because one shape cannot do both jobs (user, 2026-10-23). The SQUARE
// one goes over Blizzard's hexagon in the game scene, which is a hexagon - an oblong mark
// put in it is either squashed or cropped. The WIDE one goes in the top right corner, where
// the room is 204 x 50 and a square mark would waste it. Both are the same tournament; which
// is wanted is a property of the hole, not of the show.
//
// `fcjh-picker-free` takes the pickers off the column cap so they scale with the line.
// Do NOT give them a content width: a picker is as wide as the longest key in the image
// library, so sizing by content hands the layout to the operator's filenames.
//
// THE SWITCHES live here now, under the marks they turn on, rather than in an Options panel
// of their own. Each takes its whole graphic off rather than leaving an empty plate on air.
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
      <Row>
        <ImagePicker
          name="event.broadcaster"
          label="Broadcaster"
          className="fcjh-picker-free"
        />
        <ImagePicker name="event.logo" label="Tournament (square)" className="fcjh-picker-free" />
        <ImagePicker
          name="event.logo_wide"
          label="Tournament (wide)"
          className="fcjh-picker-free"
        />
      </Row>
      <Row>
        <Toggle name="corner.broadcaster" label="Broadcaster corner" />
        <Toggle name="tournament" label="Hex logo" />
        <Toggle name="corner.tournament" label="Tournament corner" />
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
