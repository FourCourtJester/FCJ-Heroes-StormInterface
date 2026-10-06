"""
Validate an interface's layouts against Blizzard's base UI, before the game
gets a chance to ignore them silently.

Builds the GameUI frame tree the way the game does - Blizzard's layouts from
the JamiePhan extract, in DescIndex order, with templates expanded and every
file="..." override applied - then checks what OUR files contribute to it.

Errors (the build is almost certainly wrong):
  - XML that does not parse (the game drops the whole interface)
  - DescIndex includes a file that does not exist
  - #Constant that is never defined
  - template="File/Frame" or file="..." that names nothing
  - a frame reference that resolves to nothing: Anchor relative=, Animation
    Controller/Event frame=, StateGroup When/Action frame=, {bindings}
  - Anchor with a bad side / pos / non-numeric offset
  - editing a Blizzard frame's child that does not exist: the game (and the
    old Java builder) silently creates a NEW empty frame instead. A typo, or a
    frame a patch renamed. Frames we add on purpose carry the FCJH_ prefix.

Warnings (legal, but has cost us builds before):
  - editing a frame with a different type= than Blizzard's
  - parking a frame that other frames anchor to (they get dragged with it)
  - anchoring a side that Blizzard re-anchors at runtime with SetAnchor
  - Visible=false on a Blizzard frame (does not stick; park it instead)
  - ColorAdjustMode Fill without AdjustmentColor (fills with nothing)
  - #Constant used inside a longer value (only whole values substitute)
  - a layout in the source that DescIndex does not include

    python tools/validate.py                  # validates src/FCJH.StormInterface
    python tools/validate.py <interface-dir>
    python tools/validate.py --show GameUI/UIContainer/FullscreenUpperContainer/ObserverHeroOverviewPanel/Team1HeroOverview/HeroOverview1
"""

import argparse
import re
import sys
import xml.parsers.expat
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO / "src" / "FCJH.StormInterface"
MODS = REPO / "references" / "JamiePhan" / "mods"
BASE_MODS = ["core.stormmod", "heroesdata.stormmod"]

OUR_PREFIX = "FCJH_"
PARK_THRESHOLD = 5000  # an anchor offset this large means "moved off-screen"

SIDES = {"top", "bottom", "left", "right"}
POSITIONS = {"min", "mid", "max"}


# ------------------------------------------------------------------ XML with line numbers

class El:
    __slots__ = ("tag", "attrib", "children", "file", "line", "ours")

    def __init__(self, tag, attrib, file, line, ours):
        self.tag = tag.lower()
        self.attrib = {k.lower(): v for k, v in attrib.items()}
        self.children = []
        self.file = file
        self.line = line
        self.ours = ours

    def get(self, key):
        return self.attrib.get(key)

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()


def parse_xml(path, display, ours):
    """Parse a file into El nodes. Returns (root, None) or (None, (line, message))."""
    parser = xml.parsers.expat.ParserCreate()
    stack, holder = [], []

    def start(tag, attrs):
        e = El(tag, attrs, display, parser.CurrentLineNumber, ours)
        (stack[-1].children if stack else holder).append(e)
        stack.append(e)

    parser.StartElementHandler = start
    parser.EndElementHandler = lambda tag: stack.pop()
    try:
        with open(path, "rb") as f:
            parser.ParseFile(f)
    except xml.parsers.expat.ExpatError as e:
        return None, (e.lineno, f"XML does not parse: {xml.parsers.expat.ErrorString(e.code)} "
                                f"- the game will silently ignore the whole interface")
    return holder[0], None


# ------------------------------------------------------------------ frame tree

