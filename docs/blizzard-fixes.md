# Blizzard's loose ends, and what FCJH did about them

A running log for the eventual write-up (user, 2026-10-13): things in Heroes of the Storm's own
observer UI that Blizzard left broken or player-only, and what we made or fixed. Each entry:
what Blizzard's UI does, how we know it's theirs (seen in the default UI or Ahli's, or read in
Blizzard's own files under `references/JamiePhan`), what we did (the `tools/` function), and
whether it's been seen working in game. Our own regressions - things we broke by moving
Blizzard's frames - don't belong here.

Back-filled from the project's history (HANDOFF.md and the commit log) on 2026-10-13; entries
from then on are written with their fix.

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
- **Ours:** Blizzard's toggle on Ctrl+Shift+R (layout.toml `element.replay` hotkey, ef1f1b6),
  switched on when a replay first shows the panel (as Ahli does, 030278d); a tab names the key
  while the panel is hidden.
- **Status:** hides in one press and the tab shows (user, 2026-10-16).
- **TRIAL, back on Ctrl+Shift+O** (everyone knows Blizzard's key; user, 2026-10-16): our own
  GameHotkeys.txt in every language (layout.toml `[blizzard_hotkeys]`) moves Save All to
  Ctrl+Alt+Shift+O. No interface we know of ships one, so it may not load; if Ctrl+Shift+O still
  does nothing, Ctrl+Shift+R goes back.

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
- **An inspect card for observers**, with Blizzard's own command card on it so the ability
  tooltips, cooldowns and charges are live, plus the player's talents with their tooltips on both
  teams (`inspect_card`; confirmed 2026-10-05).

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
  is the same so far. Hero forms that are units of their own (Medivh's Raven and the like) are
  still to be checked (HANDOFF item 14).

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
