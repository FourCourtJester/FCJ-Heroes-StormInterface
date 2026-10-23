"""The broadcast graphics' parts: everything the OBS layer draws over the interface, generated
from layout.toml through gen's top_bar_geometry, so the two can't drift apart.

    python tools/obs.py          (tools/gen.py writes it too, with the interface)

Writes `studio/src/generated/`, which the Single Studio app imports: `topbar.json` (every
number, as data) and the parts as SVG and PNG. **Pictures and numbers, and nothing else**
(user, 2026-10-22): no CSS, no markup, no page. `/studio` owns the whole broadcast package -
`studio/src/sources/Game.jsx` draws the graphic, `studio/src/sources/game.css` styles it from
these numbers, and `studio/src/control/panels/` is the operator's board. This file holds no
data of its own either; an operator's words and pictures live in the studio's own state.

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
PUBLIC = Path("..") / ".." / "public" / "masks"   # studio/public/masks, shipped as-is
SW, SH = 1920, 1080                  # the locked resolution every number here is in
CAP, MID = 40, 20                    # the name plate's nine-slice: slanted caps, a stretching middle
PIP_PAD = 5                          # room in a pip's SVG for its shadow
BAN_RIM = 1.6                        # the ban tile's line (the plates' chrome, thinner at this size)
TAB_RIM = 2                          # the tab's line, down the sides and along the bottom only
TAB_CAP = 24                         # px at each end of the tab's art that hold its slants;
TAB_MID = 20                         # ...and the flat middle between them, which stretches
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
        self.sb = cfg["standby"]                          # the standby screen's own band
        self.cam = cfg["webcam"]                          # ...and the webcam frames over it
        self.logo_top = self.logo["blue"][2] - self.d      # the logo plate's top edge
        self.band_box = self.name["blue"][2]
        self.n0 = self.name["blue"][0]

    def hexpts(self, cx, cy, r, flat=True, fmt="{:.2f},{:.2f}"):
        a0 = 0 if flat else 30
        return " ".join(fmt.format(cx + r * math.cos(math.radians(a0 + 60 * k)),
                                   cy + r * math.sin(math.radians(a0 + 60 * k))) for k in range(6))


# ------------------------------------------------------------------ the name plate

def frame_svg(b, side, line=True, height=None, cap=None):
    """The plates' frame, to nine-slice: rim, sheen and team line on a parallelogram, nothing
    else (the fill, glow and lattice are CSS behind it, so they stretch without distortion).

    The rim runs round three sides only - the outer slant, the top and the bottom - and never
    the INNER slant, the one facing the middle of the screen. Whatever a plate butts against
    there draws that line already: the logo plate's outer rim for the name plate, and the
    interface's own level wing for whichever plate is innermost. Two rims against each other
    read as one doubled border, so the leading edge gives way (user, 2026-10-22)."""
    h = b.h if height is None else height
    # a cap has to be wider than the slant it holds, or stretching the middle shears the ends
    cap = CAP if cap is None else cap
    w, d = 2 * cap + MID, b.lean * h
    assert cap >= d, f"a {cap} px cap cannot hold a {d:.2f} px slant"
    poly = f"0,0 {w - d:.2f},0 {w},{h} {d:.2f},{h}"
    # the same points, opened out at the inner slant: top-right -> top-left -> bottom-left ->
    # bottom-right, so the stroke covers every edge but that one
    rim = f"{w - d:.2f},0 0,0 {d:.2f},{h} {w},{h}"
    sheen = f"0,0 {w - d:.2f},0 {w - d / 2:.2f},{h / 2:.2f} {d / 2:.2f},{h / 2:.2f}"
    a, c = h - 5, h - 2
    pts = (f"{3 + b.lean * a:.2f},{a} {w - d - 3 + b.lean * a:.2f},{a} "
           f"{w - d - 3 + b.lean * c:.2f},{c} {3 + b.lean * c:.2f},{c}")
    # the logo plate takes this same frame without the team line: a bar of team colour under
    # a team's own logo says nothing the logo doesn't (user, 2026-10-22)
    team_line = f'\n<polygon points="{pts}" fill="{b.team[side]}"/>' if line else ""
    flip = "" if side == "blue" else f' transform="translate({w},0) scale(-1,1)"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><clipPath id="c"><polygon points="{poly}"/></clipPath></defs>
<g{flip}><g clip-path="url(#c)">
<polygon points="{sheen}" fill="#fff" fill-opacity="{b.sheen * .6:.3f}"/>{team_line}
<polyline points="{rim}" fill="none" stroke="{b.rim}" stroke-width="{2 * b.rim_w}"/>
</g></g></svg>
'''


def matchup_frame_svg(b):
    """A team's container on the standby screen's band, to nine-slice: a long bar coming to a
    point at each end, at HALF its height.

    One file serves both teams, because the shape is symmetrical and the rim is chrome on
    either side - what makes a container blue or red is the wash and the lattice behind it,
    which are CSS. The game band's plates carry a team line along their bottom edge; this one
    doesn't, because at this size the wash says it already.

    The caps hold the two points and the middle is a straight run of rim, top and bottom, so
    the bar stretches to whatever a team's name needs without the points shearing."""
    sb = b.sb
    h, cap = sb["team_h"], sb["team_cap"]
    pt = b.lean * h / 2                                   # how far in a point starts
    assert cap >= pt + 2 * b.rim_w, (
        f"a {cap} px cap cannot hold a {pt:.2f} px point and a {b.rim_w} px rim")
    w = 2 * cap + MID
    poly = (f"{pt:.2f},0 {w - pt:.2f},0 {w},{h / 2:.2f} "
            f"{w - pt:.2f},{h} {pt:.2f},{h} 0,{h / 2:.2f}")
    # the gloss is the top half of the shape, which here is a clean trapezoid
    sheen = f"{pt:.2f},0 {w - pt:.2f},0 {w},{h / 2:.2f} 0,{h / 2:.2f}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><clipPath id="c"><polygon points="{poly}"/></clipPath></defs>
