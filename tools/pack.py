"""
Pack an interface source folder into a .StormInterface (MPQ v1) and deploy it.
Replaces the Java builder's compile step, which turned out to be a byte-for-byte
copy of the source folder into an archive.

Checks before writing: tools/validate.py (XML, constants, templates, frame
paths, anchors - against Blizzard's base UI), and that the archive reads back
identical to the source. Validation errors stop the build; warnings are shown.

Heroes locks the deployed file only while a replay or match is open; at the
main menu it can be overwritten, and reopening a replay loads the new build.
With --wait, a locked write is retried until the lock releases.

    python tools/pack.py                          # src/FCJH.StormInterface -> FCJH.StormInterface
    python tools/pack.py --name FCJHTest.StormInterface
    python tools/pack.py --wait
    python tools/pack.py --no-deploy
    python tools/pack.py --no-validate   # pack even if validation fails
"""

import argparse
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import mpq
import validate

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO / "src" / "FCJH.StormInterface"
INTERFACES = Path.home() / "OneDrive" / "Documents" / "Heroes of the Storm" / "Interfaces"

XML_SUFFIXES = (".StormLayout", ".StormStyle", ".StormComponents")


def collect(source):
    """{archive path: bytes} for every file under the source folder."""
    return {p.relative_to(source).as_posix(): p.read_bytes()
            for p in sorted(source.rglob("*")) if p.is_file()}


def check_xml(files):
    bad = []
    for path, data in files.items():
        if path.endswith(XML_SUFFIXES) or path == "DocumentInfo":
            try:
                ET.fromstring(data)
            except ET.ParseError as e:
                bad.append(f"{path}: {e}")
    return bad


def verify_roundtrip(archive_bytes, files):
    archive = mpq.MpqArchive(archive_bytes)
    for path, data in files.items():
        if archive.read(path) != data:
            raise AssertionError(f"round-trip mismatch: {path}")


def deploy(archive_bytes, dest, wait):
    announced = False
    while True:
        try:
            dest.write_bytes(archive_bytes)
            return True
        except PermissionError:
            if not wait:
                print(f"locked: {dest.name} is held by Heroes (a replay or match is open). "
                      "Leave it, or rerun with --wait.")
                return False
            if not announced:
                print("locked - waiting for the replay to be exited...")
                announced = True
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--name", help="deployed filename (default: the source folder's name)")
    parser.add_argument("--no-deploy", action="store_true")
    parser.add_argument("--wait", action="store_true", help="retry a locked write until it succeeds")
    parser.add_argument("--no-validate", action="store_true", help="skip tools/validate.py")
    args = parser.parse_args()

    source = args.source.resolve()
    if not args.no_validate:
        errors, warnings, lines, _ = validate.validate(source)
        if lines:
            print("\n".join(lines))
        print(f"validate: {errors} error(s), {warnings} warning(s)")
        if errors:
            print("not packed - fix the errors, or rerun with --no-validate")
            return 1

    files = collect(source)
    bad = check_xml(files)
    if bad:
        print("XML does not parse - the game would silently ignore the whole interface:")
        print("\n".join(f"  {b}" for b in bad))
        return 1

    archive = mpq.write_mpq(files)
    verify_roundtrip(archive, files)
    name = args.name or source.name
    print(f"{name}: {len(files)} files, {len(archive)} bytes, MPQ v1, round-trip OK")

    if args.no_deploy:
        return 0
    dest = INTERFACES / name
    if not deploy(archive, dest, args.wait):
        return 1
    print(f"deployed: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
