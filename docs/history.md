# FCJH — finished work

Done and dropped items moved out of HANDOFF §7 on 2026-10-16, kept as written for their
reasons and lessons. Their numbers are the old §7's (two lists ran side by side); HANDOFF §7
keeps the numbers of the items still open (7, 12, 14, 15, 16). The round-by-round detail is in
git history.

## Phase 1 (2026-09-25)

**Phase 1 (2026-09-25), condensed** — each is now a rule in HANDOFF §3 or a feature in §1: the
0.9 px/unit calibration; the minimap as a fixed square the engine fits maps into; the
`ToggleControl` hide hotkey; resource bars bound inside `HeroStatus` and coloured from
Blizzard's own hero table; talent-lead tiers compared as one-digit labels; talent picks via
`TalentTierState="TierSelected"`, watched by full path from outside the icons; our own
`HeroTalentsPanel` instance for the talents pane (the engine fills it, tooltips and all);
validator animation elements don't run in observer cells, so the heal sensor reads Blizzard's
health percent label instead. The round-by-round notes are in git history (`a0180f9` and the
commits around it).

## The 2026-10-05 session

**Earlier next** (end of the 2026-10-05 session):

Waiting on a look in game: the short inspect card without its resource slot. (Blizzard's
talent picker, left to the game: seen 2026-10-06 never coming up on its own in a player's
view, only on held Ctrl.) Done this session: panes in Blizzard's talent
grid and the inspect skin, hotkeys settled (our panes on Ctrl+1-4; the inspect and death
recap keys tried and dropped), the short card for non-heroes (camp mercenaries purple,
captured ones their team's), hero forms and empty ability slots (item 3), Towers of Doom's
alerts (item 8), and (2026-10-06) the plate fountain on the health bar's outline at the outer
end with blue's heroic mirrored to the inner end (§1). Unchecked from that: blue's heroic
tooltip hover after its move, the end of blue's narrowed bars (Blizzard's short-bar art is
shaped for a heroic on the left), and whether the inspect card's fountain shows the same thin
unmasked line the plate's did (its icon is drawn 45 in a 40 mask box). Open items, the
user's pick of order: the art pass (7, 12). Anchoring (4) built 2026-10-06; its non-16:9
test waits for the final pass (14). Every map's minimap, panel and team alerts (8) built 2026-10-06, a first
pass to fine-tune with test maps (user): Towers of Doom and Cursed Hollow DONE (2026-10-06);
next Braxis, Haunted Mines, Hanamura and on - each map's neutral banners move to red's column
as it's QA'd. Later, not now (user): the older maps' minimap jitter (item 8). Camp timers (13) dropped. Item 14 collects what
waits on replays with particular heroes and maps.

Confirmed in game by then: heroic tooltips on every plate (Varian's level-4 heroic, Tracer's
Pulse Bomb with its title line), heroic cooldown counts, click-to-follow (needs the game's
camera lock, **L**, on - observers can toggle it; a day of bisecting 2026-10-05 ended there),
Tracer's charge meter (Blizzard's art), talent and heal pop-ups (pane-sized; heal 2 px
smaller; on the plate's top edge - the user will judge that from viewers' feedback), the
inspect card with Blizzard's command card on it (tooltips, cooldowns, Tracer's count centred),
and the card's talent tooltips on both teams (2026-10-05). How those tooltips finally held:
Blizzard's WHOLE top-bar talent panel as the root
(`template="TalentsOverviewPanel/TalentsOverviewTopBarTemplate"`), our overrides on top - as
the plates' heroic-tooltip copies are built. Assembled from parts (a CleanTalentsPanelTemplate
whose `HeroTalentsPanelContainer` we re-templated in our own declaration), the rows kept
Blizzard's icon places and sizes (`inspect_card.talent_tips`).

