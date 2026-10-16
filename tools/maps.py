"""Each battleground's own UI on our screen (user, 2026-10-05/06): where the minimap sits on that
map, the map's objective panel pinned to our minimap the way Blizzard pins it to theirs, and the
alerts that belong to a team stacked beside the minimap on that team's side. Written by
tools/gen.py into FCJH_Maps.StormLayout (maps.layout). Its numbers are constants: the minimap's
place per map FCJH_MINIMAP_BOTTOM_<MAP> ([minimap] in layout.toml), the stacks' FCJH_MAP_ALERT_*
([map_alerts]); gen.py constants_layout works both out from what's here.

How a map's UI works (from the game files, 2026-10-06):
  - each map's panel is a template built at runtime inside GameUI's MapMechanicPanel. The newer
    maps keep it in the map's own layout file, created by the map's script; the older five
    (Cursed Hollow, Blackheart's Bay, Haunted Mines, Garden of Terror, Dragon Shire) use panels
    in Blizzard's core MapMechanicPanelTemplate, there on every map, hidden at load and shown
    by the map's script. The script finds every part by NAME: we may move and restyle a part
    (file="<the map's file>"), never rename or drop one.
  - the panels are drawn for Blizzard's minimap in the screen's bottom-right corner: most are
    pinned to that corner, some are strips down the right edge (which clip what they hold), a
    few parts are placed from the minimap itself. Ours is bottom-centre. So each panel is
    restated from our minimap's bottom-right corner, as it stood from Blizzard's on that map
    (on_minimap) - everything in it keeps its place round the minimap.
  - a map's layout file is loaded only on that map, so its panel exists only there - shown or
    hidden by its script: that is how a map moves the minimap, as soon as the panel exists
    (placer; waiting for the panel to SHOW made the minimap jump, user 2026-10-09). Blizzard moves its own
    minimap per map with a MinimapPanel override in the map's file, which may load after ours -
    the SetAnchors win either way.
"""
import hashlib
import math
from dataclasses import dataclass, field
from itertools import combinations

T = "\t"

SCREEN_H = 1200          # layout units: the game's screen is always this tall
SCREEN_W = 2134          # ...and this wide at 16:9, rounded up: only for the left edge of
                         # Hanamura's screen-sized panels, which nothing in them is placed from
CONSOLE = "$GameUI/UIContainer/ConsoleUIContainer"
MINIMAP = CONSOLE + "/MinimapPanel"
MECHANICS = CONSOLE + "/MapMechanicPanel"

# How wide a map draws in the minimap square, px at 1080p. The engine fits the opaque part of a
# map's CustomMiniMap texture into the square, centred: Towers of Doom draws ~380 x 252 px, at
# y 810-1062 (measured in game, 2026-10-05) - its art 436 x 298 texels, so ~380 x 260.
DRAWN_PX = 380

@dataclass
class Art:
    """A banner's art, as the banner standard places it (user, 2026-10-09): every banner on every
    map lands alike - Blizzard's banners are one bar art - so each is placed by its BAR. Units.
    reach / tail: across, from the edge the frame is placed by - how far the art reaches back
    (red's bar starts there: at red's plates' inner edge) and how far short of it the art stops
    (blue's bar ends at blue's inner edge). bar_up: the bar's bottom above the edge the frame is
    placed by (0 when placed by the bar's bottom). Every bar's bottom sits in ONE place on every
    map, [map_alerts] above_core px over the core bar's top, never moving (user, 2026-10-09):
    what hangs under a bar (below: the tribute's hexagon and beak) is ignored - the banners
    draw over the plates' pop-ups. height: from the art's lowest part to its top; the tallest
    sets the stack's step (step). measured: off a 1080p screenshot - the build lists any that
    aren't (gen.py)."""
    reach: int
    tail: int = 0
    bar_up: int = 0
    below: int = 0            # not placement: the bar's place ignores what hangs under it
    height: int = None
    measured: bool = True
    note: str = ""


# "": Blizzard's NotificationFrameTemplate alert (Towers of Doom's three kinds), placed by its
# frame's right edge: reaches 500 units left, stops 12 short (measured 2026-10-06; the
# templates' arithmetic gave 388); 117 tall (Blizzard's stacked step, 147, less its 30-unit
# gap). Its bar's bottom sits 20 above its frame's, its hexagon hanging 14 under the bar
# (measured 2026-10-09 at 1080p: the bar 18 px above the tribute's baseline when placed level).
# "BANNER" and "HOLDOUT": the older maps' centre banners, placed by a spot of ours the size of
# the art (Alert.box) - set with their boxes, below.
ALERT_ART = {
    "": Art(499, 12, bar_up=20, below=14, height=117),   # reach 500 put its tip 1 px past red's plates
}
STACK_GAP = 8             # units between two stacked banners: Blizzard's 30, less 22 (20 px - user, 2026-10-09: too much dead space)


def step():
    """Units between two stacked banners' bars: the tallest art that can stack - one in a column
    with others, on any map - and the gap. A banner alone in its column never stacks (the
    tribute, with the curse's raven head: sizing the step for it spread Towers' pair too far,
    user 2026-10-09)."""
    stacking = {a.kind for m in MAPS.values() for cols in m.team.values() for col in cols.values()
                if len(col) > 1 for a in col}
    return max(ALERT_ART[k].height for k in stacking) + STACK_GAP


def unmeasured():
    return {k or "(Towers-style)": a.note for k, a in ALERT_ART.items() if not a.measured}


@dataclass
class Alert:
    """One of a team's alerts, in its stack beside the minimap. `place`: the child that carries
    the alert's position too, when its art hangs off that rather than the frame (Hanamura's icon
    box); `box`: for a frame whose art hangs off its TOP-right corner (it fills its panel, the
    art pinned near the top): the art's edges from that corner, units (left, top, right,
    bottom) - a spot of ours that size takes the slot and the frame hangs off it; `kind`: its
    art (ALERT_ART, the banner standard); `template`: for alerts of our own (FCJH_ prefix); `extra`: XML inside the
    frame, after its stack.
    Neutral alerts (no team's) go in red's column: red shares its side with them (user,
    2026-10-06 - centred above the map they sat too high, worse on a tall map)."""
    name: str
    kind: str = ""
    place: str = None                 # "Name:Type"
    box: tuple = None                 # (left, top, right, bottom) from the frame's top-right
    followers: tuple = ()             # with a box: (frame, up, xml) - frames whose art hangs off
                                      # this one's, their box reaching `up` units higher; xml inside
    spot_only: bool = False           # with a box: only the spot - another alert's frame moves
                                      # onto it (Cursed Hollow's curse on blue: cursed_side)
    template: str = None
    extra: str = ""
    note: str = ""


@dataclass
class Map:
    title: str
    art: tuple                        # texels: the opaque part of its CustomMiniMap texture
    file: str = None                  # its own layout file, if it has one
    core: str = None                  # its panel in Blizzard's MapMechanicPanelTemplate, if that
    minimap: tuple = (35, 0)          # Blizzard's MinimapPanel on this map: bottom, right (units
                                      # from the screen's, + down/right). 35, 0 unless its file says
    panels: dict = field(default_factory=dict)   # "Path/In/File:Type" -> Blizzard's anchors on the
                                      # screen: ((side, pos, offset), ...)
    place: tuple = ()                 # its panels: the first, existing, places the minimap (core_panels)
    own_place: bool = False           # an older map with its own minimap place, by its map id
                                      # (MAP_IDS, id_placers); without, it shares [minimap] bottom
    launch_cut: int = None            # own_place, opening on its top part only: that part's bottom,
                                      # px at 1080p below the drawn map's middle (measured) - on the
                                      # padding line at load ([minimap.launch_nudge])
    opens: str = None                 # ...until this (under MapMechanicPanel) first shows: then the
                                      # minimap glides to its place, for good (id_placers)
    lifts: str = None                 # a part of its own panel: while it shows, the minimap glides
                                      # [minimap.lift] px up, and back down when it hides; the part
                                      # stays put, where the lifted map hung it (lift)
    fix: str = ""                     # extra SetAnchors when this map's minimap is placed
    team: dict = field(default_factory=dict)     # {"blue": [Alert...], "red": [...]}: panel -> column
    extra: str = ""                   # map-specific XML in its file's panel (see TOWERS_EXTRA)
    above: tuple = None               # its neutral objective above the minimap, for THE GAP
                                      # ([minimap] alert_gap): (px, at) - measured at 1080p, its
                                      # hexagon's bottom `px` over the drawn map's top tip (the art's
                                      # outline) with its panels `at` px lower. gen.py moves its
                                      # panels to the gap (panel_nudges); it rides on the minimap
    gap_parts: dict = field(default_factory=dict)  # {part: (px, at)}: as `above`, but only that part
                                      # (anchored all round to its panel) goes to the gap, its
                                      # panel kept to its [minimap.panel_nudge]; `at`, px, is the
                                      # panel's nudge plus the part's own move when measured.
                                      # (px, at, (relative, pos, offset)): a part hung by its
                                      # Bottom off the minimap (Blizzard's anchor), not its panel
    across: int = 0                   # px right: its map's art is drawn off its square's centre
                                      # (measured at 1080p); its minimap goes this far right to
                                      # put the art on centre, its panels taken back (on_minimap)
    proxy: bool = False               # its file's panels' MinimapProxyFrame tied to our minimap
                                      # by its full path (proxy_lines)
    notes: str = ""


# ------------------------------------------------------------------ Towers of Doom's own alerts

TOWN_SPLITS = 7          # the towns each side holds: 0v6 .. 6v0

def town_alert(team, template, text):
    return Alert(f"FCJH_{team.capitalize()}Town", template=template, extra=(
        f'{T*3}<Frame type="Label" name="NotificationLabel"><Text val="{text}"/></Frame>\n'
        f'{T*3}<Frame type="Label" name="NotificationTargetLabel"><Text val="a town"/></Frame>\n'
        f'{T*3}<!-- gone after 5 s, as Blizzard\'s (its script waits 5 s, then hides it) -->\n'
        + timer(3)),
        note="ours, which team took a town (towers_extra)")


def timer(indent, seconds=5):
    t = T * indent
    return (f'{t}<Animation name="FCJH_Timer">\n'
            f'{t}\t<Event event="Show" action="Restart,Play"/>\n'
            f'{t}\t<Controller type="Event" end="Stop">\n'
            f'{t}\t\t<Key type="Event" time="{seconds}" event="Hide"/>\n'
            f'{t}\t</Controller>\n'
            f'{t}</Animation>\n')


CANNON_NOTE = ("gone 5 s after it shows, whoever the script's own hide reaches: switching from a\n"
               "player view to the everyone view inside those 5 s left it up for good - the hide\n"
               "goes to the team's players only (user, 2026-10-06)")


def cannons(name):
    return Alert(name, extra=f"{T*3}<!-- {CANNON_NOTE.replace(chr(10), chr(10) + T*3 + '     ')} -->\n" + timer(3),
                 note="Blizzard's, players-only (\"Your/Enemy cannons are firing\")")


def towers_extra():
    """Towers of Doom: Blizzard's town-capture pair parked; ours, from the observer-only town
    counts, stand in (their frames are in the stacks); the towns' shot counts over the screen."""
    t = T * 2
    out = [
        f'{t}<!-- Blizzard\'s town-capture pair ("Allies / The Enemy captured <town>"), viewer-relative and\n'
        f'{t}     players-only: parked above the screen - ours stand in for them in every view. -->\n',
        f'{t}<Frame type="Frame" name="EnemyCaptureNotificationFrame">\n'
        f'{t}\t<Anchor side="Bottom" relative="$GameUI" pos="Min" offset="-9999"/>\n{t}</Frame>\n',
        f'{t}<Frame type="Frame" name="AllyCaptureNotificationFrame">\n'
        f'{t}\t<Anchor side="Bottom" relative="$GameUI" pos="Min" offset="-9999"/>\n{t}</Frame>\n',
        f'{t}<!-- Which team took a town (user, 2026-10-06). Blizzard\'s town-capture alerts go only to\n'
        f'{t}     each team\'s players and name no team, so ours stand in (FCJH_BlueTown / FCJH_RedTown,\n'
        f'{t}     in the stacks above), on the capturing team\'s side, in every view. On every change\n'
        f'{t}     of hands the script sends the OBSERVER panel (our plates\' ObserverHeroOverviewPanel)\n'
        f'{t}     "BroadcastToD<blue>v<red>", the towns each team holds - Blizzard\'s own UI never uses\n'
        f'{t}     it. New<n>: the split just sent; Cur<n>: the one before, copied 0.1 s later. Blue\'s\n'
        f'{t}     count up: blue took a town; down: red did. It comes with the new town\'s spawn,\n'
        f'{t}     about a second after the old one falls. -->\n',
        f'{t}<Frame type="Frame" name="FCJH_TownWatch">\n'
        f'{t}\t<Anchor relative="$parent"/>\n'
        f'{t}\t<AcceptsMouse val="false"/>\n',
    ]
    start = TOWN_SPLITS // 2        # 3v3 at the start
    for kind in ("New", "Cur"):
        for n in range(TOWN_SPLITS):
            out.append(f'{t}\t<Frame type="Frame" name="FCJH_{kind}{n}"><Anchor relative="$parent"/>'
                       f'<Visible val="{"true" if n == start else "false"}"/><AcceptsMouse val="false"/></Frame>\n')
    flags = lambda kind, k: "".join(
        f'{t}\t\t<Controller type="Visibility" end="Pause" frame="FCJH_{kind}{n}"><Key type="Bool" time="0" '
        f'value="{"true" if n == k else "false"}"/></Controller>\n' for n in range(TOWN_SPLITS))
    for k in range(TOWN_SPLITS):
        out.append(f'{t}\t<Animation name="FCJH_Split{k}">\n'
                   f'{t}\t\t<Event event="BroadcastToD{k}v{TOWN_SPLITS - 1 - k}" action="Restart,Play" '
                   f'frame="$GameUI/UIContainer/FullscreenUpperContainer/ObserverHeroOverviewPanel"/>\n'
                   + flags("New", k)
                   + f'{t}\t\t<Controller type="Event" end="Stop">\n'
                   f'{t}\t\t\t<Key type="Event" time="0.1" event="FCJH_Sync{k}"/>\n'
                   f'{t}\t\t</Controller>\n'
                   f'{t}\t</Animation>\n'
                   f'{t}\t<Animation name="FCJH_Sync{k}">\n'
                   f'{t}\t\t<Event event="FCJH_Sync{k}" action="Restart,Play"/>\n'
                   + flags("Cur", k)
                   + f'{t}\t</Animation>\n')
    out.append(f'{t}\t<StateGroup name="FCJH_WhoTook">\n{t}\t\t<DefaultState val="Same"/>\n')
    for k in range(1, TOWN_SPLITS):
        out.append(f'{t}\t\t<State name="Blue{k}"><When type="Property" frame="$this/FCJH_Cur{k - 1}" Visible="true"/>'
                   f'<When type="Property" frame="$this/FCJH_New{k}" Visible="true"/>'
                   f'<Action type="SendEvent" frame="$parent/FCJH_BlueTown" event="Show"/></State>\n')
    for k in range(TOWN_SPLITS - 1):
        out.append(f'{t}\t\t<State name="Red{k}"><When type="Property" frame="$this/FCJH_Cur{k + 1}" Visible="true"/>'
                   f'<When type="Property" frame="$this/FCJH_New{k}" Visible="true"/>'
                   f'<Action type="SendEvent" frame="$parent/FCJH_RedTown" event="Show"/></State>\n')
    out.append(f'{t}\t\t<State name="Same"/>\n{t}\t</StateGroup>\n{t}</Frame>\n')
    out.append(
        f'{t}<!-- The towns\' shot counts (each team\'s towns plus the core shots), flanking the minimap\'s\n'
        f'{t}     middle on the screen\'s bottom edge (MapMechanicPanel TeamCollectionFrameTemplate). Their\n'
        f'{t}     panel filled the right-edge strip, which clipped them (user, 2026-10-06): it now\n'
        f'{t}     spans the screen, unclipped. -->\n'
        f'{t}<Frame type="Frame" name="PotentialPointsPanel">\n'
        f'{t}\t<Anchor side="Top"    relative="$GameUI" pos="Min" offset="0"/>\n'
        f'{t}\t<Anchor side="Left"   relative="$GameUI" pos="Min" offset="0"/>\n'
        f'{t}\t<Anchor side="Bottom" relative="$GameUI" pos="Max" offset="0"/>\n'
        f'{t}\t<Anchor side="Right"  relative="$GameUI" pos="Max" offset="0"/>\n'
        f'{t}\t<Unclipped val="true"/>\n'
        f'{t}</Frame>\n')
    return "".join(out)


# ------------------------------------------------------------------ Cursed Hollow's curse

def box_sides(box, up=0):
    """A box alert's frame from its spot: the art's box, its top-right corner where the art
    wants it (its box reaching `up` higher). -> ((side, pos, offset), ...)"""
    l, tp, r, b = box
    return (("Top", "Min", -tp - up), ("Left", "Min", 0), ("Bottom", "Max", 0), ("Right", "Max", -r))


TRIBUTE_BOX = (-489, 20, -5, 133)   # the tribute banner's art from its frame's top-right (measured;
                                    # its bar's tip 3 px short of red's plates at -486: 1164 against
                                    # Towers' 1168, Braxis's 1166 - each read at its own tip, 2026-10-09)
CURSE_UP = 30                       # the curse's raven head stands this much higher
COUNT_SPACE = -1           # units between a banner's words' box and its count's: one space.
                           # Words in Blizzard's banner style are 6 px apart; the labels' own
                           # padding made 7 units read as 14 px, -2 as 5 (measured 2026-10-06)
TRIBUTE_WORDS_START = 35   # the tribute's words start this far into the bar, as the red curse's
# "Tribute Spawning", in every language the game ships (heroesdata gamestrings,
# Param/Value/lib_UIUI_EA41E137) -> ours to go before the count, worded as Towers of Doom's
# "Altar Spawns In" is in that language (Param/Value/lib_MTOD_F838B570), with Blizzard's word
# for the tribute, and a colon where that language's "Altars activate in:" has one (the count
# that shows in game, lib_MTOD_191414BF; user, 2026-10-06). French words Towers' without a
# preposition, so its text stays.
TRIBUTE_SPAWNS_IN = {
    "Tribute Spawning": "Tribute Spawns In:",
    "Tribut erscheint": "Tribut erscheint in",
    "Aparición de tributo": "El tributo aparecerá en",
    "Engendrando tributo": "El tributo emergerá en:",
    "Apparition du tribut": "Apparition du tribut",
    "Tributo in preparazione": "Tributo generato fra:",
    "공물 생성 중": "공물 생성:",
    "Pojawia się danina": "Danina pojawi się za:",
    "Tributo aparecendo": "O tributo surge em:",
    "Появление дара": "Дар появится через",
    "贡品即将刷新": "贡品即将刷新：",
    "貢品出現": "貢品即將出現：",
}
# What the curse banner says to an observer when BLUE is cursed, in every language the game
# ships (heroesdata gamestrings, Param/Value/lib_UIUI_51946936). It's one banner for either
# team and the text is all that tells them apart: the game-string reference didn't match in a
# condition, the words did (2026-10-06).
BLUE_CURSED = ("Blue Team Cursed", "Das blaue Team wurde verflucht", "Equipe Azul Amaldiçoada",
               "Equipo azul maldito", "Niebiescy są przeklęci", "Squadra blu maledetta",
               "Équipe bleue maudite", "Синяя команда проклята", "蓝队已被诅咒", "藍隊遭到詛咒",
               "파랑팀에 저주 내림")


# Braxis Holdout's zerg warning ("Beacons activate in"): the bar 324 left of its radar-dish image
# and ending 9 past it (holdout.stormlayout); measured in game (2026-10-09, off a 1401-tall
# screenshot): 481 wide like the tribute's, its bar's bottom 148 below the frame's top - the
# art's lowest part (its radar dish doesn't hang below the bar).
HOLDOUT_BOX = (-(11 + 482), 20, -11, 150)   # read again at 1080p (2026-10-09), by the bar itself:
                                            # its tip 1 px short of red's plates, its bottom 2 px low
ALERT_ART["HOLDOUT"] = Art(HOLDOUT_BOX[2] - HOLDOUT_BOX[0], 0, height=HOLDOUT_BOX[3] - HOLDOUT_BOX[1])
# The tribute's box reaches down to its beak: its bar's bottom is 24 above that (at 1080p its bar
# 930, its box 952; 2026-10-09). Its height takes in the curse that replaces it, whose raven
# head stands CURSE_UP higher.
ALERT_ART["BANNER"] = Art(TRIBUTE_BOX[2] - TRIBUTE_BOX[0], 0, bar_up=24, below=24,
                          height=TRIBUTE_BOX[3] - TRIBUTE_BOX[1] + CURSE_UP)
# Braxis's zerg HUD, compacted (user, 2026-10-09). Observers see BossDuelLeftFrame: blue's
# hexagon BossHudLeft on the left, red's BossHudRight on the right, the progress bars between.
# Each hexagon at 1080p (screenshot 2026-10-09 21:38): 99 x 76 px, pointed at its sides, its
# bottom corners 24 px in from its points; its image's box matches the art to ~2 px (worked out
# from holdout.stormlayout), so the image's Mid is the hexagon's centre. Everything below is
# placed from that centre, in px.
HEX_W_PX, HEX_H_PX, HEX_CORNER_IN_PX = 99, 76, 24
HEX = {"Top": "$parent/$parent/BossDuelLeftFrame/BossHudLeft",       # from RadarDishModeFrame's parts
       "Bottom": "$parent/$parent/BossDuelLeftFrame/BossHudRight"}
# The two beacon dishes (which team holds each beacon; Top = the top lane's, on the left): each
# against its hexagon's lower outer edge, its ring that edge's tangent (user, 2026-10-09). They
# used to sit on the map's bottom corners; anchored to the hexagons, they follow the HUD.
BEACON_W_PX, BEACON_H_PX = 99, 117   # a dish image at Blizzard's size (ring 72 across, centred across it)
BEACON_MARGIN_PX = 22   # ...its transparent space under its ring
BEACON_SCALE = 0.9      # drawn at 90% (user, 2026-10-09); the ring and margin scale with it
BEACON_GAP_PX = 2       # each ring this far off its hexagon's edge...
BEACON_DOWN_PX = 4      # ...then this far straight down (user, 2026-10-09: a bit close, the left one's
                        # pointer reaching for its hexagon's point)
_RING = 72 * BEACON_SCALE / 2
_EDGE = (HEX_CORNER_IN_PX, HEX_H_PX / 2)               # the left hexagon's lower outer edge, point to corner
_OUT = (-_EDGE[1] / math.hypot(*_EDGE), _EDGE[0] / math.hypot(*_EDGE))   # ...facing out (left, down)
BEACON_AT_PX = tuple(round(e / 2 + o * (_RING + BEACON_GAP_PX) + (-HEX_W_PX / 2 if i == 0 else 0), 1)
                     for i, (e, o) in enumerate(zip(_EDGE, _OUT)))   # the left ring's centre (-66.6, 37.4); the right's mirrors it
_DISH_SIDE = round((abs(BEACON_AT_PX[0]) + BEACON_W_PX * BEACON_SCALE / 2) / 0.9)   # its image's outer side
_DISH_BOTTOM = round((BEACON_AT_PX[1] + BEACON_DOWN_PX + _RING + BEACON_MARGIN_PX * BEACON_SCALE) / 0.9)
# "On air" (user, 2026-10-09): while one team holds both beacons - its zerg charging - a bold
# ring in its colour over each dish, breathing like an on-air light, and a broadcast wave
# rolling out from it (they're satellites). Blizzard's electric line is only the signal now:
# the script shows HoldOutLink1-2 (blue's) while BLUE holds both and 3-4 (red's) while red does
# (libscho MMHO lightning links); kept at Alpha 0, and a state on its Visible shows our rings.
# (The line itself, first a long line along the map's bottom edge, then turned into a beam into
# each hexagon, read as nothing much - user, 2026-10-09.) The art: Blizzard's generic ring glow,
# tinted (Volskaya's stopwatch ring); each ring centred on its dish's ring (the image's Mid -
# its ring sits centred in it), sized by Width/Height with all four sides on that point (Zarya's
# energy ring), which the wave animates. Under the hexagons: the wave rolls behind them.
ON_AIR = (("Blue", 1, "TeamOrderColors"), ("Red", 3, "TeamChaosColors"))   # team, its line, its colour
ON_AIR_RING = 84                       # the steady ring, units across (the dish's ring is 72)
ON_AIR_BREATHE = (1.6, 255, 130)       # its breath: seconds, full and low alpha
ON_AIR_WAVE = (1.4, 86, 160, 220)      # the wave: seconds, units across from and to, starting alpha - from
                                       # the dish's border, where the steady ring draws (user, 2026-10-09:
                                       # from 72 it began inside it)


def _ring(team, colour, dish, kind):
    """One of team's rings on a dish (Top/Bottom), steady or the wave, inside FCJH_OnAir<team>."""
    def keys(pairs):
        return "".join(f'<Key type="Curve" time="{t}" value="{v}"/>' for t, v in pairs)
    if kind == "Ring":
        size = ON_AIR_RING
        s, hi, lo = ON_AIR_BREATHE
        anim = f'<Controller type="Fade" end="Loop">{keys(((0, hi), (s / 2, lo), (s, hi)))}</Controller>'
    else:
        s, start, end, alpha = ON_AIR_WAVE
        size = start
        anim = "".join(f'<Controller type="Dimension" dimension="{d}" relative="False" percentage="False" end="Loop">'
                       f'{keys(((0, start), (s, end)))}</Controller>' for d in ("Width", "Height"))
        anim += f'<Controller type="Fade" end="Loop">{keys(((0, alpha), (s, 0)))}</Controller>'
    dish_at = f"$parent/$parent/HoldOutBeacon{dish}Off"
    return (f'<Frame type="Image" name="FCJH_OnAir{kind}{dish}">'
            + "".join(f'<Anchor side="{side}" relative="{dish_at}" pos="Mid" offset="0"/>'
                      for side in ("Top", "Bottom", "Left", "Right"))
            + f'<Width val="{size}"/><Height val="{size}"/><Visible val="false"/>'
            f'<Texture val="@UI/Storm_UI_GenFX_RingGlow"/><BlendMode val="Add"/><ColorAdjustMode val="Colorize"/>'
            f'<LightAdjustColor val="#ColorWhite"/><DarkAdjustColor val="{{$GameUI/{colour}/@Color}}"/>'
            f'<Unclipped val="true"/><AcceptsMouse val="false"/>'
            f'<Animation name="FCJH_OnAir"><Event event="OnShown" action="Restart,Play"/>{anim}</Animation></Frame>')


def _on_air(team, link, colour):
    """FCJH_OnAir<team>: its four rings, shown while its line (HoldOutLink<link>) is."""
    parts = [(dish, kind) for dish in ("Top", "Bottom") for kind in ("Wave", "Ring")]
    return (f'<Frame type="Frame" name="FCJH_OnAir{team}"><Anchor relative="$parent"/><AcceptsMouse val="false"/>'
            f'<RenderPriority val="110"/>'      # over the dishes (100)
            + "".join(_ring(team, colour, dish, kind) for dish, kind in parts)
            + f'<StateGroup name="FCJH_OnAir"><DefaultState val="Off"/><State name="On">'
            f'<When type="Property" frame="$parent/HoldOutLink{link}" Visible="true"/>'
            + "".join(f'<Action type="SetProperty" frame="$this/FCJH_OnAir{kind}{dish}" Visible="true"/>'
                      for dish, kind in parts)
            + '</State><State name="Off"/></StateGroup></Frame>')


_SIZE = (f'<Width val="#FCJH_MAP_BEACON_W"/><Height val="#FCJH_MAP_BEACON_H"/>'
         f'<Unclipped val="true"/></Frame>')
