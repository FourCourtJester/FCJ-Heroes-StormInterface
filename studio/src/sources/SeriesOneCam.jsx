import SeriesTop from '../components/SeriesTop'

// The series screen's top half with one camera: see ../components/SeriesTop.jsx.
//
// Add to OBS as a Browser source pointed at #/source/series-one-cam, 1920 x 1080, in the series
// scene that has one camera - content/guides/obs.md has the whole scene.
export default function SeriesOneCam() {
  return <SeriesTop cams={1} />
}
