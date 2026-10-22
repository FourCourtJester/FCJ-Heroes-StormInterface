"""The broadcast graphics' parts: everything the OBS layer draws over the interface, generated
from layout.toml through gen's top_bar_geometry, so the two can't drift apart.

    python tools/obs.py          (tools/gen.py writes it too, with the interface)

Writes `studio/src/generated/`, which the Single Studio app imports: `topbar.json` (every
number, as data), the name plate's CSS, and the parts as SVG and PNG. Vite resolves the CSS's
own `url()` references and hands the components hashed URLs, so nothing here needs to know
where it is served from.

The studio draws them: `studio/src/sources/TopBar.jsx` is the browser source and
`studio/src/control/panels/` is the operator's board. This file draws no page and holds no
data of its own - an operator's words and pictures live in the studio's own state.

The rule (docs/obs-topbar-handoff.md, user 2026-10-22): OBS draws the data AND the plates
under it. The interface keeps only the places, so it stays usable with no OBS running.
"""
import json
import math
import struct
import zlib
from pathlib import Path

import gen

OUT = gen.REPO / "studio" / "src" / "generated"
SW, SH = 1920, 1080                  # the locked resolution every number here is in
CAP, MID = 40, 20                    # the name plate's nine-slice: slanted caps, a stretching middle
PIP_PAD = 5                          # room in a pip's SVG for its shadow
BAN_RIM = 1.6                        # the ban tile's line (the plates' chrome, thinner at this size)
TAB_RIM = 2                          # the tab's line, down the sides and along the bottom only
GUIDE_LINE = 3                       # the alignment guide's outline
CYAN = ("#cbe8ff", "#ffffff")        # Blizzard's ColorLightCyanGradient (the level numbers)
BASE = ("#3b2d52", "#2a1f3c")        # the band's own fill, top to bottom
DARK = "#0d0a14"
BANNED_FOOT = "#c8323c"
FONT = "Saira Semi Condensed"        # open (Google Fonts); the licence question is in the handoff


class Band:
    """Everything the kit draws, in one place: gen's geometry plus the colours it paints with."""

    def __init__(self, cfg):
        g = gen.top_bar_geometry(cfg)
        bp = cfg["top_backplate"]
        self.cfg, self.g, self.bp = cfg, g, bp
        self.h, self.lean, self.d = g["height"], g["lean"], g["slant"]
        self.seam, self.ends = g["seam"], g["ends"]
        self.name, self.logo = g["name"], g["logo"]
        self.pips, self.pip = g["pips"], g["pip"]
        self.bans, self.ban_rows = g["bans"], g["ban_rows"]
        self.tabs = g["tabs"]
        self.rim = "#" + bp["rim"][0]
        self.rim_w = bp["rim_width"]
        self.stock = ["#" + c for c in bp["stock"]]
        self.team = {"blue": "#" + bp["blue_colour"], "red": "#" + bp["red_colour"]}
        self.sheen = bp["sheen"]
        self.logo_top = self.logo["blue"][2] - self.d      # the logo plate's top edge
        self.band_box = self.name["blue"][2]
        self.n0 = self.name["blue"][0]

    def hexpts(self, cx, cy, r, flat=True, fmt="{:.2f},{:.2f}"):
        a0 = 0 if flat else 30
        return " ".join(fmt.format(cx + r * math.cos(math.radians(a0 + 60 * k)),
                                   cy + r * math.sin(math.radians(a0 + 60 * k))) for k in range(6))


# ------------------------------------------------------------------ the name plate

def frame_svg(b, side):
    """The plates' frame, to nine-slice: rim, sheen and team line on a parallelogram, nothing
    else (the fill, glow and lattice are CSS behind it, so they stretch without distortion)."""
    w, h, d = 2 * CAP + MID, b.h, b.d
    poly = f"0,0 {w - d:.2f},0 {w},{h} {d:.2f},{h}"
    sheen = f"0,0 {w - d:.2f},0 {w - d / 2:.2f},{h / 2:.2f} {d / 2:.2f},{h / 2:.2f}"
    a, c = h - 5, h - 2
    line = (f"{3 + b.lean * a:.2f},{a} {w - d - 3 + b.lean * a:.2f},{a} "
            f"{w - d - 3 + b.lean * c:.2f},{c} {3 + b.lean * c:.2f},{c}")
    flip = "" if side == "blue" else f' transform="translate({w},0) scale(-1,1)"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><clipPath id="c"><polygon points="{poly}"/></clipPath></defs>
