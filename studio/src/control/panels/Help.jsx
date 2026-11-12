import { useId, useState } from 'react'
import { Panel } from '@single-studio/core/control'

// Directions for whoever is running this, on the board itself rather than in a file they
// would have to know to look for (user, 2026-10-23).
//
// FIRST, AND FOLDED (user, 2026-11-12: moved to the top). It is where a new operator starts,
// and folded it costs one line of the board to the people who already know.
//
// QUESTIONS, NOT CHAPTERS (user, 2026-11-12). An accordion with fewer borders: the questions
// listed, each answer opening under its own. Nothing is open at first, and any number can be
// open at once, as somebody wiring OBS may read two side by side.
//
// IT POINTS AT THE SOURCE LIST RATHER THAN REPRODUCING IT (user, 2026-10-23). Embedding the
// framework's `SourceList` here put seven rows and seven URLs in the middle of the reading,
// and the gear menu already has the same list, kept current, one click away. Help's job is to
// say where things are.

const Group = ({ children }) => (
  <span className="mt-3 mb-0.5 text-xs font-semibold tracking-wide text-slate-500 uppercase first:mt-0">
    {children}
  </span>
)

// One question. No box and no rule round it: the chevron and a hover tint say it opens, and
// the answer sits indented under the question's text.
function Q({ q, children }) {
  const [open, setOpen] = useState(false)
  const id = useId()
  return (
    <div className="flex flex-col">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen(!open)}
        className="-mx-2 flex items-start gap-2 rounded-md px-2 py-1.5 text-left text-sm font-medium text-slate-200 transition-colors hover:bg-slate-800/60"
      >
        <span
          aria-hidden
          className={`inline-block w-3 shrink-0 text-slate-500 transition-transform ${open ? 'rotate-90' : ''}`}
        >
          &#9656;
        </span>
        <span>{q}</span>
      </button>
      {open && (
        <div id={id} className="flex flex-col gap-2 pt-1 pb-3 pl-5">
          {children}
        </div>
      )}
    </div>
  )
}

const P = ({ children }) => <p className="text-sm leading-relaxed text-slate-300">{children}</p>

const Code = ({ children }) => <code className="text-slate-200">{children}</code>

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
const REPO = 'https://github.com/FourCourtJester/FCJ-Heroes-StormInterface'

export default function Help() {
  return (
    <Panel title="Help" collapsible>
      <div className="flex flex-col">
        <Group>Single Studio</Group>

        <Q q="How do I get a graphic into OBS?">
          <P>
            Every graphic here is a browser source. The <b>gear, top right → Browser sources</b>{' '}
            lists every one of them with its URL and a button to copy it. In OBS:{' '}
            <b>Add → Browser</b>, paste the URL, and set the size to <b>1920 x 1080</b>.
          </P>
          <P>
            Quicker still, start from the <Download href={COLLECTION}>OBS collection</Download>:
            in OBS, <b>Scene Collection → Import</b>, then pick the file you just downloaded. It
            arrives with the scenes laid out and every browser source already placed and sized.
            Mix and match from there as the show needs; every graphic is independent of the
            others.
          </P>
          <P>
            On anything with an entrance — the matchup band, the draft — tick{' '}
            <b>Shutdown source when not visible</b>. The animation runs when the source loads, so
            shutting it down while its scene is hidden is what makes it play again each time you
            cut back, instead of once a session. Leave it off on the scores screen: reloading, it
            shows the game&rsquo;s interface for a moment before its sky arrives.
          </P>
        </Q>

        <Q q="Where do the logos and pictures live?">
          <P>
            Every picture this studio draws — team logos, tournament marks, standby slides —
            comes out of one library shared by every tab, the image store. Open it from the{' '}
            <b>gear, top right → Image store</b>, or from the <b>magnifier</b> on any image
            picker, which is the same library with the picker ready to choose from it.
          </P>
          <P>
            Drop files on it to add them. Drop a <b>folder</b> and everything in it is filed
            under that folder&rsquo;s name, which is how a slideshow gets loaded in one motion.
          </P>
          <P>
            Adding is not staged — a file arriving is not a broadcast change — but{' '}
            <b>choosing</b> one is, so nothing reaches air until you save. Files are added{' '}
            <b>on the machine doing the adding</b>: the library tells every machine that a
            picture exists, but the bytes live where they were dropped. A graphic leaves out a
            picture this machine cannot paint rather than putting a blank on air.
          </P>
        </Q>

        <Group>This studio</Group>

        <Q q="What plays on the standby screen?">
          <P>
            Whatever is filed under <Code>slides/</Code> in the image store, so dropping a folder
            named <Code>slides</Code> on the library loads the whole deck at once. There is no
            list in the studio to keep in step with it: add or remove pictures mid-show and the
            deck follows without a reload. One picture on its own simply sits there — no timer is
            armed and nothing cycles.
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
        </Q>

        <Q q="How do I shape a webcam to its frame?">
          <P>
            The webcam sources draw frames only; the cameras go underneath in OBS. Add{' '}
            <b>Filters → Image Mask/Blend</b> to the camera source, set it to{' '}
            <b>Alpha Mask (Alpha Channel)</b>, and point it at the mask for that side:{' '}
            <A href={`${MASKS}/cam_mask_left.png`}>cam_mask_left.png</A> or{' '}
            <A href={`${MASKS}/cam_mask_right.png`}>cam_mask_right.png</A>. The single centred
            window uses the left one.
          </P>
        </Q>

        <Q q="I'm not casting NGS. Can I ignore that panel?">
          <P>
            Yes. Nothing else on the board depends on it — fill the panels by hand and leave it
            folded.
          </P>
          <P>
            For a <b>Nexus Gaming Series</b> match it saves the typing: choose a division and a
            match, press <b>Load</b>, and it fills the teams and their logos, the
            tournament&rsquo;s tabs, and the series&rsquo; best-of and maps. It never sets a
            score, and everything it fills stays yours to change. It needs no key or login, and
            its one setting is under <b>gear, top right → Plugins → NGS</b>.
          </P>
        </Q>

        <Group>The interface</Group>

        <Q q="Where do I get the in-game observer interface?">
          <P>
            It is a separate download: the latest <Code>.StormInterface</Code> file from{' '}
            <A href={`${REPO}/releases/latest`}>the releases page</A>. Put it in{' '}
            <Code>Documents\Heroes of the Storm\Interfaces\</Code> (make the{' '}
            <Code>Interfaces</Code> folder if it isn&rsquo;t there), then pick it in Heroes under{' '}
            <b>Settings → Observer</b>.
          </P>
          <P>
            The source, release notes and issues are on <A href={REPO}>GitHub</A>.
          </P>
        </Q>
      </div>
    </Panel>
  )
}