<g clip-path="url(#c)">
<polygon points="{sheen}" fill="#fff" fill-opacity="{b.sheen * .6:.3f}"/>
<polygon points="{poly}" fill="none" stroke="{b.rim}" stroke-width="{2 * b.rim_w}"/>
</g></svg>
'''


def lattice_svg(b, side):
    """The hex lattice behind the plates, as the backplate's: one tile, repeated. `side` is a
    team, or "neutral" for a plate that belongs to nobody - the standby screen's, drawn in the
    chrome colour instead of a team's."""
    colour = b.rim if side == "neutral" else b.team[side]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="21" height="24.25" viewBox="0 0 21 24.25">
<polygon points="{b.hexpts(7, 6.06, 7, fmt="{:.2f},{:.2f}")}" fill="none" stroke="{colour}" stroke-width="1"/>
<polygon points="{b.hexpts(17.5, 18.19, 7, fmt="{:.2f},{:.2f}")}" fill="none" stroke="{colour}" stroke-width="1"/>
</svg>
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


def _tab_inset(b, team):
    """A tab's text box, as [left, right] px in from its own box: the upright rectangle the
    tab contains. The two differ - a tab's outer side follows the plates' lean and its inner
    side Blizzard's hexagon - which is why this is worked out here rather than in CSS."""
    poly = b.tabs[team]["poly"]
    x0, _, w, _ = _box(poly)
    left, right = _upright(poly)
    return [round(left - x0, 2), round(x0 + w - right, 2)]


def _logo_clip(b, team):
    """The logo plate's own parallelogram as a CSS clip path in its own box: a logo fills the
    plate and is cut to its shape, so none of the plate behind it shows (user, 2026-10-22).
    The plate leans with the band - blue's bottom edge sits a slant's run further in, red's
    the other way."""
    d = f"{b.d:.2f}px"
    if team == "blue":
        return f"polygon(0 0, calc(100% - {d}) 0, 100% 100%, {d} 100%)"
    return f"polygon({d} 0, 100% 0, calc(100% - {d}) 100%, 0 100%)"


def _pip_row(b):
    """The box the pips are laid out in, per side: wide enough for every pip a best of 7
    draws, placed so the first hexagon's centre lands on its designed one once each item has
    taken its negative margin (see score_pips.item_margin)."""
    svg_w = b.pip["w"] + 2 * PIP_PAD
    svg_h = b.pip["h"] + 2 * PIP_PAD
    margin = (b.cfg["top_bar"]["pip_gap"] - 2 * PIP_PAD) / 2
    pitch = svg_w + 2 * margin                      # = the hexagon's width plus the gap
    cx0, cy = b.pips["blue"][0]
    right = cx0 + svg_w / 2 + margin                # blue fills right to left, from the name
    left = right - pitch * len(b.pips["blue"])
    top = cy - svg_h / 2
    r2 = lambda v: round(float(v), 2)
    return {"blue": [r2(left), r2(top), r2(pitch * len(b.pips["blue"])), r2(svg_h)],
            "red": [r2(SW - right), r2(top), r2(pitch * len(b.pips["blue"])), r2(svg_h)]}


def _upright(poly):
    """The largest upright rectangle inside a four-sided slanted shape, as (x0, x1): the top
    and bottom edges' overlap. Text inside it never crosses a leaning edge."""
    (ax, ay), (bx, _), (cx, _), (dx, dy) = poly
    top, bottom = sorted([ax, bx]), sorted([dx, cx])
    return max(top[0], bottom[0]), min(top[1], bottom[1])


def _box(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def tab_svg(b, team):
    """The division (blue) / game (red) tab, hung from the level wing: the stock dark the
    backplate fades to, with a chrome line down both sides and along the bottom - none across
    the top, where the band's own rim closes it. OBS's art since 2026-10-22 (the rule).

    Drawn to be stretched, not scaled: TAB_CAP px at each end hold the two slants, and the
    middle between them is flat, so a tab that grows with its words keeps its ends' angles
    (user, 2026-10-22: "really its just extendable middle parts though"). The two sides lean
    differently - the outer one with the plates, the inner one with Blizzard's hexagon - so
    each cap carries its own."""
    left_run, right_run = _tab_inset(b, team)       # each side's horizontal run over the height
    h = b.ban_rows[1] - b.h                     # the tab hangs from the band to the tiles' bottom
    w = 2 * TAB_CAP + TAB_MID
    outer, inner = (left_run, right_run) if team == "blue" else (right_run, left_run)
    if team == "blue":                              # outer side on the left, both leaning right
        p = [(0, 0), (w - inner, 0), (w, h), (outer, h)]
    else:                                           # mirrored: both leaning left
        p = [(inner, 0), (w, 0), (w - outer, h), (0, h)]
    at = lambda q: f"{q[0]:.2f},{q[1]:.2f}"
    rim = (p[1], p[2], p[3], p[0]) if team == "blue" else (p[0], p[3], p[2], p[1])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}" height="{h:.2f}" viewBox="0 0 {w:.2f} {h:.2f}" preserveAspectRatio="none">
<polygon points="{" ".join(at(q) for q in p)}" fill="{b.stock[1]}" fill-opacity=".92"/>
<polyline points="{" ".join(at(q) for q in rim)}" fill="none" stroke="{b.rim}" stroke-width="{TAB_RIM}" stroke-linejoin="round"/>
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


def _paint(data, poly, colour, line=None, sheet=None):
    """Composite one convex polygon into an RGBA buffer, anti-aliased from its signed distance
    (gen.convex_sdf): filled when `line` is None, else an outline that many px wide. Only the
    shape's own box is walked, so a sheet of small shapes costs almost nothing.

    `sheet` is the buffer's size, for the masks that are not screen-sized - a cam mask is the
    window's own 800 x 450, because OBS stretches a mask over the source it filters."""
    sw, sh = sheet or (SW, SH)
    sd = gen.convex_sdf([tuple(p) for p in poly])
    x0, y0, w, h = _box(poly)
    pad = (line or 0) / 2 + 2
    r, g, bl = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(max(0, int(y0 - pad)), min(sh, int(y0 + h + pad) + 1)):
        for x in range(max(0, int(x0 - pad)), min(sw, int(x0 + w + pad) + 1)):
            d = sd(x + 0.5, y + 0.5)
            a = (0.5 - d) if line is None else (line / 2 - abs(d) + 0.5)
            a = 0.0 if a < 0 else 1.0 if a > 1 else a
            if a <= 0:
                continue
            i = (y * sw + x) * 4
            was = data[i + 3] / 255
            out = a + was * (1 - a)                      # over, on a transparent sheet
            for k, v in enumerate((r, g, bl)):
                data[i + k] = round((v * a + data[i + k] * was * (1 - a)) / out)
            data[i + 3] = round(out * 255)


def cam_window(b, side, x=0, y=0, size=None):
    """A cam window's outline: a rectangle with two opposite corners cut back at the plates'
    angle. The left window leans like a blue plate and the right one mirrors it, so the pair
    reads as the band does rather than as two identical boxes.

    `size` overrides the pair's, for the one-camera layout - the chamfer is the same run at
    either size, so the cut edge stays at the plates' angle rather than scaling with the box."""
    cam = b.cam
    (w, h) = size or (cam["w"], cam["h"])
    cy = cam["chamfer"] * h                               # a fraction of the height
    cx = b.lean * cy
    if side == "left":
        pts = [(0, 0), (w - cx, 0), (w, cy), (w, h), (cx, h), (0, h - cy)]
    else:
        pts = [(cx, 0), (w, 0), (w, h - cy), (w - cx, h), (0, h), (0, cy)]
    return [(x + px, y + py) for px, py in pts]


def cam_places(b):
    """Where the two windows land. They hang in the standby screen's free middle - under its
    countdown bug, over its band - so the two browser sources stack in OBS without either one
    having to move, and the free space is read off the band rather than typed."""
    cam, sb = b.cam, b.sb
    block = cam["h"] + cam["plate_gap"] + cam["plate_h"]
    top = sb["bug_h"]                                    # the bug's bottom edge
    bottom = SH - sb["plate_bottom"] - sb["plate_h"]     # the band's message board, its top
    assert block <= bottom - top, "the cam block is taller than the screen's free middle"
    left = (SW - (2 * cam["w"] + cam["gap"])) / 2
    solo_block = cam["solo_h"] + cam["plate_gap"] + cam["plate_h"]
    assert solo_block <= bottom - top, "the solo window is taller than the screen's free middle"
    return {"top": top + (bottom - top - block) / 2, "free": (top, bottom),
            "left": left, "right": left + cam["w"] + cam["gap"],
            "solo_left": (SW - cam["solo_w"]) / 2,
            "solo_top": top + (bottom - top - solo_block) / 2}


def cam_frame_svg(b, side, size=None):
    """The chrome round a cam window, at its own size - no nine-slice, because a window is a
    fixed box rather than something that stretches to a name. Nothing is filled: what the
    frame surrounds is the camera, showing through from the OBS source underneath."""
    cam = b.cam
    (w, h), rim = size or (cam["w"], cam["h"]), cam["rim"]
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in cam_window(b, side, size=size))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><clipPath id="c"><polygon points="{pts}"/></clipPath></defs>
<g clip-path="url(#c)">
<polygon points="{pts}" fill="none" stroke="{b.rim}" stroke-width="{2 * rim}"/>
</g></svg>
'''