BEACON_ICONS = "".join(
    f'<Frame type="Image" name="HoldOutBeaconTop{s}"><Anchor side="Bottom" relative="{HEX["Top"]}" pos="Mid" '
    f'offset="{_DISH_BOTTOM}"/><Anchor side="Left" relative="{HEX["Top"]}" pos="Mid" '
    f'offset="{-_DISH_SIDE}"/>{_SIZE}' for s in ("Off", "Order", "Chaos")) + "".join(
    # the bottom lane's keep Blizzard's bottom, on the top lane's Off
    f'<Frame type="Image" name="HoldOutBeaconBottom{s}"><Anchor side="Right" relative="{HEX["Bottom"]}" pos="Mid" '
    f'offset="{_DISH_SIDE}"/>{_SIZE}' for s in ("Off", "Order", "Chaos")) + "".join(
    f'<Frame type="Image" name="HoldOutLink{n}"><Alpha val="0"/></Frame>' for n in range(1, 5)) + "".join(
    _on_air(*t) for t in ON_AIR)
# The words on the HUD, in both BossDuel frames (the Right one is team 2's players'):
#   - each % (Left/RightBossHealthLabel) centred in its hexagon (user, 2026-10-09; Blizzard's sat
#     2 right of the middle, under the hexagon). Its letters' middle is 14 px above its box's bottom
#     (measured: offset 28 put them 11 px under the centre).
#   - "BEACON PROGRESS" and the wave's "Enemy Zerg" ABOVE the bar, on the row Blizzard gives
#     "Allied Zerg": under it they'd sit on the map once the HUD came down (user, 2026-10-09).
PCT_LETTERS_UP_PX = 14
_PCT = lambda side, hexagon: (f'<Frame type="Label" name="{side}BossHealthLabel">'
                              f'<Anchor side="Bottom" relative="$parent/BossHudLeft" pos="Mid" offset="{round(PCT_LETTERS_UP_PX / 0.9)}"/>'
                              f'<Anchor side="Left" relative="$parent/{hexagon}" pos="Mid" offset="0"/>'
                              f'<Anchor side="Right" relative="$parent/{hexagon}" pos="Mid" offset="0"/></Frame>')
ZERG_WORDS = (_PCT("Left", "BossHudLeft") + _PCT("Right", "BossHudRight")
              + '<Frame type="Label" name="BeaconProgressLabel"><Anchor side="Top" relative="$parent/BackgroundImage" '
              'pos="Min" offset="-15"/></Frame>'
              '<Frame type="Label" name="EnemyZergLabel"><Anchor side="Bottom" relative="$parent/AlliedZergLabel" '
              'pos="Max" offset="0"/></Frame>')
# Raw XML per map, inside one of its panels' parts: {map key: {path: xml}} (map_file).
PARTS = {"braxis_holdout": {"HoldOutPanel/RadarDishModeFrame": BEACON_ICONS,
                            "HoldOutPanel/BossDuelLeftFrame": ZERG_WORDS,
                            "HoldOutPanel/BossDuelRightFrame": ZERG_WORDS}}
HOLDOUT_PARTS = (("Image", "BackgroundImage", ()), ("Image", "TimerImage", ()),
                 ("Label", "HoldOutWarningInfoLabel", ()), ("Label", "HoldOutWarningTimerLabel", ()))


# ------------------------------------------------------------------ banners laid out from the bar's left

# Every banner on red's side that Blizzard sizes to its words (the hexagon at its right end, the
# bar growing left) is laid out from its left end instead, so it starts at red's plates in every
# language: the bar from the frame's left, our copy of the words in, the count one space after
# them, the hexagon after that. A banner never changes size while it counts (user, 2026-10-12:
# Garden's seed widened and narrowed with its number - the hexagon had hung off the count, and
# "11" is less than half as wide as "25"): the count gets a slot as wide as the widest it can
# read (BANNER_SLOT, the game's own sizing text, in the count's font; drawn at Alpha 0), right-
# aligned in it, and the hexagon hangs off the slot. Its width changes only with the language.
BANNER_SLOT = "8:88"
BAR_TIP_IN = 3     # the banners' bar art (HUD_MapMechanic_BG_CenterBar, every banner's) has its tip
                   # 3 in from its image's end: the image starts that much past the spot's edge, for
                   # the tip to sit on red's plates' edge (1167) as Towers' and Braxis's do (measured at
                   # the mines' tip 2026-10-09: 1170; a first read along one row for every bar said 1177)


def banner_label(name_, anchors, text, style, more=""):
    """One of our banner labels: anchors ((side, relative, pos, offset), ...), unindented."""
    return (f'<Frame type="Label" name="{name_}">\n'
            + "".join(f'\t<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
                      for sd, rel, pos, off in anchors)
            + f'\t<Text val="{text}"/>\n\t<Style val="{style}"/>\n'
            f'\t<Options val="NoWrapping"/>\n\t<Unclipped val="true"/>\n' + more + '</Frame>\n')


def count_slot(name_, row, anchor, style, slot=BANNER_SLOT):
    """The slot a count sits right-aligned in, as wide as `slot` reads: row, its Top/Bottom
    anchors; anchor, its one side's; style, the count's (the slot takes its font)."""
    return banner_label(name_, row + (anchor,), slot, style, '\t<Alpha val="0"/>\n')


def left_banner(prefix, words, count, hexagon, words_start, hex_after, depth=7, slot=BANNER_SLOT,
                count_style=None, bar=""):
    """A banner laid out from its bar's left end (above): FCJH_<prefix>Text copying Blizzard's
    words, FCJH_<prefix>Slot and FCJH_<prefix>Count its count (count None: it has none), and
    Blizzard's parts - the bar from the frame's left, the hexagon's right hex_after past the
    slot's (or the words'), Blizzard's labels hidden. count_style: the count's, if not its own
    (a count Blizzard hung under the hexagon, in a bigger style, takes the words'); bar: more
    inside the bar's image. -> the frame's insides, at depth."""
    w, s, c = (f"FCJH_{prefix}{n}" for n in ("Text", "Slot", "Count"))
    out = banner_label(w, (("Top", f"$parent/{words}", "Min", 0), ("Bottom", f"$parent/{words}", "Max", 0),
                           ("Left", "$parent/BackgroundImage", "Min", words_start)),
                       f"{{$parent/{words}/@Text}}", f"{{$parent/{words}/@Style}}")
    last = w
    if count:
        row = (("Top", f"$parent/{w}", "Min", 0), ("Bottom", f"$parent/{w}", "Max", 0))
        style = count_style or f"{{$parent/{count}/@Style}}"
        out += (count_slot(s, row, ("Left", f"$parent/{w}", "Max", COUNT_SPACE), style, slot)
                + banner_label(c, row + (("Right", f"$parent/{s}", "Max", 0),), f"{{$parent/{count}/@Text}}", style))
        last = s
    parts = ((("Image", "BackgroundImage", (), f'<Anchor side="Left" relative="$parent" pos="Min" offset="{-BAR_TIP_IN}"/>'
               + (f"\n{bar}" if bar else "")),
              ("Image", hexagon, (), f'<Anchor side="Right" relative="$parent/{last}" pos="Max" offset="{hex_after}"/>'),
              ("Label", words, (), '<Alpha val="0"/>'))
             + ((("Label", count, (), '<Alpha val="0"/>'),) if count else ()))
    return "".join(T * depth + line + "\n" for line in out.splitlines()) + unclipped(parts, depth)


# ------------------------------------------------------------------ team banners: left on red, right on blue

# A banner Blizzard shows for either team - one frame - sits on the owning team's side, and every
# one is made by the same protocol (user, 2026-10-12): team_banner. Red's side is a left banner -
# the bar's tip on red's inner edge at its LEFT end, the art at its outer end, as left_banner's -
# and blue's a right banner, its mirror: the tip on blue's inner edge at its RIGHT end, the art at
# its outer end, flipped. Each side's tip is its spot's inner edge (red's spot's left, blue's
# spot's right), the bar's image BAR_TIP_IN past it. A banner's layout is written ONCE, in red's
# terms - x out from the tip (Side) - and the protocol writes red's state from it and blue's as
# its mirror. Where blue can't be the plain mirror (a status bar's fill won't flip; text still
# reads left to right) the layout picks per side (Side.pick), beside the reason.
FLIPPED = '<TextureCoords top="0.0" left="1.0" bottom="1.0" right="0.0"/>'
_OPPOSITE = {"Left": "Right", "Right": "Left", "Min": "Max", "Max": "Min", "Mid": "Mid"}


class Side:
    """One side of a team banner, for its layout to write in red's terms (team_banner). Parts:
    "" the banner's frame, "/Part" under it, or an absolute path. x: out from the bar's tip -
    rightwards on red's side, leftwards on blue's."""

    def __init__(self, frame, spot, blue):
        self.frame, self.spot, self.blue, self.xml = frame, spot, blue, ""

    def path(self, part):
        return self.frame + part if part == "" or part.startswith("/") else part

    def pick(self, red, blue):
        return blue if self.blue else red

    def anchor(self, part, side, rel, pos, off):
        """An anchor the same on both sides (not mirrored)."""
        self.xml += (f'<Action type="SetAnchor" frame="{self.path(part)}" side="{side}" '
                     f'relative="{self.path(rel)}" pos="{pos}" offset="{off}"/>')

    def set(self, part, **props):
        self.xml += "".join(f'<Action type="SetProperty" frame="{self.path(part)}" {k}="{v}"/>'
                            for k, v in props.items())

    def box(self, part, box, up=0, spare=0):
        """part as a box alert's frame on this side's spot (box_sides), `spare` more to its right."""
        for sd, pos, off in box_sides(box, up):
            self.anchor(part, sd, self.spot, pos, off + (spare if sd == "Right" else 0))

    def _tip(self, x):
        return ("Max", -x) if self.blue else ("Min", x)

    def at(self, part, side, x):
        """part's side x out from the tip (blue's: the other side)."""
        self.anchor(part, _OPPOSITE[side] if self.blue else side, self.spot, *self._tip(x))

    def span(self, part, a, b):
        """part from a to b out from the tip."""
        self.at(part, "Left", a)
        self.at(part, "Right", b)

    def hold(self, part, side, a, b):
        """A part of its own size, a to b out from the tip, that Blizzard holds by one side: held
        by that side on both teams' (a state can't take an anchor away)."""
        self.anchor(part, side, self.spot, *self._tip(b if (side == "Right") != self.blue else a))

    def hang(self, part, side, rel, pos, off, width=None):
        """part's side off rel's edge, as on red's. Blue's mirror: the other side off rel's other
        edge - or, for a part of its own size (width), the same side, moved by its width."""
        if not self.blue:
            return self.anchor(part, side, rel, pos, off)
        if width is None:
            return self.anchor(part, _OPPOSITE[side], rel, _OPPOSITE[pos], -off)
        self.anchor(part, side, rel, _OPPOSITE[pos], -off + (width if side == "Right" else -width))

    def flip(self, part, faces="red"):
        """An image drawn for one side's layout, flipped on the other."""
        self.set(part, TextureCoords="0,0,1,1" if self.blue == (faces == "blue") else "0,1,1,0")

    def drain(self, bar):
        """A status bar draining from the tip's end, towards the art."""
        self.set(bar, Expansion=self.pick("Left", "Right"))

    def justify(self, part, style, toward):
        """A label's style ({} -> Left/Right) set towards the inner end (the tip's) or the outer."""
        self.set(part, Style=style.format(self.pick("Left", "Right") if toward == "inner" else self.pick("Right", "Left")))

    def show(self, part, team):
        """part shown on one team's side only: its copy (flipped_copy) or Blizzard's original."""
        self.set(part, Alpha=255 if (team == "blue") == self.blue else 0)


def team_banner(name, frame, spots, blue_when, layout, depth=7):
    """StateGroup FCJH_<name>Side on a team banner's frame (above): red's state the default, blue's
    while blue_when holds (its <When>s; a list for alternatives, a state each). spots: (red's,
    blue's). layout(side) writes the banner on a Side, in red's terms."""
    def write(blue):
        side = Side(frame, spots[blue], blue)
        layout(side)
        return side.xml
    whens = [blue_when] if isinstance(blue_when, str) else blue_when
    blue, t = write(True), T * depth
    return (f'{t}<StateGroup name="FCJH_{name}Side">\n{t}\t<DefaultState val="Red"/>\n'
            + "".join(f'{t}\t<State name="Blue{n if len(whens) > 1 else ""}">{when}{blue}</State>\n'
                      for n, when in enumerate(whens))
            + f'{t}\t<State name="Red">{write(False)}</State>\n{t}</StateGroup>\n')


def flipped_copy(name_, texture, anchors, depth=7, coords=FLIPPED):
    """Blue's copy of an image Blizzard holds by one side (a state can't take that anchor away,
    and blue's mirror is held by the other): the same art, flipped, shown on blue's side only
    (Side.show). anchors: ((side, relative, pos, offset), ...)."""
    t = T * depth
    return (f'{t}<Frame type="Image" name="{name_}">\n'
            + "".join(f'{t}\t<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
                      for sd, rel, pos, off in anchors)
            + f'{t}\t<Texture val="{texture}"/>\n{t}\t{coords}\n{t}\t<Unclipped val="true"/>\n'
            f'{t}\t<Alpha val="0"/>\n{t}</Frame>\n')


RAVEN = MECHANICS + "/RavenCourtPanel"
CURSE = RAVEN + "/CurseFrame"
CURSE_SPARE = 200     # red's curse box reaches this much further right: its hexagon follows the
                      # text, and a long translation pushes it past the tribute's box
# The curse's words on red's side: ours, the same text and style as Blizzard's label, but
# placed from the bar's LEFT end - Blizzard's is placed from the hexagon (cursed_side).
CURSE_WORDS_START = 35     # the words this far into the bar from its tip's end, both sides
CURSE_TEXT = (f'{T*7}<Frame type="Label" name="FCJH_CurseText">\n'
              f'{T*8}<Anchor side="Bottom" relative="$parent/BackgroundImage" pos="Max" offset="-10"/>\n'
              f'{T*8}<Anchor side="Left"   relative="$parent/BackgroundImage" pos="Min" offset="{CURSE_WORDS_START}"/>\n'
              f'{T*8}<Text val="{{$parent/CurseInfoLabel/@Text}}"/>\n'
              f'{T*8}<Style val="{{$parent/CurseInfoLabel/@Style}}"/>\n'
              f'{T*8}<Options val="NoWrapping"/>\n'
              f'{T*8}<Alpha val="0"/>\n'
              f'{T*7}</Frame>\n')
# The curse's countdown in its bar after the words, as the tribute's (user, 2026-10-06), one
# space after them; Blizzard's (in the raven head) hidden. Two of ours, one per side's layout
# (cursed_side): red's after our words, flowing right; blue's ending CURSE_WORDS_START in from
# the bar's tip, Blizzard's words ending one space before it (text reads left to right on
# both sides: blue's mirror runs it from the tip leftwards).
CURSE_STYLE = "{$parent/CurseInfoLabel/@Style}"
_CURSE_ROW = (("Top", "$parent/FCJH_CurseText", "Min", 0), ("Bottom", "$parent/FCJH_CurseText", "Max", 0))
_CURSE_ROW_BLUE = (("Top", "$parent/CurseInfoLabel", "Min", 0), ("Bottom", "$parent/CurseInfoLabel", "Max", 0))
_BLUE_END = ("Right", "$parent/BackgroundImage", "Max", -CURSE_WORDS_START)
# Each count right-aligned in its slot (left_banner): red's slot after the words (or their
# colon, curse_colon), the raven off it (cursed_side); blue's before the tip, the words ending
# one space before it - so neither side's bar changes size as the count runs.
CURSE_COUNT = "".join(
    "".join(T * 7 + line + "\n" for line in xml.splitlines()) for xml in (
        count_slot("FCJH_CurseSlot", _CURSE_ROW, ("Left", "$parent/FCJH_CurseText", "Max", COUNT_SPACE), CURSE_STYLE),
        banner_label("FCJH_CurseCount", _CURSE_ROW + (("Right", "$parent/FCJH_CurseSlot", "Max", 0),),
                     "{$parent/CurseTimerLabel/@Text}", CURSE_STYLE, '\t<Alpha val="0"/>\n'),
        count_slot("FCJH_CurseSlotBlue", _CURSE_ROW_BLUE, _BLUE_END, CURSE_STYLE),
        banner_label("FCJH_CurseCountBlue", _CURSE_ROW_BLUE + (_BLUE_END,),
                     "{$parent/CurseTimerLabel/@Text}", CURSE_STYLE, '\t<Alpha val="0"/>\n')))


# The curse's words -> the colon before its count, where that language's Towers of Doom
# "Altars activate in:" has one (lib_MTOD_191414BF; user, 2026-10-06), from the curse's blue
# and red words in every language (lib_UIUI_51946936 / 9C28BA95). "Equipo azul maldito" is
# both Spanishes' blue, and only Mexico's takes a colon: left without.
CURSE_COLONS = {
    "Blue Team Cursed": ":", "Red Team Cursed": ":",
    "El equipo rojo está maldito": ":",
    "Squadra blu maledetta": ":", "Squadra rossa maledetta": ":",
    "파랑팀에 저주 내림": ":", "빨강팀에 저주 내림": ":",
    "Niebiescy są przeklęci": ":", "Czerwoni są przeklęci": ":",
    "Equipe Azul Amaldiçoada": ":", "Equipe Vermelha amaldiçoada": ":",
    "蓝队已被诅咒": "：", "红队被诅咒": "：", "藍隊遭到詛咒": "：", "紅隊遭到詛咒": "：",
}
COLON_SPACE = -5      # units between the words' box and the colon's: touching, as a letter


def curse_colon():
    """The colon between the curse's words and its count, in its own label (the words are
    Blizzard's, or bound to them): one per side's layout, shown with that side's words
    (cursed_side). In a language with a colon the count follows the colon, else the words."""
    count, blue_count = f"{CURSE}/FCJH_CurseSlot", f"{CURSE}/FCJH_CurseSlotBlue"
    act = lambda frame, sd, rel, pos, off: (f'<Action type="SetAnchor" frame="{frame}" side="{sd}" relative="{rel}" '
                                            f'pos="{pos}" offset="{off}"/>')
    text = lambda c: (f'<Action type="SetProperty" frame="{CURSE}/FCJH_CurseColon" Text="{c}"/>'
                      f'<Action type="SetProperty" frame="{CURSE}/FCJH_CurseColonBlue" Text="{c}"/>')
    t = T * 8
    states = "".join(f'{t}\t<State name="Colon{i}"><When type="Property" frame="{CURSE}/CurseInfoLabel" Text="{words}"/>'
                     + text(c) + act(count, "Left", f"{CURSE}/FCJH_CurseColon", "Max", COUNT_SPACE)
                     + act(f"{CURSE}/CurseInfoLabel", "Right", f"{CURSE}/FCJH_CurseColonBlue", "Min", -COLON_SPACE)
                     + "</State>\n" for i, (words, c) in enumerate(CURSE_COLONS.items()))
    group = (f'{t}<StateGroup name="FCJH_CurseColon">\n{t}\t<DefaultState val="None"/>\n' + states
             + f'{t}\t<State name="None">' + text("") + act(count, "Left", f"{CURSE}/FCJH_CurseText", "Max", COUNT_SPACE)
             + act(f"{CURSE}/CurseInfoLabel", "Right", blue_count, "Min", -COUNT_SPACE) + "</State>\n"
             f'{t}</StateGroup>\n')
    label = lambda name_, words, sd, rel, pos, off, more="": (
        f'{T*7}<Frame type="Label" name="{name_}">\n'
        f'{t}<Anchor side="Top"    relative="{words}" pos="Min" offset="0"/>\n'
        f'{t}<Anchor side="Bottom" relative="{words}" pos="Max" offset="0"/>\n'
        f'{t}<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
        f'{t}<Text val=""/>\n{t}<Style val="{{$parent/CurseInfoLabel/@Style}}"/>\n'
        f'{t}<Options val="NoWrapping"/>\n{t}<Unclipped val="true"/>\n{t}<Alpha val="0"/>\n'
        + more + f'{T*7}</Frame>\n')
    return (label("FCJH_CurseColon", "$parent/FCJH_CurseText", "Left", "$parent/FCJH_CurseText", "Max", COLON_SPACE, group)
            + label("FCJH_CurseColonBlue", "$parent/CurseInfoLabel", "Right", "$parent/FCJH_CurseSlotBlue", "Min",
                    -COUNT_SPACE))


def tribute_count():
    """The tribute's countdown in its bar, after the words, as Towers of Doom's altar countdown
    (Blizzard's NotificationFrameCountdownTemplate: words then count, in the words' style; user,
    2026-10-06) - Blizzard's hung under the hexagon, onto the XP bar. Ours reads Blizzard's
    (hidden) and shows while the script shows it: the spawn countdown, not "Collect the Tribute"
    (uilib.galaxy hides the count then). While it counts, our words in the game's language
    ("Tribute Spawns In", TRIBUTE_SPAWNS_IN) replace Blizzard's. They flow as text: the words
    from the bar's left end, as the red curse's, the count one space after them, middle to
    middle (user, 2026-10-06). In a language not listed, Blizzard's words and count stand.
    "Collect the Tribute" (no count) is hidden, the whole banner (user, 2026-10-15: static words
    the minimap's marker already says; revisit after the final pass): its art and words faded
    out while the count is hidden - the frame stays shown, its intro fading it."""
    tribute = RAVEN + "/TributeSpawnFrame"
    info, count, words = f"{tribute}/TributeInfoLabel", f"{tribute}/FCJH_TributeCount", f"{tribute}/FCJH_TributeWords"
    timer = f"{tribute}/TributeTimerLabel"
    alpha = lambda frame, a: f'<Action type="SetProperty" frame="{frame}" Alpha="{a}"/>'
    art = lambda a: alpha(f"{tribute}/BackgroundImage", a) + alpha(f"{tribute}/TimerImage", a)
    counting = f'<When type="Property" frame="{timer}" Visible="true"/>'
    t = T * 8
    label = lambda name_, anchors, text, more="": (
        f'{T*7}<Frame type="Label" name="{name_}">\n'
        + "".join(f'{t}<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
                  for sd, rel, pos, off in anchors)
        + f'{t}<Text val="{text}"/>\n{t}<Style val="{{$parent/TributeInfoLabel/@Style}}"/>\n'
        f'{t}<Options val="NoWrapping"/>\n{t}<Unclipped val="true"/>\n{t}<Alpha val="0"/>\n'
        + more + f'{T*7}</Frame>\n')
    states = "".join(f'{t}\t<State name="In{i}">{counting}<When type="Property" frame="{info}" Text="{theirs}"/>'
                     f'<Action type="SetProperty" frame="{words}" Text="{ours}"/>'
                     + alpha(words, 255) + alpha(count, 255) + alpha(info, 0) + alpha(timer, 0) + art(255) + "</State>\n"
                     for i, (theirs, ours) in enumerate(TRIBUTE_SPAWNS_IN.items()))
    group = (f'{t}<StateGroup name="FCJH_TributeWords">\n{t}\t<DefaultState val="Words"/>\n' + states
             + f'{t}\t<State name="Counting">{counting}' + alpha(words, 0) + alpha(count, 0)
             + alpha(info, 255) + alpha(timer, 255) + art(255) + "</State>\n"
             f'{t}\t<State name="Words">' + alpha(words, 0) + alpha(count, 0) + alpha(info, 0) + art(0) + "</State>\n"
             f'{t}</StateGroup>\n')
    return (label("FCJH_TributeWords", (("Top", "$parent/TributeInfoLabel", "Min", 0),
                                        ("Bottom", "$parent/TributeInfoLabel", "Max", 0),
                                        ("Left", "$parent/BackgroundImage", "Min", TRIBUTE_WORDS_START)), "", group)
            + label("FCJH_TributeCount", (("Top", "$parent/FCJH_TributeWords", "Min", 0),
                                          ("Bottom", "$parent/FCJH_TributeWords", "Max", 0),
                                          ("Left", "$parent/FCJH_TributeWords", "Max", COUNT_SPACE)),
                    "{$parent/TributeTimerLabel/@Text}"))


def unclipped(parts, depth=7):
    """Blizzard's parts of a box alert, let draw past its box: the box is cut to the art as
    measured off a screenshot, and the tribute's point came out clipped (user, 2026-10-06), as
    would the curse's glow, which grows to 160%. parts: ((type, name, (child parts)[, xml]), ...),
    xml: more inside that part."""
    return "".join(f'{T*depth}<Frame type="{kind}" name="{name}">\n{T*(depth+1)}<Unclipped val="true"/>\n'
                   + "".join(f"{T*(depth+1)}{line}\n" for line in (more[0] if more else "").splitlines())
                   + unclipped(kids, depth + 1) + f'{T*depth}</Frame>\n' for kind, name, kids, *more in parts)


TRIBUTE_PARTS = (("Image", "BackgroundImage", ()), ("Image", "TimerImage", ()),
                 ("Label", "TributeInfoLabel", ()),
                 ("Label", "TributeTimerLabel", (), '<Alpha val="0"/>'))
CURSE_PARTS = (("Image", "BackgroundImage", ()), ("Image", "TimerImage", ()),
               ("Label", "CurseInfoLabel", (),
                f'<Anchor side="Right" relative="$parent/FCJH_CurseSlotBlue" pos="Min" offset="{-COUNT_SPACE}"/>'),
               ("Label", "CurseTimerLabel", (), '<Alpha val="0"/>'),
               ("Frame", "AttentionEffect", (("Image", "AttentionEffectImage", ()),
                                             ("Image", "AttentionEffect2Image", ()))))


CURSE_RAVEN_AFTER = 115   # the raven's outer side from the count's slot (red: its right; 5 + its width)
# Blue's raven, flipped at the outer end (team_banner): Blizzard's is held by its right side
CURSE_RAVEN = flipped_copy("FCJH_CurseRaven", "@UI/HUD_MapMechanic_CursedHollow_RavenHead",
                           (("Top", "$parent/TimerImage", "Min", 0),))


def curse_layout(s):
    """The curse banner, red's terms (team_banner). It hangs off the tribute banner's frame, which
    the script hides while a curse is on: both frames move onto the cursed team's spot (red's
    holds the tribute, the neutral banner). Blizzard sizes it to its words, the raven at its right
    end; ours runs from the tip: the bar from it, the words CURSE_WORDS_START in, the count after
    them (CURSE_COUNT), the raven after that - mirrored on blue, where the words still read left to
    right: Blizzard's, ending in the count before the tip."""
    s.box(RAVEN + "/TributeSpawnFrame", TRIBUTE_BOX)
    s.box("", TRIBUTE_BOX, CURSE_UP, spare=s.pick(CURSE_SPARE, 0))   # red's box: room for long words
    raven = s.pick("/TimerImage", "/FCJH_CurseRaven")
    s.at("/BackgroundImage", "Left", -BAR_TIP_IN)
    s.hang("/BackgroundImage", "Right", raven, "Max", 15)            # Blizzard's: 15 past the raven
    s.hang(raven, "Right", s.pick("/FCJH_CurseSlot", "/CurseInfoLabel"), "Max", CURSE_RAVEN_AFTER)
    for glow in ("AttentionEffectImage", "AttentionEffect2Image"):  # round the raven's middle
        for sd in ("Left", "Right"):
            s.anchor(f"/AttentionEffect/{glow}", sd, raven, "Mid", 0)
    for part, team in (("/TimerImage", "red"), ("/FCJH_CurseText", "red"), ("/FCJH_CurseCount", "red"),
                       ("/FCJH_CurseColon", "red"), ("/FCJH_CurseRaven", "blue"), ("/CurseInfoLabel", "blue"),
                       ("/FCJH_CurseCountBlue", "blue"), ("/FCJH_CurseColonBlue", "blue")):
        s.show(part, team)


