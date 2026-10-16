# Blizzard's loose ends, and what FCJH did about them

A running log for the eventual write-up (user, 2026-10-13): things in Heroes of the Storm's own
observer UI that Blizzard left broken or player-only, and what we made or fixed. Each entry:
what Blizzard's UI does, how we know it's theirs (seen in the default UI or Ahli's, or read in
Blizzard's own files under `references/JamiePhan`), what we did (the `tools/` function), and
whether it's been seen working in game. Our own regressions - things we broke by moving
Blizzard's frames - don't belong here.

Back-filled from the project's history (HANDOFF.md and the commit log) on 2026-10-13; entries
from then on are written with their fix.

## At a glance, for the discussions

Two lists the write-up will want (user, 2026-10-16), one line each. The entries below have the
detail.

**Fixed: Blizzard handled it badly**
- Plates' heroic cooldowns and tooltips, which an observer never got.
- The inspect card showing the wrong player's talents in a mirror match.
- The inspect card's resource tooltip naming the last clicked unit's resource, not the
  selected hero's.
- Towers of Doom's town captures, invisible to the free observer view.
- Dragon Shire's Dragon Knight and Garden of Terror's Terrors, which didn't say (or said
  wrongly) whose they were.
- Alterac Pass: the cage's hexagon lighting one team when both capture, and the camp alerts
  in a player's words.
- Tomb of the Spider Queen's minimap and Battlefield of Eternity's Immortals fight, drawn
  off-centre.
- The replay controls: a hide key that never worked, and the box losing its top when the
  timeline hides.

**Made: Blizzard never had it**
- Hero plates built from the player's in-game top bar, with:
  - the fountain;
  - the heroic, its cooldown and tooltip;
  - a pop-up for each talent picked;
  - a heal pop-up when a hero drops to 25%.
- Blizzard's talent-lead flame, brought over from the player HUD.
- Four info panes, one at a time, on Ctrl+1-4.
- An inspect card for observers, Blizzard's own command card on it.
- Abathur's clone marked on the inspect card: the copied hero's face, Abathur's player, a
  CLONE note for the talents it hasn't got. **A show-off shot** (see the card's entry).
- The operator's four toggles: replay controls, chat, inspect card, player names.
- Every battleground fitted round one minimap place:
  - each map's minimap set by its own drawn size;
  - its objectives above it;
  - team banners on their team's side;
  - Haunted Mines' two views;
  - Infernal Shrines' lift for the skull race.
- Banners that say less and count more:
  - Sky Temple's live temples only;
  - Warhead's counters once there are nukes;
  - the tribute's count in its bar;
  - Volskaya's toast as a sentence;
  - the word-only static banners hidden;
  - every banner given an intro.
- Tomb's Webweavers on the summoning team's side.
- The player top bar's death and respawn animations on the plates: the skull, the respawn
  flash and glow (test build, not seen yet).
- A chrome frame round each team's row (test build, not seen yet).
- Tracer's and Junkrat's resource bars on the plates cut into one segment per shot, as in
  Blizzard's own player bars (`gen.RESOURCE_SEGMENTS`; test build, not seen yet).

**Can't be fixed from a layout** - the last section: Towers' cannon alerts, the death recap,
the talent picker under Ctrl, the command card for a hero's other unit, plate clicks for
D.Va's mech, Misha and the Vikings, a replay opening with its timeline hidden, inspecting
while paused, two Alterac script bugs, and script styles beating layout styles.

## Fixed

### Plates: heroic cooldowns for observers
- **Blizzard's:** the in-game heroic bar's cooldown never shows in an observer's view.
- **Ours:** each plate's heroic counts down from the observer talent row's own heroic count,
  which does update for observers (`gen.py`; commits f1e8622, 1df2787).
- **Status:** confirmed in game (2026-10-05).

### Plates: heroic tooltips for observers
- **Blizzard's:** the game's observer talent row never gives tooltips, so an observer can't hover
  a hero's heroic to read it.
- **Ours:** our own copy of Blizzard's top-bar talent panel, fitted under the plates so each
  player's heroic icon sits on their plate, gives the real tooltip - Tracer's Pulse Bomb with its
  title line composed from the game's own strings (80a3f39, 62695c1, e6b5378).
- **Status:** confirmed on every plate (2026-10-05).

### Inspect card: mirror matches show the wrong player's talents
- **Blizzard's:** the ally/enemy events a selection raises never come for an observer, so with
  the same hero on both teams, there was nothing to tell the two apart.