def cam_mask_png(b, side, size=None):
    """The window, solid white on a clear sheet: OBS's Image Mask/Blend filter in "Alpha Mask
    (Alpha Channel)" mode, on the camera source under the frame. Without it the camera is a
    rectangle and its corners stick out past the chrome.

    One mask per lean, drawn at the largest window there is, and the operator scales it onto
    whichever they are filling - OBS stretches a mask over its source either way. That works
    because the chamfer is a fraction rather than a length, so the solo window is the pair's
    enlarged rather than the pair's with bigger corners cut off it (user, 2026-10-23).

    These are the one thing here a broadcaster needs as a FILE, so they go to studio/public,
    which ships as-is: /masks/cam_mask_left.png on the published site, rather than something
    only a clone of the repo has."""
    w, h = size or (b.cam["w"], b.cam["h"])
    data = bytearray(w * h * 4)
    _paint(data, cam_window(b, side, size=(w, h)), "#ffffff", sheet=(w, h))
    return _png_rgba(w, h, data)


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
    # the webcam windows, so a camera can be lined up by eye under its frame
    at = cam_places(b)
    for side in ("left", "right"):
        _paint(data, cam_window(b, side, at[side], at["top"]), orange, GUIDE_LINE)
    _paint(data, cam_window(b, "left", at["solo_left"], at["solo_top"],
                            size=(b.cam["solo_w"], b.cam["solo_h"])), orange, GUIDE_LINE)
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
        "screen": [SW, SH],
        "band": {"top": 0, "height": b.h, "lean_per_px_down": b.lean, "slant_run": r2(b.d),
                 "seam": r2(b.seam), "wing_ends": [r2(v) for v in b.ends]},
        "colours": {"blue": b.team["blue"], "red": b.team["red"], "rim": b.rim, "stock": b.stock,
                    "base_top": BASE[0], "base_bottom": BASE[1], "dark": DARK,
                    "name_text_gradient": list(CYAN), "tab_text": "#cbe8ff", "banned_foot": BANNED_FOOT},
        "name_plate": {"frame": {"blue": "frame_blue.svg", "red": "frame_red.svg"},
                       "logo_frame": {"blue": "frame_logo_blue.svg", "red": "frame_logo_red.svg"},
                       "lattice": {"blue": "lattice_blue.svg", "red": "lattice_red.svg"},
                       "nine_slice": {"width": 2 * CAP + MID, "caps": CAP, "stretch": MID},
                       "blue": {"left": r2(b.name["blue"][0]), "width": r2(b.band_box)},
                       "red": {"left": r2(b.name["red"][0]), "width": r2(b.band_box)},
                       "name_font_px_max": 24,
                       # how far the logo plate laps back over the name plate, so the two
                       # rims land on each other and read as one seam
                       "logo_lap": r2(b.d + b.rim_w),
                       "logo_plate": {"width": r2(b.logo["blue"][2]), "left": {"blue": r2(b.logo["blue"][0]),
                                      "red": r2(b.logo["red"][0])},
                                      "at": "the band's inner end; leave it out with no logo", "mark_px": 46}},
        "score_pips": {"svg": {"blue_won": "pip_blue.svg", "red_won": "pip_red.svg", "not_won": "pip_empty.svg"},
                       "svg_size": [r2(b.pip["w"] + 2 * PIP_PAD), r2(b.pip["h"] + 2 * PIP_PAD)],
                       "radius": r2(b.pip["r"]), "gap": b.cfg["top_bar"]["pip_gap"],
                       "off_the_name": b.cfg["top_bar"]["pip_off_name"],
                       "pad": PIP_PAD,
                       # a pip's SVG carries `pad` each side for its shadow, and the design's
                       # gap is between the HEXAGONS - so neighbouring SVGs overlap by that
                       # much. Laid out in a row, each one takes this much margin either side
                       # (negative): a flex gap cannot overlap, a margin can
                       "item_margin": r2((b.cfg["top_bar"]["pip_gap"] - 2 * PIP_PAD) / 2),
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
        # a tab grows with its words, so what is fixed is its INNER edge - the one 5 px off
        # Blizzard's hexagon. `anchor` is that edge's distance from the side of the screen it
        # faces, for a CSS `right` (division) or `left` (game); `cap` is how much of the art
        # at each end holds a slant and must not stretch.
        "tabs": {"cap": TAB_CAP, "slice": [TAB_CAP, TAB_MID, TAB_CAP],
                 "division": {"svg": "tab_division.svg", "polygon": poly(b.tabs["blue"]["poly"]),
                              "text_centre": [r2(v) for v in b.tabs["blue"]["text"]],
                              "text_inset": _tab_inset(b, "blue"),
                              "anchor": r2(SW - sum(_box(b.tabs["blue"]["poly"])[i] for i in (0, 2))),
                              "example": "DIVISION 1"},
                 "game_count": {"svg": "tab_game.svg", "polygon": poly(b.tabs["red"]["poly"]),
                                "text_centre": [r2(v) for v in b.tabs["red"]["text"]],
                                "text_inset": _tab_inset(b, "red"),
                                "anchor": r2(_box(b.tabs["red"]["poly"])[0]),
                                "example": "GAME 3 OF 5"},
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
            # each hexagon's own box, for the record and the guide
            "pips": {t: [[r2(x - b.pip["w"] / 2), r2(y - b.pip["h"] / 2),
                          r2(b.pip["w"]), r2(b.pip["h"])] for x, y in b.pips[t]]
                     for t in ("blue", "red")},
            # ...and the box the row of them is laid out in, which is what a graphic places.
            # It holds every pip a best of 7 would draw; a shorter series fills from the end
            # nearest the name, so the unused room falls away from it.
            "pip_row": _pip_row(b),
            "bans": {t: [[r2(v) for v in _box(tile)] for tile in b.bans[t]] for t in ("blue", "red")},
            "tabs": {"division": [r2(v) for v in _box(b.tabs["blue"]["poly"])],
                     "game": [r2(v) for v in _box(b.tabs["red"]["poly"])]},
            "event": [r2(v) for v in _box(b.bp["hexagon"])],
        },
        "clip": {
            "bans": {t: _tile_clip(b, t) for t in ("blue", "red")},
            "logo": {t: _logo_clip(b, t) for t in ("blue", "red")},
            "event": "polygon(" + ",".join(f"{x - _box(b.bp['hexagon'])[0]:.2f}px "
                                           f"{y - _box(b.bp['hexagon'])[1]:.2f}px"
                                           for x, y in b.bp["hexagon"]) + ")",
        },
    }