class Frame:
    __slots__ = ("type", "name", "parent", "children", "anchors", "props",
                 "refs", "actions", "handle", "ours", "el", "touch")

    def __init__(self, type_, name, el, ours):
        self.type = type_ or ""
        self.name = name
        self.parent = None
        self.children = []
        self.anchors = {}   # side -> (relative, pos, offset, El)
        self.props = {}     # tag -> El, last wins
        self.refs = []      # (kind, path, El): frame references resolved from this frame
        self.actions = []   # (target path, side, relative, El): runtime SetAnchor
        self.handle = None
        self.ours = ours    # created by our files (not merely edited by them)
        self.el = el
        self.touch = el if ours else None  # our El that created or last edited this frame

    def child(self, name):
        n = name.lower()
        for c in self.children:
            if c.name.lower() == n:
                return c
        return None

    def add(self, c):
        c.parent = self
        self.children.append(c)

    def clone(self):
        f = Frame(self.type, self.name, self.el, self.ours)
        f.anchors = dict(self.anchors)
        f.props = dict(self.props)
        f.refs = list(self.refs)
        f.actions = list(self.actions)
        f.handle = self.handle
        f.touch = self.touch
        for c in self.children:
            f.add(c.clone())
        return f

    def path(self):
        parts, f = [], self
        while f is not None:
            parts.append(f.name)
            f = f.parent
        return "/".join(reversed(parts))

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


# ------------------------------------------------------------------ catalog

