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
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import gen                   # noqa: E402
import inspect_card as ic    # noqa: E402

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
        third = (hr - hl - narrow - 2 * gen.VIKING_GAP) / 3
        for slot, frac in enumerate(st["vikings"]):
            vl = hl + narrow + slot * (third + gen.VIKING_GAP)
            out.append(rect((vl, ht, vl + third, hb), HP[team], frac))
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


def hexagon_svg():
    """Blizzard's hexagon (TopBarLogoOverlay), from the measured [top_backplate] hexagon."""
    h = [tuple(p) for p in BP["hexagon"]]
    cx = sum(x for x, _ in h) / 6
    cy = sum(y for _, y in h) / 6
    inner = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.86) for x, y in h]
    return (f'<polygon points="{pts(h)}" fill="#1a1740" stroke="#6b5fd6" stroke-width="4"></polygon>'
            f'<polygon points="{pts(inner)}" fill="none" stroke="#a79bff" stroke-opacity=".5" stroke-width="1.5"></polygon>'
            f'<ellipse cx="{round(cx, 1)}" cy="{round(cy, 1)}" rx="34" ry="31" fill="rgba(242,166,90,.12)" stroke="#F2A65A" stroke-width="2.5" stroke-dasharray="7 5"></ellipse>'
            f'<text x="{round(cx, 1)}" y="{round(cy + 4, 1)}" text-anchor="middle" fill="#F7C08A" font-family="Barlow Condensed, sans-serif" font-weight="600" font-size="13" letter-spacing="1">LOGO · OBS</text>')


def top_bar(levels=("12", "9")):
    """The top bar as built: our backplate texture, Blizzard's hexagon, level numbers and clock,
    and the OBS areas."""
    b = []
    for key in ("blue_score", "red_score"):
        b.append(at(key, "ob t", '<span style="font-size: 12px;">Score</span>', CENTRE))
    for key in ("blue_name", "red_name"):
        b.append(at(key, "ob t", '<span style="font-size: 14px;">Team name · OBS</span>', CENTRE))
    for key in ("blue_logo", "red_logo"):
        b.append(at(key, "ob t", '<span style="font-size: 12px;">Logo</span>', CENTRE))
    for key in ("blue_bans", "red_bans"):
        b.append(at(key, "ob t", '<span style="font-size: 12px;">Bans</span>', CENTRE))
    b.append(at("bracket", "ob t", '<span style="font-size: 12px;">Bracket · OBS</span>', CENTRE))
    b.append(at("game_count", "ob t", '<span style="font-size: 12px;">Game 1 of 5 · OBS</span>', CENTRE))
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
                f'<div class="s">Replays only · {R["replay"][2]} × {R["replay"][3]} · Ctrl+Shift+O collapses it to a tab</div>',
                "padding: 12px; display: flex; flex-direction: column; justify-content: space-between;"))
    b.append(top_bar())
    b.append(at("centre_banners", "faint t", "Blizzard centre banners · untouched", CENTRE))
    b.append("".join(kill_row(y, k, v) for y, k, v in ((122, "red", "blue"), (188, "blue", "red"), (254, "blue", "red"))))
    kx, _, kw, _ = R["kill_feed"]
    b.append(f'<div class="chip s" style="left: {kx + 24}px; top: 322px; width: 264px;">Kill feed · Blizzard\'s, in its own place</div>\n')
    b.append(f'<div style="position: absolute; left: {PANE_X}px; top: {PANE_Y}px;">' + stats_pane("kda") + '</div>\n')
    ix, iy, iw, ih = R["inspect"]
    b.append(f'<div class="dem" style="left: {ix}px; top: {iy}px; width: {iw}px; height: {ih}px; background: transparent;"></div>\n')
    b.append(f'<div class="chip s" style="left: {PANE_X + PANE_W + 12}px; top: {PANE_Y + 90}px; width: 270px;">Info pane · {PANE_W} × {PANE_H} · Ctrl+1 talents, 2 KDA, 3 healing, 4 structures (KDA shown)</div>\n')
    b.append(f'<div class="chip s" style="left: {ix + iw + 12}px; top: {iy + ih - 120}px; width: 300px; border: 1px solid #6FD3D3;">Teal: the inspect card, {iw} × {ih}, while a unit is selected (same left column; bottom at y {iy + ih})</div>\n')
    b.append(at("map_objectives", "dem", '<div class="t" style="font-size: 14px;">Map objective widgets · not started</div>', CENTRE))
    mm = CFG["minimap"]
    sq = gen.MINIMAP_SQUARE * PX
    b.append(f'<div class="faint" style="left: {f1(mm["centre_x"] - sq / 2)}px; top: {f1(mm["bottom"] - sq)}px; width: {f1(sq)}px; height: {f1(sq)}px; border-color: rgba(250,249,245,.25);"></div>\n')
    b.append(at("minimap", "ui", '<div class="t" style="font-size: 26px;">Minimap</div><div class="s">the engine fits each map in its square</div>',
                "display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;"))
    b.append(hero_rows_svg() + '\n')
    bx, by = CFG["dev"]["build_stamp"]
    b.append(f'<div class="chip s" style="left: {bx + 320}px; top: {by - 150}px; padding: 3px 8px;">FCJH DEV build stamp at {bx}, {by} (dev only)</div>\n')
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
                     f"Lost Vikings: three bars in thirds, {gen.VIKING_GAP} units apart (Baleog, Erik, Olaf), each with its own death timer. "
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
    lx, ly, lw, _ = R["blue_logo"]
    gap = round(geo["ends"][0] + LEAN * ly - (lx + lw), 1)       # the wing's slanted end at the logo's top
    return (f"Blue, outside in: score {r('blue_score')}, name {r('blue_name')}, logo {r('blue_logo')} ({gap} px clear of the wing). "
            f"The top row is the wings' height. Second row: bans under the name, {r('blue_bans')}; bracket {r('bracket')} and game count "
            f"{r('game_count')} under the wings, each as wide as its wing's bottom edge. Red mirrors blue about x 960.")