# ------------------------------------------------------------------ the folder

def standby_spec(b):
    """The standby screen's numbers: the "coming up next" band across the bottom, and the
    countdown bug hanging from the top. Every place is [standby] in layout.toml; what is worked
    out here is what the lean does to each piece - a point at half height on the containers and
    the message board, a taper on the arms and the bug."""
    sb = b.sb
    r2 = lambda v: round(float(v), 2)
    inner = sb["team_inset"] + sb["team_w"]               # a container's inner end
    return {
        "about": "FCJH standby screen. Generated by tools/obs.py from layout.toml's "
                 "[standby]; the screen itself is studio/src/sources/Standby.jsx.",
        "screen": [SW, SH],
        "band": {
            "height": sb["band"],
            "team": {
                "w": sb["team_w"], "h": sb["team_h"], "inset": sb["team_inset"],
                "bottom": sb["team_bottom"],
                # how far in from each end a point starts, and what is left in the middle
                "point": r2(b.lean * sb["team_h"] / 2),
                "gap": SW - 2 * inner,
                "frame": "frame_matchup.svg",
                "nine_slice": {"width": 2 * sb["team_cap"] + MID, "caps": sb["team_cap"],
                               "stretch": MID},
            },
            "plate": {"w": sb["plate_w"], "h": sb["plate_h"], "bottom": sb["plate_bottom"],
                      "point": r2(b.lean * sb["plate_h"] / 2), "text": sb["plate_text"],
                      # the strip of board the containers DON'T cover, which is the row the
                      # message is centred in: the board's top edge down to theirs
                      "row": (sb["plate_bottom"] + sb["plate_h"]
                              - sb["team_bottom"] - sb["team_h"])},
            "arm": {"w": sb["arm_w"], "h": sb["arm_h"], "bottom": sb["arm_bottom"],
                    "over": sb["arm_over"], "pad": sb["arm_pad"],
                    "taper": r2(b.lean * sb["arm_h"])},
        },
        "bug": {"w": sb["bug_w"], "h": sb["bug_h"], "taper": r2(b.lean * sb["bug_h"])},
        "colours": {"rim": b.rim, "stock": b.stock, "base_top": BASE[0], "base_bottom": BASE[1],
                    "text": CYAN[0], "blue": b.team["blue"], "red": b.team["red"],
                    "smoke": sb["smoke"], "bug_smoke": sb["bug_smoke"]},
    }


