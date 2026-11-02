# Team logos for the top bar

How to make a team logo that fills the Game source's logo plate, the slanted box beside each
team's name in the top bar. Written for teams and leagues sending us logos (user, 2026-11-02).

## The short version

- **680 × 400 PNG.** The plate is 110 × 65 px at 1080p, so this is the same shape at about
  six times the size, with room for 4K.
- **Keep the art in the clear hexagon** of the template:
  [`studio/public/masks/logo_template.png`](../studio/public/masks/logo_template.png), on
  the published studio at
  `https://fourcourtjester.github.io/FCJ-Heroes-StormInterface/masks/logo_template.png`.
  Lay it over the logo as the top layer in Photoshop, and hide it before saving.
- **Fill the rest with background**, not logo. Colour, texture or transparent all work;
  transparent shows the plate's own dark fill.

## Why a hexagon

The plate is a parallelogram, and the two sides lean opposite ways: blue's leans `\`, red's
`/`. A team can play on either side, so the only area that always shows is where the two
parallelograms overlap. The template marks it:

| On the template | What it means |
| --- | --- |
| Clear, white outline | Shows on both sides. The logo goes here. |
| Blue corners (top left, bottom right) | Show only when the team is blue. |
| Red corners (top right, bottom left) | Show only when the team is red. |
| Dark notches (far left and right) | Never show. |
| Pale bands | The plate's frame, drawn over the logo: the top, the bottom, and each side's outer slant. |

At 680 × 400 the hexagon's top and bottom edges run from x = 216 to 464, and its widest
point, halfway down, from x = 108 to 572. A square or round emblem fits at about 290 × 290
in the middle, clear of the frame. The top half of the plate also carries a faint white
sheen, as the name plate does.

## How the studio draws a logo

A logo is drawn as wide as the plate and centred, then cut to the plate's shape
(`object-fit: cover`). A 680 × 400 logo fits exactly. Any other shape is scaled to cover the
plate and loses whatever runs past it: a square logo loses its top and bottom.

**NGS logos get their own rule.** The Nexus Gaming Series pads every logo onto a 500 × 350
clear canvas, so the studio zooms a logo from NGS's address by 500/350 to make up for the
padding (`--ngs-zoom` in `studio/src/sources/game.css`). A plate-shaped logo should come in
through the board's own Logos panel, not NGS's address, or it gets zoomed too.

The Matchup, Scores and Series screens show the whole logo, uncut. A plate-shaped logo is a
second file for the top bar, not a replacement for a team's usual logo.

## Where the numbers come from

The template is generated from `layout.toml` by `tools/obs.py` (`logo_template_png`), so it
follows the plate if the plate changes; `python tools/gen.py --check` fails if it is stale.
The coordinates above are as of 2026-11-02; the template is the authority.
