"""
Tests for tools/validate.py: break a copy of the real interface on purpose and
check each mistake is caught at the right level.

    python tools/test_validate.py
"""

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

LAYOUT = Path("Base.StormData/UI/Layout/_FCJH.StormLayout")
DESC_INDEX = Path("Base.StormData/UI/Layout/DescIndex.StormLayout")


class BrokenCopy:
    """A temp copy of the interface source with one file edited."""

    def __init__(self, testcase):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "FCJH.StormInterface"
        shutil.copytree(validate.DEFAULT_SOURCE, self.root)
        testcase.addCleanup(shutil.rmtree, self.tmp)

    def edit(self, rel, old, new, regex=False, count=1):
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        if regex:
            text, n = re.subn(old, new, text, count=count)
        else:
            n = min(text.count(old), count)
            text = text.replace(old, new, count)
        assert n, f"mutation found nothing to replace: {old!r}"
        path.write_text(text, encoding="utf-8")

    def run(self):
        errors, warnings, lines, _ = validate.validate(self.root)
        return errors, warnings, lines


class ValidateTests(unittest.TestCase):

    def assertReported(self, lines, level, fragment):
        hits = [l for l in lines if f": {level}: " in l and fragment in l]
        self.assertTrue(hits, f"expected a {level} containing {fragment!r}; got:\n" + "\n".join(lines))

    def broken(self, old, new, **kw):
        copy = BrokenCopy(self)
        copy.edit(LAYOUT, old, new, **kw)
        return copy.run()

    # ---------------------------------------------------------- baseline

    def test_current_source_has_no_errors(self):
        errors, _, lines = validate.validate()[:3]
        self.assertEqual(errors, 0, "\n".join(lines))

    # ---------------------------------------------------------- errors

    def test_unbalanced_xml(self):
        errors, _, lines = self.broken("</Frame>", "", count=1)
        self.assertReported(lines, "error", "XML does not parse")

    def test_typo_in_blizzard_frame_name(self):
        errors, _, lines = self.broken('name="UIContainer">', 'name="UIContainr">')
        self.assertReported(lines, "error", "no frame 'UIContainr'")

    def test_unprefixed_new_frame_under_blizzard_frame(self):
        errors, _, lines = self.broken('name="FCJH_ClusterBacking"', 'name="ClusterBacking"')
        self.assertReported(lines, "error", "no frame 'ClusterBacking'")

    def test_missing_template(self):
        errors, _, lines = self.broken('template="_FCJH/ParkedTemplate"', 'template="_FCJH/ParkTemplate"')
        self.assertReported(lines, "error", "template '_FCJH/ParkTemplate' does not exist")

    def test_missing_blizzard_template(self):
        errors, _, lines = self.broken("UnitStatus/UnitStatusBuffDebuffDisplayTemplate",
                                       "UnitStatus/UnitStatusBuffDebuffDisplayTemplat")
        self.assertReported(lines, "error", "does not exist")

    def test_undefined_constant(self):
        errors, _, lines = self.broken('offset="#CLUSTER_TOP"', 'offset="#CLUSTER_TOPP"')
        self.assertReported(lines, "error", "constant '#CLUSTER_TOPP' is never defined")

    def test_unresolvable_anchor(self):
        errors, _, lines = self.broken('relative="$parent/BlockLeft"', 'relative="$parent/BlockLefft"')
        self.assertReported(lines, "error", "'$parent/BlockLefft' resolves to nothing")

    def test_unresolvable_handle(self):
        errors, _, lines = self.broken('frame="$GameUICommandPanel"', 'frame="$GameUICommandPanl"')
        self.assertReported(lines, "error", "resolves to nothing")

    def test_bad_anchor_pos(self):
        errors, _, lines = self.broken('pos="Mid" offset="#OBJ_HALF_NEG"', 'pos="Middle" offset="#OBJ_HALF_NEG"')
        self.assertReported(lines, "error", "Anchor pos 'Middle'")

    def test_non_numeric_offset(self):
        errors, _, lines = self.broken('offset="#BAR_HEIGHT"', 'offset="64px"')
        self.assertReported(lines, "error", "offset '64px' is not a whole number")

    def test_bad_override_file(self):
        errors, _, lines = self.broken('file="GameUI"', 'file="GameUIX"')
        self.assertReported(lines, "error", "names no known layout file")

    def test_desc_index_missing_include(self):
        copy = BrokenCopy(self)
        copy.edit(DESC_INDEX, "_FCJH.StormLayout", "_FCJHX.StormLayout")
        errors, _, lines = copy.run()
        self.assertReported(lines, "error", "_FCJHX.StormLayout', which does not exist")
        self.assertReported(lines, "warning", "is not included by DescIndex")

    # ---------------------------------------------------------- warnings

    def test_parking_icon_frame_drags_the_portrait(self):
        # The build 36-38 bug: parking IconFrame sent every hero portrait off-screen.
        errors, _, lines = self.broken(
            r'<Frame type="Image" name="IconFrame">\s*<Alpha val="0"/>\s*</Frame>',
            '<Frame type="Image" name="IconFrame" template="_FCJH/ParkedTemplate"/>', regex=True)
        self.assertReported(lines, "warning", "parking IconFrame drags")
        self.assertReported(lines, "warning", "HeroPortraitImage")

    def test_partial_constant(self):
        errors, _, lines = self.broken('<Text val="#BUILD_STAMP"/>', '<Text val="BUILD #BUILD_STAMP"/>')
        self.assertReported(lines, "warning", "only substitutes as the ENTIRE value")

    def test_fill_without_adjustment_color(self):
        errors, _, lines = self.broken(
            r'(?s)(<Frame type="Image" name="BarBlockTemplate">.*?)<AdjustmentColor val="255,0,0,0"/>',
            r"\1", regex=True)
        self.assertReported(lines, "warning", "ColorAdjustMode Fill")

    def test_visible_false_on_blizzard_frame(self):
        errors, _, lines = self.broken('<Frame type="TargetInfoFrame" name="TargetInfoFrame">',
                                       '<Frame type="TargetInfoFrame" name="TargetInfoFrame">'
                                       '<Visible val="false"/>')
        self.assertReported(lines, "warning", "Visible=false does not stick")

    def test_type_mismatch(self):
        errors, _, lines = self.broken('<Frame type="Image" name="IconFrame">',
                                       '<Frame type="Label" name="IconFrame">')
        self.assertReported(lines, "warning", "is type Image")

    def test_anchoring_a_side_blizzard_moves_at_runtime(self):
        errors, _, lines = self.broken(
            '<Frame type="Image" name="IconFrame">',
            '<Frame type="Label" name="HeroDeathTimeLabel">'
            '<Anchor side="Right" relative="$parent" pos="Max" offset="0"/></Frame>'
            '<Frame type="Image" name="IconFrame">')
        self.assertReported(lines, "warning", "re-anchors HeroDeathTimeLabel's Right side at runtime")


if __name__ == "__main__":
    unittest.main(verbosity=2)
