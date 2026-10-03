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
  - D Q W E Z per hero from each hero unit's ability card in the game data (hero_cards)
  - X closes it; its back takes the mouse so a click inside doesn't deselect (round 9)
"""
from functools import lru_cache
from pathlib import Path

T = "\t"

# Pane-local layout, in layout units (the card is 333 x 833: 300 x 750 px)
W = 333
TITLE = 29
NAME_BAND = 154                    # the name/level band, under the portrait
PORTRAIT = (TITLE, NAME_BAND)      # top, bottom: stops at the band (round 3 ran it under the
                                   # band and the art hid the level and fountain)
HP = (207, 231)
MANA = (233, 249)
FOUNTAIN = (NAME_BAND + 10, NAME_BAND + 32, 226, 260)   # top, bottom, left, right: left of the level
# Buffs then debuffs as one block: the debuff bar follows the buff bar on the same row (as in
# Blizzard's hero console); once there are 4+ buffs it drops to a second row.
BUFFS_LABEL, BUFFS, BUFF_ROW = 258, 274, 42
# Abilities mimic Blizzard's ability card: 1-5 on top, D Q W E R Z under it, at the talent
# strip's icon size and column spacing so all three rows line up.
TAL_SIZE, TAL_STEP = 36, 43
ABIL_LABEL, ABIL_ROWS = 366, (382, 425)
TAL_LABEL, TAL = 471, 487
STATS_LABEL, STATS, STAT_ROW = 551, 569, 24
M = 14                              # side margin

# The ability card's slots: (hotkey, frame, row, column, fixed AbilityLink). D Q W E Z come per
# hero from the game data (hero_cards, set by FCJH_Abilities); R is the talent strip's heroic
# (player_pack); Z falls back to the shared mount. 1-5 are talent-granted actives - Ahli's
# method, one icon per candidate ability shown only if the hero has it: two of Auriel's so
# far, as a test; a table for every hero is still to do.
SLOTS = [("1", "FCJH_Abil1", 0, 0, "AurielAngelicFlight"), ("2", "FCJH_Abil2", 0, 1, "AurielShieldOfHope"),
         ("3", "FCJH_Abil3", 0, 2, ""), ("4", "FCJH_Abil4", 0, 3, ""), ("5", "FCJH_Abil5", 0, 4, ""),
         ("D", "FCJH_AbilD", 1, 0, ""), ("Q", "FCJH_AbilQ", 1, 1, ""), ("W", "FCJH_AbilW", 1, 2, ""),
         ("E", "FCJH_AbilE", 1, 3, ""), ("R", "FCJH_AbilR", 1, 4, ""),   # R's icon comes with the player pack (player_pack)
         ("Z", "FCJH_AbilZ", 1, 5, "Mount")]


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


def lamp(name, x, colour, extra=""):
    """DIAGNOSTIC: a 30 px square at (x, 400) px on screen, hidden until something shows it."""
    ox, oy = round(x / 0.9), round(400 / 0.9)
    return (f'{T*2}<Frame type="Image" name="{name}">\n'
            + "".join(f'{T*3}<Anchor side="{sd}" relative="$GameUI" pos="Min" offset="{v}"/>\n'
                      for sd, v in (("Left", ox), ("Top", oy), ("Right", ox + 33), ("Bottom", oy + 33)))
            + f'{T*3}<Texture val="@UI/PauseScreenDimImage"/>\n{T*3}<ColorAdjustMode val="Fill"/>\n'
            f'{T*3}<AdjustmentColor val="{colour}"/>\n{T*3}<RenderPriority val="950"/>\n{T*3}<Visible val="false"/>\n'
            f'{T*3}<AcceptsMouse val="false"/>\n{T*3}<AcceptsMouseTooltip val="false"/>\n{extra}{T*2}</Frame>\n')


def inspect_diagnostics():
    """DIAGNOSTIC (2026-10-02): inspect stopped showing at 80a3f39 (a talent-row change) and
    hiding either talent row doesn't bring it back. Two lamps at (1000 / 1040, 400) px:
    green while Blizzard's own inspector (the card's on/off switch) is shown, cyan while our
    card is; Control+Shift+7 forces our card shown, whatever the switch says."""
    watch = (f'{T*3}<StateGroup name="FCJH_Watch">\n{T*4}<DefaultState val="Off"/>\n'
             f'{T*4}<State name="On"><When type="Property" frame="$parent/FCJH_Inspect" Visible="true"/>'
             f'<Action type="SetProperty" frame="$this" Visible="true"/></State>\n'
             f'{T*4}<State name="Off"><Action type="SetProperty" frame="$this" Visible="false"/></State>\n'
             f'{T*3}</StateGroup>\n')
    force = (f'{T*2}<Frame type="ToggleControl" name="FCJH_ForceInspect">\n'
             f'{T*3}<Anchor side="Top" relative="$parent" pos="Min" offset="0"/>\n'
             f'{T*3}<Anchor side="Left" relative="$parent" pos="Min" offset="0"/>\n'
             f'{T*3}<Width val="1"/>\n{T*3}<Height val="1"/>\n'
             f'{T*3}<Shortcut val="Control+Shift+7"/>\n{T*3}<Visible val="false"/>\n{T*3}<AcceptsMouse val="false"/>\n'
             f'{T*3}<Animation name="FCJH_Force">\n'
             f'{T*4}<Event event="OnShown" action="DirectionForward,Play"/>\n'
             f'{T*4}<Event event="OnHidden" action="DirectionReverse,Play"/>\n'
             f'{T*4}<Controller type="Visibility" end="Pause" frame="$parent/FCJH_Inspect">\n'
             f'{T*5}<Key type="Bool" time="0" value="false"/>\n'
             f'{T*5}<Key type="Bool" time="0.001" value="true"/>\n'
             f'{T*4}</Controller>\n{T*3}</Animation>\n{T*2}</Frame>\n')
    return (f'{T*2}<!-- DIAGNOSTIC: inspect lamps and force-show (inspect_diagnostics) -->\n'
            + lamp("FCJH_DiagBlizzInspect", 1000, "255,40,220,60")
            + lamp("FCJH_DiagOurInspect", 1040, "255,0,230,255", watch) + force)


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
           f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_DiagBlizzInspect" Visible="true"/>\n{T*4}</State>\n'
           f'{T*4}<State name="Hide">\n'
           f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_Inspect" Visible="false"/>\n'
           f'{T*5}<Action type="SetProperty" frame="$parent/FCJH_DiagBlizzInspect" Visible="false"/>\n{T*4}</State>\n'
           f'{T*3}</StateGroup>\n{T*2}</Frame>\n' + inspect_diagnostics() +
           f'{T*2}<!-- The card: our copy of Blizzard\'s inspect box -->\n'
           f'{T*2}<Frame type="TargetInfoFrame" name="FCJH_Inspect">\n'
           f'{T*3}<Visible val="false"/>\n'
           # Round 9: an X in the title band's right end, like the info panes' (tools/gen.py
           # close_button). It hides the card directly (end="Stop": not held), so the card
           # stays closed until Blizzard's inspector next hides and shows again (click off,
           # then select a unit).
           f'{T*3}<Frame type="Button" name="FCJH_Close">\n'
           f'{T*4}<Anchor side="Top"   relative="$parent" pos="Min" offset="0"/>\n'
           f'{T*4}<Anchor side="Right" relative="$parent" pos="Max" offset="0"/>\n'
           f'{T*4}<Width val="{TITLE}"/>\n{T*4}<Height val="{TITLE}"/>\n'
           f'{T*4}<RenderPriority val="700"/>\n{T*4}<AcceptsMouse val="true"/>\n'
           f'{T*4}<Frame type="Label" name="FCJH_X">\n{T*5}<Anchor relative="$parent"/>\n'
           f'{T*5}<Style val="ObsBar_MatchTimer"/>\n{T*5}<Text val="X"/>\n{T*5}<AcceptsMouse val="false"/>\n{T*4}</Frame>\n'
           f'{T*4}<Animation name="FCJH_Close">\n{T*5}<Event event="OnClick" action="Reset,Play"/>\n'
           f'{T*5}<Controller type="Visibility" end="Stop" frame="$parent">\n'
           f'{T*6}<Key type="Bool" time="0" value="false"/>\n{T*5}</Controller>\n{T*4}</Animation>\n'
           f'{T*3}</Frame>\n'
           f'{T*3}<Anchor side="Top"    relative="$parent" pos="Min" offset="#FCJH_INSPECT_T"/>\n'
           f'{T*3}<Anchor side="Left"   relative="$parent" pos="Min" offset="#FCJH_INSPECT_L"/>\n'
           f'{T*3}<Anchor side="Bottom" relative="$parent" pos="Min" offset="#FCJH_INSPECT_B"/>\n'
           f'{T*3}<Anchor side="Right"  relative="$parent" pos="Min" offset="#FCJH_INSPECT_R"/>\n'
           f'{T*3}<AcceptsMouse val="false"/>\n{T*3}<RenderPriority val="650"/>\n']
    chrome = []
    # Round 9: the back takes the mouse, so a click inside the card no longer falls through to
    # the map (which deselects the unit and closes the card, 2026-09-30)
    chrome.append(fill("FCJH_Back", 0, 0, 833, 0, "215,11,12,20", 200, 3, "Max")
                  .replace('<AcceptsMouse val="false"/>', '<AcceptsMouse val="true"/>'))
    chrome.append(fill("FCJH_TitleBand", 0, 0, TITLE, 0, "235,24,28,48", 210, 3, "Max"))
    chrome.append(label("FCJH_Title", 0, 0, TITLE, 0, "ObsBar_MatchTimer", "INSPECT", 3, "Max"))
    chrome.append(fill("FCJH_NameBand", NAME_BAND, 0, 196, 0, "235,16,18,32", 240, 3, "Max"))
    for text, top in (("BUFFS  ·  DEBUFFS", BUFFS_LABEL), ("ABILITIES", ABIL_LABEL),
                      ("TALENTS", TAL_LABEL), ("STATS", STATS_LABEL)):
        chrome.append(label(f"FCJH_Section{text.split()[0].capitalize()}", top, M, top + 15, -M, "FCJH_InspectSection", text, 3, "Max"))
    stats = [("AttackDamageFrame", 0, 0), ("MoveSpeedFrame", 1, 0), ("AttackSpeedFrame", 0, 1), ("PhysicalArmorFrame", 1, 1),
             ("AttackRangeFrame", 0, 2), ("AbilityArmorFrame", 1, 2), ("AbilityPowerFrame", 0, 3)]
    stat_frames = "".join(
        f'{T*6}<Frame type="TargetInfoStatFrame" name="{n}">\n'
        f'{T*7}<Anchor side="Top" relative="$parent" pos="Min" offset="{r * STAT_ROW}"/>\n'
        f'{T*7}<Anchor side="Left" relative="$parent" pos="Min" offset="{c * 155}"/>\n'
        f'{T*7}<Anchor side="Right" relative="$this" pos="Min" offset="0"/>\n{T*7}<Width val="150"/>\n{T*6}</Frame>\n'
        for n, c, r in stats)
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
{rect(STATS, M, STATS + 4 * STAT_ROW, -M, i=5, right_pos="Max")}{stat_frames}{T*5}<!-- the stat tooltips open off the card's right edge, level with the stats (Blizzard's
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


SLOT_KEYS = {"Trait": "D", "Ability1": "Q", "Ability2": "W", "Ability3": "E", "Mount": "Z"}
NOT_CUSTOM_MOUNT = {"Mount", "Dismount", "attack", "stop"}


def hero_cards():
    """{hero unit: {D/Q/W/E/Z: ability id}} from each hero unit's ability card (CUnit
    CardLayouts index 0, LayoutButtons by Slot). Rules (user, 2026-09-29): D only when the
    trait is something you press - a trait slot holding a plain Passive button counts as
    passive, even if a situational button shares it (Chromie's detonate); Z only for a custom
    mount (most heroes list none: the shared mount lives elsewhere). Per slot: the first
    command button with no Requirements that isn't a Cancel."""
    import xml.etree.ElementTree as ET
    cards = {}
    for f in list((MODS / "heromods").rglob("*.xml")) + list((MODS / "heroesdata.stormmod").rglob("*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for u in root.iter("CUnit"):
            uid = u.get("id") or ""
            if not uid.startswith("Hero") or uid not in HEROES:
                continue
            layout = next((c for c in u.findall("CardLayouts") if c.get("index", "0") == "0"), None)
            if layout is None:
                continue
            card, passive = {}, set()
            for b in layout.findall("LayoutButtons"):
                key = SLOT_KEYS.get(b.get("Slot"))
                if not key:
                    continue
                if b.get("Type") == "Passive" and not b.get("Requirements"):
                    passive.add(key)
                if b.get("Type") != "AbilCmd" or b.get("Requirements") or "Cancel" in (b.get("Face") or ""):
                    continue
                abil = (b.get("AbilCmd") or "").split(",")[0]
                if not abil or (key == "Z" and abil in NOT_CUSTOM_MOUNT):
                    continue
                card.setdefault(key, abil)
            if "D" in passive:
                card.pop("D", None)
            if card:
                cards[uid] = card
    return cards


CARDS = {}   # {hero unit: {D/Q/W/E/Z: ability}} (hero_cards): set by layout()
CROP = None   # the plates' portrait crop (top, left, bottom, right): set by layout()


def plate(n):
    return PLATE.format(t=1, m=n + 1) if n < 5 else PLATE.format(t=2, m=n - 4)


def player_pack(n):
    """Player n's talents (7 icons), heroic (at R) and name, from the talent pane's row n.
    Hidden (Alpha 0) unless FCJH_IsPlayer{n} matches."""
    row = ROW.format(n=n)
    tree = f"{row}/TalentsContainerFrame/SelectionUnitStatusPanel/UnitStatusFrame0"
    colour = "blue" if n < 5 else "red"
    # round 7: an icon (and its team-coloured square, as in the talent pane) shows only once its
    # tier is picked - an unpicked tier's picture is a plain white square
    icons = "".join(
        f'{T*5}<Frame type="Image" name="FCJH_Talent{k}">\n'
        + rect(TAL, M + (k - 1) * TAL_STEP, TAL + TAL_SIZE, M + (k - 1) * TAL_STEP + TAL_SIZE, i=6)
        + f'{T*6}<Texture val="{{{tree}/HeroSelectedTalentTreeFrame/TalentTreeIcon{k}/IconImage/@Texture}}"/>\n'
        f'{T*6}<RenderPriority val="668"/>  <!-- over the dark tier squares (665) -->\n'
        f'{T*6}<Alpha val="0"/>\n'
        f'{T*6}<AcceptsMouse val="true"/>\n{T*6}<AcceptsMouseTooltip val="true"/>  <!-- EXPERIMENT: the talent pane icon\'s own tooltip -->\n'
        f'{T*6}<Tooltip val="{{{tree}/HeroSelectedTalentTreeFrame/TalentTreeIcon{k}/@Tooltip}}"/>\n'
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
    portrait = (f'{T*5}<Frame type="Image" name="FCJH_Portrait">\n'
                + rect(PORTRAIT[0], 2, PORTRAIT[1], -2, i=6, right_pos="Max")
                + f'{T*6}<Texture val="{{{plate(n)}/HeroPortraitImage/@Texture}}"/>\n'
                f'{T*6}<TextureCoords top="{CROP[0]}" left="{CROP[1]}" bottom="{CROP[2]}" right="{CROP[3]}"/>\n'
                f'{T*6}<RenderPriority val="668"/>\n{T*6}<AcceptsMouse val="false"/>\n{T*5}</Frame>\n')
    rl, rt = M + 4 * TAL_STEP, ABIL_ROWS[1]
    heroic = (f'{T*5}<Frame type="UnitStatusAbilIcon" name="FCJH_Heroic">\n'
              + rect(rt, rl, rt + TAL_SIZE, rl + TAL_SIZE, i=6)
              + f'{T*6}<AbilityLink val="{{{tree}/HeroSelectedTalentTreeFrame/@HeroicAbilLink}}"/>\n'
              f'{T*6}<AcceptsMouse val="false"/>\n'
              f'{T*6}<Frame type="AbilIcon" name="AbilIcon">\n{T*7}<Anchor relative="$parent"/>\n'
              f'{T*7}<Frame type="Image" name="IconImage"><Anchor relative="$parent"/><AcceptsMouse val="true"/><AcceptsMouseTooltip val="true"/></Frame>\n'
              f'{T*7}<Frame type="Label" name="CooldownLabel"><Anchor relative="$parent"/><Style val="FCJH_HeroicCooldown"/></Frame>\n'
              f'{T*6}</Frame>\n{T*5}</Frame>\n')
    name = label("FCJH_PlayerName", NAME_BAND + 24, M, NAME_BAND + 40, 220, "FCJH_InspectSub",
                 f"{{{row}/PlayerNameFrame/PlayerNameLabel/@Text}}", 5)
    return (f'{T*4}<Frame type="Frame" name="FCJH_Player{n}">\n{T*5}<Anchor relative="$parent"/>\n'
            f'{T*5}<Alpha val="0"/>\n{T*5}<AcceptsMouse val="false"/>\n{T*5}<RenderPriority val="670"/>\n'
            f'{T*5}<!-- dark squares under the icons: an empty tier reads as a gap, not a hole -->\n'
            + "".join(fill(f"FCJH_TierBack{k}", TAL, M + (k - 1) * TAL_STEP, TAL + TAL_SIZE,
                           M + (k - 1) * TAL_STEP + TAL_SIZE, "200,30,32,48", 665, 5) for k in range(1, 8))
            + portrait + icons + heroic + name + f'{T*4}</Frame>\n')


# Heroes whose selected unit can differ from the plate's: (selected, on the plate). Guesses
# until seen in game - D.Va's mech vs pilot, each Viking vs the Vikings' controller.
ALSO = [("HeroDVaMech", "HeroDVaPilot"), ("HeroDVaPilot", "HeroDVaMech"), ("HeroDVaMech", "HeroDVaMech")] + [
    (v, p) for v in ("HeroOlaf", "HeroBaleog", "HeroErik") for p in (v, "HeroLostVikingsController")]


def matcher(n):
    """FCJH_IsPlayer{n}: shows pack n while the selected unit is the hero on plate n."""
    states = "".join(
        f'{T*5}<State name="{sel}{"" if sel == on else "_" + on}">'
        f'<When type="Property" Unit="{sel}"/>'
        f'<When type="Property" frame="{plate(n)}/HeroStatus" Unit="{on}"/>'
        f'<Action type="SetProperty" frame="$this/FCJH_Player{n}" Alpha="255"/></State>\n'
        for sel, on in [(u, u) for u in HEROES] + ALSO)
    return (f'{T*4}<StateGroup name="FCJH_IsPlayer{n}">\n{T*5}<DefaultState val="No"/>\n{states}'
            f'{T*5}<State name="No"><Action type="SetProperty" frame="$this/FCJH_Player{n}" Alpha="0"/></State>\n'
            f'{T*4}</StateGroup>\n')


def unit():
    """The card's contents: a selection panel inside it, holding Blizzard's per-unit widgets.
    A SelectionUnitStatusPanel without a PlayerId follows the observer's selection."""
    t6 = T * 6
    abil = []
    for key, name, row, col, fixed in SLOTS:
        left, top = M + col * TAL_STEP, ABIL_ROWS[row]
        link = f'\n{t6}<AbilityLink val="{fixed}"/>' if fixed else ""
        abil_key = lambda name: f'''{T*5}<StateGroup name="{name}Present">
{t6}<DefaultState val="Yes"/>
{t6}<State name="NoIcon"><When type="Property" frame="$parent/{name}" Visible="false"/><Action type="SetProperty" frame="$this" Alpha="0"/></State>
{t6}<State name="NoAbil"><When type="Property" frame="$parent/{name}/AbilIcon" Visible="false"/><Action type="SetProperty" frame="$this" Alpha="0"/></State>
{t6}<State name="Yes"><Action type="SetProperty" frame="$this" Alpha="255"/></State>
{T*5}</StateGroup>
'''
        abil.append(f'''{T*5}<Frame type="UnitStatusAbilIcon" name="{name}">
{rect(top, left, top + TAL_SIZE, left + TAL_SIZE, i=6)}{t6}<Unclipped val="true"/>{link}
{t6}<Frame type="AbilIcon" name="AbilIcon">
{t6}\t<Anchor relative="$parent"/>
{t6}\t<Frame type="Image" name="IconImage"><Anchor relative="$parent"/><Unclipped val="true"/><AcceptsMouse val="true"/><AcceptsMouseTooltip val="true"/></Frame>
{t6}\t<Frame type="Label" name="CooldownLabel">
{t6}\t\t<Anchor relative="$parent"/>
{t6}\t\t<Style val="FCJH_HeroicCooldown"/>
{t6}\t\t<RenderPriority val="700"/>
{t6}\t\t<Animation name="FCJH_Dim">
{t6}\t\t\t<Event event="OnShown" action="DirectionForward,Play"/>
{t6}\t\t\t<Event event="OnHidden" action="DirectionReverse,Play"/>
{t6}\t\t\t<Controller type="Color" end="Pause" frame="$parent/IconImage">
{t6}\t\t\t\t<Key type="Curve" time="0" value="255,255,255" inout="Step"/>
{t6}\t\t\t\t<Key type="Curve" time="0.01" value="70,70,70" inout="Step"/>
{t6}\t\t\t</Controller>
{t6}\t\t</Animation>
{t6}\t</Frame>
{t6}\t<Frame type="ProgressBar" name="CooldownBar"><Anchor relative="$parent"/><Alpha val="0"/></Frame>
{t6}</Frame>
{T*5}</Frame>
''' + label(f"{name}Key", top + TAL_SIZE - 14, left + 2, top + TAL_SIZE, left + 16, "FCJH_InspectKey", key, 5,
                  extra=abil_key(name) if key in "12345" else ""))
    states = []
    # round 6: every hero's D Q W E Z from the game data (hero_cards); a slot with nothing in it
    # hides, icon and key letter both (D: passive traits; Z: the standard mount)
    for unit_id, card in sorted(CARDS.items()):
        acts = ""
        for key in "DQWEZ":
            frame, link = f"FCJH_Abil{key}", card.get(key)
            if link:
                acts += f'{T*7}<Action type="SetProperty" frame="$this/{frame}" AbilityLink="{link}"/>\n'
            a = 255 if link else 0
            acts += (f'{T*7}<Action type="SetProperty" frame="$this/{frame}" Alpha="{a}"/>\n'
                     f'{T*7}<Action type="SetProperty" frame="$this/{frame}Key" Alpha="{a}"/>\n')
        states.append(f'{T*6}<State name="{unit_id}">\n{T*7}<When type="Property" Unit="{unit_id}"/>\n{acts}{T*6}</State>\n')
    icons = "".join(
        f'{T*6}<Frame type="UnitStatusTalentIcon" name="TalentTreeIcon{n}">\n'
        f'{T*7}<Anchor side="Top"    relative="$parent" pos="Min" offset="0"/>\n'
        f'{T*7}<Anchor side="Left"   relative="$parent" pos="Min" offset="{(n - 1) * TAL_STEP}"/>\n'
        f'{T*7}<Anchor side="Bottom" relative="$this" pos="Min" offset="0"/>\n'
        f'{T*7}<Anchor side="Right"  relative="$this" pos="Min" offset="0"/>\n'
        f'{T*7}<Width val="{TAL_SIZE}"/>\n{T*7}<Height val="{TAL_SIZE}"/>\n{T*6}</Frame>\n'
        for n in range(1, 8))
    tiers = "".join(label(f"FCJH_Tier{n}", TAL + TAL_SIZE + 2, M + (n - 1) * TAL_STEP, TAL + TAL_SIZE + 16,
                          M + (n - 1) * TAL_STEP + TAL_SIZE, "FCJH_InspectTier", str(lv), 5)
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

{T*4}<!-- 2. name, player, level -->
{T*4}<Frame type="UnitStatusName" name="FCJH_HeroName" template="UnitStatus/UnitStatusUnitNameTemplate">
{rect(NAME_BAND + 3, M, NAME_BAND + 25, 220, i=5)}{T*5}<UseNameTypeVisibilityRules val="false"/>
{T*5}<Frame type="Label" name="Label"><Anchor relative="$parent"/><Style val="FCJH_InspectName"/></Frame>
{T*4}</Frame>
{T*4}<!-- the player's name comes with the player pack (Blizzard's player-name widget read
{T*4}     "Player 5" for every hero in round 4) -->
{T*4}<Frame type="UnitStatusLevel" name="FCJH_Level" template="UnitStatus/UnitStatusLevelTemplate">
{rect(NAME_BAND + 6, 266, NAME_BAND + 36, 324, i=5)}{T*5}<!-- no truncation: "13" read "..." in round 7 -->
{T*5}<Frame type="Label" name="Label"><Anchor relative="$parent"/><Style val="FCJH_InspectLevel"/><Options val="NoWrapping | ScaleToPreventTruncation"/></Frame>
{T*4}</Frame>

{T*4}<!-- 3. fountain: the plates' sensor; Blizzard's "ready" art in the name band, just left of
{T*4}     the level (dimmed while on cooldown) -->
{T*4}<Frame type="UnitStatusBehaviorIcon" name="FCJH_FountainSensor">
{T*5}<Anchor relative="$parent"/>
{T*5}<Behavior val="HealingFountainCooldown"/>
{T*5}<Alpha val="0"/>
{T*5}<AcceptsMouse val="false"/>
{T*5}<AcceptsMouseTooltip val="false"/>  <!-- its tooltip ("use the fountain...") covered the whole card -->
{T*5}<Frame type="BehaviorIcon" name="BehaviorIcon" template="BehaviorBar/BehaviorIconTemplate"><Anchor relative="$parent"/><AcceptsMouse val="false"/><AcceptsMouseTooltip val="false"/></Frame>
{T*4}</Frame>
{T*4}<Frame type="Image" name="FCJH_FountainReady">
{rect(FOUNTAIN[0], FOUNTAIN[2], FOUNTAIN[1], FOUNTAIN[3], i=5)}{T*5}<Texture val="@UI/Storm_UI_Ingame_HealingWell_Active"/>
{T*5}<RenderPriority val="680"/>
{T*5}<AcceptsMouse val="false"/>
{T*5}<StateGroup name="FCJH_Fountain">
{T*6}<DefaultState val="Ready"/>
{T*6}<State name="Cooldown">
{T*7}<When type="Property" frame="$parent/FCJH_FountainSensor" Visible="true"/>
{T*7}<Action type="SetProperty" frame="$this" Alpha="60"/>
{T*6}</State>
{T*6}<State name="Ready">
{T*7}<Action type="SetProperty" frame="$this" Alpha="255"/>
{T*6}</State>
{T*5}</StateGroup>
{T*4}</Frame>

{T*4}<!-- 4. buffs then debuffs, one block: Blizzard's buff bars inside the selection panel (as
{T*4}     Spazzo does). The debuff bar follows the buffs on the same row; with 4+ buffs it
{T*4}     drops to a second row (FCJH_BuffSpill below) -->
{T*4}<Frame type="BehaviorBar" name="FCJH_Buffs" template="BehaviorBar/BuffBehaviorBarTemplate">
{T*5}<Anchor side="Top"  relative="$parent" pos="Min" offset="{BUFFS}"/>
{T*5}<Anchor side="Left" relative="$parent" pos="Min" offset="{M}"/>
{T*5}<RenderPriority val="670"/>
{T*4}</Frame>
{T*4}<Frame type="BehaviorBar" name="FCJH_Debuffs" template="BehaviorBar/DebuffBehaviorBarTemplate">
{T*5}<Anchor side="Top"  relative="$parent/FCJH_Buffs" pos="Min" offset="0"/>
{T*5}<Anchor side="Left" relative="$parent/FCJH_Buffs" pos="Max" offset="0"/>
{T*5}<RenderPriority val="670"/>
{T*4}</Frame>
{T*4}<StateGroup name="FCJH_BuffSpill">
{T*5}<DefaultState val="OneRow"/>
{T*5}<State name="TwoRows">
{T*6}<When type="Property" frame="$this/FCJH_Buffs/BehaviorIcon3" Visible="true"/>
{T*6}<Action type="SetAnchor" frame="$this/FCJH_Debuffs" side="Top" relative="$parent" pos="Min" offset="{BUFFS + BUFF_ROW}" undo="true"/>
{T*6}<Action type="SetAnchor" frame="$this/FCJH_Debuffs" side="Left" relative="$parent" pos="Min" offset="{M}" undo="true"/>
{T*5}</State>
{T*5}<State name="OneRow"/>
{T*4}</StateGroup>

{T*4}<!-- 5. talents (round 5). Blizzard's talent strip is keyed to a PLAYER and a selection
{T*4}     only gives a unit: rounds 3-4 drew blank, then team-coloured, squares. So the card
{T*4}     carries all ten of the talent pane's rows (PlayerFrame0-9, the same source the talent
{T*4}     pop-ups read), and shows the one whose plate holds the selected hero - see
{T*4}     FCJH_IsPlayerN below. Each pack also brings that player's heroic (R) and name. -->
{"".join(player_pack(n) for n in range(10))}{tiers}
{T*4}<!-- 6. abilities, laid out like Blizzard's ability card: 1-5 on top (talent actives: two of
{T*4}     Auriel's as a test, shown only if she has them), D Q W E R Z below. D Q W E Z per hero
{T*4}     from the game data; R from the talent strip's heroic -->
{"".join(abil)}{T*4}<StateGroup name="FCJH_Abilities">
{T*5}<DefaultState val="Other"/>
{"".join(states)}{T*5}<State name="Other"/>
{T*4}</StateGroup>

{T*4}<!-- which player is selected: player N when the selected unit's hero is the hero on
{T*4}     plate N (unit checks, one state per hero, heroes from the game data). Mirror matches
{T*4}     (the same hero on both teams) would show both packs - not handled yet. -->
{"".join(matcher(n) for n in range(10))}{T*3}</Frame>
{T*2}</Frame>
'''



FILE_HEADER = """
	<!-- The inspect card (tools/inspect_card.py; layout.toml element.inspect, 300 x 750 px): the
	     selected unit's portrait, name, player and level, fountain, health and resource, buffs
	     and debuffs, abilities, talents and stats. Shown when Blizzard's own small inspector
	     would be. -->
	<Frame type="GameUI" name="GameUI" file="GameUI">
"""


def layout(crop, head):
    """The whole layout file. crop: the plates' portrait crop (HeroCell.crop); head: the XML
    declaration, <Desc> and the generated-file banner."""
    global CROP
    CROP = crop
    HEROES[:] = cached_heroes()
    CARDS.clear()
    CARDS.update(cached_cards())
    return head + FILE_HEADER + card() + unit() + "\t\t\t</Frame>\n\t\t</Frame>\n\t</Frame>\n</Desc>\n"


@lru_cache(maxsize=None)
def cached_heroes():
    return tuple(hero_units())


@lru_cache(maxsize=None)
def cached_cards():
    HEROES[:] = cached_heroes()
    return dict(hero_cards())
