import { BoardBar, Stepper } from '@single-studio/core/control'

// The series score in the board's bar, under the top bar and in reach wherever the board is
// scrolled (user, 2026-11-13: "the most important part of the broadcast for most commentators
// is team scores"). `- 0 +  BLUE vs RED  - 0 +`.
//
// The framework's Stepper, on the same values as the Teams panel's WINS steppers, `blue.wins`
// and `red.wins` (user, 2026-11-13: "we want to use Stepper"), so the two are one score: its
// buttons add, so two operators pressing + at once come to +2, and its field takes a typed
// correction. No label of its own - the side's name beside it is the label - and a size
// down, `.fcjh-score-stepper` in src/css/index.css.
//
// BLUE AND RED, NEVER THE TEAMS' NAMES (user, 2026-11-13: "they can be extremely long"). The
// side is what the operator is pressing for, and it is the same width every match.

const Name = ({ children, tint }) => (
  <span className={`text-sm font-semibold tracking-wide uppercase ${tint}`}>{children}</span>
)

export default function ScoreBar() {
  return (
    <BoardBar className="ml-auto">
      <Stepper name="blue.wins" className="fcjh-score-stepper" />
      <Name tint="text-sky-400">Blue</Name>
      <span className="px-1 text-xs font-semibold text-slate-500 uppercase">vs</span>
      <Name tint="text-rose-400">Red</Name>
      <Stepper name="red.wins" className="fcjh-score-stepper" />
    </BoardBar>
  )
}
