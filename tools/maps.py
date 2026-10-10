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
# "ICON": placed by its icon box (Hanamura's attacking pair: a background 300 left of a 112-unit
# icon box, from the template). "BANNER" and "HOLDOUT": the older maps' centre banners, placed
# by a spot of ours the size of the art (Alert.box) - set with their boxes, below.
ALERT_ART = {
    "": Art(499, 12, bar_up=20, below=14, height=117),   # reach 500 put its tip 1 px past red's plates
    "ICON": Art(412, 0, measured=False, note="Hanamura's attacking alerts: all of it"),
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
    fix: str = ""                     # extra SetAnchors when this map's minimap is placed
    team: dict = field(default_factory=dict)     # {"blue": [Alert...], "red": [...]}: panel -> column
    extra: str = ""                   # map-specific XML in its file's panel (see TOWERS_EXTRA)
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


RAVEN = MECHANICS + "/RavenCourtPanel"
CURSE = RAVEN + "/CurseFrame"
CURSE_SPARE = 200     # red's curse box reaches this much further right: its hexagon follows the
                      # text, and a long translation pushes it past the tribute's box
# The curse's words on red's side: ours, the same text and style as Blizzard's label, but
# placed from the bar's LEFT end - Blizzard's is placed from the hexagon (cursed_side).
CURSE_TEXT = (f'{T*7}<Frame type="Label" name="FCJH_CurseText">\n'
              f'{T*8}<Anchor side="Bottom" relative="$parent/BackgroundImage" pos="Max" offset="-10"/>\n'
              f'{T*8}<Anchor side="Left"   relative="$parent/BackgroundImage" pos="Min" offset="35"/>\n'
              f'{T*8}<Text val="{{$parent/CurseInfoLabel/@Text}}"/>\n'
              f'{T*8}<Style val="{{$parent/CurseInfoLabel/@Style}}"/>\n'
              f'{T*8}<Options val="NoWrapping"/>\n'
              f'{T*8}<Alpha val="0"/>\n'
              f'{T*7}</Frame>\n')
# The curse's countdown in its bar after the words, as the tribute's (user, 2026-10-06), one
# space after them; Blizzard's (in the raven head) hidden. Two of ours, one per side's layout
# (cursed_side): red's after our words, flowing right; blue's where Blizzard ends the words
# (the bar's right end -130), Blizzard's words ending one space before it.
CURSE_WORDS_END = -130
CURSE_COUNT = "".join(
    f'{T*7}<Frame type="Label" name="{name_}">\n'
    + "".join(f'{T*8}<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
              for sd, rel, pos, off in anchors)
    + f'{T*8}<Text val="{{$parent/CurseTimerLabel/@Text}}"/>\n'
    f'{T*8}<Style val="{{$parent/CurseInfoLabel/@Style}}"/>\n'
    f'{T*8}<Options val="NoWrapping"/>\n{T*8}<Unclipped val="true"/>\n{T*8}<Alpha val="0"/>\n'
    f'{T*7}</Frame>\n'
    for name_, anchors in (
        ("FCJH_CurseCount", (("Top", "$parent/FCJH_CurseText", "Min", 0), ("Bottom", "$parent/FCJH_CurseText", "Max", 0),
                             ("Left", "$parent/FCJH_CurseText", "Max", COUNT_SPACE))),
        ("FCJH_CurseCountBlue", (("Top", "$parent/CurseInfoLabel", "Min", 0), ("Bottom", "$parent/CurseInfoLabel", "Max", 0),
                                 ("Right", "$parent/BackgroundImage", "Max", CURSE_WORDS_END)))))


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
    count, blue_count = f"{CURSE}/FCJH_CurseCount", f"{CURSE}/FCJH_CurseCountBlue"
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
            + label("FCJH_CurseColonBlue", "$parent/CurseInfoLabel", "Right", "$parent/FCJH_CurseCountBlue", "Min",
                    -COUNT_SPACE))