- **Ours:** a team sensor - a `UnitStatusColor` reading the selection's current relation, the
  way Blizzard colours the minimap - so the card shows the selected hero's own player
  (`inspect_card` `team_sense`; 69c45df, f1496c6).
- **Status:** confirmed on two Blazes (2026-10-05).

### Inspect card: the resource tooltip names the wrong unit's resource
- **Blizzard's:** the health and resource bars' tooltips name the resource by the card's
  TargetInfoFrame (`@UnitVitalName`). That follows the last unit *clicked* in the world, not
  the selection. A plate click selects without retargeting, so after clicking Sonya's unit,
  Chromie's plate read "Fury" (user).
- **Ours:** our own label (`inspect_card.vital`), set per unit from the game data
  (`vital_words`: the actors' VitalNames, through their parents, Mana by default), feeds the
  bars' two tooltip formats (`energy_formats`; 8ea751d).
- **Status:** confirmed in game, Chromie's plate after Sonya's (user, 2026-10-16).

### Towers of Doom: town captures invisible to the free observer view
- **Blizzard's:** "Allies / The Enemy captured <town>" is worded per viewer and sent to each
  team's players only. A player view (1-8) shows it; the free observer view never does.
- **Ours:** "Blue / Red team captured a town", on the capturing team's side, built from the
  observer-only `BroadcastToD<blue>v<red>` events the script sends the observer panel - blue's
  count going up means blue took it. Blizzard's originals are parked (`maps.towers_extra`; ec53caf,
  656555c).
- **Status:** confirmed working (2026-10-06), about a second late: the event comes with the new
  town's spawn.

### Dragon Shire: the Dragon Knight doesn't say whose it is
- **Blizzard's:** one knight banner for either team, and to an observer it reads the same.
- **Ours:** the team is read from the shrine markers - the script stops updating them once the
  knight is up, so the summoning team's moon and star are both still lit - and the banner goes
  on that team's side, mirrored for blue: the head flipped to the outer end and the health
  draining from the right (`maps.knight_side`, `knight_mask`; 98ab6cf, 1baee3c, 962e323).
- **Status:** confirmed in game, both teams (2026-10-09).

### Garden of Terror: observers see red's plant on blue's Terrors
- **Blizzard's:** the Terrors' health banner shows each team its own plant colour, and observers
  both at once - red's on top - whoever summoned.
- **Ours:** the summoning team is read from its seed count ("ACTIVE"), and the banner shows that
  team's plant, on that team's side (blue's Blizzard's way round, red's mirrored)
  (`maps.terror_side`; 89d2647).
- **Status:** red's confirmed (2026-10-12); blue's not seen yet - blue never summoned in the
  test replay.

### Alterac Pass: the cage's hexagon lights only one team when both are capturing
- **Blizzard's:** during the cage fight, the hexagon beside the bars lights one half, "who's
  winning", which the script sets to whichever team started channelling first. With both teams
  capturing at once, the second team's half stays dark. Seen in the default UI and in Ahli's
  (user, 2026-10-13).
- **Why it's fixable:** the script also reports each team's capture separately, through the two
  bars' states (`TopBarCaptured`, `BottomBarCaptured`), and in the observer view both can be on.
- **Ours:** when both bars report capturing (or contested), our own copies of both lit halves and
  their pulsing glows draw over Blizzard's darkened half: same textures, team colours and pulse.
  Copies, so nothing fights Blizzard's own state for the hexagon (`maps.av_both_lit`; 2bcea1d).
- **Status:** confirmed in game (user, 2026-10-14: "You even fixed the blizzard logic").

### Alterac Pass: camp alerts in a player's words on the observer's screen
- **Blizzard's:** the prisoner-camp alerts are sent to observers too, but in a player's words:
  "Allies capturing enemy camp", "Enemies retook their camp". On the everyone view they read from
  blue's side, so a caster sees "Enemies" for red. Seen in the default UI (user, 2026-10-13).
- **Ours:** Blizzard's sentences with the side names in place of "Allies" / "Enemies" -
  "Alliance capturing Horde camp", "Horde retook their camp" - in the colour Blizzard already
  gives the capturing team, the team taken from the alert's own event rather than its words, so
  it's right in any view. And each alert appears on its team's side of the screen (Alliance on
  blue's, Horde on red's), stacked with the side's other banners, instead of all piling up in
  the middle (`maps.camp_words`, `camp_slot`; 99f6a23, 8836507).
- **Status:** confirmed in game, placement and wording, over several rounds and after a
  fast-forward (user, 2026-10-14). The wording took four tries: a label of ours drawn over
  Blizzard's drew nothing, and nothing added to the alerts' template reached them; the side
  names written into Blizzard's own label worked, then a later alert reverted (the script
  rewrites it); what stuck is Blizzard's label hidden and our own in its style, chosen by the
  alert's event (b6e0e68).
