// Everything that can change this studio's state, in one object. If it is not in
// here, it cannot be dispatched.
//
// A mutation is a named function that changes state -- a reducer, if that is the
// word you know it by. Dispatch it by name from anywhere:
//
//   const mutate = useVelcroMutate()
//   <button onClick={() => mutate('my:example', { team: 'home' })}>Do it</button>
//
// However many paths it touches, every graphic sees one change rather than a
// sequence -- which is the reason to write one instead of calling `set` three times
// from a click handler.
//
// Split by area as the show grows, one file per part of the broadcast:
//
//   import { roster } from './roster'
//
//   export const mutations = { ...roster, ... }
//
// There are worked examples in ./examples.js, which nothing imports.
//
// What you are given:
//
//   ctx.read(path)          the current value at a path
//   ctx.collect(prefix)     a collection, as { key: value }
//   ctx.list(prefix, opts)  the same, ordered, as [key, value] entries
//   ctx.write(pairs)        set values; an empty value deletes the path
//   ctx.add(path, n)        add to a counter -- use this for anything an operator adjusts
//   ctx.now()               the time in the room, not on this machine
//   ctx.set / append / push / pull / move / patch / replace / ...  any built-in
//   ctx.run(name, payload)  any mutation by name, including your own
//
// Worth doing from the first one:
//
//   1. Name them `area:verb` -- `roster:add`, `game:score`. The prefix keeps yours
//      from colliding with a built-in.
//   2. Use `ctx.add` for numbers, not read-then-write.
//   3. Use `ctx.now()` rather than `Date.now()` for anything time-shaped, so a
//      stored instant means the same moment on every machine.
//   4. Nothing but the store in here -- no fetch, no timers. Those belong in
//      studio/velcro.worker.js, which calls a mutation with the result.
//
// See docs/data.md for the whole surface and worked examples.

export const mutations = {
  /**
   * A no-op you can wire to a button to check the round trip works, then replace.
   *
   * `mutate('my:example', { team: 'home' })`
   */
  'my:example'(ctx, payload) {
    // Write what should change. For example, landing together as one change on air:
    //
    //   ctx.add(`variables.${payload.team}.score`, 1)
    //   ctx.set({ 'toggles.bigplay': true })
    void ctx
    void payload
  },
}