class Catalog:
    def __init__(self):
        self.defs = {}        # (stem, name) -> El of a top-level template definition
        self.overrides = {}   # (stem, name) -> [(El, remaining path parts)]
        self.stems = set()
        self.constants = {}   # lowercase name -> value
        self.protos = {}      # (stem, name) -> built Frame, or None while building
        self.used = set()     # template keys that something instantiated
        self.handles = {}
        self.messages = {}    # dedupe: (file, line, text) -> level

    # -------------------------------------------------------------- reporting

    def report(self, level, el_or_file, line_or_text, text=None):
        if text is None:
            file, line, text = el_or_file.file, el_or_file.line, line_or_text
        else:
            file, line = el_or_file, line_or_text
        self.messages.setdefault((file, line, text), level)

    def error(self, el, text):
        if el.ours:
            self.report("error", el, text)

    def warn(self, el, text):
        if el.ours:
            self.report("warning", el, text)

    # -------------------------------------------------------------- loading

    def load_file(self, root, stem):
        self.stems.add(stem)
        for top in root.children:
            if top.tag == "constant":
                name = top.get("name")
                if name is not None:
                    self.constants[name.lower()] = top.get("val")
            elif top.tag == "frame":
                name = top.get("name")
                if not name:
                    self.error(top, "top-level Frame has no name")
                    continue
                parts = name.split("/")
                target = top.get("file")
                if target is not None:
                    key = (target.lower(), parts[0].lower())
                    self.overrides.setdefault(key, []).append((top, parts[1:]))
                elif (stem, name.lower()) in self.defs:
                    self.overrides.setdefault((stem, name.lower()), []).append((top, []))
                else:
                    self.defs[(stem, name.lower())] = top

    def const(self, value):
        if value and value.startswith("#") and not value.startswith("##"):
            return self.constants.get(value[1:].lower(), value)
        return value

    # -------------------------------------------------------------- building

    def proto(self, stem, name):
        key = (stem.lower(), name.lower())
        if key in self.protos:
            return self.protos[key]  # None here means a template cycle
        el = self.defs.get(key)
        if el is None:
            return None
        self.protos[key] = None
        tmpl = el.get("template")
        base = self.template(tmpl, el) if tmpl else None
        if base is not None:
            frame = base.clone()
            frame.name, frame.el, frame.ours = el.get("name"), el, el.ours
            frame.type = self.const(el.get("type")) or frame.type
        else:
            frame = Frame(self.const(el.get("type")), el.get("name"), el, el.ours)
        self.apply(frame, el)
        for oel, rest in self.overrides.get(key, []):
            target = frame
            for part in rest:
                nxt = target.child(part)
                if nxt is None:
                    self.error(oel, f"override path '{oel.get('name')}': no '{part}' under {target.path()}")
                    break
                target = nxt
            else:
                if oel.get("template"):
                    t = self.template(oel.get("template"), oel)
                    if t is not None:
                        self.merge(target, t)
                self.apply(target, oel)
        self.protos[key] = frame
        return frame

    def template(self, path, el):
        # Blizzard writes paths with either separator (TalentsOverviewPanel\Foo); the game accepts both.
        path = self.const(path).replace("\\", "/")
        parts = path.split("/")
        if len(parts) < 2:
            self.error(el, f"template '{path}' must be File/Frame")
            return None
        frame = self.proto(parts[0], parts[1])
        if frame is not None:
            self.used.add((parts[0].lower(), parts[1].lower()))
            for part in parts[2:]:
                frame = frame.child(part)
                if frame is None:
                    break
        if frame is None:
            self.error(el, f"template '{path}' does not exist")
        return frame

    def merge(self, dst, src):
        """Apply a template's contents onto an existing frame."""
        dst.anchors.update(src.anchors)
        dst.props.update(src.props)
        dst.refs.extend(src.refs)
        dst.actions.extend(src.actions)
        dst.handle = src.handle or dst.handle
        for sc in src.children:
            existing = dst.child(sc.name)
            if existing is not None:
                if sc.ours and sc.type and existing.type and sc.type.lower() != existing.type.lower():
                    self.warn(sc.el, f"'{sc.name}' is type {existing.type} in Blizzard's "
                                     f"{existing.path()}, not {sc.type}")
                self.merge(existing, sc)
                if sc.ours:
                    existing.touch = sc.el
            else:
                self.check_new_child(dst, sc.name, sc.el)
                dst.add(sc.clone())

    def check_new_child(self, parent, name, el):
        if el.ours and not parent.ours and not name.startswith(OUR_PREFIX):
            self.error(el, f"no frame '{name}' in Blizzard's {parent.path()} - this silently creates a "
                           f"new, empty frame. A typo or a renamed frame? (Prefix new frames {OUR_PREFIX})")

    def apply(self, frame, el):
        """Apply an XML element's children onto a frame."""
        for c in el.children:
            tag = c.tag
            if tag == "frame":
                self.apply_child_frame(frame, c)
            elif tag == "anchor":
                side = c.get("side")
                entry = (c.get("relative"), c.get("pos"), c.get("offset"), c)
                for s in ([side.lower()] if side else SIDES):
                    frame.anchors[s] = entry
            elif tag in ("animation", "stategroup"):
                self.collect(frame, c)
            elif tag == "handle":
                frame.handle = c.get("val")
            elif tag == "constant":
                if c.get("name") is not None:
                    self.constants[c.get("name").lower()] = c.get("val")
            else:
                frame.props[tag] = c
                if tag == "visible" and c.ours and not frame.ours and (c.get("val") or "").lower() == "false":
                    self.warn(c, f"Visible=false does not stick on Blizzard frames ({frame.path()}); "
                                 f"park it off-screen, or Alpha 0 if things anchor to it")
            self.collect_bindings(frame, c)

    def apply_child_frame(self, parent, c):
        name = self.const(c.get("name"))
        if not name:
            self.error(c, "Frame has no name")
            return
        parts = name.split("/")
        target = parent
        for part in parts[:-1]:
            target = target.child(part)
            if target is None:
                self.error(c, f"frame path '{name}': no '{part}' under {parent.path()}")
                return
        leaf = parts[-1]
        type_ = self.const(c.get("type"))
        tmpl = c.get("template")
        existing = target.child(leaf)
        if existing is not None:
            if c.ours and type_ and existing.type and type_.lower() != existing.type.lower():
                self.warn(c, f"'{leaf}' is type {existing.type} in Blizzard's {existing.path()}, not {type_}")
            if tmpl:
                t = self.template(tmpl, c)
                if t is not None:
                    self.merge(existing, t)
            if c.ours:
                existing.touch = c
            self.apply(existing, c)
            return
        self.check_new_child(target, leaf, c)
        base = self.template(tmpl, c) if tmpl else None
        if base is not None:
            new = base.clone()
            new.name, new.el, new.ours = leaf, c, c.ours
            new.type = type_ or new.type
            new.touch = c if c.ours else new.touch
        else:
            new = Frame(type_, leaf, c, c.ours)
        target.add(new)
        self.apply(new, c)

    def collect(self, frame, el):
        """Frame references inside an Animation or StateGroup, resolved from the owning frame."""
        for d in el.iter():
            if d.tag in ("controller", "event", "when", "action") and d.get("frame"):
                frame.refs.append((f"{d.tag} frame=", d.get("frame"), d))
            if d.tag == "action" and (d.get("type") or "").lower() == "setanchor":
                frame.actions.append((d.get("frame") or "$this", (d.get("side") or "").lower(),
                                      d.get("relative"), d))
            self.collect_bindings(frame, d, recurse=False)

    def collect_bindings(self, frame, el, recurse=False):
        for value in el.attrib.values():
            for m in re.finditer(r"\{(\$?[^{}@]+?)(?:/@[^{}]*)?\}", value):
                frame.refs.append(("binding", m.group(1), el))

    # -------------------------------------------------------------- resolving

    def resolve(self, ctx, path):
        """Resolve a frame path from ctx. Returns (frame, None) or (None, (last good frame, segment))."""
        path = self.const(path).replace("\\", "/")
        cur = ctx
        for i, seg in enumerate(path.split("/")):
            s = seg.lower()
            if s == "$parent":
                nxt = cur.parent
            elif s == "$this":
                nxt = cur
            elif s in ("$layer", "$root"):
                nxt = cur
                while nxt.parent is not None:
                    nxt = nxt.parent
            elif s.startswith("$ancestor"):
                m = re.match(r"\$ancestor\[@(type|name|oftype)=([^\]]+)\]", seg, re.I)
                nxt = cur.parent
                while nxt is not None and m:
                    value = nxt.name if m.group(1).lower() == "name" else nxt.type
                    if value.lower() == m.group(2).lower():
                        break
                    nxt = nxt.parent
            elif s.startswith("$sibling"):
                m = re.match(r"\$sibling([+-]\d+)$", s)
                nxt = None
                if m and cur.parent is not None:
                    sibs = cur.parent.children
                    idx = next(j for j, f in enumerate(sibs) if f is cur) + int(m.group(1))
                    nxt = sibs[idx] if 0 <= idx < len(sibs) else None
            elif s.startswith("$"):
                nxt = self.handles.get(s[1:]) if i == 0 else None
            else:
                nxt = cur.child(seg)
            if nxt is None:
                return None, (cur, seg)
            cur = nxt
        return cur, None

    def check_ref(self, ctx, kind, path, el):
        if path is None:
            return None
        target, fail = self.resolve(ctx, path)
        if target is None:
            at, seg = fail
            text = (f"{kind} '{path}' resolves to nothing: no '{seg}' from {at.path()} "
                    f"(this frame: {ctx.path()})")
            # List frames create their Item children at runtime; those cannot be seen statically.
            if not seg.startswith("$") and "list" in at.type.lower():
                self.warn(el, text + " - may be a runtime list item")
            else:
                self.error(el, text)
        return target


