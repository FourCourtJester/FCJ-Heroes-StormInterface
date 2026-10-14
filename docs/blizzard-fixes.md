# Blizzard's loose ends, and what FCJH did about them

A running log for the eventual write-up (user, 2026-10-13): things in Heroes of the Storm's own
observer UI that Blizzard left broken or player-only, and what we made or fixed. Each entry:
what Blizzard's UI does, how we know it's theirs (seen in the default UI or Ahli's), what we did,
and whether it's been seen working in game.

## Fixed

### Alterac Pass: the cage's hexagon lights only one team when both are capturing
- **Blizzard's:** during the cage fight, the hexagon beside the bars lights one half, "who's
  winning", which the script sets to whichever team started channelling first. With both teams
  capturing at once, the second team's half stays dark. Seen in the default UI and in Ahli's
  (user, 2026-10-13).
- **Why it's fixable:** the script also reports each team's capture separately, through the two
  bars' states (`TopBarCaptured`, `BottomBarCaptured`), and in the observer view both can be on.
- **Ours:** when both bars report capturing (or contested), our own copies of both lit halves and
  their pulsing glows draw over Blizzard's darkened half: same textures, team colours and pulse.
  Copies, so nothing fights Blizzard's own state for the hexagon. (`tools/maps.py` `av_both_lit`)
- **Status:** built 2026-10-13, not yet seen in game.

### Alterac Pass: camp alerts in a player's words on the observer's screen
- **Blizzard's:** the prisoner-camp alerts are sent to observers too, but in a player's words:
  "Allies capturing enemy camp", "Enemies retook their camp". On the everyone view they read from
  blue's side, so a caster sees "Enemies" for red. Seen in the default UI (user, 2026-10-13).
- **Ours:** they name the side - "Alliance capturing Horde camp", "Horde retook their camp" - in
  the capturing team's colour, the team taken from the alert's own event rather than its words, so
  it's right in any view. And each alert appears on its team's side of the screen (Alliance on
  blue's, Horde on red's), stacked with the side's other banners, instead of all piling up in
  the middle. (`camp_words`, `camp_slot`)
- **Status:** wording built 2026-10-13; placement built 2026-10-13; neither seen in game yet.
- **Limit:** English only - other languages keep Blizzard's words.

## Known, not fixed

### Alterac Pass: the first prisoner camp of a round doesn't alert
- Seen in the default UI (user, 2026-10-13): the first camp taken raised no alert, later ones did.
  It's in the map's script, which a layout can't change.

### Alterac Pass: a third camp alert can overwrite the second
- From Blizzard's script (`libmmap.galaxy`): it picks the alert slot by a running count, so if
  alert 1 ends while alert 2 is still up, the next alert goes into slot 2 again, replacing it.
  Not seen yet; script-side, so not ours to fix.