def tribute_count():
    """The tribute's countdown in its bar, after the words, as Towers of Doom's altar countdown
    (Blizzard's NotificationFrameCountdownTemplate: words then count, in the words' style; user,
    2026-10-06) - Blizzard's hung under the hexagon, onto the XP bar. Ours reads Blizzard's
    (hidden) and shows while the script shows it: the spawn countdown, not "Collect the Tribute"
    (uilib.galaxy hides the count then). While it counts, our words in the game's language
    ("Tribute Spawns In", TRIBUTE_SPAWNS_IN) replace Blizzard's. They flow as text: the words
    from the bar's left end, as the red curse's, the count one space after them, middle to
    middle (user, 2026-10-06). "Collect the Tribute" stays Blizzard's (user: good); in a
    language not listed, Blizzard's words and count stand."""
    tribute = RAVEN + "/TributeSpawnFrame"
    info, count, words = f"{tribute}/TributeInfoLabel", f"{tribute}/FCJH_TributeCount", f"{tribute}/FCJH_TributeWords"
    timer = f"{tribute}/TributeTimerLabel"
    alpha = lambda frame, a: f'<Action type="SetProperty" frame="{frame}" Alpha="{a}"/>'
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
                     + alpha(words, 255) + alpha(count, 255) + alpha(info, 0) + alpha(timer, 0) + "</State>\n"
                     for i, (theirs, ours) in enumerate(TRIBUTE_SPAWNS_IN.items()))
    group = (f'{t}<StateGroup name="FCJH_TributeWords">\n{t}\t<DefaultState val="Words"/>\n' + states
             + f'{t}\t<State name="Counting">{counting}' + alpha(words, 0) + alpha(count, 0)
             + alpha(info, 255) + alpha(timer, 255) + "</State>\n"
             f'{t}\t<State name="Words">' + alpha(words, 0) + alpha(count, 0) + alpha(info, 255) + "</State>\n"
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
                f'<Anchor side="Right" relative="$parent/FCJH_CurseCountBlue" pos="Min" offset="{-COUNT_SPACE}"/>'),
               ("Label", "CurseTimerLabel", (), '<Alpha val="0"/>'),
               ("Frame", "AttentionEffect", (("Image", "AttentionEffectImage", ()),
                                             ("Image", "AttentionEffect2Image", ()))))


def cursed_side():
    """The curse banner on the cursed team's side (user, 2026-10-06). It hangs off the tribute
    banner's frame, which the script hides while a curse is on: when the banner says blue,
    both frames move onto blue's spot; otherwise they stay on red's (red's side holds the
    tribute banner, the neutral one).
    Blizzard sizes the banner to its words, the hexagon at its right end. That suits blue's
    side - the hexagon at the minimap, the bar growing outward - but on red's a short text
    left the bar's start far from the minimap (user). So on red the banner is laid out from
    its left end: the bar starts at the spot's left, our copy of the words after it, the
    count after them (CURSE_COUNT), the hexagon after that."""
    t = T * 7
    act = lambda frame, sd, rel, pos, off: (f'<Action type="SetAnchor" frame="{frame}" side="{sd}" relative="{rel}" '
                                            f'pos="{pos}" offset="{off}"/>')
    def place(spot, red):
        out = "".join(act(frame, sd, f"{RAVEN}/{spot}", pos, off + (CURSE_SPARE if red and frame == CURSE and sd == "Right" else 0))
                      for frame, up in ((f"{RAVEN}/TributeSpawnFrame", 0), (CURSE, CURSE_UP))
                      for sd, pos, off in box_sides(TRIBUTE_BOX, up))
        tribute = f"{RAVEN}/TributeSpawnFrame"
        if red:
            out += (act(f"{CURSE}/BackgroundImage", "Left", CURSE, "Min", 0)
                    + act(f"{CURSE}/TimerImage", "Right", f"{CURSE}/FCJH_CurseCount", "Max", 115))
        else:      # Blizzard's own layout, the count before the hexagon
            out += (act(f"{CURSE}/BackgroundImage", "Left", f"{CURSE}/CurseInfoLabel", "Min", -35)
                    + act(f"{CURSE}/TimerImage", "Right", f"{tribute}/TimerImage", "Max", 0))
        shown = lambda frame, on: f'<Action type="SetProperty" frame="{CURSE}/{frame}" Alpha="{255 if on else 0}"/>'
        return (out + shown("CurseInfoLabel", not red) + shown("FCJH_CurseCountBlue", not red)
                + shown("FCJH_CurseColonBlue", not red) + shown("FCJH_CurseText", red)
                + shown("FCJH_CurseCount", red) + shown("FCJH_CurseColon", red))
    out = f'{t}<StateGroup name="FCJH_CursedSide">\n{t}\t<DefaultState val="Red"/>\n'
    for n, text in enumerate(BLUE_CURSED):
        out += (f'{t}\t<State name="Blue{n}"><When type="Property" frame="{CURSE}" Visible="true"/>'
                f'<When type="Property" frame="{CURSE}/CurseInfoLabel" Text="{text}"/>'
                f'{place("FCJH_CurseFrameSpot", False)}</State>\n')
    return out + f'{t}\t<State name="Red">{place("FCJH_TributeSpawnFrameSpot", True)}</State>\n{t}</StateGroup>\n'


