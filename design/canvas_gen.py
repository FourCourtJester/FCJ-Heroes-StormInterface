"""FCJH wireframe canvas, drawn from the build's own numbers.

Every position and size comes from tools/gen.py (layout.toml through load_config, HeroCell,
rects, team_bar_rects, heroic_*_rect, stat_geometry, place_columns, top_backplate_geometry)
and tools/inspect_card.py, so re-running this after a layout change keeps the boards in
step with the game. Nothing here is copied by hand except the talents pane (hand-written
layout, FCJH_InfoPane) and a few stand-in values (hero names, numbers) marked as such.

    python design/canvas_gen.py      -> design/canvas/project/*.dc.html + canvas.json

Then publish them to the canvas, https://claude.ai/artifact/6MmAcxcKjfAAprCN3oc3ZK
(root design/canvas). Stock.dc.html is not written: it annotates the stock UI.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import gen                   # noqa: E402
import inspect_card as ic    # noqa: E402
import maps                  # noqa: E402

OUT = Path(__file__).resolve().parent / "canvas" / "project"
CFG = gen.load_config()
PX = 1 / gen.Units(CFG).scale                  # px per layout unit at 1080p (0.9)
CELL = gen.HeroCell(CFG)
RECTS = gen.rects(CFG)
R = {k: r for k, (r, _) in RECTS.items()}
ROW = CFG["hero_row"]
S = lambda v: round(v * ROW["scale"])          # Blizzard's native cell units -> this build's
NARROW = S(gen.NARROW)                         # the bars narrow this much while the heroic shows
LEAN = CELL.overlap / CELL.h                   # the plates' slant, across per down
FG = {t: gen.fountain_rect(CFG, t) for t in ("blue", "red")}   # the plate fountain: (box, scale)
STAMP = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%h %cs", "--", "tools", "layout.toml", "src"],   # the last commit that changed the build
                       capture_output=True, text=True).stdout.strip()

# Uploaded to the canvas (Artifact asset store)
BG = "/_blob/e917171bdc2ff8862417f58430599c04"          # a game view, as the background
BACKPLATE = "/_blob/fa981478bd1fb50611111ce2f78ebb6f"   # gen.top_backplate_texture, as built
REF_CORE = "/_blob/f1f23a5699beb642c78ad903deaef0f2"    # design/ref_default_core_hp.png, 850 x 55
REF_TOP_ULTS = "/_blob/67e7950f93c40b2f67d69233cde55090"     # design/ref_ingame_topbar_ults.png, 1130 x 60
REF_TOP_NOULTS = "/_blob/880d87ab44c6b4c0b0ded9e7fb5dfeb3"   # design/ref_ingame_topbar_noults.png
REF_OBS_LEVELS = "ref_obs_levels.png"                   # already on the canvas, 440 x 160

hexc = lambda h: "#" + h.lower()
BP = CFG["top_backplate"]
HP = {"blue": hexc(BP["blue_colour"]), "red": hexc(BP["red_colour"])}   # Blizzard's health fill, sampled
XP_FILL = hexc(CFG["team_xp"]["colour"])
TRACK = "rgba(11,12,20,%.2f)" % (CFG["team_xp"]["track_alpha"] / 255)
CORE = {"blue": hexc(CFG["team_core"]["blue_colour"]), "red": hexc(CFG["team_core"]["red_colour"])}
HEAL = hexc(CFG["heal_popup"]["colour"])
COL = {"blue": {"line": "#6FA2FF", "portrait": "#1d3a6e", "txt": "#E4EDFF", "pop": "#4C8DFF"},
       "red": {"line": "#FF7A7F", "portrait": "#6e1d2c", "txt": "#FFE1E2", "pop": "#FF7A7F"}}
ENERGY = {"mana": "#5B8CFF", "fury": "#FF8A2A", "brew": "#F2C94C"}
GOLD = "#E8B84A"


def font_styles():
    """Our font styles (FontStyles.StormStyle): {name: (px, colour)}. Heights are layout units."""
    text = (REPO / "src" / "FCJH.StormInterface" / "Base.StormData" / "UI" / "FontStyles.StormStyle").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'<Style name="(\w+)"([^>]*)/>', text):
        h = re.search(r'height="(\d+)"', m.group(2))
        c = re.search(r'textcolor="(\w+)"', m.group(2))
        out[m.group(1)] = (round(int(h.group(1)) * PX, 1) if h else None, "#" + c.group(1) if c else None)
    return out


FONTS = font_styles()
f1 = lambda v: f"{v:g}" if isinstance(v, (int, float)) and v == int(v) else f"{round(v, 1):g}"
pts = lambda p: " ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in p)


# ---------------------------------------------------------------- page skeleton
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&amp;family=Barlow:wght@400;500;600&amp;family=Exo+2:wght@500;600;700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#0b0c14}}
.t{{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:16px;letter-spacing:.05em;text-transform:uppercase;line-height:1.15}}
.s{{font-family:'Barlow',sans-serif;font-weight:500;font-size:13px;line-height:1.3}}
.chip{{position:absolute;box-sizing:border-box;background:rgba(20,20,19,.9);color:#FAF9F5;padding:6px 10px;border-radius:4px}}
td,th{{text-align:left;vertical-align:top;padding:8px 12px;border-bottom:1px solid #2A2C3A;font-size:15px;line-height:1.35}}
th{{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:#A7A9B8}}
.k{{display:inline-block;border-radius:3px;padding:2px 8px;font-family:'Barlow',sans-serif;font-size:13px;font-weight:600;color:#fff;white-space:nowrap}}
.game{{background:#2E7D5B}}.built{{background:#2F63A8}}.unk{{background:#A84A26}}.obs{{background:transparent;border:2px dashed #F2A65A;color:#F7C08A}}.none{{background:#3A3C4A}}
.bz{{background:#6E4E9C}}.ours{{background:#2E7D5B}}.mix{{background:#2F63A8}}
{css}
</style>
</helmet>
'''
FOOT = '''</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
GAME = "font-family: 'Exo 2', sans-serif;"   # stands in for Blizzard's fonts on the canvas
TAGS = {"game": "In game", "built": "Built, not seen", "unk": "Unknown", "obs": "OBS", "none": "Dropped"}


def page(title, w, h, body, css=""):
    return (HEAD.format(title=title, css=css) +
            f'<div style="position: relative; width: {w}px; height: {h}px; overflow: hidden; background: #12131c; color: #ECECF1; font-family: \'Barlow\', sans-serif;">\n'
            + body + '</div>\n' + FOOT.format(w=w, h=h))


def header(title, sub, width=1600):
    return (f'<div style="position: absolute; left: 48px; top: 40px; width: {width}px; display: flex; flex-direction: column; gap: 6px;">'
            f'<h1 style="margin: 0; font-family: \'Barlow Condensed\', sans-serif; font-weight: 700; font-size: 40px; letter-spacing: .03em; text-transform: uppercase;">{title}</h1>'
            f'<p style="margin: 0; font-size: 16px; color: #A7A9B8;">{sub}</p></div>\n')


def heading(x, y, text, sub="", w=900):
    s = f'<div class="s" style="font-size: 15px; color: #C9CAD6; margin-top: 4px;">{sub}</div>' if sub else ""
    return (f'<div style="position: absolute; left: {f1(x)}px; top: {f1(y)}px; width: {w}px;">'
            f'<div class="t" style="font-size: 22px; color: #F2C94C;">{text}</div>{s}</div>\n')


def note(x, y, w, title, text, colour="#F2C94C"):
    return (f'<div style="position: absolute; left: {f1(x)}px; top: {f1(y)}px; width: {w}px; display: flex; flex-direction: column; gap: 2px;">'
            f'<div class="t" style="font-size: 18px; color: {colour};">{title}</div>'
            f'<div class="s" style="font-size: 15px; color: #C9CAD6;">{text}</div></div>\n')


def tag(kind):
    return f'<span class="k {kind}">{TAGS[kind]}</span>'


# ---------------------------------------------------------------- one hero plate
def plate_poly(team, x0, y0, w, h, ov):
    if team == "blue":   # leans \: the bottom edge sits one overlap right of the top
        return [(x0, y0), (x0 + w - ov, y0), (x0 + w, y0 + h), (x0 + ov, y0 + h)]
    return [(x0 + ov, y0), (x0 + w, y0), (x0 + w - ov, y0 + h), (x0, y0 + h)]


def slanted(team, l, t, r, b):
    """A box leaning with the plate (blue \\, red /), as the plate's own art leans."""
    cut = LEAN * (b - t)
    if team == "blue":
        return [(l, t), (r - cut, t), (r, b), (l + cut, b)]
    return [(l + cut, t), (r, t), (r - cut, b), (l, b)]


def text(x, y, s, size, fill="#ffffff", anchor="middle", weight=700, stroke=True, extra=""):
    st = f' stroke="#000000" stroke-width="{round(size / 9, 2)}" paint-order="stroke"' if stroke else ""
    return (f'<text x="{round(x, 1)}" y="{round(y, 1)}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-family="Exo 2, sans-serif" font-weight="{weight}" font-size="{round(size, 1)}" fill="{fill}"{st}{extra}>{s}</text>')


def plate(team, x0, y0, z, st, uid):
    """One plate at (x0, y0), z times its size on screen. Every part is placed from
    HeroCell / heroic_*_rect in cell units. st: the state to draw."""
    c, g = COL[team], CELL.team[team]
    k = PX * z                                            # px per cell unit, zoomed
    w, h, ov = CELL.w * k, CELL.h * k, CELL.overlap * k
    box = lambda r: (x0 + r[0] * k, y0 + r[1] * k, x0 + r[2] * k, y0 + r[3] * k)
    rect = lambda r, fill, frac=1.0, right=False, extra="": (
        f'<rect x="{round(box(r)[0] + (1 - frac) * (box(r)[2] - box(r)[0]) * right, 1)}" y="{round(box(r)[1], 1)}" '
        f'width="{round((box(r)[2] - box(r)[0]) * frac, 1)}" height="{round(box(r)[3] - box(r)[1], 1)}" fill="{fill}"{extra}></rect>')
    def leaned(mid0, mid1, t, bot, fill):
        """A bar at the plates' lean, mid0..mid1 across its MIDDLE row (cell units): blue's
        bottom edge sits half the slant's run further in, red's the other way."""
        half = (1 if team == "blue" else -1) * gen.HeroCell.LEAN * (bot - t) / 2
        p = [(mid0 - half, t), (mid1 - half, t), (mid1 + half, bot), (mid0 + half, bot)]
        return f'<polygon points="{pts([(x0 + a * k, y0 + b * k) for a, b in p])}" fill="{fill}"></polygon>'

    heroic = st.get("heroic")
    dead = st.get("dead")
    narrow = rnarrow = 0                    # (the bars below are already narrowed)
    out = [f'<clipPath id="c{uid}"><polygon points="{pts(plate_poly(team, x0, y0, w, h, ov))}"></polygon></clipPath>',
           f'<g clip-path="url(#c{uid})">',
           f'<rect x="{round(x0, 1)}" y="{round(y0, 1)}" width="{round(w, 1)}" height="{round(h, 1)}" fill="{"#2a2a33" if dead else c["portrait"]}"></rect>',
           text(x0 + w / 2 + (-1 if team == "blue" else 1) * 10 * k, y0 + 24 * k, st.get("label", "HERO"), 15 * k,
                c["txt"], weight=600, stroke=False, extra=f' opacity="{0.35 if dead else 0.7}"')]
    hl, ht, hr, hb = g["health"]
    el, et, er, eb = g["energy"]
    if heroic:   # the bars narrow from the heroic's side: blue's right, red's left
        if team == "blue":
            hr, er = hr - NARROW, er - NARROW
        else:
            hl, el = hl + NARROW, el + NARROW
    out.append(rect(g["health_backing"], "#0b0c14"))
    out.append(rect(g["mana_backing"], "#0b0c14"))
    if st.get("vikings"):
        # three bars at the plates' lean, meeting along one slanted line (gen.viking_bars):
        # each one's middle row runs step wide, the mask taking half the slant's run off
        # either end of its frame
        vl, vr = gen.viking_span(CELL, team)
        bars, _ = gen.viking_bars(vl, vr, hb - ht)
        run = gen.HeroCell.LEAN * (hb - ht)
        for (bl, br), frac in zip(bars, st["vikings"]):
            mid0, mid1 = bl + run / 2, br - run / 2
            out.append(leaned(mid0, mid0 + (mid1 - mid0) * frac, ht, hb, HP[team]))
    elif st.get("rexxar"):   # Blizzard's HeightOverride: Rexxar's bar runs full height (Misha's bar gone)
        out.append(rect((hl + narrow, ht, hr, eb), HP[team], st.get("hp", 1.0)))
    else:
        out.append(rect((hl + narrow, ht, hr, hb), HP[team], 0 if dead else st.get("hp", 1.0)))
    if not st.get("rexxar"):
        out.append(rect((el + rnarrow, et, er, eb), ENERGY[st.get("energy", "mana")], 0 if dead else st.get("mp", 1.0)))
    mid_x = x0 + w / 2 + CELL.death_shift * k             # the death timer's and CC icon's centre
    if st.get("cc") or st.get("clone"):
        half = CELL.cc_half * k
        cy = y0 + CELL.cc_mid * k
        fill, line = ("rgba(120,70,200,.9)", "#D9C2FF") if st.get("clone") else ("rgba(170,90,230,.9)", "#E7C8FF")
        out.append(f'<rect x="{round(mid_x - half, 1)}" y="{round(cy - half, 1)}" width="{round(2 * half, 1)}" height="{round(2 * half, 1)}" '
                   f'rx="{round(2.5 * k, 1)}" fill="{fill}" stroke="{line}" stroke-width="{round(1.2 * k, 1)}"></rect>')
        size = FONTS["FCJH_CCText"][0] * z
        out.append(text(x0 + (hl + narrow + hr) / 2 * k, y0 + (ht + hb) / 2 * k, "CLONE" if st.get("clone") else st["cc"], size,
                        extra=f' letter-spacing="{round(0.4 * z, 1)}" textLength="{round(min((hr - hl - narrow) * k, size * 0.66 * len(st.get("cc", "CLONE"))), 1)}" lengthAdjust="spacingAndGlyphs"'))
    if heroic and not dead:
        out.append(heroic_panel(team, box, k, z, heroic))
    if not dead:   # the fountain: st["fountain"] "cd<seconds>" for on cooldown
        out.append(fountain_slot(team, box(FG[team][0]), k, z, st.get("fountain", "ready")))
    if dead:
        out.append(text(mid_x, y0 + CELL.death_mid * k, dead, 28 * k, "#FF3A4E"))
    out.append('</g>')
    poly = pts(plate_poly(team, x0, y0, w, h, ov))
    out.append(f'<polygon points="{poly}" fill="none" stroke="#050608" stroke-width="{round(2.4 * z, 1)}"></polygon>')
    out.append(f'<polygon points="{poly}" fill="none" stroke="{c["line"]}" stroke-opacity=".55" stroke-width="{round(1 * z, 1)}"></polygon>')
    return "".join(out)


