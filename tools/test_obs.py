"""
Tests for the broadcast generator's nine-slice frames: every plate's cap must hold its
own point.

This is the check that was missing on 2026-10-26, when the matchup band's cap was an
authored number and three 10% passes walked it under the point it was slicing. The slice
cut through the frame's diagonal, the leftover slope was stretched the length of the bar,
and nothing complained - the silhouette is a clip-path computed from lean x height and
stayed correct the whole time, so only the chrome came apart.

    python tools/test_obs.py
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen  # noqa: E402
import obs  # noqa: E402

GENERATED = Path(__file__).resolve().parent.parent / "studio" / "src" / "generated"

# every frame the band draws, and the height it is cut for
FRAMES = {
    "frame_matchup.svg": lambda b: b.sb["team_h"],      # the standby band's container
    "frame_plate.svg": obs._plate_h,                    # the slab composition's name plate
    "frame_unit.svg": obs._unit_h,                      # the one-container composition
}


def band():
    """The same config the generator runs on - derived, not raw TOML."""
    return obs.Band(gen.load_config())


class FrameCaps(unittest.TestCase):
    """The committed art, read back as a file rather than recomputed."""

    @classmethod
    def setUpClass(cls):
        cls.b = band()

    def art(self, name):
        """(width, height, point) of a generated frame, from the file itself."""
        svg = (GENERATED / name).read_text(encoding="utf-8")
        w, h = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
        # the clip polygon's first vertex is the top of the leading point
        point = float(re.search(r'points="([\d.]+),0', svg).group(1))
        return w, h, point

    def test_every_frame_is_cut_for_its_own_height(self):
        """The art's point must be lean x height / 2 for the height it serves - which is what
        makes the chrome's angle match the clip-path's. Art cut for another height draws a
        blunter point in anything shorter."""
        for name, height_of in FRAMES.items():
            with self.subTest(frame=name):
                h = height_of(self.b)
                _, art_h, point = self.art(name)
                self.assertAlmostEqual(art_h, h, places=2,
                                       msg=f"{name} is cut at {art_h}, not {h}")
                self.assertAlmostEqual(point, self.b.lean * h / 2, places=2)

    def test_cap_holds_the_point_with_room_for_the_rim(self):
        """THE REGRESSION THIS FILE EXISTS FOR. A cap narrower than the point slices through
        the diagonal, and the leftover slope is stretched down the whole bar."""
        for name in FRAMES:
            with self.subTest(frame=name):
                w, _, point = self.art(name)
                cap = (w - obs.MID) / 2
                self.assertGreaterEqual(
                    cap, point + 2 * self.b.rim_w,
                    f"{name}: a {cap} px cap cannot hold a {point} px point and its rim")

    def test_the_spec_hands_out_the_caps_the_art_was_cut_with(self):
        """The stylesheet slices with the number the spec gives it, so a spec that disagrees
        with the file is the same bug by another route."""
        spec = obs.matchup_spec(self.b)
        for frame_name, cap in (
            (spec["name"]["frame"], spec["name"]["nine_slice"]["caps"]),
            (spec["unit"]["frame"], spec["unit"]["cap"]),
        ):
            with self.subTest(frame=frame_name):
                w, _, _ = self.art(frame_name)
                self.assertEqual(cap, (w - obs.MID) / 2,
                                 f"{frame_name}: spec says {cap}, art has {(w - obs.MID) / 2}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