# ------------------------------------------------------------------ Haunted Mines' banner

# "Mines will open in: 0:23" (core MapMechanicPanel, HauntedMinesPanel/MineTimerModeFrame): its
# hexagon (CenterpieceImageMine) pinned 20 in from the frame's top-right, the bar ending 15
# past it and starting 50 before its words - Blizzard sizes it to them, growing left. Measured
# at 1080p (2026-10-09): the bar 385 px wide in English (428 units), its bottom 86 under the
# hexagon's top as placed (the frame's 27 + 50 = 77 put the bar's bottom edge 8 px under the
# tribute's and Towers', user - read by the bar's lower bracket: 937 against 929). On red's side
# it's laid out from its left end, as red's curse is (cursed_side): the bar from the spot's
# left, our copy of the words 50 in, the count one space after them, the hexagon after that -
# so in every language the bar starts at red's plates.
MINES_BOX = (-433, 0, -5, 86)
MINES_WORDS_START = 50
MINES_TIP_IN = 3          # the bar art's left tip is 3 px inside its frame: the frame starts that
                          # much left of the spot, for the tip to sit on red's plates' edge (1167) as
                          # Towers' and Braxis's do (measured at its tip 2026-10-09: 1170; a first
                          # read along one row for every bar said 1177)
MINES_HEX_AFTER = 115     # the hexagon's right from the count's: 5 + its width, as the curse's
                          # (measured: 106 px from the count's last letter to its right edge)
ALERT_ART["MINES"] = Art(MINES_BOX[2] - MINES_BOX[0], 0, height=MINES_BOX[3] - MINES_BOX[1] + 6)
MINES_TEXT = "".join(
    f'{T*7}<Frame type="Label" name="{name_}">\n'
    + "".join(f'{T*8}<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
              for sd, rel, pos, off in anchors)
    + f'{T*8}<Text val="{{$parent/{theirs}/@Text}}"/>\n{T*8}<Style val="{{$parent/{theirs}/@Style}}"/>\n'
    f'{T*8}<Options val="NoWrapping"/>\n{T*8}<Unclipped val="true"/>\n{T*7}</Frame>\n'
    for name_, theirs, anchors in (
        ("FCJH_MinesText", "MineOpenLabel", (("Top", "$parent/MineOpenLabel", "Min", 0),
                                             ("Bottom", "$parent/MineOpenLabel", "Max", 0),
                                             ("Left", "$parent/BackgroundImage", "Min", MINES_WORDS_START))),
        ("FCJH_MinesCount", "MineOpenTimer", (("Top", "$parent/FCJH_MinesText", "Min", 0),
                                              ("Bottom", "$parent/FCJH_MinesText", "Max", 0),
                                              ("Left", "$parent/FCJH_MinesText", "Max", COUNT_SPACE)))))