def fountain_slot(team, r, k, z, state):
    """The plate fountain (gen.fountain_rect): Blizzard's buff slot, leaning with the plate,
    on its dark purple backdrop. state: "ready", or "cd<seconds>" (the art dimmed, the frame
    still lit, the count on top)."""
    f = FG[team][1] * k                       # px per slot unit
    ax, ay, aw, ah = gen.SLOT_ART
    l, t = r[0] + ax * f, r[1] + ay * f      # the slot art's visible part
    rr, b = l + aw * f, t + ah * f
    cut = gen.SLOT_LEAN * (b - t)
    shape = pts([(l, t), (rr - cut, t), (rr, b), (l + cut, b)] if team == "blue" else
                [(l + cut, t), (rr, t), (rr - cut, b), (l, b)])
    dim = state.startswith("cd")
    cx, cy = (l + rr) / 2, (t + b) / 2
    a, s = 2.6 * k, 13 * k
    out = [f'<polygon points="{shape}" fill="rgb({gen.FOUNTAIN_BACKDROP})"></polygon>',
           f'<g opacity="{0.35 if dim else 1}">'
           f'<polygon points="{shape}" fill="#2F7BFF"></polygon>'
           f'<rect x="{round(cx - a / 2, 1)}" y="{round(cy - s / 2, 1)}" width="{round(a, 1)}" height="{round(s, 1)}" fill="#ffffff"></rect>'
           f'<rect x="{round(cx - s / 2, 1)}" y="{round(cy - a / 2, 1)}" width="{round(s, 1)}" height="{round(a, 1)}" fill="#ffffff"></rect></g>',
           f'<polygon points="{shape}" fill="none" stroke="#C9D6EE" stroke-width="{round(1.2 * z, 1)}"></polygon>']
    if not dim:
        out.append(f'<polygon points="{shape}" fill="none" stroke="#9FE0FF" stroke-opacity=".5" stroke-width="{round(3.5 * z, 1)}"></polygon>')
    else:
        out.append(text(cx, cy, state[2:], 14 * k))      # FCJH_FountainCooldown
    return "".join(out)


def heroic_panel(team, box, k, z, state):
    """Blizzard's in-game heroic panel as we mirror it: the icon square (57 units) on the
    cell's bottom edge, the gold frame (68 x 38) centred on it. The art is Blizzard's; here
    the icon's visible part is drawn as the frame's slanted shape."""
    il, it, ir, ib = box(gen.heroic_icon_rect(CFG, team))
    fl, ft, fr, fb = box(gen.heroic_frame_rect(CFG, team))
    shape = pts(slanted(team, fl, ft, fr, fb))
    dim = state.startswith("cd")
    icon = {"ready": "#7B3FD0", "charge": "#7B3FD0", "unpicked": "#3a2a55"}.get(state, "#55505f")
    out = [f'<rect x="{round(il, 1)}" y="{round(it, 1)}" width="{round(ir - il, 1)}" height="{round(ib - it, 1)}" fill="rgba(10,8,16,.55)"></rect>',
           f'<polygon points="{shape}" fill="{icon}" opacity="{0.45 if dim else 1}"></polygon>']
    cx, cy = (fl + fr) / 2, (ft + fb) / 2
    if state == "unpicked":
        out.append(text(cx, cy, "?", 20 * k, "#E7C8FF"))
    if state == "charge":   # Tracer: Blizzard's own charge meter (ChargeFillProgress), lifted onto the frame
        fill = pts(slanted(team, fl, fb - (fb - ft) * 0.55, fr, fb))
        out.append(f'<polygon points="{fill}" fill="#FFB347" opacity=".75"></polygon>')
    out.append(f'<polygon points="{shape}" fill="none" stroke="{GOLD}" stroke-width="{round(1.6 * z, 1)}"></polygon>')
    if state == "ready":
        out.append(f'<polygon points="{shape}" fill="none" stroke="#FFF1A8" stroke-opacity=".55" stroke-width="{round(4 * z, 1)}"></polygon>')
    if dim:
        out.append(text(cx, cy, state[2:], 17 * k))
    return "".join(out)


def popup(cx, edge_y, z, kind, drop=0.0, alpha=1.0, team="blue", ghost=False):
    """A pop-up: talent_popup_size square centred on the cell box's middle, straddling its
    top edge when settled (drop: px still to rise, at 1x)."""
    size = ROW["talent_popup_size"] * z
    x, y = cx - size / 2, edge_y - size / 2 + drop * z
    dash = f' stroke-dasharray="{round(4 * z, 1)} {round(3 * z, 1)}"' if ghost else ""
    if kind == "talent":
        edge = 3 * z
        return (f'<g opacity="{alpha}"><rect x="{round(x, 1)}" y="{round(y, 1)}" width="{round(size, 1)}" height="{round(size, 1)}" '
                f'fill="#12202e" stroke="{COL[team]["pop"]}" stroke-width="{round(edge, 1)}"{dash}></rect>'
                + text(cx, y + size / 2, "TALENT", 9 * z, "#A8EBEB", stroke=False) + '</g>')
    edge = size * 4 / 64                    # gen.square_border: 4 of 64 px
    a, t = size * 0.18, size * 0.62
    return (f'<g opacity="{alpha}"><rect x="{round(x + edge / 2, 1)}" y="{round(y + edge / 2, 1)}" width="{round(size - edge, 1)}" height="{round(size - edge, 1)}" '
            f'fill="rgba(10,30,16,.55)" stroke="{HEAL}" stroke-width="{round(edge, 1)}"{dash}></rect>'
            f'<rect x="{round(cx - a / 2, 1)}" y="{round(y + (size - t) / 2, 1)}" width="{round(a, 1)}" height="{round(t, 1)}" rx="{round(z, 1)}" fill="{HEAL}"></rect>'
            f'<rect x="{round(cx - t / 2, 1)}" y="{round(y + (size - a) / 2, 1)}" width="{round(t, 1)}" height="{round(a, 1)}" rx="{round(z, 1)}" fill="{HEAL}"></rect></g>')


def slab(team, r, frac, fill, from_inner):
    """A bar cut to the plates' slant (team_bar_rects): its track, and its fill at frac,
    growing from the row's inner end (toward the minimap) when from_inner."""
    x, y, w, h = r
    cut = LEAN * h
    def poly(x0, w0):
        if team == "blue":
            return pts([(x0, y), (x0 + w0 - cut, y), (x0 + w0, y + h), (x0 + cut, y + h)])
        return pts([(x0 + cut, y), (x0 + w0, y), (x0 + w0 - cut, y + h), (x0, y + h)])
    fw = w * frac
    inner_right = team == "blue"
    fx = x + w - fw if (from_inner == inner_right) else x
    return (f'<polygon points="{poly(x, w)}" fill="{TRACK}"></polygon>'
            f'<polygon points="{poly(fx, fw)}" fill="{fill}"></polygon>')


BLUE_STATES = [   # stand-ins: blue at level 12 (heroics out), red at 9 (none yet)
    {"label": "1", "dead": "14", "heroic": "ready"},
    {"label": "2", "hp": 0.83, "mp": 0.4, "heroic": "ready"},
    {"label": "3", "hp": 0.18, "mp": 0.9, "heroic": "cd37"},
    {"label": "4", "hp": 0.69, "mp": 0.3, "energy": "fury", "heroic": "charge"},
    {"label": "5", "hp": 0.52, "mp": 0.6, "cc": "STUNNED", "heroic": "ready"},
]
RED_STATES = [
    {"label": "6", "hp": 0.91, "mp": 0.5},
    {"label": "7", "hp": 0.27, "mp": 0.2},
    {"label": "8", "vikings": (1.0, 0.45, 0.8), "mp": 0.7},
    {"label": "9", "hp": 0.43, "mp": 0.8, "cc": "ROOTED"},
    {"label": "0", "hp": 1.0, "rexxar": True},
]


def cell_x(team, i):
    left = ROW["blue_left"] if team == "blue" else ROW["red_left"]
    return round(left + i * CELL.pitch * PX, 1)


def hero_rows_svg():
    top = ROW["top"]
    parts = [slab("blue", R["blue_xp"], 1.0, XP_FILL, True), slab("red", R["red_xp"], 0.62, XP_FILL, True),
             slab("blue", R["blue_core"], 0.78, CORE["blue"], True), slab("red", R["red_core"], 0.64, CORE["red"], True)]   # drains from the outer end
    for team, pct in (("blue", "78%"), ("red", "64%")):
        x, y, w, h = R[f"{team}_core"]
        inner = x + w - 16 if team == "blue" else x + 16
        parts.append(text(inner, y + h / 2, pct, 16, "#EAF6FF", "end" if team == "blue" else "start"))
    for i, st in enumerate(BLUE_STATES):
        parts.append(plate("blue", cell_x("blue", i), top, 1, st, f"b{i}"))
    for i, st in enumerate(RED_STATES):
        parts.append(plate("red", cell_x("red", i), top, 1, st, f"r{i}"))
    w = CELL.w * PX
    parts.append(popup(cell_x("blue", 1) + w / 2, top, 1, "talent"))
    parts.append(popup(cell_x("blue", 2) + w / 2, top, 1, "heal"))
    parts.append(popup(cell_x("red", 1) + w / 2, top, 1, "talent", team="red"))
    return ('<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position: absolute; left: 0; top: 0;" '
            'aria-label="Both hero rows as slanted interlocking plates, with team XP and core bars above them">' + "".join(parts) + '</svg>')


# ---------------------------------------------------------------- info panes (pane-local px)
PANE_X, PANE_Y, PANE_W, PANE_H = R["info_pane"]
PANE_CSS = (f"position: relative; width: {PANE_W}px; height: {PANE_H}px; box-sizing: border-box; background: rgba(11,12,20,.9); "
            f"border: {CFG['info_pane']['border']}px solid rgba(106,122,170,.6); overflow: hidden;")
u = lambda v: round(v * PX, 1)                 # layout units -> px


def abs_box(x, y, w, h, extra=""):
    return f'position: absolute; left: {f1(x)}px; top: {f1(y)}px; width: {f1(w)}px; height: {f1(h)}px; box-sizing: border-box; {extra}'


def title_band(title, w=PANE_W):
    th = CFG["info_pane"]["title_height"]
    return (f'<div style="{abs_box(0, 0, w, th)} background: rgb(24,28,48); display: flex; align-items: center; justify-content: center; '
            f'{GAME} font-weight: 600; font-size: 14px; letter-spacing: .06em; color: #C9D3EA;">{title}</div>'
            f'<div style="{abs_box(w - th, 0, th, th)} display: flex; align-items: center; justify-content: center; {GAME} font-weight: 700; font-size: 14px; color: #C9D3EA;">X</div>')


def portrait(x, y, team, label, w=81, h=30):
    c = COL[team]
    return (f'<div style="{abs_box(x, y, w, h)} background: {c["portrait"]}; border: 1px solid {c["line"]}; display: flex; align-items: center; '
            f'justify-content: center; {GAME} font-size: 12px; color: {c["txt"]};">{label}</div>')


def talents_pane():
    # FCJH_InfoPane (hand-written): rows 60 units apart under the title band, portrait at 23,
    # tier icons from 133 with Blizzard's gaps
    out = [f'<div style="{PANE_CSS}">', title_band("TALENTS")]
    icons = [119.7, 170.1, 220.5, 276.3, 331.2, 381.6, 437.4]
    picks = [6, 6, 6, 5, 6, 5, 5, 5, 4, 5]
    for i in range(10):
        team = "blue" if i < 5 else "red"
        top = u(29 + 7 + 60 * i)
        out.append(portrait(u(23), round(top + u(12), 1), team, f"{(i + 1) % 10}"))
        for j, x in enumerate(icons):
            c = COL[team]
            style = (f'background: {c["portrait"]}; border: 1px solid {c["line"]};' if j < picks[i]
                     else 'border: 1px dashed rgba(255,255,255,.25);')
            out.append(f'<div style="{abs_box(x, round(top + u(7), 1), 36, 36)} border-radius: 3px; {style}"></div>')
    out.append('</div>')
    return "".join(out)


DEMO = {   # stand-in numbers
    "kda": (["1", "1", "0", "13,660"], ["0", "0", "2", "13,572"],
            [["0", "0", "0", "1,532"], ["0", "0", "0", "2,252"], ["0", "0", "0", "6,130"], ["0", "1", "0", "2,787"], ["0", "0", "0", "959"],
             ["0", "0", "0", "2,117"], ["0", "0", "0", "3,767"], ["1", "0", "0", "2,789"], ["0", "0", "1", "1,913"], ["0", "0", "1", "2,986"]]),
    "healing": (["6,402", "18,220", "4,915"], ["5,871", "16,004", "7,330"],
                [["1,210", "0", "480"], ["2,004", "0", "0"], ["640", "18,220", "4,435"], ["1,988", "0", "0"], ["560", "0", "0"],
                 ["1,002", "0", "2,210"], ["2,410", "16,004", "5,120"], ["980", "0", "0"], ["1,112", "0", "0"], ["367", "0", "0"]]),
    "structures": (["41,230", "12,480", "18,904"], ["38,771", "9,960", "17,322"],
                   [["6,120", "1,840", "3,410"], ["9,870", "3,210", "4,002"], ["4,410", "900", "3,115"], ["12,006", "4,480", "4,870"],
                    ["8,824", "2,050", "3,507"], ["7,302", "1,010", "3,221"], ["10,580", "3,900", "3,788"], ["5,114", "1,200", "3,366"],
                    ["9,640", "2,650", "3,519"], ["6,135", "1,200", "3,428"]]),
}


def stats_pane(key):
    """gen.stat_pane's layout: stat_geometry + place_columns, in px."""
    _, title, columns = next(p for p in gen.STAT_PANES if p[0] == key)
    g = gen.stat_geometry(CFG)
    placed = gen.place_columns(columns, g["columns"])
    tb, tr, rows = DEMO[key]
    head_px, head_col = FONTS["FCJH_StatHeading"]
    out = [f'<div style="{PANE_CSS}">', title_band(title.replace("  ", " "))]
    lbl = f"position: absolute; display: flex; align-items: center; justify-content: flex-end; {GAME}"
    for (_, _, name, x, w, _) in placed:
        out.append(f'<div style="{lbl} left: {u(x)}px; top: {u(g["title"])}px; width: {u(w)}px; height: {u(g["team_tops"][0] - g["title"])}px; '
                   f'font-size: {head_px}px; font-weight: 600; color: {head_col};">{name}</div>')
    for t, team in enumerate(("blue", "red")):
        band_c = gen.TEAMS[t][2].split(",")
        y = g["team_tops"][t]
        out.append(f'<div style="{abs_box(0, u(y), PANE_W, u(g["team_h"]))} background: rgba({",".join(band_c[1:])},{int(band_c[0]) / 255:.2f});"></div>')
        tp, tc = FONTS[f"FCJH_StatTeam_{team.capitalize()}"]
        out.append(f'<div style="{lbl} justify-content: flex-start; left: {u(gen.STAT_MARGIN)}px; top: {u(y)}px; height: {u(g["team_h"])}px; '
                   f'font-size: {tp}px; font-weight: 600; letter-spacing: .06em; color: {tc};">{team.upper()}</div>')
        vp, vc = FONTS[f"FCJH_StatTotal_{team.capitalize()}"]
        for (_, _, _, x, w, _), v in zip(placed, (tb, tr)[t]):
            out.append(f'<div style="{lbl} left: {u(x)}px; top: {u(y)}px; width: {u(w)}px; height: {u(g["team_h"])}px; '
                       f'font-size: {vp}px; font-weight: 700; color: {vc};">{v}</div>')
    for i, y in enumerate(g["row_tops"]):
        team = "blue" if i < 5 else "red"
        vp, vc = FONTS[f"FCJH_StatValue_{team.capitalize()}"]
        out.append(portrait(u(gen.STAT_MARGIN), u(y + 10), team, f"{(i + 1) % 10}"))
        for (_, _, _, x, w, _), v in zip(placed, rows[i]):
            out.append(f'<div style="{lbl} left: {u(x)}px; top: {u(y + 12)}px; width: {u(w)}px; height: {u(gen.STAT_ROW_H - 12)}px; '
                       f'font-size: {vp}px; font-weight: 600; color: {vc};">{v}</div>')
    out.append('</div>')
    return "".join(out)


