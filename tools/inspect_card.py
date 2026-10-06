"""The inspect card (layout.toml element.inspect): the tall card for the SELECTED unit -
portrait, name, player and level, fountain, health and resource, buffs and debuffs, the ability
card (1-5 talent actives, D Q W E R Z), the talent strip and stats. Written by tools/gen.py
into FCJH_Inspect.StormLayout (inspect_card.layout); ported from the dev probe's scratch script
(nine rounds, 2026-09-26..30) with its output unchanged.

What the rounds established (the file's comments carry the detail):
  - it shows exactly when Blizzard's own small inspector would (FCJH_InspectGate): Blizzard's
    box is parked, not forced hidden (FCJH_Hidden), so its visibility is still the game's.
    On its own our TargetInfoFrame came up on a game's first plate click; the default UI's doesn't
  - Blizzard's TargetInfoFrame follows its own TARGET, not the selection: it's only the on/off
    switch; everything drawn follows the selection (a SelectionUnitStatusPanel inside the card)
  - talents are keyed to a PLAYER, a selection only gives a unit: the card carries the ten
    talent-pane rows and shows the one whose plate holds the selected hero (FCJH_IsPlayerN, a
    unit check per hero from the game data)
  - abilities are Blizzard's own command card laid over the card (command_panel, 2026-10-02):
    native tooltips, talent actives and the right R for every hero - Ahli's method
  - X closes it; its back takes the mouse so a click inside doesn't deselect (round 9)
"""
from functools import lru_cache
from pathlib import Path

T = "\t"

# Pane-local layout, in layout units. One padding, PAD, between every section and the next and
# between the card's edge and everything on it, measured from inside the edge (user,
# 2026-10-05: the same whitespace in every direction). The card is cut to fit what it holds
# (H, at the bottom: one row of buffs, two of abilities, the talents, three rows of stats).
W = 333                            # 300 px
BORDER = 2                         # the team-coloured edge
EDGE = 5                           # the edge: our team line, then Blizzard's border art (inset 3)
PAD = 10
M = EDGE + PAD                     # side margin
INNER = W - 2 * M                  # the width everything is laid across
TITLE = 30                         # the title band: the hero's name
NAME_BAND, NAME_H = 155, 30        # the player's name and the level, under the portrait
NAME_DROP = 2                      # their text set this much low: centred, it read high (2026-10-05)
PORTRAIT = (TITLE, NAME_BAND)      # top, bottom: stops at the band (round 3 ran it under the
                                   # band and the art hid the level)
HP = (NAME_BAND + NAME_H + PAD, NAME_BAND + NAME_H + PAD + 24)
MANA = (HP[1] + 2, HP[1] + 18)
# Buffs then debuffs on one row, the fountain first (as a buff of its own, in Blizzard's buff
# art). Blizzard's buff slot is 58 x 34, each overlapping the last by 19
# (BehaviorIconTemplate, #BuffOffset).
BUFF_W, BUFF_H, BUFF_OVERLAP = 58, 34, 19
BUFFS = MANA[1] + PAD
# Abilities are Blizzard's command buttons (command_panel), at Ahli's sizes: a 52-unit button
# with its icon 5 in from each side, its frame art drawn at 68 and its glows at 60.
CMD_SIZE, CMD_INSET, CMD_BORDER, CMD_GLOW = 52, 5, 68, 60
CMD_CHARGE, CMD_CHARGE_RING = 20, 30   # the charge badge and its ring (Ahli's 26 / 38 read too big, 2026-10-05)
# The mount (Z) is Blizzard's bookend button, one wide piece (83 x 54) whose art is anchored to
# its edges; squeezed to 52 x 52 with our 68-unit frame art it read far too big (2026-10-05).
# It keeps its own proportions, centred in its slot, and Blizzard's inner layout.
MOUNT_W, MOUNT_H = 56, 36
# the buttons' frame art reaches (CMD_BORDER - CMD_SIZE) / 2 past them, but the hexagon you
# see is about the button: spacing is to the button (user, 2026-10-05: with the art on the
# margins the row read narrower than the card, and the gap over it too big)
ART = (CMD_BORDER - CMD_SIZE) // 2
# The bottom row's six slots spread evenly so the outer buttons meet the margins; the talent
# actives sit on the row above, each over the gap between two bottom buttons, starting
# between Q and W (cmd_centre), nested into the row below as a honeycomb - every neighbour,
# along the row or across, the same distance apart (user: the gap under the top row as
# even as the bottom row's)
CMD_STEP = (INNER - CMD_SIZE) / 5
CMD_PITCH = round(CMD_STEP * 3 ** 0.5 / 2)
ABIL_TOP = BUFFS + BUFF_H + PAD
ABIL_ROWS = (ABIL_TOP, ABIL_TOP + CMD_PITCH)
TAL_LABEL = ABIL_ROWS[1] + CMD_SIZE + ART + PAD
TAL = TAL_LABEL + 16
TAL_SIZE = 36                      # the talent strip's icons, spread across the card
TAL_STEP = (INNER - TAL_SIZE) / 6
# Stats: three columns, related values sharing a row (user, 2026-10-05) - (frame, column, row)
STATS_GRID = (("AttackDamageFrame", 0, 0), ("AttackSpeedFrame", 1, 0), ("AttackRangeFrame", 2, 0),
              ("AbilityPowerFrame", 0, 1), ("MoveSpeedFrame", 1, 1),
              ("PhysicalArmorFrame", 0, 2), ("AbilityArmorFrame", 1, 2))
STATS_LABEL = TAL + TAL_SIZE + 16 + PAD    # under the tier numbers (16 tall)
STATS, STAT_ROW, STAT_COL, STAT_H = STATS_LABEL + 18, 24, INNER // 3, 20   # STAT_H: Blizzard's stat row
STAT_END = STATS + 2 * STAT_ROW + STAT_H
H = STAT_END + PAD + EDGE          # the card's height (layout.toml element.inspect: 525 px)
TEAM = {}                          # the border's colours, "a,r,g,b" by team: set by layout()


ORIGIN = (0, 0)   # the card's top-left on screen, in layout units: set by layout()
PX = 0.9          # screen pixels per layout unit: set by layout()


def line(at, axis, way, want=2):
    """How many units in from the card-relative edge `at` (axis 0: across, 1: down; way 1: the
    box runs on past it, -1: it ends there) a line `want` screen pixels thick ends. Units
    aren't whole pixels, so a fixed thickness rounds to different widths along the card."""
    px = lambda u: int(u * PX + 0.5)
    e = ORIGIN[axis] + at
    for w in (2, 1, 3, 4):
        if abs(px(e + way * w) - px(e)) == want:
            return w
    return 2


def tal_left(k):
    """Talent k's (1-7) left edge on the card."""
    return M + round((k - 1) * TAL_STEP)


def cmd_centre(row, c):
    """The middle of command slot c on ability row 0 (talent actives) or 1 (Z Q W E R D)."""
    first = M + CMD_SIZE / 2
    if row == 1:
        return first + c * CMD_STEP
    # over the gaps: Q/W, W/E, E/R, R/D, then Z/Q; a sixth (never seen) over Z
    return first + ((1.5, 2.5, 3.5, 4.5, 0.5, 0)[c]) * CMD_STEP

def rect(top, left, bottom, right, rel="$parent", i=4, right_pos="Min"):
    t = T * i
    return (f'{t}<Anchor side="Top"    relative="{rel}" pos="Min" offset="{top}"/>\n'
            f'{t}<Anchor side="Left"   relative="{rel}" pos="Min" offset="{left}"/>\n'
            f'{t}<Anchor side="Bottom" relative="{rel}" pos="Min" offset="{bottom}"/>\n'
            f'{t}<Anchor side="Right"  relative="{rel}" pos="{right_pos}" offset="{right}"/>\n')


def label(name, top, left, bottom, right, style, text, i=4, right_pos="Min", extra=""):
    t = T * i
    return (f'{t}<Frame type="Label" name="{name}">\n' + rect(top, left, bottom, right, i=i + 1, right_pos=right_pos) +
            f'{t}\t<Style val="{style}"/>\n{t}\t<Text val="{text}"/>\n'
            f'{t}\t<Options val="NoWrapping | ScaleToPreventTruncation"/>\n{t}\t<AcceptsMouse val="false"/>\n{extra}{t}</Frame>\n')


