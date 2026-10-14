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

## Made for observers

Not bugs - things Blizzard's observer UI never offered, which the write-up may want.

- **Team banners on their team's side.** Blizzard draws a map's team banners in one place for
  both teams. Ours put each on its team's side, beside that team's plates, and mirror blue's
  (the hexagon at the outer end) - one builder for every map (`maps.team_banner`; 73fa559).
  Seen: Cursed Hollow's curse, Dragon Shire's knight, Blackheart's Bay's cannon, Towers of Doom's
  alerts, Garden of Terror's Terrors (red), Alterac Pass's cavalry.
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