# ---------------------------------------------------------------- inspect card (card-local px)
def inspect_card():
    """tools/inspect_card.py's layout (layout units -> px)."""
    W, M, T = ic.W, ic.M, ic.TITLE
    cw, ch = R["inspect"][2], R["inspect"][3]
    b = lambda top, left, bottom, right, extra="": f'<div style="{abs_box(u(left), u(top), u(right - left), u(bottom - top))} {extra}"></div>'
    txt = lambda top, left, bottom, right, s, style, extra="": (
        f'<div style="{abs_box(u(left), u(top), u(right - left), u(bottom - top))} display: flex; align-items: center; {GAME} '
        f'font-size: {FONTS[style][0]}px; color: {FONTS[style][1]}; {extra}">{s}</div>')
    p = [f'<div style="position: relative; width: {cw}px; height: {ch}px; background: rgba(11,12,20,.84); overflow: hidden;">']
    p.append(b(0, 0, T, W, "background: rgba(24,28,48,.92);"))
    p.append(txt(0, M, T, W - T - 4, "Auriel", "FCJH_InspectName", "font-weight: 700;"))   # the hero's name, in the title band
    p.append(b(ic.PORTRAIT[0], 2, ic.PORTRAIT[1], W - 2, f"background: {COL['blue']['portrait']};"))
    p.append(f'<div style="{abs_box(u(2), u(ic.PORTRAIT[0]), u(W - 4), u(ic.PORTRAIT[1] - ic.PORTRAIT[0]))} display: flex; align-items: center; justify-content: center; '
             f'{GAME} font-size: 13px; letter-spacing: .06em; color: rgba(228,237,255,.55);">PLATE PORTRAIT · SAME CROP</div>')
    band = ic.NAME_BAND + ic.NAME_H
    p.append(b(ic.NAME_BAND, 0, band, W, "background: rgba(16,18,32,.92);"))
    p.append(txt(ic.NAME_BAND, M, band, W - M - 70, "PLAYER NAME", "FCJH_InspectSub"))
    p.append(txt(ic.NAME_BAND, W - M - 60, band, W - M, "16", "FCJH_InspectLevel", "justify-content: flex-end; font-weight: 700;"))
    p.append(f'<div style="{abs_box(0, 0, cw, ch)} box-sizing: border-box; border: {u(ic.BORDER)}px solid #5cbcec;"></div>')   # the team edge (blue shown)
    p.append(b(ic.HP[0], M, ic.HP[1], W - M, "background: #0d1526;"))
    p.append(b(ic.HP[0], M, ic.HP[1], M + (W - 2 * M) * 0.78, "background: #3f7fd8;"))
    p.append(txt(ic.HP[0], M + 6, ic.HP[1], W - M - 6, "<span>1988 / 2549</span><span>+5.3/s</span>", "FCJH_InspectSub", "justify-content: space-between; color: #ffffff; font-weight: 600;"))
    p.append(b(ic.MANA[0], M, ic.MANA[1], W - M, "background: #1b1a2c;"))
    p.append(b(ic.MANA[0], M, ic.MANA[1], M + (W - 2 * M) * 0.55, f"background: {ENERGY['mana']};"))
    sect = lambda top, s: txt(top, M, top + 15, W - M, s, "FCJH_InspectSection", "font-weight: 600; letter-spacing: .08em;")
    # the fountain first, then buffs, then debuffs: Blizzard's 58 x 34 slots, each overlapping the last
    step = ic.BUFF_W - ic.BUFF_OVERLAP
    for i, look in enumerate(["background: rgba(60,80,230,.85); border: 1px solid #9EB6FF;"]
                             + ["background: #1f4d2e; border: 1px solid #5BD08A;"] * 3
                             + ["background: #4d1f26; border: 1px solid #E0668F;"] * 2):
        left = M + i * step
        p.append(b(ic.BUFFS, left, ic.BUFFS + ic.BUFF_H, left + ic.BUFF_W, look + " transform: skewX(-20deg); border-radius: 3px;"))
    slots = [(ic.COMMAND_KEYS[k], r, c) for r, row_ in enumerate(ic.COMMAND_ROWS) for c, k in enumerate(row_)]
    for key, row, col in slots:
        size = ic.CMD_SIZE - 2 * ic.CMD_INSET
        left, top = round(ic.cmd_centre(row, col) - size / 2), ic.ABIL_ROWS[row] + ic.CMD_INSET   # the button's icon
        filled = row == 1 or col < 2
        heroic = key == "R"
        colour = ("#3a2466", "#C9A8FF") if heroic else (("#22304f", "#6FA2FF") if filled else ("transparent", "rgba(255,255,255,.2)"))
        p.append(b(top, left, top + size, left + size, f"background: {colour[0]}; border: 1px solid {colour[1]}; border-radius: 3px;"))
        p.append(txt(top + size - 14, left + 2, top + size, left + 16, key, "FCJH_InspectTier", "font-weight: 700;"))   # in game: Blizzard's own hotkey label
        if key in ("E", "R"):
            p.append(txt(top, left, top + size, left + size, "12" if key == "E" else "37", "FCJH_HeroicCooldown",
                         "justify-content: center; font-weight: 700; background: rgba(8,8,12,.6);"))
    p.append(sect(ic.TAL_LABEL, "TALENTS"))
    for n, lv in enumerate((1, 4, 7, 10, 13, 16, 20)):
        left = ic.tal_left(n + 1)
        picked = n < 5
        p.append(b(ic.TAL, left, ic.TAL + ic.TAL_SIZE, left + ic.TAL_SIZE,
                   "background: #1d3a6e; border: 2px solid #4C8DFF;" if picked else "background: rgba(8,8,16,.9); border: 1px solid rgba(115,102,141,.8);"))
        p.append(txt(ic.TAL + ic.TAL_SIZE + 2, left, ic.TAL + ic.TAL_SIZE + 16, left + ic.TAL_SIZE, str(lv), "FCJH_InspectTier", "justify-content: center;"))
    p.append(sect(ic.STATS_LABEL, "STATS"))
    shown = {"AttackDamageFrame": ("Dmg", "87.4"), "AttackSpeedFrame": ("Spd", "1.25"), "AttackRangeFrame": ("Rng", "1.5"),
             "AbilityPowerFrame": ("Spell", "0%"), "MoveSpeedFrame": ("Move", "130%"),
             "PhysicalArmorFrame": ("Armor", "0"), "AbilityArmorFrame": ("Sp.armor", "0")}
    for frame, c, r in ic.STATS_GRID:
        n, v = shown[frame]
        top, left = ic.STATS + r * ic.STAT_ROW, M + c * ic.STAT_COL
        p.append(txt(top, left, top + ic.STAT_ROW, left + ic.STAT_COL - 4, f'<span style="color: #8fa3c8;">{n}</span><span style="color: #ffffff; font-weight: 600;">{v}</span>',
                     "FCJH_InspectTier", "justify-content: space-between; padding-right: 8px;"))
    spare = ic.STATS + (1 + max(r for _, _, r in ic.STATS_GRID)) * ic.STAT_ROW
    p.append(f'<div style="{abs_box(u(M), u(spare) + 8, u(W - 2 * M), ch - u(spare) - 20)} border: 1px dashed rgba(255,255,255,.18); display: flex; align-items: center; '
             f'justify-content: center; {GAME} font-size: 11px; color: #6f7b96;">spare · {round(ch - u(spare))} px</div>')
    p.append('</div>')
    return "".join(p)


# ================================================================= Main
MAIN_CSS = """.ui{position:absolute;box-sizing:border-box;background:rgba(250,249,245,.16);border:2px solid rgba(250,249,245,.85);border-radius:4px;color:#FAF9F5}
.ob{position:absolute;box-sizing:border-box;border:2px dashed #F2A65A;background:rgba(242,166,90,.12);border-radius:4px;color:#F7C08A}
.dem{position:absolute;box-sizing:border-box;border:2px dashed #6FD3D3;background:rgba(111,211,211,.12);border-radius:4px;color:#A8EBEB}
.faint{position:absolute;box-sizing:border-box;border:2px dashed rgba(250,249,245,.45);border-radius:4px;color:rgba(250,249,245,.8)}
.chip{font-size:13px}"""


def at(key, cls, inner="", extra=""):
    x, y, w, h = R[key]
    return f'<div class="{cls}" style="left: {f1(x)}px; top: {f1(y)}px; width: {f1(w)}px; height: {f1(h)}px; {extra}">{inner}</div>\n'


CENTRE = "display: flex; align-items: center; justify-content: center; text-align: center;"
key = lambda k: CFG["toggles"][k].replace("Control", "Ctrl")      # layout.toml [toggles], as written on screen
TOGGLES = (("replay", "replay box"), ("chat", "chat"), ("inspect", "inspect card"), ("names", "player names"))


def hexagon_svg():
    """Blizzard's hexagon (TopBarLogoOverlay), from the measured [top_backplate] hexagon."""
    h = [tuple(p) for p in BP["hexagon"]]
    cx = sum(x for x, _ in h) / 6
    cy = sum(y for _, y in h) / 6
    inner = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.86) for x, y in h]
    return (f'<polygon points="{pts(h)}" fill="#1a1740" stroke="#6b5fd6" stroke-width="4"></polygon>'
            f'<polygon points="{pts(inner)}" fill="none" stroke="#a79bff" stroke-opacity=".5" stroke-width="1.5"></polygon>'
            + event_logo_svg())


def event_logo_svg():
    """OBS's tournament logo in the hexagon's middle ([element.event_logo])."""
    x, y, w, h = R["event_logo"]
    cx, cy = x + w / 2, y + h / 2
    return (f'<ellipse cx="{f1(cx)}" cy="{f1(cy)}" rx="{f1(w / 2)}" ry="{f1(h / 2)}" fill="rgba(242,166,90,.12)" stroke="#F2A65A" stroke-width="2.5" stroke-dasharray="7 5"></ellipse>'
            f'<text x="{f1(cx)}" y="{f1(cy - 3)}" text-anchor="middle" fill="#F7C08A" font-family="Barlow Condensed, sans-serif" font-weight="600" font-size="12" letter-spacing="1">EVENT</text>'
            f'<text x="{f1(cx)}" y="{f1(cy + 11)}" text-anchor="middle" fill="#F7C08A" font-family="Barlow Condensed, sans-serif" font-weight="600" font-size="12" letter-spacing="1">LOGO</text>')


BANS = CFG["top_bar"]["bans"]   # bans a side ([top_bar]); the slots fill *_bans, drawn square


def ban_slots(team):
    x, y, w, h = R[f"{team}_bans"]
    gap = (w - BANS * h) / (BANS - 1)
    return "".join(f'<div class="ob t" style="left: {f1(x + i * (h + gap))}px; top: {f1(y)}px; width: {f1(h)}px; height: {f1(h)}px; {CENTRE} font-size: 10px;">Ban</div>\n'
                   for i in range(BANS))


def tabs_svg():
    """The division and game tabs as the interface draws them (gen.top_bar_tab_texture): the
    stock dark the backplate fades to, a chrome line down both sides and along the bottom, and
    none across the top, where the band's own rim closes them."""
    g = gen.top_bar_geometry(CFG)
    bp = CFG["top_backplate"]
    out = [f'<svg width="1920" height="140" viewBox="0 0 1920 140" style="position: absolute; left: 0; top: 0;" aria-label="The division and game tabs">']
    for team in ("blue", "red"):
        p0, p1, p2, p3 = g["tabs"][team]["poly"]
        pt = lambda q: f"{f1(q[0])},{f1(q[1])}"
        out.append(f'<polygon points="{" ".join(pt(q) for q in (p0, p1, p2, p3))}" fill="#{bp["stock"][1]}" fill-opacity=".9"/>')
        out.append(f'<polyline points="{" ".join(pt(q) for q in (p1, p2, p3, p0))}" fill="none" stroke="#{bp["rim"][0]}" '
                   f'stroke-width="{CFG["top_bar"]["tab_rim"]}" stroke-linejoin="round"/>')
    out.append('</svg>\n')
    return "".join(out)


def score_pips(team, wins):
    """The series score: hexagon pips, no plate, filled from the name outward (gen's
    top_bar_geometry; a best of 5 here, so three a side of the four [top_bar] keeps room for)."""
    g = gen.top_bar_geometry(CFG)
    r = g["pip"]["r"]
    out = []
    for i, (cx, cy) in enumerate(g["pips"][team][:3]):
        pts = " ".join(f"{cx + r * math.cos(math.radians(30 + 60 * k)):.1f},{cy + r * math.sin(math.radians(30 + 60 * k)):.1f}"
                       for k in range(6))
        fill = COL[team]["line"] if i < wins else "none"
        out.append(f'<svg width="1920" height="{f1(g["height"])}" viewBox="0 0 1920 {f1(g["height"])}" '
                   f'style="position: absolute; left: 0; top: 0;" aria-label="Series score pip">'
                   f'<polygon points="{pts}" fill="{fill}" fill-opacity="{1 if i < wins else 0}" stroke="#F7C08A" stroke-width="2"/></svg>\n')
    return "".join(out)


def top_bar(levels=("12", "9")):
    """The top bar as built: our backplate texture, Blizzard's hexagon, level numbers and clock;
    and OBS's data, stand-ins in orange. OBS draws data only, never art (user, 2026-10-16): team
    names, logos, series score, the tournament's name, division and logo, the game's bans. The
    plates under them are the interface's (white: the name plates; the rest come with the art
    pass)."""
    b = []
    for team, wins in (("blue", 1), ("red", 2)):
        b.append(score_pips(team, wins))
        b.append(at(f"{team}_name", "ob t", '<span style="font-size: 22px;">Team name</span>', CENTRE))
        b.append(at(f"{team}_logo", "ob t", '<span style="font-size: 12px;">Logo</span>', CENTRE))
        b.append(ban_slots(team))
    b.append(tabs_svg())
    for stem, words in (("division", "Division 1"), ("game_count", "Game 3 of 5")):
        x, y = gen.top_bar_geometry(CFG)["tabs"]["blue" if stem == "division" else "red"]["text"]
        b.append(f'<div class="t" style="position: absolute; left: {f1(x - 80)}px; top: {f1(y - 9)}px; width: 160px; '
                 f'{CENTRE} font-size: 12px; color: #F7C08A;">{words}</div>\n')
    x, y, w, h = R["top_backplate"]
    b.append(f'<img src="{BACKPLATE}" alt="Our top bar backplate texture, as built" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px;">\n')
    b.append(f'<svg width="1920" height="140" viewBox="0 0 1920 140" style="position: absolute; left: 0; top: 0;" aria-label="Blizzard\'s centre hexagon">{hexagon_svg()}</svg>\n')
    for key, lv in zip(("blue_level", "red_level"), levels):
        b.append(at(key, "t", lv, f"position: absolute; {CENTRE} font-size: 40px; font-weight: 700; color: #FAF9F5; {GAME} text-transform: none; "
                                  "text-shadow: 0 0 3px #000, 0 0 3px #000;"))
    b.append(at("clock", "t", "02:09", f"position: absolute; {CENTRE} font-size: 18px; color: #C9D3EA; {GAME}"))
    return "".join(b)


