"""
Build the interface: generate, stage, validate, pack, deploy.

  1. generate  tools/gen.py rewrites the committed generated layouts from layout.toml
  2. stage     src/FCJH.StormInterface is copied to build/<profile>/; a dev build adds
               the build stamp and src/dev/ layouts
               (experiments and probes) there, and only there
  3. validate  tools/validate.py on the staged tree; an error stops the build
  4. pack      the staged tree becomes an MPQ v1 archive, read back and checked
  5. deploy    written to the Heroes Interfaces folder

Profiles:
  dev (default)  stamp + overlay, deployed as FCJH.StormInterface
  --release      exactly what src/ holds; refuses if src/, layout.toml or tools/ have
                 uncommitted changes, so every release is reproducible from its commit;
                 written to dist/v<version>/, deployed only with --deploy

Heroes locks the deployed file only while a replay or match is open. At the main menu it
can be overwritten, and reopening a replay loads the new build. --wait retries a locked
write until the lock releases.

    python tools/pack.py --wait                  # the everyday loop
    python tools/pack.py --no-deploy
    python tools/pack.py --release               # dist/v0.1.0/FCJH.StormInterface
    python tools/pack.py --release --deploy
"""

import argparse
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import gen
import mpq
import validate

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = gen.SOURCE
DEV_LAYOUTS = REPO / "src" / "dev"
BUILD = REPO / "build"
DIST = REPO / "dist"
INTERFACES = Path.home() / "OneDrive" / "Documents" / "Heroes of the Storm" / "Interfaces"
NAME = "FCJH.StormInterface"

XML_SUFFIXES = (".StormLayout", ".StormStyle", ".StormComponents")
RELEASE_PATHS = ["src", "layout.toml", "tools"]


def git(*args):
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return out.stdout.rstrip() if out.returncode == 0 else ""


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


def stage(cfg, source, profile):
    """Copy the source to build/<profile>/ and add profile extras. Returns the staged folder."""
    staged = BUILD / profile / source.name
    if staged.exists():
        shutil.rmtree(staged)
    shutil.copytree(source, staged)
    if profile == "dev":
        layout_dir = staged / gen.LAYOUT_REL
        # src/dev/*.StormLayout: dev-only layouts (experiments, probes). Committed, never shipped.
        probes = sorted(DEV_LAYOUTS.glob("*.StormLayout")) if DEV_LAYOUTS.is_dir() else []
        for probe in probes:
            shutil.copy(probe, layout_dir / probe.name)
        order = gen.layout_order(source / gen.LAYOUT_REL, extra=[p.name for p in probes] + [gen.DEV_FILE])
        commit = git("rev-parse", "--short", "HEAD") or "nogit"
        dirty = "+" if git("status", "--porcelain", "--", *RELEASE_PATHS) else ""
        stamp = f"FCJH DEV {cfg['meta']['version']} {commit}{dirty} {datetime.now():%H:%M:%S}"
        (layout_dir / gen.DEV_FILE).write_text(gen.dev_layout(cfg, stamp), encoding="utf-8", newline="\n")
        (layout_dir / gen.INDEX_FILE).write_text(gen.desc_index(order), encoding="utf-8", newline="\n")
        print(f"stamp: {stamp}")
    return staged


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
    parser.add_argument("--release", action="store_true", help="release profile (see above)")
    parser.add_argument("--deploy", action="store_true", help="with --release: also deploy")
    parser.add_argument("--no-deploy", action="store_true")
    parser.add_argument("--name", default=NAME, help=f"deployed filename (default {NAME})")
    parser.add_argument("--wait", action="store_true", help="retry a locked write until it succeeds")
    parser.add_argument("--no-validate", action="store_true", help="skip tools/validate.py")
    args = parser.parse_args()

    source = args.source.resolve()
    cfg = gen.load_config()
    profile = "release" if args.release else "dev"

    # 1. generate
    if source == DEFAULT_SOURCE:
        for rel in gen.write(cfg, source):
            print(f"generated: {rel.as_posix()}")

    if args.release:
        dirty = git("status", "--porcelain", "--", *RELEASE_PATHS)
        if dirty:
            print("not released - commit these first, so the release matches a commit:")
            print("\n".join(f"  {line}" for line in dirty.splitlines()))
            return 1

    # 2. stage
    staged = stage(cfg, source, profile)

    # 3. validate
    if not args.no_validate:
        errors, warnings, lines, _ = validate.validate(staged)
        if lines:
            print("\n".join(lines))
        print(f"validate: {errors} error(s), {warnings} warning(s)")
        if errors:
            print("not packed - fix the errors, or rerun with --no-validate")
            return 1

    # 4. pack
    files = collect(staged)
    bad = check_xml(files)
    if bad:
        print("XML does not parse - the game would silently ignore the whole interface:")
        print("\n".join(f"  {b}" for b in bad))
        return 1
    archive = mpq.write_mpq(files)
    verify_roundtrip(archive, files)
    print(f"{profile}: {len(files)} files, {len(archive)} bytes, MPQ v1, round-trip OK")

    if args.release:
        out = DIST / f"v{cfg['meta']['version']}" / NAME
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(archive)
        print(f"release: {out.relative_to(REPO).as_posix()}  (commit {git('rev-parse', '--short', 'HEAD')})")
        if not args.deploy:
            return 0
    elif args.no_deploy:
        return 0

    # 5. deploy
    dest = INTERFACES / args.name
    if not deploy(archive, dest, args.wait):
        return 1
    print(f"deployed: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