def fill(name, top, left, bottom, right, colour, prio, i=4, right_pos="Min"):
    t = T * i
    return (f'{t}<Frame type="Image" name="{name}">\n' + rect(top, left, bottom, right, i=i + 1, right_pos=right_pos) +
            f'{t}\t<Texture val="@UI/PauseScreenDimImage"/>\n{t}\t<ColorAdjustMode val="Fill"/>\n'
            f'{t}\t<AdjustmentColor val="{colour}"/>\n{t}\t<RenderPriority val="{prio}"/>\n{t}\t<AcceptsMouse val="false"/>\n{t}</Frame>\n')


def parked(name, ftype):
    """One of Blizzard's inspect-box pieces moved far off screen, mouse off."""
    return (f'{T*4}<Frame type="{ftype}" name="{name}">\n'
            f'{T*5}<Anchor side="Top"    relative="$parent" pos="Min" offset="9999"/>\n'
            f'{T*5}<Anchor side="Left"   relative="$parent" pos="Min" offset="9999"/>\n'
            f'{T*5}<Anchor side="Bottom" relative="$parent" pos="Min" offset="10099"/>\n'
            f'{T*5}<Anchor side="Right"  relative="$parent" pos="Min" offset="10099"/>\n'
            f'{T*5}<Alpha val="0"/>\n{T*5}<AcceptsMouse val="false"/>\n{T*5}<AcceptsMouseTooltip val="false"/>\n'
            f'{T*4}</Frame>\n')


COMMAND_PANEL = "$GameUI/UIContainer/ConsoleUIContainer/CommandPanel"


CARD = "$GameUI/UIContainer/ConsoleUIContainer/FCJH_Inspect"


def command_switch():
    """Blizzard's command card (the selected hero's ability buttons, with their own tooltips,
    talent actives and the right R for every hero - how Ahli's hero card does abilities),
    held shown by a looping animation (the game brings the player HUD back, or takes it away,
    whenever it likes). It's never hidden: while the card is closed it's parked off screen
    (command_anchors, from the card's gate). The first try showed and hid it with two looping
    animations, one per side, and it never showed (2026-10-03): a stopped loop seems to keep
    its last value. Was always hidden with the rest of the HUD (FCJH_Hidden) until 2026-10-02."""
    return (f'{T*2}<Frame type="Frame" name="FCJH_CommandShown">\n'
            f'{T*3}<Anchor relative="$parent"/>\n{T*3}<AcceptsMouse val="false"/>\n'
            f'{T*3}<Animation name="FCJH_Assert">\n{T*4}<Event event="OnShown" action="Play"/>\n'
            f'{T*4}<Controller type="Visibility" end="Loop" frame="{COMMAND_PANEL}">\n'
            f'{T*5}<Key type="Bool" time="0" value="true"/>\n'
            f'{T*4}</Controller>\n{T*3}</Animation>\n{T*2}</Frame>\n')


def placed(top, left, w, h, indent, rel="$parent"):
    """A frame's place by its top-left corner and an explicit size. Blizzard's command card
    and its buttons carry Width/Height in their templates (1060 x 190; 120 x 120), and those
    beat opposite-side anchors: anchored on all four sides, the buttons stayed 120 units
    (2026-10-03). Bottom and Right are tied to the frame itself, undoing the template's."""
    t = T * indent
    return (f'{t}<Anchor side="Top"    relative="{rel}" pos="Min" offset="{top}"/>\n'
            f'{t}<Anchor side="Left"   relative="{rel}" pos="Min" offset="{left}"/>\n'
            f'{t}<Anchor side="Bottom" relative="$this" pos="Min" offset="0"/>\n'
            f'{t}<Anchor side="Right"  relative="$this" pos="Min" offset="0"/>\n'
            f'{t}<Width val="{w}"/>\n{t}<Height val="{h}"/>\n')


def command_anchors(on_card, indent, tag="Action"):
    """The command card's top-left corner: on the card's ability rows, or parked off screen
    (its size is set on the frame - see placed). tag "Action": as StateGroup actions (the
    gate); "Anchor": as the frame's own anchors."""
    if on_card:
        sides = (("Top", CARD, "Min", ABIL_ROWS[0]), ("Left", CARD, "Min", M))
    else:
        sides = (("Top", "$GameUI", "Min", 9999), ("Left", "$GameUI", "Min", 9999))
    target = f' type="SetAnchor" frame="{COMMAND_PANEL}"' if tag == "Action" else ""
    return "".join(f'{T*indent}<{tag}{target} side="{s}" relative="{rel}" pos="{pos}" offset="{v}"/>\n'
                   for s, rel, pos, v in sides)


# The command card's buttons on the card's two ability rows, in Blizzard's own order (players
# know it): talent actives and other dynamic buttons on top (CommandButton30-35), then the
# mount, the four abilities and the trait (CommandButton04, 00, 01, 02, 03, 05 - left to
# right as in the default UI). Each button shows its own hotkey. The hearth (13), Blizzard's
# hidden spare (15), the empty-slot art, targeting prompts and tutorial arrows are put away.
COMMAND_ROWS = (("30", "31", "32", "33", "34", "35"), ("04", "00", "01", "02", "03", "05"))
# The keys those buttons hold (for the design canvas only - in game each button labels
# itself): seen in game 2026-10-03, Z Q W E R D left to right.
COMMAND_KEYS = {"04": "Z", "00": "Q", "01": "W", "02": "E", "03": "R", "05": "D",
                **{str(30 + i): str(1 + i) for i in range(6)}}
COMMAND_PUT_AWAY = ([("CommandButton", "CommandButton13"), ("CommandButton", "CommandButton15"),
                     ("Image", "MiddleFill"), ("Image", "CommandTargetImage"), ("Label", "CommandTargetName"),
                     ("Label", "CommandTargetPrompt"), ("Frame", "ButtonEffectAttention"), ("Frame", "HudEffectPhased")]
                    + [("Image", f"EmptyDynamicButton{k}") for k in range(30, 36)]
                    + [("Frame", f"TutorialArrow0{k}") for k in range(6)])


