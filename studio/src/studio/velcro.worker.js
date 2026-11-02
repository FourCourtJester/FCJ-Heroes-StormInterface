import { createVelcroHost, urlAssets } from '@single-studio/core/worker'
import { logos, ngs, NgsHandler } from '@single-studio/plugin-ngs'
import { connectSupabase } from '@single-studio/provider-supabase'

import { STUDIO_ID } from './config'
import { mutations } from '../mutations'

// The worker that owns this studio's state, shared by every tab. No React in here.

/**
 * How this studio reaches other operators.
 *
 * Nothing connects until somebody pastes an invite link, so a one-machine show
 * costs nothing -- but leaving this in is what lets a producer join later without a
 * redeploy.
 */
const connect = (context) => {
  // This template ships a Supabase client and nothing else.
  if (!/^https?:/.test(context.url)) {
    throw new Error(
      `This studio only knows how to reach a Supabase project, and ${context.url} is not one. To run your own relay, add y-websocket and a branch here.`,
    )
  }

  return connectSupabase(context)
}

/**
 * What the NGS plugin fetched, written under variables.ngs for the board's NGS panel. The
 * paths are listed in ../mutations/ngs.js, beside the Load that reads them (user, 2026-10-29).
 */
class Heroes extends NgsHandler {
  onSeason({ season, divisions, teams, maps }) {
    // every logo into the image library, as ngs/<team name>, on every machine
    this.mutate('set', urlAssets(logos(teams)))
    this.mutate('set', {
      'variables.ngs.season': season,
      'variables.ngs.divisions': divisions.map(({ key, name }) => ({ key, name })),
      'variables.ngs.maps': maps,
      'variables.ngs.problem': null,
    })
  }

  onMatches({ matches }) {
    // the match picker's choices, each whole so Load needs nothing else; a played match is
    // left out, as nobody casts one twice. The plugin names the rounds ("Round 2",
    // "Semifinals") over the whole division before this, from 0.2.0 (user, 2026-11-02).
    const label = (match) =>
      `${match.roundName || 'Round ?'}: ${match.home?.name ?? 'TBD'} vs ${match.away?.name ?? 'TBD'}`
    this.mutate('set', {
      'variables.ngs.matches': matches
        .filter((match) => !match.reported)
        .map((match) => ({ ...match, label: label(match) })),
      'variables.ngs.problem': null,
    })
  }

  onProblem({ message }) {
    this.mutate('set', { 'variables.ngs.problem': message || 'The league did not answer.' })
  }
}

createVelcroHost({
  name: STUDIO_ID,
  mutations,
  plugins: [ngs(Heroes)],
  sync: { connect },

  /**
   * Runs once the show has loaded, before anything is on air.
   *
   * For data your studio owns rather than an operator: a scoring feed, a socket, a
   * clock of your own. Delete it if only people write to your show.
   */
  onReady({ mutate, owns }) {
    if (!import.meta.env.VITE_FEED_URL) return

    setInterval(async () => {
      // Only the machine running OBS fetches. Everyone else gets the same data a
      // moment later, replicated.
      if (!owns()) return

      try {
        const response = await fetch(import.meta.env.VITE_FEED_URL)

        mutate('my:feed', await response.json())
      } catch (error) {
        // A feed that is down leaves the last values it sent on air.
        console.warn('[studio] feed unreachable', error)
      }
    }, 5000)
  },
})
