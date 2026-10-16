# Polish research - notes for the user (2026-10-16)

This is research only: nothing has been built or changed. It covers your first-pass polish list,
which is in HANDOFF item 7. Each item has five parts:
- what Blizzard does in the player view;
- what Ahli does;
- what I'd do;
- what needs testing in game;
- the questions for you.

The questions are collected at the bottom.

## The short version

| # | Item | Can we? | Size | Risk |
|---|------|---------|------|------|
| 1 | Timers flash white under 5 s | Yes: Blizzard's own animation, copied | Tiny | One unknown (see item 1) |
| 2 | Skull, then countdown | Yes: Blizzard's own art and timings | Small | Low |
| 3 | Split plates (Misha, Vikings) | Very likely: Blizzard's top bar already has the split pictures | Medium | One unknown (the pictures) |
| 4 | 3 px metallic frame round each row | Yes: drawn like the top backplate's chrome rim | Small to medium | Low |
| 5 | Intro animation for OBS | Yes: Ahli has one | Small | Needs your OBS plan |
| 6 | "Closer to the player's top bar" | Items 1-3 are most of it; a few extras listed | - | - |

**What I'd build first:** items 1 and 2 together, as one test build, since both are about death. Then item 3.

**The key finding behind all of this:** the player's top bar is still there in an observer game.
- It is Blizzard's `PartyFramePanel`, hidden, and the game keeps updating it.
- Our plates already read the Viking timers and the heroic from it, and Ahli reads it too.
- So whatever it knows, we can mirror: per-unit timers, the split pictures, the "almost respawned" signal.

---

## 1. Death timers flash white under 5 s

**Blizzard (player view).** It's all in the layout, not in code (`partyframe.stormlayout`, `HeroDeathTimeLabel` ~line 1997).
- The game sends the hero's cell a `HeroAlmostRespawned` event at 5 s left, and `HeroRespawned` when the hero is back.
- An animation on the timer listens for those events. It swaps the label between two Blizzard font styles every half second for 5 s:
  - `Storm_TopBar_DeathTimer`: the red we already use;
  - `Storm_TopBar_DeathTimer_Respawn`: a pale yellow-white.
- A glow (`HUD_TopBar_Team_HeroFrame_RespawnFrame`) pulses over the plate at the same time.
- Each Viking and Misha has its own timer with its own events: `...Hero1/2/3`, `...Pet`.

**Ahli / Spazzo:** neither has this. It would be ours.

**What I'd do:**
- Put Blizzard's animation on our timer as it is.
- Our main timer already uses `Storm_TopBar_DeathTimer`, so the swap drops straight in.
- Listen for the events on the hidden party cell (or our own cell, whichever gets them).
- We already listen to another panel's events on the maps (`maps.py`, the town splits), so that part is proven.
- Add the glow pulse too if you like it.

**What needs testing:** does the game send `HeroAlmostRespawned` to the party cells when they're hidden, or to the observer cells? The test build would listen to both and show a square for each, so one death tells us which works.

## 2. Ahli's skull, then the countdown

**Blizzard (player view).** `HeroDeathAnimFrameTemplate` (~line 975), 1.1 s long, plays on death:
- a skull icon (`HUD_TopBar_Team_HeroFrame_DeathIcon`);
- a burst frame that snaps in toward the plate and settles (`..._DeathFrame`);
- a dark overlay (`..._DeathOverlay`).

The portrait goes to Blizzard's dead tint ("Colorize", 70% opacity); ours already darkens.

**Ahli.** His version keys off the timer appearing:
- the skull fades in by 0.35 s while growing from nothing to full size;
- it keeps growing to double size as it fades out by 1.1 s;
- the countdown fades in from 0.7 s to 1.2 s, so the skull hands over to the number.

**What I'd do:**
- Use Blizzard's skull art and the player view's timings, since the player view is the look you're after.
- Use Ahli's handover: the number arrives as the skull leaves.
- Trigger it from our own timer appearing. That's proven: Ahli does it, and it fires on our cell.
- Vikings and Misha would get a smaller skull on their own part (Blizzard has `_Sm` and `_Xs` versions of the art). That waits on item 3.

**What needs testing:** only that it looks right. It's low risk.

## 3. Split plates for Rexxar and Misha, and the Lost Vikings

**Blizzard (player view).** The hidden top bar's cell has three portrait images (~line 1789-1995):
- `HeroPortraitImage`, `2` and `3`;
- the game shows `2` and `3` only for multi-unit heroes, and gives each its own picture;
- separators (`HUD_TopBar_Team_HeroFrame_Separator`) draw between the parts;
- each part darkens on its own unit's death, keyed off that unit's own timer label;
- each part has its own click area (`..._Mask_Multi_Left_A/B/C`, `_Petowner`).

**Where each timer sits in Blizzard's cell:**
- Misha's (`HeroDeathTimePetLabel`): on the right half of the plate, centred on her part;
- the Vikings': Olaf on the left, Baleog in the middle, Erik on the right.