def kill_row(y, killer, victim):
    """Blizzard's kill row in its own place: killer from 27 units in, victim ending at 210."""
    ck, cv = COL[killer], COL[victim]
    left = R["kill_feed"][0] + u(27)
    right = R["kill_feed"][0] + u(gen.KILL_ROW_SINGLE)
    return (f'<div style="position: absolute; left: {f1(left)}px; top: {y}px; width: {f1(right - left)}px; height: 56px;">'
            f'<div style="position: absolute; left: 0; top: 0; width: 56px; height: 56px; border-radius: 50%; box-sizing: border-box; border: 3px solid {ck["line"]}; background: {ck["portrait"]};"></div>'
            f'<div style="position: absolute; left: 60px; top: 18px; width: 40px; height: 20px; text-align: center; {GAME} font-size: 14px; color: #FAF9F5;">&#8250;</div>'
            f'<div style="position: absolute; right: 0; top: 0; width: 56px; height: 56px; border-radius: 50%; box-sizing: border-box; border: 3px solid {cv["line"]}; background: {cv["portrait"]};"></div>'
            f'</div>')


def main_board():
    b = [f'<img src="{BG}" alt="Heroes of the Storm game view, used as a background" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; opacity: 0.55;">\n',
         '<div style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; background: rgba(8,10,20,0.35);"></div>\n']
    b.append(at("replay", "ui", f'<div class="t" style="font-size: 18px;">Replay controls · Blizzard\'s panel</div>'
                f'<div class="s">Replays only · {R["replay"][2]} × {R["replay"][3]} · {key("replay")} slides it out, leaving a tab in the corner</div>',
                "padding: 12px; display: flex; flex-direction: column; justify-content: space-between;"))
    b.append(top_bar())
    b.append(at("centre_banners", "faint t", "Blizzard's centre banners · the map banners went beside the minimap (Maps board)", CENTRE + " font-size: 14px;"))
    b.append("".join(kill_row(y, k, v) for y, k, v in ((122, "red", "blue"), (188, "blue", "red"), (254, "blue", "red"))))
    kx, _, kw, _ = R["kill_feed"]
    b.append(f'<div class="chip s" style="left: {kx + 210}px; top: 126px; width: 250px;">Kill feed · Blizzard\'s, in its own place; under an info pane while one shows</div>\n')
    b.append(f'<div style="position: absolute; left: {PANE_X}px; top: {PANE_Y}px;">' + stats_pane("kda") + '</div>\n')
    ix, iy, iw, ih = R["inspect"]
    b.append(f'<div class="dem" style="left: {ix}px; top: {iy}px; width: {iw}px; height: {ih}px; background: transparent;"></div>\n')
    b.append(f'<div class="chip s" style="left: {PANE_X + PANE_W + 12}px; top: {PANE_Y + 90}px; width: 270px;">Info pane · {PANE_W} × {PANE_H} · Ctrl+1 talents, 2 KDA, 3 healing, 4 structures (KDA shown)</div>\n')
    b.append(f'<div class="chip s" style="left: {ix + iw + 12}px; top: {iy + ih - 120}px; width: 300px; border: 1px solid #6FD3D3;">Teal: the inspect card, {iw} × {ih}, while a unit is selected (same left column; bottom at y {iy + ih})</div>\n')
    b.append(at("map_objectives", "dem", '<div class="t" style="font-size: 14px;">Map objectives · per map, at THE GAP (Maps board)</div>', CENTRE))
    mm = CFG["minimap"]
    sq = gen.MINIMAP_SQUARE * PX
    b.append(f'<div class="faint" style="left: {f1(mm["centre_x"] - sq / 2)}px; top: {f1(mm["bottom"] - sq)}px; width: {f1(sq)}px; height: {f1(sq)}px; border-color: rgba(250,249,245,.25);"></div>\n')
    b.append(at("minimap", "ui", '<div class="t" style="font-size: 26px;">Minimap</div><div class="s">the engine fits each map in its square</div>',
                "display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;"))
    b.append(hero_rows_svg() + '\n')
    bx, by = CFG["dev"]["build_stamp"]
    b.append(f'<div class="chip s" style="left: {bx}px; top: {by}px; padding: 3px 8px;">FCJH DEV build stamp at {bx}, {by} (dev only)</div>\n')
    rx, ry, rw, rh = R["replay"]
    b.append(f'<div class="chip s" style="left: {rx}px; top: {ry + rh + 10}px; width: {rw}px; padding: 4px 8px;">Operator keys: '
             + " · ".join(f"{key(k)} {what}" for k, what in TOGGLES) + '</div>\n')
    x, y, w, h = R["blue_core"]
    b.append(f'<div class="chip s" style="left: {f1(x)}px; top: {f1(y - 40)}px; width: {f1(w)}px; padding: 3px 8px;">Core HP {f1(w)} × {f1(h)} · shown when a core takes damage</div>\n')
    b.append(f'<div class="chip s" style="left: {f1(R["red_core"][0] + R["red_core"][2] + 10)}px; top: {f1(R["red_xp"][1] - 44)}px; width: 250px; padding: 3px 8px;">'
             f'XP {f1(R["red_xp"][2])} × {f1(R["red_xp"][3])}, {CFG["team_xp"]["gap"]} px above the plates · red at 62%</div>\n')
    return page("Default view, as built", 1920, 1080, "".join(b), MAIN_CSS)


# ================================================================= Plate anatomy
def dim_h(x1, x2, y, label, colour="#FF7A7F"):
    return (f'<line x1="{round(x1, 1)}" y1="{round(y, 1)}" x2="{round(x2, 1)}" y2="{round(y, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<line x1="{round(x1, 1)}" y1="{round(y - 6, 1)}" x2="{round(x1, 1)}" y2="{round(y + 6, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<line x1="{round(x2, 1)}" y1="{round(y - 6, 1)}" x2="{round(x2, 1)}" y2="{round(y + 6, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<text x="{round((x1 + x2) / 2, 1)}" y="{round(y - 12, 1)}" text-anchor="middle" font-family="Barlow, sans-serif" font-size="15" font-weight="600" fill="#FFB3B6">{label}</text>')


def dim_v(x, y1, y2, label, colour="#FF7A7F", side=1):
    return (f'<line x1="{round(x, 1)}" y1="{round(y1, 1)}" x2="{round(x, 1)}" y2="{round(y2, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<line x1="{round(x - 6, 1)}" y1="{round(y1, 1)}" x2="{round(x + 6, 1)}" y2="{round(y1, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<line x1="{round(x - 6, 1)}" y1="{round(y2, 1)}" x2="{round(x + 6, 1)}" y2="{round(y2, 1)}" stroke="{colour}" stroke-width="2"></line>'
            f'<text x="{round(x + 10 * side, 1)}" y="{round((y1 + y2) / 2, 1)}" text-anchor="{"start" if side > 0 else "end"}" dominant-baseline="central" '
            f'font-family="Barlow, sans-serif" font-size="15" font-weight="600" fill="#FFB3B6">{label}</text>')


def callout(x1, y1, x2, y2, label, anchor="start"):
    return (f'<line x1="{round(x1, 1)}" y1="{round(y1, 1)}" x2="{round(x2, 1)}" y2="{round(y2, 1)}" stroke="#6FD3D3" stroke-width="1.5"></line>'
            f'<circle cx="{round(x1, 1)}" cy="{round(y1, 1)}" r="4" fill="#6FD3D3"></circle>'
            f'<text x="{round(x2 + (6 if anchor == "start" else -6), 1)}" y="{round(y2, 1)}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-family="Barlow, sans-serif" font-size="15" font-weight="600" fill="#A8EBEB">{label}</text>')


def px_(v):
    return f"{round(v * PX, 1):g}"


def plate_board():
    W_, z = 1700, 4
    k = PX * z
    w, h = CELL.w * k, CELL.h * k
    svg, b = [], []
    b.append(header("Hero plate · 4× zoom",
                    f"Blizzard's in-game top-bar cell at scale {ROW['scale']:g}: {px_(CELL.w)} × {px_(CELL.h)} px ({CELL.w} × {CELL.h} layout units), "
                    f"{px_(CELL.pitch)} px apart, neighbours interlocking along the slant ({px_(CELL.overlap)} px). "
                    f"Every number below is the build's (tools/gen.py HeroCell), in px at 1080p; units in brackets. Build {STAMP}.", 1600))
    # --- blue, heroic out, CC; red, no heroic, dead
    for row_i, (team, st, uid, title) in enumerate((
            ("blue", {"label": "PORTRAIT", "hp": 0.62, "mp": 0.45, "cc": "STUNNED", "heroic": "ready"}, "zb",
             "Blue · heroic out (bottom right, bars narrowed from the right), stunned"),
            ("red", {"label": "PORTRAIT", "hp": 0.8, "mp": 0.6}, "zr",
             "Red · mirrored, before the heroic (resource row full width)"))):
        x0, y0 = (150, 330) if row_i == 0 else (150, 900)
        b.append(heading(x0 - 90, y0 - 150, title, w=900))
        if team == "blue":
            nb = plate("blue", x0 + CELL.pitch * k, y0, z, {"label": "NEXT", "hp": 0.9, "mp": 0.7, "heroic": "ready"}, "zbn")
            svg.append(f'<clipPath id="nbclip"><rect x="0" y="0" width="1100" height="2000"></rect></clipPath><g opacity=".3" clip-path="url(#nbclip)">{nb}</g>')
        else:
            nb = plate("red", x0 - CELL.pitch * k, y0, z, {"label": "PREV", "hp": 0.9, "mp": 0.7}, "zrn")
            svg.append(f'<clipPath id="nrclip"><rect x="0" y="0" width="1100" height="2000"></rect></clipPath><g opacity=".3" clip-path="url(#nrclip)">{nb}</g>')
        svg.append(plate(team, x0, y0, z, st, uid))
        g = CELL.team[team]
        narrow = rnarrow = NARROW if st.get("heroic") else 0
        svg.append(dim_h(x0, x0 + w, y0 + h + 36, f"{px_(CELL.w)} px ({CELL.w})"))
        svg.append(dim_v(x0 - 40, y0, y0 + h, f"{px_(CELL.h)} ({CELL.h})", side=-1))
        ovx = x0 + w - CELL.overlap * k if team == "blue" else x0
        svg.append(dim_h(ovx, ovx + CELL.overlap * k, y0 - 26, f"overlap {px_(CELL.overlap)}"))
        # pop-up spot
        size = ROW["talent_popup_size"] * z
        cx = x0 + w / 2
        svg.append(f'<rect x="{round(cx - size / 2, 1)}" y="{round(y0 - size / 2, 1)}" width="{round(size, 1)}" height="{round(size, 1)}" fill="none" '
                   f'stroke="#6FD3D3" stroke-width="3" stroke-dasharray="10 6"></rect>')
        right = 1150
        hl, ht, hr, hb = g["health"]
        el, et, er, eb = g["energy"]
        svg.append(callout(cx + size / 2, y0 - size / 4, right, y0 - 60,
                           f"Pop-up · {ROW['talent_popup_size']} px, box centre, straddling the top edge"))
        svg.append(callout(x0 + (hl + narrow + 20) * k, y0 + (ht + hb) / 2 * k, right, y0 + 150,
                           f"Health · {px_((hr - hl - narrow))} × {px_(hb - ht)} ({hr - hl - narrow} × {hb - ht})" + (" · narrowed" if narrow else "")))
        svg.append(callout(x0 + (el + rnarrow + 30) * k, y0 + (et + eb) / 2 * k, right, y0 + 190,
                           f"Resource · {px_(er - el - rnarrow)} × {px_(eb - et)} ({er - el - rnarrow} × {eb - et})" + (" · narrowed" if rnarrow else "")))
        fl, ft, fr, fb = FG[team][0]
        svg.append(callout(x0 + (fl + fr) / 2 * k, y0 + ft * k, right, y0 + 20,
                           f"Fountain · {px_(fr - fl)} × {px_(fb - ft)} ({fr - fl} × {fb - ft}), on the health bar, the plate's outer end"))
        if st.get("cc"):
            svg.append(callout(x0 + w / 2 + (CELL.death_shift + CELL.cc_half) * k, y0 + CELL.cc_mid * k, right, y0 + 60,
                               f"CC icon · {px_(2 * CELL.cc_half)} px ({2 * CELL.cc_half}) square, centred in the portrait"))
            svg.append(callout(x0 + (hr - 10) * k, y0 + ht * k, right, y0 + 100,
                               f"CC text · {FONTS['FCJH_CCText'][0]} px, centred on the health bar"))
        if st.get("heroic"):
            il, it, ir, ib = gen.heroic_icon_rect(CFG, team)
            fl2, ft2, fr2, fb2 = gen.heroic_frame_rect(CFG, team)
            svg.append(f'<rect x="{round(x0 + il * k, 1)}" y="{round(y0 + it * k, 1)}" width="{round((ir - il) * k, 1)}" height="{round((ib - it) * k, 1)}" '
                       f'fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="6 5"></rect>')
            svg.append(callout(x0 + il * k, y0 + (it + 6) * k, right, y0 + 230,
                               f"Heroic · icon {px_(ir - il)} px ({ir - il}) square, gold frame {px_(fr2 - fl2)} × {px_(fb2 - ft2)}"))
            svg.append(callout(x0 + (hl + narrow) * k, y0 + hb * k, right, y0 + 270,
                               f"Bars narrow {px_(NARROW)} px ({NARROW}) from the heroic's side while it shows (blue right, red left)"))
        else:
            svg.append(callout(x0 + w / 2 + CELL.death_shift * k, y0 + CELL.death_mid * k, right, y0 + 100,
                               f"Death timer · centred {px_(CELL.death_shift)} px right of the middle"))
            svg.append(callout(x0 + (hl + 2) * k, y0 + hb * k, right, y0 + 230,
                               "No heroic yet: full-width bars. Red's heroic goes bottom left, blue's bottom right"))
    # --- pop-up storyboard (2x)
    tp, hp = CFG["talent_popup"], CFG["heal_popup"]
    zz, sy = 2, 1520
    b.append(heading(48, sy - 180, "Pop-ups · one spot, one motion",
                     f"Rise {px_(38)} px from inside the plate to straddle its top edge over 0.35 s, fading in over 0.25 s (tools/gen.py popup_frame). "
                     f"Talent: holds {tp['hold']} s, fades over {tp['fade']} s (gone at {round(0.25 + tp['hold'] + tp['fade'], 2)} s), always plays out, drawn on top. "
                     f"Heal: at {hp['threshold']}% or less, holds {hp['hold']} s, fades over {hp['fade']} s; clears at once above {hp['clear_above']}%; "
                     f"fades over {hp['death_fade']} s on a death; a plate can't fire again for {hp['lock']:g} s.", 1600))
    frames = [("0 s · inside the plate, invisible", [("talent", 38 * PX, 0.2, True)]),
              ("0.15 s · rising, fading in", [("talent", 14, 0.7, False)]),
              ("0.35 s · settled on the top edge", [("talent", 0, 1.0, False)]),
              ("Both up · talent on top of heal", [("heal", 0, 1.0, False), ("talent", 0, 1.0, False)]),
              ("Heal alone · until its own end, above 30%, or a death", [("heal", 0, 1.0, False)])]
    for i, (caption, pops) in enumerate(frames):
        fx = 60 + i * 322
        svg.append(plate("blue", fx, sy, zz, {"label": "HERO", "hp": 0.2 if i >= 3 else 0.7, "mp": 0.5}, f"sb{i}"))
        for kind, drop, alpha, ghost in pops:
            svg.append(popup(fx + CELL.w * PX * zz / 2, sy, zz, kind, drop, alpha, ghost=ghost))
        b.append(f'<div class="s" style="position: absolute; left: {fx}px; top: {sy + 190}px; width: 300px; font-size: 15px; color: #C9CAD6;">{caption}</div>\n')
    # --- heroic states (2x)
    hy = 2010
    b.append(heading(48, hy - 180, "Heroic panel · Blizzard's in-game panel, mirrored",
                     "Shows once the heroic is picked (Blizzard's party frame; level 10, or earlier for heroes like Varian at 4). "
                     "Ready: Blizzard's glow. On cooldown: the icon dims and greys with the count from the observer bar's own heroic (one source). "
                     "Tracer: no cooldown, her Pulse Bomb charge meter instead. Hover: the talent icon's own tooltip.", 1600))
    states = [("Before the heroic · bars full width", None), ("Ready · Blizzard's glow", "ready"),
              ("On cooldown · dim, grey, count", "cd37"), ("Tracer · charge meter", "charge")]
    for i, (caption, st) in enumerate(states):
        fx = 60 + i * 400
        stt = {"label": "HERO", "hp": 0.8, "mp": 0.6}
        if st:
            stt["heroic"] = st
        svg.append(plate("blue", fx, hy, zz, stt, f"hs{i}"))
        b.append(f'<div class="s" style="position: absolute; left: {fx}px; top: {hy + 190}px; width: 340px; font-size: 15px; color: #C9CAD6;">{caption}</div>\n')
    # --- special cases (2x)
    cy_ = 2490
    b.append(heading(48, cy_ - 150, "Special plates",
                     f"Lost Vikings: three bars across the health bar, each cut to the plates' lean so neighbours meet on one slanted line "
                     f"under a separator (Baleog, Erik, Olaf), each with its own death timer. "
                     "Rexxar: Blizzard's full-height bar, no Misha bar or timer. Abathur's clone: the Ultimate Evolution icon in the CC spot and CLONE on the bar.", 1600))
    specials = [("Lost Vikings", {"label": "VIKINGS", "vikings": (1.0, 0.45, 0.8), "mp": 0}),
                ("Rexxar", {"label": "REXXAR", "rexxar": True, "hp": 0.7}),
                ("Abathur, cloned", {"label": "ABATHUR", "hp": 0.9, "mp": 0.8, "clone": True})]
    for i, (caption, st) in enumerate(specials):
        fx = 60 + i * 440
        svg.append(plate("blue", fx, cy_, zz, st, f"sp{i}"))
        b.append(f'<div class="s" style="position: absolute; left: {fx}px; top: {cy_ + 190}px; width: 340px; font-size: 15px; color: #C9CAD6;">{caption}</div>\n')
    # --- the fountain on the health bar (2x)
    fy = 3020
    bl, bt, br, bb = FG["blue"][0]
    b.append(heading(48, fy - 210, "Fountain and heroic · either end of the plate",
                     "The inspect card's fountain: Blizzard's buff slot (it leans / as on red; mirrored on blue), bright when ready, dimmed with the seconds left on cooldown. "
                     f"Slot box {px_(br - bl)} × {px_(bb - bt)} px ({br - bl} × {bb - bt}). It stands on the health bar's top edge at the plate's outer end (blue left, red right), "
                     "its slanted side against the plate's edge. The heroic sits at the inner end, by the minimap (blue bottom right, red bottom left: blue's mirrors "
                     "Blizzard's red), and the bars narrow from its side while it shows. Gone with the bars on a death.", 1600))
    cols = [("No heroic · ready", {}), ("No heroic · on cooldown", {"fountain": "cd42"}),
            ("Heroic out, ready", {"heroic": "ready"}),
            ("Heroic out · on cooldown", {"fountain": "cd17", "heroic": "cd37"})]
    for row_i, team in enumerate(("blue", "red")):
        ry = fy + row_i * 300
        for i, (caption, extra) in enumerate(cols):
            fx = 60 + i * 400
            svg.append(plate(team, fx, ry, zz, {"label": "HERO", "hp": 0.7, "mp": 0.5, **extra}, f"fp{team}{i}"))
            b.append(f'<div class="s" style="position: absolute; left: {fx}px; top: {ry + 190}px; width: 340px; font-size: 15px; color: #C9CAD6;">'
                     f'{team.capitalize()} · {caption}</div>\n')
    H = fy + 300 + 240
    b.insert(1, f'<svg width="{W_}" height="{H}" viewBox="0 0 {W_} {H}" style="position: absolute; left: 0; top: 0;" aria-label="Hero plate anatomy, pop-up storyboard, heroic states, special plates">{"".join(svg)}</svg>\n')
    return page("Hero plate anatomy", W_, H, "".join(b)), (W_, H)