<g{flip}><g clip-path="url(#c)">
<polygon points="{sheen}" fill="#fff" fill-opacity="{b.sheen * .6:.3f}"/>
<polygon points="{line}" fill="{b.team[side]}"/>
<polygon points="{poly}" fill="none" stroke="{b.rim}" stroke-width="{2 * b.rim_w}"/>
</g></g></svg>
'''


def lattice_svg(b, side):
    """The hex lattice behind the plates, as the backplate's: one tile, repeated."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="21" height="24.25" viewBox="0 0 21 24.25">
<polygon points="{b.hexpts(7, 6.06, 7, fmt="{:.2f},{:.2f}")}" fill="none" stroke="{b.team[side]}" stroke-width="1"/>
<polygon points="{b.hexpts(17.5, 18.19, 7, fmt="{:.2f},{:.2f}")}" fill="none" stroke="{b.team[side]}" stroke-width="1"/>
</svg>
'''


def _rgba(hx, a):
    return f"rgba({int(hx[1:3], 16)},{int(hx[3:5], 16)},{int(hx[5:7], 16)},{a})"


def namebar_css(b):
    """The name plate as a web component: the markup it wants is in the comment."""
    lean, h, d = b.lean, b.h, b.d
    glow = lambda t, to: (f"linear-gradient(to {to},{_rgba(t, .92)} 0%,{_rgba(t, .58)} 22%,"
                          f"{_rgba(t, .32)} 50%,{_rgba(t, .58)} 80%,{_rgba(t, .95)} 100%)")
    fade = lambda to: f"linear-gradient(to {to},rgba(0,0,0,.7),rgba(0,0,0,.25) 50%,rgba(0,0,0,.4))"
    win = (f"polygon({5 + lean * 6:.2f}px 6px,{b.logo_top - 5 + lean * 6:.2f}px 6px,"
           f"{b.logo_top - 5 + lean * (h - 6):.2f}px {h - 6:.1f}px,{5 + lean * (h - 6):.2f}px {h - 6:.1f}px)")
    winr = (f"polygon(calc(100% - {5 + lean * 6:.2f}px) 6px,calc(100% - {b.logo_top - 5 + lean * 6:.2f}px) 6px,"
            f"calc(100% - {b.logo_top - 5 + lean * (h - 6):.2f}px) {h - 6:.1f}px,"
            f"calc(100% - {5 + lean * (h - 6):.2f}px) {h - 6:.1f}px)")
    return f'''/* FCJH top bar: the team name plate (OBS browser source). Generated by tools/obs.py from
   layout.toml; numbers at {SW} x {SH}. One .fcjh-band per team: a name plate, and a logo plate
   if the tournament has logos - leave .fcjh-logo out and the name plate runs on to the wing.

   <div class="fcjh-band blue">
     <div class="fcjh-name"><div class="t"><span>TEAM NAME</span></div></div>
     <div class="fcjh-logo"><div class="win"></div><img class="mark" src="logo.png"></div>
   </div>

   The plates' frame (rim, sheen, team line) is a nine-slice of frame_<team>.svg: {CAP} px
   slanted caps, a middle that stretches. The dark fill, the team glow and the lattice sit
   behind it as CSS, on the band, so they stretch without distortion and run on across the
   name and the logo as one. The band's outer end is fixed (the score pips hang off it), its
   inner end is the level wing's: blue's box is left {b.n0:.2f}, width {b.band_box:.2f}; red's mirrors. */

.fcjh-band {{ position: absolute; top: 0; height: {h}px; display: flex; isolation: isolate; }}
.fcjh-band.blue {{ left: {b.n0:.2f}px; width: {b.band_box:.2f}px;
  clip-path: polygon(0 0, calc(100% - {d:.2f}px) 0, 100% 100%, {d:.2f}px 100%);
  background: {glow(b.team["blue"], "left")}, linear-gradient({BASE[0]}, {BASE[1]}); }}
.fcjh-band.red {{ left: {SW - b.n0 - b.band_box:.2f}px; width: {b.band_box:.2f}px; flex-direction: row-reverse;
  clip-path: polygon({d:.2f}px 0, 100% 0, calc(100% - {d:.2f}px) 100%, 0 100%);
  background: {glow(b.team["red"], "right")}, linear-gradient({BASE[0]}, {BASE[1]}); }}
/* the lattice, fading along the band as the backplate's */
.fcjh-band::before {{ content: ""; position: absolute; inset: 0; z-index: -1; }}
.fcjh-band.blue::before {{ background: url(lattice_blue.svg); -webkit-mask-image: {fade("left")}; mask-image: {fade("left")}; }}
.fcjh-band.red::before {{ background: url(lattice_red.svg); -webkit-mask-image: {fade("right")}; mask-image: {fade("right")}; }}

.fcjh-name, .fcjh-logo {{ position: relative; height: 100%; }}
.fcjh-name {{ flex: 1 1 0; min-width: 0; }}
.fcjh-logo {{ flex: 0 0 {b.logo["blue"][2]:.2f}px; }}
.blue .fcjh-logo {{ margin-left: -{d + b.rim_w:.2f}px; }}   /* its rim on the name's: one line between */
.red .fcjh-logo {{ margin-right: -{d + b.rim_w:.2f}px; }}
/* the nine-slice frame, over each plate */
.fcjh-name::after, .fcjh-logo::after {{ content: ""; position: absolute; inset: 0; z-index: 1;
  border-style: solid; border-width: 0 {CAP}px; border-image-slice: 0 {CAP} fill;
  border-image-width: 0 {CAP}px; border-image-repeat: stretch; pointer-events: none; }}
.blue .fcjh-name::after, .blue .fcjh-logo::after {{ border-image-source: url(frame_blue.svg); }}
.red .fcjh-name::after, .red .fcjh-logo::after {{ border-image-source: url(frame_red.svg); }}

/* the name: centred at the plate's mid-height, 12 px clear of its slants, shrunk to fit */
.fcjh-name .t {{ position: absolute; inset: 0 {d / 2 + 12:.2f}px; z-index: 2; display: flex;
  align-items: center; justify-content: center; }}
.fcjh-name .t span {{ font: 700 24px/1 '{FONT}', sans-serif; letter-spacing: .04em;
  color: #e4f3ff; -webkit-text-stroke: 3px #000; paint-order: stroke fill; white-space: nowrap;
  margin-top: 2px; flex: none; }}   /* flex: none - it keeps its natural width, so a long
                                       name can be measured and shrunk to fit */

/* the logo: a dark window, the mark centred on it */
.fcjh-logo .win {{ position: absolute; inset: 0; background: rgba(13,10,20,.5); }}
.blue .fcjh-logo .win {{ clip-path: {win}; }}
.red .fcjh-logo .win {{ clip-path: {winr}; }}
.fcjh-logo .mark {{ position: absolute; left: 50%; top: 50%; width: 46px; height: 46px;
  transform: translate(-50%, -52%); z-index: 2; object-fit: contain; }}
'''


