# FCJH — the maps

How a battleground's UI works and what each map got, moved out of HANDOFF §7 on 2026-10-16
once the map pass was complete (user, 2026-10-15: "That's all the real maps"). "Item N" means
HANDOFF §7's numbered items (14 is the final pass); the code is `tools/maps.py` (its docstring
says how a map's UI works) and the map entries in `layout.toml`. The standing rules from it are
in HANDOFF §3 ("Banners") and the memory rules.

## The system (built 2026-10-06, the map id 2026-10-09)

8. **Map objectives and the minimap per map - BUILT 2026-10-06, a first pass; the user will
   fine-tune with test maps that cover every map.** All of it is `tools/maps.py`, written by gen
   into `FCJH_Maps.StormLayout` (it replaced the hand-written `FCJH_MapAlerts`; its docstring
   says how a map's UI works). **The user's direction (2026-10-05/06):** centre the objectives
   round the minimap, not on the right edge; a team's alert goes on that team's side (blue left
   of the map, red right), neutral ones stay centred; a team's alert sits at its core bar's spot
   (on the XP bar at the row's inner end, stepping up onto the core bar while that shows); "if
   all alerts fall to the sides of the minimap, and they grow/jump as to not be on top of each
   other, then we're set". **Later (2026-10-06, Cursed Hollow):** no neutral banner at the top
   middle (it sits too high, worse on tall maps) - neutral alerts go in RED's column, right of
   the map, as Towers of Doom's do; red shares the space. The minimap is exempt from the 20 px
   padding rule: a map's team counters may sit on its bottom edge. Every map alert sits
   `[map_alerts] lift` (10 px) higher than its bar, clear of the talent/health pop-ups off the
   plates (superseded by the standard below). **Every banner's art lands in the same place on every map** (Blizzard's banners are
   one art; landing alike is what reads as one, user): across, red's starts where red's row
   does and blue's ends where blue's does (`[hero_row] red_left` / `blue_right`, the plates'
   distance from the map); up, on the shared slots. A banner whose parts hang below its art
   gets edited, not raised (the tribute's countdown, below).
   **The banner standard (user, 2026-10-09)** - `maps.ALERT_ART`, one `Art` per Blizzard banner
   layout (not per map: the NotificationFrameTemplate is Towers', Alterac's and Hanamura's; the
   centre banners are the older maps' and Braxis's): every banner is placed by its BAR, one
   Blizzard bar art. Every bar's bottom sits in ONE place on every map, `[map_alerts]
   above_core` (10 px, user) over the core bar's top - never moving, core bar shown or not (the core
   bar is taller than any pop-up), and ignoring what hangs under the bar: the banners draw over
   the plates' pop-ups (user). Stacked banners are one step apart: the tallest art that can
   stack (one sharing a column, any map) plus `STACK_GAP` (`step`: Towers' 117 + 8 = 125 units;
   user, twice: Blizzard's 30-unit gap left too much dead space, and sizing for the tribute's
   143, alone in its column, spread Towers' pair further). The
   first banner to show keeps its slot (user). Growth runs outward from the plates' inner edge;
   a banner Blizzard lays out from its hexagon end gets re-laid from its inner end, as the red
   curse. Blue's banners are MIRRORED (user): Blizzard draws one banner for both sides, its
   hexagon at the right end - blue's inner end, over blue's core bar - so blue's take
   Blizzard's own NotificationFrameLeftTemplate anchors (`maps.MIRROR`): hexagon outward. The
   blue curse (centre banner, Blizzard's layout) needs the same - unseen yet. Each layout's bar is measured once off a 1080p screenshot (`bar_up`: its bar's bottom
   over the edge its frame is placed by - Towers 20, the tribute 24, Braxis 0); gen prints the
   unmeasured (Hanamura's ICON art). No per-map banner nudge exists.
   **How a map's UI works** (game files): each map's panel is a template built at runtime in
   GameUI's `MapMechanicPanel` - the newer maps' in their own layout file, created by the map's
   script; the older five's (Cursed Hollow, Blackheart's Bay, Haunted Mines, Garden, Dragon
   Shire) in core `MapMechanicPanelTemplate`, on every map, hidden at load and shown by the
   map's script. Scripts find parts by NAME: move and restyle (`file="<map's file>"`), never
   rename or drop. A map's layout file loads only on that map. Blizzard moves its own minimap
   per map that way too (a `MinimapPanel` override in the file: Braxis -35, Battlefield +75,
   Hanamura +80, Warhead 0 and the map 30 right in its panel; 35 elsewhere).
   **The three parts:**
   - **The minimap per map:** each map draws with its bottom on the padding line (1060 at
     1080p, level with the plates' bottom). How tall a map draws: the opaque part of its
     `CustomMiniMap` texture, read from the map archives in Battle.net's cache (the
     battlegrounds aren't in the game's storage; our `mpq.py` reads them), fitted 380 px wide
     (Towers of Doom, measured: ~380 x 252, y 810-1062; the model gives 260 tall). Tall maps
     rise (Haunted Mines 380 px tall, top at 680); wide ones sink (Braxis 224 px). Moved from
     load, no jitter (2026-10-09): a newer map by a placer inside its own panel
     (`maps.placer`); an older map by **Blizzard's map id** (`maps.id_placers`, below) once it has
     `own_place=True` - until then it shares `[minimap] bottom`. `[minimap.nudge]` in
     layout.toml, px per map, for fine-tuning; `[minimap.panel_nudge]` moves only the panel's
     parts (both px, + lowers). The ARAM maps (no panel) keep `[minimap] bottom`.
   - **Each map's panel on our minimap:** every part Blizzard placed from the screen's
     bottom-right corner (where its minimap was) is restated from our minimap's corner, at the
     same distance as it stood from Blizzard's minimap on that map (`maps.on_minimap`). So the
     timers, counters, health bars and neutral banners sit round our minimap as they sat round
     Blizzard's, follow it per map, and the right-edge strips (Alterac, Volskaya, Garden's
     terror bar) stop clipping minimap-placed parts (Volskaya's capture hex). Towers of Doom's
     strip stays put (all it holds that matters is ours; its town health is drawn from the top).
   - **Team alerts:** a generic stack per side (`maps.stack_states`): an alert's slot is how
     many alerts before it in its side's column are showing; the bottom slot is the XP bar, or
     the core bar while that shows; 147 units a slot. Towers of Doom (now through it: Raven no
     longer lands on the tunnels) and Hanamura's "attacking" pair (one frame per team, to
     everyone - `AttackingCoreFrame_Order` blue, `_Chaos` red; placed by its icon box, art
     412 units, unmeasured). Other maps' alerts are neutral (timers, "spawns in") or blue-left /
     red-right halves of one HUD - checked in the files; none is per team. An alert whose art
     hangs off its frame's top-right (`maps.Alert box=`) is placed by our own spot frame
     (`FCJH_<name>Spot`): the spot takes the stack slot, the frame becomes the art's box on it
     (children draw only inside their parent's box). `followers` ride along on the same spot.
   **To check in game, map by map** (with item 14's test maps): the map's bottom on the padding
   line (nudge it if not), and when it moves (at load, or when its panel first shows - Sky
   Temple's and Tomb's start hidden); the panel's timers and counters above the map, not over the
   plates or the alert stacks; Volskaya's capture hex showing; Warhead's map centred; Hanamura's
   "attacking" alert on the attacking team's side, its art clear of the map; Blackheart's Bay
   placed at all (its panel is shown by its own script - unchecked). Then ARAM keeps the default.
   **Done:** Towers of Doom (2026-10-06; DONE again 2026-10-09 on the banner standard: bars on
   the fixed place with and without the core bar, blue's mirrored, the stack's spacing - user:
   "not likely to adjust them again"); Cursed Hollow (2026-10-06, below; its minimap and counters
   seen right after the no-jitter change); Volskaya Foundry (2026-10-15, under item 4 above).
   **Towers of Doom, as approved (2026-10-06):** altar countdown and towers upgrading on red's
   side, tunnels on blue's (kept balanced, user). "Cannons are firing": the script shows RAVEN's
   alert for blue's capture and NECRO's for red's (only the Your/Enemy text is per viewer), to
   each team's players only - player views show them, hidden 5 s later by our timer. The
   town-capture pair (Allies / The Enemy captured <town>) is viewer-relative, players-only:
   parked; OUR town alerts stand in, in every view - "Blue / Red team captured a town", from the
   observer-only "BroadcastToD<blue>v<red>" events the script sends our plates'
   ObserverHeroOverviewPanel (blue's count up = blue took it; ~1 s late, with the new town's
   spawn). **No free-view cannon alert is possible:** nothing an observer's UI receives marks an
   altar capture. The towns' shot counts show at the minimap's bottom corners.
   **Cursed Hollow, as approved (2026-10-06):** minimap nudged 20 px down, its panel 25 px up
   (`panel_nudge`), so the tribute counters sit on the map's bottom corners. Tribute spawning /
   collect the tribute (neutral, one frame) in red's column. The curse (one `CurseFrame` for
   either team, timer parts anchored to the tribute frame's) goes on the cursed team's side:
   which team, from its text - `maps.cursed_side`, one state per language, matched on the
   LITERAL words (`Text="@Param/Value/..."` never matches). Red's is laid out from its left end
   (our `FCJH_CurseText` label, Blizzard's art had dead space there); blue's keeps Blizzard's
   layout from the right. **Red's curse seen and approved; blue's not seen yet** (no replay with
   it - item 14). The tribute's countdown hung under its hexagon onto the XP bar: it's now in
   the bar after the words, as Towers' "Altars activate in: 0:24" (`maps.tribute_count`) -
   our words per language ("Tribute Spawns In:", `TRIBUTE_SPAWNS_IN`, found by matching
   Blizzard's literal words), from the bar's left end like the red curse's, the count one space
   after them (`TRIBUTE_COUNT_SPACE` -1 units: the labels pad ~8 px, measured), Blizzard's count
   hidden; "Collect the Tribute" (no count then - the script hides it) hidden 2026-10-15 (§7 item 16).
   The curse's countdown the same way (approved 2026-10-06): Blizzard's in the raven head
   hidden, ours after the words (`CURSE_COUNT`; red's flows right from our words, the hexagon
   after it; blue's sits where Blizzard ends the words, they end before it), with a colon
   where that language's Towers "Altars activate in:" has one (`CURSE_COLONS`, its own label;
   Chinese takes "："; blue's "Equipo azul maldito" is both Spanishes', left without). Blue's
   count, like blue's curse, not yet seen (item 14).
   **Map-specific tech - SOLVED 2026-10-09 (the breakthrough).** The older five's panels are
   Blizzard's core ones, on every map, hidden at load - no panel tells them apart, and the
   first one shows at the first objective (the old jitter). **Blizzard's map id does, from
   load:** a `DataRefFrame` reading the script variable `libCore_gv_mAPMapStringID` (Spazzo's
   way), tested with `<When type="Property" frame="..." StringValue="HauntedMines"/>`. Read on
   screen: `HauntedMines`, `BraxisHoldout`. In code:
   - `maps.MAP_IDS` - every map's id and where it's from (read in GAME, Blizzard's SCRIPT, or
     SPAZZO only; every one has now been read in GAME, 2026-10-15).
     Odd ones: Garden `HauntedWoods`, Tomb `Crypts`, Sky Temple `ControlPoints`, Warhead
     `Warhead Junction` (a space).
   - `maps.id_placers` - the reader and each map's state group, at GameUI level: **always
     shown** (the same inside HM's hidden core panel never fired). DefaultState on the
     unconditioned state (memory rule 27).
   - `maps.on_map(key)` - the condition, for any other per-map state.
   - **Converting an older map is one line:** `own_place=True` on its entry; its
     `[minimap.nudge]` then applies (gen refuses one without). Converted: Haunted Mines.
   - Can't: a map-only layout file of our own (ours load everywhere); Galaxy scripts (not
     an interface component, and replays re-simulate them). Newer maps keep their panel
     placers (proven); the map id would work for them too.
   **Haunted Mines - two views (2026-10-09; the launch view and the glide seen working - user: "Glide worked great"):** at load only the
   surface (`launch_cut` -8: the surface's bottom 8 px above the drawn map's middle, the mines'
   top 35 below - measured), its bottom on the padding line (`[minimap.launch_nudge]`), the
   mines under the screen. When the mines first open (the script shows `SkullModeFrame`) the
   minimap glides up over 1 s (`maps.glide`, eased) to the whole map on the line
   (`[minimap.nudge]` 34), and stays: the glide raises `FCJH_Opened`, which stops later openings
   replaying it. The skull counts ride with the minimap; the "Needed" plaque is fixed to the
   screen for the whole-map view. **A relative Anchor controller counts from the frame's LAYOUT
   anchor, not from a state's SetAnchor** - the first glide stopped 125 px high (memory rule
   28); its keys now run launch-minus-shared to place-minus-shared. The same rule made the
   tribute's and the curse's intros fade-only (`maps.FADE_ONLY`): `cursed_side` moves their
   sides, and a paused slide would have held them on red's spot.
   **Braxis Holdout (in QA, 2026-10-09):** the zerg wave banner at the standard place (art
   measured, `HOLDOUT_BOX`); the panel above the map 4 lower (`[minimap.panel_nudge]`). The
   beacon dishes (Blizzard pinned them under its own minimap, off our screen) are re-anchored
   from the screen, not moved with their frame (moving `RadarDishModeFrame` hid them - a frame
   draws only inside its box): at 90% (Width/Height), beside Leoric's and Nova's plates
   (`maps.BEACON_*`, `FCJH_MAP_BEACON_*`; the arrows are in Blizzard's dish art - Top points
   up, Bottom down). The electric line between them (`HoldOutLink1-4`, its own frames) is
   stretched from dish to dish under them (its ends fade, ~17% each), along the map's bottom
   edge, and under the MINIMAP: Braxis's placer sets the whole `MapMechanicPanel` to
   renderPriority 511, under the minimap's default (`Map.fix`; only on Braxis, where the
   placer exists). Line approved by eye (user: "this is the way"); its last 2 px down and the
   rest of Braxis still to check: the minimap from 0:00, nothing else under the map.
   **Lessons for every map:** (1) a right-edge strip clips anything moved out of it: Unclipped,
   or move the strip. (2) Read the script for who each alert is sent to - one can look
   viewer-relative ("Your cannons") and be one frame per TEAM. (3) A player view (1-8) shows
   alerts sent to that player's team; the free observer view doesn't. (4) An alert's art can
   hang off a child, not its frame (Hanamura's icon box): move the child.

## The map pass, map by map (2026-10-09 .. 10-16)

**Next (2026-10-09, end of night; start here).** The map pass: the four working maps and
Dragon Shire are DONE (items 3-4; Dragon Shire's knight on either team's side, blue's mirrored);
Blackheart's Bay DONE 2026-10-12 (chests banner, either team's cannon, the plates' carried
doubloons); Garden of Terror DONE 2026-10-12 (the seed banners, the Terrors on the summoning
team's side; blue's Terrors still unseen). The banner protocols' recheck PASSED on all five
(2026-10-12). Alterac Pass DONE 2026-10-14 (everything below seen and approved in one pass). Hanamura
Temple DONE 2026-10-16 (its split scrapped; THE GAP measured on target).
Tomb, Warhead, Volskaya, Battlefield done 2026-10-15; Infernal Shrines DONE 2026-10-15, blue's
Punisher too 2026-10-18 (user: "works as intended", 23ecda4). Sky Temple DONE 2026-10-15 (eedab7d): every map passed.
Infernal's minimap on the floor with its skull-race lift, 2026-10-15 (082126f).
**The map pass is COMPLETE (user, 2026-10-15: "That's all the real maps").** ARAM maps have no
banners (as the user last checked). Brawls are out of scope: the user intends to ignore them.
What's left is the final every-map pass (item 14) and the other open items.
For each, screenshots of: each banner as it comes up, anything hanging off the
minimap's bottom. Hero test rosters come from the tracker in item 14 ("not seen yet").

**Recheck after the banner protocols (2026-10-12, d2604a6 and after; §3 "Banners"): PASSED (user,
2026-10-12: "all the banner generation on the other maps seem solid", every map before Alterac).
Not recorded: whether a replay showed blue's curse; check it if one does.** What was checked:
- **Mines, shrines, seeds, curse:** the banner holds its width while the count runs, down to single
  digits. A narrow count leaves a wider space before it.
- **Dragon Knight:** both bars are on the standard tip now, red's 3 units (about 3 px) left and
  blue's 2 units out.
- **Curse, red:** 3 units left.
- **Curse, blue:** now the mirror, never seen. The raven is flipped at the outer end with its glow
  around it, the words read toward the tip, and the bar runs from the raven to blue's inner edge.
- **Cannons and Terrors:** unchanged, position for position.

1. **Look in game at what's built but unseen** (build 2026-10-09 evening):
   - **Haunted Mines: DONE (user, 2026-10-09).** The two views and the glide (once only), the
     skull counts' line back (it was clipped under its panel: Unclipped), skulls and counts 2 px
     lower and 4 px in, the "Needed" plaque 28 px in the gap between the maps (the bar art
     stretched whole: a squeezed nine-slice loses its corners), riding with the minimap; centred
     in the gap 2026-10-12 (6 px up, by measure then eye). The
     surface sits ~20 px left of centre in Blizzard's art at launch: left as is (user: it
     lasts two minutes).
   - Cursed Hollow: the tribute and curse banners now FADE in without sliding - check both
     land on their spots every time, the curse on red's side and (if a replay has one) on blue's.
2. **Banners stay put - check on each map in the pass:** every bar's bottom on the one place
   (`[map_alerts] above_core`), the tip on the plates' inner edge, with and without the core
   bar, and the intros (tribute, curse, zerg, mines) not shifting them. By the code they can't
   move with the minimap: all 90 banner anchors and stack moves are to the screen (checked
   2026-10-09). Any banner whose sides a STATE moves must stay fade-only (`maps.FADE_ONLY`).
3. **The four working maps, map by map (map-id tech) - ALL DONE (2026-10-09):**
   - **Haunted Mines** - DONE (above).
   - **Cursed Hollow - DONE (user, 2026-10-09):** id read in game (`CursedHollow`), banners
     correct, the tribute and curse fading in. It's the BASELINE (user): `[minimap] bottom` is
     its place, so it keeps no `own_place`; the other older maps get their own. Changing
     `[minimap] bottom` moves Cursed Hollow and the ARAM maps.
   - **Braxis Holdout - DONE (user, 2026-10-09):** id `BraxisHoldout`; its zerg banner slides
     in (only the tribute and curse are fade-only). Its zerg HUD compacted (maps.py
     BEACON_ICONS / ZERG_WORDS / ON_AIR):
     - the %s centred in their hexagons;
     - the dishes against each hexagon's lower outer edge, 4 px down, anchored to the hexagons
       (BossDuelLeftFrame/BossHudLeft, /BossHudRight), so they follow the HUD;
     - the electric line hidden (Alpha 0), kept as the signal: the script shows blue's pair
       (Link1-2) while BLUE holds both beacons, red's (3-4) while red does. A state on it shows
       "on air" rings in that team's colour over both dishes (FCJH_OnAirBlue/Red): a breathing
       ring on the dish's border and a wave rolling out from it (Storm_UI_GenFX_RingGlow,
       tinted). Tried first and dropped: the line along the map's bottom edge, then a beam from
       each dish into its hexagon (Rotation works: degrees clockwise, about the middle);
     - "BEACON PROGRESS" and the wave's "Enemy Zerg" above the bar, on Blizzard's "Allied
       Zerg" row; the HUD 20 px lower (`[minimap.panel_nudge] braxis_holdout = 24`);
     - its map 18 px down onto the floor (`[minimap.nudge] braxis_holdout = 18`); the mechanics
       panel no longer goes under the minimap.
   - **THE FLOOR, every map (user, 2026-10-09):** no map's visual bottom edge (its art's
     outline, not the texture box or unit icons) may sit lower than Cursed Hollow's: y ~1065
     at 1080p (`[minimap] floor`). Haunted Mines is within it; Braxis sits on it.
   - **Towers of Doom - DONE (user, 2026-10-09):** id `TowersOfDoom` read in game; nothing to
     adjust. Its map's visual bottom ~1066, on the floor; the blue/red line between the bell
     markers sits just under it, on the screen's minimum edge (user: fine as is).
4. **Dragon Shire - DONE (user, 2026-10-09):** id `DragonShire` read in game; its map's bottom
   ~1060, inside the floor, at the shared place (no own_place - nothing to move).
   - The shrines' countdown is the neutral banner on red's side (maps.py SHRINE_*, laid out
     from its left end as the mines'); the Dragon Knight replaces it from the same spot
     (DRAGON_PARTS), its timer up on the name's row, ~12 px before the % (DRAGON_TIMER).
   - The knight on its team's side, like the curse (user, 2026-10-09; blue's confirmed in game):
     blue's on blue's spot, mirrored - head flipped at the outer end, "% timer" from there,
     "DRAGON KNIGHT" at the inner end, its health draining from the right (knight_side). Told
     by blue's moon and star both still lit: the script stops setting them once the knight is
     up, and the markers' hidden panel doesn't stop a When reading them. Red's knight after a
     blue one went back to red's layout, draining as before (user, 2026-10-09). Blue's backing
     flipped (our copy, TextureCoords); its fill can't be - a status bar ignores TextureCoords -
     so it's widened and cut to the mirrored lean by a mask of ours (knight_mask), its outer end
     overshooting the backing as red's does (Blizzard's own). DONE (user, 2026-10-09).
   - The shrine markers (moon, star) up from off the screen, their team line level with Towers'
     at ~1070 (`[minimap.panel_nudge] dragon_shire = -29`); the stars clear the map's flanks.
   **Blackheart's Bay - DONE (user, 2026-10-12):** id `BlackheartsBay` read in game; its map's
   bottom tab ~1056, inside the floor, at the shared place.
   - The doubloon counts' team line up to ~1070, level with Towers' (`[minimap.panel_nudge]
     blackhearts_bay = -30`; they'd been cut off by the screen's edge).
   - "Chests have spawned" is the neutral banner on red's side (maps.py CHEST_*), with the full
     intro: its bar is a nine-slice from the frame's left, as the cannon's, so the bar grow has
     a left end to move (Blizzard's is a fixed-width image anchored at its right only - nothing
     grew, 2026-10-12).
   - The cannon on the firing team's side (cannon_side, told by Team1ShotCounter's Visible):
     red's Blizzard's layout, blue's mirrored - our flipped cannon at the outer end, the pips
     running right from it, our copy of the words and count. Fade-only (FADE_ONLY).
   - The plates' carried box shows the doubloons (item 7's note; gen.py `carry_box`).
   **Garden of Terror: DONE (user, 2026-10-12).** Its id `HauntedWoods` read in game.
   - The seed counts' team line 29 up (`[minimap.panel_nudge] garden_of_terror = -29`).
   - "Seed spawning in" and "Gather the seed!" (hidden 2026-10-15, §7 item 16) are neutral banners on red's side (`seed_banner`
     on `left_banner`; they're templates of the map's own file, so they're overridden through
     PARTS and hang off our spot). They restate their box's size: the template's 600 x 140 was
     centred on the box.
   - The Terrors' health is on the summoning team's side (`team_banner`, told by its ACTIVE seed
     count): blue's is Blizzard's way round, red's the mirror. **Blue's not seen yet** - blue never
     summoned in the test replay; look next time.
   **Alterac Pass: DONE, every item closed (user, 2026-10-14: "That looks great!", then on the
   clean build 0c07030: "Everything can be marked off for alterac").** Its id `AlteracPass` read in game. One Blizzard
   frame (`AVMechanicContainer`) shows the prisoners countdown, then the cage fight, then the
   cavalry's health. Measured at Blizzard's place (all four modes seen there, both teams' cavalry).
   - It hangs off a carrier of ours (`maps.av_carrier`). The first build (caa5687) put the
     prisoners and cage on red's spot and the cavalry on its team's; seen in game, all four landed
     (tips 1167 / 755, brackets 930), and the carrier move worked both ways.
   - **Redone (user, 2026-10-12, having watched it a few times): the prisoners and the cage stay
     above the minimap, at Blizzard's place; once the cage is won its outro plays there and the
     cavalry appears on its team's side.** The carrier sits at Blizzard's place; on `TeamWins`
     1 or 2 it jumps to that team's spot 0.6 s on (`AV_HANDOFF_S`: Blizzard's cage bars are
     gone and the cavalry plate shows then), by a relative Anchor controller with gen.py's
     `FCJH_MAP_AV_<TEAM>_DX/_DY`; `TeamWins` 0 resets it. Checked:
     - the cage's outro above the minimap, then the cavalry on the winner's side. If it jumps
       before the outro, `TeamWins` is set before "MechanicDone" and the delay needs raising;
     - the next prisoners back above the minimap (if not, `TeamWins` doesn't return to 0);
     - the hexagon jumps with it at 0.6 s (a cut, not a slide).
     **Seen (user, 2026-10-13):** the outro above the minimap and then the jump "looks like a
     staggered movement; not quite polished", and when blue's cavalry died the slain banner went
     back above the minimap (the script resets `TeamWins` and sends "Hide" 5 s after
     "CavalrySlain"). Now (`maps.av_parkers`): the banner is parked off-screen from the win until
     it lands on the winner's spot at 0.6 s, and from "CavalrySlain" until the next round's
     "Show": no outro above the minimap and no slain line. Seen (2026-10-14).
   - **Both teams capturing lit only one half of the cage's hexagon** (Blizzard's, seen in Ahli's
     too; user, 2026-10-13): it lights "who's winning", whoever channelled first. Now
     (`maps.av_both_lit`): with both bars capturing (`TopBarCaptured` and `BottomBarCaptured` "10"
     or "11"), our copies of both lit halves and glows draw over Blizzard's darkened half. Seen (2026-10-14).
     If a copy shows outside a capture (after the win, say), the bars' states outlive it.
   - The neutral banner sat 10 px lower (user, 2026-10-13); since 2026-10-14 it's placed by THE
     GAP (Hanamura below; `maps.py above`) - 10 px back up. Seen on target (2026-10-16, "PRISONERS
     LOCATED IN"): the hexagon's bottom ~10 px over the map's tip at 1080p. The cavalry's jump
     allows for it (gen.py), so only the neutral moves.
   - **The cage bars broke (user, 2026-10-13, against the default UI):** in Blizzard's, the fill
     and its timer move while the team-coloured backing stands the bar's length; in ours the
     backing slid along with the fill. Cause: `Unclipped` on the frame (to draw past its panel on
     red's spot) took the clipping from inside it. Fixed: no `Unclipped`. Instead the panel strip
     is widened (`AV_PANEL_GROW` right, 200 left), and the carrier and flag alerts are placed back
     from its new right. The cavalry's plate and fill-up slide in under masks too: check
     they don't show outside the bar.
   - **Then the bars drew cut short (user, 2026-10-13):** no timers, no red stub, the fill's end
     off. A diagnostic (coloured strips spanning each frame on the bars' chain) showed the bars'
     strip (`ProgressBarsContainer`) 891 units wide: Blizzard anchors its Left and Right to two
     different points (art Mid -210, +218) with Width 463, and ours resolved each side as its
     anchor -/+ half the width, so the bars started far left under the mask. Fixed
     (`maps.av_bars`): both sides on one point, Mid +4, which centres 463 on Blizzard's span.
     **Seen and approved** (user: "looks good"), matching the default UI at the same times.
     Lesson: a Width with Left and Right on DIFFERENT points isn't centred between them.
   - **Technical limitation (user, 2026-10-12: "not the end of the world"): not mirrored.**
     Blizzard's animations slide its parts: the hexagon 373 left when the cage starts, the cage
     bars and the cavalry's fill-up in from the left. Each slide counts from its layout anchor, so
     no state can mirror them. Blue's cavalry is Blizzard's way round, which is blue's mirror; red's
     keeps the hexagon at the inner end. Accepted as is (user, 2026-10-14: everything marked off).
     If it's ever wanted: restate those animations for red and flip the cage's `ProgressBar`s
     (the `$this` anchor trick, untested - no Blizzard bar fills right to left).
   - **The camp alerts (`NotificationFrame1`/`2`) go to the side their event names (user,
     2026-10-13):** Alliance's (EventID 11/12) on blue's, Horde's (21/22) on red's, on that side's
     stack - a slot up for the cavalry there, and alert 2 a slot up for alert 1 there. Each hangs
     off a carrier of ours (`maps.camp_slot`, states keyed on its EventID) so Blizzard's intro
     still slides. Art kind `CAMP` measured off the default UI (`ALERT_ART`). Seen (2026-10-14). Technical
     limitation: not mirrored on blue's side (one frame serves both teams; the intro's relative
     slide would undo a state's mirror), so blue's hexagon is at its inner end.
     Earlier they were pinned where Blizzard's banner sits between rounds (seen stacking over it).
     **Seen in the default UI's everyone view (user, 2026-10-13):** they
     are for observers and they stack. Their words are blue's player's ("Allies capturing enemy
     camp" = blue capturing). Ours name the side (user): "Alliance capturing Horde camp", "Horde
     retook their camp" and so on (`maps.camp_words`). The team comes from the alert's EventID; the
     English words only gate the kind and the language. The placement was seen working
     (2026-10-14), the words weren't: the first build drew a label of ours over Blizzard's, hidden
     by Visible - ours drew nothing (its Style bound to Blizzard's label's) and Blizzard's stayed
     up. Now the side names are written into Blizzard's own label (its EventID states already
     colour it); once written the words stop matching, so nothing loops. Nothing added to the
     alerts' template (`AVNotificationFrameTemplate`) reached them, so the states sit on each
     alert (`NotificationFrame1`/`2`). Written into Blizzard's label it worked, then reverted on
     a later alert (the script rewrites the label; a state already entered doesn't act again).
     Now Blizzard's label is hidden for good and ours, in its style, takes the words by the event
     alone (any language gets ours in English); until a state runs it mirrors Blizzard's words
     (after a replay seek one alert showed no state had run). CONFIRMED (user, 2026-10-14): both
     teams' words, several rounds, after a fast-forward to 8:37; the diagnostic line is gone.
     The cavalry-slain line ("All Allied/Enemy Cavalry Slain", in the banner itself) had the same
     player's wording, but it never shows now: the banner is parked from "CavalrySlain" (above).
   **Hanamura Temple: DONE (user, 2026-10-16; "for today, it's good to go" 2026-10-14).** id `Hanamura` read in game (Spazzo's, as
   guessed). Its map's bottom was ~1047, 18 px above the floor: now 18 px down onto it
   (`[minimap.nudge]`, user 2026-10-14: "Minimap looks good").
   **No per-side alerts here (user, 2026-10-14):** the countdown ("Payload spawns in"), the
   payload's push status and the shots ("Shots remaining") take turns in one place above the
   minimap and animate as one, so all three stay Blizzard's, there. Tried and dropped: the
   countdown on red's side and the shots on their team's - blue's shots came out clipped (the
   intro slides the icon 198 right, past the frame's edge). "CONTESTED!" above the hexagon
   instead of under it (the escort counts there are hidden while contested): seen and approved
   (user: "Contested looks good"), and blue's shots ("shots remaining looks good").
   **The objective never moved:** a 26 px panel nudge did nothing (the hexagon stayed at ~798,
   which I misread as moved), and the minimap's 18 px move left it behind (user: "you didn't
   bring the alert with you"). Its frames hang off each panel's MinimapProxyFrame, which
   Blizzard ties to the minimap by `$parent/$parent/$parent` - and that never followed. Now tied
   by the full path (`maps.proxy_lines`, `proxy=True`), as everything that does follow is.
   **THE GAP (user, 2026-10-14: "standardize that gap between maps"):** every neutral objective
   above the minimap sits `[minimap] alert_gap` (10 px) over the drawn map's top tip, measured
   from its HEXAGON's bottom - what hangs under it (labels, timers, numbers) goes either side of
   the tip, and those are moving above the alerts anyway (user, 2026-10-15). Each such
   map has a measure (`maps.py above`: px over the tip, at a known panel move); gen.py's
   `panel_nudges` moves its panels to the gap. Alterac: measured 0 at 10 down (its cage's
   hexagon on the tip), so it goes back up 10 (unseen). Hanamura: ESTIMATED from the template
   (35 over at 0), so 25 down - measure it from the next screen and fix `above`. Every newer
   map left gets a measure (and `proxy` if its frames hang off the proxy) in its QA.
   Red's shots never fired in the test replay. A spawn's flick (neutral, blue +1, neutral) was
   seen in the default UI too; most likely Cassia at the payload's edge as it spawned (user,
   2026-10-14) - left as is. If it recurs with no one near, suspect the validator's state left
   from the previous payload (hide the status ~0.25 s after it shows).
   The split into per-side parts is scrapped (user, 2026-10-16): revisit only if someone
   complains. THE GAP measured off the countdown's hexagon (2026-10-16): ~9 px, on target.
   Roster played (user, 2026-10-14): blue Azmodan, Cassia, Lunara, Tassadar, Yrel; red Medivh,
   Deathwing, Abathur, Samuro, D.Va.
   **Tomb of the Spider Queen (done, user 2026-10-15: "I think that's that"):** id `Crypts`
   read in game. The gem counts (`CryptPanel`, hung off the minimap's bottom, no proxy) at
   ~1030, as Garden's. The minimap 29 down (40 cut off its bottom marker - a building's, ~1036
   at 0; the floor now counts the map's own markers). The Webweavers' banner (`SoulEaterFrame`,
   one frame for both teams, neutral) and the egg timer (`SoulCageCooldownFrame`, shown after
   the Webweavers die) at THE GAP over the minimap, as maps.py `gap_parts` (a part placed on its
   own, its panel kept to its nudge). Its art is drawn ~21 px left of its square's centre: the
   minimap 18 px right (maps.py `across`, its panels taken back - only the map moves); 21 since
   the centering pass (2026-10-19, below).
   The Webweavers' hexagons (user's plan A): Blizzard's own set per team
   (`SoulEaterModeBlueFrame` / `RedFrame`, the summoner's shown) on that team's side, in the dead
   space between the drawn minimap and the plates - from the gem counts' line (1071) up the
   minimap's height, each 40 px further out, centred between the minimap's side and the plates'
   edge then 10 px out (maps.py WEAVER_*, gen.py places them). Seen on fb854f0, both teams
   (red's centres 1109 / 1149 / 1189, blue's 805 / 765 / 725). Their health image must stay
   clipped: the script drains it by shrinking its frame (Unclipped there kept it full; fixed in
   6c52e5e, drain seen). Clicking them can't pan the camera (no click events in the script, no
   unit behind them; the user let it go).
   **Warhead Junction (done, user 2026-10-15: "I think that's all for this map"):** id
   `Warhead Junction` (with the space) read in game. Drawn centred (no `across`); its outline's
   tip, its lowest part, 1043 -> the floor: [minimap.nudge] 22, seen at 1065 (1b0dea6). The nuke
   counters (`SC2Panel/Team1TerrazineFrame` blue, `Team2` red - hung off the minimap's bottom
   either side of its tip, cut off at the screen's bottom at Blizzard's place) 50 px out and up
   (maps.warhead_counters): seen clear of the map, icons ~815-870 / ~1040-1100 down to ~1062;
   then 2 more up (cd1e81b) for their team strips, uncovered by the lift, to end on the floor -
   seen (2026-10-16): both strips 1063-1065, on the floor. Then turned round as Tomb's (user,
   2026-10-16): icon outer, count inner, the strips meeting at the centre (out 0 - under the
   map's tip at the floor; "build it first, and raise later if need"), and hidden (alpha 0) until
   warheads first spawn, shown for good after: a sensor in the banner's "N LEFT" label (shown
   only while warheads are out; started hidden, as Blizzard's is visible until the first
   countdown) plays a never-reversed fade on both (maps.nuke_sensor). Seen (2026-10-16, 18f4cbb):
   hidden at the start and through the first countdown, up at "N LEFT"; strips ~814-1103 at
   1063-1065, meeting at the map's tip (~955); icons ~828-880 / ~1028-1078, counts ~895-917 /
   ~992-1005. Later waves seen too: they stayed up, no blink (user, 2026-10-16, three waves). Icon
   and count too close to the map (user): both moved out (WARHEAD_MARKS_OUT_PX), strips left
   meeting - 15 px seen (7236174), "a bit more" (user); 30 px seen (bca6517): "perfect" (user, 2026-10-16).
   The warheads' banner (`TerrazineEruptionFrame`: the countdown, then how many are left)
   moved as Blizzard draws it to red's bottom slot - a neutral banner, no copied words (user);
   its box is the English countdown's, so the other text's tip lands off red's plates by its
   length (1b0dea6). Seen, both texts (2026-10-16): "WARHEADS DEPLOYED IN: 0:27" tip at x 1166,
   "WARHEADS AVAILABLE: 3 LEFT" at 1171 - both just off red's plates (~1175) - its words ~15 px
   clear of the hexagon, its bar ending ~37 px over the XP bar (966). Its other SC2Panel parts
   (NukeSiloFrame, NukeSiloFrame2, TerrazineBuffFrame) never show, in any view: the map's
   script (`libmsc2.galaxy`) hides them for everyone at setup and nothing ever shows them -
   leftovers. Nothing left on Warhead.
   **The minimap's tooltip - OFF, every map (user, 2026-10-15: "Just hide it or disable it";
   seen gone on 08eeb21).** Hovering a named minimap icon (a watch tower, a fort, Tomb's Spider
   Altar) showed Blizzard's `MinimapPanel/MinimapPanelTooltip` at ~1332-1467 x, ~800-850 y,
   stranded by its `$parent` anchors when we move the panel. Not stoppable at the source (no
   tooltip frame named: the name showed anyway, clamped elsewhere; the minimap with tooltip
   hover off: no change); the box is see-through instead (FCJH_Minimap.StormLayout).
   **Volskaya Foundry - DONE (user, 2026-10-15: "perfect. mark it done!").** Id `Volskaya`
   read in game; minimap 7 down to the floor (a1f60ca). The toast (`VolskayaToastContainer`,
   maps.TOAST): our banners' font, a sentence before its count while counting
   (VOLSKAYA_UNLOCKS_IN, every language), the bar out to the sentence and centred on the screen
   in every language (6ff536a: the bar's right end hangs from the Mid of a hidden copy of the
   words shown, anchored by its Left only - half their width out). CONTESTED over the capture
   hex, hidden in overtime from the robot's frame (a `<When>` naming a script-built frame built
   AFTER the watcher never fires; the script builds capture panel, toast, overtime, robot in that
   order). The robot (`VolskayaRobotHealthSlideout`) a team banner (maps.robot_layout): blue's
   fill its own bar copy (FCJH_BlueHealthBar - the progress bar mirrors only its mask layer),
   the timer over the %, pilot and gunner beside the robot (THE GAP). Its outro is Blizzard's
   own animation, the same in default - left alone. SetAnchor relative="$this" doesn't take:
   name frames by path.
   **Battlefield of Eternity - done (2026-10-15, bot game).** Id `BattlefieldOfEternity` read in
   game (9f4d45f). Minimap 16 down to the floor (60558ea). `BossDuelPanel`'s three phases are
   three sibling frames, one shown at a time, so they're split up as Dragon Shire's (user,
   e5c7c9c): the countdown ("Immortals spawning", BossSpawnFrame) is the neutral banner in red's
   column (`SPAWN_BANNER`, left_banner; seen 14_28_58, 14_48_59); the fight
   (BossDuelLeft/RightFrame, Braxis's zerg template) stays above the minimap, "IMMORTALS
   FIGHTING" above its bars as Braxis's, the panel 9 right (Blizzard draws its boxes 8 px left
   of centre), THE GAP from its portraits' hexagons with the numbers either side of the map's
   tip (`above=(32, 0)`; seen centred, ~11 px, 14_49_06); the winner's Immortal pushing
   (BossLaningFrame) goes in the countdown's place on its team's side, mirrored on blue's
   (`lane_side`, team_banner; blue told by its label's text, `BLUE_IMMORTAL`, 24 strings; seen
   both teams, 14_39_52, 14_44_56, 14_49_19, 14_49_45). Blue's words are our own label
   (`FCJH_LaneWords`) bound to Blizzard's text: the script restyles Blizzard's label as it
   writes it, beating a state's Style, so it stayed left-justified (14_38_47).
   **Infernal Shrines - DONE but for blue's Punisher (user, 2026-10-15: "Infernal looks great.
   Mark it done except for the blue mortar"; 54eaed2).** First build 61f1be5 (map id `Shrines`
   read in game), from
   Blizzard's panel as seen (20_52_34 - 20_53_22: everything in one place above the minimap,
   the minimap 11 short of THE FLOOR, the skulls at ~1050):
   - The minimap 11 down (`[minimap.nudge]`), its notch 1054 -> 1065.
   - The skull race 30 up (`[minimap.panel_nudge]`, ShrinesPanel) - its counts' tops ~1050 ->
     ~1031, the crystal riding with them over the map's bottom.
   - "Shrine activates in" and "Shrine active" as one neutral banner on red's side
     (`WARNING_BANNER`, `ACTIVE_BANNER` - `left_banner`, `INFERNAL_BOX`; the active banner a
     follower on the warning's spot - since hidden, below). Blizzard's count sat on the map under its words; ours is
     in the bar after the words, in their style, as the tribute's (`left_banner` gained
     `count_style` and `bar`).
   - The Punisher a team banner (`punisher_side`, team_banner; blue told by any `Punisher*Ally`
     icon being shown, libmshe.galaxy ~372-401), mirrored on blue's: the icons flipped to the
     outer end, the backing a flipped stretched copy (`FCJH_PunisherBarBG` - Blizzard's is a
     NineSlice, which a flip can't use), the fill masked and drained from the right as the
     knight's, the % at the outer end. Hud placed from 20_53_22 (`PUNISHER_HUD`, `_TOP` -86).
   Seen on 61f1be5 (21_28_14 - 21_29_45): the countdown with its count in the bar, red's
   Punisher, the skull race and crystal - all right. "Shrine active" barely showed and
   flickered: hidden (user: "lets avoid activating 'shrine is active' banner" - the objective
   markers say it; e48326a). The countdown ends without an outro, as Blizzard's (user: fine).
   Seen on 54eaed2: no flicker between the countdown and the skull race. Blue's
   Punisher - the bots never got one - seen in a human replay and DONE (user, 2026-10-18: "works
   as intended", 23ecda4). Player views (1-8) show the
   Punisher by the viewer's team (the script shows the viewer's team as Ally) - expected, logged.
   **On THE FLOOR, lifting for the skull race (user, 2026-10-15: "Houston, we have lift" /
   "And touchdown"; 082126f).** The skull race's counts and crystal cover the minimap's bottom
   (21_39_22, 21_39_31). It was the floor's one exception for a while: the map 50 px up all game
   (5099bf4). Now the minimap sits on THE FLOOR (`[minimap.nudge]` 11) and glides 50 px up
   (`[minimap.lift]`) only while the race shows, then back down for the Punisher (`maps.lift`,
   the `lifts` field). The race is pinned to the screen where the lifted panel hung it, so it
   doesn't ride the map (all four sides overridden: overriding only Blizzard's bottom drew
   nothing, fbebed4). The glide is triggered by `lift_sensor`, a frame inside the race watching
   `$parent`'s Visible. Watched by name from the placer, which comes before the race in the
   panel, it never fired (135435c; layout rule 34). Seen in game: the race at 3:00 on Normal,
   the lift (22_48_56), and the settle with red's Punisher (22_49_26). The second race lifted and
   settled too (user: "the second one works too").
   Earlier tries: moving the race above the map was declined. The crystal at 85% by a Dimension
   animation (75ecc91, 578f83d) wasn't convincing and was reverted.
   Sky Temple's id `ControlPoints` read in game (user, 2026-10-15) - every id now GAME.
   **Sky Temple DONE (user, 2026-10-15: "no flicker ... Sky Temple is done"; eedab7d).** The
   countdown is the neutral banner on red's side (`temple_banner`; Blizzard's centre-screen
   banner), its bar on the shared 930 line (`TEMPLE_BOX`'s bottom 98: the hexagon image's top is
   clear above its art, so 69 had put it 26 px low). "Capture the Temples" hidden (item 16).
   The three discs moved off the minimap's bottom half to THE GAP above it, centred on the tip,
   on a CenterBar backing (`PARTS["sky_temple"]`); the minimap up 22 to THE FLOOR. Only what
   matters shows: the row and bar only while the countdown frame is up (countdown and live),
   each disc only while it carries the time (next) or is lit (live) - hidden in its own slot,
   so the left is always the top temple. No flicker going live (the script lights all three
   and greys the dead ones in one pass). Seen: between rounds, two next, one next, live.
   Any map could get a two-view or other per-map behaviour the same way (`launch_cut`/`opens`, `on_map`).

## The centering pass (2026-10-19)

Every map centred on our UI's midpoint (959 px at 1080p: halfway between the rows' inner
chrome edges, not the screen's 960), by its two core swirls' outer outline: one per team,
placed symmetrically, the map's ends on most. Measured by pixel rows through each swirl's
middle (the camera box's border reads as a dark line too). Each map's `across` (maps.py, px
right; its panels taken back, only the map moves):

| map | swirls' outline | centre | `across` |
|---|---|---|---|
| Alterac Pass | 782 / 1152 | 967 | -8 |
| Battlefield of Eternity | 775 / 1144 | 959.5 | 0 |
| Blackheart's Bay | 774 / 1144 | 959 | 0 |
| Braxis Holdout | ~770 / 1138 | 954 | 5 |
| Cursed Hollow | 765 / 1130 | 947.5 | 11 |
| Dragon Shire | 776 / 1142 | 959 | 0 |
| Garden of Terror | 765 / 1152 | 958.5 | 0 |
| Hanamura Temple | 777 / 1142 | 959.5 | 0 |
| Haunted Mines (top level) | 789 / 1087 | 938 | 21 |
| Infernal Shrines | 772 / 1148 | 960 | -1 |
| Sky Temple | 771 / 1159 | 965 | -6 |
| Tomb of the Spider Queen (at 18) | 797 / 1115 | 956 | 21 |
| Towers of Doom | 769 / 1153 | 961 | -2 |
| Volskaya Foundry | 777 / 1143 | 960 | -1 |
| Warhead Junction | 778 / 1130 | 954 | 5 |

Haunted Mines is centred by its top level (user); its mines below drew at ~961, now ~982.
Garden's seed counts' plants overlap the map's bottom corners; its swirls sit above them.

The confirm pass (user's roster, shots 15_27_51 .. 15_40_04): every map centred on 959 but
Cursed Hollow (946.5: unmoved - an older map at the shared place, only its panels were taken
back; now placed by its id, `own_place`, [minimap.nudge] 20 keeping its height; an assert
stops `across` on a map that doesn't move). On or above the floor but Sky Temple (~1071.5:
nudge -22 -> -29). THE GAP ~10-11 on Alterac, BoE, Tomb; Hanamura ~8, Sky Temple ~8 off the
bars (agreed); Volskaya ~17 off the hexagon's silver rim, ~10 off its dark band (question for
the user). Markers mirrored about 959 on every map but Cursed Hollow: Blizzard's two tribute
counts aren't mirrored, red's count sat over the map's lower-right corner - both counts 4.5 px
out, red's raven and count on blue's mirror (maps.tribute_extra). Plates equidistant. Tomb's
Webweavers on the plates' slant (0.54; they leaned 0.67). The carry box (Bay, Tomb) runs on
from the fountain's sides again: 15 units out over its step (CARRY_LEAN), as approved - the
0.54 plates (cffee7f) had put it a unit further, "no longer a smooth angle" (user).