1. **Inspect card: DONE (2026-10-05, evening QA rounds through f1496c6).** Seen and approved
   in game: hero name centred in the title band, player name and level (16, set 2 low in their
   band), team-coloured edge, Blizzard's inspector art as the background (permanent, 90%; its
   border under the contents), one padding (`PAD` 10) everywhere inside the edge, the card cut
   to fit (583 units, 525 px; gen refuses a layout.toml size that disagrees), the fountain as
   the first buff with its countdown and tooltips ("Healing Fountain Available" while ready),
   abilities spread across the card with the talent actives nested over the gaps (a honeycomb),
   talents spread across with pixel-exact empty-tier boxes (`inspect_card.line`), stats in
   three related rows, the Vikings' portrait on its own crop, no X (clicking off closes it),
   mirror matches (a team sensor, `team_sense`), and no stray lines or tooltips (Blizzard's
   inspect box contents hidden every frame, `FCJH_Hidden`). Left: placement (item 9).

   **All panels - DONE 2026-10-05 (through d716d10), seen in game:**
   - every pane wears the inspect card's look (Blizzard's inspector art, background 10%
     darker): one template, `FCJH_Constants/FCJH_PaneSkin` from `inspect_card.pane_skin`, at
     priority 400 under the rows. Blizzard's own pane backdrop (`obs_talents_bg`, one picture
     with the hexes and the blue-to-red blend) was tried, turned top to bottom, and scrapped.
   - the talents pane has Blizzard's row grid (`obs_talents_top`, 1130 x 60: blue's 565 on
     the left, red's mirrored) behind its rows, 2 above the first row as Blizzard hangs it;
     portraits and talents fitted into its boxes (heroic tiers 4 and 7 at 46). The pane's box
     didn't change.
   - **DONE 2026-10-23 (78644dc, HANDOFF §7 item 2):** ~~Later: the numbers panes (KDA, healing, structures) need a better visual~~ - fine for
     now (user). Their colour pass for both teams goes with it. Blizzard's stats grid art
     (`obs_stats_top`: a portrait box and five column cells per row, blue left, red right)
     and the leader underlines (`obs_stats_leader_blue/red`) are candidates (seen on a dev art board
     at native size, since removed: obs_stats_top is 1130 wide like the talents grid).
2. **Command card polish - DONE (2026-10-05).** Talent-granted abilities seen clean in the
   honeycomb on Sonya (level 16) and Chromie (a talent-granted ability, user): the morning's
   oversized art behind them (flame frame, faded portrait; `Screenshot2026-10-05 11_16_54.jpg`)
   went with the honeycomb's per-piece sizing. The mount button and the top row's layout were
   settled by the honeycomb too.
3. **Card swaps - researched 2026-10-05; forms built, awaiting QA.** What the data says:
   - **There's no swap to follow for an observer.** Blizzard has no per-hero command card
     layout; one CommandPanel shows the card of the unit it follows, and each form is a unit
     with its own card (`CardLayouts` in the unit data, buttons placed by named Slot:
     Ability1-3 = Q W E (00-02), Heroic = R (03), Mount = Z (04), Trait = D (05), Hearth = 13,
     talent actives 30-35; the slot-to-button map is the engine's). An observer's card follows
     the SELECTED unit: selecting Abathur shows Abathur's card even mid-Symbiote (the
     Symbiote is a unit of its own, `AbathurSymbiote`, the player steers). The "gap" in the
     user's Abathur screenshot (09:45:55) is his own card: Abathur has NO E (Ability3).
   - **Forms built:** units of their own that our hero check and player matchers didn't
     know - Medivh's Raven (`HeroMedivhRaven`), Deathwing's Dragonflight
     (`DeathwingDragonflightUnit`), Alexstrasza's Dragonqueen (`HeroAlexstraszaDragon`),
     Ragnaros's Molten Core (`RagnarosBigRag`), plus Greymane's Worgen, Valeera stealthed and
     Deathwing's World Breaker - `inspect_card.FORMS`, paired with their hero every way
     (which unit the plate shows meanwhile is unknown). To QA: each form shows the tall card
     with its player's portrait and talents, and its own buttons.
   - **Empty slots - built 2026-10-05, awaiting QA:** Blizzard's empty-slot frame
     (EmptyDynamicButtonImageTemplate, 80 alpha) under Q W E R at the buttons' frame-art size
     (`command_panel` empties): a button covers its own; Abathur's missing E shows the empty
     frame, the row unchanged (user's pick). No Z or D just isn't there (the row's ends).
   - Not in FORMS: D.Va and the Vikings (already in ALSO); Tychus's Odin (no morph or unit
     card of its own found - likely the same unit); Abathur's clone (likely a copy of the
     cloned hero's unit, so it would match that hero's player - unchecked); Samuro's images
     and Jaina's elemental (summons: the short card).