**What I'd do:**
- Give our plate up to three portrait parts, each cut by its own mask (we already cut ours with generated masks).
- Copy each part's picture from the hidden cell, e.g. `Texture = {...PartyFramePanel/.../HeroOverview3/HeroPortraitImage2/@Texture}`.
  - We already do this for Abathur's clone portrait, inside our own cell.
  - Ahli copies hero icons from another panel the same way.
- Mirror which parts show from the hidden cell, using Blizzard's own check (is `HeroPortraitImage2` showing?).
- Each part darkens on its own unit's timer.
- Misha's timer comes back, centred on her part. It was dropped 2026-09-30 only because she had no part of her own to sit on.

**What needs testing:** what pictures the hidden cell actually holds for Misha and for each Viking. A diagnostic build would show the copied pictures raw on the plate, one Rexxar game and one Vikings game.

**Not likely:** clicking a part to select that unit. The observer plate has one click target, and Blizzard's per-part click areas live in the hidden top bar. I can test it, but I wouldn't promise it.

## 4. A 3 px metallic frame round each team's row

**Blizzard.** The player view has a tray behind each row (`HUD_TopBar_Team_Backing_Left/Right`, a stretched nine-slice). It isn't a slanted metal frame, so it doesn't fit our plates.

**What I'd do:**
- Draw the frame the way our top backplate's chrome rim is drawn: the same four chrome colours and the same anti-aliasing (`[top_backplate] rim`).
- It follows the row's slanted outline, one texture per team.
- Rows of 1-4 heroes would get their own versions, as the XP bar has.
- The numbers would live in `layout.toml`: width 3 px, the colours, and which pieces it wraps.

**What needs testing:** that it covers the gaps and overflows between plates without hiding the edges of the pop-ups or the heroic.

## 5. An intro animation for OBS

**Ahli.** Each team's plates slide out and fade in. His trigger is the first plate appearing, at the game's start.

**What I'd do:** wait for your OBS plan. The trigger is the real question:
- a **hotkey** the operator presses when OBS's intro plays: easiest to time with OBS;
- or the game's start (like Ahli's);
- or both.

Either can drive a slide and fade on every piece: the plates, the bars, the top bar, the minimap cluster.

## 6. "Closer to the player's top bar": what else the player view has

Beyond items 1-3, the player's cell also animates:
- **Hearthstone:** a frame glow while channelling, and a fizzle if it's cancelled (`HearthstoneStart` / `Fizzle` / `Complete` events, per Viking too);
- **Auriel's revive:** `AurielReviveHero1/2/3`;
- **"On fire":** a Blizzard cutscene effect over the portrait (`OnFireCutsceneFrame`);
- **the respawn pulse** from item 1.

All of them are driven by events from the game to that hidden cell, so they would each need the same test as item 1 first. Once that test passes, they're cheap.

## Questions for you

1. **Skull:** Blizzard's art and timings with Ahli's handover to the number (my pick)? Or Ahli's grow-and-fade?
2. **The flash:** the text flash alone, or Blizzard's glow pulse over the plate too?
3. **The frame:** round the plates only, or the XP and core bars too? And a thin line between each hero as well, or just the outline?
4. **Intro:** a hotkey, the game start, or both? Which pieces move?
5. **Extras:** do the hearthstone glow, Auriel's revive and "on fire" sound worth having on the plates?
6. **Go-ahead:** shall I make the first test build (items 1 and 2, plus the squares that show which events arrive) when you're back at the desk?

## Where things are (for me)

- **Blizzard's player view:** `references/JamiePhan/mods/core.stormmod/base.stormdata/ui/layout/ui/partyframe.stormlayout`:
  - the cell: `HeroOverviewTemplate` ~1760, mirrored `_R` ~2448;
  - the skull: `HeroDeathAnimFrameTemplate` 975 (`Small` 1156, `XSmall` 1337);
  - the row: `PartyFrameOverview` 4087.
- **Font styles:** `fontstyles.stormstyle` 1820-1823.
- **Ahli:**
  - the skull: `_TopPanel.StormLayout` (`HeroDeathIconImage`, `HeroDeathTimeLabel2`);
  - the intro: `IntroAnimOnce` in the same file.
- **Ours (gen.py):**
  - the cell: `hero_cell_template`;
  - the timer: `HeroDeathTimeLabel` (~2163);
  - the Viking and Misha timers: `PET_TIMERS` and `pet_death_labels` / `pet_death_bindings`;
  - the textures: `slant_bars` and `top_backplate_texture`.

## Tonight's test build (2026-10-16, stamp ad48279)

**What I picked for your questions** (say if any is wrong):
1. Skull: Blizzard's art and timings, with Ahli's handover to the number.
2. Flash: the white text flash in the last 5 s, plus Blizzard's glow pulse over the plate.
3. Frame: one chrome line round the plates and the XP bar together. The core bar is left out, and there are no lines between heroes. `[row_frame] width = 0` takes it away.
4. Intro: not built. It still needs your OBS plan (hotkey, game start, or both).
5. Extras: the hearthstone squares only. The glow, Auriel's revive and "on fire" come later, if the squares light.
6. The test build is made and deployed.

