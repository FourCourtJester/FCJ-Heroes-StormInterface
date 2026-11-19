# A responsive board bar in Single Studio

Findings from FCJH, 2026-11-19, on Single Studio 0.18.1. The aim is to carry them to other
studios. The board's header bar holds the panel jump and a series score. As the board narrows,
the bar goes from one line, to two, to three. Everything here was measured in Chromium. Check
it in your own OBS dock before you trust it on air.

## The layout

| Bar content width | Layout |
| --- | --- |
| over jump + gap + score | **One line.** The jump at the left, the score pushed right (`ml-auto`). |
| jump + gap + score or less | **Two lines.** The jump fills line one; the score is centred on line two. |
| score or less | **Three lines.** The jump, then Blue, then Red, each centred, with "vs" hidden. Both sides read *name then stepper*, and the names share one width so the steppers line up. |

Each side's stepper and name sit in one span, so the pair never splits when the bar wraps.

```jsx
// Control.jsx
<BoardBar className="x-jump-group">
  <PanelJump className="x-jump" />
</BoardBar>
<ScoreBar />
```

```jsx
// ScoreBar.jsx
import { BoardBar, Stepper } from '@single-studio/core/control'

const Name = ({ children, tint }) => (
  <span className={`x-score-label text-sm font-semibold tracking-wide uppercase ${tint}`}>
    {children}
  </span>
)

export default function ScoreBar() {
  return (
    <BoardBar className="x-score-group ml-auto">
      <span className="x-score-side blue">
        <Stepper name="blue.wins" className="x-score-stepper" />
        <Name tint="text-sky-400">Blue</Name>
      </span>
      <span className="x-score-vs px-1 text-xs font-semibold text-slate-500 uppercase">vs</span>
      <span className="x-score-side red">
        <Name tint="text-rose-400">Red</Name>
        <Stepper name="red.wins" className="x-score-stepper" />
      </span>
    </BoardBar>
  )
}
```

Use **Blue and Red, never the teams' names.** Names can be very long, and the bar has to be
the same width every match.

```css
/* Stepper has no compact size, so this is a size down for a strip rather than a panel row */
.x-score-stepper { --ss-input-h: 1.75rem; }
.x-score-stepper .ss-stepper-value { width: 2.5rem; flex-grow: 0; font-size: 1rem; }
.x-score-stepper button { font-size: 1rem; }

.x-score-side { display: flex; align-items: center; gap: 0.5rem; }

/* the bar is the container, so both steps measure the bar, not the window */
.ss-board-bar { container: x-bar / inline-size; }

@container x-bar (max-width: 503.4px) {   /* jump + gap + score: re-measure yours */
  .x-jump-group { flex-basis: 100%; }
  .x-jump { width: 100%; }
  .x-score-group { flex-basis: 100%; justify-content: center; }
}

@container x-bar (max-width: 346.6px) {   /* the score on one line */
  .x-score-vs { display: none; }
  .x-score-side { flex-basis: 100%; justify-content: center; }
  .x-score-side.blue .x-score-label { order: -1; }
  .x-score-label { min-width: 2.75rem; text-align: right; }
}
```

## What we learned

### 1. Measure the bar, not the window

A media query measures the window, and the window's width includes the scrollbar. That
scrollbar is not one number:

| Situation | Scrollbar |
| --- | --- |
| Windows, before Single Studio 0.18.1 | 17px |
| Single Studio 0.18.1 and later (thin, dark scrollbars) | about 13px |
| Board short enough not to scroll | none |
| macOS, Linux and phones (overlay scrollbars) | none |

So a window breakpoint lines up with your layout for only one of these. A container query on
`.ss-board-bar` measures the bar's content box, and it fires at the same place in every case.

### 2. The jump's width is your panel titles, not the font

`PanelJump` is a native `<select>`, and a select is as wide as its longest option. That
option is your longest panel title. Our score measured the same 346.6px as the studio this
came from, because the labels, steppers and font are the same. Our jump didn't match. The
original two-line rule was a 511px window; ours is 503.4px of bar, about a 527px window. With
the borrowed 511, between 511 and 527px our score wrapped onto line two by itself and sat at
the right, uncentred.

**Re-measure the two-line step whenever a panel title gets longer** (a season number in a
title is enough).

### 3. How to measure

In the board, at any width wide enough for one line:

```js
const g = document.querySelector('.x-score-group')
const kids = [...g.children].filter((k) => getComputedStyle(k).display !== 'none')
const score = kids.reduce((a, k) => a + k.getBoundingClientRect().width, 0)
  + parseFloat(getComputedStyle(g).columnGap) * (kids.length - 1)
const jump = document.querySelector('.x-jump-group').getBoundingClientRect().width
const barGap = parseFloat(getComputedStyle(document.querySelector('.ss-board-bar')).columnGap)
;({ score, twoLine: jump + barGap + score })
```

These are the thresholds for the two `@container` rules.

To turn a bar width into a window width, add the bar's horizontal padding. Under 640px that's
24px (0.75rem a side, `--ss-bar-pad-x`). Then add the scrollbar, if there is one:

| Step | Bar content | Window, no scrollbar | Window, 0.18.1 thin scrollbar |
| --- | --- | --- | --- |
| Three lines | 346.6px or less | 370px or less (371 is two lines) | 383px or less (384 is two lines) |
| Two lines | 503.4px or less | about 527px or less | about 540px or less |

### 4. Elements in a panel that should switch with the bar

We stack the Score Screen Winner's two buttons, a `Row`, at the same point as the bar's third
step. A Row goes side by side by setting `--ss-basis: 0%`. The framework does it at 48rem, and
FCJH moves the board's Rows to 40rem. One Row can have a breakpoint of its own:

```css
@media (min-width: 384px) {   /* the bar's three-line point with the thin scrollbar */
  .x-winner-row { --ss-basis: 0%; }
}
```

This is a window rule, so it only lines up with the bar when there's a scrollbar. With none,
the bar splits at 371px and the buttons at 384px. To line it up in every case, wrap the Row in
a container and query that wrapper instead. Its width is the bar's less the board's and the
panel's padding and border, which for FCJH is 41.6px less, so 346.6px there is 305px here.
Measure both at the same window width.

### 5. Use whole pixels in media queries

On a 2× screen, a 388px window measured a hair over 388, so a `min-width: 388.01px` rule
matched at 388. Write `min-width: 389px` rather than chasing the fraction.

### 6. Check scrollbar cases in the real dock

The Claude desktop app's browser pane and Chrome's device emulation use overlay scrollbars, so
they always show the no-scrollbar case. The thin-scrollbar numbers above were measured in the
real thing. Before you trust a scrollbar number, check it in OBS's dock or in desktop Chrome
with a long board.

### 7. Framework notes (0.18.x)

- **Padding is a set of properties since 0.18.0:** `--ss-board-pad`, `--ss-board-gap`,
  `--ss-panel-pad`, `--ss-bar-pad-x` and `--ss-bar-pad-y`, set on `.ss-control`. They still
  step at 40rem by default. Set them on `.ss-control` in your own CSS to change them at every
  width; you no longer need unlayered rules against Tailwind's utilities.
- **Scrollbars are thin and dark since 0.18.1.** Recolour them with `--ss-scrollbar-thumb`
  and `--ss-scrollbar-track` on the root.
- **`BoardBar`** takes a `className`, and several BoardBars sit side by side as groups.
  **`PanelJump`** takes a `className` too.
- **`Stepper`'s buttons add**, so two operators pressing + at once come to +2. Put the bar's
  steppers on the same paths as the panel's, so the two are one score.
