import { useVelcroValue } from '@single-studio/core'

import cb from '../generated/colourblind.json'

// Colour-blind mode, on the operator's toggle (Tournament panel, user 2026-10-25). The game's
// own colour-blind option turns our interface's red orange and its blue a touch cyan, but a
// browser source can't read the game's options - so the operator says, and every graphic
// that paints a team colour switches to the same two the interface uses.
//
// The colours come from ../generated/colourblind.json, which tools/obs.py writes with the
// interface's own rule (gen.colour_blind_cfg), so OBS and the game cannot disagree. Art that
// carries a team colour has a `_cb` twin there too; a scene root wears `cb` when the mode is
// on, and its stylesheet swaps the URLs.

export const COLOUR_BLIND = cb.colours

// "#5cbcec" -> "92 188 236", the form the stylesheets' rgb(var(--x-rgb) / alpha) wants
const rgbOf = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ')

// the team colours as custom properties, for a scene that reads --blue-rgb and --red-rgb
export const COLOUR_BLIND_VARS = {
  '--blue-rgb': rgbOf(COLOUR_BLIND.blue),
  '--red-rgb': rgbOf(COLOUR_BLIND.red),
}

/** Is colour-blind mode on? Absent means off. */
export const useColourBlind = () => Boolean(useVelcroValue('toggles.colourblind'))