def cursed_side():
    """The curse on the cursed team's side (user, 2026-10-06): blue's when its words say so."""
    return team_banner("Cursed", CURSE, (f"{RAVEN}/FCJH_TributeSpawnFrameSpot", f"{RAVEN}/FCJH_CurseFrameSpot"),
                       [f'<When type="Property" frame="{CURSE}" Visible="true"/>'
                        f'<When type="Property" frame="{CURSE}/CurseInfoLabel" Text="{text}"/>' for text in BLUE_CURSED],
                       curse_layout)


# ------------------------------------------------------------------ Haunted Mines' banner

# "Mines will open in: 0:23" (core MapMechanicPanel, HauntedMinesPanel/MineTimerModeFrame): its
# hexagon (CenterpieceImageMine) pinned 20 in from the frame's top-right, the bar ending 15
# past it and starting 50 before its words - Blizzard sizes it to them, growing left. Measured
# at 1080p (2026-10-09): the bar 385 px wide in English (428 units), its bottom 86 under the
# hexagon's top as placed (the frame's 27 + 50 = 77 put the bar's bottom edge 8 px under the
# tribute's and Towers', user - read by the bar's lower bracket: 937 against 929). On red's side
# it's laid out from its left end (left_banner), the words 50 in.
MINES_BOX = (-433, 0, -5, 86)
MINES_WORDS_START = 50
MINES_HEX_AFTER = 115     # the hexagon's right from the count's: 5 + its width, as the curse's
                          # (measured: 106 px from the count's last letter to its right edge)
ALERT_ART["MINES"] = Art(MINES_BOX[2] - MINES_BOX[0], 0, height=MINES_BOX[3] - MINES_BOX[1] + 6)
MINES_BANNER = left_banner("Mines", "MineOpenLabel", "MineOpenTimer", "CenterpieceImageMine",
                           MINES_WORDS_START, MINES_HEX_AFTER)
# The golems' health (GolemModeFrame, shown instead of the mines banner once one is summoned):
# Blizzard pins its bar's bottom-right to the mines bar's and its hexagon (GolemHud) to the
# frame's top-right. Ours from the spot's left too: its bar (481 units, its texture's own width,
# as the tribute's) from the spot's left, the hexagon 15 in from its right end, as Blizzard's.
GOLEM_BAR = 481
_HEALTH = (("UnitStatusShieldedHealthBar", "HealthBar", ()),
           ("UnitStatusHealthLabel", "HealthLabel", (("Label", "StatusLabel", ()),)))
GOLEM_PARTS = (("Image", "BackgroundImage", (), f'<Anchor side="Right" relative="$parent" pos="Min" offset="{GOLEM_BAR}"/>'),
               ("Image", "GolemHud", (), '<Anchor side="Right" relative="$parent/BackgroundImage" pos="Max" offset="-15"/>'),
               ("Image", "HealthBarBgTop", ()), ("Image", "HealthBarBgBottom", ()),
               ("UnitStatusFrame", "AllyGolemHealthBar", _HEALTH), ("UnitStatusFrame", "EnemyGolemHealthBar", _HEALTH),
               ("Label", "AllySkullCounter", ()), ("Label", "EnemySkullCounter", ()),
               ("Label", "AllyGolemLabel", ()), ("Label", "EnemyGolemLabel", ()))


# ------------------------------------------------------------------ Garden of Terror's banners

# "Seed spawning in: 0:23" (EventWarningFrame) and "Gather the seed!" (GatherTheSeedsFrame):
# templates of the map's own file (gardenmapmechanic), which its script makes in the mechanics
# panel - nothing to put them in, so they hang off a spot of ours in the core panel
# (GardenOfTerrorPanel/FCJH_EventWarningFrameSpot, red's: neutral, user 2026-10-12). Blizzard's:
# the seed (CenterpieceImage) 20 down at the frame's top-right, the bar's top 30 under its top
# and its right end 30 in from its right, sized to the words (35 before them), growing left;
# the count right-aligned 10 into the seed. Measured at 1080p (2026-10-12): the words and count
# end at x 1040, the bar's right end 1153; its tip 817 ("Seed spawning in: 23", 373 units) and
# 853 ("Gather the seed!"); its lower bracket 790. The bar is the mines' art (its height theirs:
# 59 units from its top to the lower bracket), so its bottom is 50 + 59 under the frame's top.
# On red's side laid out from its left end (left_banner), the words 35 in - and our intro (the
# template's own slides its Right anchor, which nothing hangs off any more).
# The templates set Width 600 and Height 140, and the engine keeps them, centring that on the box
# the anchors give: ours restate the box's size (it sat 100 px left and 15 up, user 2026-10-12).
# Read off that: the bar's lower bracket 107 under the frame's top.
SEED_BOX = (-378, 0, -5, 107)
SEED_WORDS_START = 35
SEED_SLOT = "88"               # its count is bare seconds ("25", "11")
SEED_HEX_AFTER = {True: 153,   # the seed's right from the count's slot: the count's last letter 113 px
                               # from the bar's right end, as Blizzard's (2026-10-12: 153 read 107-112;
                               # 110, from a misread, put the seed over the count, user)
                  False: 153}  # ...from the words' ("Gather the seed!"): 140 px from the last letter
                               # to its right, less the label's padding, as the mines' - unmeasured
SEED_SPOT = MECHANICS + "/GardenOfTerrorPanel/FCJH_EventWarningFrameSpot"
ALERT_ART["SEED"] = Art(SEED_BOX[2] - SEED_BOX[0], 0, height=SEED_BOX[3] - SEED_BOX[1])


def seed_banner(count):
    """One of Garden's seed banners on the seed spot (above). count: it has a TimerLabel."""
    out = "".join(f'<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{SEED_SPOT}" pos="{pos}" offset="{off}"/>\n'
                  for sd, pos, off in box_sides(SEED_BOX))
    out += (f'<Width val="{-SEED_BOX[0]}"/>\n'      # the spot's left to 5 past its right (box_sides)
            f'<Height val="{SEED_BOX[3] - SEED_BOX[1]}"/>\n<Unclipped val="true"/>\n' + intro(0))
    return out + left_banner("Seed", "TextLabel", "TimerLabel" if count else None, "CenterpieceImage",
                             SEED_WORDS_START, SEED_HEX_AFTER[count], depth=0, slot=SEED_SLOT)


# The Terrors' health (GardenTerrorHealthFrame, the map file's template, made in the mechanics
# panel): the plant in its hexagon (Icon_Blue / Icon_Red, 184 x 172 at the frame's top-left, -12)
# and a chevron-ended plate (MapMechanicStatusBG, 463 x 50) with a bar per lane's Terror (65 in
# from the plate's left, 9 from its right). On the summoning team's side (user, 2026-10-12), as
# the Dragon Knight: blue's Blizzard's way round, the plant at the outer end; red's mirrored, the
# plate's chevron on red's plates and the plant at the outer end, flipped. Blizzard's frame
# (530 x 150) centres the plate 10 right of its middle; ours places it from the frame's top-left
# in the same place (TERROR_PLATE), the art 5 .. 507 across - so mirrored, x -> 512 - x.
# Measured at 1080p (2026-10-12, red's, at Blizzard's place): the plate 754 .. 1171 (its chevron's
# tip), its drawn lower edge 795 (105 under the frame's top), the bars' red 9 px tall; the plant's
# leaves out to 720. The bars' red ends at the chevron: the middle one's 1153, the others' 1148 -
# 20 and 25 in from the plate's left once mirrored, flat (a status bar ignores TextureCoords).
# The team: the summoning team's seed count reads "ACTIVE" (SeedsFrame/Team<n>StatusLabel, shown
# to everyone); the script shows each team its own icon colour and observers both, red's on top.
# Red's sits on the seed banners' spot (red's: the two never share the screen for long), blue's
# on a spot of its own.
GARDEN = MECHANICS + "/GardenOfTerrorPanel"
TERROR_ART = (5, 507)                   # the art across, frame units: the leaves to the chevron
TERROR_LINE = 105                       # the plate's drawn lower edge under the frame's top
TERROR_PLATE = (44, 50, 507, 100)       # Blizzard's plate in the frame: left, top, right, bottom
TERROR_BOX = (TERROR_ART[0] - TERROR_ART[1], 0, 0, TERROR_LINE)
ALERT_ART["TERROR"] = Art(TERROR_ART[1] - TERROR_ART[0], 0, height=TERROR_LINE)
TERROR_RED_IN = {1: 25, 2: 20, 3: 25}   # mirrored, each bar's red from the plate's left


TERROR_ICON = (-12, 184)                # the plant's hexagon: its left in Blizzard's frame, its width


def terror_layout(s):
    """The Terrors' health, red's terms (team_banner): x out from the plate's chevron, Blizzard's
    frame's v at x = TERROR_PLATE's right - v (its art is drawn for blue's side: the mirror)."""
    x = lambda v: TERROR_PLATE[2] - v
    y = lambda v: v - TERROR_LINE                  # down from the spot's bottom, the plate's lower edge on it
    # the frame keeps Blizzard's size, its art 5 .. 507 across, from the spot's left
    for sd, pos, off in (("Left", "Min", -TERROR_ART[0]), ("Right", "Min", 530 - TERROR_ART[0]),
                         ("Top", "Max", y(0)), ("Bottom", "Max", y(150))):
        s.anchor("", sd, s.spot, pos, off)
    plate = "/MapMechanicStatus"
    l, t, r, b = TERROR_PLATE
    s.span(plate, x(r), x(l))
    s.anchor(plate, "Top", s.spot, "Max", y(t))
    s.anchor(plate, "Bottom", s.spot, "Max", y(b))
    s.flip(plate + "/MapMechanicStatusBG", faces="blue")
    for n in (1, 2, 3):
        bar = f"{plate}/TerrorHealthBarAnchorFrame{n}"
        # 65 in from the plate's outer end and 9 from the chevron on blue (Blizzard's); a status
        # bar's fill doesn't flip, so red's ends where its red does (TERROR_RED_IN)
        s.span(bar, s.pick(TERROR_RED_IN[n], 9), x(l + 65))
        s.drain(f"{bar}/TerrorUnitStatusFrame/HealthBar")
    left, width = TERROR_ICON
    for icon, team in (("Icon_Blue", "blue"), ("Icon_Red", "red")):
        s.hold(f"/{icon}", "Left", x(left + width), x(left))
        s.flip(f"/{icon}", faces="blue")
        s.show(f"/{icon}", team)


def terror_side():
    return team_banner("Terror", "$this", (f"{GARDEN}/FCJH_EventWarningFrameSpot",
                                            f"{GARDEN}/FCJH_GardenTerrorHealthFrameSpot"),
                       f'<When type="Property" frame="{GARDEN}/SeedsFrame/Team1StatusLabel" Visible="true"/>',
                       terror_layout, depth=0)


def terror_frame():
    """The Terrors' frame override: on red's spot to start (terror_side moves it), fade-only -
    a state moves it (FADE_ONLY)."""
    spot = f"{GARDEN}/FCJH_EventWarningFrameSpot"
    return ("".join(f'<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{spot}" pos="{pos}" offset="{off}"/>\n'
                    for sd, pos, off in (("Left", "Min", -TERROR_ART[0]), ("Right", "Min", 530 - TERROR_ART[0]),
                                         ("Top", "Max", -TERROR_LINE), ("Bottom", "Max", 150 - TERROR_LINE)))
            + '<Unclipped val="true"/>\n' + intro(0, slide=False) + terror_side())


# ------------------------------------------------------------------ Dragon Shire's banners

# "Shrines activate in: 0:02" (core MapMechanicPanel, DragonShirePanel/ShrineTimerModeFrame),
# built as the mines' (user, 2026-10-09: "move that spawn banner to the right"): its hexagon
# (CenterpieceImage, the dragonstone) pinned to the frame's top-right, 10 in; the bar ending 10
# past it, starting 35 before its words, the count right-aligned in the 50 before the hexagon -
# Blizzard sizes it to its words, growing left. Measured at 1080p (2026-10-09, at Blizzard's
# place, the panel's top-right at 1184, 718): the bar 382 px from its tip to its end in English,
# its lower bracket 113 units under the frame's top (y 820); the hexagon's bottom 835. On red's
# side laid out from its left end (left_banner), the words 35 in.
SHRINE_BOX = (-432, 0, 0, 113)
SHRINE_WORDS_START = 35
SHRINE_HEX_AFTER = 121     # the hexagon's right from the count's (measured: 112 px from the count's
                           # last letter to its box's right, less the label's padding, as the mines')
ALERT_ART["SHRINE"] = Art(SHRINE_BOX[2] - SHRINE_BOX[0], 0, height=130)   # down to the hexagon's bottom
SHRINE_BANNER = left_banner("Shrine", "ShrineActivateLabel", "ShrineActivateTimer", "CenterpieceImage",
                            SHRINE_WORDS_START, SHRINE_HEX_AFTER)


# ------------------------------------------------------------------ Warhead Junction's banner

# "Warheads deployed in: 0:14", then "Warheads available: 3 left" (scmap2.stormlayout,
# SC2Panel/TerrazineEruptionFrame; libmsc2.galaxy MMSC2UISetMode): one neutral banner, centred
# over the minimap by Blizzard - to red's side as it is (user, 2026-10-15: "Since this doesnt
# have a red/blue system, we can probably move the alert to the neutral red-side"; "the default
# banner just being moved shouldnt require any word or translation changes"). Blizzard's bar
# grows left with its words from the frame's right, its hexagon (TimerImage) 12 in from there:
# the box is its English countdown's, so that tip lands on red's plates; other words reach
# their own length from the same right end. Measured at Blizzard's place (2026-10-15, 08eeb21 at
# 1080p; the frame's bottom-right worked out at 1184, 747): the bar 768-1182, its lower bracket
# 724 (25 units over the frame's bottom), the hexagon 652-746.
WARHEAD_BOX = (-460, 20, 0, 126)
ALERT_ART["WARHEAD"] = Art(WARHEAD_BOX[2] - WARHEAD_BOX[0], 0, bar_up=25, below=25,
                           height=WARHEAD_BOX[3] - WARHEAD_BOX[1])
def nuke_sensor():
    """The nuke counters' trigger (warhead_counters), in this banner's "N LEFT" label, which the
    script shows only while warheads are out (NukesActive, libmsc2 MMSC2UISetMode). The counters
    come before the banner in the panel, so they can't watch it (rules 34, 38): the sensor sends
    across. The label is visible in Blizzard's layout until the first countdown hides it, so ours
    starts hidden, or the sensor would fire at load."""
    return ('<Visible val="false"/>\n'
            '<Frame type="Frame" name="FCJH_NukeSensor">\n'
            '\t<Anchor relative="$parent"/>\n'
            '\t<AcceptsMouse val="false"/>\n'
            '\t<StateGroup name="FCJH_Nukes">\n'
            '\t\t<DefaultState val="Off"/>\n'
            '\t\t<State name="On">\n'
            '\t\t\t<When type="Property" frame="$parent" Visible="true"/>\n'
            + "".join(f'\t\t\t<Action type="SendEvent" frame="$parent/$parent/$parent/Team{n}TerrazineFrame" event="FCJH_NukesOn"/>\n'
                      for n in (1, 2)) +
            '\t\t</State>\n'
            '\t\t<State name="Off"/>\n'
            '\t</StateGroup>\n'
            '</Frame>')


WARHEAD_PARTS = (("Image", "BackgroundImage", ()), ("Image", "TimerImage", ()),
                 ("Label", "EruptionInfoLabel", ()), ("Label", "EruptionTimerLabel", ()),
                 ("Label", "EruptionQuantityLabel", (), nuke_sensor()))
# The Dragon Knight (DragonModeFrame, shown instead once a team holds both shrines): Blizzard pins
# its bar's bottom-right to the countdown's bar's, the dragon's head (DragonHud), its timer and
# health bar all hanging off its bar. Ours from the spot's left, as the golems': its bar at its
# texture's own width (481, as the golems'; measured 432 px), its bottom still on the countdown's.
# Its timer (how long the knight lasts) hung under the dragon's head, below the bar - up beside
# the % instead, on the "DRAGON KNIGHT" row, in that row's small style (user, 2026-10-09).
DRAGON_TIMER_GAP, DRAGON_TIMER_W = -8, 80  # its right this far from the %'s box's left (the %'s
                                           # figures start there: at 8 its last digit ran ~2 px into
                                           # the %; -2 left ~7 px, user: 5 px more); its width
_ROW = "$parent/DragonInfoLabel"
_PCT_BOX = "$parent/DragonHealthBar/HealthLabel"
DRAGON_TIMER = "\n".join((
    f'<Anchor side="Top"    relative="{_ROW}" pos="Min" offset="0"/>',
    f'<Anchor side="Bottom" relative="{_ROW}" pos="Max" offset="0"/>',
    f'<Anchor side="Right"  relative="{_PCT_BOX}" pos="Min" offset="{DRAGON_TIMER_GAP}"/>',
    f'<Anchor side="Left"   relative="{_PCT_BOX}" pos="Min" offset="{DRAGON_TIMER_GAP - DRAGON_TIMER_W}"/>',
    '<Style val="Storm_MapMechanic_MechanicCounterSmallRight_Blue"/>'))
# Drawn over the dragon's head, as in Blizzard's order - and over blue's copy of it (KNIGHT_COPIES),
# which, being ours, comes after them (siblings at the default 512 draw in order)
_OVER = '<RenderPriority val="513"/>'
DRAGON_PARTS = (("Image", "BackgroundImage", (), f'<Anchor side="Right" relative="$parent" pos="Min" offset="{GOLEM_BAR}"/>'),
                ("Image", "HealthBarBG", ()), ("Image", "DragonHud", ()),
                ("Label", "DragonTimer", (), DRAGON_TIMER + "\n" + _OVER), ("Label", "DragonInfoLabel", (), _OVER),
                ("UnitStatusFrame", "DragonHealthBar", _HEALTH, _OVER))
# The knight on its team's side (user, 2026-10-09: "like Curse"): red's on red's side as above,
# blue's on blue's spot, mirrored - the bar ending at blue's inner edge, the dragon's head at its
# outer end (flipped), "DRAGON KNIGHT" at the inner end, the % then the timer from the outer.
# It's one frame for either team, and to an observer it says the same: the team is told by the
# shrine markers (ShrineModeFrame), hidden while the knight is up but left as they stood - the
# script sets each team's lit moon and star only while the shrines are up (mapmechanicslib MM
# Gardens dragon UI loop), so the knight's team is the one with both lit (Team1 is blue). The
# head and its health bar's backing are images with only one side anchored (their own size),
# so blue's are copies of ours, the other side anchored; the labels move and change alignment.
SHIRE = MECHANICS + "/DragonShirePanel"
KNIGHT = SHIRE + "/DragonModeFrame"
KNIGHT_COPIES = (
    flipped_copy("FCJH_KnightBarBG", "@UI/HUD_MapMechanic_BG_HealthBar",
                 (("Top", "$parent/BackgroundImage", "Mid", 5), ("Right", "$parent/BackgroundImage", "Max", -12)))
    + flipped_copy("FCJH_KnightHead", "@UI/HUD_MapMechanic_DragonShire_DragonHUD",
                   (("Top", "$parent/BackgroundImage", "Min", -43), ("Left", "$parent/BackgroundImage", "Min", -30))))
# Blue's health bar mirrored. Its fill is a parallelogram leaning \ at both ends (Blizzard's art)
# and a status bar won't flip it - TextureCoords on it did nothing (2026-10-09; Blizzard ships a
# second texture where it needs a bar mirrored, and the dragon's has none). So blue's is widened
# by the lean at each end and masked to the / parallelogram red's would make flipped: the mask
# spans the bar's frame, and the bar drains by cropping (a flat end), so the cut ends hold.
# Measured at 1080p (2026-10-09): the fill's ends lean ~6 px over its 10 px height.
KNIGHT_LEAN = 7            # units
KNIGHT_OUTER_TRIM = 2      # units more off the outer (left) end: cut at the lean alone it sat 2-3 px
                           # past the backing's slanted edge (user, 2026-10-09: "a bit more trim"), 4
                           # sat inside it - but red's own fill overshoots its backing there (Blizzard's),
                           # and blue's mimics red's (user): half back. The inner end was right
KNIGHT_BAR_H = 11          # units: Blizzard's HealthBar Height
TEXTURES = "_Assets\\Textures"   # gen.TEXTURE_DIR
WHITE = TEXTURES + "\\FCJH_White.dds"   # gen.WHITE: an opaque mask, for red's


def knight_mask(sub=4):
    """The / parallelogram over blue's widened bar (width 360 + 2 leans), as alpha:
    -> (width, height, BGRA rows). Texels at the art's 1440p scale, as gen's (1.2 per unit)."""
    width = 360 + 2 * KNIGHT_LEAN
    w, h = math.ceil(width * 1.2), math.ceil(KNIGHT_BAR_H * 1.2)
    rows = bytearray()
    for ty in range(h):
        for tx in range(w):
            cover = 0.0
            for s in range(sub):
                down = (ty + (s + 0.5) / sub) / h
                left = ((2 - down) * KNIGHT_LEAN + KNIGHT_OUTER_TRIM) / width * w   # 2 leans in at the top, 1 at the bottom
                right = (width - (1 + down) * KNIGHT_LEAN) / width * w
                cover += max(0.0, min(tx + 1, right) - max(tx, left))
            rows += bytes((255, 255, 255, round(255 * cover / sub)))
    return w, h, bytes(rows)


KNIGHT_MASK = knight_mask()
KNIGHT_MASK_FILE = f"FCJH_KnightMask_{hashlib.sha1(KNIGHT_MASK[2]).hexdigest()[:8]}.dds"
KNIGHT_MASK_PATH = TEXTURES + "\\" + KNIGHT_MASK_FILE


KNIGHT_PCT_W = 58         # the health %'s box (Blizzard's HealthLabel, its own width)
SMALL = "Storm_MapMechanic_MechanicCounterSmall{}_Blue"


def knight_layout(s):
    """The Dragon Knight, red's terms (team_banner): the bar its art's own width from the tip, the
    dragon's head at its outer end, "DRAGON KNIGHT" from the inner, the % then the timer from the
    outer; the health draining from the tip's end (Blizzard never sets Expansion from a state;
    a state's takes - 2026-10-09). Blue's head and backing are flipped copies (KNIGHT_COPIES)."""
    s.box("", SHRINE_BOX)
    s.hold("/BackgroundImage", "Right", -BAR_TIP_IN, GOLEM_BAR - BAR_TIP_IN)
    for part, team in (("/DragonHud", "red"), ("/HealthBarBG", "red"),
                       ("/FCJH_KnightHead", "blue"), ("/FCJH_KnightBarBG", "blue")):
        s.show(part, team)
    bg, bar, pct = s.pick("/HealthBarBG", "/FCJH_KnightBarBG"), "/DragonHealthBar/HealthBar", "/DragonHealthBar/HealthLabel"
    s.anchor(bar, "Top", bg, "Min", 5)
    # the bar 8 in from the backing's end, 360 long; blue's fill can't flip, so it's widened by the
    # lean at each end and cut to the mirrored lean (KNIGHT_MASK) - its box a lean further out
    s.hang(bar, "Left", bg, "Min", s.pick(8, 8 + KNIGHT_LEAN), width=360)
    s.set(bar, Width=s.pick(360, 360 + 2 * KNIGHT_LEAN), AlphaMaskTexture=s.pick(WHITE, KNIGHT_MASK_PATH))
    s.drain(bar)
    for sd, pos, off in (("Bottom", "Min", 2), ("Left", "Min", 15), ("Right", "Max", -15)):
        s.anchor("/DragonInfoLabel", sd, bg, pos, off)          # the backing's ends, 15 in
    s.justify("/DragonInfoLabel", SMALL, "inner")
    s.hang(pct, "Right", bar, "Max", s.pick(-3, -3 - KNIGHT_LEAN), width=KNIGHT_PCT_W)
    s.justify(pct + "/StatusLabel", SMALL, "inner")
    s.hang("/DragonTimer", "Right", pct, "Min", DRAGON_TIMER_GAP)
    s.hang("/DragonTimer", "Left", pct, "Min", DRAGON_TIMER_GAP - DRAGON_TIMER_W)
    s.justify("/DragonTimer", SMALL, "outer")


def knight_side():
    return team_banner("Knight", KNIGHT, (f"{SHIRE}/FCJH_ShrineTimerModeFrameSpot", f"{SHIRE}/FCJH_DragonModeFrameSpot"),
                       "".join(f'<When type="Property" frame="{SHIRE}/ShrineModeFrame/Team1{s}ShrineEnabled" Visible="true"/>'
                               for s in ("Moon", "Star")), knight_layout)


# ------------------------------------------------------------------ Blackheart's Bay's banners

# "Chests have spawned" (core MapMechanicPanel, BlackheartsBayPanel/ChestSpawnFrame): the
# tribute's build - the hexagon (the chest) 20 in from the frame's top-right, the bar its art's
# own width (481) ending 15 past it, the words in the bar. The neutral banner on red's side, as
# the tribute (user, 2026-10-12). Measured at 1080p (2026-10-12, at Blizzard's place): the
# chest's top 691, the bar's lower bracket 776 (94 units), the chest's bottom 794; the bar
# 435 px tip to end. Its left as the tribute's, the tip on red's plates.
CHEST_BOX = (-489, 0, -5, 94)
ALERT_ART["CHEST"] = Art(CHEST_BOX[2] - CHEST_BOX[0], 0, height=114)     # down to the chest's bottom
# Its bar is Blizzard's fixed-width image, anchored by its right end only: the intro's bar grow
# moves a Left anchor, so it had none to move (user, 2026-10-12: neither banner animated). Drawn
# as the cannon's is - the same art, a nine-slice from the frame's left (CANNON_PARTS).
CHEST_PARTS = (("Image", "BackgroundImage", (),
                f'<Anchor side="Left" relative="$parent" pos="Min" offset="-{BAR_TIP_IN}"/>\n'
                '<TextureType val="Nineslice"/>'),
               ("Image", "ChestImage", ()), ("Label", "ChestInfoLabel", ()))
# Blackheart's cannon (CannonModeFrame, in the chests' place while a team's cannonballs last): on
# the firing team's side (user, 2026-10-12), like the Dragon Knight - red's on red's spot, blue's
# on blue's, mirrored. Blizzard's own tell: the script shows the firing team's shots count
# (Team1ShotCounter blue, Team2 red) to everyone and hides the other (libbbay
# ShowCannonballForTeam); its "cannonballs remaining" label colours itself by it. Its art: the
# cannon's hexagon 15 down and 20 in from the frame's top-right, the bar (a nine-slice) from the
# frame's left to 15 past the hexagon, its bottom on the chests' bar's; twelve cannonball pips
# chained left from the hexagon (42 wide, 30 apart), the words and count above the bar. Its
# bar measured 461 px (516 units) tip to end at Blizzard's place (2026-10-12), the first pip
# 14 in from its tip. From the spot's left on red, as the mines' (the chests' box is too
# narrow for twelve pips): the bar CANNON_BAR long, the hexagon at its right end.
CANNON_BAR = 518
BAY = MECHANICS + "/BlackheartsBayPanel"
CANNON = BAY + "/CannonModeFrame"
CANNON_PARTS = ((("Image", "BackgroundImage", (), f'<Anchor side="Left" relative="$parent" pos="Min" offset="{-BAR_TIP_IN}"/>'),
                 ("Image", "CenterpieceImageCannon", (),
                  f'<Anchor side="Right" relative="$parent" pos="Min" offset="{-BAR_TIP_IN + CANNON_BAR - 15}"/>'),
                 ("Label", "Team1ShotCounter", ()), ("Label", "Team2ShotCounter", ()), ("Label", "CannonballsLeftLabel", ()))
                + tuple(("Frame", f"CannonShotFrame{n}", ()) for n in range(1, 13)))
