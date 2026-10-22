import { createVelcroHost } from '@single-studio/core/worker'
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

createVelcroHost({
  name: STUDIO_ID,
  mutations,
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
