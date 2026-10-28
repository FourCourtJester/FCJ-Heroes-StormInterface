import SeriesTop from '../components/SeriesTop'

// The series screen's top half with no cameras: see ../components/SeriesTop.jsx.
//
// Add to OBS as a Browser source pointed at #/source/series-no-cams, 1920 x 1080, in the series
// scene that has no cameras - content/guides/obs.md has the whole scene.
export default function SeriesNoCams() {
  return <SeriesTop cams={0} />
}
