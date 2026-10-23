import { Panel, Toggle } from '@single-studio/core/control'

// What this broadcast shows at all, as against what it says: the pieces not every tournament
// uses. Each one takes its whole graphic off rather than leaving an empty plate on air - no
// bans means no tiles, not six empty slots under the team names.
//
// Last on the board, because it is set once at the start of a show and left alone, while
// everything above it changes between games.
//
// Each Toggle writes its own "Show"/"Hide" into the button, so the label here is the thing,
// not the verb. New options go here as the graphics grow.
export default function Options() {
  return (
    <Panel title="Options" collapsible>
      {/* <Toggle name="bans" label="Bans" /> shelved with the bans themselves (2026-10-22) */}
      <Toggle name="tournament" label="Tournament logo" />
    </Panel>
  )
}