def webcam_spec(b):
    """The webcam frames' numbers. The pair hangs in the standby screen's free middle - under
    its countdown bug, over its band - so the two browser sources stack in OBS without either
    one having to move, and the free space is worked out from the band rather than typed."""
    cam = b.cam
    r2 = lambda v: round(float(v), 2)
    at = cam_places(b)
    free_top, free_bottom = at["free"]
    return {
        "about": "FCJH webcam frames: borders only, for OBS to put cameras under. Generated "
                 "by tools/obs.py from layout.toml's [webcam]; the source itself is "
                 "studio/src/sources/Webcams.jsx.",
        "screen": [SW, SH],
        "cam": {
            "w": cam["w"], "h": cam["h"], "top": r2(at["top"]),
            "left": r2(at["left"]), "right": r2(at["right"]),
            # the cut corner, and the mask OBS needs because of it
            # the cut corner as a FRACTION of the box, which is the same for every window
            # because they are all 16:9 and the chamfer is itself a fraction. CSS cuts any of
            # them with one pair of percentages.
            "chamfer_pct": [r2(100 * b.lean * cam["chamfer"] * 9 / 16),
                            r2(100 * cam["chamfer"])],
            "rim": cam["rim"],
            "frame": {"left": "cam_frame_left.svg", "right": "cam_frame_right.svg"},
            # served from the site root, and drawn at the solo window's size for the operator
            # to scale onto whichever they are filling
            "mask": {"left": "/masks/cam_mask_left.png", "right": "/masks/cam_mask_right.png",
                     "drawn_at": [cam["solo_w"], cam["solo_h"]]},
        },
        # the one-camera layout: the same construction, centred, with the screen to itself
        "solo": {
            "w": cam["solo_w"], "h": cam["solo_h"],
            "top": r2(at["solo_top"]), "left": r2(at["solo_left"]),
            # the pair's, scaled: an SVG stretches without loss and the shapes are similar
            "frame": "cam_frame_left.svg", "mask": "/masks/cam_mask_left.png",
        },
        "plate": {"h": cam["plate_h"], "gap": cam["plate_gap"], "pad": cam["plate_pad"],
                  "point": r2(b.lean * cam["plate_h"] / 2),
                  "name": cam["name"], "social": cam["social"]},
        "free": {"top": free_top, "bottom": free_bottom},
        "colours": {"rim": b.rim, "text": CYAN[0], "smoke": b.sb["smoke"],
                    "plate_smoke": cam["plate_smoke"]},
    }


