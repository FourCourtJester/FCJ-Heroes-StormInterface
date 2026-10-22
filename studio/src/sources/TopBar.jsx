import { useVelcroValue } from '@single-studio/core'
import { Image, Scene, Tally, Variable } from '@single-studio/core/source'

import spec from '../generated/topbar.json'
import '../generated/namebar.css'
import banBlue from '../generated/ban_blue.svg'
import banRed from '../generated/ban_red.svg'
import pipBlue from '../generated/pip_blue.svg'
import pipEmpty from '../generated/pip_empty.svg'
import pipRed from '../generated/pip_red.svg'
import tabDivision from '../generated/tab_division.svg'
import tabGame from '../generated/tab_game.svg'

// The top bar: the plates that sit over the interface's own top bar, and the data on
// them. Every number here comes from ../generated/topbar.json, which tools/obs.py
// writes from the interface's layout.toml - so this graphic and the game's UI are
// drawn from one set of numbers and cannot drift apart.
//
// Add to OBS as a Browser source pointed at #/source/top-bar, 1920 x 1080, over the
// game capture. The interface draws the places; this draws the plates.
//
// The interface must stay usable with no OBS running (2026-10-22), so nothing here
// has a counterpart in the .StormInterface file: with this source off, the game's top
// bar is the level wings, Blizzard's hexagon and the clock.

const { boxes, clip, colours, tabs } = spec
const SIDES = ['blue', 'red']
const PIP = { blue: pipBlue, red: pipRed }
const TILE = { blue: banBlue, red: banRed }

// a generated box, [x, y, width, height] on the 1920 x 1080 page
const at = ([x, y, width, height]) => ({ position: 'absolute', left: x, top: y, width, height })

/** A team's name plate, with its logo plate when the tournament has logos. */
function Band({ side }) {
  const logo = useVelcroValue(`variables.${side}.logo`)
  return (
    <div className={`fcjh-band ${side}`}>
      <div className="fcjh-name">
        <div className="t">
          <Variable name={`${side}.name`} fallback="" fit />
        </div>
      </div>
      {logo ? (
        <div className="fcjh-logo">
          <div className="win" />
          <Image name={`${side}.logo`} className="mark" alt="" fit="contain" />
        </div>
      ) : null}
    </div>
  )
}

/** The series score: hexagon pips, filled from the name outward. */
function Pips({ side }) {
  const row = boxes.pips[side]
  const left = Math.min(...row.map((b) => b[0]))
  const right = Math.max(...row.map((b) => b[0] + b[2]))
  return (
    <Tally
      name={`${side}.wins`}
      of="series.pips"
      src={PIP[side]}
      empty={pipEmpty}
      alt=""
      style={{
        ...at([left, row[0][1], right - left, row[0][3]]),
        display: 'flex',
        gap: `${spec.score_pips.gap}px`,
        // index 0 is the pip nearest the name: blue's row grows away from it to the
        // left, red's to the right
        flexDirection: side === 'blue' ? 'row-reverse' : 'row',
      }}
      itemClassName="shrink-0"
    />
  )
}

/** One ban tile: the empty tile is the art, the portrait is clipped to its shape. */
function BanTile({ side, index, box }) {
  const picked = useVelcroValue(`variables.${side}.bans.${index}`)
  return (
    <div
      style={{
        ...at(box),
        backgroundImage: `url(${TILE[side]})`,
        backgroundSize: '100% 100%',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {picked ? (
        <div style={{ position: 'absolute', inset: 0, clipPath: clip.bans[side] }}>
          <Image
            name={`${side}.bans.${index}`}
            alt=""
            fit="cover"
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', filter: 'grayscale(1) brightness(.72)' }}
          />
          <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 4, background: colours.banned_foot }} />
        </div>
      ) : null}
    </div>
  )
}

/** The division (blue) and game (red) tabs: our art, the operator's words. */
function Tab({ name, box, art, example }) {
  return (
    <div style={at(box)}>
      <img src={art} alt="" style={{ width: '100%', height: '100%' }} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: tabs.font_px,
          fontWeight: 600,
          letterSpacing: '.08em',
          textTransform: 'uppercase',
          color: colours.tab_text,
          textShadow: '0 1px 2px #000',
        }}
      >
        <Variable name={name} fallback="" fit title={example} />
      </div>
    </div>
  )
}

export default function TopBar() {
  return (
    <Scene width={1920} height={1080}>
      <div style={{ position: 'relative', width: 1920, height: 1080 }}>
        {SIDES.map((side) => (
          <Band key={side} side={side} />
        ))}
        {SIDES.map((side) => (
          <Pips key={side} side={side} />
        ))}
        {SIDES.map((side) =>
          boxes.bans[side].map((box, index) => (
            <BanTile key={`${side}${index}`} side={side} index={index} box={box} />
          )),
        )}
        <Tab name="division" box={boxes.tabs.division} art={tabDivision} example={tabs.division.example} />
        <Tab name="game" box={boxes.tabs.game} art={tabGame} example={tabs.game_count.example} />
        <div style={{ ...at(boxes.event), clipPath: clip.event }}>
          <Image
            name="event.logo"
            alt=""
            fit="contain"
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
          />
        </div>
      </div>
    </Scene>
  )
}
