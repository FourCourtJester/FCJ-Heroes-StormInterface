import spec from '../generated/scores.json'
import './sky.css'

// The sky: Blizzard's Nexus plate with stars, dust and comets moving over it. The scores
// screen shows it through four windows round Blizzard's stats panel; the Backdrop source
// shows it whole, under the series screen (user, 2026-10-27: "the Score animated background,
// but you know, minus the giant hole in the middle").
//
// One sky, so the two cannot drift apart. Its numbers are the scores screen's (scores.json
// `sky`) because the horizon is: the plate's lit floor starts at the stats panel's foot.
//
// It is a full screen whatever holds it, and absolutely placed, so a window can push it back
// to line it up.

const [SCREEN_W, SCREEN_H] = spec.screen
const { sky, colours } = spec

// "#5cbcec" -> "92 188 236", so the stylesheet can say rgb(var(--star-rgb) / .8)
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

const SKY_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--horizon': `${sky.horizon}px`,
  '--comet-fade': `${sky.comet_fade}px`,
  '--star-rgb': rgbOf(colours.text),
}

export default function Sky() {
  return (
    <div className="fcjh-sky" style={SKY_VARS}>
      {/* The comets are in a field of their own because the field carries the mask that
          stops them at the horizon - a comet crossing the lit floor reads as a streak ON the
          ground (user, 2026-10-23).

          Their delays are deliberate, not random: a comet must be at the same point in its
          journey in every copy of the sky, or it would tear at a seam. */}
      <div className="fcjh-comet-field">
        <i className="fcjh-comet one" />
        <i className="fcjh-comet two" />
        <i className="fcjh-comet three" />
      </div>
    </div>
  )
}