GENERATED = ("<!-- Generated by tools/obs.py from layout.toml. Do not edit by hand:\n"
             "     change layout.toml (or tools/obs.py) and rebuild. -->\n")


def files(cfg):
    """Everything under studio/src/generated/, by path relative to it."""
    b = Band(cfg)
    enc = lambda s: s.encode("utf-8")
    out = {
        Path("pip_empty.svg"): enc(pip_svg(b, DARK, .6, False)),
        Path("tab_division.svg"): enc(tab_svg(b, "blue")),
        Path("tab_game.svg"): enc(tab_svg(b, "red")),
        Path("event_mask.png"): event_mask_png(b),
        Path("guide.png"): guide_png(b),
        Path("topbar.json"): enc(json.dumps(spec(b), indent=2, ensure_ascii=False) + "\n"),
        # the standby screen's band: one frame for both containers (see matchup_frame_svg).
        # Its message board and logo arms are plain smoke and want no art at all
        Path("frame_matchup.svg"): enc(matchup_frame_svg(b)),
        Path("standby.json"): enc(json.dumps(standby_spec(b), indent=2, ensure_ascii=False) + "\n"),
        # the webcam frames: a border and an OBS mask per side, and the places for both
        Path("webcam.json"): enc(json.dumps(webcam_spec(b), indent=2, ensure_ascii=False) + "\n"),
    }
    for side in ("left", "right"):
        out[Path(f"cam_frame_{side}.svg")] = enc(cam_frame_svg(b, side))
    mask_at = (b.cam["solo_w"], b.cam["solo_h"])      # the largest window; scale it down
    for side in ("left", "right"):
        out[PUBLIC / f"cam_mask_{side}.png"] = cam_mask_png(b, side, size=mask_at)
    for team in ("blue", "red"):
        out[Path(f"frame_{team}.svg")] = enc(frame_svg(b, team))
        out[Path(f"frame_logo_{team}.svg")] = enc(frame_svg(b, team, line=False))
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
