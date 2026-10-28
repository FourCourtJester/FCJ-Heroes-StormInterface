import { useVelcroCollection } from '@single-studio/core'
import { Image, Scene, Variable } from '@single-studio/core/source'

import FitLines from '../components/FitLines'
import { draft } from '../components/series'
import spec from '../generated/series.json'
import './series.css'

// The series screen's map draft: a tall card a map, across the middle of the screen (user,
// 2026-10-27).
//
// The cards only. The top half - cameras and marks - is its own source per camera count
// (SeriesTwoCams, SeriesOneCam, SeriesNoCams), and the matchup under the cards is the
// Matchup Draft source, cropped and scaled in OBS. So the cards are the same in all three
// scenes, and cutting between them moves nothing here.
//
// A card a map in the pool, sharing the band between them: fifteen are narrow, nine are as
// wide as they get. The art is cut for nine (series.json `art`) and cropped to its middle
// for more, never stretched.
//
//   available   the art and the map's name
//   banned      the art greyed, a BAN bar in the banner's colour, their logo at the foot
//   picked      a rim in the picker's colour, "Game N" across the top, their name - no logo:
//               the rim says whose (user, 2026-10-27: "The colored border is good enough")
//   playing     the same, with a dot in the tag and a glow
//   won         the art dimmed, the winner's logo at the foot with their name under it - the
//               logo arrives with the win ("THEN add the team logo, anchored on the
//               bottom"). No laurel: it did not work on a card this narrow, "or, any of
//               them, actually" (user, 2026-10-27)
//
// THE NAME SITS ON THE BOTTOM EDGE of every card alike, and is ALWAYS TWO LINES TALL, wrapped
// or not, so whatever stacks above it starts at one height across the row (user, 2026-10-27:
// "makes it look more uniform"). A name two lines cannot hold shrinks. A team's name, the
// winner's or the picker's, wraps to two lines before it shrinks too ("can grow to 2 lines
// before Fit") - FitLines.
//
// Add to OBS as a Browser source pointed at #/source/series, 1920 x 1080, over the top half
// and the Matchup Draft source - content/guides/obs.md has the scene.

const [SCREEN_W, SCREEN_H] = spec.screen
const { cards, art, colours } = spec

const SCENE_VARS = {
  '--screen-w': `${SCREEN_W}px`,
  '--screen-h': `${SCREEN_H}px`,
  '--cards-top': `${cards.top}px`,
  '--cards-h': `${cards.bottom - cards.top}px`,
  '--card-cut': `${cards.cut}px`,
  '--card-rim': `${cards.rim}px`,
  '--map-name': `${cards.name}px`,
  '--blue': colours.blue,
  '--red': colours.red,
  '--rim': colours.rim,
  '--text': colours.text,
}

// a clear pixel, for a map whose art has not been cut yet: the card's own dark shows instead
const NO_ART = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='

function Who({ side, logo = true, name = true }) {
  return (
    <div className="fcjh-card-who">
      {logo ? <Image name={`${side}.logo`} alt="" fit="contain" className="fcjh-card-logo" /> : null}
      {name ? (
        <FitLines>
          <Variable name={`${side}.name`} fallback="" />
        </FitLines>
      ) : null}
    </div>
  )
}

function Card({ map, x, w }) {
  const { slug, name, state, by, game, won, live } = map
  const classes = ['fcjh-card', state, by, won ? 'won' : null, live ? 'live' : null]

  return (
    <div className={classes.filter(Boolean).join(' ')} style={{ left: `${x}px`, width: `${w}px` }}>
      <div className="fcjh-card-rim" />
      <div className="fcjh-card-art">
        <Image value={slug} src={`${art.dir}:value:${art.ext}`} fallback={NO_ART} alt="" fit="cover" />

        {state === 'pick' ? (
          <div className="fcjh-card-tag">
            {live ? <i /> : null}
            {game ? `Game ${game}` : 'Pick'}
          </div>
        ) : null}

        {state === 'ban' ? <div className="fcjh-card-bar">Ban</div> : null}

        <div className="fcjh-card-foot">
          {/* a won map says its winner by logo and name; a pick says its picker by name, the rim
              its colour; a ban's bar already wears the banner's colour, so it keeps the logo
              and drops the name (user, 2026-10-27) */}
          {won ? (
            <div className={`fcjh-card-win ${won}`}>
              <Image name={`${won}.logo`} alt="" fit="contain" className="fcjh-card-logo" />
              <FitLines>
                <Variable name={`${won}.name`} fallback="" />
              </FitLines>
            </div>
          ) : by ? (
            <Who side={by} logo={state === 'ban'} name={state !== 'ban'} />
          ) : null}
          <div className="fcjh-card-name">
            <FitLines>{name}</FitLines>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Series() {
  const { value: toggles, loaded: a } = useVelcroCollection('toggles.series')
  const { value: games, loaded: b } = useVelcroCollection('variables.series.game')

  // nothing until both have loaded: a draft drawn from half its state is a wrong one
  const maps = a && b ? draft(toggles, games) : []
  const n = maps.length
  const w = n ? (cards.right - cards.left - cards.gap * (n - 1)) / n : 0

  return (
    <Scene width={SCREEN_W} height={SCREEN_H}>
      <div className="fcjh-series" style={SCENE_VARS}>
        {maps.map((map, i) => (
          <Card key={map.slug} map={map} x={cards.left + i * (w + cards.gap)} w={w} />
        ))}
      </div>
    </Scene>
  )
}