# ------------------------------------------------------------------ the checks

def offset_value(cat, off):
    try:
        return int(cat.const(off))
    except (TypeError, ValueError):
        return None


def check_raw(cat, root):
    """Checks that need only our XML, not the merged tree."""
    for el in root.iter():
        for key, value in el.attrib.items():
            if value.startswith("#") and not value.startswith("##"):
                if value[1:].lower() not in cat.constants:
                    cat.error(el, f"constant '{value}' is never defined")
            elif re.search(r"\S#[A-Za-z_]", value) or re.search(r"\s#[A-Za-z_]", value):
                cat.warn(el, f"'{value}': a #Constant only substitutes as the ENTIRE value")
        if el.tag == "anchor":
            side, pos, off = el.get("side"), el.get("pos"), el.get("offset")
            if side is not None and side.lower() not in SIDES:
                cat.error(el, f"Anchor side '{side}' is not Top/Bottom/Left/Right")
            if pos is not None and cat.const(pos).lower() not in POSITIONS:
                cat.error(el, f"Anchor pos '{pos}' is not Min/Mid/Max")
            if off is not None and offset_value(cat, off) is None:
                cat.error(el, f"Anchor offset '{off}' is not a whole number")
            if el.get("relative") is None:
                cat.error(el, "Anchor has no relative=")