def command_panel():
    """Blizzard's command card laid over the card's ability rows. It lives in the console
    container, as the card now does (one step under it in RenderPriority), so its buttons draw
    over the card's back and take the mouse first. The panel covers only the ability band, so
    it can't cover the card's other tooltips. Blizzard's hero-specific command-card panel and
    control-group panel hang off it, so they go where it goes (parked while the card's shut)."""
    top = ABIL_ROWS[0]
    sized = lambda name_, ftype, size, i: (f'{T*i}<Frame type="{ftype}" name="{name_}">'
                                           f'<Width val="{size}"/><Height val="{size}"/><Unclipped val="true"/></Frame>\n')
    # the button's pieces at its size (Blizzard's are drawn for a 120-unit button): the icon
    # inset, the frame art and glows sized - Ahli's recipe
    inset = "".join(f'{T*6}<Anchor side="{s}" relative="$parent" pos="{p}" offset="{v}"/>\n'
                    for s, p, v in (("Top", "Min", CMD_INSET), ("Left", "Min", CMD_INSET),
                                    ("Bottom", "Max", -CMD_INSET), ("Right", "Max", -CMD_INSET)))
    # The talent actives (dynamic buttons, 30-35) are Blizzard's DynamicButtonTemplate, whose
    # icon is 67 x 67 by its own Width/Height - that beat our inset (rule: a template's size
    # beats opposite-side anchors) and the icon, and the cooldown sweep hung on it, drew far
    # past the button (Sonya, 2026-10-05). So they get the size outright, the ability mask
    # rather than the inventory one (as Ahli's do), and the sweep laid over the icon as on the
    # other buttons.
    icon = CMD_SIZE - 2 * CMD_INSET
    dynamic = (f'{T*6}<Width val="{icon}"/>\n{T*6}<Height val="{icon}"/>\n'
               f'{T*6}<ImageMaskTexture val="@UI/HUD_BTN_BG_Ability_AlphaMask"/>\n')
    sweep = (f'{T*5}<Frame type="ProgressBar" name="CooldownProgress">\n'
             + "".join(f'{T*6}<Anchor side="{s}" relative="$parent/NormalImage" pos="{p}" offset="0"/>\n'
                       for s, p in (("Top", "Min"), ("Left", "Min"), ("Bottom", "Max"), ("Right", "Max")))
             + f'{T*5}</Frame>\n')
    parts = lambda dyn: (
        f'{T*5}<Frame type="Image" name="NormalImage">\n' + inset + (dynamic if dyn else "")
             + f'{T*6}<Unclipped val="true"/>\n{T*5}</Frame>\n' + (sweep if dyn else "")
             + sized("GameButtonDefaultBorder", "Image", CMD_BORDER, 5)
             + f'{T*5}<Frame type="Frame" name="ActiveEffect">\n'
             + sized("ActiveEffectImage", "Image", CMD_GLOW, 6) + sized("ActiveEffect2Image", "Image", CMD_GLOW, 6)
             + f'{T*5}</Frame>\n{T*5}<Frame type="Frame" name="AttentionEffect">\n'
             + sized("AttentionEffectImage", "Image", CMD_GLOW, 6) + sized("AttentionEffect2Image", "Image", CMD_GLOW, 6)
             + sized("InnerGlowImage", "Image", CMD_GLOW, 6)
             + f'{T*5}</Frame>\n{T*5}<Frame type="Frame" name="HitTestFrame"><Anchor relative="$parent"/></Frame>\n'
             # the text on the button, sized for 120 units: hotkey letters off (Ahli's choice;
             # they piled onto the icons, 2026-10-03), cooldown count in our heroic-cooldown
             # style, the charge badge, ring and count at Ahli's sizes
             + f'{T*5}<Frame type="CommandHotkeyFrame" name="HotkeyFrame"><Frame type="Label" name="HotkeyLabel"><Alpha val="0"/></Frame></Frame>\n'
             f'{T*5}<Frame type="Label" name="CooldownLabel">'
             f'<Anchor side="Left" relative="$parent" pos="Min" offset="0"/><Anchor side="Right" relative="$parent" pos="Max" offset="0"/>'
             f'<Style val="FCJH_HeroicCooldown"/></Frame>\n'
             f'{T*5}<Frame type="Image" name="ChargeBackground">'
             f'<Anchor side="Bottom" relative="$parent" pos="Max" offset="3"/><Anchor side="Right" relative="$parent" pos="Max" offset="-2"/>'
             f'<Width val="{CMD_CHARGE}"/><Height val="{CMD_CHARGE}"/><Unclipped val="true"/></Frame>\n'
             + sized("ChargeCompleteImage", "Image", CMD_CHARGE, 5) + sized("ChargeCooldown", "ProgressBar", CMD_CHARGE_RING, 5)
             + f'{T*5}<Frame type="Label" name="ChargeLabel"><Style val="FCJH_InspectCharge"/><Unclipped val="true"/>'
             f'<RenderPriority val="600"/></Frame>\n')
    buttons = []
    for r, row in enumerate(COMMAND_ROWS):
        for c, k in enumerate(row):
            # placed by its middle, against the panel (whose left edge is the card's margin)
            left = lambda w: round(cmd_centre(r, c) - w / 2) - M
            y = ABIL_ROWS[r] - top
            if k == "04":   # the mount: its own shape, only its hotkey letter put away
                buttons.append(f'{T*4}<Frame type="CommandButton" name="CommandButton{k}">\n'
                               + placed(y + (CMD_SIZE - MOUNT_H) // 2, left(MOUNT_W), MOUNT_W, MOUNT_H, 5)
                               + f'{T*5}<Frame type="CommandHotkeyFrame" name="HotkeyFrame"><Frame type="Label" name="HotkeyLabel"><Alpha val="0"/></Frame></Frame>\n'
                               + f'{T*4}</Frame>\n')
                continue
            buttons.append(f'{T*4}<Frame type="CommandButton" name="CommandButton{k}">\n'
                           + placed(y, left(CMD_SIZE), CMD_SIZE, CMD_SIZE, 5) + parts(k.startswith("3"))
                           # the ability buttons' dark hexagon behind the icon (only their
                           # template has one: not the mount's bookend nor the dynamic buttons)
                           + (f'{T*5}<Frame type="Image" name="IconBackground">\n' + inset + f'{T*5}</Frame>\n'
                              if k in ("00", "01", "02", "03", "05") else "")
                           # each button's hero-specific panel (Tracer's Pulse Bomb dial lives in
                           # R's) is Blizzard's 120 x 120 - it read oversized (2026-10-05)
                           + sized("ButtonSpecificOverlayPanel" if k.startswith("3") else "HeroSpecificCommandCardPanel",
                                   "HeroSpecificContainerPanel", CMD_SIZE, 5)
                           + f'{T*4}</Frame>\n')
    away = "".join(
        f'{T*4}<Frame type="{ftype}" name="{n}">\n'
        f'{T*5}<Anchor side="Top"    relative="$parent" pos="Min" offset="9999"/>\n'
        f'{T*5}<Anchor side="Left"   relative="$parent" pos="Min" offset="9999"/>\n'
        f'{T*5}<Anchor side="Bottom" relative="$parent" pos="Min" offset="10036"/>\n'
        f'{T*5}<Anchor side="Right"  relative="$parent" pos="Min" offset="10036"/>\n'
        f'{T*5}<Alpha val="0"/>\n{T*5}<AcceptsMouse val="false"/>\n{T*5}<AcceptsMouseTooltip val="false"/>\n{T*4}</Frame>\n'
        for ftype, n in COMMAND_PUT_AWAY)
    return (f'{T*2}<!-- Blizzard\'s command card on the card\'s ability rows (inspect_card.command_panel) -->\n'
            f'{T*2}<Frame type="CommandPanel" name="CommandPanel">\n'
            f'{T*3}<!-- parked; the card\'s gate moves it onto the card while the card shows -->\n'
            + command_anchors(False, 3, "Anchor")
            + f'{T*3}<Anchor side="Bottom" relative="$this" pos="Min" offset="0"/>\n'
            f'{T*3}<Anchor side="Right"  relative="$this" pos="Min" offset="0"/>\n'
            f'{T*3}<Width val="{INNER}"/>\n{T*3}<Height val="{ABIL_ROWS[1] + CMD_SIZE - ABIL_ROWS[0]}"/>\n'
            + "".join(buttons) + away + f'{T*2}</Frame>\n'
            # Blizzard's control-group panel (the selection's unit icons, with health bars and
            # tooltips) hangs off the command card, so it came onto the card with it and stuck
            # out past its right edge, mostly invisible but answering the mouse (user,
            # 2026-10-05): parked for good
            f'{T*2}<Frame type="ControlGroupPanel" name="ControlGroupPanel">\n'
            + placed(9999, 9999, 500, 120, 3, "$GameUI")
            + f'{T*3}<Alpha val="0"/>\n{T*3}<AcceptsMouse val="false"/>\n{T*3}<AcceptsMouseTooltip val="false"/>\n'
            f'{T*2}</Frame>\n')


def blizzard_skin():
    """The default inspector's own art on the card (the user's background pass, 2026-10-05:
    "the pure black needs something to punch it up"; chosen over the flat look in game) -
    TargetInfoPanelTemplate's layers: a nine-slice background, its top band tinted 564c6d at
    76 alpha with a 73668d line under it (here on both our bands), and a nine-slice border
    inset 3. All of it just over our back (which stays: it takes the mouse) and under
    everything drawn on the card, as in Blizzard's panel (border 270, contents 280): the
    border's middle isn't clear, and drawn over the card (689, the first try) it muted the
    health bars and the fountain (user, 2026-10-05)."""
    u = T * 5
    def img(name_, top, bottom, extra, prio, inset=0, to_end=False):
        """An image across the card from `top` to `bottom` (or the card's end), `inset` in from
        the card's sides (and its top or bottom when it reaches them)."""
        return (f'{T*4}<Frame type="Image" name="{name_}">\n'
                f'{u}<Anchor side="Top"    relative="$parent" pos="Min" offset="{top + (inset if top == 0 else 0)}"/>\n'
                f'{u}<Anchor side="Left"   relative="$parent" pos="Min" offset="{inset}"/>\n'
                f'{u}<Anchor side="Bottom" relative="$parent" pos="{"Max" if to_end else "Min"}" offset="{-inset if to_end else bottom}"/>\n'
                f'{u}<Anchor side="Right"  relative="$parent" pos="Max" offset="{-inset}"/>\n'
                f'{extra}{u}<RenderPriority val="{prio}"/>\n{u}<AcceptsMouse val="false"/>\n{T*4}</Frame>\n')
    nine = lambda tex: f'{u}<Texture val="@UI/{tex}"/>\n{u}<TextureType val="Nineslice"/>\n'
    tint = lambda colour: f'{u}<Color val="{colour}"/>\n{u}<Alpha val="76"/>\n'
    # the background at 90%, the game showing through a little as through the replay panel
    # (user, 2026-10-05: 80% was a touch much); nothing under it (our back is faded, mouse only)
    return (img("FCJH_SkinBack", 0, 0, nine("Storm_UI_TargetInfoPanel_Background") + f'{u}<Alpha val="230"/>\n',
                205, to_end=True)
            + img("FCJH_SkinBorder", 0, 0, nine("Storm_UI_TargetInfoPanel_BackgroundBorder"), 207, 3, to_end=True)
            + img("FCJH_SkinTitle", 0, TITLE, tint("564c6d"), 211, 3)
            + img("FCJH_SkinTitleLine", TITLE - 1, TITLE, tint("73668d"), 212)
            + img("FCJH_SkinName", NAME_BAND, NAME_BAND + NAME_H, tint("564c6d"), 241, 3))


def card():
    """Our copy of Blizzard's inspect box, re-laid out tall (portrait, bars, stats)."""
    out = [f'{T*2}<!-- Round 9 (2026-09-30): the card shows exactly when Blizzard\'s own small inspector\n'
           f'{T*2}     would. Ours alone (a TargetInfoFrame the game doesn\'t manage) came up on the first\n'
           f'{T*2}     plate click of a game; the default UI\'s doesn\'t (user). Blizzard\'s is now parked\n'
           f'{T*2}     off screen rather than forced hidden (FCJH_Hidden), so its visibility is still the\n'
           f'{T*2}     game\'s, and this watcher copies it onto the card. -->\n'
           f'{T*2}<Frame type="Frame" name="FCJH_InspectGate">\n'
           f'{T*3}<Anchor relative="$parent"/>\n{T*3}<AcceptsMouse val="false"/>\n'
           f'{T*3}<StateGroup name="FCJH_Gate">\n{T*4}<DefaultState val="Hide"/>\n'
           f'{T*4}<State name="Show">\n'
           f'{T*5}<When type="Property" frame="$GameUI/UIContainer/FullscreenUpperContainer/TargetInfoFrame" Visible="true"/>\n'
           f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_Inspect" Visible="true"/>\n'
           + (f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_TalentTips" Visible="true"/>\n' if TALENT_TIPS else "")
           + command_anchors(True, 5) + f'{T*4}</State>\n'
           f'{T*4}<State name="Hide">\n'
           f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_Inspect" Visible="false"/>\n'
           + (f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_TalentTips" Visible="false"/>\n' if TALENT_TIPS else "")
           + command_anchors(False, 5) + f'{T*4}</State>\n'
           f'{T*3}</StateGroup>\n{T*2}</Frame>\n' + command_switch() +
           f'{T*2}<!-- The card: our copy of Blizzard\'s inspect box -->\n'
           f'{T*2}<Frame type="TargetInfoFrame" name="FCJH_Inspect">\n'
           f'{T*3}<Visible val="false"/>\n'
           # no X (round 9 had one; dropped 2026-10-05): clicking off the unit closes the card, as
           # it does Blizzard's - the X is for the panes you summon (tools/gen.py close_button)
           f'{T*3}<Anchor side="Top"    relative="$parent" pos="Min" offset="#FCJH_INSPECT_T"/>\n'
           f'{T*3}<Anchor side="Left"   relative="$parent" pos="Min" offset="#FCJH_INSPECT_L"/>\n'
           f'{T*3}<Anchor side="Bottom" relative="$parent" pos="Min" offset="#FCJH_INSPECT_B"/>\n'
           f'{T*3}<Anchor side="Right"  relative="$parent" pos="Min" offset="#FCJH_INSPECT_R"/>\n'
           # in the console container, just under its command card (610), whose buttons draw
           # on the card's ability rows (command_panel)
           f'{T*3}<AcceptsMouse val="false"/>\n{T*3}<RenderPriority val="600"/>\n']
    chrome = []
    # Round 9: the back takes the mouse, so a click inside the card no longer falls through to
    # the map (which deselects the unit and closes the card, 2026-09-30)
    # (faded since Blizzard's background went on: it's only here for the mouse - a faded frame
    # still takes it. A clear fill colour didn't do: the card stayed opaque, 2026-10-05)
    chrome.append(fill("FCJH_Back", 0, 0, H, 0, "255,11,12,20", 200, 3, "Max")
                  .replace('<AcceptsMouse val="false"/>', '<AcceptsMouse val="true"/>\n\t\t\t\t<Alpha val="0"/>'))
    # the title band carries the hero's name (unit(): FCJH_HeroName), not a title (user, 2026-10-05)
    chrome.append(blizzard_skin())
    # no buffs or abilities heading (user, 2026-10-05): their pictures say what they are
    for text, top in (("TALENTS", TAL_LABEL), ("STATS", STATS_LABEL)):
        chrome.append(label(f"FCJH_Section{text.capitalize()}", top, M, top + 15, -M, "FCJH_InspectSection", text, 3, "Max"))
    stat_frames = "".join(
        f'{T*6}<Frame type="TargetInfoStatFrame" name="{n}">\n'
        f'{T*7}<Anchor side="Top" relative="$parent" pos="Min" offset="{r * STAT_ROW}"/>\n'
        f'{T*7}<Anchor side="Left" relative="$parent" pos="Min" offset="{c * STAT_COL}"/>\n'
        f'{T*7}<Anchor side="Right" relative="$this" pos="Min" offset="0"/>\n{T*7}<Width val="{STAT_COL - 4}"/>\n{T*6}</Frame>\n'
        for n, c, r in STATS_GRID)
    stat_rows = 1 + max(r for _, _, r in STATS_GRID)
    energy = "".join(f'{T*4}<Frame type="UnitStatusEnergyBar" name="{n}"><Anchor side="Right" relative="$parent/HealthBar" pos="Max" offset="0"/><Width val="0"/></Frame>\n'
                     for n in ("NormalEnergyBar", "OrangeEnergyBar", "PinkEnergyBar", "YellowEnergyBar", "DeathwingEnergyBar"))
    # Round 7: everything drawn follows the SELECTION. Blizzard's inspect box (TargetInfoFrame)
    # follows its own target - at game start it latched onto something and showed, and later it
    # showed Rexxar's portrait, health and stats under Chromie's name. It stays only as the
    # on/off switch (it closes on click-off); nothing of it is drawn.
    global CARD_CONTENT
    CARD_CONTENT = (
        f'{T*4}<!-- the card itself, inside the selection panel: shown only with a selection -->\n'
        + "".join(chrome) +
        f'''{T*4}<!-- health and resource: Blizzard's inspect-box bars (this frame's template), placed -->
{T*4}<Frame type="UnitStatusShieldedHealthBar" name="HealthBar">
{T*5}<Anchor side="Top"   relative="$parent" pos="Min" offset="{HP[0]}"/>
{T*5}<Anchor side="Left"  relative="$parent" pos="Min" offset="{M}"/>
{T*5}<Anchor side="Right" relative="$parent" pos="Max" offset="-{M}"/>
{T*5}<Height val="{HP[1] - HP[0]}"/>
{T*5}<Width val="0"/>
{T*4}</Frame>
{energy}{T*4}<!-- stats: Blizzard's stat rows, from the inspect box's template -->
{T*4}<Frame type="Frame" name="FCJH_Stats" template="TargetInfoPanel/TargetInfoPanelTemplate/HealthAndManaUnitStatusFrame/TargetStatsPanel">
{rect(STATS, M, STATS + stat_rows * STAT_ROW, -M, i=5, right_pos="Max")}{stat_frames}{T*5}<!-- the stat tooltips open off the card's right edge, level with the stats (Blizzard's
{T*5}     hung them under the box - the bottom of our tall card, round 7) -->
{T*5}<Frame type="Frame" name="TooltipAnchorFrame">
{T*6}<Anchor side="Top"    relative="$parent" pos="Min" offset="0"/>
{T*6}<Anchor side="Left"   relative="$parent/$parent" pos="Max" offset="{M}"/>
{T*6}<Anchor side="Bottom" relative="$parent" pos="Max" offset="0"/>
{T*6}<Width val="10"/>
{T*6}<TooltipAnchorPosition val="TopToTop | LeftToLeft"/>
{T*5}</Frame>
{T*4}</Frame>
''')
    out.append(f'''{T*3}<Frame type="Frame" name="TargetInfoPanel" template="TargetInfoPanel/TargetInfoPanelTemplate">
{T*4}<Anchor relative="$parent"/>
{T*4}<Visible val="{{$this/@Enabled}}"/>
{T*4}<!-- the on/off switch only: none of Blizzard's own pieces drawn -->
{T*4}<Frame type="Image" name="BackgroundFrame"><Alpha val="0"/></Frame>
{T*4}<Frame type="Image" name="TopBackground"><Alpha val="0"/></Frame>
{T*4}<Frame type="Image" name="BottomBorderImage"><Alpha val="0"/></Frame>
{T*4}<Frame type="Image" name="BorderFrame"><Alpha val="0"/></Frame>
{T*4}<!-- parked off screen, not just faded: faded, their stat rows still answered the mouse
{T*4}     under our portrait (duplicate tooltips, round 7) -->
{parked("TargetPortraitFrame", "Frame")}{parked("HealthAndManaUnitStatusFrame", "UnitStatusFrame")}{parked("AdditionalInfoIcon", "Image")}{parked("TargetHeroUnitFrame", "UnitTargetFrame")}
''')
    return "".join(out)   # left open: TargetInfoPanel and the card; the selection panel (unit()) goes inside


MODS = Path(__file__).resolve().parent.parent / "references" / "JamiePhan" / "mods"
ROW = ("$GameUI/UIContainer/FullscreenUpperContainer/ObserverHeroOverviewPanel/TalentsOverview/TalentOverview/"
       "HeroTalentsPanelContainer/PlayerFrame{n}")
PLATE = "$GameUI/UIContainer/FullscreenUpperContainer/ObserverHeroOverviewPanel/Team{t}HeroOverview/HeroOverview{m}"


def hero_units():
    """Every hero's unit id, from the game data: CHero entries, Unit defaulting to Hero<id>."""
    import xml.etree.ElementTree as ET
    units = set()
    for f in list((MODS / "heromods").rglob("*.xml")) + list((MODS / "heroesdata.stormmod").rglob("*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for h in root.iter("CHero"):
            hid = h.get("id")
            if not hid or h.get("default"):
                continue
            u = h.find("Unit")
            units.add(u.get("value") if u is not None and u.get("value") else f"Hero{hid}")
    return sorted(u for u in units if u.startswith("Hero") and "#" not in u)


HEROES = []   # every hero unit id (hero_units): set by layout()


CROP = None   # the plates' portrait crop (top, left, bottom, right): set by layout()


# heroes whose plate picture holds several (the Vikings): shown whole on the card; the units a
# Vikings plate can hold (ALSO's guesses)
WIDE_PORTRAITS = ("HeroLostVikingsController", "HeroOlaf", "HeroBaleog", "HeroErik")
PORTRAIT_ART = 2.75   # the heroes' portrait art, width over height (tools/gen.py HeroCell.ART_ASPECT)


def plate(n):
    return PLATE.format(t=1, m=n + 1) if n < 5 else PLATE.format(t=2, m=n - 4)


def player_pack(n):
    """Player n's talents (7 icons) and name, from the talent pane's row n.
    Hidden (Alpha 0) unless FCJH_IsPlayer{n} matches."""
    row = ROW.format(n=n)
    tree = f"{row}/TalentsContainerFrame/SelectionUnitStatusPanel/UnitStatusFrame0"
    colour = "blue" if n < 5 else "red"
    # round 7: an icon (and its team-coloured square, as in the talent pane) shows only once its
    # tier is picked - an unpicked tier's picture is a plain white square
    icons = "".join(
        f'{T*5}<Frame type="Image" name="FCJH_Talent{k}">\n'
        + rect(TAL, tal_left(k), TAL + TAL_SIZE, tal_left(k) + TAL_SIZE, i=6)
        + f'{T*6}<Texture val="{{{tree}/HeroSelectedTalentTreeFrame/TalentTreeIcon{k}/IconImage/@Texture}}"/>\n'
        f'{T*6}<RenderPriority val="668"/>  <!-- over the dark tier squares (665) -->\n'
        f'{T*6}<Alpha val="0"/>\n'
        f'{T*6}<AcceptsMouse val="false"/>  <!-- the tooltip comes from talent_tips over it -->\n'
        f'{T*6}<Frame type="Image" name="FCJH_Border">\n'
        f'{T*7}<Anchor side="Top"    relative="$parent" pos="Min" offset="-5"/>\n'
        f'{T*7}<Anchor side="Left"   relative="$parent" pos="Min" offset="-5"/>\n'
        f'{T*7}<Anchor side="Bottom" relative="$parent" pos="Max" offset="5"/>\n'
        f'{T*7}<Anchor side="Right"  relative="$parent" pos="Max" offset="5"/>\n'
        f'{T*7}<Texture val="@UI/obs_talents_highlight_{colour}"/>\n'
        f'{T*7}<Unclipped val="true"/>\n{T*7}<AcceptsMouse val="false"/>\n{T*6}</Frame>\n'
        f'{T*6}<StateGroup name="FCJH_Picked">\n{T*7}<DefaultState val="No"/>\n'
        f'{T*7}<State name="Yes"><When type="AnimationState" frame="{tree}/HeroSelectedTalentTreeFrame/TalentTreeIcon{k}" TalentTierState="TierSelected"/>'
        f'<Action type="SetProperty" frame="$this" Alpha="255"/></State>\n'
        f'{T*7}<State name="No"><Action type="SetProperty" frame="$this" Alpha="0"/></State>\n'
        f'{T*6}</StateGroup>\n{T*5}</Frame>\n'
        for k in range(1, 8))
    # the portrait: this player's plate picture, with the plate's crop (layout 2.6:1, near the card's)
    pic = lambda name_, coords, alpha, top=PORTRAIT[0], bottom=PORTRAIT[1]: (
        f'{T*5}<Frame type="Image" name="{name_}">\n'
        + rect(top, 2, bottom, -2, i=6, right_pos="Max")
        + f'{T*6}<Texture val="{{{plate(n)}/HeroPortraitImage/@Texture}}"/>\n'
        f'{T*6}<TextureCoords top="{coords[0]}" left="{coords[1]}" bottom="{coords[2]}" right="{coords[3]}"/>\n'
        f'{T*6}<RenderPriority val="668"/>\n{T*6}<Alpha val="{alpha}"/>\n{T*6}<AcceptsMouse val="false"/>\n{T*5}</Frame>\n')
    # the Vikings' three in one picture: the plates' crop (the art's right part) cut Baleog off,
    # and the whole art cut Olaf (user, 2026-10-05) - for them, the plates' crop with the
    # picture moved right a fifth of its width (the user's pick)
    shift = round(0.2 * (CROP[3] - CROP[1]), 3)
    swap = lambda wide: (f'<Action type="SetProperty" frame="$this/FCJH_PortraitWide" Alpha="{255 if wide else 0}"/>'
                         f'<Action type="SetProperty" frame="$this/FCJH_Portrait" Alpha="{0 if wide else 255}"/>')
    portrait = (pic("FCJH_Portrait", CROP, 255)
                + pic("FCJH_PortraitWide", (CROP[0], round(CROP[1] - shift, 3), CROP[2], round(CROP[3] - shift, 3)), 0)
                + f'{T*5}<StateGroup name="FCJH_PortraitCrop">\n{T*6}<DefaultState val="Hero"/>\n'
                + "".join(f'{T*6}<State name="{u}"><When type="Property" frame="{plate(n)}/HeroStatus" Unit="{u}"/>{swap(True)}</State>\n'
                          for u in WIDE_PORTRAITS)
                + f'{T*6}<State name="Hero">{swap(False)}</State>\n{T*5}</StateGroup>\n')
    name = label("FCJH_PlayerName", NAME_BAND + NAME_DROP, M, NAME_BAND + NAME_H + NAME_DROP, W - M - 70, "FCJH_InspectSub",
                 f"{{{row}/PlayerNameFrame/PlayerNameLabel/@Text}}", 5)
    # the card's edge in the player's team colour (user, 2026-10-05)
    edge = TEAM[colour]
    border = (fill("FCJH_EdgeTop", 0, 0, BORDER, W, edge, 690, 5)
              + fill("FCJH_EdgeBottom", H - BORDER, 0, H, W, edge, 690, 5)
              + fill("FCJH_EdgeLeft", 0, 0, H, BORDER, edge, 690, 5)
              + fill("FCJH_EdgeRight", 0, W - BORDER, H, W, edge, 690, 5))
    return (f'{T*4}<Frame type="Frame" name="FCJH_Player{n}">\n{T*5}<Anchor relative="$parent"/>\n'
            f'{T*5}<Alpha val="0"/>\n{T*5}<AcceptsMouse val="false"/>\n{T*5}<RenderPriority val="670"/>\n'
            f'{T*5}<!-- an empty tier\'s box under each icon: a line in the band art\'s 73668d round a dark\n'
            f'{T*5}     square (the old plain dark squares vanished on Blizzard\'s background, 2026-10-05) -->\n'
            # (2 units: 1 is 0.9 px, and the top line rounded away, 2026-10-05)
            + "".join(fill(f"FCJH_TierLine{k}", TAL, tal_left(k), TAL + TAL_SIZE, tal_left(k) + TAL_SIZE,
                           "200,115,102,141", 664, 5)
                      + fill(f"FCJH_TierBack{k}", TAL + line(TAL, 1, 1), tal_left(k) + line(tal_left(k), 0, 1),
                             TAL + TAL_SIZE - line(TAL + TAL_SIZE, 1, -1),
                             tal_left(k) + TAL_SIZE - line(tal_left(k) + TAL_SIZE, 0, -1), "230,8,8,16", 665, 5)
                      for k in range(1, 8))
            + portrait + icons + name + border + f'{T*4}</Frame>\n')


# Heroes whose selected unit can differ from the plate's: (selected, on the plate). Guesses
# until seen in game - D.Va's mech vs pilot, each Viking vs the Vikings' controller.
ALSO = [("HeroDVaMech", "HeroDVaPilot"), ("HeroDVaPilot", "HeroDVaMech"), ("HeroDVaMech", "HeroDVaMech")] + [
    (v, p) for v in ("HeroOlaf", "HeroBaleog", "HeroErik") for p in (v, "HeroLostVikingsController")]


def matcher(n):
    """FCJH_IsPlayer{n}: shows pack n while the selected unit is the hero on plate n, and
    raises flag FCJH_TipSel{n}, which brings player n's talent tooltips onto the card."""
    flag = lambda on: (f'<Action type="SetProperty" frame="$this/FCJH_TipSel{n}" Visible="{on}"/>'
                       if TALENT_TIPS else "")
    states = "".join(
        f'{T*5}<State name="{sel}{"" if sel == on else "_" + on}">'
        f'<When type="Property" Unit="{sel}"/>'
        f'<When type="Property" frame="{plate(n)}/HeroStatus" Unit="{on}"/>'
        f'<Action type="SetProperty" frame="$this/FCJH_Player{n}" Alpha="255"/>{flag("true")}</State>\n'
        for sel, on in [(u, u) for u in HEROES] + ALSO)
    return (f'{T*4}<StateGroup name="FCJH_IsPlayer{n}">\n{T*5}<DefaultState val="No"/>\n{states}'
            f'{T*5}<State name="No"><Action type="SetProperty" frame="$this/FCJH_Player{n}" Alpha="0"/>{flag("false")}</State>\n'
            f'{T*4}</StateGroup>\n')


# the card's talent tooltips; False builds the card without them (panel, row switches, gate
# actions)
TALENT_TIPS = True
TIPS = "$GameUI/UIContainer/ConsoleUIContainer/FCJH_TalentTips"
TIP_ROW = TIPS + "/FCJH_TalentTipPanel/TalentOverview/HeroTalentsPanelContainer/PlayerFrame{n}"
TIP_W = INNER                          # the talent strip's width: seven icons, across the card


def tip_switch(n):
    """Player n's tooltip row: on the card's talent strip while flag FCJH_TipSel{n} is up
    (matcher), parked off screen otherwise - so only the selected player's icons answer the
    mouse. The row is moved by its box, never its icons (an icon outside its box gives no
    tooltip, 2026-10-02)."""
    row = TIP_ROW.format(n=n)
    at = lambda rel, top, left: "".join(
        f'<Action type="SetAnchor" frame="{row}" side="{s}" relative="{rel}" pos="Min" offset="{v}"/>'
        for s, v in (("Top", top), ("Left", left)))
    return (f'{T*4}<Frame type="Frame" name="FCJH_TipSel{n}"><Anchor relative="$parent"/>'
            f'<Visible val="false"/><AcceptsMouse val="false"/></Frame>\n'
            f'{T*4}<StateGroup name="FCJH_TipRow{n}">\n{T*5}<DefaultState val="Away"/>\n'
            f'{T*5}<State name="On"><When type="Property" frame="$this/FCJH_TipSel{n}" Visible="true"/>{at(CARD, TAL, M)}</State>\n'
            f'{T*5}<State name="Away">{at("$GameUI", 9999, 9999)}</State>\n{T*4}</StateGroup>\n')


def talent_tips():
    """Tooltips on the card's talents. Our talent icons are pictures bound to the talent row
    and give none; tooltips only come from Blizzard's talent icons in Blizzard's own panel
    (the heroic-tooltip work, 2026-10-02). So: our own instance of Blizzard's talent panel,
    as the talents pane uses (FCJH_InfoPane: a plain holder, mouse off, around a
    CleanTalentsPanelTemplate; its tooltips work), with every player's seven icons re-laid
    in a line the size of the card's talent strip, invisible but answering the mouse. Only
    the selected player's row is on the card (tip_switch); the whole thing shows only while
    the card does (the gate). Just above the card (605), under the command card (610)."""
    # each icon placed against its own player's box, named by its full path
    icon = lambda k, n: (f'{T*10}<Frame type="UnitStatusTalentIcon" name="TalentTreeIcon{k}">\n'
                         + placed(0, tal_left(k) - M, TAL_SIZE, TAL_SIZE, 11, TIP_ROW.format(n=n))
                         + f'{T*11}<Alpha val="0"/>\n{T*10}</Frame>\n')
    # the row's heroic ability icon and Tracer's meter: faded, deaf to the mouse (as the
    # heroic tooltips' copies have them)
    muted = lambda ty, nm: (f'{T*9}<Frame type="{ty}" name="{nm}"><Alpha val="0"/><AcceptsMouse val="false"/>'
                            f'<AcceptsMouseTooltip val="false"/></Frame>\n')
    nest = ("SelectionUnitStatusPanel", "SelectionUnitStatusPanel"), ("UnitStatusFrame", "UnitStatusFrame0")
    rows = "".join(
        f'{T*5}<Frame type="HeroTalentsPanelPlayerFrame" name="PlayerFrame{n}">\n'
        # parked until selected (tip_switch)
        + placed(9999, 9999, TIP_W, TAL_SIZE, 6, "$GameUI")
        + f'{T*6}<Frame type="Frame" name="TalentsContainerFrame">\n{T*7}<Batch val="false"/>\n'
        + "".join(f'{T*(7 + i)}<Frame type="{ty}" name="{nm}">\n' for i, (ty, nm) in enumerate(nest))
        + f'{T*9}<Frame type="PlayerHeroSelectedTalentTreeFrame" name="HeroSelectedTalentTreeFrame">\n'
        + "".join(icon(k, n) for k in range(1, 8))
        + f'{T*9}</Frame>\n'
        + muted("UnitStatusAbilIcon", "UnitStatusAbil") + muted("Frame", "TracerChargeContainer")
        + f'{T*8}</Frame>\n{T*7}</Frame>\n{T*6}</Frame>\n{T*5}</Frame>\n'
        for n in range(10))
    return (f'{T*2}<!-- Tooltips on the card\'s talents (inspect_card.talent_tips) -->\n'
            f'{T*2}<Frame type="Frame" name="FCJH_TalentTips">\n'
            f'{T*3}<Anchor relative="$parent"/>\n{T*3}<Visible val="false"/>\n{T*3}<AcceptsMouse val="false"/>\n'
            f'{T*3}<RenderPriority val="605"/>\n'
            # Blizzard's whole top-bar talent panel as the root, our changes on top - exactly as
            # the heroic tooltips' copies are built, where icons both re-size and move. Built
            # here from its parts instead (a clean panel, its row container given a row
            # template in our own declaration), the rows kept Blizzard's icon places and sizes:
            # blue bottom-panel rows whatever we tried, top-bar rows on both teams (2026-10-05)
            f'{T*3}<Frame type="Frame" name="FCJH_TalentTipPanel" template="TalentsOverviewPanel/TalentsOverviewTopBarTemplate">\n'
            f'{T*4}<Anchor side="Top"    relative="{CARD}" pos="Min" offset="0"/>\n'
            f'{T*4}<Anchor side="Left"   relative="{CARD}" pos="Min" offset="0"/>\n'
            f'{T*4}<Anchor side="Bottom" relative="{CARD}" pos="Max" offset="0"/>\n'
            f'{T*4}<Anchor side="Right"  relative="{CARD}" pos="Max" offset="0"/>\n'
            # faded from the root: fading each icon left its picture parts drawing over our
            # talent pictures (2026-10-05); a faded frame still answers the mouse
            f'{T*4}<Alpha val="0"/>\n'
            f'{T*4}<Frame type="HeroTalentsPanel" name="TalentOverview">\n{T*5}<Visible val="true"/>\n{T*5}<Batch val="false"/>\n'
            f'{T*5}<Frame type="Frame" name="HeroTalentsPanelContainer">\n'
            + rows + f'{T*5}</Frame>\n{T*4}</Frame>\n{T*3}</Frame>\n{T*2}</Frame>\n')


def diag_team():
    """DIAGNOSTIC (2026-10-05, mirror matches): three squares in the title band's left end, lit
    by the unit-relation event the selection's status frame gets - blue: UnitStatusAlly, red:
    UnitStatusEnemy, white: UnitStatusOwner (Blizzard colours health bars by them). If blue and
    red follow the teams, they tell the card which player of a mirrored hero is selected."""
    events = (("Ally", "255,92,188,236"), ("Enemy", "255,231,92,121"), ("Owner", "255,255,255,255"))
    out = [f'{T*4}<!-- DIAGNOSTIC: which unit-relation event the selection gets (inspect_card.diag_team) -->\n']
    for i, (ev, colour) in enumerate(events):
        others = [e for e, _ in events if e != ev]
        out.append(
            f'{T*4}<Frame type="Image" name="FCJH_Diag{ev}">\n'
            + placed(8, M + i * 18, 14, 14, 5)
            + f'{T*5}<Texture val="@UI/PauseScreenDimImage"/>\n{T*5}<ColorAdjustMode val="Fill"/>\n'
            f'{T*5}<AdjustmentColor val="{colour}"/>\n{T*5}<RenderPriority val="700"/>\n'
            f'{T*5}<Alpha val="40"/>\n{T*5}<AcceptsMouse val="false"/>\n'
            f'{T*5}<Animation name="FCJH_On">\n{T*6}<Event event="UnitStatus{ev}" action="Reset,Play" frame="$parent"/>\n'
            f'{T*6}<Controller type="Fade" end="Pause">\n{T*7}<Key type="Curve" time="0" value="255" inout="Linear"/>\n'
            f'{T*7}<Key type="Curve" time="0.01" value="255" inout="Linear"/>\n{T*6}</Controller>\n{T*5}</Animation>\n'
            f'{T*5}<Animation name="FCJH_Off">\n'
            + "".join(f'{T*6}<Event event="UnitStatus{o}" action="Reset,Play" frame="$parent"/>\n' for o in others)
            + f'{T*6}<Controller type="Fade" end="Pause">\n{T*7}<Key type="Curve" time="0" value="40" inout="Linear"/>\n'
            f'{T*7}<Key type="Curve" time="0.01" value="40" inout="Linear"/>\n{T*6}</Controller>\n{T*5}</Animation>\n'
            f'{T*4}</Frame>\n')
    return "".join(out)


def unit():
    """The card's contents: a selection panel inside it, holding Blizzard's per-unit widgets.
    A SelectionUnitStatusPanel without a PlayerId follows the observer's selection."""
    tiers = "".join(label(f"FCJH_Tier{n}", TAL + TAL_SIZE + 2, tal_left(n), TAL + TAL_SIZE + 16,
                          tal_left(n) + TAL_SIZE, "FCJH_InspectTier", str(lv), 5)
                    for n, lv in enumerate((1, 4, 7, 10, 13, 16, 20), start=1))
    return f'''
{T*2}<!-- The card's contents, numbered 1-6 below: Blizzard's per-unit widgets in a selection
{T*2}     panel, following the observer's selection -->
{T*2}<Frame type="SelectionUnitStatusPanel" name="FCJH_InspectUnit">
{T*3}<Anchor relative="$parent"/>
{T*3}<AcceptsMouse val="false"/>
{T*3}<AcceptsMouseTooltip val="false"/>
{T*3}<RenderPriority val="660"/>
{T*3}<!-- INSIDE the card (round 5), so it hides with it. Beside the card (rounds 3-4) its
{T*3}     parts stayed on screen after click-off, bound to the card's Visible or faded by Alpha -->
{T*3}<Frame type="UnitStatusFrame" name="UnitStatusFrame0" template="TargetInfoPanelUnitStatusTemplate/TargetInfoPanelUnitStatusBarTemplate">
{T*4}<Anchor relative="$parent"/>
{T*4}<AcceptsMouse val="false"/>
{CARD_CONTENT}
{T*4}<!-- 1. animated model: DROPPED (round 6). The hero cutscene kept the first hero clicked
{T*4}     (Chromie) over every later selection; the static portrait underneath updates. -->

{diag_team()}
{T*4}<!-- 2. name (in the title band, user 2026-10-05), player, level -->
{T*4}<Frame type="UnitStatusName" name="FCJH_HeroName" template="UnitStatus/UnitStatusUnitNameTemplate">
{T*5}<!-- centred on the card: the template's own size (220 x 30) beat the
{T*5}     anchors and held it off centre (2026-10-05), so the size is given -->
{placed(0, TITLE, W - 2 * TITLE, TITLE, 5)}{T*5}<UseNameTypeVisibilityRules val="false"/>
{T*5}<Frame type="Label" name="Label"><Anchor relative="$parent"/><Style val="FCJH_InspectName"/></Frame>
{T*4}</Frame>
{T*4}<!-- the player's name comes with the player pack (Blizzard's player-name widget read
{T*4}     "Player 5" for every hero in round 4) -->
{T*4}<Frame type="UnitStatusLevel" name="FCJH_Level" template="UnitStatus/UnitStatusLevelTemplate">
{T*5}<!-- its right edge on the margin, as the player's name's left (the template's 25 x 20 beat
{T*5}     the anchors before and left it short of the edge, 2026-10-05) -->
{placed(NAME_BAND + NAME_DROP, W - M - 60, 60, NAME_H, 5)}{T*5}<!-- no truncation: "13" read "..." in round 7 -->
{T*5}<Frame type="Label" name="Label"><Anchor relative="$parent"/><Style val="FCJH_InspectLevel"/><Options val="NoWrapping | ScaleToPreventTruncation"/></Frame>
{T*4}</Frame>

{T*4}<!-- 3. fountain: the first buff, in Blizzard's own buff slot art (user, 2026-10-05): Blizzard's
{T*4}     "ready" art, dimmed while on cooldown, with the seconds left over it -->
{T*4}<!-- the plates' sensor, on the slot: Blizzard's fountain behaviour icon, present only while
{T*4}     the fountain is on cooldown. Its own pictures are off; it lends the slot its countdown
{T*4}     (the game fills a CooldownLabel in a behaviour icon, as in Blizzard's hero console) -->
{T*4}<Frame type="UnitStatusBehaviorIcon" name="FCJH_FountainSensor">
{placed(BUFFS, M, BUFF_W, BUFF_H, 5)}{T*5}<Behavior val="HealingFountainCooldown"/>
{T*5}<RenderPriority val="680"/>
{T*5}<AcceptsMouse val="false"/>
{T*5}<!-- its tooltip, Blizzard's own, while the fountain cools down (off while the sensor
{T*5}     covered the whole card) -->
{T*5}<Frame type="BehaviorIcon" name="BehaviorIcon" template="BehaviorBar/BehaviorIconTemplate">
{T*6}<Anchor relative="$parent"/>
{T*6}<AcceptsMouse val="false"/>
{"".join(f'{T*6}<Frame type="{ty}" name="{nm}"><Visible val="false"/><Alpha val="0"/></Frame>{chr(10)}'
         for ty, nm in (("Frame", "ImageMaskContainer"), ("Image", "IconImageBg"), ("Label", "StackLabel"),
                        ("ProgressBar", "QuestProgressBar"), ("ProgressBar", "CooldownBar"), ("Image", "BGFlashImage")))}{T*6}<Frame type="Label" name="CooldownLabel">
{T*7}<Anchor side="Top"    relative="$parent" pos="Min" offset="2"/>
{T*7}<Anchor side="Left"   relative="$parent" pos="Min" offset="9"/>
{T*7}<Anchor side="Bottom" relative="$parent" pos="Max" offset="0"/>
{T*7}<Anchor side="Right"  relative="$parent" pos="Max" offset="-6"/>
{T*7}<Style val="FCJH_HeroicCooldown"/>
{T*7}<Options val="NoWrapping | ScaleToPreventTruncation"/>
{T*7}<RenderPriority val="700"/>
{T*6}</Frame>
{T*5}</Frame>
{T*4}</Frame>
{T*4}<Frame type="Frame" name="FCJH_FountainReady">
{placed(BUFFS, M, BUFF_W, BUFF_H, 5)}{T*5}<RenderPriority val="670"/>
{T*5}<AcceptsMouse val="false"/>
{T*5}<!-- ready: Blizzard's hero console tooltip for it -->
{T*5}<Tooltip val="@UI/HealingFountainDescription"/>
{T*5}<TooltipAnchorPosition val="TopRight"/>
{T*5}<!-- BehaviorIconTemplate's pieces: the icon in the slanted buff mask, then the slot's frame -->
{T*5}<Frame type="Frame" name="ImageMaskContainer">
{placed(-2, 9, 40, 40, 6)}{T*6}<AlphaMaskTexture val="@UI/Storm_UI_InGame_Buff_IconMask"/>
{T*6}<Frame type="Image" name="IconImage">
{T*7}<Anchor side="Top"    relative="$parent" pos="Mid" offset="0"/>
{T*7}<Anchor side="Bottom" relative="$parent" pos="Mid" offset="0"/>
{T*7}<Anchor side="Left"   relative="$parent" pos="Mid" offset="0"/>
{T*7}<Anchor side="Right"  relative="$parent" pos="Mid" offset="0"/>
{T*7}<Width val="45"/>
{T*7}<Height val="45"/>
{T*7}<Texture val="@UI/Storm_UI_Ingame_HealingWell_Active"/>
{T*7}<!-- the middle of the art only: its own frame's edges drew as stray lines in the slanted
{T*7}     mask (user, 2026-10-05) -->
{T*7}<TextureCoords top="0.2" left="0.2" bottom="0.8" right="0.8"/>
{T*7}<RenderPriority val="671"/>
{T*7}<AcceptsMouse val="false"/>
{T*6}</Frame>
{T*5}</Frame>
{T*5}<Frame type="Image" name="IconImageBg">
{T*6}<Anchor relative="$parent"/>
{T*6}<Texture val="@UI/Storm_UI_InGame_Buff_Background"/>
{T*6}<RenderPriority val="672"/>
{T*6}<AcceptsMouse val="false"/>
{T*5}</Frame>
{T*5}<StateGroup name="FCJH_Fountain">
{T*6}<DefaultState val="Ready"/>
{T*6}<State name="Cooldown">
{T*7}<When type="Property" frame="$parent/FCJH_FountainSensor" Visible="true"/>
{T*7}<Action type="SetProperty" frame="$this" Alpha="60"/>
{T*7}<Action type="SetProperty" frame="$this" AcceptsMouseTooltip="false"/>
{T*6}</State>
{T*6}<State name="Ready">
{T*7}<Action type="SetProperty" frame="$this" Alpha="255"/>
{T*7}<Action type="SetProperty" frame="$this" AcceptsMouseTooltip="true"/>
{T*6}</State>
{T*5}</StateGroup>
{T*4}</Frame>

{T*4}<!-- 4. buffs then debuffs, one row after the fountain: Blizzard's buff bars inside the
{T*4}     selection panel (as Spazzo does). One row is all a hero needs (user, 2026-10-05) -->
{T*4}<Frame type="BehaviorBar" name="FCJH_Buffs" template="BehaviorBar/BuffBehaviorBarTemplate">
{T*5}<Anchor side="Top"  relative="$parent" pos="Min" offset="{BUFFS}"/>
{T*5}<Anchor side="Left" relative="$parent/FCJH_FountainReady" pos="Max" offset="-{BUFF_OVERLAP}"/>
{T*5}<RenderPriority val="670"/>
{T*4}</Frame>
{T*4}<Frame type="BehaviorBar" name="FCJH_Debuffs" template="BehaviorBar/DebuffBehaviorBarTemplate">
{T*5}<Anchor side="Top"  relative="$parent/FCJH_Buffs" pos="Min" offset="0"/>
{T*5}<Anchor side="Left" relative="$parent/FCJH_Buffs" pos="Max" offset="0"/>
{T*5}<RenderPriority val="670"/>
{T*4}</Frame>

{T*4}<!-- 5. talents (round 5). Blizzard's talent strip is keyed to a PLAYER and a selection
{T*4}     only gives a unit: rounds 3-4 drew blank, then team-coloured, squares. So the card
{T*4}     carries all ten of the talent pane's rows (PlayerFrame0-9, the same source the talent
{T*4}     pop-ups read), and shows the one whose plate holds the selected hero - see
{T*4}     FCJH_IsPlayerN below. Each pack also brings that player's name. -->
{"".join(player_pack(n) for n in range(10))}{tiers}
{T*4}<!-- 6. abilities: Blizzard's command card, laid over the card (command_panel) -->

{T*4}<!-- which player is selected: player N when the selected unit's hero is the hero on
{T*4}     plate N (unit checks, one state per hero, heroes from the game data). Mirror matches
{T*4}     (the same hero on both teams) would show both packs - not handled yet. -->
{"".join(matcher(n) + (tip_switch(n) if TALENT_TIPS else "") for n in range(10))}{T*3}</Frame>
{T*2}</Frame>
'''



FILE_HEADER = """
	<!-- The inspect card (tools/inspect_card.py; layout.toml element.inspect, 300 x 525 px): the
	     selected unit's portrait, name, player and level, fountain, health and resource, buffs
	     and debuffs, abilities, talents and stats. Shown when Blizzard's own small inspector
	     would be. It lives in Blizzard's console container, beside the command card whose buttons
     it borrows (as Ahli's hero card does). -->
	<Frame type="GameUI" name="GameUI" file="GameUI">
	<Frame type="Frame" name="UIContainer">
	<Frame type="Frame" name="ConsoleUIContainer">
"""


def layout(crop, head, team_colours, origin=(0, 0), px=0.9):
    """The whole layout file. crop: the plates' portrait crop (HeroCell.crop); head: the XML
    declaration, <Desc> and the generated-file banner; team_colours: {"blue": "rrggbb",
    "red": ...}, the border's (the plates' own blue and red)."""
    global CROP, ORIGIN, PX
    CROP, ORIGIN, PX = crop, origin, px
    TEAM.update({team: "255," + ",".join(str(int(hex_[i:i + 2], 16)) for i in (0, 2, 4))
                 for team, hex_ in team_colours.items()})
    HEROES[:] = cached_heroes()
    return (head + FILE_HEADER + card() + unit() + "\t\t\t</Frame>\n\t\t</Frame>\n"
            + (talent_tips() if TALENT_TIPS else "") + command_panel()
            + "\t</Frame>\n\t</Frame>\n\t</Frame>\n" + tracer_charge() + "</Desc>\n")


def tracer_charge():
    """Tracer's Pulse Bomb on her R button: Blizzard draws it from her own hero layout (a
    68 x 76 meter with a "0%" label) into the button's hero-specific panel, so sizing our
    button left it oversized (2026-10-05). Overridden in her file at our button's size, as
    Ahli does at his (56): the meter scaled from his 34 x 38, the percent label off (the fill
    shows the charge)."""
    k = CMD_SIZE / 56
    w, h, ping = round(34 * k), round(38 * k), round(40 * k)
    # the count was anchored to the percent label (now off) and sat cut off to the left
    # (2026-10-05): centred in the meter instead
    count = ('\t\t\t\t<Frame type="Label" name="ChargesLabel">'
             + "".join(f'<Anchor side="{s}" relative="$parent/TracerPulseBombBackgroundImage" pos="{p}" offset="0"/>'
                       for s, p in (("Top", "Min"), ("Left", "Min"), ("Bottom", "Max"), ("Right", "Max")))
             + '<Style val="FCJH_HeroicCooldown"/><Unclipped val="true"/></Frame>\n')
    return (f'\t<!-- Tracer\'s Pulse Bomb meter on the command card, at our button size (inspect_card.tracer_charge) -->\n'
            f'\t<Frame type="SelectionUnitStatusPanel" name="TracerPulseBombChargeButtonOverrideFrame" file="Tracer">\n'
            f'\t\t<Width val="{CMD_SIZE}"/>\n\t\t<Height val="{CMD_SIZE}"/>\n'
            f'\t\t<Frame type="UnitStatusFrame" name="UnitStatusFrame0">\n'
            f'\t\t\t<Frame type="UnitStatusAbilCharge" name="TracerPulseBombChargeFrame">\n'
            f'\t\t\t\t<Width val="{w}"/>\n\t\t\t\t<Height val="{h}"/>\n'
            f'\t\t\t\t<Frame type="ProgressBar" name="ChargeFillProgress"><Width val="{w}"/><Height val="{h}"/></Frame>\n'
            '\t\t\t\t<Frame type="Label" name="ChargePercentLabel"><Visible val="false"/><Text val=""/></Frame>\n'
            + count
            + f'\t\t\t\t<Frame type="Image" name="PulseBombReadyPingImage"><Width val="{ping}"/><Height val="{ping}"/><Unclipped val="true"/></Frame>\n'
            f'\t\t\t</Frame>\n\t\t</Frame>\n\t</Frame>\n')


@lru_cache(maxsize=None)
def cached_heroes():
    return tuple(hero_units())