def topbar_board():
    w = 1920
    geo = gen.top_backplate_geometry(CFG)
    b = [header("Top bar · as built",
                f"Our backplate (variant C: silver chrome rim; team colour strongest at the wings' outer ends, fading to a stock dark toward the hexagon; "
                f"a hexagon lattice fading the same way). It becomes the basis of the rest of the UI in the visual pass. One {gen.TOP_BACKPLATE_SIZE[0]} × "
                f"{gen.TOP_BACKPLATE_SIZE[1]} texture drawn 1:1 at x {R['top_backplate'][0]}, from layout.toml [top_backplate]. Build {STAMP}.", 1820)]
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
             ("Orange dashes · OBS areas", "Left empty for OBS. " + obs_areas()),
             ("Rim and pattern", f"Chrome {', '.join('#' + c for c in BP['rim'])}, {BP['rim_width']} px; sheen {BP['sheen']}; hexagons {BP['hex_px']} px across at {BP['lattice']} strength.")]
    y = zy
    for t, d in items:
        b.append(note(nx, y, w - nx - 48, t, d))
        y += 128
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
    w, h = 1100, 1460
    blue_r = R["hero_5"][0] + R["hero_5"][2]
    red_r = R["hero_0"][0] + R["hero_0"][2]
    tp, hp = CFG["talent_popup"], CFG["heal_popup"]
    xs = lambda k: f"{f1(R[k][2])} × {f1(R[k][3])}"
    rows = [
        ("Hero plates × 10", f"{px_(CELL.w)} × {px_(CELL.h)} (scale {ROW['scale']:g}), blue x {f1(ROW['blue_left'])}–{f1(blue_r)}, red x {ROW['red_left']}–{f1(red_r)}, y {f1(ROW['top'])}–{ROW['bottom']}", "built",
         "Blizzard's in-game cell art, portrait masked to the slant, click selects the hero and clamps the camera. Seen at 1.375; this +10% not yet"),
        ("Health + resource", "Each plate; narrowed while the heroic shows", "game", "Blizzard's fill art. Resource colour per hero"),
        ("Heroic panel", "The plate's inner end: blue bottom right, red bottom left", "built", "Blizzard's panel mirrored: icon, gold frame, ready glow, cooldown dim + count, tooltip (the talent icon's own), Tracer's charge meter"),
        ("CC icon + text", f"Icon {px_(2 * CELL.cc_half)} px in the portrait; text on the health bar", "game", "Text fits the bar's width (UNSTOPPABLE fits)"),
        ("Death timers", "Plate centre", "game", "Per-Viking timers too; Misha's removed"),
        ("Special plates", "Vikings, Rexxar, Abathur", "game", "Vikings in thirds (Baleog, Erik, Olaf); Rexxar full-height bar; Abathur's clone icon + CLONE"),
        ("Fountain", "On the health bar at the plate's outer end", "built", "Bright when ready, dimmed with its count on cooldown"),
        ("Talent pop-ups", f"{ROW['talent_popup_size']} px, straddling the top edge", "game", f"Hold {tp['hold']} s, fade {tp['fade']} s; always play out; drawn over heal. Seen at 40 px"),
        ("Heal pop-up", f"Same spot and motion; at {hp['threshold']}% or less", "game", f"Hold {hp['hold']} s; clears above {hp['clear_above']}%; fades at once on death; {hp['lock']:g} s lock per plate"),
        ("Team XP", f"{xs('blue_xp')}, y {f1(R['blue_xp'][1])}, on the plates' top edge", "game", "Cut to the slant; hidden before the game starts. Moves with the plates"),
        ("Core HP", f"{xs('blue_core')}, y {f1(R['blue_core'][1])}, on XP at the inner end", "built", "Blizzard's bar and size, our slanted track and mask. Check in Towers of Doom; restyle from the reference"),
        ("Top bar backplate", f"{gen.TOP_BACKPLATE_SIZE[0]} × {gen.TOP_BACKPLATE_SIZE[1]} texture at x {R['top_backplate'][0]}", "game", "Variant C, chrome. The look the rest of the UI follows"),
        ("Team levels + flame", f"{xs('blue_level')} at x {R['blue_level'][0]} / {R['red_level'][0]}", "game", "Blizzard's numbers; the talent-lead flame works"),
        ("Hexagon, clock", "Blizzard's places", "game", "Towers and kills removed"),
        ("Names, logos, scores, bans, bracket", "Top bar", "obs", "Left empty for OBS; no name plate drawn yet"),
        ("Kill feed", "Blizzard's own, top-left", "game", "Not moved: its rows grow rightward, so multi-kills ran off a right-hand feed"),
        ("Replay controls", f"{R['replay'][0]}, {R['replay'][1]} · {xs('replay')}", "game", "Ctrl+Shift+O collapses to a tab"),
        ("Info panes", f"{PANE_X}, {PANE_Y} · {PANE_W} × {PANE_H}", "game", "Ctrl+1-4: talents, KDA + hero dmg, healing, structures + XP. One at a time"),
        ("Inspect card", f"{R['inspect'][0]}, {R['inspect'][1]} · {xs('inspect')}", "game", "Follows Blizzard's inspector: shows on selecting a unit, not on plate clicks; clicks inside stay. Anything not a hero gets a short card"),
        ("Blizzard's small inspector", "Parked off screen", "game", "Never shows; its visibility drives our card"),
        ("Minimap", f"Bottom-centre, {xs('minimap')}", "game", "The engine fits each map in its square"),
        ("Map objectives", "Over the minimap", "unk", "Per map; not started"),
        ("Player HUD", "Hidden", "game", "Ctrl+5 is Blizzard's observe-player key"),
    ]
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


# ================================================================= write
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = {}
    (OUT / "Main.dc.html").write_text(main_board(), encoding="utf-8")
    for name, fn in (("Plate.dc.html", plate_board), ("Panes.dc.html", panes_board), ("Inspect.dc.html", inspect_board),
                     ("TopBar.dc.html", topbar_board), ("Visual.dc.html", visual_board), ("Spec.dc.html", spec_board)):
        html, size = fn()
        (OUT / name).write_text(html, encoding="utf-8")
        sizes[name] = size
    (OUT.parent / "sizes.json").write_text(json.dumps(sizes), encoding="utf-8")   # board sizes, for canvas.json
    print("wrote", ", ".join(["Main.dc.html"] + list(sizes)), "·", STAMP)
    print(json.dumps(sizes))


if __name__ == "__main__":
    main()