4. **Anchoring pass - BUILT 2026-10-06; the non-16:9 test is in the final pass (14) - the user
   stays at 1080p until then.** Until then everything we
   placed was anchored to the screen's top-left with 1080p offsets, so a window that isn't
   16:9 shifted Blizzard's centred pieces against ours (the hexagon left its backplate in a
   2558 x 1401 window, 2026-10-03). The game is always 1200 units tall; the width follows the
   window. Now, as Ahli and Spazzo do (and the user's previous UI: top-middle and
   bottom-middle), big pieces anchor to the screen and what sits on them to the piece
   (`gen.py ANCHORS`; the constants are offsets from each rect's anchor):
   - **top-centre**: our backplate (Blizzard's hexagon is centred); the team levels hang off
     the backplate, the advantage flames off the levels;
   - **bottom-centre**: the minimap and everything on the plates: the cells, XP and core
     bars, the row packer, the map alerts, the heroic tooltip rows' top, and the inspect card
     (in line with blue's row, user). They share the screen point (`gen.py PLATES_AT`), so
     they still move together. The first pass hung them off two bare row frames at the
     screen's root (`FCJH_BlueRow` / `FCJH_RedRow`). The frames sat right, but the cells
     inside Blizzard's observer panel came out twice their height and 40 px high. Anchor to
     the screen or a sibling, never to one of our frames in another branch (memory rule 22);
   - **left edge**: the info panes, [screen] padding in (user: they line up with the card at
     1080p); **top right**: the replay box, [screen] padding in, and its tab flush in the corner
     (since 2026-10-16, confirmed; the right edge's middle, then red's row, before); top left:
     the dev stamp.
   At 16:9 nothing moved (gen's `check_anchoring`, and every anchor in the XML resolved before
   and after: none off by a unit). Wider, the centred pieces stay together round the middle,
   the panes and replay box keep to their edges. Narrower than 16:9 isn't supported (the rows
   are sized to fill 16:9; they'd run off a 16:10 screen). To check in a non-16:9 window: the
   hexagon on its backplate, the rows round the minimap, the card on blue's row, plate clicks
   and heroic tooltips still working. The user expects to iterate on how it feels.

6. Tried and undone: hiding Blizzard's observer talent row plainly (71181f7, undone in
   d279ecc) - plate clicks stopped following heroes. The row stays held shown and spread.

9. **Viewport padding** (user, 2026-10-05). One more size pass on our hero plates, to set
   the screen's base padding: the gap between the plates and the screen's edges becomes the
   margin for everything. Then the replay box (top-left), the inspect card and the info panes
   (left column), and the rest of what we place respect that same margin - one number in
   layout.toml that they're all laid out from, rather than each element's own offsets. Goes
   with the anchoring pass (item 4) and the card's last item (line it up with the left edge).
   **Inspect placement** (user, 2026-10-05): the card's BOTTOM-LEFT corner sits on the blue
   plates' TOP-LEFT corner, that padding above it - the card grows up from the plates, its
   left edge in line with theirs. Laid out from the plates' rect and the padding (not its own
   `[element.inspect]` x/y), so it follows any plate resize; this settles the card's
   "line it up with the left edge" item.
   **Built 2026-10-05, 20 px experiment, awaiting in-game QA:** `[screen] padding = 20`;
   `[hero_row] scale = "fit"` (gen.py fit_hero_scale: 1.5561, XP bars 21 px from the sides,
   bottom at 1060); panes and inspect at x 20; the replay's frame at 14, 14 so its glass art
   (6 px inside the frame, `art_inset`) lands on 20 - seen in game; its collapsed tab at 20,
   20; inspect's y from `above = "blue_xp"`; gen.py check_padding refuses anything closer
   (top bar, minimap and kill feed exempt). Kill feed: back to Blizzard's own, top-left
   (FCJH_KillFeed removed; user: moved right, Blizzard's rows grow rightward so multi-kills
   ran off the screen, and they can't be right-aligned); seen in game: no clash with the
   replay box, and it sits ~20 px from the side on its own. The user's verdict
   (2026-10-05): the plates stay this size, so maps may be no wider than Towers of Doom
   (fine in game, ~380 px drawn). Blizzard's 394 px square caps every map at about that
   anyway, inside the plates' 415 px gap. Open, map by map (with item 8): HEIGHT. The
   square is centred at y ~936 and hangs off the bottom, so a tall map may cross the bottom
   padding or the screen's edge.
10. **Hotkeys for the inspect card and a death recap - DROPPED (user, 2026-10-05).** Built
    and tried: Ctrl+I switched the card off and on (a ToggleControl the card's gate also
    watched, as Ahli's Ctrl+C) - the user didn't like it; Ctrl+D as a Shortcut on Blizzard's
    death recap toast (`ConsoleUIContainer/HeroDeathStunFrame/DeathRecapButton`) did nothing -
    the toast likely never shows for an observer. Both removed outright; the card follows the
    selection only. Found while testing: holding Ctrl in a player's view brings up Blizzard's
    talent picker (game hotkey QuickHeroTalentTreeSelection = Control) - left to the game, see
    §3 "Blizzard's talent picker".
11. **A non-hero inspect card - built 2026-10-05, awaiting QA.** For minions, mercenaries,
    bosses, buildings: a SHORT card (`inspect_card` SHIFT / H_SHORT: 249 units, 224 px, bottom
    still on the plates) - name, the team's name on the band, health, buffs, stats. No portrait
    (Blizzard's unit picture is 112 x 49, too small to blow up: user's call), fountain,
    abilities (command card parked), talents or resource bar (none of them have one, user).
    - **hero or not:** `hero_check` - the selected unit against the hero units (game data
      plus ALSO's forms), FCJH_IsHero, read by the gate (`card()`); `shape()` moves the card's
      top and the rows, both ways. The first try keyed it to the plates' matchers and some
      heroes got the short card at a match's start for a while (user, 2026-10-05). If a hero
      still shows blank (no portrait or talents) early on, the plates' matchers are slow too.
    - **edge widths:** each side as many units as make 2 px there (`line`); the right side was
      a flat 2 units, 1.8 px, rounded to 1 (user, 2026-10-05).
    - **edge:** every unit's edge is now the team sensor's (`unit_team`): blue, red, or
      `[element.inspect] neutral_colour` (a lighter purple, user) for neither team - it replaced
      the player packs' own edge. Seen 2026-10-05: camp mercenaries purple, a captured
      camp's red or blue as they march down the lane (user).

How the heroic tooltips work: `tools/gen.py`, the comment above `HEROIC_TIPS`.

13. **Camp timer displays: DROPPED** (user, 2026-10-06: no clear place for them on our
    screen). Blizzard's own stay as they are - seen 2026-10-05 as "1:08 / -ELITE- / Boss Camp
    / Player 4" in a stack at the screen's left, mid-height.

## Finished since (2026-10-15 .. 10-16)

5. **The diagnostic - REMOVED (user, 2026-10-15: "Lets remove all diagnostics, including map
   id").** Every map's id was confirmed in game first, so `maps.diag` and `FCJH_DiagMapId`
   are gone. No diagnostics are left in the build.
6. **DONE (2026-10-16): the stray ability card.** Now and then, on hero inspects, the ability
   card stayed on screen after the card hid (user, 2026-10-09). Caught with the gate's state as
   squares on screen: click Sonya's unit, inspect, click Johanna's plate, deselect - the game
   hid our TargetInfoFrame itself while Blizzard's parked one (on the last hero CLICKED, Sonya)
   still read visible, so the gate stayed on Hero and kept the command card on the card's rows.
   Fix: the command card and the talent tips follow OUR card (`inspect_card.card_watch`), the
   gate only shows and shapes it. Seen fixed with a second row of squares for the watcher, then
   both rows removed. Known, accepted: opening the card after that sequence shows the tricked
   hero for under a second before the right one. The gate keeps its Hero/Unit split (not
   merged into the watcher): entering either state re-shows the card, which may be what brings
   it back after the trick. The resource tooltip (item 14) was a separate problem, solved.

- **The resource tooltip names** (inspect card) - SOLVED (user, 2026-10-16, 8ea751d). It was
  never a refresh problem: Blizzard's bar tooltips name the resource by the card's
  TargetInfoFrame (`@UnitVitalName`), which follows the last unit CLICKED in the world, not
  the selection. A plate click selects without retargeting, so the name stayed behind
  (user: Sonya's unit, then Chromie's plate, read "Fury"); clicking units worked. Now our
  own label (`inspect_card.vital`), set per unit from the game data (`vital_words`: the
  actors' VitalNames Energy through their parents, Mana by default), feeds the bars' two
  tooltip formats (`energy_formats`). Seen right on Chromie's plate after Sonya's;
  the diagnostic read Blizzard's name "Fury" and ours "Mana: 371/510".