def check_tree(cat, root):
    parked = {}  # id(frame) -> El that parked it
    for f in root.walk():
        if f.handle:
            cat.handles.setdefault(f.handle.lower(), f)
    for f in root.walk():
        for side, (rel, pos, off, el) in f.anchors.items():
            if el.ours:
                cat.check_ref(f, "Anchor relative", rel, el)
                v = offset_value(cat, off)
                if v is not None and abs(v) >= PARK_THRESHOLD:
                    parked.setdefault(id(f), f.touch or el)
        for kind, path, el in f.refs:
            if el.ours:
                cat.check_ref(f, kind, path, el)
        for tpath, side, rel, el in f.actions:
            if el.ours:
                target = cat.check_ref(f, "SetAnchor frame=", tpath, el)
                if target is not None and rel:
                    cat.check_ref(target, "SetAnchor relative", rel, el)
        cam = f.props.get("coloradjustmode")
        if cam is not None and cam.ours and (cam.get("val") or "").lower() == "fill" \
                and "adjustmentcolor" not in f.props:
            cat.warn(cam, f"ColorAdjustMode Fill reads AdjustmentColor (A,R,G,B), which {f.name} "
                          f"does not set - it will fill with nothing")

    # Frames outside a parked subtree that anchor into it get dragged off-screen too.
    parked_by = {}
    for f in root.walk():
        if id(f) in parked:
            for d in f.walk():
                parked_by.setdefault(id(d), (f, parked[id(f)]))
    for f in root.walk():
        if id(f) in parked_by:
            continue
        dragged = {}  # parked owner -> sides of f that point into it
        for side in ("top", "bottom", "left", "right"):
            rel = f.anchors.get(side, (None,))[0]
            if rel is None:
                continue
            target, _ = cat.resolve(f, rel)
            if target is not None and id(target) in parked_by:
                owner, park_el = parked_by[id(target)]
                dragged.setdefault(id(owner), (owner, park_el, target, []))[3].append(side.title())
        for owner, park_el, target, sides in dragged.values():
            cat.warn(park_el, f"parking {owner.name} drags {f.path()} with it ({'/'.join(sides)} "
                              f"anchored to {target.name}). If you want {f.name}, hide {owner.name} "
                              f"with Alpha 0 instead, or re-anchor {f.name}")

    # Sides we anchor that Blizzard re-anchors at runtime.
    for f in root.walk():
        for tpath, side, rel, el in f.actions:
            if el.ours or not side:
                continue
            target, _ = cat.resolve(f, tpath)
            if target is None:
                continue
            ours = target.anchors.get(side)
            if ours is not None and ours[3].ours:
                cat.warn(ours[3], f"Blizzard re-anchors {target.name}'s {side.title()} side at runtime "
                                  f"(SetAnchor at {el.file}:{el.line}) - this anchor may not hold")


def check_desc_index(cat, source, layout_dir, includes, index_el):
    listed = set()
    for inc in includes:
        path = inc.get("path") or ""
        listed.add(path.lower())
        if not (source / path).is_file() and not _find_ci(source, path):
            cat.error(inc, f"DescIndex includes '{path}', which does not exist")
    for p in sorted(layout_dir.rglob("*.StormLayout")):
        rel = p.relative_to(source).as_posix()
        if p.name.lower() != "descindex.stormlayout" and rel.lower() not in listed:
            cat.report("warning", index_el.file, index_el.line,
                       f"{rel} is not included by DescIndex, so the game never loads it")


def _find_ci(root, rel):
    cur = root
    for part in rel.replace("\\", "/").split("/"):
        match = next((c for c in cur.iterdir() if c.name.lower() == part.lower()), None) \
            if cur.is_dir() else None
        if match is None:
            return None
        cur = match
    return cur


# ------------------------------------------------------------------ driver

def load_base(cat):
    count = 0
    # the per-hero and per-map mods too (heromods/<hero>.stormmod, heroesmapmods/
    # battlegroundmapmods/<map>.stormmod): their layout files can be overridden by name
    # (file="Tracer" - Tracer's Pulse Bomb meter, inspect_card.tracer_charge; file=
    # "FieldofSlaughter" - Towers of Doom's alerts; every map's panel, FCJH_Maps)
    extra = sorted(p.relative_to(MODS).as_posix() for p in (MODS / "heromods").glob("*.stormmod")) + \
        sorted(p.relative_to(MODS).as_posix() for p in (MODS / "heroesmapmods" / "battlegroundmapmods").glob("*.stormmod"))
    for mod in BASE_MODS + extra:
        data = MODS / mod / "base.stormdata"
        index = data / "ui" / "layout" / "descindex.stormlayout"
        if mod in extra and not index.is_file():
            continue   # a hero or map mod with no UI of its own
        root, err = parse_xml(index, str(index), ours=False)
        if root is None:
            raise SystemExit(f"cannot read base DescIndex {index}: {err}")
        for inc in root.children:
            if inc.tag != "include":
                continue
            path = data / inc.get("path").lower().replace("\\", "/")
            if not path.is_file():
                continue  # Blizzard-only files the extract does not carry
            file_root, err = parse_xml(path, path.relative_to(MODS).as_posix(), ours=False)
            if file_root is not None:
                cat.load_file(file_root, path.stem.lower())
                count += 1
    return count


