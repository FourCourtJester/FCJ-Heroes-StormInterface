"""
Smoke test for the packer: author a tiny interface in Python, pack it, deploy it.

Use it when a patch may have broken loading. It takes the FCJH layout out of
the question: if the magenta box shows, the packer and archive format still
work, and any problem is in the layout.

What to look for in game: a MAGENTA block near the top-centre of the screen
carrying "FCJH PY-MPQ v1 TEST" and the build time. Everything else is stock UI.
  - Block visible, time matches this run  -> packer works, v1 accepted.
  - Stock UI only, no block               -> archive rejected (or not selected -
                                             check both Variables.txt files).

Deploys as FCJHTest.StormInterface, so select that in both Variables.txt files.

The file set mirrors a known-good FCJH archive. DocumentHeader is editor
metadata in a binary format we have not decoded; it is copied from the FCJH
source rather than authored.

Confirmed working 2026-09-25 (MPQ v1 accepted; replay reopen picks up rebuilds).

    python tools/make_test_ui.py            # build, verify, deploy
    python tools/make_test_ui.py --wait     # retry while a replay holds the lock
    python tools/make_test_ui.py --no-deploy
"""

import argparse
import sys
from datetime import datetime

import mpq
import pack

FCJH_SOURCE = pack.DEFAULT_SOURCE
NAME = "FCJHTest.StormInterface"

LOCALES = ["enUS", "frFR", "deDE", "esES", "esMX", "ruRU", "koKR",
           "zhCN", "zhTW", "plPL", "itIT", "ptBR"]

LAYOUT_PATH = "Base.StormData/UI/Layout/_FCJHTest.StormLayout"

XML_DECL = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'


def test_layout(stamp):
    return XML_DECL + f"""<Desc>
	<Frame type="GameUI" name="GameUI" file="GameUI">
		<Frame type="Image" name="FCJHTest_Block">
			<Anchor side="Top"    relative="$parent" pos="Min" offset="200"/>
			<Anchor side="Bottom" relative="$parent" pos="Min" offset="360"/>
			<Anchor side="Left"   relative="$parent" pos="Mid" offset="-300"/>
			<Anchor side="Right"  relative="$parent" pos="Mid" offset="300"/>
			<Texture val="@UI/PauseScreenDimImage"/>
			<ColorAdjustMode val="Fill"/>
			<AdjustmentColor val="255,255,0,255"/>
			<AcceptsMouse val="false"/>
		</Frame>
		<Frame type="Label" name="FCJHTest_Label">
			<Anchor side="Top"   relative="$parent/FCJHTest_Block" pos="Min" offset="60"/>
			<Anchor side="Left"  relative="$parent/FCJHTest_Block" pos="Min" offset="20"/>
			<Anchor side="Right" relative="$parent/FCJHTest_Block" pos="Max" offset="-20"/>
			<Style val="WaitingForPlayersDialogChat"/>
			<Text val="{stamp}"/>
			<Options val="NoWrapping"/>
			<Unclipped val="true"/>
			<AcceptsMouse val="false"/>
		</Frame>
	</Frame>
</Desc>
"""


def desc_index(layouts):
    includes = "".join(f'\t<Include path="{p}"/>\n' for p in layouts)
    return XML_DECL + f"<Desc>\n{includes}</Desc>\n"


def component_list():
    text = [f'    <DataComponent Type="text" Locale="{loc}">GameText</DataComponent>'
            for loc in LOCALES]
    return "\n".join([
        '<?xml version="1.0" encoding="utf-8"?>',
        "<Components>",
        "    <Optimized/>",
        '    <DataComponent Type="gada">GameData</DataComponent>',
        text[0],
        '    <DataComponent Type="info">DocumentInfo</DataComponent>',
        '    <DataComponent Type="uiui">UI/Layout/DescIndex.StormLayout</DataComponent>',
        '    <DataComponent Type="font">UI/FontStyles.StormStyle</DataComponent>',
        *text[1:],
        "</Components>",
    ]) + "\n"


DOCUMENT_INFO = """<?xml version="1.0" encoding="utf-8"?>
<DocInfo>
    <ModType>
        <Value>Interface</Value>
    </ModType>
</DocInfo>
"""

FONT_STYLES = XML_DECL + "<StyleFile>\n</StyleFile>\n"

GAME_STRINGS = "﻿DocInfo/DescLong=\r\nDocInfo/DescShort=\r\nDocInfo/Name=\r\n"


def author(stamp):
    """Every file in the interface, as {archive path: bytes}."""
    files = {
        "ComponentList.StormComponents": component_list(),
        "DocumentInfo": DOCUMENT_INFO,
        "ObserverVariables.txt": "",
        "Base.StormData/GameData/Assets.txt": "",
        "Base.StormData/UI/FontStyles.StormStyle": FONT_STYLES,
        "Base.StormData/UI/Layout/DescIndex.StormLayout": desc_index([LAYOUT_PATH]),
        LAYOUT_PATH: test_layout(stamp),
    }
    for loc in LOCALES:
        files[f"{loc}.StormData/LocalizedData/GameStrings.txt"] = GAME_STRINGS
    files = {path: text.encode("utf-8") for path, text in files.items()}
    files["DocumentHeader"] = (FCJH_SOURCE / "DocumentHeader").read_bytes()
    return files


def verify_roundtrip(archive_bytes, files):
    archive = mpq.MpqArchive(archive_bytes)
    assert archive.format_version == 0, archive.format_version
    for path, data in files.items():
        assert archive.read(path) == data, f"round-trip mismatch: {path}"
    listed = sorted(archive.names())
    expected = sorted(p.replace("/", "\\") for p in files)
    assert listed == expected, (listed, expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--no-deploy", action="store_true")
    parser.add_argument("--wait", action="store_true", help="retry a locked write until it succeeds")
    args = parser.parse_args()

    stamp = f"FCJH PY-MPQ v1 TEST - built {datetime.now():%Y-%m-%d %H:%M:%S}"
    files = author(stamp)
    for problem in pack.check_xml(files):
        raise SystemExit(f"XML does not parse: {problem}")
    archive = mpq.write_mpq(files)
    verify_roundtrip(archive, files)
    print(f"{NAME}: {len(files)} files, {len(archive)} bytes, MPQ v1, round-trip OK")
    print(f"stamp: {stamp}")

    if args.no_deploy:
        return 0
    dest = pack.INTERFACES / NAME
    if not pack.deploy(archive, dest, args.wait):
        return 1
    print(f"deployed: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
