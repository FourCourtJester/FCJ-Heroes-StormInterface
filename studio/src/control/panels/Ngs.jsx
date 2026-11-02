import { useState } from 'react'

import { useVelcroMutate, useVelcroValue } from '@single-studio/core'
import { Panel, Row } from '@single-studio/core/control'

// The Nexus Gaming Series (user, 2026-10-29): Season > Division > Match > Load, each step
// narrowing the next. The season fetches itself when the studio loads (user, 2026-11-02: a
// button used once every three months had no place on the board); choose a division (its
// matches are fetched), choose a match (nothing is), and Load it before going live. What Load writes is in
// src/mutations/ngs.js; it is never a score.
//
// THE PICKERS ARE THIS BOARD'S, not the show's: a choice being made, kept in the component as
// the plugin's README has it, so one operator browsing matches moves nobody else's board.
// They are plain selects in the framework's Select's classes, because a Select stages until
// saved and these have to act when chosen.
//
// It sits first, as it is pressed once before the show: it fills Teams, Tournament's tabs and
// the Series panel's best-of and maps, which stay the operator's to change afterwards.

const LABEL = 'ss-label flex h-4 items-center text-xs font-medium tracking-wide text-slate-400 uppercase'
const SELECT =
  'h-[var(--ss-input-h,2.5rem)] rounded-md border border-slate-700 bg-slate-900 px-3 py-1 text-slate-100 transition-colors outline-none focus:border-sky-500 disabled:opacity-50'
const BUTTON = 'rounded-md bg-sky-600 font-medium text-white transition-colors hover:bg-sky-500'

function Picker({ label, value, onChange, disabled, children }) {
  return (
    <label className="ss-select flex flex-col gap-1">
      <span className={LABEL}>{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className={SELECT}
      >
        {children}
      </select>
    </label>
  )
}

export default function Ngs() {
  const mutate = useVelcroMutate()
  const season = useVelcroValue('variables.ngs.season')
  const divisions = useVelcroValue('variables.ngs.divisions') ?? []
  const matches = useVelcroValue('variables.ngs.matches') ?? []
  const problem = useVelcroValue('variables.ngs.problem')
  const [division, setDivision] = useState('')
  const [match, setMatch] = useState('')

  const choose = (key) => {
    setDivision(key)
    setMatch('')
    if (key) mutate('ngs:matches', { division: key })
  }
  const shown = matches.filter((one) => one.division === division)

  return (
    <Panel title={season ? `NGS season ${season}` : 'NGS'} collapsible>
      <Row>
        <Picker label="Division" value={division} onChange={choose} disabled={!divisions.length}>
          <option value="">{divisions.length ? '— choose —' : 'Fetching the season…'}</option>
          {divisions.map(({ key, name }) => (
            <option key={key} value={key}>
              {name}
            </option>
          ))}
        </Picker>
        <Picker label="Match" value={match} onChange={setMatch} disabled={!shown.length}>
          <option value="">{division && !shown.length ? 'No matches yet' : '— choose —'}</option>
          {shown.map((one) => (
            <option key={one.id} value={one.id}>
              {one.label}
            </option>
          ))}
        </Picker>
      </Row>
      <button
        type="button"
        disabled={!match}
        onClick={() => mutate('ngs:load', { id: match })}
        className={`${BUTTON} h-[var(--ss-input-h,2.5rem)] px-3 text-sm disabled:opacity-50 disabled:hover:bg-sky-600`}
      >
        Load match
      </button>
      {problem ? <p className="text-sm text-rose-400">{problem}</p> : null}
    </Panel>
  )
}