MINES_PARTS = (("Image", "BackgroundImage", (), f'<Anchor side="Left" relative="$parent" pos="Min" offset="{-MINES_TIP_IN}"/>'),
               ("Image", "CenterpieceImageMine", (),
                f'<Anchor side="Right" relative="$parent/FCJH_MinesCount" pos="Max" offset="{MINES_HEX_AFTER}"/>'),
               ("Label", "MineOpenLabel", (), '<Alpha val="0"/>'),
               ("Label", "MineOpenTimer", (), '<Alpha val="0"/>'))
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


# ------------------------------------------------------------------ Dragon Shire's banners

# "Shrines activate in: 0:02" (core MapMechanicPanel, DragonShirePanel/ShrineTimerModeFrame),
# built as the mines' (user, 2026-10-09: "move that spawn banner to the right"): its hexagon
# (CenterpieceImage, the dragonstone) pinned to the frame's top-right, 10 in; the bar ending 10
# past it, starting 35 before its words, the count right-aligned in the 50 before the hexagon -
# Blizzard sizes it to its words, growing left. Measured at 1080p (2026-10-09, at Blizzard's
# place, the panel's top-right at 1184, 718): the bar 382 px from its tip to its end in English,
# its lower bracket 113 units under the frame's top (y 820); the hexagon's bottom 835. On red's
# side laid out from its left end, as the mines': the bar from the spot's left, our copy of the
# words 35 in, the count one space after them, the hexagon after that.
SHRINE_BOX = (-432, 0, 0, 113)
SHRINE_WORDS_START = 35
SHRINE_HEX_AFTER = 121     # the hexagon's right from the count's (measured: 112 px from the count's
                           # last letter to its box's right, less the label's padding, as the mines')
ALERT_ART["SHRINE"] = Art(SHRINE_BOX[2] - SHRINE_BOX[0], 0, height=130)   # down to the hexagon's bottom
SHRINE_TEXT = "".join(
    f'{T*7}<Frame type="Label" name="{name_}">\n'
    + "".join(f'{T*8}<Anchor side="{sd}"{" " * (6 - len(sd))} relative="{rel}" pos="{pos}" offset="{off}"/>\n'
              for sd, rel, pos, off in anchors)
    + f'{T*8}<Text val="{{$parent/{theirs}/@Text}}"/>\n{T*8}<Style val="{{$parent/{theirs}/@Style}}"/>\n'
    f'{T*8}<Options val="NoWrapping"/>\n{T*8}<Unclipped val="true"/>\n{T*7}</Frame>\n'
    for name_, theirs, anchors in (
        ("FCJH_ShrineText", "ShrineActivateLabel", (("Top", "$parent/ShrineActivateLabel", "Min", 0),
                                                    ("Bottom", "$parent/ShrineActivateLabel", "Max", 0),
                                                    ("Left", "$parent/BackgroundImage", "Min", SHRINE_WORDS_START))),
        ("FCJH_ShrineCount", "ShrineActivateTimer", (("Top", "$parent/FCJH_ShrineText", "Min", 0),
                                                     ("Bottom", "$parent/FCJH_ShrineText", "Max", 0),
                                                     ("Left", "$parent/FCJH_ShrineText", "Max", COUNT_SPACE)))))
SHRINE_PARTS = (("Image", "BackgroundImage", (), f'<Anchor side="Left" relative="$parent" pos="Min" offset="{-MINES_TIP_IN}"/>'),
                ("Image", "CenterpieceImage", (),
                 f'<Anchor side="Right" relative="$parent/FCJH_ShrineCount" pos="Max" offset="{SHRINE_HEX_AFTER}"/>'),
                ("Label", "ShrineActivateLabel", (), '<Alpha val="0"/>'),
                ("Label", "ShrineActivateTimer", (), '<Alpha val="0"/>'))