def validate(source=DEFAULT_SOURCE):
    """Returns (errors, warnings, lines) for the interface folder."""
    source = Path(source).resolve()
    if not MODS.is_dir():
        raise SystemExit(f"base UI extract missing: {MODS} - clone jamiephan/HeroesOfTheStorm_Gamedata")
    cat = Catalog()
    load_base(cat)

    layout_dir = source / "Base.StormData" / "UI" / "Layout"
    index_path = layout_dir / "DescIndex.StormLayout"
    display = lambda p: p.relative_to(REPO).as_posix() if p.is_relative_to(REPO) else str(p)
    index_root, err = parse_xml(index_path, display(index_path), ours=True)
    ours = []
    if index_root is None:
        cat.report("error", display(index_path), err[0], err[1])
    else:
        includes = [i for i in index_root.children if i.tag == "include"]
        check_desc_index(cat, source, layout_dir, includes, index_root)
        for inc in includes:
            path = _find_ci(source, inc.get("path") or "")
            if path is None:
                continue
            root, err = parse_xml(path, display(path), ours=True)
            if root is None:
                cat.report("error", display(path), err[0], err[1])
                continue
            cat.load_file(root, path.stem.lower())
            ours.append((root, path.stem.lower()))

    for root, stem in ours:
        check_raw(cat, root)
        for top in root.children:
            if top.tag == "frame" and top.get("file") is not None:
                if top.get("file").lower() not in cat.stems:
                    cat.error(top, f"file='{top.get('file')}' names no known layout file")
                elif (top.get("file").lower(), top.get("name").split("/")[0].lower()) not in cat.defs:
                    cat.error(top, f"no '{top.get('name')}' in layout '{top.get('file')}' to override")

    game_ui = cat.proto("GameUI", "GameUI")
    if game_ui is None:
        raise SystemExit("base UI has no GameUI/GameUI - is the JamiePhan extract intact?")
    check_tree(cat, game_ui)

    for root, stem in ours:
        for top in root.children:
            if top.tag == "frame" and top.get("file") is None and top.get("name") \
                    and (stem, top.get("name").lower()) not in cat.used:
                cat.report("note", top, f"template '{top.get('name')}' is never used")

    order = {"error": 0, "warning": 1, "note": 2}
    items = sorted(cat.messages.items(), key=lambda kv: (kv[0][0], kv[0][1], order[kv[1]]))
    lines = [f"{file}:{line}: {level}: {text}" for (file, line, text), level in items]
    errors = sum(1 for level in cat.messages.values() if level == "error")
    warnings = sum(1 for level in cat.messages.values() if level == "warning")
    return errors, warnings, lines, (cat, game_ui)


def show(cat, root, path):
    frame, fail = cat.resolve(root, "/".join(path.split("/")[1:])) if "/" in path else (root, None)
    if frame is None:
        print(f"no such frame: {path} (stopped at '{fail[1]}' under {fail[0].path()})")
        return

    def dump(f, depth):
        who = "ours" if f.ours else "blizz"
        print(f"{'  ' * depth}{f.name}  [{f.type}] ({who})")
        for side in ("top", "bottom", "left", "right"):
            if side in f.anchors:
                rel, pos, off, el = f.anchors[side]
                src = "ours" if el.ours else "blizz"
                print(f"{'  ' * depth}    {side:<6} -> {rel} {pos} {off}  ({src} {el.file}:{el.line})")
        for c in f.children:
            dump(c, depth + 1)

    dump(frame, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--show", metavar="FRAME_PATH",
                        help="print the merged frame tree under this path, e.g. GameUI/UIContainer")
    args = parser.parse_args()
    errors, warnings, lines, (cat, game_ui) = validate(args.source)
    if args.show:
        show(cat, game_ui, args.show)
        return 0
    print("\n".join(lines))
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