# Blue's: the cannon flipped (our copy) at the outer end, the pips chained right from it; the
# words and count ours too (bound to Blizzard's, blue's colour), after the hexagon - Blizzard's
# words are a fixed box, right-aligned before the count.
CANNON_COPIES = (
    flipped_copy("FCJH_CannonHex", "@UI/HUD_MapMechanic_BlackheartsBay_Cannon",
                 (("Top", "$parent", "Min", 15), ("Left", "$parent/BackgroundImage", "Min", 15)))
    + "".join(
        f'{T*7}<Frame type="Label" name="{name_}">\n'
        f'{T*8}<Anchor side="Top"    relative="$parent/Team1ShotCounter" pos="Min" offset="0"/>\n'
        f'{T*8}<Anchor side="Bottom" relative="$parent/Team1ShotCounter" pos="Max" offset="0"/>\n'
        f'{T*8}<Anchor side="Left"   relative="{rel}" pos="Max" offset="{off}"/>\n'
        f'{T*8}<Text val="{{$parent/{theirs}/@Text}}"/>\n{T*8}<Style val="{{$parent/{theirs}/@Style}}"/>\n'
        f'{T*8}<ColorAdjustMode val="Colorize"/>\n{T*8}<LightAdjustColor val="#ColorWhite"/>\n'
        f'{T*8}<DarkAdjustColor val="{{$GameUI/TeamOrderColors/@Color}}"/>\n'
        f'{T*8}<GlowColor val="{{$GameUI/TeamOrderColors/@Color}}"/>\n'
        f'{T*8}<Options val="NoWrapping"/>\n{T*8}<Unclipped val="true"/>\n{T*8}<Alpha val="0"/>\n{T*7}</Frame>\n'
        for name_, theirs, rel, off in (("FCJH_CannonText", "CannonballsLeftLabel", "$parent/FCJH_CannonHex", 10),
                                        ("FCJH_CannonCount", "Team1ShotCounter", "$parent/FCJH_CannonText", 2))))


CANNON_SHOT_W = 42        # a cannonball pip's box


def cannon_layout(s):
    """Blackheart's cannon, red's terms (team_banner): the bar CANNON_BAR long from the tip, the
    cannon at its outer end (Blizzard's 15 in, CANNON_PARTS; blue's a flipped copy), the twelve
    pips chained in from it (the first 3 inside it, then 12 apart, Blizzard's)."""
    s.box("", CHEST_BOX)
    s.span("/BackgroundImage", -BAR_TIP_IN, CANNON_BAR - BAR_TIP_IN)
    hexagon = s.pick("/CenterpieceImageCannon", "/FCJH_CannonHex")
    for n in range(1, 13):
        s.hang(f"/CannonShotFrame{n}", "Right", hexagon if n == 1 else f"/CannonShotFrame{n - 1}", "Min",
               3 if n == 1 else 12, width=CANNON_SHOT_W)
    for part in ("/CenterpieceImageCannon", "/CannonballsLeftLabel", "/Team1ShotCounter", "/Team2ShotCounter"):
        s.show(part, "red")
    for part in ("/FCJH_CannonHex", "/FCJH_CannonText", "/FCJH_CannonCount"):
        s.show(part, "blue")


def cannon_side():
    return team_banner("Cannon", CANNON, (f"{BAY}/FCJH_ChestSpawnFrameSpot", f"{BAY}/FCJH_CannonModeFrameSpot"),
                       f'<When type="Property" frame="{CANNON}/Team1ShotCounter" Visible="true"/>', cannon_layout)


# The skull counts (HauntedMinesPanel/SkullModeFrame), shown while the mines are open. Their
# team-coloured line (the TeamHighlight backgrounds, everything else pinned to them) crossed the
# mines' map: lowered SKULL_LINE_DOWN, to just under the map's bottom (at 1080p the line 1048,
# the map's bottom 1060; user, 2026-10-09), the skulls and counts kept where they were.
# The skulls still needed ("55 Needed", SkullsRemainingLabel) sat between them on the line:
# moved between the surface and the mines, on a plaque of Blizzard's bar art - its pointed ends make the
# elongated hexagon (user) - sized for the longest language ("Необходимо: 100").
SKULL_LINE_DOWN = 16       # units (14 px). That put the line wholly under its panel's box, which
                           # clipped it away (user, 2026-10-09: "we lost the line"): Unclipped
SKULL_PLAQUE_W = 200
# The plaque fills the gap between the two maps, centred in it (user, 2026-10-09), and rides with
# the minimap (its glide). Measured at 1080p: the surface's bottom 8 px above the drawn map's
# middle, the mines' top 35 below; the plaque 42 px tall (the art's own height, as the mines
# bar's: a Height of 50 drew it 30 px tall, its slices off). The drawn map's middle is the
# minimap square's (438 units, its half 219); 1 unit = 0.9 px.
SKULL_GAP_PX = (-8, 35)
SKULL_PLAQUE_DOWN_PX = -4  # centred in the gap (user, 2026-10-12). At 2 (2 under, by eye 2026-10-09) its
                           # middle read 922-923 at 1080p, the gap's 913-915 (the surface's bottom 893-894,
                           # the mines' top 932-937 under the hero icons): 8 up, then 2 back down by eye
# Its height: 28 px (user, 2026-10-09: the size a squeezed nine-slice drew, "about the size I
# want"). The art is a nine-slice 42 px tall: drawn shorter as one (a Height, or anchored top and
# bottom) its corners overlap and only the top bracket shows - Blizzard only ever draws it
# taller. So it's drawn as a plain image, the whole art stretched into the box.
SKULL_PLAQUE_H_PX = 28
SKULL_PLAQUE_ART_PX = 42   # the art's own height: Blizzard's bar words sit 5 under its middle
_MID = -219 + (sum(SKULL_GAP_PX) / 2 + SKULL_PLAQUE_DOWN_PX) / 0.9    # its middle, from the square's bottom
SKULL_PLAQUE_B = round(_MID + SKULL_PLAQUE_H_PX / 2 / 0.9)
SKULL_PLAQUE_T = round(_MID - SKULL_PLAQUE_H_PX / 2 / 0.9)
SKULL_WORDS_DOWN = round(5 * SKULL_PLAQUE_H_PX / SKULL_PLAQUE_ART_PX)
# The skulls and their counts, off the line (user, 2026-10-09, by eye): 2 px lower and 4 px in,
# towards the map, each side; the line stays. Blizzard's places across, from the line's outer
# end: blue's skull -5 and count 70 from its left, red's 5 and -72 from its right.
SKULLS_DOWN_PX, SKULLS_IN_PX = 2, 4
SKULL_ACROSS = {1: ("Left", "Min", -5, 70, 1), 2: ("Right", "Max", 5, -72, -1)}   # side, pos, skull, count, inward sign


def skulls_extra():
    t = T * 6
    line = lambda name_, kind, sd, off, rel="$parent", pos="Max", more="": (
        f'{t}\t<Frame type="{kind}" name="{name_}"><Anchor side="{sd}" relative="{rel}" pos="{pos}" offset="{off}"/>'
        + more + f'<Unclipped val="true"/></Frame>\n')
    mid = lambda sd, off: f'<Anchor side="{sd}" relative="$GameUI" pos="Mid" offset="{off}"/>'
    down, inward = round(SKULLS_DOWN_PX / 0.9), round(SKULLS_IN_PX / 0.9)
    def across(n, skull):
        sd, pos, s, c, sign = SKULL_ACROSS[n]
        return (f'<Anchor side="{sd}" relative="$parent/Team{n}Background" pos="{pos}" '
                f'offset="{(s if skull else c) + sign * inward}"/>')
    return (f'{t}<!-- the skull counts\' line under the mines\' map; the skulls needed above it (maps.skulls_extra) -->\n'
            f'{t}<Frame type="Frame" name="SkullModeFrame">\n'
            + line("Team1Background", "Image", "Bottom", SKULL_LINE_DOWN)
            + line("Team2Background", "Image", "Bottom", SKULL_LINE_DOWN)
            + "".join(line(f"Team{n}Skull", "Image", "Bottom", 10 - SKULL_LINE_DOWN + down, f"$parent/Team{n}Background",
                           more=across(n, True))
                      + line(f"Team{n}SkullCounter", "Label", "Bottom", -10 - SKULL_LINE_DOWN + down,
                             f"$parent/Team{n}Background", more=across(n, False))
                      for n in (1, 2))
            + f'{t}\t<Frame type="Image" name="FCJH_SkullsPlaque">\n'
            f'{t}\t\t<Anchor side="Bottom" relative="{MINIMAP}" pos="Max" offset="{SKULL_PLAQUE_B}"/>\n'
            f'{t}\t\t<Anchor side="Top"    relative="{MINIMAP}" pos="Max" offset="{SKULL_PLAQUE_T}"/>\n'
            f'{t}\t\t{mid("Left", -SKULL_PLAQUE_W // 2)}\n{t}\t\t{mid("Right", SKULL_PLAQUE_W // 2)}\n'
            f'{t}\t\t<Texture val="@UI/HUD_MapMechanic_BG_CenterBar"/>\n'
            f'{t}\t\t<RenderPriority val="500"/>\n{t}\t\t<Unclipped val="true"/>\n{t}\t</Frame>\n'
            # its words centred on it, as Blizzard's bar words sit (Mid +5 on the art's own height)
            f'{t}\t<Frame type="Label" name="SkullsRemainingLabel">\n'
            f'{t}\t\t<Anchor side="Top"    relative="$parent/FCJH_SkullsPlaque" pos="Mid" offset="{SKULL_WORDS_DOWN}"/>\n'
            f'{t}\t\t<Anchor side="Bottom" relative="$parent/FCJH_SkullsPlaque" pos="Mid" offset="{SKULL_WORDS_DOWN}"/>\n'
            f'{t}\t\t{mid("Left", 0)}\n{t}\t\t{mid("Right", 0)}\n'
            f'{t}\t\t<Unclipped val="true"/>\n{t}\t</Frame>\n'
            f'{t}</Frame>\n')


# ------------------------------------------------------------------ Alterac Pass's banner

# One frame (AlteracMechanicsPanel/AVMechanicContainer, the map file's), three things in turn:
# "Prisoners located in: 0:28" (neutral), the cage fight (both teams' bars; neutral) and the
# cavalry's health (the team that won the cage: TeamWins, 1 Order = blue, 2 Chaos = red; 0
# between). The neutral two stay at Blizzard's place, above the minimap; once the cage is won
# its outro plays there and the cavalry appears on its team's side (user, 2026-10-12, having
# watched it on red's side a few times). Measured at 1080p (2026-10-12, at Blizzard's place: the
# frame's right 1184, its middle 748): the bar's bracket tips 730 and 1163, the prisoners' hexagon
# out to 1170, its lower bracket 773.5; the cavalry's hammers up to 684. On the spots (2026-10-12):
# red's tip 1167, blue's 755, both lower brackets 930.
# Not mirrored (a technical limitation, user 2026-10-12: "not the end of the world"): Blizzard's
# own animations slide its parts - the hexagon 373 left when the cage starts, the cage bars and
# the cavalry's plate and fill-up in from the left - each counted from its layout anchor, so no
# state can move or mirror them (storminterface-layout-rules 28). Moving the WHOLE banner works:
# its layout anchors hang off a carrier of ours, and only the carrier moves (av_carrier).
# Blue's cavalry comes out Blizzard's way round - blue's mirror, the hexagon at the outer end; red's
# keeps its hexagon at the inner end, by the minimap. The full mirror would rewrite those slides
# and flip the cage's ProgressBars (no Blizzard bar fills right to left): HANDOFF.
AV_BOX = (-504, -21, -16, 78)   # the art from the frame's top-right: the left tip, the hammers,
                                # the hexagon's right, the lower bracket
ALERT_ART["AV"] = Art(AV_BOX[2] - AV_BOX[0], 0, height=AV_BOX[3] - AV_BOX[1])
AV_HALF_H = 50                  # half Blizzard's frame (Height 100), centred on its Top/Bottom anchor
AV_MID = 245                    # Blizzard's frame's middle under its panel's (alteracmechanics)
AV_HANDOFF_S = 0.6              # the cage won ("MechanicDone"), its bars are gone and the cavalry's
                                # plate shows 0.6 s on, sliding in from there: the carrier moves then
AV_PARK = 2000                  # units down: off the screen's bottom (av_parkers)
TEAM_WINS = {"Blue": 1, "Red": 2}
# Its panel is a strip up the minimap's right (1000 wide) and clips what it holds: red's spot is
# past it. Unclipped on the frame let it draw there, but it also took the clipping from inside it -
# the cage bars' fill: their team-coloured backing slid along with the fill instead of standing
# the bar's length (user, 2026-10-13, against the default UI). So the strip is widened instead, its
# right AV_PANEL_GROW further right (past red's spot) and 200 more to the left (blue's), and what
# Blizzard places from its right is placed back where it was.
AV_PANEL_GROW = 600
AV_PANEL_W = 1000 + AV_PANEL_GROW + 200


def av_neutral(down):
    """The carrier at Blizzard's place: (its right from MinimapPanel's right, its bottom from
    MinimapPanel's bottom), units - gen.py works the moves to the spots out from it. down: the
    panel's [minimap.panel_nudge], units."""
    m = MAPS["alterac_pass"]
    sides = {sd: on_minimap(sd, pos, off, m, down)[1] for sd, pos, off in m.panels["AlteracMechanicsPanel"]}
    return (sides["Right"] - AV_PANEL_GROW + AV_BOX[2],
            (sides["Top"] + sides["Bottom"]) / 2 + AV_MID + AV_BOX[3] - AV_HALF_H)


def av_carrier():
    """The carrier the banner hangs off: at Blizzard's place (av_neutral), the art's box; the cage
    won, it jumps to the winner's spot AV_HANDOFF_S on, by #FCJH_MAP_AV_<TEAM>_DX/_DY (gen.py) - a
    relative Anchor controller, held there (end Pause) until the next round puts it back (Reset).
    The banner hangs off it through two parkers (av_parkers), which hide it meanwhile."""
    l, tp, r, b = AV_BOX
    out = (f'<Anchor side="Right"  relative="$parent" pos="Max" offset="{r - AV_PANEL_GROW}"/>\n'
           f'<Anchor side="Bottom" relative="$parent" pos="Mid" offset="{AV_MID + b - AV_HALF_H}"/>\n'
           f'<Width val="{r - l}"/>\n<Height val="{b - tp}"/>\n<AcceptsMouse val="false"/>\n')
    for team in TEAM_WINS:
        out += (f'<Animation name="FCJH_To{team}">\n\t<Event event="FCJH_{team}" action="Restart,Play"/>\n'
                + "".join(f'\t<Event event="FCJH_{other}" action="Reset"/>\n'
                          for other in ("Neutral", *TEAM_WINS) if other != team))
        for sd, d in (("Right", "DX"), ("Bottom", "DY")):
            out += (f'\t<Controller type="Anchor" end="Pause" side="{sd}" relative="true">\n'
                    f'\t\t<Key type="Curve" time="0" value="0"/>\n'
                    f'\t\t<Key type="Curve" time="{AV_HANDOFF_S}" value="0"/>\n'
                    f'\t\t<Key type="Curve" time="{AV_HANDOFF_S + 0.01}" value="#FCJH_MAP_AV_{team.upper()}_{d}"/>\n'
                    f'\t</Controller>\n')
        out += '</Animation>\n'
    when = lambda team: f'<When type="AnimationState" frame="$parent/AVMechanicContainer" TeamWins="{TEAM_WINS[team]}"/>'
    send = lambda event: f'<Action type="SendEvent" frame="$this" event="FCJH_{event}"/>'
    blink = '<Action type="SendEvent" frame="$parent/FCJH_AVBlink" event="FCJH_Won"/>'
    return (out + '<StateGroup name="FCJH_AVSide">\n\t<DefaultState val="Neutral"/>\n'
            + "".join(f'\t<State name="{team}">{when(team)}{send(team)}{blink}</State>\n' for team in TEAM_WINS)
            + f'\t<State name="Neutral">{send("Neutral")}</State>\n</StateGroup>\n')


def av_parkers():
    """Between the carrier and the banner, two frames that park it off the screen's bottom
    (AV_PARK; user, 2026-10-13 - "completely hide the neutral when a side completes the event"):
    FCJH_AVBlink from the cage's win until the carrier lands on the winner's spot (no outro above
    the minimap, no jump across: it read as a staggered movement), and FCJH_AVSlain from the
    cavalry's death ("CavalrySlain") until the next round's "Show" (the script resets TeamWins
    and fades the banner 5 s after the death: the carrier went home and the slain line faded out
    above the minimap). Each its own frame, each animation's first key 0, so a Reset, whatever
    it holds, never leaves the banner parked. -> {path: xml} for PARTS."""
    l, tp, r, b = AV_BOX
    av = "$parent/AVMechanicContainer"

    def parker(on, name_, events, keys):
        return ("".join(f'<Anchor side="{sd}" relative="$parent/{on}" pos="Max" offset="0"/>\n'
                        for sd in ("Right", "Bottom"))
                + f'<Width val="{r - l}"/>\n<Height val="{b - tp}"/>\n<AcceptsMouse val="false"/>\n'
                + f'<Animation name="{name_}">\n'
                + "".join(f'\t<Event event="{e}" action="{a}"' + (f' frame="{f}"' if f else "") + '/>\n'
                          for e, a, f in events)
                + '\t<Controller type="Anchor" end="Pause" side="Bottom" relative="true">\n'
                + "".join(f'\t\t<Key type="Curve" time="{t}" value="{v}"/>\n' for t, v in keys)
                + '\t</Controller>\n</Animation>\n')
    return {"AlteracMechanicsPanel/FCJH_AVBlink":
                parker("FCJH_AVCarrier", "FCJH_Blink", [("FCJH_Won", "Restart,Play", "")],
                       [(0, 0), (0.001, AV_PARK), (AV_HANDOFF_S, AV_PARK), (AV_HANDOFF_S + 0.01, 0)]),
            "AlteracMechanicsPanel/FCJH_AVSlain":
                parker("FCJH_AVBlink", "FCJH_Slain", [("CavalrySlain", "Restart,Play", av), ("Show", "Reset", av)],
                       [(0, 0), (0.001, AV_PARK)])}


# The cage's hexagon lights one half - "who's winning" (TeamWinningCage), set to whichever team
# channelled first - so with both teams capturing, only that team's half shows lit (Blizzard's
# own, seen in Ahli's too; user, 2026-10-13). The bars say each team's capture apart
# (TopBarCaptured: Order's, BottomBarCaptured: Chaos's, in the everyone view; "10" capturing,
# "11" contested): with both on, our copies of both lit halves and their glows draw over
# Blizzard's darkened half. Copies, not Blizzard's images, so no state of ours fights theirs.
AV_ICON = "AlteracMechanicsPanel/AVMechanicContainer/Team0Icon/IconContainer/FCJH_BothLit"
AV_LIT = (("FCJH_OrderLit", "Order", "TimerBGNeutralAlliance", False),
          ("FCJH_ChaosLit", "Chaos", "TimerBGNeutralHorde", False),
          ("FCJH_OrderGlow", "Order", "TimerBGGlowAlliance", True),
          ("FCJH_ChaosGlow", "Chaos", "TimerBGGlowHorde", True))


def av_both_lit():
    av = "$parent/$parent/$parent"          # AVMechanicContainer, from the copies' frame
    states = "".join(f'\t<State name="Both{t}{b}"><When type="AnimationState" frame="{av}" TopBarCaptured="{t}"/>'
                     f'<When type="AnimationState" frame="{av}" BottomBarCaptured="{b}"/>'
                     '<Action type="SetProperty" frame="$this" Visible="true"/></State>\n'
                     for t in ("10", "11") for b in ("10", "11"))
    colours = '{$ancestor[@name=AlteracMechanicsPanel]/UnitStatusColorContainer/Team%s%sColors/@Color}'
    out = {AV_ICON: ('<Anchor relative="$parent"/>\n<AcceptsMouse val="false"/>\n<Visible val="false"/>\n'
                     '<StateGroup name="FCJH_BothCapturing">\n\t<DefaultState val="One"/>\n' + states
                     + '\t<State name="One"><Action type="SetProperty" frame="$this" Visible="false"/></State>\n'
                     '</StateGroup>\n')}
    for name_, team, texture, glow in AV_LIT:
        out[f"{AV_ICON}/{name_}:Image"] = (
            '<Anchor relative="$parent"/>\n<ColorAdjustMode val="Colorize"/>\n'
            + ('<BlendMode val="Add"/>\n' if glow else "")
            + f'<DarkAdjustColor val="{colours % (team, "Dark")}"/>\n'
            f'<LightAdjustColor val="{colours % (team, "Light")}"/>\n'
            f'<Texture val="@UI/Storm_UI_HUD_WCAV_{texture}"/>\n<AcceptsMouse val="false"/>\n'
            + ('<Animation name="FCJH_Pulse">\n\t<Event event="OnShown" action="Restart,Play"/>\n'
               '\t<Event event="OnShown" action="Restart,Play" frame="$parent"/>\n'
               '\t<Controller type="Fade" end="PingPong">\n'
               + "".join(f'\t\t<Key type="Curve" time="{k}" value="{v}" inout="Linear,Fast"/>\n'
                         for k, v in ((0, 255), (0.5, 127), (1, 255)))
               + '\t</Controller>\n</Animation>\n' if glow else ""))
    return out


def av_frame():
    """Blizzard's frame on the carrier (through the parkers), its art on the carrier's box (AV_BOX)."""
    l, tp, r, b = AV_BOX
    mid = AV_HALF_H - b                 # its middle, from the carrier's bottom (the art's)
    return "".join(f'<Anchor side="{sd}" relative="$parent/FCJH_AVSlain" pos="Max" offset="{off}"/>\n'
                   for sd, off in (("Top", mid), ("Bottom", mid), ("Right", -r)))


# The flag-capture alerts (NotificationFrame1, 2 - the script fills 2 while 1 shows) go to the
# side their event names (user, 2026-10-13: Alliance's on blue's, Horde's on red's), on that
# side's stack, one slot up per banner already there: the cavalry, and for 2, 1. Each hangs off
# a carrier of ours (FCJH_CampSlot1, 2) that states move - Blizzard's intro slides it relative to
# its layout anchors, the carrier's (av_carrier's way). Their art: AVNotificationFrameTemplate,
# 500 x 184, placed by its frame's bottom-right as Towers' (""): measured 2026-10-13 off the
# default UI (alert 1, its frame's right 1 in from the screen's, bottom 10 over the cage
# banner's): the bracket tip 509 back, the hexagon's right 18 short, the bar's bottom 21 up,
# the hexagon 15 under it. Not mirrored on blue's side - one frame serves both teams, and the
# intro's relative slide on its art would undo a state's mirror: the hexagon at blue's inner end.
ALERT_ART["CAMP"] = Art(509, 18, bar_up=21, below=15, height=91)
CAMP_TEAMS = {"Blue": (11, 12), "Red": (21, 22)}   # EventID: the captor's team, then the camp's
# Their words are a player's ("Allies capturing enemy camp"); an observer's screen shows blue's
# (user, 2026-10-13, everyone view: blue's capture read "Allies", red's "Enemies"). Ours name the
# side: Blizzard's sentences, only "Allies" / "Enemies" (and "allied" / "enemy") swapped for
# Alliance (Order, blue) and Horde (Chaos, red), as the map has them (user, 2026-10-14: "we're
# observers, we shouldn't have allies or enemies"). The team is the alert's own event (its
# EventID, which picks its icon and colours: 1x Order's doing, 2x Chaos's; x2 / x1 the other's
# camp / its own), so it holds in a player's view too; Blizzard's words only say which kind of
# event it is. Ours are English in every language (camp_words).
CAMP_WORDS = {   # EventID: (ours - Blizzard's: "Allies/Enemies capturing enemy/allied camp", "... retook their camp"; the colour)
    12: ("Alliance capturing Horde camp", "TeamOrderColors"),
    21: ("Horde capturing Alliance camp", "TeamChaosColors"),
    11: ("Alliance retook their camp", "TeamOrderColors"),
    22: ("Horde retook their camp", "TeamChaosColors"),
}
CAMP_STYLE = "Storm_MapMechanic_MechanicTimerCentered_Blue"   # Blizzard's label's (NotificationFrameTemplate)


def av_bars():
    """The cage bars' strip (ProgressBarsContainer). Blizzard's: Left at the art's Mid -210, Right
    at Mid +218, Width 463 - in ours it came out 891 wide (seen 2026-10-13, av_diag: each side
    its anchor -/+ half the width), the bars starting far left under the mask, which hid their
    start, the timers and red's stub. Both sides on one point, as the art and the mask: centred
    there, 463 wide - Blizzard's span exactly (-227.5 .. +235.5). The slide-in (MapMechanicActive,
    MechanicDone) moves both sides alike, so it holds."""
    mid = (-210 + 218) // 2
    return "".join(f'<Anchor side="{sd}" relative="$parent/$parent/BackgroundImage" pos="Mid" offset="{mid}"/>\n'
                   for sd in ("Left", "Right"))


def camp_slot(i, at=("$GameUI", "Mid", "Max")):
    """Alert i's carrier (CAMP_TEAMS above): on its team's side, a slot up for the cavalry there
    and, for 2, for 1 showing there. States most-conditions first; the first that holds wins."""
    place = lambda team, up: (
        f'<Action type="SetAnchor" frame="$this" side="Right" relative="{at[0]}" pos="{at[1]}" '
        f'offset="#FCJH_MAP_ALERT_{team.upper()}_R_CAMP"/>'
        f'<Action type="SetAnchor" frame="$this" side="Bottom" relative="{at[0]}" pos="{at[2]}" '
        f'offset="#FCJH_MAP_ALERT_{team.upper()}_B_CAMP{f"_{up + 1}" if up else ""}"/>')
    states = []
    for team, events in CAMP_TEAMS.items():
        cavalry = (f'<When type="AnimationState" frame="$parent/AVMechanicContainer" TeamWins="{TEAM_WINS[team]}"/>'
                   '<When type="Property" frame="$parent/AVMechanicContainer" Visible="true"/>')
        below = [("", "")] + ([(f"Over1_{e}",
                                f'<When type="Property" frame="$parent/NotificationFrame1" Visible="true"/>'
                                f'<When type="AnimationState" frame="$parent/NotificationFrame1" EventID="{e}"/>')
                               for e in events] if i == 2 else [])
        for event in events:
            mine = f'<When type="AnimationState" frame="$parent/NotificationFrame{i}" EventID="{event}"/>'
            for label, one in below:
                for cav in (cavalry, ""):
                    up = (one != "") + (cav != "")
                    states.append((up, f'{team}{event}{label}{"OverCavalry" * (cav != "")}',
                                   mine + one + cav + place(team, up)))
    states.sort(key=lambda s: -s[0])
    return (f'<Anchor side="Right"  relative="{at[0]}" pos="{at[1]}" offset="#FCJH_MAP_ALERT_RED_R_CAMP"/>\n'
            f'<Anchor side="Bottom" relative="{at[0]}" pos="{at[2]}" offset="#FCJH_MAP_ALERT_RED_B_CAMP"/>\n'
            '<Width val="1"/>\n<Height val="1"/>\n<AcceptsMouse val="false"/>\n'
            f'<StateGroup name="FCJH_CampSide">\n\t<DefaultState val="Waiting"/>\n'
            + "".join(f'\t<State name="{name_}">{xml}</State>\n' for _, name_, xml in states)
            + '\t<State name="Waiting"/>\n</StateGroup>\n')


def camp_frame(i):
    return "".join(f'<Anchor side="{sd}" relative="$parent/FCJH_CampSlot{i}" pos="Max" offset="0"/>\n'
                   for sd in ("Bottom", "Right"))