# The Dragon Knight (DragonModeFrame, shown instead once a team holds both shrines): Blizzard pins
# its bar's bottom-right to the countdown's bar's, the dragon's head (DragonHud), its timer and
# health bar all hanging off its bar. Ours from the spot's left, as the golems': its bar at its
# texture's own width (481, as the golems'; measured 432 px), its bottom still on the countdown's.
# Its timer (how long the knight lasts) hung under the dragon's head, below the bar - up beside
# the % instead, on the "DRAGON KNIGHT" row, in that row's small style (user, 2026-10-09).
DRAGON_TIMER_GAP, DRAGON_TIMER_W = -2, 80  # its right this far from the %'s box's left (the %'s
                                           # figures start there: at 8 its last digit ran ~2 px into
                                           # the %; user, 2026-10-09: padding before the %); its width
_ROW = "$parent/DragonInfoLabel"
_PCT_BOX = "$parent/DragonHealthBar/HealthLabel"
DRAGON_TIMER = "\n".join((
    f'<Anchor side="Top"    relative="{_ROW}" pos="Min" offset="0"/>',
    f'<Anchor side="Bottom" relative="{_ROW}" pos="Max" offset="0"/>',
    f'<Anchor side="Right"  relative="{_PCT_BOX}" pos="Min" offset="{DRAGON_TIMER_GAP}"/>',
    f'<Anchor side="Left"   relative="{_PCT_BOX}" pos="Min" offset="{DRAGON_TIMER_GAP - DRAGON_TIMER_W}"/>',
    '<Style val="Storm_MapMechanic_MechanicCounterSmallRight_Blue"/>'))
DRAGON_PARTS = (("Image", "BackgroundImage", (), f'<Anchor side="Right" relative="$parent" pos="Min" offset="{GOLEM_BAR}"/>'),
                ("Image", "HealthBarBG", ()), ("Image", "DragonHud", ()),
                ("Label", "DragonTimer", (), DRAGON_TIMER), ("Label", "DragonInfoLabel", ()),
                ("UnitStatusFrame", "DragonHealthBar", _HEALTH))


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
SKULL_PLAQUE_DOWN_PX = 2   # its middle 2 px under the gap's (user, 2026-10-09, by eye)
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


# ------------------------------------------------------------------ the maps

BOTTOM_RIGHT = (("Bottom", "Max", 0), ("Right", "Max", 0))     # pinned to the screen's corner
STRIP = (("Top", "Min", 0), ("Bottom", "Max", 0), ("Right", "Max", 0))   # down the right edge
SCREEN = (("Top", "Min", 0), ("Bottom", "Max", 0), ("Left", "Min", 0), ("Right", "Max", 0))