- **Limit:** our lines are English; a client in another language gets them in English too.

### Tomb of the Spider Queen: its minimap drawn off-centre
- **Blizzard's:** the map's art sits about 21 px (at 1080p) left of the centre of its own
  minimap square, so its bottom point lands well left of the gem counts' blue/red split under it.
  The user called it the most lopsided map so far (2026-10-14).
- **Ours:** Tomb's minimap moves 18 px right, so the art is centred. The gem counts, the
  Webweavers banner and the egg timer stay where they were (`maps.py` `across`).
- **Status:** fixed, seen in game (2026-10-15).

### Battlefield of Eternity: the Immortals' fight drawn off-centre
- **Blizzard's:** the fight's boxes sit 8 px (at 1080p) left of the screen's centre, though the
  minimap under them is centred.
- **Ours:** the panel moves 9 right (`maps.py`, the Battlefield entry's `panels`; 90da446).
- **Status:** fixed, seen centred in game (2026-10-15).

### Replay controls: the hide key never worked
- **Blizzard's:** the replay panel's own hide toggle (`ToggleControlObserverTools`,
  stormobserverpanel.stormlayout) is bound to Ctrl+Shift+O, which Blizzard's own hotkeys give to
  the UI editor's Save All (`gamehotkeys.txt`: `UIEditorSaveAll=Control+Shift+O`), so the key never
  reaches the interface. It does nothing in the default UI, in Ahli 0.75 (which rebinds the same
  key) or in ours (user, 2026-10-16). The toggle also starts off while the panel shows, so a
  working key needed two presses.
- **Ours:** Blizzard's toggle on Ctrl+Shift+R (layout.toml `[toggles]` replay, ef1f1b6),
  switched on when a replay first shows the panel (as Ahli does, 030278d); a tab names the key
  while the panel is hidden.
- **Status:** confirmed in game - one press hides it and the tab shows, the next brings it back
  (user, 2026-10-16).
- **Blizzard's key can't be freed:** an interface's own GameHotkeys.txt (every language, moving
  Save All to Ctrl+Alt+Shift+O) doesn't load - Ctrl+Shift+O still did nothing (d33a0ec, user,
  2026-10-16). So Ctrl+Shift+R, and an interface can't add or move entries in the game's hotkey
  menu that way either.

### Replay controls: hiding the timeline drops the box's top
- **Blizzard's:** the panel's art hangs off its timeline, so hiding the timeline (its chevron or
  Ctrl+T) shrinks the box from its top. That suits a box at the bottom of the screen, but a
  box in a top corner falls away from the edge. Blizzard's hide/show also always slides in
  from the left.
- **Ours:** the box sits top-right, [screen] padding in, and its tab flush in the corner (user,
  2026-10-16). `FCJH_TimelineLift`
  raises the panel 40 units (gen.py `REPLAY_TIMELINE`) while the timeline is hidden, and our own
  copy of Blizzard's toggle slides it in from the right.
- **Status:** confirmed in game (user, 2026-10-16): the slide from the right, the box's top
  staying put with the timeline hidden, and the tab flush in the corner.

## Made for observers

Not bugs - things Blizzard's observer UI never offered, which the write-up may want.

