import SeriesTop from '../components/SeriesTop'

// The series screen's top half with two cameras: see ../components/SeriesTop.jsx.
//
// Add to OBS as a Browser source pointed at #/source/series-two-cams, 1920 x 1080, in the series
// scene that has two cameras - content/guides/obs.md has the whole scene.
export default function SeriesTwoCams() {
  return <SeriesTop cams={2} />
}