# Art: each map's CustomMiniMap, the opaque part, read from the map archives in Battle.net's
# cache (2026-10-06; the battlegrounds aren't in the game's own storage).
MAPS = {
    "alterac_pass": Map(
        "Alterac Pass", (441, 316), file="AlteracMechanics",
        panels={"AlteracMechanicsPanel": (("Top", "Min", -25), ("Bottom", "Max", -25), ("Right", "Max", 0))},
        place=("AlteracMechanicsPanel",),
        notes="a strip down the right edge; the cage fight bar and its two event banners at its middle"),
    "battlefield_of_eternity": Map(
        "Battlefield of Eternity", (438, 269), file="BossDuel", minimap=(75, 0),
        panels={"BossDuelPanel": BOTTOM_RIGHT}, place=("BossDuelPanel",)),
    "blackhearts_bay": Map("Blackheart's Bay", (452, 313), core="BlackheartsBayPanel"),
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
        # "Tribute spawning" / "Collect the tribute": one neutral banner, on red's side. Its art:
        # the hexagon pinned 20 in from the frame's top-right, the bar 481 wide ending 15 past it,
        # the count under the hexagon (measured in game, 2026-10-06). The curse banner hangs off
        # the same hexagon (CurseFrame/TimerImage) and goes to the cursed team's side
        # (cursed_side): red's is the tribute's spot, blue's a spot of its own.
        team={"RavenCourtPanel": {
            "blue": [Alert("CurseFrame", kind="BANNER", box=TRIBUTE_BOX, spot_only=True,
                           note="the curse, when it's on blue")],
            "red": [Alert("TributeSpawnFrame", kind="BANNER", box=TRIBUTE_BOX,
                          followers=(("CurseFrame", CURSE_UP, CURSE_TEXT + CURSE_COUNT + curse_colon() + unclipped(CURSE_PARTS)),),
                          extra=cursed_side() + tribute_count() + unclipped(TRIBUTE_PARTS),
                          note="the tribute spawning, then waiting to be collected (neutral); the curse on red")]}},
        notes="the tribute counts sit at the minimap's bottom corners"),
    "dragon_shire": Map(
        "Dragon Shire", (434, 282), core="DragonShirePanel",
        # "Shrines activate in", then the Dragon Knight in its place: one neutral banner, on red's
        # side. The shrine markers (ShrineModeFrame: each team's moon and star, lit while it holds
        # them) stay on the panel, pinned to the screen's bottom as Blizzard's:
        # [minimap.panel_nudge] puts them on the padding line.
        team={"DragonShirePanel": {
            "red": [Alert("ShrineTimerModeFrame", kind="SHRINE", box=SHRINE_BOX,
                          followers=(("DragonModeFrame", 0, unclipped(DRAGON_PARTS)),),
                          extra=SHRINE_TEXT + unclipped(SHRINE_PARTS),
                          note="the shrines' countdown, then the Dragon Knight (neutral)")]}}),
    "garden_of_terror": Map(
        "Garden of Terror", (438, 270), core="GardenOfTerrorPanel", file="GardenMapMechanic",
        panels={"GardenTerrorHealthFrame": (("Top", "Min", 220), ("Bottom", "Max", 220), ("Right", "Max", 0))},
        notes="its night warning and seed frames are placed from the minimap already"),
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
        # "Attacking the core": one frame per team, shown to everyone, by the attacking team
        # (the map script, libmhmu: lv_attackingStructureFrame[team]) - Order is blue. Placed
        # by its icon box (its art hangs off that, not off the frame).
        team={"HanamuraReworkVictoryShotsStatusPanel": {
            "blue": [Alert("AttackingCoreFrame_Order", kind="ICON", place="NotificationIconAnchor:Image",
                           note="blue's payload on a fort")],
            "red": [Alert("AttackingCoreFrame_Chaos", kind="ICON", place="NotificationIconAnchor:Image",
                          note="red's payload on a fort")]}}),
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
                          extra=MINES_TEXT + unclipped(MINES_PARTS),
                          note="the mines opening, then the golems (neutral)")]}},
        extra="skulls"),
    "infernal_shrines": Map(
        "Infernal Shrines", (458, 301), file="Shrines",
        panels={"ShrinesPanel": BOTTOM_RIGHT}, place=("ShrinesPanel",)),
    "sky_temple": Map(
        "Sky Temple", (437, 344), file="CapturePoints",
        panels={"CapturePointsPanel": BOTTOM_RIGHT}, place=("CapturePointsPanel",)),
    "tomb_of_the_spider_queen": Map(
        "Tomb of the Spider Queen", (430, 262), file="SoulCage",
        panels={"CryptPanel": BOTTOM_RIGHT}, place=("CryptPanel",)),
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
        notes="the capture point's hex is placed from the minimap; its strip clipped it"),
    "warhead_junction": Map(
        "Warhead Junction", (460, 390), file="SCMap2", minimap=(0, 0), place=("SC2Panel",),
        # its file nudges the map 30 units right in the minimap panel: back to the square's place
        fix=f'<Action type="SetAnchor" frame="{MINIMAP}/Minimap" side="Left" relative="{MINIMAP}" pos="Min" offset="0"/>',
        notes="its panel is placed from the minimap already"),
}
EXTRAS = {"towers": towers_extra, "skulls": skulls_extra}