- **Team banners on their team's side.** Blizzard draws a map's team banners in one place for
  both teams. Ours put each on its team's side, beside that team's plates, and mirror blue's
  (the hexagon at the outer end) - one builder for every map (`maps.team_banner`; 73fa559).
  Seen: Cursed Hollow's curse, Dragon Shire's knight, Blackheart's Bay's cannon, Towers of Doom's
  alerts, Garden of Terror's Terrors (red), Alterac Pass's cavalry, Battlefield of Eternity's
  winning Immortal (both teams; 2026-10-15 - Blizzard's countdown, fight and pushing Immortal all took
  turns in one place above the minimap; the countdown is now a neutral banner and the pushing
  Immortal goes to the winner's side). Infernal Shrines' Punisher on its summoner's side
  (`maps.punisher_side`; 61f1be5) - Blizzard's shrine countdown, "active" banner, Punisher and
  skull race all sit in one place above the minimap. Red's seen (2026-10-15); blue's mirrored
  one is built but not seen yet.
  Limit: in a player view (1-8) the script shows the viewer's team as Ally, so there the
  Punisher goes by the viewer's team, not the summoner's.
- **Sky Temple: only the temples that matter.** Blizzard's three temple discs sit on the
  minimap's bottom half all game, greyed between rounds, with no mark on the ones about to
  activate but a countdown label. Ours sit above the minimap on a backing bar, shown only during
  the countdown and while temples are live, and each disc only while it's next (carrying the
  time) or live - hidden in its own slot, so its place still names its lane (`PARTS["sky_temple"]`;
  c7e5da1). Seen in game with one and two temples (2026-10-15).
- **Warhead Junction: nuke counters only once there are nukes.** Blizzard's two "0" counters sit
  under the minimap from the start, though no warhead can be picked up until the first wave.
  Ours stay hidden until the warheads banner first says how many are left, then fade in for the
  rest of the game - and they're turned round as Tomb's gem counts (icon outer, count inner,
  the team strips meeting under the map), where Blizzard's had the count outside the icon
  (`maps.warhead_counters`, `nuke_sensor`; 18f4cbb, bca6517). Seen over three waves, no blink
  (2026-10-16).
- **Banner intros on the older maps.** Towers of Doom's banners slide and fade in; the older
  maps' have no intro at all. Ours give every banner the same intro (`maps.intro`). Blackheart's
  chests banner needed rebuilding to do it: Blizzard's bar is a fixed-width image anchored at
  one end, so there was nothing for the intro to grow (99a8030).
- **The rest of the map pass** (docs/maps.md has each map):
  - **One minimap place for every map.** Each map's minimap sits by its own drawn size (read
    from Blizzard's minimap art) on THE FLOOR, with its objectives above it at THE GAP.
    Blizzard's objective panels each sit wherever the map's script put them.
  - **Haunted Mines' two views:** the surface at load, then a 1 s glide to the whole map once
    the mines open (`maps.glide`; 2026-10-09).
  - **Infernal Shrines' lift:** the minimap rises 50 px only while the skull race covers its
    bottom, then settles back for the Punisher (`maps.lift`; 082126f).
  - **Tomb's Webweavers on the summoner's side:** Blizzard's own hexagon set per team, in the
    space between the minimap and that team's plates (seen both teams).
  - **Cursed Hollow's tribute count in its bar:** "Tribute Spawns In: 0:24", as Towers' altars
    read, where Blizzard's count hung under its hexagon (`maps.tribute_count`).
  - **Volskaya's toast as a sentence:** a sentence before its count, every language, centred on
    the screen (`maps.TOAST`; 6ff536a).
  - **Static banners hidden:** word-only banners that sit up until the objective is taken, saying
    what the minimap's markers already say (Shrine active, Collect the Tribute, Gather the seed!,
    Capture the Temples; 54eaed2, e48326a). To revisit after the final pass (HANDOFF item 16).
- **Hero plates for observers, from the player's in-game top bar** (`gen.py HeroCell`). It's the
  player's cell art, slanted and interlocking, scaled to fit. On it:
  - **Blizzard's in-game heroic panel**: icon, ready glow, cooldown, tooltip, Tracer's charge;
  - **the fountain**: bright when ready, dimmed with its countdown;
  - per-Viking bars and death timers, and Abathur's clone marker.
  Blizzard's observer bar has none of the fountain or the heroic panel.
- **Talent pop-ups:** the talent just picked pops up on its hero's plate, for every hero.
- **A heal pop-up:** a green plus when a hero drops to 25% health (once per dip; gone after
  about 4 s, at death or above 30%). Blizzard's critical-health element doesn't run in observer
  cells.
- **The talent-lead flame:** the player HUD's flame, shown behind the level of the team a talent
  tier ahead. The panel that carries it (`PartyFramePanel`) is hidden for observers, so it
  plays in our own frame.
