import { useVelcroMutate, useVelcroValue } from '@single-studio/core'
import { Panel, ResetButton, Row, Select, Toggle } from '@single-studio/core/control'

import { BAN, DRAFT_PATHS, HIDDEN, MAPS, PICK, SIDES, WON } from '../../components/series'

// The series: how long it is, and the map draft that runs through it (user, 2026-10-27: the
// map draft is "Series", and the best-of moves into it with it).
//
// The best-of has moved twice: Teams, then Tournament under the two tabs, then here. It is
// the same `series.pips` throughout, so a set best-of carries over, and clearing the teams
// still leaves it alone. It is the number of pips a side, which is what the graphic draws: a
// best of five is three.
//
// THE DRAFT: a row per map, banned or picked by a side. EVERY MAP IS IN until its Hide is pressed (user, 2026-10-27: the map pool "is
// hilarious" - a second list of the same fifteen names). Hide folds the block to its name
// and takes the card off the screen, and nothing it held is cleared: press it again and the
// map is back as it was ("We can always re-toggle it, and nothing disappears"). Reset draft
// shows them all again.
//
// Every button writes immediately, as a toggle does - this is a running record, and nothing
// here is half-typed. They are the framework's Toggle with its click handed to a mutation
// (src/mutations/series.js), because a ban or a pick clears what it replaces: a map is one
// thing at a time, and a new pick takes the next game number.
//
// WHO WON A MAP IS PRESSED HERE, and only here: a Win a side under each map's Ban and Pick
// (user, 2026-10-27: "we will scrap any kind of automatic stamping of a winner"). For an
// afternoon the Score Screen Winner marked the latest game's map; people were asked and it
// went. The two are the framework's grouped toggles, a group a map, so a map has one winner
// and pressing the lit one takes it back. They wait for a pick: a map nobody picked has no
// game to win, and a new pick clears a result anyway (series:mark).
//
// Two rows a map on a wide board - Ban Pick Ban Pick, then Win Win under their sides - and
// three on a narrow one, blue's pair, red's, then the wins (user, 2026-10-27).
//
// Reset draft empties the draft and un-hides every map, and keeps the best-of, which is the
// series' format rather than its progress. Swap sides on the Teams panel trades the draft with the teams.

const strip = (path) => path.replace(/^toggles\./, '')

// the buttons name what they do and their colour is whose (user, 2026-10-27: "color them up
// and remove the team associations"); the side is in the class, for css/index.css's tint
const LABEL = { ban: 'Ban', pick: 'Pick' }

// the heading over a block wears the Panel title's own classes, as the Score Screen Winner's
// does, so the sections read as part of the board
const HEADING = 'text-sm font-semibold tracking-wide text-slate-400 uppercase'

function MapDraft({ slug, name }) {
  const mutate = useVelcroMutate()
  const hidden = useVelcroValue(HIDDEN(slug))
  const picked = [useVelcroValue(PICK('blue', slug)), useVelcroValue(PICK('red', slug))].some(Boolean)

  const mark = (side, as) => () => mutate('series:mark', { map: slug, side, as })

  return (
    <>
      <div className="flex items-center justify-between gap-2">
        <span className={HEADING}>{name}</span>
        {/* a plain toggle at the board's small size: lit while the map is hidden */}
        <Toggle name={strip(HIDDEN(slug))} size="sm">
          {hidden ? 'Show' : 'Hide'}
        </Toggle>
      </div>
      {hidden ? null : (
        <Row className="row-cols-2 sm:row-cols-4">
          {/* side by side, as the screen is: blue's ban and pick, then red's */}
          {SIDES.flatMap((side) =>
            ['ban', 'pick'].map((as) => (
              <Toggle
                key={`${as}.${side}`}
                name={strip(as === 'ban' ? BAN(side, slug) : PICK(side, slug))}
                onClick={mark(side, as)}
                className={`fcjh-won tint ${side}`}
              >
                {LABEL[as]}
              </Toggle>
            )),
          )}
        </Row>
      )}
      {hidden ? null : (
        <Row className="row-cols-2">
          {SIDES.map((side) => (
            <Toggle
              key={`won.${side}`}
              name={strip(WON(side, slug))}
              group={`won.${slug}`}
              disabled={!picked}
              className={`fcjh-won tint ${side}`}
            >
              Win
            </Toggle>
          ))}
        </Row>
      )}
    </>
  )
}

export default function Series() {
  return (
    <Panel title="Series" collapsible actions={<ResetButton label="draft" paths={DRAFT_PATHS} size="sm" />}>
      <Select
        name="series.pips"
        label="Best of"
        options={[
          { label: 'Best of 3', value: '2' },
          { label: 'Best of 5', value: '3' },
          { label: 'Best of 7', value: '4' },
        ]}
      />

      <hr className="border-0 border-t border-slate-700/60" />
      {MAPS.map(({ slug, name }) => (
        <MapDraft key={slug} slug={slug} name={name} />
      ))}
    </Panel>
  )
}