# ------------------------------------------------------------------ the score pips

def pip_svg(b, fill, opacity, gloss):
    r, w = b.pip["r"], b.pip["w"]
    sw, sh = w + 2 * PIP_PAD, 2 * r + 2 * PIP_PAD
    cx, cy = sw / 2, sh / 2
    g = (f'\n<polygon points="{b.hexpts(cx, cy - 2, r * .52, flat=False)}" fill="#fff" fill-opacity=".35"/>'
         if gloss else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{sw:.2f}" height="{sh:.2f}" viewBox="0 0 {sw:.2f} {sh:.2f}">
<defs><filter id="s" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="1" stdDeviation="1.6" flood-color="#000" flood-opacity=".7"/></filter></defs>
<polygon points="{b.hexpts(cx, cy, r, flat=False)}" fill="{fill}" fill-opacity="{opacity}" stroke="{b.rim}" stroke-width="2.2" stroke-linejoin="round" filter="url(#s)"/>{g}
</svg>
'''


# ------------------------------------------------------------------ the tabs and the ban tiles

def _lean_poly(x, y, w, h, d, team):
    """The parallelogram a plate's bounding box holds: blue leans \\ (its bottom edge d px
    further in), red leans / (the mirror)."""
    if team == "blue":
        return [(x, y), (x + w - d, y), (x + w, y + h), (x + d, y + h)]
    return [(x + d, y), (x + w, y), (x + w - d, y + h), (x, y + h)]


def _box(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def tab_svg(b, team):
    """The division (blue) / game (red) tab, hung from the level wing: the stock dark the
    backplate fades to, with a chrome line down both sides and along the bottom - none across
    the top, where the band's own rim closes it. OBS's art since 2026-10-22 (the rule)."""
    poly = b.tabs[team]["poly"]
    x0, y0, w, h = _box(poly)
    p = [(x - x0, y - y0) for x, y in poly]
    at = lambda q: f"{q[0]:.2f},{q[1]:.2f}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}" height="{h:.2f}" viewBox="0 0 {w:.2f} {h:.2f}">
<polygon points="{" ".join(at(q) for q in p)}" fill="{b.stock[1]}" fill-opacity=".92"/>
<polyline points="{" ".join(at(q) for q in (p[1], p[2], p[3], p[0]))}" fill="none" stroke="{b.rim}" stroke-width="{TAB_RIM}" stroke-linejoin="round"/>
</svg>
'''


def ban_tile_svg(b, team):
    """One empty ban tile: a parallelogram at the plates' lean, dark, with a thin chrome line.
    Every tile a side is the same shape, so the page repeats this one."""
    poly = b.bans[team][0]
    x0, y0, w, h = _box(poly)
    p = [(x - x0 + BAN_RIM / 2, y - y0 + BAN_RIM / 2) for x, y in poly]
    at = lambda q: f"{q[0]:.2f},{q[1]:.2f}"
    w, h = w + BAN_RIM, h + BAN_RIM
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}" height="{h:.2f}" viewBox="0 0 {w:.2f} {h:.2f}">
<polygon points="{" ".join(at(q) for q in p)}" fill="{DARK}" fill-opacity=".85" stroke="{b.rim}" stroke-width="{BAN_RIM}" stroke-linejoin="round"/>
</svg>
'''


def _tile_clip(b, team):
    """The ban tile's shape as a CSS clip-path, in its own box: the portrait is clipped to it."""
    poly = b.bans[team][0]
    x0, y0, _, _ = _box(poly)
    return "polygon(" + ",".join(f"{x - x0:.2f}px {y - y0:.2f}px" for x, y in poly) + ")"


# ------------------------------------------------------------------ PNG: the mask and the guide

def _png_rgba(w, h, data):
    """A plain RGBA PNG (no PIL in tools/): data is w*h*4 bytes, row-major."""
    row = 4 * w
    raw = b"".join(b"\0" + bytes(data[y * row:(y + 1) * row]) for y in range(h))
    def chunk(tag, payload):
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def _paint(data, poly, colour, line=None):
    """Composite one convex polygon into an RGBA buffer, anti-aliased from its signed distance
    (gen.convex_sdf): filled when `line` is None, else an outline that many px wide. Only the
    shape's own box is walked, so a sheet of small shapes costs almost nothing."""
    sd = gen.convex_sdf([tuple(p) for p in poly])
    x0, y0, w, h = _box(poly)
    pad = (line or 0) / 2 + 2
    r, g, bl = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(max(0, int(y0 - pad)), min(SH, int(y0 + h + pad) + 1)):
        for x in range(max(0, int(x0 - pad)), min(SW, int(x0 + w + pad) + 1)):
            d = sd(x + 0.5, y + 0.5)
            a = (0.5 - d) if line is None else (line / 2 - abs(d) + 0.5)
            a = 0.0 if a < 0 else 1.0 if a > 1 else a
            if a <= 0:
                continue
            i = (y * SW + x) * 4
            was = data[i + 3] / 255
            out = a + was * (1 - a)                      # over, on a transparent sheet
            for k, v in enumerate((r, g, bl)):
                data[i + k] = round((v * a + data[i + k] * was * (1 - a)) / out)
            data[i + 3] = round(out * 255)


def event_mask_png(b):
    """Blizzard's hexagon, white on a clear sheet: an OBS image mask for the tournament logo."""
    data = bytearray(SW * SH * 4)
    _paint(data, b.bp["hexagon"], "#ffffff")
    return _png_rgba(SW, SH, data)


def guide_png(b):
    """Every place as an orange outline on a clear sheet: lay it over a scene while lining
    the sources up, then hide it."""
    data = bytearray(SW * SH * 4)
    orange = "#ff8c00"
    for team in ("blue", "red"):
        for key in ("name", "logo"):
            x, y, w, h = getattr(b, key)[team]
            _paint(data, _lean_poly(x, y, w, h, b.d, team), orange, GUIDE_LINE)
        for cx, cy in b.pips[team]:
            _paint(data, [tuple(float(v) for v in p.split(","))
                          for p in b.hexpts(cx, cy, b.pip["r"], flat=False).split()], orange, GUIDE_LINE)
        for tile in b.bans[team]:
            _paint(data, tile, orange, GUIDE_LINE)
        _paint(data, b.tabs[team]["poly"], orange, GUIDE_LINE)
    _paint(data, b.bp["hexagon"], orange, GUIDE_LINE)
    return _png_rgba(SW, SH, data)


# ------------------------------------------------------------------ every number, as data

def spec(b):
    r2 = lambda v: round(float(v), 2)
    poly = lambda p: [[r2(x), r2(y)] for x, y in p]
    return {
        "about": f"FCJH top bar, the OBS layer: every number in screen px at {SW} x {SH} "
                 f"(x 4/3 at 1440p). Red mirrors blue about x {SW // 2}, except the two tabs, which "
                 "follow Blizzard's hexagon. Generated by tools/obs.py from layout.toml "
                 "([top_bar]) and gen.top_bar_geometry; edit there, not here.",
        "band": {"top": 0, "height": b.h, "lean_per_px_down": b.lean, "slant_run": r2(b.d),
                 "seam": r2(b.seam), "wing_ends": [r2(v) for v in b.ends]},
        "colours": {"blue": b.team["blue"], "red": b.team["red"], "rim": b.rim, "stock": b.stock,
                    "base_top": BASE[0], "base_bottom": BASE[1], "dark": DARK,
                    "name_text_gradient": list(CYAN), "tab_text": "#cbe8ff", "banned_foot": BANNED_FOOT},
        "name_plate": {"css": "namebar.css", "frame": {"blue": "frame_blue.svg", "red": "frame_red.svg"},
                       "lattice": {"blue": "lattice_blue.svg", "red": "lattice_red.svg"},
                       "nine_slice": {"width": 2 * CAP + MID, "caps": CAP, "stretch": MID},
                       "blue": {"left": r2(b.name["blue"][0]), "width": r2(b.band_box)},
                       "red": {"left": r2(b.name["red"][0]), "width": r2(b.band_box)},
                       "name_font_px_max": 24, "name_clear_of_slants_px": 12,
                       "logo_plate": {"width": r2(b.logo["blue"][2]), "left": {"blue": r2(b.logo["blue"][0]),
                                      "red": r2(b.logo["red"][0])},
                                      "at": "the band's inner end; leave it out with no logo", "mark_px": 46}},
        "score_pips": {"svg": {"blue_won": "pip_blue.svg", "red_won": "pip_red.svg", "not_won": "pip_empty.svg"},
                       "svg_size": [r2(b.pip["w"] + 2 * PIP_PAD), r2(b.pip["h"] + 2 * PIP_PAD)],
                       "radius": r2(b.pip["r"]), "gap": b.cfg["top_bar"]["pip_gap"],
                       "off_the_name": b.cfg["top_bar"]["pip_off_name"],
                       "per_side": {"best_of_3": 2, "best_of_5": 3, "best_of_7": 4},
                       "fill_order": "from the name outward (index 0 first)",
                       "centres": {t: [[r2(x), r2(y)] for x, y in b.pips[t]] for t in ("blue", "red")}},
        "bans": {"tiles_per_side": b.cfg["top_bar"]["bans"],
                 "tile": f"{b.cfg['top_bar']['ban_tile']} px parallelogram, "
                         f"{b.cfg['top_bar']['ban_pitch']} px pitch, the band's lean",
                 "svg": {"blue": "ban_blue.svg", "red": "ban_red.svg"},
                 "y": [r2(v) for v in b.ban_rows],
                 "banned": "the hero's portrait, desaturated, with a 4 px banned_foot along the bottom",
                 "polygons": {t: [poly(tile) for tile in b.bans[t]] for t in ("blue", "red")},
                 "order": "index 0 innermost", "optional": True},
        "tabs": {"division": {"svg": "tab_division.svg", "polygon": poly(b.tabs["blue"]["poly"]),
                              "text_centre": [r2(v) for v in b.tabs["blue"]["text"]], "example": "DIVISION 1"},
                 "game_count": {"svg": "tab_game.svg", "polygon": poly(b.tabs["red"]["poly"]),
                                "text_centre": [r2(v) for v in b.tabs["red"]["text"]], "example": "GAME 3 OF 5"},
                 "font_px": 14,
                 "note": "OBS's art since 2026-10-22, with its words: the interface draws nothing here"},
        "event_logo": {"hexagon": poly(b.bp["hexagon"]),
                       "centre": [r2(gen.top_backplate_geometry(b.cfg)["centre"]), b.h],
                       "mask": "event_mask.png",
                       "note": "over Blizzard's Nexus hexagon; event_mask.png is that hexagon, white, "
                               f"on a {SW} x {SH} clear sheet"},
        "guide": f"guide.png: every place above as an orange outline on a clear {SW} x {SH} sheet, "
                 "for lining up a scene",
        # ready to place with: every piece as [x, y, width, height] on the 1920 x 1080 page,
        # and the shapes that can't be a box as CSS clip paths in their own box
        "boxes": {
            "band": {t: [r2(v) for v in b.name[t]] for t in ("blue", "red")},
            "logo": {t: [r2(v) for v in b.logo[t]] for t in ("blue", "red")},
            "pips": {t: [[r2(x - b.pip["w"] / 2), r2(y - b.pip["h"] / 2),
                          r2(b.pip["w"]), r2(b.pip["h"])] for x, y in b.pips[t]]
                     for t in ("blue", "red")},
            "bans": {t: [[r2(v) for v in _box(tile)] for tile in b.bans[t]] for t in ("blue", "red")},
            "tabs": {"division": [r2(v) for v in _box(b.tabs["blue"]["poly"])],
                     "game": [r2(v) for v in _box(b.tabs["red"]["poly"])]},
            "event": [r2(v) for v in _box(b.bp["hexagon"])],
        },
        "clip": {
            "bans": {t: _tile_clip(b, t) for t in ("blue", "red")},
            "event": "polygon(" + ",".join(f"{x - _box(b.bp['hexagon'])[0]:.2f}px "
                                           f"{y - _box(b.bp['hexagon'])[1]:.2f}px"
                                           for x, y in b.bp["hexagon"]) + ")",
        },
    }


# ------------------------------------------------------------------ the folder

GENERATED = ("<!-- Generated by tools/obs.py from layout.toml. Do not edit by hand:\n"
             "     change layout.toml (or tools/obs.py) and rebuild. -->\n")


def files(cfg):
    """Everything under studio/src/generated/, by path relative to it."""
    b = Band(cfg)
    enc = lambda s: s.encode("utf-8")
    out = {
        Path("namebar.css"): enc(namebar_css(b)),
        Path("pip_empty.svg"): enc(pip_svg(b, DARK, .6, False)),
        Path("tab_division.svg"): enc(tab_svg(b, "blue")),
        Path("tab_game.svg"): enc(tab_svg(b, "red")),
        Path("event_mask.png"): event_mask_png(b),
        Path("guide.png"): guide_png(b),
        Path("topbar.json"): enc(json.dumps(spec(b), indent=2, ensure_ascii=False) + "\n"),
    }
    for team in ("blue", "red"):
        out[Path(f"frame_{team}.svg")] = enc(frame_svg(b, team))
        out[Path(f"lattice_{team}.svg")] = enc(lattice_svg(b, team))
        out[Path(f"pip_{team}.svg")] = enc(pip_svg(b, b.team[team], 1, True))
        out[Path(f"ban_{team}.svg")] = enc(ban_tile_svg(b, team))
    return out


def _same(path, data):
    """Is the file already what we'd write? git (core.autocrlf) may check a text file out with
    CRLF, which isn't a change - but a PNG is bytes, and "fixing" its newlines would make it
    differ from itself on every run."""
    on_disk = path.read_bytes()
    return on_disk == data if path.suffix in (".png",) else on_disk.replace(b"\r\n", b"\n") == data


def write(cfg, out=OUT):
    changed = []
    for rel, data in files(cfg).items():
        path = out / rel
        if not path.is_file() or not _same(path, data):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            changed.append(rel)
    return changed


def stale(cfg, out=OUT):
    return [rel for rel, data in files(cfg).items()
            if not (out / rel).is_file() or not _same(out / rel, data)]


def main():
    changed = write(gen.load_config())
    print("\n".join(f"wrote studio/src/generated/{rel.as_posix()}" for rel in changed)
          or "studio/src/generated/ up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