- **Four info panes on Ctrl+1-4**: talents (in Blizzard's observer talent grid), KDA and hero
  damage, healing, structures and XP. One at a time, with each column's leader highlighted.
  Blizzard's observer panes keep their own places and lose Ctrl+1/2.
- **An inspect card for observers**, with Blizzard's own command card on it so the ability
  tooltips, cooldowns and charges are live, plus the player's talents with their tooltips on both
  teams (`inspect_card`; confirmed 2026-10-05).
  - **Abathur's clone marked** (2026-10-16, d309816 and 4fa66d8; seen working 2026-10-16): Ultimate Evolution's clone is a unit of the copied ally's type with
    nothing on it saying clone, so Blizzard's card - and ours, until now - read it as that ally:
    the ally's player and the ally's talents, none of which the clone has (Blizzard's script
    only levels it). Our card now takes it apart and puts it back right:
    - the **copied ally's portrait**, as the clone wears their skin;
    - **Abathur's player's name**, as Abathur's player owns and steers it;
    - a **CLONE note** with Ultimate Evolution's icon ("Abathur's Ultimate Evolution: no
      talents") where the talents go, and no talent tooltips;
    - the live command card and stats as on any hero (Evolution's +20% heal and damage, +10%
      speed show in the stats).

    Keyed off Blizzard's `UltimateEvolutionBuff`, which sits on the clone for its whole life
    (`inspect_card.clone_sensor`); the two players' packs each show their part
    (`FCJH_CloneParts{n}`). Cost: +34 KB on a 1 MB layout (a first draft cost 1.1 MB).

    **Showing it off** - a before/after pair is the shot: the copied ally's own card next to
    the clone's (same face, different player, talents swapped for the CLONE note), with the
    plate's CLONE marker in frame. To stage it:
    - build 4fa66d8 or later (the stamp, top left);
    - the replay **running** - a paused replay leaves stale stats on the card (0% / 100%
      paused, 20% / 110% running);
    - **click the clone** - the card doesn't follow it: Abathur stays selected as he burrows,
      and there's no hotkey for the clone;
    - the user's example: Budokai's Abathur cloning BlackoutCR's Falstad, about 8:20-9:01.
- **The operator's four toggles** (layout.toml `[toggles]`; user, 2026-10-16). Blizzard's
  hotkeys (`gamehotkeys.txt`) have none of these that works for an observer: the replay panel's
  is dead (above), and there's no chat, inspect or player-name toggle at all. Ahli and Spazzo
  each ship dozens of toggles; ours are just these four, each Ctrl+Shift and the thing's
  initial, and `validate.py` fails the build if one is a Blizzard in-game key or two of ours
  share one (the info panes' Ctrl+1-4 are the players' quick talent picks, which an observer
  can't use, so they're allowed):
  - Ctrl+Shift+R, the replay panel (above).
  - Ctrl+Shift+C, the chat messages (`FCJH_Toggles`: Blizzard's `ChatDisplay` fades out and in;
    Ahli's key too).
  - Ctrl+Shift+I, the inspect card: off, it slides left off screen (0.2 s) with its command card and talent
    tips (`inspect_card`, `FCJH_InspectSlot`), as Ahli's does. Hiding it lost: the game shows
    the card again on every new selection (user, 2026-10-16). Tried on Ctrl+I 2026-10-05 and
    dropped then.
  - Ctrl+Shift+N, the player names over the heroes' health bars (`FCJH_Toggles`). Ahli binds
    each name's VisibleTo* to his toggle, which would also bring back the names Blizzard hides
    on purpose (the NoName status frames, Medivh's raven, the Volskaya robot); ours binds the
    name's inner Label instead, so it only ever hides - on all 40 hero status frames Blizzard
    has, the heroes' own included.
  - **Status:** replay, chat and names confirmed first, then inspect, rebuilt
    to park off screen. All four confirmed in game (user, 2026-10-16) - DONE.

- **The player's death and respawn animations, on the observer plates** (test build ad48279,
  2026-10-16; not seen yet). The player's top bar (`partyframe.stormlayout`,
  `HeroDeathAnimFrameTemplate`) plays a skull when a hero dies. In the last 5 s of the timer it
  flashes the number white and pulses a glow over the plate. The observer cells have none of it. Ours:
  - Blizzard's skull art and timings, with Ahli's handover: the number fades in about 1 s after
    the skull (`gen.death_skull`);
  - Blizzard's flash keys between the red and pale timer styles, plus the glow pulse, on the
    respawn events (`gen.style_flash`, `pet_death_bindings`). The Vikings' own timers flash too.
  Which cell the game sends the respawn events to is still being tested (the event squares).
- **A chrome frame round each team's row** (test build ad48279, 2026-10-16; not seen yet).
  Blizzard's player view has a flat tray behind each row (`HUD_TopBar_Team_Backing_*`); the
  observer view has nothing. Ours is one anti-aliased line round the plates and the XP bar, in
  the top backplate's rim colours, cut for rows of 1-5 (`gen.row_frame_texture`, `[row_frame]`).

## Known, not fixed

### Towers of Doom: no cannon alert in the free observer view
- "Cannons are firing" goes to each team's players only, and nothing an observer's UI receives
  marks an altar capture, so no layout can raise it for the free view. Player views (1-8) still
  show Blizzard's, on the capturing team's side (568adc9).

### Death recap: never shows for an observer
- Blizzard's death recap toast is player-only as far as we can tell: pressing it from a hotkey
  did nothing in the observer (2026-10-05).

### The talent picker can't be hidden while Ctrl is held
- In a player's view (1-8), holding Ctrl opens Blizzard's talent picker, and the engine
  re-asserts it every frame: every way of hiding it lost, and fighting it made it flicker. Ahli
  and Spazzo leave it be too (2026-10-06).

### The command card doesn't follow a hero's other unit
- An observer's command card follows the selected unit only. Selecting Abathur while he's in
  Symbiote on someone leaves his own buttons up, not the Symbiote's. The same goes for a hero
  steering another unit. Neither Ahli's nor Spazzo's command card changes over (user,
  2026-10-16), so either neither author cared or the game sends nothing to change it by. Ours
  is the same. A form the player becomes (Medivh's Raven, 2026-10-16) is selected itself, so
  its own buttons show; the rest of the forms are in HANDOFF's final pass (item 14).

### D.Va's plate can't select her mech, nor Rexxar's Misha
- A plate's click (Blizzard's UnitTargetFrame: select the hero, centre the camera) always
  takes the player's hero unit, which for D.Va is the pilot. In her mech the pilot is tucked
  inside it, so the click does nothing (user, 2026-10-16); out of it, it works. Her data has
  no tracker from the pilot to the mech (only the mech's DVaMechPilotUnitTracker, the other
  way), so the plate can't be given a mech click as each Viking's is.
  Not fixable in a layout. TLV's plates take no clicks at all (user, 2026-10-16).
- Rexxar's Misha is the same: she can't be selected from the plate either (user, 2026-09-30,
  when her bar was dropped; 2026-10-16). A diagnostic then showed no click squares on her or
  on D.Va's mech - the game gives them no target.

### A replay can't open with its timeline hidden
- The replay panel's timeline (the slider) hides only by its own Hide button or the "Toggle
  Replay Timeline" hotkey, both engine-side; there's no option for it. Starting the slider
  hidden in the layout was tried (user, 2026-10-16): the game showed it again on load.

### A paused replay opens no inspector
- Clicking a unit while paused selects nothing new, so neither Blizzard's inspector nor ours can
  appear until the replay runs.

### Alterac Pass: the first prisoner camp of a round doesn't alert
- Seen in the default UI (user, 2026-10-13): the first camp taken raised no alert, later ones did.
  It's in the map's script, which a layout can't change.

### Alterac Pass: a third camp alert can overwrite the second
- From Blizzard's script (`libmmap.galaxy`): it picks the alert slot by a running count, so if
  alert 1 ends while alert 2 is still up, the next alert goes into slot 2 again, replacing it.
  Not seen yet; script-side, so not ours to fix.

### A script's label style beats a layout's
- Where Blizzard's script sets a label's style (`SetDialogItemStyle`), a layout state's `Style`
  doesn't stick: Battlefield of Eternity's pushing-Immortal label is restyled left-justified
  whenever its words are written. To right-justify blue's, we hide Blizzard's label there and
  show our own bound to its text (`maps.LANE_COPIES` `FCJH_LaneWords`; 3edae7a, seen right
  2026-10-15). This is a workaround, not a fix of Blizzard's.

### Battlefield of Eternity: the pushing Immortal's box just vanishes
- When the winner's Immortal dies, the script keeps its box up about a second, then turns the
  whole panel off: no outro. The fight's loser gets an X slashed across its portrait
  (`SlashAnimationTemplate`), the pushing Immortal nothing - checked in the default UI (user,
  2026-10-15). Ours would have to fit in that second, so we've left it.