# ================================================================= Panes
def panes_board():
    w, h = 2216, 900
    b = [header(f"Info panes · one box, {PANE_W} × {PANE_H}, at 1:1",
                f"At {PANE_X}, {PANE_Y}. One pane at a time, Ctrl+1-4; the X closes it. Stats panes from tools/gen.py (stat_geometry, place_columns); "
                f"numbers are stand-ins. Build {STAMP}.", 2100)]
    panes = [("TALENTS · Ctrl+1", talents_pane()), ("KDA · Ctrl+2", stats_pane("kda")),
             ("HEALING · Ctrl+3", stats_pane("healing")), ("STRUCTURES · Ctrl+4", stats_pane("structures"))]
    for i, (label, html) in enumerate(panes):
        x = 48 + i * 542
        b.append(f'<div class="t" style="position: absolute; left: {x}px; top: 150px; font-size: 18px; color: #F2C94C;">{label}</div>\n')
        b.append(f'<div style="position: absolute; left: {x}px; top: 184px;">{html}</div>\n')
    g = gen.stat_geometry(CFG)
    gap = g["row_tops"][1] - g["row_tops"][0] - gen.STAT_ROW_H
    b.append(f'<div class="s" style="position: absolute; left: 48px; top: 790px; width: 494px; font-size: 15px; color: #C9CAD6;">Rows {u(60)} px apart (Blizzard\'s 60-unit row), portrait {u(23)} px in. Blizzard\'s talent icons and team squares.</div>\n')
    b.append(f'<div class="s" style="position: absolute; left: 590px; top: 790px; width: 1576px; font-size: 15px; color: #C9CAD6;">'
             f'Title {CFG["info_pane"]["title_height"]} px, headings {CFG["info_pane"]["header_height"]} px, team bands {CFG["info_pane"]["team_height"]} px. '
             f'Rows {u(gen.STAT_ROW_H)} px tall, {u(gap)} px apart, spread to fill the box so switching panes never resizes it. '
             f'Numbers right-aligned in columns {u(gen.STAT_SHARE_W)} px per share (a count 1, a big number 2); the spare room is shared as equal gaps, '
             f'so the last column ends {u(gen.STAT_MARGIN)} px from the edge, like the portrait on the left.</div>\n')
    return page("Info panes, as built", w, h, "".join(b)), (w, h)


# ================================================================= Inspect
def inspect_board():
    w, h = 1560, 1000
    ix, iy, iw, ih = R["inspect"]
    b = [header(f"Inspect card · {iw} × {ih} at 1:1",
                f"At {ix}, {iy}; bottom at {iy + ih}, clear of the blue core bar. Shows exactly when Blizzard's small inspector would (a unit selected; "
                f"click off to hide), never on a plate click. Laid out from tools/inspect_card.py. Build {STAMP}.", 1460)]
    b.append(f'<div style="position: absolute; left: 48px; top: 150px;">{inspect_card()}</div>\n')
    rows = [
        ("Title band, X", "game", "The X closes the card until the next selection. A click anywhere inside no longer falls through to the map."),
        ("Portrait", "game", "The selected player's plate picture, same crop, from the title band down to the name band."),
        ("Name, player, level", "game", "The hero's name in the title band; the player's name and the level, one size, in the band under the portrait. "
                                        "Blizzard's widgets; the player name from the talent pane's row. Card edge in the player's team colour."),
        ("Health, resource", "game", "Blizzard's inspect-box bars, placed. Regen on the right."),
        ("Fountain, buffs, debuffs", "game", "One block, no heading: the fountain first, in Blizzard's buff slot art (dim on cooldown), with its countdown, then buffs, then "
                                             "debuffs, all on one row."),
        ("Abilities", "game", "Blizzard's own command card laid on the card: talent actives (1-5) over Z Q W E R D, honeycombed; tooltips, cooldowns and charges "
                              "are the game's. An empty Q W E R slot shows Blizzard's empty frame."),
        ("Talents", "game", "Blizzard's talent strip for the selected player; an icon and its team square show once its tier is picked. Tier levels underneath."),
        ("Stats", "game", f"Blizzard's seven stats in three columns, related values sharing a row: attack damage / speed / range; "
                          f"spell power / move speed; armor / spell armor. Rows {u(ic.STAT_ROW)} px apart; tooltips open off the card's right edge."),
        ("Spare", "none", "The bottom of the card is empty. Room for quests, or a shorter card, in the visual pass."),
    ]
    b.append('<div style="position: absolute; left: 400px; top: 150px; width: 1110px;"><table style="border-collapse: collapse; width: 100%;">'
             '<thead><tr><th style="width: 190px;">Block</th><th style="width: 150px;">Status</th><th>How</th></tr></thead><tbody>\n')
    for n, st, d in rows:
        tg = tag(st) if st != "none" else '<span class="k none">Empty</span>'
        b.append(f'<tr><td>{n}</td><td>{tg}</td><td>{d}</td></tr>\n')
    b.append('</tbody></table>\n')
    b.append(f'<div class="s" style="margin-top: 18px; font-size: 15px; color: #C9CAD6;">Section tops, px from the card\'s top: buffs {u(ic.BUFFS)}, abilities {u(ic.ABIL_ROWS[0])}, '
             f'talents {u(ic.TAL_LABEL)}, stats {u(ic.STATS_LABEL)}. Side margin {u(ic.M)} px. The card and the info pane share the left column; '
             'the card sits over whichever pane is up.</div></div>\n')
    return page("Inspect card, as built", w, h, "".join(b)), (w, h)


# ================================================================= Top bar
def obs_areas():
    """The OBS areas' rects and the logos' clearance from the wings, for the top bar board."""
    geo = gen.top_backplate_geometry(CFG)
    r = lambda k: f"{R[k][0]}, {R[k][1]} · {R[k][2]} × {R[k][3]}"
    g = gen.top_bar_geometry(CFG)
    return (f"Blue, outside in: the score's pips {r('blue_pips')} (a best of 7's four, {CFG['top_bar']['pip_off_name']} px off the name and "
            f"{CFG['top_bar']['pip_gap']} apart, filled from the name outward), the name plate {r('blue_name')} with its logo plate {r('blue_logo')} "
            f"lapping the inner end so the two rims make one seam at x {f1(g['seam'])}. The band is the wings' height and its inner end is the wing's "
            f"({f1(geo['ends'][0])} along the top edge). Second row: bans under the name, {r('blue_bans')}, {BANS} tiles at the plates' lean; the division "
            f"tab {r('division')} and the game tab {r('game_count')} hung from the band to the tiles' bottom, their outer sides the seam carried down and "
            f"their inner sides {CFG['top_bar']['tab_clear']} px off Blizzard's hexagon. Red mirrors blue about x 960 - except the two tabs, which follow "
            f"the hexagon, 2.75 px left of it. The tournament's logo goes in the hexagon's middle, {r('event_logo')}; its name has left the clock for a tab "
            f"of its own, still to settle. Every box from layout.toml [top_bar] (gen.top_bar_geometry), so the interface and the OBS layer can't drift apart.")


