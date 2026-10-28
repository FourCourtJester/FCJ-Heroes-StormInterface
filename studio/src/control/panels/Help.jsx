import { useState } from 'react'
import { Panel } from '@single-studio/core/control'

// Directions for whoever is running this, on the board itself rather than in a file they
// would have to know to look for (user, 2026-10-23).
//
// LAST, AND FOLDED. Everything above it is used every show; this is read once while OBS is
// being wired and then never again. Collapsed by default like every other panel, so it costs
// one line of the board to the people who already know.
//
// IT POINTS AT THE SOURCE LIST RATHER THAN REPRODUCING IT (user, 2026-10-23). Embedding the
// framework's `SourceList` here put seven rows and seven URLs in the middle of the reading,
// and the gear menu already has the same list, kept current, one click away. Help's job is to
// say where things are.

const H = ({ children }) => (
  <span className="text-sm font-semibold tracking-wide text-slate-400 uppercase">{children}</span>
)

const P = ({ children }) => <p className="text-sm leading-relaxed text-slate-300">{children}</p>

const Rule = () => <hr className="border-0 border-t border-slate-700/60" />

const A = ({ href, children }) => (
  <a href={href} target="_blank" rel="noreferrer" className="text-sky-400 underline">
    {children}
  </a>
)

// A DOWNLOAD THAT SAYS SO (user, 2026-10-23: the `download` link works in an OBS dock,
// "there's just no visual about it"). The dock saves the file without a download bar, so a
// click looked like nothing happened. The link answers for it for a few seconds instead.
const Download = ({ href, children }) => {
  const [saved, setSaved] = useState(false)
  const click = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 4000)
  }
  return (
    <>
      <a
        href={href}
        download
        target="_blank"
        rel="noreferrer"
        onClick={click}
        className="text-sky-400 underline"
      >
        {children}
      </a>
      {saved && <span className="text-emerald-400"> (downloaded)</span>}
    </>
  )
}

const PAGES = 'https://fourcourtjester.github.io/FCJ-Heroes-StormInterface'
const MASKS = `${PAGES}/masks`
const COLLECTION = `${PAGES}/FCJ_Heroes_Esports_v1.0.json`

export default function Help() {
  return (
    <Panel title="Help" collapsible>
      <H>The image store</H>
      <P>
        Every picture this studio draws — team logos, tournament marks, standby slides — comes
        out of one library shared by every tab. Open it from the <b>gear, top right → Image
        store</b>, or from the <b>magnifier</b> on any image picker, which is the same library
        with the picker ready to choose from it.
      </P>
      <P>
        Drop files on it to add them. Drop a <b>folder</b> and everything in it is filed under
        that folder&rsquo;s name, which is how a slideshow gets loaded in one motion.
      </P>
      <P>
        Adding is not staged — a file arriving is not a broadcast change — but <b>choosing</b>{' '}
        one is, so nothing reaches air until you save. Note that files are added <b>on the
        machine doing the adding</b>: the library tells every machine that a picture exists,
        but the bytes live where they were dropped. A graphic leaves out a picture this machine
        cannot paint rather than putting a blank on air.
      </P>

      <Rule />
      <H>Browser sources</H>
      <P>
        Every graphic here is a browser source. The <b>gear, top right → Browser sources</b>{' '}
        lists every one of them with its URL and a button to copy it. In OBS:{' '}
        <b>Add → Browser</b>, paste the URL, and set the size to <b>1920 x 1080</b>.
      </P>
      <P>
        On anything with an entrance — the matchup band, the draft — tick{' '}
        <b>Shutdown source when not visible</b>. The animation runs when the source loads, so
        shutting it down while its scene is hidden is what makes it play again each time you
        cut back, instead of once a session. Leave it off on the scores screen: reloading, it
        shows the game's interface for a moment before its sky arrives.
      </P>

      <Rule />
      <H>Using this studio</H>
      <P>
        Start from the <Download href={COLLECTION}>OBS collection</Download> and use it as a base: in OBS, <b>Scene Collection → Import</b>, then pick the file you
        just downloaded. It arrives with the scenes laid out and every browser source already
        placed and sized. Mix and match from there as the show needs — nothing here assumes
        you are running all of them, and every graphic is independent of the others.
      </P>
      <P>
        <b>Standby slides.</b> The standby screen plays whatever is filed under{' '}
        <code className="text-slate-200">slides/</code> in the image store, so dropping a
        folder named <code className="text-slate-200">slides</code> on the library loads the
        whole deck at once. There is no list in the studio to keep in step with it: add or
        remove pictures mid-show and the deck follows without a reload. One picture on its own
        simply sits there — no timer is armed and nothing cycles.
      </P>
      <P>
        <b>File them at 2560 x 1440 or larger, 16:9.</b> The screen drifts slowly across each
        picture at 1.3x, so a 1920-wide slide is already being enlarged before anyone sees it
        — 2560 is what it takes to stay sharp at that scale. A slide that is not 16:9 is
        <b> centre-cropped to fill</b> rather than letterboxed, so a portrait picture loses
        most of itself; a small one is enlarged rather than shown small. If a slide is a
        designed card rather than a photograph, keep anything that has to stay on screen
        inside the middle <b>~50% across and ~60% down</b> — that is what the drift leaves
        visible for the whole cycle.
      </P>
      <P>
        <b>Webcam masks.</b> The webcam sources draw frames only; the cameras go underneath in
        OBS. To cut the camera to the frame&rsquo;s shape, add <b>Filters → Image Mask/Blend</b>{' '}
        to the camera source, set it to <b>Alpha Mask (Alpha Channel)</b>, and point it at the
        mask for that side: <A href={`${MASKS}/cam_mask_left.png`}>cam_mask_left.png</A> or{' '}
        <A href={`${MASKS}/cam_mask_right.png`}>cam_mask_right.png</A>. The single centred
        window uses the left one.
      </P>
    </Panel>
  )
}
