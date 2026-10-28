"""The series cards' map art: each battleground's picture, cut to the card from Blizzard's own art.

    python tools/series_art.py

Reads layout.toml's [series.art] - each map's texture, where across it the card centres and,
for a few, a zoom and where down the picture the zoomed slice sits -
and writes studio/public/maps/<slug>.jpg at twice the size obs.py's series_spec cuts the art
for, which ships as-is. The textures come from the CASCView extract (references/CASCView),
which is not in the repo, so this is run by hand when the art changes and what it writes is
committed - like the rest of what the studio ships, CI never makes it.

It is not part of gen.py --check: the extract may be missing, and a JPEG's bytes follow the
encoder, so the same cut can differ between machines without anything being wrong.
"""
import sys
from pathlib import Path

from PIL import Image

import gen
import obs

TEXTURES = (gen.REPO / "references" / "CASCView" / "mods" / "heroes.stormmod"
            / "base.stormassets" / "assets" / "textures")
OUT = gen.REPO / "studio" / "public" / "maps"
SCALE = 2          # the cut at twice the card, so a pool smaller than art_for scales it down
QUALITY = 88


def texture(name):
    """A texture by file name: the load screens are in their own folder, the home screens not."""
    for at in (TEXTURES / name, TEXTURES / "loadscreen" / name):
        if at.exists():
            return at
    sys.exit(f"series_art: {name} is not in {TEXTURES} - extract it with CASCView")


def cut(path, across, w, h, zoom=1.0, down=0.0):
    """The card's shape out of the picture, centred `across` its width and kept inside it, then
    scaled to w x h. Never stretched: the shape is the card's.

    At `zoom` 1 the cut is the picture's full height. A zoom takes a shorter slice of it, and
    `down` says where that slice sits in the height left over: 0 the top, 1 the bottom. It is
    for a mascot standing lower than the rest (user, 2026-10-27: Raynor's head on Volskaya is
    "way farther down ... than almost every other map"), lifting its head into line."""
    im = Image.open(path).convert("RGB")
    pw, ph = im.size
    ch = ph / zoom
    cw = ch * w / h
    x0 = min(max(across * pw - cw / 2, 0), pw - cw)
    y0 = (ph - ch) * down
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((w, h), Image.LANCZOS)


def main():
    cfg = gen.load_config()
    spec = obs.series_spec(obs.Band(cfg))
    w, h = SCALE * spec["art"]["w"], SCALE * spec["art"]["h"]
    table = cfg["series"]["art"]
    slugs = [m["slug"] for m in spec["maps"]]
    assert set(table) == set(slugs), f"[series.art] and [series] maps differ: {set(table) ^ set(slugs)}"
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        name, across, *lift = table[slug]
        zoom, down = (float(lift[0]), float(lift[1])) if lift else (1.0, 0.0)
        cut(texture(name), float(across), w, h, zoom, down).save(
            OUT / f"{slug}.jpg", quality=QUALITY, optimize=True, progressive=True)
        print(f"{slug}.jpg  {w}x{h}  from {name} at {across}" + (f", x{zoom} at {down} down" if lift else ""))


if __name__ == "__main__":
    main()
