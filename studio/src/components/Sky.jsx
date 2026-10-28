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
//
// `won` is the side the scores screen has called, or nothing: the glow on the horizon takes
// that side's colour (user, 2026-10-28). The Backdrop passes none, so the series screen's sky
// stays neutral.

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
  // the scores screen sets --blue-rgb and --red-rgb itself, colour-blind or not; these are
  // what the glow falls back on anywhere else
  '--sky-blue-rgb': rgbOf(colours.blue),
  '--sky-red-rgb': rgbOf(colours.red),
  '--glow-x': `${sky.glow.x}px`,
  '--glow-w': `${sky.glow.w}px`,
  '--glow-h': `${sky.glow.h}px`,
  '--rays-r': `${sky.glow.rays}px`,
  '--glow-twin-y': `${sky.glow.twin_y}px`,
  '--glint-cycle': `${sky.glint_cycle}s`,
  '--meteor-cycle': `${sky.meteor_cycle}s`,
}

// each glint a fixed share of the cycle after the last, so they take turns and every copy of
// the sky agrees which one is lit
const GLINTS = sky.glints.map(([x, y], i) => ({
  left: `${x}px`,
  top: `${y}px`,
  animationDelay: `${((i * sky.glint_cycle) / sky.glints.length).toFixed(2)}s`,
}))

export default function Sky({ won = '' }) {
  return (
    <div className={`fcjh-sky${won ? ` won-${won}` : ''}`} style={SKY_VARS}>
      {/* The glow on the horizon and the rays over it. The glow always lights the floor;
          a winner's tint goes over it and recolours it, faded in rather than the glow
          recoloured, since a gradient's colour does not transition and opacity does in
          every CEF. Siblings, not children of one box: a box round them would make them
          blend with each other instead of with the sky. */}
      <div className="fcjh-ray-field">
        <i className="fcjh-rays" />
      </div>
      <i className="fcjh-glow neutral" />
      <i className="fcjh-glow blue" />
      <i className="fcjh-glow red" />
      <i className="fcjh-glow blue lift" />
      <i className="fcjh-glow red lift" />
      {/* the winner's glow mirrored on the panel's top edge - the floor is already blue, so
          blue alone reads as the floor; the twin is on dark sky, so it is the team's colour only */}
      <i className="fcjh-glow blue lift twin" />
      <i className="fcjh-glow red lift twin" />

      {GLINTS.map((style, i) => (
        <i key={i} className="fcjh-glint" style={style} />
      ))}

      {/* The comets are in a field of their own because the field carries the mask that
          stops them at the horizon - a comet crossing the lit floor reads as a streak ON the
          ground (user, 2026-10-23).

          Their delays are deliberate, not random: a comet must be at the same point in its
          journey in every copy of the sky, or it would tear at a seam. */}
      <div className="fcjh-comet-field">
        <i className="fcjh-comet one" />
        <i className="fcjh-comet two" />
        <i className="fcjh-comet three" />
        <i className="fcjh-meteor" />
      </div>
    </div>
  )
}
