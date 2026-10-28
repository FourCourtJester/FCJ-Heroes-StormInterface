import { Field, Panel, Row, SwapButton } from '@single-studio/core/control'

// The two webcam frames, and who is in them.
//
// This panel names people; it does not place cameras. The frames are a browser source of
// borders (src/sources/Webcams.jsx) and the cameras go under it in OBS, each with the
// matching mask from src/generated/ - see that file's header for the two steps.
//
// Left and right are the frames as the viewer sees them, which is also the order they sit
// in OBS. When the casters swap seats, Swap sides trades the two names and handles (user,
// 2026-10-27), in the header as on Teams; it asks first, as that one does.
//
// A side with neither a name nor a handle shows its window and no bar at all, which is what
// a guest camera with no lower third should look like.

// one seat, then the other, in the same order
const SEATS = ['cam.left.name', 'cam.left.social', 'cam.right.name', 'cam.right.social']

export default function Cams() {
  return (
    <Panel title="Webcams" collapsible actions={<SwapButton label="Swap sides" names={SEATS} size="sm" />}>
      <Row>
        <Field name="cam.left.name" label="Left" placeholder="Commentator" />
        <Field name="cam.left.social" label="Left handle" placeholder="@handle" />
      </Row>
      <Row>
        <Field name="cam.right.name" label="Right" placeholder="Commentator" />
        <Field name="cam.right.social" label="Right handle" placeholder="@handle" />
      </Row>
    </Panel>
  )
}
