import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'

/**
 * Text that wraps to `lines` lines and only then shrinks to fit - the framework's `fit` with
 * room to wrap first.
 *
 * WHY NOT `fit`. Single Studio's `fit` holds its text on one line (`whitespace-nowrap`) and
 * shrinks it to the width. A series card is 107 px wide at fifteen maps, so a team or a map
 * on one line comes out tiny where two lines at full size would read (user, 2026-10-27: the
 * winners' names "can grow to 2 lines before Fit"). This wraps first and shrinks only what
 * two lines still cannot hold - a long name, or one word wider than the card.
 *
 * It refits as the framework's does: when the box it sits in changes size, or its text
 * changes (a Variable inside it loading or being retyped) - and when a font finishes loading.
 * The size it starts from is the CSS one, so the ceiling is the stylesheet's.
 *
 * `<FitLines lines={2}><Variable name="blue.name" fallback="" /></FitLines>`
 */
export default function FitLines({ lines = 2, className, children }) {
  const ref = useRef(null)
  const [stale, setStale] = useState(true)

  const fit = useCallback(() => {
    const el = ref.current
    if (!el) return
    el.style.fontSize = ''

    // lines are counted by the box's own height, not scrollHeight: at a tight line-height the
    // glyphs overhang their lines, and scrollHeight counts the overhang as overflow - two
    // lines read as more, and every name shrank to one
    const fits = () => {
      const lh = parseFloat(window.getComputedStyle(el).lineHeight)
      return el.clientHeight <= lh * lines + 1 && el.scrollWidth <= el.clientWidth
    }
    if (fits()) return

    // the largest size that fits, by halving the gap: twelve steps is under a hundredth of a px
    let lo = 0
    let hi = parseFloat(window.getComputedStyle(el).fontSize)
    for (let i = 0; i < 12; i += 1) {
      const mid = (lo + hi) / 2
      el.style.fontSize = `${mid}px`
      if (fits()) lo = mid
      else hi = mid
    }
    el.style.fontSize = `${lo}px`
  }, [lines])

  useLayoutEffect(() => {
    if (!stale) return
    fit()
    setStale(false)
  }, [stale, fit])

  useEffect(() => {
    const el = ref.current
    if (!el?.parentElement) return
    const refit = () => setStale(true)
    const size = new ResizeObserver(refit)
    const text = new MutationObserver(refit)
    size.observe(el.parentElement)
    text.observe(el, { characterData: true, childList: true, subtree: true })
    // and when a font arrives: measured in the fallback, a name fits a size it will not in
    // the real one, and nothing else changes to say so
    document.fonts.addEventListener('loadingdone', refit)
    document.fonts.ready.then(refit)
    return () => {
      size.disconnect()
      text.disconnect()
      document.fonts.removeEventListener('loadingdone', refit)
    }
  }, [])

  return (
    <span ref={ref} className={['fcjh-fit-lines', className].filter(Boolean).join(' ')}>
      {children}
    </span>
  )
}