# Blizzard's map id per map: the script variable libCore_gv_mAPMapStringID, which a layout can
# read from the match's start, on any map (id_placers, on_map; user, 2026-10-09). Where each is
# from: GAME read on screen in game; SCRIPT tested by Blizzard's own scripts (Jamie Phan
# gamelib.galaxy / uilib.galaxy - the battlegrounds' own scripts aren't in it); SPAZZO tested in
# Spazzo's interface (CustomPanelSpazzo) only - read one on screen before relying on it.
MAP_IDS = {
    "alterac_pass": "AlteracPass",                    # SPAZZO
    "battlefield_of_eternity": "BattlefieldOfEternity",  # SCRIPT
    "blackhearts_bay": "BlackheartsBay",              # SPAZZO
    "braxis_holdout": "BraxisHoldout",                # GAME (2026-10-09)
    "cursed_hollow": "CursedHollow",                  # GAME (2026-10-09; CursedHollowSandbox: the sandbox's)
    "dragon_shire": "DragonShire",                    # GAME (2026-10-09)
    "garden_of_terror": "HauntedWoods",               # SPAZZO
    "hanamura_temple": "Hanamura",                    # SPAZZO
    "haunted_mines": "HauntedMines",                  # GAME (2026-10-09)
    "infernal_shrines": "Shrines",                    # SCRIPT
    "sky_temple": "ControlPoints",                    # SCRIPT
    "tomb_of_the_spider_queen": "Crypts",             # SCRIPT
    "towers_of_doom": "TowersOfDoom",                 # GAME (2026-10-09)
    "volskaya_foundry": "Volskaya",                   # SCRIPT
    "warhead_junction": "Warhead Junction",           # SCRIPT - with the space
}
assert set(MAP_IDS) == set(MAPS), f"MAP_IDS: every map needs its id - {set(MAPS) ^ set(MAP_IDS)}"
# own_place is for the older maps: a newer one's panel placer moves it already (placer)
assert not [k for k, m in MAPS.items() if m.own_place and m.place], "own_place: a map with a placer of its own"
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
    downwards (layout.toml [minimap.panel_nudge]). -> (pos, offset) of MINIMAP."""
    right = m.minimap[1]
    if side in ("Left", "Right"):
        return "Max", offset - right - {"Min": SCREEN_W, "Mid": SCREEN_W // 2, "Max": 0}[pos]
    return "Max", offset - m.minimap[0] + down - {"Min": SCREEN_H, "Mid": SCREEN_H // 2, "Max": 0}[pos]


def const(key):
    return f"#FCJH_MINIMAP_BOTTOM_{key.upper()}"


def place_actions(key, indent):
    """The SetAnchors that put the minimap where this map wants it - at load, for a map that
    opens on part of its map (launch_cut)."""
    t = T * indent
    bottom = f"#FCJH_MINIMAP_LAUNCH_{key.upper()}" if MAPS[key].launch_cut is not None else const(key)
    out = (f'{t}<Action type="SetAnchor" frame="{MINIMAP}" side="Left"   relative="$GameUI" pos="Mid" offset="#FCJH_MINIMAP_PANEL_L"/>\n'
           f'{t}<Action type="SetAnchor" frame="{MINIMAP}" side="Right"  relative="$GameUI" pos="Mid" offset="#FCJH_MINIMAP_PANEL_R"/>\n'
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
# Banners whose sides a state moves - the curse, between red's layout and blue's (cursed_side):
# the fade only. A relative Anchor controller counts from the LAYOUT anchor, not a state's
# SetAnchor, and end="Pause" holds it (Haunted Mines' glide, 2026-10-09): the slide would
# have pinned the curse to red's spot and Blizzard's bar layout after its first intro. The
# tribute too: cursed_side moves it with the curse, whose hexagon on blue hangs off the tribute's.
FADE_ONLY = ("CurseFrame", "TributeSpawnFrame")


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


def map_file(key, at, down):
    """Everything this map's own layout file gets: its panels on our minimap, the minimap's
    place (placer, in its first panel), its team alerts."""
    m = MAPS[key]
    root = Node(None)
    for path, sides in m.panels.items():
        root.at(path).body += anchor_lines(sides, m, len(path.split("/")) + 1, down.get(key, 0))
    for path, xml in PARTS.get(key, {}).items():
        root.at(path).body += T * (len(path.split("/")) + 1) + xml + "\n"
    if m.place:
        root.at(m.place[0]).body += placer(key, len(m.place[0].split("/")) + 1)
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


def placer(key, indent):
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
            f'{t}</Frame>\n')


MAP_ID = "libCore_gv_mAPMapStringID"   # Blizzard's script variable naming the map (MAP_IDS)
MAP_ID_READER = "$GameUI/FCJH_MapId"   # ours, reading it (id_placers)


def on_map(key, reader=MAP_ID_READER):
    """A state's condition: we're on this map. Holds from the match's start and never changes -
    a group in a state on it never leaves it (leaving undoes its actions). Put such a group in
    a frame that's always shown: in a hidden one (Haunted Mines' core panel) it never ran."""
    return f'<When type="Property" frame="{reader}" StringValue="{MAP_IDS[key]}"/>'


GLIDE_S = 1.0         # seconds the minimap takes to glide to its place (opens)
GLIDE_STEPS = 10      # keys along it, eased in and out


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
    ease = lambda f: f * f * (3 - 2 * f)
    keys = "".join(f'{t}\t\t<Key type="Curve" time="{round(GLIDE_S * n / GLIDE_STEPS, 2)}" '
                   f'value="{round(ends[0] + (ends[1] - ends[0]) * ease(n / GLIDE_STEPS))}"/>\n'
                   for n in range(GLIDE_STEPS + 1))
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
    same reader never placed the minimap, while the diagnostic's here read the id (user,
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


# DIAGNOSTIC (2026-10-09): the map's id, read on screen, for each map until its id is confirmed
# in game (MAP_IDS' sources); remove once every map's is. The rest of it - each older panel's
# shown/hidden and Haunted Mines' labels - went once the map id solved the jitter (user,
# 2026-10-09).
def diag():
    t = T * 2
    cell = lambda name, left, width, text: (
        f'{t}<Frame type="Label" name="{name}">\n'
        f'{t}\t<Anchor side="Top"  relative="$GameUI" pos="Min" offset="300"/>\n'
        f'{t}\t<Anchor side="Left" relative="$GameUI" pos="Min" offset="{left}"/>\n'
        f'{t}\t<Width val="{width}"/>\n{t}\t<Height val="26"/>\n'
        f'{t}\t<Style val="WaitingForPlayersDialogChat"/>\n{t}\t<Options val="NoWrapping"/>\n'
        f'{t}\t<Unclipped val="true"/>\n{t}\t<AcceptsMouse val="false"/>\n'
        f'{t}\t<Text val="{text}"/>\n{t}</Frame>\n')
    # Blizzard's script variable, read the way Spazzo does (CustomPanelSpazzo: DataRefFrame
    # GalaxyVar libCore_gv_mAPMapStringID)
    return (f'{t}<!-- DIAGNOSTIC (maps.diag): the map id -->\n'
            f'{t}<Frame type="DataRefFrame" name="FCJH_DiagMapId">\n'
            f'{t}\t<Argument name="GalaxyVar" val="libCore_gv_mAPMapStringID"/>\n{t}</Frame>\n'
            + cell("FCJH_Diag0", 25, 300, "map id:")
            + cell("FCJH_DiagValue0", 325, 400, "{$parent/FCJH_DiagMapId/@StringValue}"))


def layout(header, at, down, bottoms, glides):
    """FCJH_Maps.StormLayout. at: (frame, across pos, down pos), where the plates are anchored -
    the stacks' constants run from there, as the plates' do (gen.py PLATES_AT). down: {map key:
    units}, how much lower each map's panel goes (layout.toml [minimap.panel_nudge]). bottoms:
    the minimap's bottom, units from the screen's: {None: the shared place, map key: its own}
    (gen.py minimap_bottoms). glides: {map key: (from, to)}, the minimap's bottom at load and in
    full, units from the shared place, for a map that opens on part of its map (launch_cut; glide)."""
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
{id_placers(glides)}{diag()}	</Frame>
''' + "".join(f"\t<!-- ===== {MAPS[k].title}{(': ' + MAPS[k].notes) if MAPS[k].notes else ''} ===== -->\n"
              + map_file(k, at, down) for k in MAPS if MAPS[k].file) + "</Desc>\n"
