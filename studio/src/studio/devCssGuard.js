// Is the dev server actually serving the stylesheet it thinks it is?
//
// Twice on 2026-10-23 it was not. Once a hot update applied half of a two-part edit, leaving a
// rule reading a custom property whose declaration had not updated; once the whole Tailwind
// utility layer went missing after Vite auto-restarted on a `vite.config.js` mtime change that
// was not a change at all. Both times `npm run build` was correct and only the running server
// was wrong, so every instinct - read the file, read the served response, read the cascade -
// pointed away from the actual fault. Both times the cure was a RESTART, not a reload.
//
// So: check, say so loudly, and name the cure. Development only; `import.meta.env.DEV` is
// false in the build, and a bundler drops the whole thing.
//
// The banner styles itself inline, on purpose. The one thing we know when it fires is that
// the stylesheet cannot be trusted.

const PROBE = 'flex'

export function checkDevCss() {
  if (!import.meta.env.DEV) return

  // after a frame, so Vite's injected <style> has certainly landed
  requestAnimationFrame(() => {
    const probe = document.createElement('div')
    probe.className = PROBE
    probe.style.position = 'absolute'
    probe.style.visibility = 'hidden'
    document.body.appendChild(probe)
    const ok = getComputedStyle(probe).display === 'flex'
    probe.remove()
    if (ok) return

    const cure = 'Restart the dev server (not a reload, and not a hard reload).'
    // eslint-disable-next-line no-console
    console.error(
      `[fcjh] Tailwind's utilities are missing from the served CSS. ${cure}\n` +
        'The code is probably fine: run `npm run build` and look at dist/assets/*.css. ' +
        'If the built CSS has .flex in it, this is the dev server, not you. ' +
        'See docs/single-studio-reports.md, entry 3.',
    )

    const bar = document.createElement('div')
    bar.setAttribute('data-fcjh-dev-css', '')
    bar.textContent = `Dev CSS is stale — utilities are missing. ${cure}`
    Object.assign(bar.style, {
      position: 'fixed',
      insetInline: '0',
      top: '0',
      zIndex: '2147483647',
      background: '#b91c1c',
      color: '#fff',
      font: '600 13px/1.4 system-ui, sans-serif',
      padding: '10px 14px',
      textAlign: 'center',
      letterSpacing: '0.02em',
    })
    document.body.prepend(bar)
  })
}