**What to check in a replay:**
- The stamp, top left, says ad48279.
- **The squares** above each plate light for 6 s when an event arrives. Left to right:

  | # | Colour | Event | Cell |
  |---|---|---|---|
  | 0 | magenta | almost respawned | ours |
  | 1 | cyan | almost respawned | party |
  | 2 | yellow | Viking almost respawned | party |
  | 3 | orange | Viking almost respawned | ours |
  | 4 | green | respawned | ours |
  | 5 | white | respawned | party |
  | 6 | purple | pet almost respawned | party |
  | 7 | pink | hearthstone start | party |
  | 8 | teal | hearthstone start | ours |

  Tell me which ones light.
- **A death:** the skull plays, then the number fades in about 1 s later.
- **Respawn:** in the last 5 s, the number flashes white and the glow pulses. The Vikings' own timers flash too.
- **Thumbnails** above the plates show the party cell's portraits 1, 2 and 3. In a Rexxar game and a Vikings game, do 2 and 3 show Misha and each Viking?
- **The frame:**
  - Does the chrome line sit cleanly round each row?
  - Do the pop-ups and the heroic stay on top of it?
  - Does it look right in a 3v3, if you have one?
  - The rows now sit 2 px higher and a touch smaller, to keep the frame inside the padding.
- **D.Va's Self-Destruct charge** (visual pass): her mech's charge meter doesn't go on the
  plate, but check it shows on her talent card, the way Tracer's Pulse Bomb meter does.
- **Ammo segments** (new in this build): Tracer's bar should show 10 segments, Junkrat's 4
  (3 with Cannonball), Gazlowe's scrap 10 (12 with his talent). If the dividers look wrong or
  don't show, we revisit; if they work, they stay.
- **Hogger:** check his plate's resource bar. He isn't in our per-hero colour list, so it
  probably shows mana blue rather than his rage colour, and unsegmented. Blizzard's own
  Hogger bar is segmented (`hogger.stormlayout`); Ahli cuts his rage every 50.

## Decisions from the question round (2026-10-16, before the test)

Nothing here is built yet; it waits for tonight's diagnostics.

- **The row frame:**
  - The nameplate row and its XP bar stay one piece.
  - Each plate is also wrapped: 3 px seams along every slant (1 px of this plate's inset,
    1 px of border, 1 px of the neighbour's inset), to hide the rough slant edges.
  - The core bar gets its own thinner frame (1-2 px). It's attached to the core and shows only
    when the core shows. The exact widths are for the visual pass.
- **The intro:** at game start. Details and the OBS plan come later.
- **Hearthstone glow, Auriel's revive, on fire:** all wanted, if buildable.
  - Each effect has to work with the chrome: drawn over it, or masked to the plate's shape.
  - On fire comes in team colours. Blizzard's cutscene has Ally/Enemy filters (the colour)
    and Left/Right (the side). An observer may get neither Ally nor Enemy, so we pin blue's
    copy to Ally and red's to Enemy. The next test build needs an on-fire square.
- **Death recap:** to test tonight. In player view, press V (the default hotkey) on a dead
  hero: does Blizzard's recap open? If so, we may only need to keep that route working.
- **Quests:**
  - **Talents pane:** a default-quest column between the hero card and the level-1 talent,
    empty when the hero has none. The pane gets one icon wider; one slot is enough.
    - Blizzard's data shows no hero starting with two default quests; its second slot looks
      like spare room.
    - The heroes that start with a quest counter: Arthas, Azmodan, Butcher, Diablo, Jaina,
      Kerrigan, Leoric, the Lost Vikings, Muradin, Murky, Nova, Sylvanas, Tyrande and
      Witch Doctor. Arthas's and the Vikings' only fill after a talent pick.
  - **Talent quests:** progress shows on the talent's own icon, in the pane and on the
    inspect card.
  - **Inspect card:** nothing extra. Quest counters are visible buffs with their count, so
    the card's buff row already shows them.
  - Buff-row overflow: not a worry unless the user sees it.
- **Tracer:**
  - Pulse Bomb is done (Blizzard's charge meter, lifted onto her plate).
  - Ammo segments are a nice-to-have, only if cheap. Her ammo is her energy: 20 max, and each
    shot spends 2, so 10 shots. No talent changes the max in the current data.
  - Blizzard's own Tracer bar is a segmented energy bar (`Segmented` + `SegmentValue 2`,
    `tracer.stormlayout`), and our plate's `FCJH_Resource` is the same frame type. So it
    may be one Tracer-only state; the divider art needs checking in game.
- **Replay rewind:** not a design consideration. The overlay is for live casting, not replay
  analysis. If there's time at the end, research what a rewind upsets (pop-ups replaying,
  the latched talent watchers, flashes) and whether any of it is cheap to fix.
