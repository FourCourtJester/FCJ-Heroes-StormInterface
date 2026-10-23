# Single Studio: things to raise upstream

A running log of framework behaviour this studio had to work around, for filing against
[Single Studio](https://github.com/FourCourtJester/Single-Studio). Each entry: what it does,
exactly where, since when, why it's a problem here, what we'd ask for, and — where there is
one — the override we are carrying meanwhile.

Our own mistakes don't belong here. The framework's do, and so does toolchain behaviour that
bites a studio building on it: entry 3 is almost certainly not core's doing, but it is core's
users who hit it. Every number in here was measured on a running board, not reasoned out.

---

## 1. The board re-pads itself at 640px, and a studio can't turn it off

**Found** 2026-10-23, on 0.13.0. **Not a 0.13.0 regression** — 0.12.0's bundle carries the
same classes, byte for byte. It only became obvious here once the panels were made
collapsible and the board stopped being tall enough to hide it.

### What happens

Three things step at Tailwind's `sm` (40rem / 640px), measured on a live board at 625px and
700px:

| Element | Classes | Below 640 | 640 and up |
|---|---|---|---|
| `.ss-panel` (`control.js`) | `p-3 sm:p-4` | 12px | 16px |
| the board's `<main>` (`index.js`) | `gap-3 p-3 sm:gap-4 sm:p-4` | 12px padding, 12px gap | 16px and 16px |
| `.ss-control-bar` (`index.js`) | `px-3 py-2.5 sm:px-4 sm:py-3` | 12px / 10px | 16px / 12px |

(`sm:inset-6` on `AssetLibraryDialog` is excluded — that one is documented and deliberate.)

### Why it's a problem

1. **Nobody asked for it, and it can't be configured.** These are Tailwind utilities baked
   into the markup. The only way out is for a studio to write unlayered CSS that beats
   `@layer utilities` — which works, but means overriding the framework's own markup rather
   than setting a value it offers.

2. **It's inconsistent with how the same file treats the Row.** `.ss-row` exposes
   `--ss-row-gap`, `--ss-basis` and `--ss-label-offset`, and `base.css` says in a comment that
   its rules sit in `@layer components` *on purpose* so a studio's plain CSS can win. The Row
   is tunable by design; the padding around it is not, and there is no stated reason for the
   difference.

3. **The `<main>` has no hook at all.** `.ss-panel` and `.ss-control-bar` can at least be
   named. The board's `<main>` carries only Tailwind classes, so an override has to reach it
   through `.ss-control > main` — a structural selector that breaks the first time the tree
   changes.

4. **It is keyed to the viewport, but the thing that varies is the dock.** In an OBS custom
   browser dock those are the same, which means the chrome visibly re-flows while an operator
   drags the dock edge past 640 — a size change nobody asked for in the middle of a show.

### What we'd ask for

Expose them the way the Row already is, keeping the current values as defaults so nothing
changes for anyone who doesn't care:

```css
.ss-panel      { padding: var(--ss-panel-pad); }
.ss-control    { --ss-board-pad: …; --ss-board-gap: …; }
.ss-control-bar{ padding: var(--ss-bar-pad-y) var(--ss-bar-pad-x); }
```

and give the board's `<main>` an `ss-board` class so it can be addressed by name.

A studio that wants the step keeps it. A studio that wants one constant size sets four
properties instead of fighting four utilities.

### What we carry meanwhile

In `studio/src/css/index.css`, unlayered, pinned to the ≥640 values so the board looks the way
it does now at every width:

```css
.ss-panel { padding: var(--fcjh-panel-pad); }
.ss-control > main { padding: var(--fcjh-panel-pad); gap: var(--fcjh-panel-pad); }
.ss-control-bar { padding: var(--fcjh-bar-pad-y) var(--fcjh-panel-pad); }
```

Related: the same stylesheet moves `.ss-row`'s own breakpoint from 48rem to 40rem. That one is
a preference rather than a defect — the framework offers the properties to do it with, which
is exactly the point being made above.

---

## 2. `col-auto` on a control with operator-supplied content has no ceiling

**Found** 2026-10-23, on 0.13.0. Same in 0.12.0.

### What happens

`col-auto` means "size to your content and do not shrink" — `flex: 0 0 auto`. That is right
for a control whose content is bounded: a Stepper is 160px and always will be. It is wrong
for `ImagePicker`, whose width is set by the longest key in the image library, because a
`<select>` sizes itself to its widest option. The library is filled by the operator at run
time, so the control has no ceiling.

Measured on a 640px board, by renaming one asset:

| longest key | picker | the Field beside it |
|---|---|---|
| `x` | 136px | 255px |
| `broadcaster` | 202px | 188px |
| `northwind-esports-primary-logo-2026` | 365px | **25px** |

A board laid out and checked at design time silently degrades months later because somebody
named a logo descriptively. Nothing warns, and the control that loses is whichever neighbour
is `flex: 1 1 0` — usually the name field that matters most.

### What we'd ask for

Put the ceiling where the cause is, in the utility itself:

```css
@utility col-auto {
  .ss-row > & { flex: 0 0 auto; }
  .ss-row > &.ss-image-picker { max-width: var(--ss-picker-max, 9.25rem); }
}
```

This has to live in the framework, because **a studio cannot express it**. `col-auto` is a
Tailwind utility, so an element carries the literal class `sm:col-auto`, and that class is
present at every width while the `flex` rule only applies inside the variant's media query.
An attribute selector like `[class*="col-auto"]` therefore matches below the breakpoint too —
exactly where the control has a line to itself and must fill it. Declared inside the utility,
the variant's media query wraps the cap as well, and it is correct at every breakpoint for
free.

The same argument covers any control sized by operator-supplied content. `col-auto` is a
promise about layout that only the component knows how to keep.

### What we carry meanwhile

A breakpoint band in `studio/src/css/index.css`, which is the shape of the rule we can write:

```css
@media (min-width: 40rem) and (max-width: 47.9375rem) {
  .ss-image-picker { max-width: var(--fcjh-picker-max); }
}
```

It is a stand-in, not an equivalent. It caps by *width* where the real rule is about *sizing
mode*, so it also caps a row of two pickers that has room to spare — in our Tournament panel
that leaves about 338px unused at 700px wide. With the cap on `col-auto` instead, that row
would scale and only a `col-auto` picker would be held back.

---

## 3. A mistyped custom property is a silent no-op, and dev HMR can manufacture one

**Found** 2026-10-23, on 0.13.0, working in a studio's own `src/css/index.css`. Likely a
Vite/Tailwind behaviour rather than anything in core — filed here because core's own layer is
custom-property-driven, so the failure mode belongs to anyone building on it.

### What happened

Mid-edit, a rule in the studio's stylesheet measured as having no effect at all. The page's
served `<style>` held this:

```css
@media (min-width: 40rem) and (max-width: 47.9375rem) {
  .ss-image-picker { max-width: var(--fcjh-picker-max); }   /* the new rule */
}
.ss-control { --fcjh-picker-name: 4.5rem; }                 /* the OLD variable name */
```

The rule had updated; the block declaring the property it reads had not. Two edits to one file
seconds apart, and the hot update applied one of them. `npm run build` was correct throughout,
and the raw file on disk was correct, so everything *looked* right everywhere except the only
place that mattered. Restarting the dev server cleared it.

Seen once and not isolated further, so this is a report of a state, not a reproduction.

### Why it is worth knowing

The visible symptom is not "a stale rule" — it is **no rule**. `max-width: var(--undefined)`
is an invalid declaration at computed-value time, so it resolves to `none`: identical to a
stylesheet that never loaded. Fifteen minutes went into checking the file, the served
response, the build output and the cascade before looking at the two together.

That matters here specifically because core's layer is built on custom properties —
`--ss-basis`, `--ss-label-offset`, `--ss-shift`, `--ss-duration`, `--ss-row-gap`. A studio
overriding one and misspelling it gets silence, not a warning, and the same is true of a
studio reading one that gets renamed in a future release. Our own `.ss-row` and `.ss-image-picker`
overrides are exactly that shape.

### What we'd ask for

Nothing in the code. Two things in the docs, where the custom properties are introduced:

- say that a studio reading an `--ss-*` property should use the two-argument form,
  `var(--ss-basis, 0%)`, so a rename or a typo degrades to a default rather than to nothing;
- note that a half-applied CSS hot update can produce exactly this, and that the check is to
  read the page's own `<style>` rather than the file — a restart, not a reload, clears it.

If core ever renames an `--ss-*` property, that is a breaking change for every studio
overriding it, and one that breaks quietly. Worth a line in the release notes when it happens.