def camp_words(i):
    """Alert i's frame (NotificationFrame1, 2 - not their template: nothing added to
    AVNotificationFrameTemplate reached them, seen 2026-10-14 by a diagnostic): Blizzard's label
    hidden for good (nothing animates its visibility - the intro only fades it - and the script
    only writes its text), ours in its place in Blizzard's style, its words and team colour by
    the alert's event alone. Writing into Blizzard's label worked once, then the next alert's
    words came back (user, 2026-10-14: "the second volley reverted"): the script rewrites them,
    and a state already entered doesn't act again. The script never touches ours, so a repeat of
    the same event keeps them - seen over several rounds and after a fast-forward (user,
    2026-10-14). -> {path: xml} for PARTS."""
    frame = f"AlteracMechanicsPanel/NotificationFrame{i}"
    states = "".join(
        f'\t<State name="Event{event}"><When type="AnimationState" EventID="{event}"/>'
        f'<Action type="SetProperty" frame="$this/FCJH_CampText" Text="{ours}"/>'
        f'<Action type="SetProperty" frame="$this/FCJH_CampText" DarkAdjustColor="{{$GameUI/{colour}/@Color}}"/>'
        f'<Action type="SetProperty" frame="$this/FCJH_CampText" GlowColor="{{$GameUI/{colour}/@Color}}"/></State>\n'
        for event, (ours, colour) in CAMP_WORDS.items())
    label = ("".join(f'<Anchor side="{sd}" relative="$parent/NotificationLabel" pos="{pos}" offset="0"/>\n'
                     for sd, pos in (("Top", "Min"), ("Bottom", "Max"), ("Left", "Min"), ("Right", "Max")))
             + f'<Style val="{CAMP_STYLE}"/>\n<ColorAdjustMode val="Colorize"/>\n<LightAdjustColor val="#ColorWhite"/>\n'
             '<DarkAdjustColor val="{$parent/NotificationLabel/@DarkAdjustColor}"/>\n'
             # Blizzard's words until a state writes ours (a missed state shows theirs, not nothing)
             '<Text val="{$parent/NotificationLabel/@Text}"/>\n'
             '<AcceptsMouse val="false"/>\n')   # as the map's label (alteracmechanics AVNotificationFrameTemplate)
    return {frame: camp_frame(i) + '<StateGroup name="FCJH_CampWords">\n\t<DefaultState val="None"/>\n'
                   + states + '\t<State name="None"/>\n</StateGroup>\n',
            f"{frame}/NotificationLabel:Label": '<Visible val="false"/>\n',
            f"{frame}/FCJH_CampText:Label": label}


PARTS["alterac_pass"] = {"AlteracMechanicsPanel": f'<Width val="{AV_PANEL_W}"/>\n',
                         "AlteracMechanicsPanel/FCJH_AVCarrier": av_carrier(),
                         **av_parkers(),
                         "AlteracMechanicsPanel/AVMechanicContainer": av_frame(),
                         "AlteracMechanicsPanel/AVMechanicContainer/ProgressBarMasker/ProgressBarsContainer": av_bars(),
                         **av_both_lit(),
                         "AlteracMechanicsPanel/FCJH_CampSlot1": camp_slot(1),
                         "AlteracMechanicsPanel/FCJH_CampSlot2": camp_slot(2),
                         **camp_words(1), **camp_words(2)}


# "CONTESTED!" above the payload's hexagon, not under it (user, 2026-10-14) - the escort counts
# that sit there are hidden while it's contested (hanamurarework Payload_Contested)
PARTS["hanamura_temple"] = {"HanamuraReworkActivePaylaodStatusPanel/HanamuraPayloadContestedFrame": "".join(
    f'<Anchor side="{sd}" relative="$parent/ActivePayloadImageNeutral" pos="Min" offset="{off}"/>\n'
    for sd, off in (("Top", -38), ("Bottom", -2)))}


# ------------------------------------------------------------------ Volskaya Foundry

MINIMAP_SQUARE = "$parent/$parent/$parent/MinimapPanel/Minimap"   # as Blizzard's anchors name it
VOLSKAYA = MECHANICS + "/VolskayaCapturePointPanel"
# "Control point will unlock" (VolskayaToastContainer, the map's own toast): in our banners' font
# (Blizzard's banner words, MechanicTimerCentered_Blue; user, 2026-10-15: "standardize the font
# with the others"), its countdown in the bar after the words as Cursed Hollow's (Blizzard hangs
# it under the hexagon). Blizzard's bar is sized to its words, the hexagon at its right end: ours
# keeps that, the words ending one space before the count's slot where Blizzard's ended, the bar
# starting the standard 35 before them. Blizzard's labels hidden, ours bound to them.
TOAST_WORDS_START = 35
TOAST_RIGHT = 29           # the toast's right end this far right of Blizzard's (units; 26 px)
# English's sentence measured 320 wide (13_33_27: words 719 px, count 1006.5 px): the bar's right
# end half that left of its words' copy's middle keeps English where 44b79a7 centred it
TOAST_CENTRE = -160
TOAST_SLOT = 53            # the count's slot and the space before it: the bar without them halves it
TOAST_STYLE = "Storm_MapMechanic_MechanicTimerCentered_Blue"
_TOAST_ROW = (("Top", "$parent/BackgroundImage", "Mid", 4), ("Bottom", "$parent/BackgroundImage", "Mid", 4))
_TOAST_COUNT = "$parent/TimerLabel"
# "Control Point Will Unlock", in every language the game ships (volskayamechanics gamestrings:
# Param/Value/lib_VLSK_81009092, what the script shows, and UI/MapMechanic/Volskaya/
# ControlPointWillUnlock, the layout's - French and Taiwanese differ) -> a sentence to go before the count, as the
# tribute's (TRIBUTE_SPAWNS_IN; user, 2026-10-15: "Control Point Will Unlock in: 00:xx"):
# Blizzard's words for the point, worded as that language's "TEMPLE ACTIVATES IN:" (Sky Temple,
# lib_MLCP_6037C0FB) and "MINES WILL OPEN IN:" (UI/MapMechanics/MinesOpen) are, colon or not.
VOLSKAYA_UNLOCKS_IN = {
    "Control Point Will Unlock": "Control Point Will Unlock In:",
    "Kontrollpunkt wird verfügbar": "Kontrollpunkt verfügbar in",
    "Punto de control activándose": "Punto de control activo en:",
    "El punto de control se activará": "El punto de control se activará en:",
    "Déblocage du point de contrôle": "Déblocage du point de contrôle dans :",
    "Le point de contrôle va bientôt être débloqué": "Point de contrôle débloqué dans :",
    "Attivazione punto di conquista": "Punto di conquista attivo fra:",
    "거점 해제": "거점 해제:",
    "Odblokowanie punktu": "Punkt odblokuje się za:",
    "Ponto de Controle ativará em": "Ponto de Controle ativará em:",
    "Объект активируется": "Объект активируется через",
    "控制点将会解锁": "控制点解锁还剩：",
    "平台即將解鎖": "平台即將解鎖：",
    "控制平台即將解鎖": "控制平台即將解鎖：",
}