def topbar_board():
    w = 1920
    geo = gen.top_backplate_geometry(CFG)
    b = [header("Top bar · as built",
                f"Our backplate (variant C: silver chrome rim; team colour strongest at the wings' outer ends, fading to a stock dark toward the hexagon; "
                f"a hexagon lattice fading the same way). It becomes the basis of the rest of the UI in the visual pass. One {gen.TOP_BACKPLATE_SIZE[0]} × "
                f"{gen.TOP_BACKPLATE_SIZE[1]} px frame at x {R['top_backplate'][0]} (its texture drawn for 1440p, shown at 75% here), from layout.toml [top_backplate]. Build {STAMP}.", 1820)]
    # 1:1 strip
    b.append(heading(48, 150, "1:1 · the top of the screen"))
    b.append('<div style="position: absolute; left: 0; top: 200px; width: 1920px; height: 200px; overflow: hidden; background: #0b0c14;">'
             f'<img src="{BG}" alt="" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; opacity: 0.45;">'
             + top_bar() + at("replay", "ui", '<div class="t" style="font-size: 16px;">Replay controls</div>', "padding: 10px;")
             + '</div>\n')
    # zoom
    z = 3
    x0, x1 = geo["ends"][0] - 8, geo["ends"][1] + 8
    zx, zy = 48, 500
    zw, zh = (x1 - x0) * z, 132 * z
    b.append(heading(48, 440, f"{z}× · the shapes, with their numbers"))
    tx = lambda x: zx + (x - x0) * z
    ty = lambda y: zy + y * z
    shp = lambda p: pts([(tx(a), ty(c)) for a, c in p])
    over = [f'<svg width="{w}" height="{zy + zh + 40}" viewBox="0 0 {w} {zy + zh + 40}" style="position: absolute; left: 0; top: 0;" aria-label="The backplate at 3x with its geometry">',
            f'<polygon points="{shp(geo["wings"])}" fill="none" stroke="#6FD3D3" stroke-width="2" stroke-dasharray="8 6"></polygon>',
            f'<polygon points="{shp(geo["padded"])}" fill="none" stroke="#F2C94C" stroke-width="2" stroke-dasharray="8 6"></polygon>',
            f'<polygon points="{shp(geo["hexagon"])}" fill="none" stroke="#FF7A7F" stroke-width="2"></polygon>']
    for key in ("blue_level", "red_level"):
        x, y, lw, lh = R[key]
        over.append(f'<rect x="{round(tx(x), 1)}" y="{round(ty(y), 1)}" width="{lw * z}" height="{lh * z}" fill="none" stroke="#FAF9F5" stroke-opacity=".7" stroke-width="2" stroke-dasharray="4 4"></rect>')
    over.append(dim_h(tx(geo["ends"][0]), tx(geo["ends"][1]), ty(0) - 18, f"wings {round(geo['ends'][0], 1)} – {round(geo['ends'][1], 1)} on the top edge"))
    over.append('</svg>')
    bx = R["top_backplate"][0]
    b.append(f'<div style="position: absolute; left: {zx}px; top: {zy}px; width: {round(zw)}px; height: {round(zh)}px; overflow: hidden; background: #0b0c14;">'
             f'<img src="{BACKPLATE}" alt="The backplate texture at 3x" style="position: absolute; left: {round((bx - x0) * z)}px; top: 0; '
             f'width: {gen.TOP_BACKPLATE_SIZE[0] * z}px; height: {gen.TOP_BACKPLATE_SIZE[1] * z}px;"></div>\n')
    b.append("".join(over) + "\n")
    nx = zx + zw + 48
    hexagon = ", ".join(f"({f1(a)}, {f1(c)})" for a, c in BP["hexagon"])
    items = [("Red line · Blizzard's hexagon", f"TopBarLogoOverlay's outer edge as it lands at 1920 × 1080, measured at 6× from a screenshot: {hexagon}. Not regular: the top edge is wider than the bottom."),
             ("Gold dashes · the hexagon's plate", f"The hexagon grown {BP['padding']} px: a neutral plate, {BP['plate'][0]} to {BP['plate'][1]}; only its padding shows under Blizzard's art."),
             ("Teal dashes · the wings", f"Along the top edge, {BP['wing_margin']} px past each level plate's outer edge, down to the hexagon's side points (y {f1(geo['wings'][2][1])}); "
                                         f"the ends climb with the plates' lean ({round(LEAN, 3)} across per down)."),
             ("White dashes · team levels", f"Blizzard's level numbers, {R['blue_level'][2]} × {R['blue_level'][3]} at x {R['blue_level'][0]} and {R['red_level'][0]}. "
                                            "The talent-lead flame shows behind the team that's ahead."),
             ("Colour", f"Team colours = the plates' health bars ({HP['blue']}, {HP['red']}), strength along each wing {BP['fade']} (0 beside the hexagon, 1 at the end), "
                        f"over a stock dark {BP['stock'][0]} to {BP['stock'][1]}."),
             ("Orange dashes · OBS", "OBS draws data only, never art (user, 2026-10-16): the plates under it are ours, the name plates now and the rest in the art pass. " + obs_areas()),
             ("Rim and pattern", f"Chrome {', '.join('#' + c for c in BP['rim'])}, {BP['rim_width']} px; sheen {BP['sheen']}; hexagons {BP['hex_px']} px across at {BP['lattice']} strength.")]
    y = zy
    for t, d in items:
        b.append(note(nx, y, w - nx - 48, t, d))
        y += max(128, 60 + 20 * -(-len(d) * 7 // (w - nx - 48)))   # as tall as its text wraps
    # references
    ry = max(zy + zh, y) + 80
    b.append(heading(48, ry, "Blizzard's, for reference",
                     "Default observer bar (the colour beside the hexagon, the stock dark, faint hexagons), and the in-game top bar the plates are built from.", 1800))
    b.append(f'<img src="{REF_OBS_LEVELS}" width="880" height="320" alt="Blizzard\'s default observer top bar, levels and hexagon, at 2x" style="position: absolute; left: 48px; top: {ry + 80}px; border-radius: 6px;">\n')
    b.append(f'<div class="s" style="position: absolute; left: 960px; top: {ry + 80}px; font-size: 15px; color: #C9CAD6;">In-game top bar, heroics out · 1:1</div>\n')
    b.append(f'<img src="{REF_TOP_ULTS}" width="1130" height="60" alt="Blizzard\'s in-game top bar with heroics" style="position: absolute; left: 960px; top: {ry + 106}px; max-width: 912px; height: auto;">\n')
    b.append(f'<div class="s" style="position: absolute; left: 960px; top: {ry + 190}px; font-size: 15px; color: #C9CAD6;">Before the heroics · 1:1</div>\n')
    b.append(f'<img src="{REF_TOP_NOULTS}" width="1130" height="60" alt="Blizzard\'s in-game top bar before heroics" style="position: absolute; left: 960px; top: {ry + 216}px; max-width: 912px; height: auto;">\n')
    h = ry + 80 + 320 + 60
    return page("Top bar, as built", w, round(h), "".join(b), MAIN_CSS), (w, round(h))


# ================================================================= Visual language
def swatch(color, name, value, border=False):
    bd = "border: 1px solid rgba(255,255,255,.3);" if border else ""
    return (f'<div style="display: flex; align-items: center; gap: 10px;"><div style="width: 40px; height: 28px; border-radius: 3px; background: {color}; {bd}"></div>'
            f'<div style="display: flex; flex-direction: column;"><div class="s" style="font-size: 14px; color: #ECECF1;">{name}</div>'
            f'<div class="s" style="font-size: 12px; color: #A7A9B8;">{value}</div></div></div>')


def visual_board():
    w = 1700
    band = lambda t: gen.TEAMS[t][2].split(",")
    rgba = lambda c: f"rgba({','.join(c[1:])},{int(c[0]) / 255:.2f})"
    sv = lambda n: FONTS[n]
    b = ['<div style="position: absolute; left: 0; top: 0; width: 1700px; box-sizing: border-box; padding: 40px 48px; display: flex; flex-direction: column; gap: 28px;">\n',
         '<div style="display: flex; flex-direction: column; gap: 6px;"><h1 style="margin: 0; font-family: \'Barlow Condensed\', sans-serif; font-weight: 700; font-size: 40px; letter-spacing: .03em; text-transform: uppercase;">Visual language · what we have, what to decide</h1>'
         f'<p style="margin: 0; font-size: 16px; color: #A7A9B8;">Every value is what the build uses today (px at 1080p, read from layout.toml, gen.py and FontStyles; build {STAMP}). The agenda for the final art pass.</p></div>\n',
         '<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 40px;">\n']
    colours = [swatch(HP["blue"], "Blue · plates + backplate", f"{HP['blue']} · Blizzard's health fill, sampled"),
               swatch(HP["red"], "Red · plates + backplate", f"{HP['red']}"),
               swatch(sv("FCJH_StatValue_Blue")[1], "Blue · pane numbers", f"{sv('FCJH_StatValue_Blue')[1]} · totals {sv('FCJH_StatTotal_Blue')[1]}"),
               swatch(sv("FCJH_StatValue_Red")[1], "Red · pane numbers", f"{sv('FCJH_StatValue_Red')[1]} · totals {sv('FCJH_StatTotal_Red')[1]}"),
               swatch(rgba(band(0)), "Blue band", f"{','.join(band(0)[1:])} at {round(int(band(0)[0]) / 2.55)}%"),
               swatch(rgba(band(1)), "Red band", f"{','.join(band(1)[1:])} at {round(int(band(1)[0]) / 2.55)}%"),
               swatch(CORE["blue"], "Core HP", f"{CORE['blue']} · {CORE['red']}"),
               swatch(XP_FILL, "XP fill", f"{XP_FILL}, both teams · track {TRACK}"),
               swatch(HEAL, "Heal pop-up", f"{HEAL}, plus and border"),
               swatch(f"linear-gradient(#{BP['rim'][0]}, #{BP['rim'][1]} 35%, #{BP['rim'][2]} 60%, #{BP['rim'][3]})", "Chrome rim", " · ".join("#" + c for c in BP["rim"])),
               swatch(f"linear-gradient(#{BP['stock'][0]}, #{BP['stock'][1]})", "Stock dark", f"#{BP['stock'][0]} → #{BP['stock'][1]}", True),
               swatch("rgba(11,12,20,.84)", "Pane / card backdrop", "11,12,20 at 84% · title band 24,28,48 at 92%", True)]
    b.append('<div style="display: flex; flex-direction: column; gap: 12px;"><div class="t" style="font-size: 20px; color: #F2C94C;">Colour, today</div>' + "".join(colours) +
             '<div class="s" style="font-size: 14px; color: #FFB3B6; margin-top: 4px;">Still four blues and four reds: health/backplate, pane numbers, bands, core. The backplate already took the health bars\' pair.</div></div>\n')
    styles = [("FCJH_StatHeading", "COLUMN HEADING"), ("FCJH_StatValue_Blue", "2,252 · value"), ("FCJH_StatTotal_Blue", "13,660 · team total, glow"),
              ("FCJH_StatTeam_Blue", "BLUE · team band"), ("FCJH_CCText", "STUNNED · CC text, outlined"), ("FCJH_HeroicCooldown", "37 · cooldown"),
              ("FCJH_InspectName", "Auriel · inspect name"), ("FCJH_InspectSub", "PLAYER · inspect sub"), ("FCJH_InspectSection", "ABILITIES · section"),
              ("FCJH_InspectTier", "20 · tier level")]
    type_rows = [f'<div style="{GAME} font-size: {sv(n)[0]}px; font-weight: 600; color: {sv(n)[1] if sv(n)[1] not in ("#ffffff", None) else "#FAF9F5"};">{s} · {sv(n)[0]} px</div>' for n, s in styles]
    sizes = sorted({sv(n)[0] for n, _ in styles})
    b.append('<div style="display: flex; flex-direction: column; gap: 10px;"><div class="t" style="font-size: 20px; color: #F2C94C;">Type, today</div>' + "".join(type_rows) +
             f'<div class="s" style="font-size: 14px; color: #FFB3B6; margin-top: 4px;">Blizzard\'s fonts (HeaderExtendedTemplate; Exo 2 stands in here). {len(sizes)} sizes of ours: {", ".join(f1(s) for s in sizes)} px, '
             'plus Blizzard\'s own (levels, clock, death timers, heroic count).</div></div>\n')
    g = gen.stat_geometry(CFG)
    spacing = [f"Plate · <b>{px_(CELL.w)} × {px_(CELL.h)}</b>, <b>{px_(CELL.pitch)}</b> apart, overlap <b>{px_(CELL.overlap)}</b> (scale {ROW['scale']:g})",
               f"Rows · blue <b>{f1(ROW['blue_left'])}–{ROW['blue_right']}</b>, red <b>{ROW['red_left']}–{f1(R['hero_0'][0] + R['hero_0'][2])}</b>, top <b>{f1(ROW['top'])}</b>, bottom <b>{ROW['bottom']}</b>",
               f"XP · <b>{CFG['team_xp']['height']} px</b>, <b>{CFG['team_xp']['gap']} px</b> above the plates · core <b>{f1(R['blue_core'][3])} px</b>, <b>{CFG['team_core']['gap']} px</b> above XP",
               f"Pop-ups · <b>{ROW['talent_popup_size']} px</b> square",
               f"Pane side margin · <b>{u(gen.STAT_MARGIN)} px</b> · inspect <b>{u(ic.M)} px</b>",
               f"Title band <b>{CFG['info_pane']['title_height']}</b> · headings <b>{CFG['info_pane']['header_height']}</b> · team band <b>{CFG['info_pane']['team_height']}</b> px",
               f"Stats rows · <b>{u(gen.STAT_ROW_H)} px</b>, <b>{u(g['row_tops'][1] - g['row_tops'][0] - gen.STAT_ROW_H)} px</b> apart · talent rows <b>{u(60)} px</b>",
               f"Inspect icons · <b>{u(ic.TAL_SIZE)} px</b>, <b>{u(ic.TAL_STEP)} px</b> pitch",
               f"Screen edge margin · <b>{CFG['screen']['padding']} px</b> (replay art, panes, card, plates)"]
    b.append('<div style="display: flex; flex-direction: column; gap: 10px;"><div class="t" style="font-size: 20px; color: #F2C94C;">Spacing, today</div>' +
             "".join(f'<div class="s" style="font-size: 14px;">{s}</div>' for s in spacing) +
             '<div class="s" style="font-size: 14px; color: #FFB3B6; margin-top: 4px;">Numbers from three places: our px, Blizzard\'s units (0.9 px each), and Blizzard\'s art. No shared grid.</div></div>\n')
    b.append('</div>\n')
    rows = [("Hero plates", "mix", "Frame, glass, health and mana fills, heroic panel: Blizzard's in-game cell. Portrait crop and mask, CC, fountain, pop-ups: ours"),
            ("Top bar backplate", "ours", "Our generated texture (chrome rim, team fade, hexagon lattice). The hexagon, level numbers, flame and clock on it: Blizzard's"),
            ("Team XP", "mix", "Blizzard's bar; our solid fill, slanted track and mask"),
            ("Core HP", "mix", "Blizzard's bar and number; our slanted track and mask, our fills"),
            ("Pop-ups", "mix", "Talent icon and highlight square: Blizzard's. Heal border: ours. Motion: ours"),
            ("Info panes", "mix", "Backdrop, bands, lines, number styles: ours. Talent icons, portraits, best-value underlines: Blizzard's"),
            ("Inspect card", "mix", "Layout, backdrop, bands: ours. Bars, stats, buffs, ability and talent widgets: Blizzard's"),
            ("Kill feed", "bz", "Blizzard's, in its own place"), ("Replay · minimap", "bz", "Blizzard's, only moved (the replay's collapsed tab is ours)")]
    lab = {"bz": ("bz", "Blizzard"), "ours": ("ours", "Ours"), "mix": ("mix", "Mixed")}
    b.append('<div style="display: flex; flex-direction: column; gap: 8px;"><div class="t" style="font-size: 20px; color: #F2C94C;">Whose art is on screen</div>'
             '<table style="border-collapse: collapse; width: 100%;"><thead><tr><th style="width: 240px;">Element</th><th style="width: 110px;">Art</th><th>What\'s Blizzard\'s, what\'s ours</th></tr></thead><tbody>\n')
    for n, kk, d in rows:
        c, t = lab[kk]
        b.append(f'<tr><td>{n}</td><td><span class="k {c}">{t}</span></td><td>{d}</td></tr>\n')
    b.append('</tbody></table></div>\n')
    qs = [("One look", "DECIDED 30 Sept: the chrome backplate (variant C) is the basis. Carry its rim, stock dark and team fade onto the panes, the card, the pop-ups and the plate trays."),
          ("One blue, one red", "Started: the backplate uses the health bars' pair. Pane numbers, bands and core fills still have their own. Move them all onto one pair, or keep the brighter pair for text only?"),
          ("Core HP", "Blizzard's (reference below): slanted, draining from the outer end, vertical gradient with a bright line at the drain edge, dark empty part with a team outline, number at the inner end. "
                      "Player view adds a horizontal bevel through the middle. Worth doing for XP too?"),
          ("A spacing grid", "One step (4 or 8 px) for margins, bands and row pitch; talent and stats rows could share one pitch."),
          ("A type ramp", "Three sizes, not ten (label, value, headline), and whether Blizzard's own labels get resized to match."),
          ("Density", "Stats rows spread to fill (fixed box) or pack tight (box per pane)? The inspect card's spare bottom: fill it or shorten the card?"),
          ("Blizzard skins", "Kill feed, replay panel, inspect bars: keep Blizzard's, or reskin in chrome?"),
                    ("Numbers", "Thousands separators (13,660) or short form (13.7k)?")]
    b.append('<div style="display: flex; flex-direction: column; gap: 10px;"><div class="t" style="font-size: 20px; color: #F2C94C;">To decide together</div>'
             '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 40px;">')
    for i, (t, d) in enumerate(qs):
        b.append(f'<div style="display: flex; gap: 12px;"><div class="t" style="font-size: 22px; color: #6FD3D3; width: 24px;">{i + 1}</div>'
                 f'<div style="display: flex; flex-direction: column; gap: 3px;"><div class="t" style="font-size: 17px;">{t}</div>'
                 f'<div class="s" style="font-size: 15px; color: #C9CAD6;">{d}</div></div></div>')
    b.append('</div></div>\n')
    b.append('<div style="display: flex; flex-direction: column; gap: 10px;"><div class="t" style="font-size: 20px; color: #F2C94C;">References for the art pass</div>'
             '<div class="s" style="font-size: 15px; color: #C9CAD6;">Blizzard\'s default observer core HP bars (1:1)</div>'
             f'<img src="{REF_CORE}" width="850" height="55" alt="Blizzard\'s default observer core health bars" style="display: block;">'
             '<div class="s" style="font-size: 15px; color: #C9CAD6; margin-top: 8px;">Blizzard\'s in-game top bar, heroics out (1:1): the plates\' source</div>'
             f'<img src="{REF_TOP_ULTS}" width="1130" height="60" alt="Blizzard\'s in-game top bar with heroics" style="display: block;"></div>\n')
    b.append('</div>\n')
    h = 1880
    return page("Visual language, to decide", w, h, "".join(b)), (w, h)


# ================================================================= Spec
def spec_board():
    w = 1100
    blue_r = R["hero_5"][0] + R["hero_5"][2]
    red_r = R["hero_0"][0] + R["hero_0"][2]
    tp, hp = CFG["talent_popup"], CFG["heal_popup"]
    xs = lambda k: f"{f1(R[k][2])} × {f1(R[k][3])}"
    obs = lambda k: f"{f1(R[k][0])}, {f1(R[k][1])} · {xs(k)}"
    rows = [
        ("Hero plates × 10", f"{px_(CELL.w)} × {px_(CELL.h)} (scale {ROW['scale']:g}), blue x {f1(ROW['blue_left'])}–{f1(blue_r)}, red x {ROW['red_left']}–{f1(red_r)}, y {f1(ROW['top'])}–{ROW['bottom']}", "game",
         "Blizzard's in-game cell art, scaled to fit the padding, portrait masked to the slant. A click selects the hero and follows it (camera lock L on). D.Va's mech, TLV and Misha take no clicks (Blizzard's)"),
        ("Health + resource", "Each plate; narrowed while the heroic shows", "game", "Blizzard's fill art. Resource colour per hero"),
        ("Heroic panel", "The plate's inner end: blue bottom right, red bottom left", "game", "Blizzard's panel mirrored: icon, gold frame, ready glow, cooldown dim + count, tooltip, Tracer's charge meter"),
        ("CC icon + text", f"Icon {px_(2 * CELL.cc_half)} px in the portrait; text on the health bar", "game", "Text fits the bar's width (UNSTOPPABLE fits)"),
        ("Death timers", "Plate centre", "game", "Per-Viking timers too; Misha's removed"),
        ("Special plates", "Vikings, Rexxar, Abathur", "game", "Vikings in thirds (Baleog, Erik, Olaf); Rexxar full-height bar; Abathur's clone icon + CLONE"),
        ("Fountain", "On the health bar at the plate's outer end", "game", "Bright when ready, dimmed with its count on cooldown"),
        ("Talent pop-ups", f"{ROW['talent_popup_size']} px, straddling the top edge", "game", f"Hold {tp['hold']} s, fade {tp['fade']} s; always play out; drawn over heal"),
        ("Heal pop-up", f"Same spot and motion; at {hp['threshold']}% or less", "game", f"Hold {hp['hold']} s; clears above {hp['clear_above']}%; fades at once on death; {hp['lock']:g} s lock per plate"),
        ("Team XP", f"{xs('blue_xp')}, y {f1(R['blue_xp'][1])}, on the plates' top edge", "game", "Cut to the slant; hidden until a team's first hero loads. Moves with the plates"),
        ("Core HP", f"{xs('blue_core')}, y {f1(R['blue_core'][1])}, on XP at the inner end", "game", "Blizzard's bar and size, our slanted track and mask; shows while a core takes damage"),
        ("Map banners", f"Beside the minimap: bars {CFG['map_alerts']['above_core']} px over the core bar, blue's ending at x {ROW['blue_right']}, red's starting at {ROW['red_left']}", "game",
         f"Every map's, in one place on every map; neutral ones on red's side; stacked {f1(round(maps.step() * PX, 1))} px apart (Maps board)"),
        ("Map objectives", "Round the minimap, per map", "game", f"Neutral objectives above the minimap at THE GAP ({CFG['minimap']['alert_gap']} px over the map's top tip). Every map passed 2026-10-15/16 (Maps board)"),
        ("Minimap", f"Bottom-centre, {xs('minimap')}", "game", f"Placed per map, each map's visual bottom on THE FLOOR, y {CFG['minimap']['floor']}"),
        ("Top bar backplate", f"{gen.TOP_BACKPLATE_SIZE[0]} × {gen.TOP_BACKPLATE_SIZE[1]} texture at x {R['top_backplate'][0]}", "game", "Variant C, chrome. The look the rest of the UI follows"),
        ("Team levels + flame", f"{xs('blue_level')} at x {R['blue_level'][0]} / {R['red_level'][0]}", "game", "Blizzard's numbers; the talent-lead flame works"),
        ("Hexagon, clock", "Blizzard's places", "game", "Towers and kills removed"),
        ("Name plates", f"{obs('blue_name')} / {f1(R['red_name'][0])}", "obs", "OBS's own art, the one exception: only OBS knows whether a tournament has logos. Without OBS, no name plates"),
        ("Team names", "On the name plates", "obs", "Data only: OBS never draws art (user, 2026-10-16)"),
        ("Team logos", f"{obs('blue_logo')} / {f1(R['red_logo'][0])}", "obs", "A logo plate lapping the name plate's inner end, one seam between them"),
        ("Series score", f"{obs('blue_pips')} / {f1(R['red_pips'][0])}", "obs", "Hexagon pips, no plate: 2 a side in a Bo3, 3 in a Bo5, 4 in a Bo7, filled from the name outward"),
        ("Bans", f"{obs('blue_bans')} / {f1(R['red_bans'][0])}", "obs", f"The game's bans, {BANS} tiles a side under the name, at the plates' lean. Optional: a toggle"),
        ("Division + game tabs", f"{obs('division')} / {obs('game_count')}", "built", "Our art (gen.top_bar_tab_texture): stock fill, a chrome line down the sides and along the bottom, none across the top. OBS writes the words"),
        ("Ban tiles", "Under each name, the band's second row", "unk", "Interface art, still to build: the empty tiles, and a way to hide them - their size and shape get their own pass"),
        ("Tournament logo", f"{obs('event_logo')}, the hexagon's middle", "obs", "Over Blizzard's hexagon, masked to it (event_mask.png)"),
        ("Tournament name", "A tab of its own", "unk", "It has left the clock; where exactly is still to settle (user, 2026-10-19)"),
        ("Division", f"{obs('division')}, hung from blue's wing", "obs", "With the bracket stage if it fits. A generic panel: what goes in it is the operator's call"),
        ("Game count", f"{obs('game_count')}, hung from red's wing", "obs", "Game N of M"),
        ("Kill feed", "Blizzard's own, top-left", "game", "Not moved: its rows grow rightward, so multi-kills ran off a right-hand feed"),
        ("Replay controls", f"{R['replay'][0]}, {R['replay'][1]} · {xs('replay')}, top-right", "game", f"{key('replay')} slides them out, leaving a tab flush in the corner. Replays only"),
        ("Operator keys", " · ".join(key(k) for k, _ in TOGGLES), "game", "The replay box, chat, the inspect card, player names. None a Blizzard key (validate.py checks)"),
        ("Info panes", f"{PANE_X}, {PANE_Y} · {PANE_W} × {PANE_H}", "game", "Ctrl+1-4: talents, KDA + hero dmg, healing, structures + XP. One at a time"),
        ("Inspect card", f"{R['inspect'][0]}, {R['inspect'][1]} · {xs('inspect')}", "game", f"Shows when Blizzard's small inspector would. Anything not a hero gets a short card. {key('inspect')} slides it off left"),
        ("Blizzard's small inspector", "Parked off screen", "game", "Never shows; its visibility drives our card"),
        ("Player HUD", "Hidden", "game", "Ctrl+5 is Blizzard's observe-player key"),
    ]
    # the board's height, from the rows: each as tall as its longest cell wrapped (~7 px a
    # character at 15 px, in columns of ~156, ~266 and ~430 px)
    lines = lambda t, cw: -(-len(t) * 7 // cw)
    h = 300 + sum(19 + 20 * max(lines(n, 156), lines(wh, 266), lines(nt, 430)) for n, wh, _, nt in rows)
    b = [f'<div style="position: absolute; left: 0; top: 0; width: {w}px; box-sizing: border-box; padding: 40px 44px; display: flex; flex-direction: column; gap: 18px;">\n',
         '<div style="display: flex; flex-direction: column; gap: 6px;"><h1 style="margin: 0; font-family: \'Barlow Condensed\', sans-serif; font-weight: 700; font-size: 40px; letter-spacing: .03em; text-transform: uppercase;">Default view · element spec</h1>'
         f'<p style="margin: 0; font-size: 16px; color: #A7A9B8;">As built, {STAMP}. Positions in px at 1920 × 1080, from layout.toml through tools/gen.py.</p></div>\n',
         '<div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 14px; color: #C9CAD6;">'
         f'<span>{tag("game")} seen working</span><span>{tag("built")} in the build</span><span>{tag("unk")} not started</span><span>{tag("obs")} left for OBS</span></div>\n',
         '<table style="border-collapse: collapse; width: 100%;"><thead><tr><th style="width: 180px;">Element</th><th style="width: 290px;">Where · size</th><th style="width: 130px;">Status</th><th>Notes</th></tr></thead><tbody>\n']
    for n, where, st, nt in rows:
        b.append(f'<tr><td>{n}</td><td>{where}</td><td>{tag(st)}</td><td>{nt}</td></tr>\n')
    b.append('</tbody></table>\n</div>\n')
    return page("Default view element spec", w, h, "".join(b)), (w, h)


# ================================================================= Maps
# Every battleground's minimap and banners, from tools/maps.py and layout.toml: the drawn map
# (its texture's opaque part, as the engine fits it), the banners where the banner standard puts
# them (user, 2026-10-09), and the neutral objectives at THE GAP. What the drawing can't show
# (counters, hexagons, gliding) is in each map's note, from docs/maps.md.
MAP_CROP = (240, 440, 1440, 640)          # x, y, w, h: the bottom of the screen, where every map's UI is
STANDARD_CROP = (160, 440, 1740, 640)     # ...wider for the standard's numbers
NEUTRAL = "#9C8CFF"
FLOOR_C, GAP_C, MAP_C = "#F2C94C", "#FF7A7F", "#6FD3D3"
LINE = CFG["screen"]["height"] - CFG["screen"]["padding"]     # the padding line: a placed map's box bottom
SQ = gen.MINIMAP_SQUARE * PX
BANNER = {                                # labels where the alert's note doesn't make one
    "RavenNotificationFrame": "cannons firing (players only)", "NecroNotificationFrame": "cannons firing (players only)",
    "FCJH_BlueTown": "a town taken (ours)", "FCJH_RedTown": "a town taken (ours)",
    "AVCavalryBlue": "the cavalry, blue's", "AVCavalryRed": "the cavalry, red's",
}
AT_GAP = {                                # what each map has at THE GAP: maps.py `above` and gap_parts
    "alterac_pass": ["the cage fight"], "battlefield_of_eternity": ["the Immortals' fight"],
    "hanamura_temple": ["payload · countdown · shots"], "TempleModeFrame": "the temples",
    "SoulEaterFrame": "Webweavers", "SoulCageCooldownFrame": "egg timer", "CenterHex": "capture point",
    "VolskayaToastContainer": "toast",
}
MAP_NOTES = {                             # summarised from docs/maps.md
    "alterac_pass": "The cage fight's bar and banners at THE GAP; the cavalry jumps to the winning team's banner spot.",
    "battlefield_of_eternity": "The Immortals' fight above the minimap at THE GAP. Their countdown neutral on red's side, then the winner's Immortal on its own side.",
    "blackhearts_bay": "The chests neutral on red's side; the cannon on the firing team's side; doubloon counts on the panel.",
    "braxis_holdout": "The zerg wave warning neutral on red's side; Blizzard's HUD compacted above the map.",
    "cursed_hollow": "The tribute neutral on red's side; the curse on the cursed team's side; tribute counts at the minimap's bottom corners.",
    "dragon_shire": "The shrines' countdown neutral on red's side; the Dragon Knight on its team's side; shrine markers on the panel.",
    "garden_of_terror": "The seed banners neutral, at red's spot; the Terrors on their team's side.",
    "hanamura_temple": "No team banners: the payload, countdown and shots stay Blizzard's, above the minimap at THE GAP.",
    "haunted_mines": "Opens on its top part (dashed, at load) and glides to its place when the mines open. Mines and golems neutral on red's side; skull counts.",
    "infernal_shrines": "The shrine's countdown neutral on red's side; the Punisher on the summoner's side. Lifts while the skull race shows (dashed).",
    "sky_temple": "The temples' countdown neutral on red's side; the temples themselves at THE GAP.",
    "tomb_of_the_spider_queen": "The Webweavers banner and the egg timer at THE GAP; the Webweaver lane hexagons either side of the minimap.",
    "towers_of_doom": "The tallest stacks. Blue: tunnels, cannons, a town taken. Red: the altar, the towers upgrading, cannons, a town taken.",
    "volskaya_foundry": "The capture point's hexagon and its toast at THE GAP; the robot as a team banner on either side.",
    "warhead_junction": "The warheads' countdown neutral on red's side, then how many are left; the nuke counters by the minimap.",
}


def drawn_box(key):
    """The drawn map on `key` (its art fitted to maps.DRAWN_PX), px: (x, y, w, h). A map that
    moves the minimap has its box's bottom on the padding line, nudged; the rest share the
    square's place ([minimap] bottom), centred in it."""
    m = maps.MAPS[key]
    aw, ah = m.art
    k = min(maps.DRAWN_PX / aw, maps.DRAWN_PX / ah)
    w, h = aw * k, ah * k
    bottom = (LINE + CFG["minimap"].get("nudge", {}).get(key, 0) if m.place or m.own_place
              else CFG["minimap"]["bottom"] - SQ / 2 + h / 2)
    return CFG["minimap"]["centre_x"] - w / 2, bottom - h, w, h


def banner_boxes(key):
    """Each banner on `key` as the banner standard places it, px: (team, x, top, w, h, bar, alert):
    its bar's bottom [map_alerts] above_core over the core bar's top, one step up per alert
    below it; red's from red's row's inner edge, blue's ending at blue's."""
    out = []
    for cols in maps.MAPS[key].team.values():
        for team, col in cols.items():
            bar0 = R[f"{team}_core"][1] - CFG["map_alerts"]["above_core"]
            for i, a in enumerate(col):
                art = maps.ALERT_ART[a.kind]
                w, bar = (art.reach - art.tail) * PX, bar0 - i * maps.step() * PX
                top = bar - (art.height - art.below) * PX
                x = ROW["red_left"] if team == "red" else ROW["blue_right"] - w
                out.append((team, x, top, w, bar + art.below * PX - top, bar, a))
    return out


def gap_labels(key):
    m = maps.MAPS[key]
    parts = [AT_GAP[p.split("/")[-1].split(":")[0]] for p in m.gap_parts]
    return (AT_GAP.get(key, ["the objective"]) if m.above else []) + parts


def svg_text(x, y, t, fs, fill, anchor="middle", weight=600):
    return (f'<text x="{f1(x)}" y="{f1(y)}" text-anchor="{anchor}" dominant-baseline="central" fill="{fill}" '
            f'font-family="Barlow, sans-serif" font-weight="{weight}" font-size="{f1(fs)}">{t}</text>')


def hexagon_at(cx, bottom, w=64, h=56):
    return [(cx - w / 2, bottom - h / 2), (cx - w / 4, bottom - h), (cx + w / 4, bottom - h),
            (cx + w / 2, bottom - h / 2), (cx + w / 4, bottom), (cx - w / 4, bottom)]


def map_scene(key, scale, standard=False, crop=MAP_CROP):
    """One map's bottom of the screen (MAP_CROP) at `scale`, as an svg. standard: the banner
    standard on its own, every slot outlined, on a stand-in map (`key`'s)."""
    cx0, cy0, cw, ch = crop
    fs = lambda v: v / scale                           # screen px wanted -> viewBox units
    sw = fs(1.5)
    p = [f'<svg width="{round(cw * scale)}" height="{round(ch * scale)}" viewBox="{cx0} {cy0} {cw} {ch}" style="display: block; background: #0b0c14; border-radius: 6px;" aria-label="{maps.MAPS[key].title}: minimap and banners">',
         f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" fill="#0f111b"></rect>']
    # the plates, their XP and core bars
    for s in gen.BLUE_SLOTS + gen.RED_SLOTS:
        team = "blue" if s in gen.BLUE_SLOTS else "red"
        x, y, w, h = R[f"hero_{s}"]
        p.append(f'<polygon points="{pts(slanted(team, x, y, x + w, y + h))}" fill="{COL[team]["portrait"]}" fill-opacity=".6" stroke="{COL[team]["line"]}" stroke-opacity=".45" stroke-width="{f1(sw)}"></polygon>')
    for team in ("blue", "red"):
        for bar, fill in (("xp", XP_FILL), ("core", CORE[team])):
            x, y, w, h = R[f"{team}_{bar}"]
            p.append(f'<polygon points="{pts(slanted(team, x, y, x + w, y + h))}" fill="{fill}" fill-opacity=".55"></polygon>')
    # the minimap's square and the drawn map
    m = maps.MAPS[key]
    x, y, w, h = drawn_box(key)
    mid = y + h / 2
    p.append(f'<rect x="{f1(CFG["minimap"]["centre_x"] + m.across - SQ / 2)}" y="{f1(mid - SQ / 2)}" width="{f1(SQ)}" height="{f1(SQ)}" fill="none" stroke="#FAF9F5" stroke-opacity=".22" stroke-width="{f1(sw)}" stroke-dasharray="{f1(fs(5))} {f1(fs(4))}"></rect>')
    if m.launch_cut is not None:                       # at load: its top part on the padding line
        ly = LINE + CFG["minimap"].get("launch_nudge", {}).get(key, 0) - m.launch_cut - h / 2
        p.append(f'<rect x="{f1(x)}" y="{f1(ly)}" width="{f1(w)}" height="{f1(h)}" fill="none" stroke="{MAP_C}" stroke-opacity=".6" stroke-width="{f1(sw)}" stroke-dasharray="{f1(fs(6))} {f1(fs(4))}"></rect>')
        p.append(svg_text(x + w + fs(6), min(ly + h, cy0 + ch) - fs(30), "at load", fs(11), MAP_C, "start"))
    lift = CFG["minimap"].get("lift", {}).get(key)
    if lift:
        p.append(f'<rect x="{f1(x)}" y="{f1(y - lift)}" width="{f1(w)}" height="{f1(h)}" fill="none" stroke="{MAP_C}" stroke-opacity=".6" stroke-width="{f1(sw)}" stroke-dasharray="{f1(fs(6))} {f1(fs(4))}"></rect>')
        p.append(svg_text(x + w + fs(6), y - lift + fs(10), f"lifted {lift} px", fs(11), MAP_C, "start"))
    p.append(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" rx="{f1(fs(3))}" fill="{MAP_C}" fill-opacity=".14" stroke="{MAP_C}" stroke-width="{f1(sw)}"></rect>')
    p.append(svg_text(x + w / 2, mid, "the map" if standard else f"{f1(round(w))} × {f1(round(h))}", fs(12), "#A8EBEB"))
    # THE FLOOR, and THE GAP over the map's top
    floor = CFG["minimap"]["floor"]
    p.append(f'<line x1="{cx0}" y1="{floor}" x2="{cx0 + cw}" y2="{floor}" stroke="{FLOOR_C}" stroke-opacity=".7" stroke-width="{f1(sw)}" stroke-dasharray="{f1(fs(8))} {f1(fs(5))}"></line>')
    gap = CFG["minimap"]["alert_gap"]
    labels = ["a neutral objective"] if standard else gap_labels(key)
    for i, label in enumerate(labels):
        hx = CFG["minimap"]["centre_x"] + (i - (len(labels) - 1) / 2) * 150
        p.append(f'<polygon points="{pts(hexagon_at(hx, y - gap))}" fill="{NEUTRAL}" fill-opacity=".3" stroke="{NEUTRAL}" stroke-width="{f1(sw)}"></polygon>')
        p.append(svg_text(hx, y - gap - 56 - fs(9), label, fs(11), "#CFC7FF"))
    # the banners
    bars = set()
    boxes = banner_boxes(key)
    if standard:                                       # every slot, in the Towers-style art
        art = maps.ALERT_ART[""]
        boxes = []
        for team in ("blue", "red"):
            bar0 = R[f"{team}_core"][1] - CFG["map_alerts"]["above_core"]
            for i in range(maps.max_stack()):
                w_, bar = (art.reach - art.tail) * PX, bar0 - i * maps.step() * PX
                top = bar - (art.height - art.below) * PX
                bx = ROW["red_left"] if team == "red" else ROW["blue_right"] - w_
                boxes.append((team, bx, top, w_, bar + art.below * PX - top, bar, f"slot {i + 1}"))
    for team, bx, top, bw, bh, bar, a in boxes:
        if standard:
            colour, label, then = COL[team]["pop"], a, ""
        else:
            colour = NEUTRAL if "(neutral)" in a.note else COL[team]["pop"]
            label = BANNER.get(a.name) or re.split(r",|;| \(", a.note)[0]
            then = a.note.split(", then ")[1].replace(" (neutral)", "") if ", then " in a.note else ""
        p.append(f'<rect x="{f1(bx)}" y="{f1(top)}" width="{f1(bw)}" height="{f1(bh)}" rx="{f1(fs(3))}" fill="{colour}" fill-opacity=".2" stroke="{colour}" stroke-width="{f1(sw)}"></rect>')
        p.append(f'<line x1="{f1(bx)}" y1="{f1(bar)}" x2="{f1(bx + bw)}" y2="{f1(bar)}" stroke="{colour}" stroke-width="{f1(fs(3))}"></line>')
        p.append(svg_text(bx + bw / 2, top + bh / 2 - (fs(7) if then else 0), label, fs(12), "#FAF9F5"))
        if then:
            p.append(svg_text(bx + bw / 2, top + bh / 2 + fs(8), "then " + then, fs(10), "#C9CAD6", weight=500))
        bars.add(round(bar, 1))
    if standard:                                       # the numbers
        bar0 = R["red_core"][1] - CFG["map_alerts"]["above_core"]
        p.append(dim_v(ROW["red_left"] + 480, bar0, R["red_core"][1], f'{CFG["map_alerts"]["above_core"]} px over the core bar'))
        p.append(dim_v(ROW["red_left"] + 470, bar0 - maps.step() * PX, bar0, f"step {f1(round(maps.step() * PX, 1))} px"))
        for ex, label, anchor in ((ROW["blue_right"], f"blue's end at x {ROW['blue_right']}", "end"), (ROW["red_left"], f"red's start at x {ROW['red_left']}", "start")):
            p.append(f'<line x1="{ex}" y1="{cy0}" x2="{ex}" y2="{cy0 + ch}" stroke="#FAF9F5" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="6 5"></line>')
            p.append(svg_text(ex + (-8 if anchor == "end" else 8), cy0 + 16, label, 14, "#FAF9F5", anchor))
        p.append(dim_v(CFG["minimap"]["centre_x"] + 70, y - gap, y, f"THE GAP {gap} px"))
        p.append(svg_text(cx0 + 12, floor - 12, f"THE FLOOR y {floor}: every map's visual bottom", 14, FLOOR_C, "start"))
    p.append('</svg>')
    return "".join(p)


def place_note(key):
    """How `key`'s minimap is placed, from maps.py and layout.toml."""
    m = maps.MAPS[key]
    n = CFG["minimap"].get("nudge", {}).get(key, 0)
    how = ("its own place, by map id" if m.own_place else "moved by its panel" if m.place
           else f"the shared place ([minimap] bottom {CFG['minimap']['bottom']})")
    bits = [how + (f", {n:+} px" if n else "")]
    if m.across:
        bits.append(f"its art {m.across} px off its square's centre, put back")
    pn = gen.panel_nudges(CFG).get(key, 0)
    if pn and not m.above:
        bits.append(f"its panel {pn:+} px")
    return "; ".join(bits)


def maps_board():
    scale, cols, gutter = 0.4, 4, 36
    cw, ch = round(MAP_CROP[2] * scale), round(MAP_CROP[3] * scale)
    w = 96 + cols * cw + (cols - 1) * gutter
    b = [header("Maps · as built",
                f"Every battleground's minimap and banners, drawn from tools/maps.py and layout.toml (build {STAMP}). The bottom of the screen, "
                f"x {MAP_CROP[0]}–{MAP_CROP[0] + MAP_CROP[2]}, y {MAP_CROP[1]}–1080. The drawn map is its texture's opaque box as the engine fits it, "
                "so THE GAP is shown to the box's top; in game it's measured to the art's top tip.", w - 96)]
    legend = [(COL["blue"]["pop"], "blue's banner"), (COL["red"]["pop"], "red's banner"), (NEUTRAL, "neutral: on red's side, or at THE GAP"),
              (MAP_C, "the drawn map (dashed: lifted, or at load)"), (FLOOR_C, "THE FLOOR")]
    b.append('<div style="position: absolute; left: 48px; top: 150px; display: flex; gap: 22px; font-size: 14px; color: #C9CAD6;">'
             + "".join(f'<span style="display: flex; align-items: center; gap: 8px;"><span style="width: 22px; height: 12px; border-radius: 2px; '
                       f'border: 2px solid {c}; background: {c}33;"></span>{t}</span>' for c, t in legend) + '</div>\n')
    # the standard, at 3/4
    sk = 0.75
    sy = 250
    b.append(heading(48, 200, "The banner standard", "The same on every map (user, 2026-10-09 and 2026-10-14). Towers of Doom's art in every slot.", 1400))
    b.append(f'<div style="position: absolute; left: 48px; top: {sy + 20}px;">' + map_scene("cursed_hollow", sk, standard=True, crop=STANDARD_CROP) + '</div>\n')
    nx = 48 + round(STANDARD_CROP[2] * sk) + 48
    items = [("Bars, not boxes", f"Every banner is placed by its bar: the bar's bottom {CFG['map_alerts']['above_core']} px over the core bar's top, in one place on every map, "
                                 "whether the core bar shows or not. What hangs under a bar is ignored: the banners draw over the plates' pop-ups."),
             ("Across", f"Red's banners start where red's row does (x {ROW['red_left']}); blue's end where blue's does (x {ROW['blue_right']}): "
                        "the same distance from the minimap as the plates."),
             ("Stacking", f"One step up per banner below: the tallest art that ever stacks plus {maps.STACK_GAP} units, "
                          f"{f1(round(maps.step() * PX, 1))} px. Up to {maps.max_stack()} (Towers of Doom's red). A banner alone in its column never stacks."),
             ("Neutral", "A banner that is no team's goes in red's column; red shares its side with them. A neutral objective that sits above the minimap "
                         f"goes to THE GAP: its hexagon's bottom {CFG['minimap']['alert_gap']} px over the drawn map's top tip, on every map."),
             ("THE FLOOR", f"Each map's visual bottom (its outline, not its box) at y {CFG['minimap']['floor']}: [minimap.nudge] per map.")]
    y = sy + 20
    for t, d in items:
        b.append(note(nx, y, w - nx - 48, t, d))
        y += 96
    # every map
    gy = sy + 20 + round(STANDARD_CROP[3] * sk) + 70
    b.append(heading(48, gy, "Every battleground", "Each banner labelled from its note in tools/maps.py; \"then\" is what the same spot shows next."))
    y0 = gy + 70
    pitch = ch + 190
    for i, (key, m) in enumerate(maps.MAPS.items()):
        x = 48 + (i % cols) * (cw + gutter)
        y = y0 + (i // cols) * pitch
        b.append(f'<div class="t" style="position: absolute; left: {x}px; top: {y}px; font-size: 20px; color: #F2C94C;">{m.title}</div>\n')
        b.append(f'<div style="position: absolute; left: {x}px; top: {y + 32}px;">' + map_scene(key, scale) + '</div>\n')
        b.append(f'<div class="s" style="position: absolute; left: {x}px; top: {y + 42 + ch}px; width: {cw}px; font-size: 14px; color: #C9CAD6;">'
                 f'<div style="color: #A8EBEB; margin-bottom: 4px;">Minimap: {place_note(key)}.</div>{MAP_NOTES[key]}</div>\n')
    h = y0 + -(-len(maps.MAPS) // cols) * pitch
    return page("Maps, as built", w, h, "".join(b)), (w, h)


# ================================================================= write
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = {}
    (OUT / "Main.dc.html").write_text(main_board(), encoding="utf-8")
    for name, fn in (("Plate.dc.html", plate_board), ("Panes.dc.html", panes_board), ("Inspect.dc.html", inspect_board),
                     ("TopBar.dc.html", topbar_board), ("Maps.dc.html", maps_board), ("Visual.dc.html", visual_board),
                     ("Spec.dc.html", spec_board)):
        html, size = fn()
        (OUT / name).write_text(html, encoding="utf-8")
        sizes[name] = size
    (OUT.parent / "sizes.json").write_text(json.dumps(sizes), encoding="utf-8")   # board sizes, for canvas.json
    print("wrote", ", ".join(["Main.dc.html"] + list(sizes)), "·", STAMP)
    print(json.dumps(sizes))


if __name__ == "__main__":
    main()