def toast_sentence():
    """FCJH_VolskayaSentence's states: shown, Blizzard's words (ours, copied) hidden and the bar
    from the sentence, while the count shows and the words are a language's listed; else hidden.
    And the bar centred whatever its words' length (user, 2026-10-15): its right end hangs from
    the middle of a hidden copy of the words shown (FCJH_VolskayaSentenceWidth/TextWidth), held
    by its left - half their width out - so the bar grows both ways. Anchors name frames by path:
    relative="$this" left the bar where it was (seen 2026-10-15)."""
    alpha = lambda frame, a: f'<Action type="SetProperty" frame="{frame}" Alpha="{a}"/>'
    anchor = lambda side, rel, pos, off: (f'<Action type="SetAnchor" frame="$parent/BackgroundImage" side="{side}" '
                                          f'relative="{rel}" pos="{pos}" offset="{off}"/>')
    bar = lambda frame: anchor("Left", frame, "Min", -TOAST_WORDS_START)
    centre = lambda width, off=TOAST_CENTRE: anchor("Right", width, "Mid", off)
    words, sentence = "$parent/FCJH_VolskayaText", "$parent/FCJH_VolskayaSentence"
    return ('\t<StateGroup name="FCJH_Sentence">\n\t\t<DefaultState val="Words"/>\n'
            + "".join(f'\t\t<State name="In{i}"><When type="Property" frame="{_TOAST_COUNT}" Visible="true"/>'
                      f'<When type="Property" frame="$parent/InfoLabel" Text="{theirs}"/>'
                      f'<Action type="SetProperty" frame="{sentence}" Text="{ours}"/>'
                      f'<Action type="SetProperty" frame="{sentence}Width" Text="{ours}"/>'
                      + alpha(sentence, 255) + alpha(words, 0) + bar(sentence) + centre(sentence + "Width") + '</State>\n'
                      for i, (theirs, ours) in enumerate(VOLSKAYA_UNLOCKS_IN.items()))
            # no count: the bar shorter by its slot and the space before it
            + f'\t\t<State name="Bare"><When type="Property" frame="{_TOAST_COUNT}" Visible="false"/>'
            + alpha(sentence, 0) + alpha(words, 255) + bar(words)
            + centre(words + "Width", TOAST_CENTRE - TOAST_SLOT // 2) + '</State>\n'
            + '\t\t<State name="Words">' + alpha(sentence, 0) + alpha(words, 255) + bar(words)
            + centre(words + "Width") + '</State>\n'
            '\t</StateGroup>\n')


def toast_width(name_, text):
    """A hidden copy of the toast's words, its left at the toast's right (toast_sentence)."""
    return banner_label(name_, _TOAST_ROW + (("Left", "$parent", "Max", 0),), text, TOAST_STYLE, '\t<Alpha val="0"/>\n')


TOAST = "".join((
    # the bar grows left from its right end (Blizzard's, the minimap panel's right): English's
    # sentence put its middle 26 px left of the screen's (13_33_27, bar 690-1178) - moved over.
    # Every language centred by the bar's right end (toast_sentence), from these hidden copies
    f'<Anchor side="Right" relative="$parent" pos="Max" offset="{TOAST_RIGHT}"/>\n',
    toast_width("FCJH_VolskayaTextWidth", "{$parent/InfoLabel/@Text}"),
    toast_width("FCJH_VolskayaSentenceWidth", ""),
    banner_label("FCJH_VolskayaText", _TOAST_ROW + (("Right", "$parent/FCJH_VolskayaSlot", "Min", -COUNT_SPACE),),
                 "{$parent/InfoLabel/@Text}", TOAST_STYLE),
    # its count reads "00:22" (GetFormattedTimeRemaining), wider than our banners' "8:88"
    count_slot("FCJH_VolskayaSlot", _TOAST_ROW, ("Right", "$parent/BackgroundImage", "Max", -140), TOAST_STYLE,
               slot="88:88"),
    # no countdown (Blizzard's hidden): the words end where Blizzard's did
    banner_label("FCJH_VolskayaCount", _TOAST_ROW + (("Right", "$parent/FCJH_VolskayaSlot", "Max", 0),),
                 f"{{{_TOAST_COUNT}/@Text}}", TOAST_STYLE,
                 '\t<StateGroup name="FCJH_Counting">\n\t\t<DefaultState val="Counting"/>\n'
                 f'\t\t<State name="Bare"><When type="Property" frame="{_TOAST_COUNT}" Visible="false"/>'
                 '<Action type="SetProperty" frame="$this" Alpha="0"/>'
                 '<Action type="SetAnchor" frame="$parent/FCJH_VolskayaText" side="Right" '
                 'relative="$parent/BackgroundImage" pos="Max" offset="-140"/></State>\n'
                 '\t\t<State name="Counting"><Action type="SetProperty" frame="$this" Alpha="255"/>'
                 '<Action type="SetAnchor" frame="$parent/FCJH_VolskayaText" side="Right" '
                 f'relative="$parent/FCJH_VolskayaSlot" pos="Min" offset="{-COUNT_SPACE}"/></State>\n'
                 '\t</StateGroup>\n'),
    # while it counts, in a language listed: our sentence over the words (VOLSKAYA_UNLOCKS_IN),
    # ending where they end, the bar's left end moved out to it
    banner_label("FCJH_VolskayaSentence", _TOAST_ROW + (("Right", "$parent/FCJH_VolskayaText", "Max", 0),),
                 "", TOAST_STYLE, '\t<Alpha val="0"/>\n' + toast_sentence()),
    '<Frame type="Image" name="BackgroundImage">\n'
    f'\t<Anchor side="Left" relative="$parent/FCJH_VolskayaText" pos="Min" offset="{-TOAST_WORDS_START}"/>\n'
    '</Frame>\n',
    '<Frame type="Label" name="InfoLabel">\n\t<Alpha val="0"/>\n</Frame>\n',
    '<Frame type="Label" name="TimerLabel">\n\t<Alpha val="0"/>\n</Frame>\n'))

# The capture point (user, 2026-10-15): "CONTESTED" above the hexagon, as Hanamura's, and gone
# in overtime - the overtime banner says it ("that's the definition of overtime"), above the hex.
CONTESTED = (
    '<Anchor side="Top"    relative="$parent/CenterHex" pos="Mid" offset="-89"/>\n'
    '<Anchor side="Bottom" relative="$parent/CenterHex" pos="Mid" offset="-39"/>\n')
# ...hidden from the robot's frame: the script builds the capture panel before the overtime panel,
# and a <When> naming a frame not yet built never fires (seen 2026-10-15, CONTESTED under OVERTIME).
# The robot's frame is built last, and a hidden frame's StateGroup still runs (layout rule 30).
CONTESTED_OVERTIME = (
    '<StateGroup name="FCJH_Overtime">\n\t<DefaultState val="Normal"/>\n'
    f'\t<State name="Overtime"><When type="Property" frame="{MECHANICS}/VolskayaOvertimePanel" Visible="true"/>'
    f'<Action type="SetProperty" frame="{VOLSKAYA}/ContestedLabel" Alpha="0"/></State>\n'
    f'\t<State name="Normal"><Action type="SetProperty" frame="{VOLSKAYA}/ContestedLabel" Alpha="255"/></State>\n'
    '</StateGroup>\n')

# The Triglav Protector's health (VolskayaRobotHealthSlideout, its own frame: one, recoloured for
# the team that holds it - TeamColoringTemplate's RedBlue): a team banner (team_banner), on the
# owning team's side (user, 2026-10-15), its pilot, gunner and timer moved up over the bar.
# Measured at 1080p (2026-10-15, Blizzard's place, the minimap panel's right at 1184): the bar's
# image (storm_ui_hud_volskaya_objective_bg, as the toast's) 778-1166 x 675-719 - its tip 4 in, its
# lower bracket 3 over its bottom; the robot's art 1075-1180 x 620-728, the seats' rings 48 px
# inside their 72-unit boxes. Red's terms: x from the tip, y up from the lower bracket.
ROBOT = MECHANICS + "/VolskayaRobotHealthSlideout"
ROBOT_BAR = 431            # the bar's image across, units
ROBOT_TIP_IN = 4           # its tip this far in from the image's inner end
ROBOT_BAR_H = 49           # ...and its height, the lower bracket ROBOT_BRACKET over its bottom
ROBOT_BRACKET = 3
ROBOT_SEATS = 108          # the seats' boxes' top over the bracket (their rings' bottom ~2 over the plate)
# The seats at the outer end, beside the robot (the timer moved off them; user, 2026-10-15): the
# gunner's box out to here. Measured on blue (13_26_05): the robot's shoulder at seat height 339
# out from the tip, a seat's ring 4 inside its 72-unit box - so THE GAP between them.
ROBOT_SEATS_OUT = 339 - 11 + 4
ROBOT_TIMER_MID =ROBOT_BRACKET - ROBOT_BAR_H - 14   # the timer's middle: its digits' bottom ~5 px over the bar
ROBOT_BOX = (-447, 0, 0, 108)          # the robot's art's outer side, its top
# Blue's fill: Blizzard's TextureCoordinateProgressBar slides only its mask (layer 0) - mirroring
# its coords drained it from blue's tip, but the colour layer's stripes stayed red's slant against
# blue's flipped plate (2026-10-15), and a state can't set one layer's coords. So blue's side has
# its own: the same bar, its coords mirrored, its colour layer flipped and read from Blizzard's.
_FILL = "$parent/$parent/$parent/RobotHealthBar/FillImageContainer/FillImage/TexturePathStore"
ROBOT_BLUE_FILL = (
    '<Frame type="TextureCoordinateProgressBar" name="FCJH_BlueHealthBar">\n'
    '\t<Anchor relative="$parent/Background" offset="0"/>\n'
    '\t<AcceptsMouse val="False"/>\n'
    '\t<MinValue val="0"/>\n'
    '\t<MaxValue val="{$parent/HealthValues/@MaxHealth}"/>\n'
    '\t<Value val="{$parent/HealthValues/@Health}"/>\n'
    '\t<NumSegments val="20"/>\n'
    '\t<UseFillContainer val="false"/>\n'
    '\t<MaxTextureCoords top="0" left="0.99" bottom="1" right="-0.01"/>\n'
    '\t<MinTextureCoords top="0" left="0.08" bottom="1" right="-0.92"/>\n'
    '\t<Unclipped val="true"/>\n'
    '\t<Alpha val="0"/>\n'
    '\t<Frame type="Frame" name="FillImageContainer">\n'
    '\t\t<Anchor relative="$parent"/>\n'
    '\t\t<Frame type="Image" name="FillImage">\n'
    '\t\t\t<Anchor relative="$parent"/>\n'
    '\t\t\t<RenderPriority val="800"/>\n'
    '\t\t\t<LayerCount val="2"/>\n'
    '\t\t\t<Texture val="Assets\\Textures\\storm_ui_hud_volskaya_mech_health_mask.dds" layer="0"/>\n'
    '\t\t\t<AlphaLayer val="True" layer="0"/>\n'
    f'\t\t\t<Texture val="{{{_FILL}/@Text}}" layer="1"/>\n'
    '\t\t\t<TextureCoords top="0" left="1" bottom="1" right="0" layer="1"/>\n'
    '\t\t</Frame>\n'
    '\t</Frame>\n'
    '</Frame>')
ALERT_ART["ROBOT"] = Art(447, 0, height=121)   # down to the robot's bottom, 13 under the bracket
ROBOT_SPOTS = (f"{VOLSKAYA}/FCJH_VolskayaRobotHealthSlideoutSpot", f"{VOLSKAYA}/FCJH_VolskayaRobotBlueSpot")


def robot_layout(s):
    """The robot's banner, red's terms (team_banner): x out from the bar's tip. Every part hangs
    off the spot, not the frame - Blizzard's slide holds the frame's layout anchor (layout rule 28)."""
    bar = "/BackgroundImage"
    s.span(bar, -ROBOT_TIP_IN, ROBOT_BAR - ROBOT_TIP_IN)
    s.anchor(bar, "Top", s.spot, "Max", ROBOT_BRACKET - ROBOT_BAR_H)
    s.flip(bar)
    # Blizzard's: the robot 40 past the bar's outer end, 164 across; the health plate 68 in, 272
    # across; the % 16 in, 70 across
    end = ROBOT_BAR - ROBOT_TIP_IN
    s.hold("/RobotIcon", "Right", end + 40 - 164, end + 40)
    for part in ("/RobotIcon", "/DeathIcon1", "/DeathIcon2", "/DeathIcon3"):
        s.flip(part)
    plate = "/RobotStatusFrame/Background"
    s.hold(plate, "Left", 68 - ROBOT_TIP_IN, 68 - ROBOT_TIP_IN + 272)
    s.flip(plate)
    s.hold("/RobotStatusFrame/HealthLabel", "Left", 16 - ROBOT_TIP_IN, 16 - ROBOT_TIP_IN + 70)
    # the fill: Blizzard's on red's side, blue's own copy on blue's (ROBOT_BLUE_FILL)
    s.show("/RobotStatusFrame/FCJH_BlueHealthBar", "blue")
    s.show("/RobotStatusFrame/RobotHealthBar", "red")
    # over the bar's outer end: the pilot, the gunner, then the robot (ROBOT_SEATS_OUT). Each
    # seat's ring and border are separate images (the border Blizzard's template copy of the
    # ring, its anchors too); the pilot's top follows the gunner's (Blizzard's)
    for part in ("/GunnerEmptyIcon", "/GunnerBorderIcon"):
        s.anchor(part, "Top", s.spot, "Max", -ROBOT_SEATS)
        s.hold(part, "Right", ROBOT_SEATS_OUT - 72, ROBOT_SEATS_OUT)
    for part in ("/PilotEmptyIcon", "/PilotBorderIcon"):
        s.hold(part, "Right", ROBOT_SEATS_OUT - 144, ROBOT_SEATS_OUT - 72)
    # the timer over the % at the tip's end, just over the bar's top (user, 2026-10-15). Its
    # style centres it; its digits ~16 px tall (Blizzard's zero-width label centred on the robot
    # drew nothing here: given a width)
    s.at("/RobotTimer", "Left", 16 - ROBOT_TIP_IN)
    s.at("/RobotTimer", "Right", 16 - ROBOT_TIP_IN + 70)
    s.anchor("/RobotTimer", "Top", s.spot, "Max", ROBOT_TIMER_MID - 20)
    s.anchor("/RobotTimer", "Bottom", s.spot, "Max", ROBOT_TIMER_MID + 20)


ROBOT_PARTS = (("Image", "BackgroundImage", ()), ("Image", "RobotIcon", ()),
               ("Image", "DeathIcon1", ()), ("Image", "DeathIcon2", ()), ("Image", "DeathIcon3", ()),
               ("Label", "RobotTimer", ()),
               ("UnitStatusFrame", "RobotStatusFrame", (
                   ("Image", "Background", ()),
                   ("TextureCoordinateProgressBar", "RobotHealthBar", (
                       ("Frame", "FillImageContainer", (("Image", "FillImage", ()),)),)),
                   ("UnitStatusHealthLabel", "HealthLabel", (("Label", "StatusLabel", ()),))),
                ROBOT_BLUE_FILL),
               ("Image", "GunnerEmptyIcon", ()), ("Image", "GunnerPlayerIcon", ()), ("Image", "GunnerBorderIcon", ()),
               ("Image", "PilotEmptyIcon", ()), ("Image", "PilotPlayerIcon", ()), ("Image", "PilotBorderIcon", ()))


def robot_frame():
    """The robot's frame override: on red's spot to start (its team_banner moves the parts), the
    box the art's. Blizzard's own slide and fade kept: its parts hang off the spots, not the frame."""
    l, tp, r, b = ROBOT_BOX
    return ("".join(f'<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{ROBOT_SPOTS[0]}" pos="{pos}" offset="{off}"/>\n'
                    for sd, pos, off in box_sides(ROBOT_BOX))
            + f'<Width val="{r - l}"/>\n<Height val="{b - tp}"/>\n<Unclipped val="true"/>\n'
            + unclipped(ROBOT_PARTS, 0) + CONTESTED_OVERTIME
            + team_banner("Robot", "$this", ROBOT_SPOTS,
                          f'<When type="StateGroup" frame="{ROBOT}/RobotStatusFrame/RobotColorizeFrame" RedBlue="Blue"/>',
                          robot_layout, depth=0))


# The Immortals' fight (BossDuelLeft/RightFrame, the template Braxis's zerg HUD uses): "IMMORTALS
# FIGHTING" (PhaseLabel) above the bars, where Braxis's "BEACON PROGRESS" sits (user, 2026-10-15:
# "like the other maps") - Blizzard hangs it under them, over the map
PHASE_ABOVE = '<Frame type="Label" name="PhaseLabel"><Anchor side="Top" relative="$parent/BackgroundImage" pos="Min" offset="-15"/></Frame>'
PARTS["battlefield_of_eternity"] = {"BossDuelPanel/BossDuelLeftFrame": PHASE_ABOVE,
                                    "BossDuelPanel/BossDuelRightFrame": PHASE_ABOVE}

# Its three phases are three frames of BossDuelPanel, one shown at a time (libMLBD MMBOEUISetMode),
# split up as Dragon Shire's (user, 2026-10-15): "Immortals spawning 0:27" (BossSpawnFrame) the
# neutral banner on red's side; the fight stays above the minimap; the winner's Immortal pushing
# (BossLaningFrame) in its place, on the winning team's side, mirrored on blue's (lane_side).
# Measured at 1080p (13_48_24, 13_50_25; the frames' top-right at 1184.1, 622.8): the countdown's
# tip 732, its lower bracket 773 (167 under the frame's top), the wings' top 689, its hexagon's
# bottom 790, its sword's right 1175; the lane box's lower bracket 773 too (they take turns in
# one place), its tip 737 - its bar the golems' 481 units, the portrait 8 in from its right end.
SPAWN_BOX = (-502, 74, -10, 167)
SPAWN_WORDS_START = 55     # Blizzard's: the bar 55 before its words
SPAWN_HEX_AFTER = 180      # the incoming portrait's right from the count's (165 px from the count's
                           # last glyph, 1028, to its box's right, 1193 - Blizzard's 10 past the frame's
                           # - less the label's padding, as the shrine's)
ALERT_ART["SPAWN"] = Art(SPAWN_BOX[2] - SPAWN_BOX[0], 0, height=114)   # the hexagons' bottom, 188 (790, 792)
SPAWN_BANNER = (left_banner("Spawn", "InfoLabel", "TimerLabel", "BossLaningHudAngelImage",
                            SPAWN_WORDS_START, SPAWN_HEX_AFTER)
                + unclipped((("Image", "BossLaningHudDemonImage", ()),)))   # on the angel, as Blizzard's

BOE = MECHANICS + "/BossDuelPanel"
LANE = BOE + "/BossLaningFrame"
LANE_SPOTS = (f"{BOE}/FCJH_BossSpawnFrameSpot", f"{BOE}/FCJH_BossLaningFrameSpot")
LANE_DEMON_R = GOLEM_BAR - BAR_TIP_IN - 8    # the portrait's right out from the tip: 8 short of the bar's end
# What the lane label says to an observer when it's BLUE's Immortal, preparing then attacking, in
# every language the game ships (heroesdata gamestrings, lib_MLBD_2C3736B5 / 89ACF292): the text
# is all that tells the teams apart (the curse's protocol, BLUE_CURSED)
BLUE_IMMORTAL = (
    "Blue Team Immortal Preparing", "Blue Team Immortal Is Attacking",
    "Ilarian wappnet sich", "Ilarian greift an",
    "Preparando inmortal: equipo azul", "El inmortal del equipo azul ataca",
    "El Inmortal del equipo azul se está preparando", "El Inmortal del equipo azul está atacando",
    "L’Immortel de l’équipe bleue se prépare", "L’Immortel de l’équipe bleue attaque",
    "Immortale della squadra blu in preparazione", "L'immortale della squadra blu attacca",
    "파랑팀 불멸자 준비 중", "파랑팀 불멸자 공격 중",
    "Nieśmiertelny niebieskich przygotowuje się", "Nieśmiertelny niebieskich atakuje",
    "O Imortal da Equipe Azul está se preparando", "O Imortal da Equipe Azul está atacando",
    "Бессмертный синей команды готовится к бою", "Бессмертный синей команды атакует",
    "蓝队不朽者正在准备中", "蓝队不朽者正在攻击",
    "藍隊的不朽戰士正在準備", "藍隊的不朽戰士正在攻擊")
# Blue's backings, flipped copies as the knight's (KNIGHT_COPIES): Blizzard's are held by their
# left. The shield's is upside down too, as Blizzard's. And blue's portraits' boxes: invisible
# copies of the portraits themselves (their own size, which nothing here knows), mirroring red's -
# the demon's left where red's right is, the angel 4 short of the demon's other end (Blizzard's
# angel 4 in from the demon's left, flipped). Blizzard's portraits are held by one side, and the
# script fades them (the winner's in): they're moved onto these, not copied.
LANE_COPIES = (
    flipped_copy("FCJH_LaneShieldBG", "@UI/HUD_MapMechanic_BG_HealthBar",
                 (("Bottom", "$parent/BackgroundImage", "Mid", 5), ("Right", "$parent/BackgroundImage", "Max", -13)),
                 coords='<TextureCoords top="1.0" left="1.0" bottom="0.0" right="0.0"/>')
    + flipped_copy("FCJH_LaneHealthBG", "@UI/HUD_MapMechanic_BG_HealthBar",
                   (("Top", "$parent/BackgroundImage", "Mid", 5), ("Right", "$parent/BackgroundImage", "Max", -13)))
    + flipped_copy("FCJH_LaneDemonBox", "@UI/hud_minimap_boe_portrait_demon_blue",
                   (("Top", "$parent", "Min", 75), ("Left", LANE_SPOTS[1], "Max", -LANE_DEMON_R)))
    + flipped_copy("FCJH_LaneAngelBox", "@UI/hud_minimap_boe_portrait_angel_blue",
                   (("Top", "$parent", "Min", 75), ("Right", "$parent/FCJH_LaneDemonBox", "Max", -4)))
    # blue's words: Blizzard's label is restyled by the script as it writes them (libmlbd.galaxy
    # SetDialogItemStyle ...SmallLeft_Blue), which beats a state's Style, so blue's stayed
    # left-justified (14_38_47). Ours, right-justified from the tip, shows Blizzard's words.
    + f'{T*7}<Frame type="Label" name="FCJH_LaneWords">\n'
    + "".join(f'{T*8}<Anchor side="{sd}" relative="{rel}" pos="{pos}" offset="{off}"/>\n'
              for sd, rel, pos, off in (("Bottom", "$parent/BackgroundImage", "Min", 10),
                                        ("Left", "$parent/AllyAngelHud", "Max", 0),
                                        ("Right", "$parent/BackgroundImage", "Max", -25)))
    + f'{T*8}<Style val="{SMALL.format("Right")}"/>\n'
    + f'{T*8}<Text val="{{$parent/BossLaningInfoLabel/@Text}}"/>\n'
    + f'{T*8}<Unclipped val="true"/>\n{T*8}<RenderPriority val="513"/>\n'
    + f'{T*8}<AcceptsMouse val="false"/>\n{T*8}<Alpha val="0"/>\n{T*7}</Frame>\n')
# What Blizzard draws after the backings drawn over blue's copies of them too, as the knight's
# (_OVER): the copies, being ours, come last and hid the fills (14_31_07)
LANE_PARTS = (("Image", "BackgroundImage", ()), ("Label", "BossLaningInfoLabel", (), _OVER),
              ("Image", "ShieldBarBg", ()), ("Image", "HealthBarBg", ()),
              ("UnitStatusFrame", "BossLaningShieldBar", (("UnitStatusShieldedHealthBar", "ShieldBar", ()),), _OVER),
              ("UnitStatusFrame", "BossLaningHealthBar", (("UnitStatusShieldedHealthBar", "HealthBar", ()),), _OVER),
              ("Image", "AllyDemonHud", (), _OVER), ("Image", "EnemyDemonHud", (), _OVER),
              ("Image", "AllyAngelHud", (), _OVER), ("Image", "EnemyAngelHud", (), _OVER))


def lane_layout(s):
    """The winner's Immortal pushing, red's terms (team_banner): the bar its art's own width from
    the tip, the portrait at its outer end, the words from the inner; the shield over the health,
    both draining from the tip's end. Blue's health fill is cut to the mirrored lean, as the
    knight's (KNIGHT_MASK); its shield's segments aren't."""
    s.box("", SPAWN_BOX)
    s.hold("/BackgroundImage", "Right", -BAR_TIP_IN, GOLEM_BAR - BAR_TIP_IN)
    # the portraits: the Enemy ones hang off the Ally ones (Blizzard's)
    if s.blue:
        s.anchor("/AllyDemonHud", "Right", "/FCJH_LaneDemonBox", "Max", 0)
        s.anchor("/AllyAngelHud", "Left", "/FCJH_LaneAngelBox", "Min", 0)
    else:
        s.anchor("/AllyDemonHud", "Right", s.spot, "Min", LANE_DEMON_R)
        s.anchor("/AllyAngelHud", "Left", "/AllyDemonHud", "Min", 4)
    for part in ("/AllyDemonHud", "/EnemyDemonHud"):
        s.flip(part)
    for part in ("/AllyAngelHud", "/EnemyAngelHud"):    # Blizzard's drawn flipped on red's
        s.flip(part, faces="blue")
    for part, team in (("/ShieldBarBg", "red"), ("/HealthBarBg", "red"),
                       ("/FCJH_LaneShieldBG", "blue"), ("/FCJH_LaneHealthBG", "blue"),
                       ("/BossLaningInfoLabel", "red"), ("/FCJH_LaneWords", "blue")):
        s.show(part, team)
    # the shield: its frame from its backing to under the portrait, the bar 354 long from its left
    sbg, shield = s.pick("/ShieldBarBg", "/FCJH_LaneShieldBG"), "/BossLaningShieldBar"
    s.anchor(shield, "Top", sbg, "Min", 4)
    s.hang(shield, "Left", sbg, "Min", 8)
    s.hang(shield, "Right", "/AllyDemonHud", "Min", 43)
    s.hang(shield + "/ShieldBar", "Left", shield, "Min", 0, width=354)
    s.drain(shield + "/ShieldBar")
    # the health: its frame from the bar's end to under the portrait, the fill 8 in from its
    # backing's end to 8 past the frame's; blue's a lean further out at each end, masked
    hbg, health = s.pick("/HealthBarBg", "/FCJH_LaneHealthBG"), "/BossLaningHealthBar"
    s.hang(health, "Left", "/BackgroundImage", "Min", 0)
    s.hang(health, "Right", "/AllyDemonHud", "Min", 58)
    bar = health + "/HealthBar"
    s.anchor(bar, "Top", hbg, "Min", 5)
    s.hang(bar, "Left", hbg, "Min", s.pick(8, 8 - KNIGHT_LEAN))
    s.hang(bar, "Right", health, "Max", s.pick(8, 8 + KNIGHT_LEAN))
    s.set(bar, AlphaMaskTexture=s.pick(WHITE, KNIGHT_MASK_PATH))
    s.drain(bar)


def lane_side():
    return team_banner("Lane", LANE, LANE_SPOTS,
                       [f'<When type="Property" frame="{LANE}/BossLaningInfoLabel" Text="{t}"/>' for t in BLUE_IMMORTAL],
                       lane_layout)


# ------------------------------------------------------------------ Infernal Shrines' banners

# "A shrine is activating" (ShrineWarningFrame), "Shrine active" (ShrineActiveFrame) and the
# Punisher (PunisherFrame) take turns in one place over the minimap (shrines.stormlayout,
# ShrinesPanel): the countdown the neutral banner on red's side ("Shrine active" hidden, below); the Punisher, one frame
# for either team, on the summoner's side, mirrored on blue's (punisher_side). Blizzard's: the
# hexagon (TimerImage, ActiveImage) 20 down and 20 in from the frame's top-right, the bar a fixed-
# width image ending 15 past it, the words centred in it and the count under the hexagon.
# Measured at 1080p (20_52_52, 3edae7a; the panel's top-right at about 1176, 605.5): the bar's
# tip 743, its top 718, its lower bracket 760 (173 under the frame's top); the hexagon 1067-1161,
# its top 697, its bottom 779. On red's side laid out from its left end (left_banner), the words
# 35 in, and the count up off the hexagon into the bar after them, in the words' style, as the
# tribute's (tribute_count): under the hexagon it hung onto the map.
SHRINES = MECHANICS + "/ShrinesPanel"
INFERNAL_BOX = (-483, 102, -5, 173)
INFERNAL_WORDS_START = 35
INFERNAL_HEX_AFTER = 118   # the hexagon's right from the count's: its art ~91 px left of its box's
                           # right, 12 px after the count, less the label's padding (as the shrine's)
INFERNAL_SLOT = "88:88"    # its count reads "00:27"
ALERT_ART["INFERNAL"] = Art(INFERNAL_BOX[2] - INFERNAL_BOX[0], 0,
                            height=INFERNAL_BOX[3] - INFERNAL_BOX[1] + 21)   # down to the hexagon's bottom
# Its bar is the fixed-width image, held by its right end: with our left end it's a nine-slice,
# as the chests' (CHEST_PARTS)
_NINESLICE = '<TextureType val="Nineslice"/>'
WARNING_BANNER = left_banner("ShrineWarning", "ShrineWarningInfoLabel", "ShrineWarningTimerLabel", "TimerImage",
                             INFERNAL_WORDS_START, INFERNAL_HEX_AFTER, slot=INFERNAL_SLOT,
                             count_style="{$parent/ShrineWarningInfoLabel/@Style}", bar=_NINESLICE)
# "Shrine active" (ShrineActiveFrame) hidden (user, 2026-10-15: the objective markers say it; it
# flickered on 61f1be5). Between the countdown and the skull race the script re-sets that mode
# every 0.25 s (libmshe.galaxy MMISUIHandler: its lastState never updates there), showing the
# panel again each time - the likely restart of the banner's intro. Alpha, not a park: its bar
# hangs off the warning's hexagon, not its own frame.
PARTS["infernal_shrines"] = {"ShrinesPanel/ShrineActiveFrame": '<Alpha val="0"/>\n'}
# The Punisher (PunisherFrame): Blizzard's bar (481, fixed) ends 10 past ShrineHud, a frame 111 x
# 124 at the frame's top-right, 20 in, the bar's bottom 33 over the hud's; the Punisher's portrait
# 26 over the hud, 8 past its right; the health backing (a nine-slice) from 12 in to 18 under the
# hud, the fill 8 in at each end. Measured at 1080p (20_53_22, Blizzard's place): the bar's tip
# 738, its top 643, its lower bracket 683 - 4 px over the image's bottom (687, worked out); the
# portrait's art 1068-1172, centred on the hud - so its image is 127 wide, 8 past the hud each side.
# Ours as the knight's: the bar from the tip, the portrait at its outer end, the words from the
# inner, the % from the outer; its lower bracket on the spot's bottom, as the warning's.
PUNISHER = SHRINES + "/PunisherFrame"
PUNISHER_HUD = (357, 468)  # the hud's sides out from the tip: its outer 10 short of the bar's end
PUNISHER_HUD_TOP = -86     # its top from the spot's bottom: 124 tall, the bar's image 33 over its
                           # bottom and the lower bracket 5 over the image's
PUNISHER_ICONS = tuple(f"/Punisher{k}{t}" for k in ("Arcane", "Frozen", "Mortar") for t in ("Ally", "Enemy"))
# Blue's health backing, a flipped copy as the knight's (KNIGHT_COPIES), from 18 under the hud to
# 12 in from the bar's end - stretched (Blizzard's a nine-slice; its own width is about this)
PUNISHER_COPIES = flipped_copy("FCJH_PunisherBarBG", "@UI/HUD_MapMechanic_BG_HealthBar",
                               (("Top", "$parent/BackgroundImage", "Mid", 5),
                                ("Left", "$parent/ShrineHud", "Max", -18),
                                ("Right", "$parent/BackgroundImage", "Max", -12)))
# What Blizzard draws after the backing drawn over blue's copy too (_OVER)
PUNISHER_PARTS = ((("Image", "BackgroundImage", ()), ("Image", "HealthBarBG", ()), ("Frame", "ShrineHud", ()))
                  + tuple(("Image", icon[1:], (), _OVER) for icon in PUNISHER_ICONS)
                  + (("Label", "PunisherInfoLabel", (), _OVER),
                     ("UnitStatusFrame", "PunisherHealthBar", _HEALTH, _OVER)))


def punisher_layout(s):
    """The Punisher, red's terms (team_banner): the bar its art's own width from the tip, the
    portrait at its outer end (flipped on blue's), the words from the inner end, the % from the
    outer; the health draining from the tip's end, blue's cut to the mirrored lean (KNIGHT_MASK)."""
    s.box("", INFERNAL_BOX)
    s.hold("/BackgroundImage", "Right", -BAR_TIP_IN, GOLEM_BAR - BAR_TIP_IN)   # its bottom hangs off the hud
    s.hold("/ShrineHud", "Right", *PUNISHER_HUD)
    s.anchor("/ShrineHud", "Top", s.spot, "Max", PUNISHER_HUD_TOP)
    # the portraits: the others fill the first's box (Blizzard's), 8 past the hud each side
    s.anchor(PUNISHER_ICONS[0], "Left", "/ShrineHud", "Min", -8)
    s.anchor(PUNISHER_ICONS[0], "Right", "/ShrineHud", "Max", 8)
    for icon in PUNISHER_ICONS:
        s.flip(icon)
    s.show("/HealthBarBG", "red")
    s.show("/FCJH_PunisherBarBG", "blue")
    hbg, health = s.pick("/HealthBarBG", "/FCJH_PunisherBarBG"), "/PunisherHealthBar"
    s.anchor(health, "Left", hbg, "Min", 0)
    s.anchor(health, "Right", hbg, "Max", 0)
    bar = health + "/HealthBar"
    s.anchor(bar, "Top", hbg, "Min", 5)
    s.hang(bar, "Left", hbg, "Min", s.pick(8, 8 - KNIGHT_LEAN))
    s.hang(bar, "Right", hbg, "Max", s.pick(-8, -8 + KNIGHT_LEAN))
    s.set(bar, AlphaMaskTexture=s.pick(WHITE, KNIGHT_MASK_PATH))
    s.drain(bar)
    for sd, pos, off in (("Bottom", "Min", 2), ("Left", "Min", 15), ("Right", "Max", -15)):
        s.anchor("/PunisherInfoLabel", sd, hbg, pos, off)       # the backing's ends, 15 in
    s.justify("/PunisherInfoLabel", SMALL, "inner")
    pct = health + "/HealthLabel"
    s.hang(pct, "Right", bar, "Max", s.pick(-15, -15 - KNIGHT_LEAN), width=KNIGHT_PCT_W)
    s.justify(pct + "/StatusLabel", SMALL, "inner")


def punisher_side():
    """The Punisher on its summoner's side. The script hides all six portraits, then shows the
    observer the Ally one if the summoner is Order (blue), the Enemy one if not (libmshe.galaxy):
    blue's while an Ally portrait shows. A player's view is per team - red's players' Ally is
    red's - so in a red player's view red's Punisher goes to blue's side."""
    return team_banner("Punisher", PUNISHER, (f"{SHRINES}/FCJH_ShrineWarningFrameSpot", f"{SHRINES}/FCJH_PunisherFrameSpot"),
                       [f'<When type="Property" frame="{PUNISHER}{icon}" Visible="true"/>'
                        for icon in PUNISHER_ICONS if icon.endswith("Ally")],
                       punisher_layout)


# ------------------------------------------------------------------ Sky Temple's banner

# "Temples activate in: 0:04" (TimerModeFrame), then "Capture the Temples" - the same frame, its
# timer hidden (libmlcp.galaxy MMSkyTempleUISetMode: Timer mode shows the time label, Temple mode
# hides it). Blizzard's (capturepoints.stormlayout): the hexagon (CenterpieceImage, the temple)
# at the frame's top, 20 in from its right; the bar ending 15 past it, starting 35 before its
# words, its bottom 11 under them - Blizzard sizes it to its words, growing left. Measured at
# 1080p (22_00_38, 3227b64, Blizzard's place): the bar's tip 784, its other tip 1175, its top
# 628, its lower bracket 668; the hexagon 1067-1164, its top ~606, its bottom 683 - so the
# frame's top-right about 1182, 606. On red's side laid out from its left end (left_banner),
# the words 35 in. The frame's top isn't the hexagon's visible top (the image's top is clear
# above it): 69 units down put the bar's lower bracket at 956, against every banner's 930 (the
# core bar's top 940, less 10) - 22_18_43, c7e5da1; so 26 px (29 units) further down.
TEMPLE = MECHANICS + "/CapturePointsPanel/TimerModeFrame"
TEMPLE_BOX = (-444, 0, -5, 98)
TEMPLE_WORDS_START = 35
TEMPLE_HEX_AFTER = 115     # the hexagon's right from the count's: 106 px from its last letter, as the mines'
ALERT_ART["TEMPLE"] = Art(TEMPLE_BOX[2] - TEMPLE_BOX[0], 0, height=TEMPLE_BOX[3] - TEMPLE_BOX[1] + 17)   # down to the hexagon's bottom


def temple_banner():
    """The countdown, the neutral banner on red's side. "Capture the Temples" (no count) is
    hidden, the whole banner (user, 2026-10-15: "that useless banner", as Cursed Hollow's
    "Collect the Tribute"): its art and words faded out while the timer is hidden - the frame
    stays shown, its intro fading it."""
    alpha = lambda a: "".join(f'<Action type="SetProperty" frame="{TEMPLE}/{part}" Alpha="{a}"/>'
                              for part in ("BackgroundImage", "CenterpieceImage", "FCJH_TempleText", "FCJH_TempleCount"))
    t = T * 7
    return (left_banner("Temple", "TempleActivateLabel", "TempleActivateTimer", "CenterpieceImage",
                        TEMPLE_WORDS_START, TEMPLE_HEX_AFTER)
            + f'{t}<StateGroup name="FCJH_TempleCounting">\n{t}\t<DefaultState val="Idle"/>\n'
            f'{t}\t<State name="Counting"><When type="Property" frame="{TEMPLE}/TempleActivateTimer" Visible="true"/>'
            + alpha(255) + "</State>\n"
            f'{t}\t<State name="Idle">' + alpha(0) + "</State>\n"
            f'{t}</StateGroup>\n')


# The temples (TempleModeFrame: three discs, each its capture fill, bullets and cooldown) above
# the minimap, at THE GAP, on a bar of Blizzard's banner art (user, 2026-10-15: under the map
# they covered its bottom half). Blizzard's: the first disc's left 110 in from the panel's left,
# the others chained right off it (each off the one before's fire effect). The discs are
# Blizzard's size (the script fills a 112 x 112 mask: a smaller disc would read full early).
# Measured at 1080p (22_00_20, 3227b64, Blizzard's place): the discs 823-893, 947-1016,
# 1069-1140, their bottoms 1055-1058; the map's top tip 788, its notch's middle ~965 - the row's
# middle 981.5, so 18 units left. The bar (its art's own height) runs from 30 before the first
# disc to 30 past the last, its bottom 25 under the discs' middle; under them (RenderPriority).
TEMPLE_ROW_LEFT = 92       # the first disc's left in from the panel's: Blizzard's 110, centred on the tip
TEMPLE_BAR_PAST = 30       # the bar's ends past the outer discs
TEMPLE_BAR_DOWN = 25       # the bar's bottom under the discs' middle
_DISC = "$parent/ShrineIndicators{}/ShrineIcon"
_ROW = MECHANICS + "/CapturePointsPanel/TempleModeFrame"


def temple_shown(name, whens):
    """A StateGroup showing its frame (Alpha) while any of whens holds, hidden otherwise."""
    t = T * 4
    return (f'{t}<StateGroup name="{name}">\n{t}\t<DefaultState val="Hidden"/>\n'
            + "".join(f'{t}\t<State name="Shown{i}">{w}<Action type="SetProperty" Alpha="255"/></State>\n'
                      for i, w in enumerate(whens, 1))
            + f'{t}\t<State name="Hidden"><Action type="SetProperty" Alpha="0"/></State>\n{t}</StateGroup>')


# Only the temples that matter (user, 2026-10-15: "No real reason to show dead temples, and no
# real reason to show the bar between temple objectives"). Blizzard's script never hides the row
# (MMSkyTempleUIHandler shows the panel once): between rounds all three discs greyed, in the
# countdown the next ones carrying the time (their CooldownLabel), live the live ones lit
# (ShrineIcon's Ownership Order or Chaos, the rest Disable). So: the row and its bar shown only
# while the countdown frame is (Timer and Temple modes; Idle hides it); each disc shown, in its
# own slot (the left always the top temple), only while it carries the time or is lit. Going
# live the script lights all three then greys the dead ones - the same pass, no Wait between.
TEMPLE_DISC_SHOWN = lambda i: temple_shown("FCJH_TempleDisc", (
    f'<When type="Property" frame="{_ROW}/ShrineIndicators{i}/CooldownLabel" Visible="true"/>',
    f'<When type="AnimationState" frame="{_ROW}/ShrineIndicators{i}/ShrineIcon" Ownership="Order"/>',
    f'<When type="AnimationState" frame="{_ROW}/ShrineIndicators{i}/ShrineIcon" Ownership="Chaos"/>'))
PARTS["sky_temple"] = {
    "CapturePointsPanel/TempleModeFrame":
        temple_shown("FCJH_TempleRow", (f'<When type="Property" frame="{TEMPLE}" Visible="true"/>',)).replace(T * 4, ""),
    **{f"CapturePointsPanel/TempleModeFrame/ShrineIndicators{i}":
           TEMPLE_DISC_SHOWN(i).replace(T * 4, "") for i in (1, 2, 3)},
    "CapturePointsPanel/TempleModeFrame/ShrineIndicators1/ShrineIcon:Image":
        f'<Anchor side="Left" relative="$parent/$parent" pos="Min" offset="{TEMPLE_ROW_LEFT}"/>',
    "CapturePointsPanel/TempleModeFrame/FCJH_TempleBar:Image":
        f'<Anchor side="Left"   relative="{_DISC.format(1)}" pos="Min" offset="{-TEMPLE_BAR_PAST}"/>\n'
        f'<Anchor side="Right"  relative="{_DISC.format(3)}" pos="Max" offset="{TEMPLE_BAR_PAST}"/>\n'
        f'<Anchor side="Bottom" relative="{_DISC.format(1)}" pos="Mid" offset="{TEMPLE_BAR_DOWN}"/>\n'
        '<Texture val="@UI/HUD_MapMechanic_BG_CenterBar"/>\n<TextureType val="Nineslice"/>\n'
        '<RenderPriority val="500"/>\n<Unclipped val="true"/>\n<AcceptsMouse val="false"/>'}


PARTS["volskaya_foundry"] = {"VolskayaToastContainer/ToastNotification": TOAST,
                             "VolskayaCapturePointPanel/ContestedLabel:Label": CONTESTED,
                             "VolskayaRobotHealthSlideout": robot_frame()}


# ------------------------------------------------------------------ the maps

BOTTOM_RIGHT =(("Bottom", "Max", 0), ("Right", "Max", 0))     # pinned to the screen's corner
STRIP = (("Top", "Min", 0), ("Bottom", "Max", 0), ("Right", "Max", 0))   # down the right edge
SCREEN = (("Top", "Min", 0), ("Bottom", "Max", 0), ("Left", "Min", 0), ("Right", "Max", 0))

# Art: each map's CustomMiniMap, the opaque part, read from the map archives in Battle.net's
# cache (2026-10-06; the battlegrounds aren't in the game's own storage).
MAPS = {
    "alterac_pass": Map(
        "Alterac Pass", (441, 316), file="AlteracMechanics",
        # its right AV_PANEL_GROW further, for red's cavalry spot (av_carrier)
        panels={"AlteracMechanicsPanel": (("Top", "Min", -25), ("Bottom", "Max", -25), ("Right", "Max", AV_PANEL_GROW))},
        place=("AlteracMechanicsPanel",),
        # THE GAP: the cage's hexagon on the map's top tip (797 px both) with the panel 10 px
        # lower (user, 2026-10-13: "move down the neutral banner ... by about 10px"; b6e0e68)
        above=(0, 10),
        # the prisoners, the cage fight and the cavalry: one frame, on a carrier (av_carrier) at
        # Blizzard's place above the minimap; the cavalry on these spots
        team={"AlteracMechanicsPanel": {
            "blue": [Alert("AVCavalryBlue", kind="AV", box=AV_BOX, spot_only=True,
                           note="the cavalry, when it's blue's (av_carrier)")],
            "red": [Alert("AVCavalryRed", kind="AV", box=AV_BOX, spot_only=True,
                          note="the cavalry, when it's red's (av_carrier)")]}},
        notes="a strip down the right edge; the cage fight bar and its two event banners at its middle"),
    "battlefield_of_eternity": Map(
        "Battlefield of Eternity", (438, 269), file="BossDuel", minimap=(75, 0),
        # Blizzard's corner, 9 right: its boxes are drawn 8 px left of the screen's centre (the
        # fight's tips 736 .. 1168, 13_48_52; the map itself centred, 774 .. 1145) - user,
        # 2026-10-15: "if its not centered, then center it"
        panels={"BossDuelPanel": (("Bottom", "Max", 0), ("Right", "Max", 9))}, place=("BossDuelPanel",),
        # The fight above the minimap. THE GAP: its portraits' hexagons (the health numbers, 19
        # lower, hang either side of the map's tip). 793 px over the map's top tip 825 (13_48_52,
        # the numbers 812; 14_29_30: the hexagons 811, the box's bottom edge 799, the numbers 830)
        above=(32, 0),
        # "Immortals spawning": the neutral banner, on red's side; the winner's Immortal pushing
        # in its place, on its team's side, mirrored on blue's (lane_side)
        team={"BossDuelPanel": {
            "blue": [Alert("BossLaningFrame", kind="SPAWN", box=SPAWN_BOX, spot_only=True,
                           note="the winner's Immortal pushing, when it's blue's")],
            "red": [Alert("BossSpawnFrame", kind="SPAWN", box=SPAWN_BOX,
                          followers=(("BossLaningFrame", 0, unclipped(LANE_PARTS) + LANE_COPIES + lane_side()),),
                          extra=SPAWN_BANNER,
                          note="the Immortals' countdown (neutral), then the winner's Immortal pushing on red")]}}),
    "blackhearts_bay": Map(
        "Blackheart's Bay", (452, 313), core="BlackheartsBayPanel",
        # "Chests have spawned": the neutral banner, on red's side; Blackheart's cannon in its
        # place, on the firing team's side (cannon_side). The doubloon counts stay on the panel,
        # pinned to the screen's bottom as Blizzard's: [minimap.panel_nudge] lifts them.
        team={"BlackheartsBayPanel": {
            "blue": [Alert("CannonModeFrame", kind="CHEST", box=CHEST_BOX, spot_only=True,
                           note="Blackheart's cannon, when it's blue's")],
            "red": [Alert("ChestSpawnFrame", kind="CHEST", box=CHEST_BOX,
                          followers=(("CannonModeFrame", 0, unclipped(CANNON_PARTS) + CANNON_COPIES + cannon_side()),),
                          extra=unclipped(CHEST_PARTS),
                          note="the chests spawning (neutral), then Blackheart's cannon on red")]}}),
    "braxis_holdout": Map(
        "Braxis Holdout", (447, 264), file="HoldOut", minimap=(-35, 0),
        # its zerg HUD compacted: the dishes and their beams on the hexagons, the words in and
        # above them (PARTS: BEACON_ICONS, ZERG_WORDS); the whole HUD down by [minimap.panel_nudge].
        # Nothing of it touches the map any more: the mechanics panel no longer goes under the
        # minimap (it did for the line along the map's bottom edge).
        panels={"HoldOutPanel": BOTTOM_RIGHT},
        place=("HoldOutPanel",),
        # The zerg wave warning: one neutral banner, on red's side, its countdown already in the
        # bar between the words and the hexagon (holdout.stormlayout). Shown in ZergWarning mode
        # (libscho.galaxy MMHOUISetMode). Its art as the tribute's: the hexagon 20 in from the
        # frame's top-right, the bar 324 left of it and 9 past it.
        team={"HoldOutPanel": {
            "red": [Alert("HoldOutWarningFrame", kind="HOLDOUT", box=HOLDOUT_BOX,
                          extra=unclipped(HOLDOUT_PARTS, 3), note="the zerg wave warning (neutral)")]}}),
    "cursed_hollow": Map(
        "Cursed Hollow", (436, 312), core="RavenCourtPanel",
        # "Tribute spawning" ("Collect the tribute" hidden: tribute_count): one neutral banner, on red's side. Its art:
        # the hexagon pinned 20 in from the frame's top-right, the bar 481 wide ending 15 past it,
        # the count under the hexagon (measured in game, 2026-10-06). The curse banner hangs off
        # the same hexagon (CurseFrame/TimerImage) and goes to the cursed team's side
        # (cursed_side): red's is the tribute's spot, blue's a spot of its own.
        team={"RavenCourtPanel": {
            "blue": [Alert("CurseFrame", kind="BANNER", box=TRIBUTE_BOX, spot_only=True,
                           note="the curse, when it's on blue")],
            "red": [Alert("TributeSpawnFrame", kind="BANNER", box=TRIBUTE_BOX,
                          followers=(("CurseFrame", CURSE_UP, CURSE_TEXT + CURSE_COUNT + curse_colon() + unclipped(CURSE_PARTS)
                                       + CURSE_RAVEN),),
                          extra=cursed_side() + tribute_count() + unclipped(TRIBUTE_PARTS),
                          note="the tribute spawning (neutral); the curse on red")]}},
        notes="the tribute counts sit at the minimap's bottom corners"),
    "dragon_shire": Map(
        "Dragon Shire", (434, 282), core="DragonShirePanel",
        # "Shrines activate in", then the Dragon Knight in its place: a neutral banner, on red's
        # side, then the knight on its team's. The shrine markers (ShrineModeFrame: each team's moon and star, lit while it holds
        # them) stay on the panel, pinned to the screen's bottom as Blizzard's:
        # [minimap.panel_nudge] puts them on the padding line.
        # The knight moves to blue's spot, mirrored, when it's blue's (knight_side).
        team={"DragonShirePanel": {
            "blue": [Alert("DragonModeFrame", kind="SHRINE", box=SHRINE_BOX, spot_only=True,
                           note="the Dragon Knight, when it's blue's")],
            "red": [Alert("ShrineTimerModeFrame", kind="SHRINE", box=SHRINE_BOX,
                          followers=(("DragonModeFrame", 0, unclipped(DRAGON_PARTS) + KNIGHT_COPIES + knight_side()),),
                          extra=SHRINE_BANNER,
                          note="the shrines' countdown (neutral), then the Dragon Knight on red")]}}),
    "garden_of_terror": Map(
        "Garden of Terror", (438, 270), core="GardenOfTerrorPanel", file="GardenMapMechanic",
        # the seed banners and the Terrors: the map file's own templates, on these spots
        # (seed_banner, terror_frame; PARTS)
        team={"GardenOfTerrorPanel": {
            "blue": [Alert("GardenTerrorHealthFrame", kind="TERROR", box=TERROR_BOX, spot_only=True,
                           note="the Terrors' health, when they're blue's (terror_side)")],
            "red": [Alert("EventWarningFrame", kind="SEED", box=SEED_BOX, spot_only=True,
                          note="the seed banners' spot (neutral): EventWarningFrame (and "
                               "GatherTheSeedsFrame, hidden) hang off it; red's Terrors too")]}}),
    "hanamura_temple": Map(
        "Hanamura Temple", (473, 287), file="HanamuraRework", minimap=(80, 0),
        # three screen-sized panels, their parts placed from the screen's right edge
        panels={"HanamuraReworkPayloadWarningTimerPanel": SCREEN,
                "HanamuraReworkActivePaylaodStatusPanel": SCREEN,
                "HanamuraReworkVictoryShotsStatusPanel": SCREEN,
                # ...and the payload's picture from the right edge of the panel they're in
                **{f"HanamuraReworkActivePaylaodStatusPanel/{n}:Image": (("Right", "Max", -204),)
                   for n in ("ActivePayloadImageAnchor", "ActivePayloadImageOrder",
                             "ActivePayloadImageChaos", "ActivePayloadImageNeutral")}},
        place=("HanamuraReworkPayloadWarningTimerPanel", "HanamuraReworkActivePaylaodStatusPanel",
               "HanamuraReworkVictoryShotsStatusPanel"),
        # THE GAP: the payload status's hexagon - estimated from the template (its image's bottom
        # 57 units under the minimap's top) and the map's tip at 852 px; measured in game off the
        # countdown's hexagon (2026-10-16): ~9 px at 1080p, on the gap within JPEG and scaling
        above=(35, 0), proxy=True,
        # No alerts on the teams' sides (user, 2026-10-14): the countdown ("Payload spawns in"),
        # the payload's push status and the shots ("Attacking the core", one frame per team)
        # take turns in one place above the minimap and animate as one, so they stay Blizzard's,
        # there. Tried and dropped: the countdown on red's side, the shots on their team's (the
        # shots' frame clipped its bar and icon: Blizzard's intro slides the icon 198 right of
        # its layout place, past the frame's right edge where ours put it).
        ),
    "haunted_mines": Map(
        "Haunted Mines", (433, 437), core="HauntedMinesPanel",
        # Its minimap holds the surface and the mines stacked: square, so at the older five's
        # shared place the mines hung off the screen. Its own place from the start, by its map
        # id (id_placers). Two views (user, 2026-10-09): at load only the surface, its bottom on
        # the padding line, the mines below the screen; when the mines first open (the script
        # shows the skull counts: libmhtm SetMode Skulls), it glides up to the whole map, and
        # stays. The surface's bottom is 8 px above the drawn map's middle, the mines' top 35
        # below (measured at 1080p, 2026-10-09).
        own_place=True, launch_cut=-8, opens="HauntedMinesPanel/SkullModeFrame",
        # "Mines will open in", then the golems' health in its place: one neutral banner, on
        # red's side. The skull counts (SkullModeFrame) stay on the panel, pinned to the
        # screen's bottom as Blizzard's: [minimap.panel_nudge] puts them on the padding line.
        team={"HauntedMinesPanel": {
            "red": [Alert("MineTimerModeFrame", kind="MINES", box=MINES_BOX,
                          followers=(("GolemModeFrame", 0, unclipped(GOLEM_PARTS)),),
                          extra=MINES_BANNER,
                          note="the mines opening, then the golems (neutral)")]}},
        extra="skulls"),
    "infernal_shrines": Map(
        "Infernal Shrines", (458, 301), file="Shrines",
        panels={"ShrinesPanel": BOTTOM_RIGHT}, place=("ShrinesPanel",),
        # "A shrine is activating": the neutral banner, on red's side ("Shrine active" hidden:
        # PARTS); the Punisher in its place, on its summoner's side (punisher_side). The skull
        # race stays on the panel: [minimap.panel_nudge] lifts it. The minimap on THE FLOOR but
        # while the race shows (CursedEvent mode, libmshe.galaxy MMTowerPushUISetMode): then it
        # glides up out of the race's way, the race pinned where it was (user, 2026-10-15; lift).
        lifts="ShrinesPanel/CursedMinionKillFrame",
        team={"ShrinesPanel": {
            "blue": [Alert("PunisherFrame", kind="INFERNAL", box=INFERNAL_BOX, spot_only=True,
                           note="the Punisher, when it's blue's")],
            "red": [Alert("ShrineWarningFrame", kind="INFERNAL", box=INFERNAL_BOX,
                          followers=(("PunisherFrame", 0, unclipped(PUNISHER_PARTS) + PUNISHER_COPIES + punisher_side()),),
                          extra=WARNING_BANNER,
                          note="the shrine's countdown (neutral), then the Punisher on red")]}}),
    "sky_temple": Map(
        "Sky Temple", (437, 344), file="CapturePoints",
        panels={"CapturePointsPanel": BOTTOM_RIGHT}, place=("CapturePointsPanel",),
        # "Temples activate in": the neutral banner, on red's side ("Capture the Temples"
        # hidden: temple_banner). The temples to the gap on their own, on a bar (PARTS): on
        # 3227b64 their lowest bottom ~1058, the tip ~788.
        gap_parts={"CapturePointsPanel/TempleModeFrame": (-270, 0)},
        team={"CapturePointsPanel": {
            "red": [Alert("TimerModeFrame", kind="TEMPLE", box=TEMPLE_BOX, extra=temple_banner(),
                          note="the temples' countdown (neutral)")]}}),
    "tomb_of_the_spider_queen": Map(
        "Tomb of the Spider Queen", (430, 262), file="SoulCage",
        panels={"CryptPanel": BOTTOM_RIGHT}, place=("CryptPanel",),
        # Its neutral two to the gap on their own - the gem counts and the lanes' hexagons share
        # their panel, at the screen's bottom. They never show together (the timer after the
        # Webweavers die). The Webweavers' banner (one frame, its words set per team by the
        # script - neutral, as Hanamura's): on f11f8f4 its portrait's bottom ~806, the tip ~838.
        # The egg timer (user, 2026-10-14: "top of the minimap is fine"): on f03aba6 its hexagon's
        # bottom ~1066, the tip ~878, the panel at -69.
        gap_parts={"CryptPanel/SoulEaterFrame": (32, 0),
                   "CryptPanel/SoulCageCooldownFrame": (-188, -69)},
        # its art drawn 21 px left of its square's centre (2026-10-14, 01359b3: the outline's
        # sides at ~780 and ~1098, the bottom point at ~936 against the counts' line at ~956 -
        # user: "the most lopsided map I've seen"). Only the map moves. 20 put the point ~1-2 px
        # right of the split (127c01a); 17 a touch left (5f04383); the user: "2px was probably the
        # right call".
        across=18),
    "towers_of_doom": Map(
        "Towers of Doom", (436, 298), file="FieldofSlaughter",
        place=("MainFoSPanel",),
        # Its strip stays on the right edge: everything a broadcast needs from it is ours now
        # (below), and what's left (town health, at the top) is drawn from the screen's top.
        # "Cannons are firing": the script shows RAVEN's alert when blue captures an altar and
        # NECRO's when red does (only the Your/Enemy text is per viewer), to each team's
        # players only - a player view (1-8) shows them, the free observer view never does,
        # and nothing an observer's UI receives marks a capture (user, 2026-10-06). The towns
        # are ours, from the observer's own town counts (towers_extra).
        team={"MainFoSPanel": {
            "blue": [Alert("WaygateNotificationFrame", note="the tunnels opening"),
                     cannons("RavenNotificationFrame"),
                     town_alert("blue", "FieldofSlaughter/MainFoSPanel/AllyCaptureNotificationFrame",
                                "Blue team captured")],
            "red": [Alert("AltarSpawnNotificationFrame", note="the altar countdown"),
                    Alert("TowersNotificationFrame", note="the towers upgrading"),
                    cannons("NecroNotificationFrame"),
                    town_alert("red", "FieldofSlaughter/MainFoSPanel/EnemyCaptureNotificationFrame",
                               "Red team captured")]}},
        extra="towers"),
    "volskaya_foundry": Map(
        "Volskaya Foundry", (452, 314), file="VolskayaMapMechanic",
        panels={"VolskayaCapturePointPanel": STRIP}, place=("VolskayaCapturePointPanel",),
        # its two neutrals to the gap, each from Blizzard's own anchor to the minimap (they don't
        # hang off their panels). On a1f60ca: the capture point's hexagon's bottom 40 px over the
        # map's top tip (803); the toast's lowest part, its hexagon, 765
        gap_parts={"VolskayaCapturePointPanel/CenterHex:Image": (40, 0, (MINIMAP_SQUARE, "Min", 75)),
                   "VolskayaToastContainer": (38, 0, ("$parent/$parent/MinimapPanel", "Min", 80))},
        # the robot (robot_frame, PARTS): a team banner on these spots
        team={"VolskayaCapturePointPanel": {
            "red": [Alert("VolskayaRobotHealthSlideout", kind="ROBOT", box=ROBOT_BOX, spot_only=True,
                          note="the robot's spot when it's red's (robot_frame)")],
            "blue": [Alert("VolskayaRobotBlue", kind="ROBOT", box=ROBOT_BOX, spot_only=True,
                           note="the robot's spot when it's blue's")]}},
        notes="the capture point's hex is placed from the minimap; its strip clipped it"),
    "warhead_junction": Map(
        "Warhead Junction", (460, 390), file="SCMap2", minimap=(0, 0), place=("SC2Panel",),
        # its file nudges the map 30 units right in the minimap panel: back to the square's place
        fix=f'<Action type="SetAnchor" frame="{MINIMAP}/Minimap" side="Left" relative="{MINIMAP}" pos="Min" offset="0"/>',
        # the warheads' countdown, then how many are left: one neutral banner, on red's side
        # (WARHEAD_BOX, as Blizzard draws it); the nuke counters by the minimap (warhead_counters, PARTS)
        team={"SC2Panel": {
            "red": [Alert("TerrazineEruptionFrame", kind="WARHEAD", box=WARHEAD_BOX, extra=unclipped(WARHEAD_PARTS, 3),
                          note="the warheads' countdown, then how many are left (neutral)")]}},
        notes="its panel is placed from the minimap already"),
}
EXTRAS = {"towers": towers_extra, "skulls": skulls_extra}

# Blizzard's map id per map: the script variable libCore_gv_mAPMapStringID, which a layout can
# read from the match's start, on any map (id_placers, on_map; user, 2026-10-09). Where each is
# from: GAME read on screen in game; SCRIPT tested by Blizzard's own scripts (Jamie Phan
# gamelib.galaxy / uilib.galaxy - the battlegrounds' own scripts aren't in it); SPAZZO tested in
# Spazzo's interface (CustomPanelSpazzo) only - read one on screen before relying on it.
MAP_IDS = {
    "alterac_pass": "AlteracPass",                    # GAME (2026-10-12)
    "battlefield_of_eternity": "BattlefieldOfEternity",  # GAME (2026-10-15)
    "blackhearts_bay": "BlackheartsBay",              # GAME (2026-10-12)
    "braxis_holdout": "BraxisHoldout",                # GAME (2026-10-09)
    "cursed_hollow": "CursedHollow",                  # GAME (2026-10-09; CursedHollowSandbox: the sandbox's)
    "dragon_shire": "DragonShire",                    # GAME (2026-10-09)
    "garden_of_terror": "HauntedWoods",               # GAME (2026-10-12)
    "hanamura_temple": "Hanamura",                    # GAME (2026-10-14)
    "haunted_mines": "HauntedMines",                  # GAME (2026-10-09)
    "infernal_shrines": "Shrines",                    # GAME (2026-10-15)
    "sky_temple": "ControlPoints",                    # GAME (2026-10-15)
    "tomb_of_the_spider_queen": "Crypts",             # GAME (2026-10-14)
    "towers_of_doom": "TowersOfDoom",                 # GAME (2026-10-09)
    "volskaya_foundry": "Volskaya",                   # GAME (2026-10-15)
    "warhead_junction": "Warhead Junction",           # GAME (2026-10-15) - with the space
}
assert set(MAP_IDS) == set(MAPS), f"MAP_IDS: every map needs its id - {set(MAPS) ^ set(MAP_IDS)}"
# own_place is for the older maps: a newer one's panel placer moves it already (placer)
assert not [k for k, m in MAPS.items() if m.own_place and m.place], "own_place: a map with a placer of its own"
# a lift is played in the map's own panel, by its placer (lift)
assert not [k for k, m in MAPS.items() if m.lifts and not (m.place and m.file)], "lifts: a map with its own panel's placer"
# a map opening on part of its map is placed by its id, and needs what opens it
assert not [k for k, m in MAPS.items() if (m.launch_cut is not None) != bool(m.own_place and m.opens)], \
    "launch_cut: with own_place and opens, and only then"


def drawn_height(key):
    """How tall a map draws in the minimap square, px at 1080p (DRAWN_PX wide, or tall if it's
    taller than wide)."""
    w, h = MAPS[key].art
    return h * min(DRAWN_PX / w, DRAWN_PX / h)


def max_stack():
    """The tallest stack any map builds on one side."""
    return max(len(col) for m in MAPS.values() for cols in m.team.values() for col in cols.values())


def on_minimap(side, pos, offset, m, down=0):
    """A side Blizzard anchored to the screen (`pos` of it, `offset` units), as the same
    distance from our minimap's bottom-right corner: Blizzard's minimap's bottom is m.minimap[0]
    below the screen's, its right m.minimap[1] right of the screen's. `down`: units more,
    downwards (layout.toml [minimap.panel_nudge]). A map moved across (m.across) has its panels
    taken back: they stay where they were, only the map moves (user, 2026-10-14). -> (pos,
    offset) of MINIMAP."""
    right = m.minimap[1]
    if side in ("Left", "Right"):
        return "Max", offset - right - round(m.across / 0.9) - {"Min": SCREEN_W, "Mid": SCREEN_W // 2, "Max": 0}[pos]
    return "Max", offset - m.minimap[0] + down - {"Min": SCREEN_H, "Mid": SCREEN_H // 2, "Max": 0}[pos]


def const(key):
    return f"#FCJH_MINIMAP_BOTTOM_{key.upper()}"


def place_actions(key, indent):
    """The SetAnchors that put the minimap where this map wants it - at load, for a map that
    opens on part of its map (launch_cut)."""
    t = T * indent
    bottom = f"#FCJH_MINIMAP_LAUNCH_{key.upper()}" if MAPS[key].launch_cut is not None else const(key)
    sides = "_" + key.upper() if MAPS[key].across else ""      # its own, moved across (gen.py)
    out = (f'{t}<Action type="SetAnchor" frame="{MINIMAP}" side="Left"   relative="$GameUI" pos="Mid" offset="#FCJH_MINIMAP_PANEL_L{sides}"/>\n'
           f'{t}<Action type="SetAnchor" frame="{MINIMAP}" side="Right"  relative="$GameUI" pos="Mid" offset="#FCJH_MINIMAP_PANEL_R{sides}"/>\n'
           f'{t}<Action type="SetAnchor" frame="{MINIMAP}" side="Bottom" relative="$GameUI" pos="Max" offset="{bottom}"/>\n')
    return out + (f"{t}{MAPS[key].fix}\n" if MAPS[key].fix else "")


def anchor_lines(sides, m, indent, down=0):
    t = T * indent
    out = ""
    for side, pos, offset in sides:
        p, off = on_minimap(side, pos, offset, m, down)
        out += f'{t}<Anchor side="{side}"{" " * (6 - len(side))} relative="{MINIMAP}" pos="{p}" offset="{off}"/>\n'
    return out


def short(name):
    for cut in ("NotificationFrame", "FCJH_"):
        name = name.replace(cut, "")
    return name.replace("Frame", "")


def bottoms(team, kind):
    """The stacks' constants for one art (gen.py writes them): FCJH_MAP_ALERT_<TEAM>_B_<KIND>,
    then _2, _3... - where that art's frame goes for its bar to land on the slot."""
    return f"#FCJH_MAP_ALERT_{team.upper()}_B" + (f"_{kind}" if kind else "")


def stack_states(team, column, i, targets, at, indent, kind=""):
    """Alert i of its side's column: on the bottom slot - one place, its bar over the core bar's
    top (user, 2026-10-09: it no longer steps up while the core bar shows) - or one slot up for
    each alert before it in the column that's showing. The states go from most alerts showing
    to fewest; the first whose alerts all show wins: the first to show keeps its slot."""
    t = T * indent
    key = bottoms(team, kind)
    act = lambda c: "".join(f'<Action type="SetAnchor" frame="{target}" side="Bottom" relative="{at[0]}" '
                            f'pos="{at[2]}" offset="{c}"/>' for target in targets)
    out = f'{t}<StateGroup name="FCJH_Stack">\n{t}\t<DefaultState val="Bottom"/>\n'
    before = column[:i]
    for n in range(len(before), 0, -1):
        for over in combinations(before, n):
            when = "".join(f'<When type="Property" frame="$parent/{a.name}" Visible="true"/>' for a in over)
            out += f'{t}\t<State name="Over{"".join(short(a.name) for a in over)}">{when}{act(f"{key}_{n + 1}")}</State>\n'
    out += (f'{t}\t<State name="Bottom">{act(key)}</State>\n'
            f'{t}</StateGroup>\n')
    return out


def spot_name(a):
    return f"FCJH_{a.name}Spot"


# Blizzard's banner intro, on every banner we place by its art (user, 2026-10-09: Towers of Doom's
# are the newest banners - every map's alike, each keeping its own effects). Towers' alerts are
# Blizzard's NotificationFrameTemplate, which has it ("Intro", core mapmechanicpanel); the older
# maps' banners have none. As the template's: shown, the banner fades in over 0.2 s sliding 50 in
# from the right, its bar growing out of the hexagon (its left end 350 in, out by 0.3 s). Its text
# fades with the frame - the template's own label fades would fight our labels' states.
# Started when the banner SHOWS (OnShown) - its own, or its panel's, when the script shows the
# panel with the banner already up (Haunted Mines). Towers' scripts send the template a "Show"
# event; the older maps' never do (the first try waited for it: nothing played, user 2026-10-09).
# So no hide: the template's plays backwards on "Hide", holding the frame up meanwhile - on
# OnHidden that would show it again. Standard banners only - the bar
# and hexagon art; nothing of a map's own (user, 2026-10-09: the golems' double health bar, Braxis's
# beacons and zerg HUD keep only their placement). NOT_BANNERS: followers that aren't one.
NOT_BANNERS = ("GolemModeFrame",)
# Banners whose sides a state moves - the team banners, between red's side and blue's
# (team_banner): the fade only. A relative Anchor controller counts from the LAYOUT anchor, not a
# state's SetAnchor, and end="Pause" holds it (Haunted Mines' glide, 2026-10-09): the slide would
# have pinned the curse to red's spot and Blizzard's bar layout after its first intro. The
# tribute too: cursed_side moves it with the curse, whose raven's height hangs off the tribute's.
FADE_ONLY = ("CurseFrame", "TributeSpawnFrame", "DragonModeFrame", "CannonModeFrame", "BossLaningFrame",
             "PunisherFrame")


def intro(indent, slide=True):
    if not slide:
        t = T * indent
        return (f'{t}<Animation name="FCJH_Intro">\n'
                f'{t}\t<Event event="OnShown" action="Restart,Play"/>\n'
                f'{t}\t<Event event="OnShown" action="Restart,Play" frame="$parent"/>\n'
                f'{t}\t<Controller type="Fade" end="Pause">\n'
                + "".join(f'{t}\t\t<Key type="Curve" time="{k}" value="{v}"/>\n' for k, v in ((0, 0), (".2", 255), (".4", 255)))
                + f'{t}\t</Controller>\n{t}</Animation>\n')
    t = T * indent
    curve = lambda *keys: "".join(f'{t}\t\t<Key type="Curve" time="{k}" value="{v}"/>\n' for k, v in keys)
    slide = lambda sd, frame="": (f'{t}\t<Controller type="Anchor" end="Pause" side="{sd}" relative="true"'
                                  + (f' frame="{frame}"' if frame else "") + ">\n")
    return (f'{t}<Animation name="FCJH_Intro">\n'
            f'{t}\t<Event event="OnShown" action="Restart,Play"/>\n'
            f'{t}\t<Event event="OnShown" action="Restart,Play" frame="$parent"/>\n'
            f'{t}\t<Controller type="Fade" end="Pause">\n' + curve((0, 0), (".2", 255), (".4", 255)) + f'{t}\t</Controller>\n'
            + "".join(slide(sd) + curve((0, 50), (".1", 0), (".4", 0)) + f'{t}\t</Controller>\n' for sd in ("Left", "Right"))
            + slide("Left", "BackgroundImage") + curve((0, 350), (".1", 350), (".3", 0), (".4", 0))
            + f'{t}\t</Controller>\n'
            + f'{t}</Animation>\n')



# Garden's seed banners (seed_banner): written here, after intro
# Tomb's Webweavers (user, 2026-10-14, "plan A"): the three lanes' hexagons on the summoning
# team's side, in the gap between the minimap and its plates - the bottom lane lowest - and
# climbing outward (user: "between the minimap and the team
# nameplates" - over the plate they stood too far out; nothing else of a team's stacks there). Blizzard keeps a set per team (SoulEaterModeBlueFrame / RedFrame; the
# script shows the summoner's), so each set lives on its side for good. Each lane's health
# fill, lit frame and fire ring hang off its hexagon; all of it may draw past the panel's box.
# gen.py places them (FCJH_MAP_WEAVER_<TEAM>_<LANE>_X/_B: the hexagon's centre and bottom).
# The stack (user, 2026-10-15: "about as high as the minimap total") runs from the plates'
# bottom up to the minimap's drawn top tip; the middle one halfway, the hexagons nesting
# into each other a little, each WEAVER_STEP_PX further out than the one below.
WEAVER_W_PX = 54                      # a hexagon's width as drawn at 1080p (31a031d)
WEAVER_ART = {"Bottom": (72, 5),      # each lane's hexagon as drawn at 1080p (31a031d): its height
              "Mid": (62, 14),        # (the top one has a point above, the bottom one a point
              "Top": (72, 14)}        # below) and its box's bottom under it
# Lowered (user, 2026-10-15) so the bottom one's point is level with the gem counts' blue/red
# line, the stack's height kept; and across, centred in the dead space between the drawn
# minimap and the plates (user: "center it in the deadspace"): each one's centre between the
# two edges at its height, then the straight line nearest those.
WEAVER_BOTTOM_PX = 1071               # the gem counts' blue/red line (127c01a, Tomb's minimap at 29 down)
WEAVER_TOP_PX = 868 + WEAVER_BOTTOM_PX - 1060   # the minimap's drawn top tip (868, 31a031d), as lowered
WEAVER_MINIMAP_PX = (955, 158, 943, 1.05)   # Tomb's drawn minimap (6c52e5e): its middle, its side
                                      # lobes' reach either way, and its sides from that height down
                                      # going in this much per px
WEAVER_OUT_PX = 10                    # then this much further out (user, 2026-10-15, 48d775e centred:
                                      # "still slightly too close the minimap")
WEAVER_STEP_PX = 40                  # each one this much further out than the one below (31a031d:
                                      # 40 per 81 up, the plates' slant; now per ~60 up, leaning more)
WEAVER_LANES = ("Bottom", "Mid", "Top")   # from the stack's bottom up


def weaver_parts():
    out = {}
    for team, frame in (("blue", "SoulEaterModeBlueFrame"), ("red", "SoulEaterModeRedFrame")):
        for lane in WEAVER_LANES:
            at, c = f"CryptPanel/{frame}/", f"#FCJH_MAP_WEAVER_{team.upper()}_{lane.upper()}"
            out[f"{at}{lane}SoulEaterDisabled:Image"] = (
                '<Unclipped val="true"/>\n'
                f'<Anchor side="Bottom" relative="$GameUI" pos="Max" offset="{c}_B"/>\n'
                f'<Anchor side="Left"   relative="$GameUI" pos="Mid" offset="{c}_X"/>\n'
                f'<Anchor side="Right"  relative="$GameUI" pos="Mid" offset="{c}_X"/>\n')
            # not the health image: the script drains it by shrinking its frame, which crops it
            # (Unclipped there kept it full - user, 2026-10-15: "they dont seem to drain their hp")
            for part in (f"{lane}SoulEaterHealthDisabled:Image", f"{lane}SoulEaterEnabled:Image",
                         f"{lane}SoulEaterHealth",
                         f"{lane}FireEffect", f"{lane}FireEffect/FireEffectBase:Image",
                         f"{lane}FireEffect/FireEffectAdd:Image"):
                out[at + part] = '<Unclipped val="true"/>\n'
    return out


PARTS["tomb_of_the_spider_queen"] = weaver_parts()


# Warhead Junction's nuke counters (Team1TerrazineFrame blue, Team2 red: each team's nukes
# held, an icon and a count, hung off the minimap's bottom either side of its tip). With the
# map down to the floor ([minimap.nudge]) they'd sit on its lower sides, and they were cut off
# at the screen's bottom already (2026-10-15, 08eeb21: icons ~1020 down past 1080, the map's
# tip at 1043). The map has no markers under it to keep clear (user: "we can probably move
# these nukes outwards and move the minimap downwards"): each team's out to its side, clear of
# the map's sides at their height, and up off the screen's bottom.
#
# Then turned round as Tomb's gem counts (user, 2026-10-16): the icon at the outer end, the count
# inner, the two strips meeting under the map's tip, and hidden until warheads first spawn (no
# point counting nukes nobody can pick up yet), then up for the rest of the game.
WARHEAD_COUNTERS_OUT_PX = 0           # the strips meet at the square's Mid-5, ~950 px; at 50 out
                                      # they ran ~762-904 / ~1007-1155 (00_14_47). Under the map's
                                      # stub (~928-978 at the floor): raise if it reads badly
WARHEAD_COUNTERS_UP_PX = 44           # the map's 22 down taken back, then 22 up: seen on 1b0dea6 at 20
                                      # up, the icons' bottom ~1062 and their team strips' (blue/red
                                      # lines under them, once off the screen) 1067 - 2 past the floor
# Turned round, in units from each strip's ends (its Background: blue's ~798-950 px, red's
# ~950-1103). Blizzard's: blue's icon 74 in from its outer end, its count 105 in from the inner,
# red's mirrored (84 / 105). Ours: the icons 30 in (blue's art ~827-880 px) and 46 (red's ~1026-
# 1079 - its art sits further in its image), the counts' inner edges ~915 / ~991 px, either side
# of the map's stub (centre ~953). Blizzard's count styles kept: blue's right-justified, red's left.
# Seen so (18f4cbb): icons ~828-880 / ~1028-1078, counts ~895-917 / ~992-1005, strips ~814-1103 -
# too close to the map (user, 2026-10-16), so both moved out WARHEAD_MARKS_OUT_PX, the strips left
# be. At 15 (7236174): icons ~813-863 / ~1042-1093, counts end ~902 / start ~1005, ~22 px off the
# map's sides - "a bit more" (user): at 30 blue's icon hangs ~15 past its strip's end, as Tomb's.
WARHEAD_MARKS_OUT_PX = 30
_out = round(WARHEAD_MARKS_OUT_PX / 0.9)
WARHEAD_ICON_IN = (30 - _out, 46 - _out)    # blue's icon Left from its strip's Min, red's Right from Max
WARHEAD_COUNT_IN = (39 + _out, 37 + _out)   # blue's count Right from its strip's Max, red's Left from Min


def warhead_counters():
    up, out = round(WARHEAD_COUNTERS_UP_PX / 0.9), round(WARHEAD_COUNTERS_OUT_PX / 0.9)
    parts = {}
    for n, side in ((1, -1), (2, 1)):
        x = side * out
        frame = f"SC2Panel/Team{n}TerrazineFrame"
        parts[frame] = (
            f'<Anchor side="Top"    relative="{MINIMAP_SQUARE}" pos="Max" offset="{-146 - up}"/>\n'
            f'<Anchor side="Bottom" relative="$parent" pos="Max" offset="{-up}"/>\n'
            f'<Anchor side="Left"   relative="{MINIMAP_SQUARE}" pos="Min" offset="{x}"/>\n'
            f'<Anchor side="Right"  relative="{MINIMAP_SQUARE}" pos="Max" offset="{x}"/>\n'
            # hidden until FCJH_NukeSensor (in the warheads banner) sends this, once: never reversed
            '<Alpha val="0"/>\n'
            '<Animation name="FCJH_NukesOn">\n'
            '\t<Event event="FCJH_NukesOn" action="Play"/>\n'
            '\t<Controller type="Fade" end="Pause">\n'
            + "".join(f'\t\t<Key type="Curve" time="{k}" value="{v}"/>\n' for k, v in ((0, 0), (".2", 255), (".4", 255)))
            + '\t</Controller>\n'
            '</Animation>\n')
        icon = (f'<Anchor side="Left" relative="$parent/Background" pos="Min" offset="{WARHEAD_ICON_IN[0]}"/>\n'
                if n == 1 else
                f'<Anchor side="Right" relative="$parent/Background" pos="Max" offset="{-WARHEAD_ICON_IN[1]}"/>\n')
        parts[frame + "/TerrazineIcon:Image"] = parts[frame + "/TerrazineIconGlow:Image"] = icon
        parts[frame + "/TerrazineCounter:Label"] = (
            f'<Anchor side="Right" relative="$parent/Background" pos="Max" offset="{-WARHEAD_COUNT_IN[0]}"/>\n'
            if n == 1 else
            f'<Anchor side="Left" relative="$parent/Background" pos="Min" offset="{WARHEAD_COUNT_IN[1]}"/>\n')
    return parts


PARTS["warhead_junction"] = warhead_counters()

PARTS["garden_of_terror"] = {"EventWarningFrame": seed_banner(True),
                             # "Gather the seed!" hidden (user, 2026-10-15: static words the minimap's
                             # seed already says; revisit after the final pass): parked above the
                             # screen, as Towers' pair (towers_extra) - its own slide-in fades it, so
                             # not by alpha. seed_banner(False) builds it again.
                             "GatherTheSeedsFrame": '<Anchor side="Bottom" relative="$GameUI" pos="Min" offset="-9999"/>\n',
                             "GardenTerrorHealthFrame": terror_frame()}

def alert_frame(team, column, i, at, indent=2):
    a = column[i]
    t = T * indent
    right = f"#FCJH_MAP_ALERT_{team.upper()}_R" + (f"_{a.kind}" if a.kind else "")
    spot = (f'\t<Anchor side="Bottom" relative="{at[0]}" pos="{at[2]}" offset="{bottoms(team, a.kind)}"/>\n'
            f'\t<Anchor side="Right"  relative="{at[0]}" pos="{at[1]}" offset="{right}"/>\n'
            f'\t<Unclipped val="true"/>\n')
    out = f'{t}<!-- {team}, {"the bottom slot" if i == 0 else f"over {i} before it"}: {a.note} -->\n' if a.note else ""
    if a.box:
        # the spot takes the slot. The frame becomes the art's box with its top-right corner
        # where the art wants it - its parts draw only inside it (the panel was its box)
        l, tp, r, b = a.box
        frame = lambda name_, up: (
            f'{t}<Frame type="Frame" name="{name_}">\n'
            + "".join(f'{t}\t<Anchor side="{sd}"{" " * (6 - len(sd))} relative="$parent/{spot_name(a)}" '
                      f'pos="{pos}" offset="{off}"/>\n' for sd, pos, off in box_sides(a.box, up))
            + f'{t}\t<Unclipped val="true"/>\n')
        out += (f'{t}<Frame type="Frame" name="{spot_name(a)}">\n'
                + "".join(f"{t}{line}\n" for line in spot.splitlines())
                + f'{t}\t<Width val="{r - l}"/>\n{t}\t<Height val="{b - tp}"/>\n{t}\t<AcceptsMouse val="false"/>\n'
                + stack_states(team, column, i, ["$this"], at, indent + 1, a.kind) + f'{t}</Frame>\n')
        if a.spot_only:
            return out
        out += frame(a.name, 0) + intro(indent + 1, a.name not in FADE_ONLY) + a.extra + f"{t}</Frame>\n"
        # frames whose art hangs off this one's (their own box reaching `up` higher)
        for name_, up, xml in a.followers:
            out += (frame(name_, up) + ("" if name_ in NOT_BANNERS else intro(indent + 1, name_ not in FADE_ONLY))
                    + xml + f"{t}</Frame>\n")
        return out
    out += f'{t}<Frame type="Frame" name="{a.name}"' + (f' template="{a.template}"' if a.template else "") + ">\n"
    out += "".join(f"{t}{line}\n" for line in spot.splitlines())
    targets = ["$this"]
    if a.place:
        child, ctype = a.place.split(":")
        targets.append(f"$this/{child}")
        out += f'{t}\t<Frame type="{ctype}" name="{child}">\n'
        out += "".join(f"{t}\t{line}\n" for line in spot.splitlines())
        out += f'{t}\t</Frame>\n'
    out += stack_states(team, column, i, targets, at, indent + 1, a.kind)
    if team == "blue" and a.kind == "":
        out += "".join(f"{t}\t{line}\n" for line in MIRROR)
    return out + a.extra + f"{t}</Frame>\n"


# Blue's banners mirrored (user, 2026-10-09): Blizzard draws a NotificationFrameTemplate banner
# the same for either side, its hexagon at the right end - on blue's side that's the inner end,
# over blue's core bar. Blizzard's own mirror, NotificationFrameLeftTemplate (core
# mapmechanicpanel), puts the icon at the left end and keeps the bar's right end on the frame's:
# its anchors, laid over the frame. Across and up, nothing else moves: the bar still ends at
# blue's inner edge, at the same height.
MIRROR = (
    '<!-- mirrored for blue: the hexagon at the outer end (NotificationFrameLeftTemplate) -->',
    '<Frame type="Frame" name="NotificationIconAnchor">',
    '\t<Anchor side="Left"  relative="$parent/BackgroundImage" pos="Min" offset="16"/>',
    '\t<Anchor side="Right" relative="$this" pos="Min" offset="0"/>',
    '</Frame>',
    '<Frame type="Label" name="NotificationLabel">',
    '\t<Anchor side="Right" relative="$parent/BackgroundImage" pos="Max" offset="-25"/>',
    '</Frame>',
    '<Frame type="Image" name="BackgroundImage">',
    '\t<Anchor side="Right" relative="$parent" pos="Max" offset="-10"/>',
    '\t<Anchor side="Left"  relative="$parent/NotificationLabel" pos="Min" offset="-129"/>',
    '</Frame>',
)


class Node:
    """A frame override, and the frames under it, written once however many entries touch it."""

    def __init__(self, name, type_="Frame"):
        self.name, self.type, self.body, self.children = name, type_, "", {}

    def at(self, path):
        node = self
        for seg in path.split("/"):
            name, _, type_ = seg.partition(":")
            node = node.children.setdefault(name, Node(name, type_ or "Frame"))
        return node

    def xml(self, indent, file=None):
        t = T * indent
        out = f'{t}<Frame type="{self.type}" name="{self.name}"' + (f' file="{file}"' if file else "") + ">\n"
        out += self.body
        for c in self.children.values():
            out += c.xml(indent + 1)
        return out + f"{t}</Frame>\n"


def proxy_lines(down):
    """A map panel's MinimapProxyFrame (Blizzard's MechanicFrameTemplate), the stand-in for the
    minimap that the map's own frames hang off, tied to our minimap by its full path, `down`
    units lower. Blizzard's finds it by $parent/$parent/$parent: on Hanamura its frames stayed
    put both when the panel moved (they don't hang off the panel) and when the minimap did
    (user, 2026-10-14: "you didn't bring the alert with you"), while everything anchored to
    MinimapPanel by its full path follows it (our panels; Haunted Mines' plaque, Braxis's HUD)."""
    t = T * 2
    return (f'{t}<Frame type="Frame" name="MinimapProxyFrame">\n'
            + "".join(f'{t}\t<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{MINIMAP}/Minimap" pos="{pos}" '
                      f'offset="{down if sd in ("Top", "Bottom") else 0}"/>\n'
                      for sd, pos in (("Top", "Min"), ("Bottom", "Max"), ("Left", "Min"), ("Right", "Max")))
            + f'{t}</Frame>\n')


def shift_lines(down, depth):
    """A part anchored all round to its panel (`relative="$parent"`), `down` units lower in it."""
    return "".join(f'{T * depth}<Anchor side="{sd}" relative="$parent" pos="{pos}" offset="{down if sd in ("Top", "Bottom") else 0}"/>\n'
                   for sd, pos in (("Top", "Min"), ("Bottom", "Max"), ("Left", "Min"), ("Right", "Max")))


def map_file(key, at, down, bottoms, lifts):
    """Everything this map's own layout file gets: its panels on our minimap, the minimap's
    place (placer, in its first panel), its team alerts. bottoms, lifts: as layout's."""
    m = MAPS[key]
    root = Node(None)
    if m.lifts:
        # the lifting part pinned to the screen, its bottom where its panel's is with the map
        # lifted: Blizzard's hang only its bottom and middle off it (shrines.stormlayout). All
        # four sides: Blizzard's is one all-sides anchor, and overriding its bottom alone
        # showed nothing (fbebed4; rule 1)
        _, off = on_minimap("Bottom", "Max", 0, m, down.get(key, 0))
        t = T * (len(m.lifts.split("/")) + 1)
        root.at(m.lifts).body += (f'{t}<Anchor side="Top" relative="$parent" pos="Min" offset="0"/>\n'
                                  f'{t}<Anchor side="Left" relative="$parent" pos="Min" offset="0"/>\n'
                                  f'{t}<Anchor side="Right" relative="$parent" pos="Max" offset="0"/>\n'
                                  f'{t}<Anchor side="Bottom" relative="$GameUI" pos="Max" '
                                  f'offset="{bottoms[None] + lifts[key][1] + off}"/>\n'
                                  + lift_sensor(key, len(m.lifts.split("/")) + 1))
    for path, sides in m.panels.items():
        root.at(path).body += anchor_lines(sides, m, len(path.split("/")) + 1, down.get(key, 0))
        if m.proxy and "/" not in path:
            root.at(path).body += proxy_lines(down.get(key, 0))
    for part, (_, _, *hung) in m.gap_parts.items():
        depth = len(part.split("/")) + 1
        if hung:
            rel, pos, off = hung[0]
            root.at(part).body += f'{T * depth}<Anchor side="Bottom" relative="{rel}" pos="{pos}" offset="{off + down[key, part]}"/>\n'
        else:
            root.at(part).body += shift_lines(down[key, part], depth)
    for path, xml in PARTS.get(key, {}).items():
        root.at(path).body += "".join(T * (len(path.split("/")) + 1) + line + "\n" for line in xml.splitlines())
    if m.place:
        root.at(m.place[0]).body += placer(key, len(m.place[0].split("/")) + 1, lifts.get(key))
    for panel, cols in m.team.items():
        if panel == m.core:
            continue                  # in the core panel: core_panels
        node = root.at(panel)
        for team in ("blue", "red"):
            for i in range(len(cols.get(team, []))):
                node.body += alert_frame(team, cols[team], i, at)
    if m.extra:
        root.at(m.place[0]).body += EXTRAS[m.extra]()
    return "".join(c.xml(1, file=m.file) for c in root.children.values())


def core_alerts(m, at):
    """The alerts in an older map's core panel (its `team` entry for that panel)."""
    cols = m.team.get(m.core, {})
    return "".join(alert_frame(team, cols[team], i, at, 6)
                   for team in ("blue", "red") for i in range(len(cols.get(team, []))))


def core_panels(down, at, bottoms):
    """The older maps' panels in Blizzard's core MapMechanicPanel, on our minimap, with their
    alerts.
    No jitter (user, 2026-10-09): a map moved the minimap when its panel first SHOWED - the
    older five's at their first objective (Cursed Hollow's ~2:30), and newer maps whose script
    hides the panel while idle (Braxis). A newer map's panel exists only on that map, so its
    placer moves the minimap as soon as the panel exists. The older five's panels exist on
    every map, so a panel can't tell them apart - Blizzard's map id can, from the start
    (id_placers). One with own_place moves to its own place by it (Haunted Mines); the rest
    share FCJH_Minimap's place ([minimap] bottom). Either way each panel hangs off the
    minimap, tuned per map ([minimap.panel_nudge])."""
    core = {k: m for k, m in MAPS.items() if m.core}
    t = T * 5
    panels = "".join(f'{T*5}<Frame type="Frame" name="{m.core}">\n'
                     f'{T*6}<!-- {m.title} -->\n' + anchor_lines(BOTTOM_RIGHT, m, 6, down.get(k, 0))
                     + core_alerts(m, at) + (EXTRAS[m.extra]() if m.extra else "")
                     + f'{T*5}</Frame>\n' for k, m in core.items())
    own = [m.title for m in core.values() if m.own_place]
    shared = [m.title for m in core.values() if not m.own_place]
    return (f'{T*4}<!-- Older maps sharing FCJH_Minimap\'s place ([minimap] bottom), as the ARAM maps: '
            f'{", ".join(shared) or "none"}.\n'
            f'{T*4}     Placed by Blizzard\'s map id (tools/maps.py id_placers): {", ".join(own) or "none"} -->\n'
            f'{T*4}<Frame type="Frame" name="MapMechanicPanel">\n' + panels + f'{T*4}</Frame>\n')


def placer(key, indent, lifted=None):
    """A frame inside the map's panel - which exists only on this map - that moves the minimap
    to this map's place as soon as the script builds the panel, shown or hidden: one state, no
    condition (a state group runs on a hidden frame too). It used to wait for the panel to
    SHOW, and the minimap jumped when it did (Braxis hides its panel while idle; user,
    2026-10-09). A condition on the panel from the minimap can't be written instead: the panel
    doesn't exist until the script makes it (validate.py refuses it)."""
    t = T * indent
    return (f'{t}<!-- the minimap\'s place on {MAPS[key].title}, from the moment this panel exists -->\n'
            f'{t}<Frame type="Frame" name="FCJH_MinimapPlace">\n'
            f'{t}\t<Anchor relative="$parent"/>\n'
            f'{t}\t<AcceptsMouse val="false"/>\n'
            f'{t}\t<StateGroup name="FCJH_Place">\n'
            f'{t}\t\t<DefaultState val="Placed"/>\n'
            f'{t}\t\t<State name="Placed">\n'
            + place_actions(key, indent + 3) +
            f'{t}\t\t</State>\n'
            f'{t}\t</StateGroup>\n'
            + (lift(key, lifted, indent + 1) if lifted else "") +
            f'{t}</Frame>\n')


MAP_ID ="libCore_gv_mAPMapStringID"   # Blizzard's script variable naming the map (MAP_IDS)
MAP_ID_READER = "$GameUI/FCJH_MapId"   # ours, reading it (id_placers)


def on_map(key, reader=MAP_ID_READER):
    """A state's condition: we're on this map. Holds from the match's start and never changes -
    a group in a state on it never leaves it (leaving undoes its actions). Put such a group in
    a frame that's always shown: in a hidden one (Haunted Mines' core panel) it never ran."""
    return f'<When type="Property" frame="{reader}" StringValue="{MAP_IDS[key]}"/>'


GLIDE_S = 1.0         # seconds the minimap takes to glide to its place (opens)
GLIDE_STEPS = 10      # keys along it, eased in and out


def glide_keys(ends, indent):
    """The minimap's bottom from ends[0] to ends[1], eased in and out over GLIDE_S."""
    t = T * indent
    ease = lambda f: f * f * (3 - 2 * f)
    return "".join(f'{t}\t\t<Key type="Curve" time="{round(GLIDE_S * n / GLIDE_STEPS, 2)}" '
                   f'value="{round(ends[0] + (ends[1] - ends[0]) * ease(n / GLIDE_STEPS))}"/>\n'
                   for n in range(GLIDE_STEPS + 1))


def lift(key, ends, indent):
    """While the map's `lifts` part shows, the minimap glides up out of its way, and back down
    when it hides - every time (user, 2026-10-15: Infernal Shrines' skull race; Haunted Mines'
    glide goes up once and stays). One animation, played forwards to lift and backwards to
    settle: from wherever it is, so a settle mid-lift turns round. ends: (from, to), as glide's -
    counted from the minimap's LAYOUT anchor, not the placer's. Settled, it rests at its first
    key: the placer's own place. In the map's own panel, the placer's frame: the part's path
    exists only on this map. Played by lift_sensor, inside the part."""
    t = T * indent
    return (f'{t}<!-- {MAPS[key].title}: the minimap up while {MAPS[key].lifts.split("/")[-1]} shows, '
            f'back down when it hides (maps.lift) -->\n'
            f'{t}<Animation name="FCJH_Lift">\n'
            f'{t}\t<Event event="FCJH_Lift" action="DirectionForward,Play"/>\n'
            f'{t}\t<Event event="FCJH_Settle" action="DirectionReverse,Play"/>\n'
            f'{t}\t<Controller type="Anchor" end="Pause" side="Bottom" relative="true" frame="{MINIMAP}">\n'
            + glide_keys(ends, indent) +
            f'{t}\t</Controller>\n'
            f'{t}</Animation>\n')


def lift_sensor(key, indent):
    """lift's trigger: a frame inside the lifting part, its group on the part's own Visible
    ($parent, rule 30 - it runs while the part is hidden), playing the placer's animation. In
    the placer, watching the part by name, it never fired (135435c): the placer comes before
    the part in the panel (rule 34). The animation stays in the placer: shown while the part
    hides (Punisher mode), so the settle still runs (rule 11)."""
    t = T * indent
    place = "$parent/" * len(MAPS[key].lifts.split("/")[1:]) + "$parent/FCJH_MinimapPlace"
    return (f'{t}<!-- {MAPS[key].title}: lifts the minimap while this shows (maps.lift_sensor) -->\n'
            f'{t}<Frame type="Frame" name="FCJH_LiftSensor">\n'
            f'{t}\t<Anchor relative="$parent"/>\n'
            f'{t}\t<AcceptsMouse val="false"/>\n'
            f'{t}\t<StateGroup name="FCJH_Lift">\n'
            f'{t}\t\t<DefaultState val="Settled"/>\n'
            f'{t}\t\t<State name="Lifted">\n'
            f'{t}\t\t\t<When type="Property" frame="$parent" Visible="true"/>\n'
            f'{t}\t\t\t<Action type="SendEvent" frame="{place}" event="FCJH_Lift"/>\n'
            f'{t}\t\t</State>\n'
            f'{t}\t\t<State name="Settled">\n'
            f'{t}\t\t\t<Action type="SendEvent" frame="{place}" event="FCJH_Settle"/>\n'
            f'{t}\t\t</State>\n'
            f'{t}\t</StateGroup>\n'
            f'{t}</Frame>\n')


def glide(key, ends, indent):
    """A map that opens on part of its map (launch_cut): when its `opens` frame first shows,
    the minimap glides up to its place, and stays for the rest of the game (user, 2026-10-09).
    ends: (from, to), the minimap's bottom in units from FCJH_Minimap's own anchor ([minimap]
    bottom) - a relative Anchor controller counts from the anchor in the layout, NOT from where
    a state's SetAnchor put it: counted from the launch place, the map went 125 px too high
    (user, 2026-10-09: the first keys ran 0 -> -183, and it stopped at the shared place - 183). The script shows the frame while the panel is up, every time the objective
    comes round (Haunted Mines' skull counts, at each mines opening): "Open" sends the glide
    while it shows, unless FCJH_Opened is up - the glide puts that up, for good, so the next
    time nothing plays. Its first key is the launch place, so it starts where the map sits;
    end="Pause" holds its last key."""
    t = T * indent
    keys = glide_keys(ends, indent)
    return (f'{t}<!-- {MAPS[key].title}: the whole map once {MAPS[key].opens.split("/")[-1]} first shows, gliding up (maps.glide) -->\n'
            f'{t}<Frame type="Frame" name="FCJH_Opened">\n'
            f'{t}\t<Anchor relative="$parent"/>\n{t}\t<Visible val="false"/>\n{t}\t<AcceptsMouse val="false"/>\n'
            f'{t}</Frame>\n'
            f'{t}<Animation name="FCJH_Glide">\n'
            f'{t}\t<Event event="FCJH_Open" action="Play"/>\n'
            f'{t}\t<Controller type="Anchor" end="Pause" side="Bottom" relative="true" frame="{MINIMAP}">\n'
            + keys +
            f'{t}\t</Controller>\n'
            f'{t}\t<Controller type="Visibility" end="Pause" frame="FCJH_Opened">\n'
            f'{t}\t\t<Key type="Bool" time="0" value="true"/>\n'
            f'{t}\t</Controller>\n'
            f'{t}</Animation>\n'
            f'{t}<StateGroup name="FCJH_Open">\n'
            f'{t}\t<DefaultState val="Shut"/>\n'
            f'{t}\t<State name="Open">\n'
            f'{t}\t\t{on_map(key, "$parent/FCJH_MapId")}\n'
            f'{t}\t\t<When type="Property" frame="{MECHANICS}/{MAPS[key].opens}" Visible="true"/>\n'
            f'{t}\t\t<When type="Property" frame="$this/FCJH_Opened" Visible="false"/>\n'
            f'{t}\t\t<Action type="SendEvent" frame="$this" event="FCJH_Open"/>\n'
            f'{t}\t</State>\n'
            f'{t}\t<State name="Shut"/>\n'
            f'{t}</StateGroup>\n')


def id_placers(glides):
    """The older maps' own minimap places from the match's start. Their panels exist on every
    map, so a panel can't tell its map apart - Blizzard's map id can: a DataRefFrame reads the
    script variable (Spazzo's way, CustomPanelSpazzo), and each map's one state matches its id.
    Read on screen 2026-10-09: "HauntedMines" on Haunted Mines, "BraxisHoldout" on Braxis.
    Straight in GameUI, never hidden: inside Haunted Mines' panel - hidden from the start - the
    same reader never placed the minimap, while a diagnostic's here read the id (user,
    2026-10-09). The id never changes, so a group never leaves its state (leaving undoes its
    actions). "Other", with no condition, is the fallback when nothing matches - the DefaultState."""
    t = T * 2
    out = (f'{t}<!-- the older maps\' own minimap places, from the start: Blizzard\'s map id (tools/maps.py id_placers) -->\n'
           f'{t}<Frame type="DataRefFrame" name="FCJH_MapId">\n'
           f'{t}\t<Argument name="GalaxyVar" val="{MAP_ID}"/>\n'
           f'{t}</Frame>\n')
    for key, m in MAPS.items():
        if m.own_place:
            out += (f'{t}<Frame type="Frame" name="FCJH_MinimapPlace{MAP_IDS[key].replace(" ", "")}">\n'
                    + (f'{t}\t<Anchor relative="$parent"/>\n' if m.opens else "") +   # the glide's frame, as FCJH_TownWatch
                    f'{t}\t<AcceptsMouse val="false"/>\n'
                    f'{t}\t<StateGroup name="FCJH_Place">\n'
                    f'{t}\t\t<DefaultState val="Other"/>\n'
                    f'{t}\t\t<State name="Placed">\n'
                    f'{t}\t\t\t{on_map(key, "$parent/FCJH_MapId")}\n'
                    + place_actions(key, 5) +
                    f'{t}\t\t</State>\n'
                    f'{t}\t\t<State name="Other"/>\n'
                    f'{t}\t</StateGroup>\n'
                    + (glide(key, glides[key], 3) if m.opens else "") +
                    f'{t}</Frame>\n')
    return out


def layout(header, at, down, bottoms, glides, lifts):
    """FCJH_Maps.StormLayout. at: (frame, across pos, down pos), where the plates are anchored -
    the stacks' constants run from there, as the plates' do (gen.py PLATES_AT). down: {map key:
    units}, how much lower each map's panel goes (layout.toml [minimap.panel_nudge]). bottoms:
    the minimap's bottom, units from the screen's: {None: the shared place, map key: its own}
    (gen.py minimap_bottoms). glides: {map key: (from, to)}, the minimap's bottom at load and in
    full, units from the shared place, for a map that opens on part of its map (launch_cut; glide).
    lifts: {map key: (from, to)}, the same, settled and lifted, for a map with `lifts` (lift)."""
    return header + f'''
	<!-- Each battleground's own UI on our screen (tools/maps.py, which says how a map's UI works).

	     Per map: the minimap's place - the map drawn with its bottom on the screen's padding
	     line, as the plates ([minimap] nudge to adjust one); the map's objective panel moved
	     with the minimap, so it sits round ours as it sat round Blizzard's; and the alerts that
	     belong to a team in a stack on that team's side of the map, on its plates' inner end
	     (user, 2026-10-05/06): on the XP bar, or the core bar while that shows (Blizzard shows
	     it while the core takes damage), one slot up for each alert below it that's showing.
	     Neutral alerts join red's stack: red shares its side with them (user, 2026-10-06).

	     The older five maps' panels are Blizzard's core ones, here first; then each newer map's
	     own file. -->
	<Frame type="GameUI" name="GameUI" file="GameUI">
		<Frame type="Frame" name="UIContainer">
			<Frame type="Frame" name="ConsoleUIContainer">
{core_panels(down, at, bottoms)}			</Frame>
		</Frame>
{id_placers(glides)}	</Frame>
''' + "".join(f"\t<!-- ===== {MAPS[k].title}{(': ' + MAPS[k].notes) if MAPS[k].notes else ''} ===== -->\n"
              + map_file(k, at, down, bottoms, lifts) for k in MAPS if MAPS[k].file) + "</Desc>\n"
