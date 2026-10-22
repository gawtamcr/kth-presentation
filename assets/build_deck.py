#!/usr/bin/env python3
"""Build the STL-FM defence deck on the KTH PowerPoint template.

The template is `assets/kth_template.potx` (KTH PPT template 251203), which is read and never
modified. Every slide is created from a template layout and written from the specifications
below, with its speaker notes. The output is `STL-FM Defense.pptx`. Display equations are the
images that `make_math.py` typesets from the thesis LaTeX; run it first after changing one.

Usage:  python3 build_deck.py
        PPTX_SKILL=<pptx skill dir> python3 build_deck.py   (path of add_slide.py/clean.py)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

HERE = Path(__file__).resolve().parent
PPT = HERE.parent
THESIS = PPT.parent / "kth-thesis"
FIGS = THESIS / "figures"
SRC = HERE / "kth_template.potx"
OUT = PPT / "STL-FM Defense.pptx"
SKILL = Path(os.environ.get(
    "PPTX_SKILL",
    "/home/gawtam_wsl/.claude/skills/synced/"
    "c18127dd-13d5-4974-aa99-1aba286ebf46_2e881403-ff96-49f9-9581-606d714d8f37/pptx"))
sys.path.insert(0, str(SKILL / "scripts"))
import add_slide  # noqa: E402

EMU = 914400
# KTH template layouts: Title KTH blue, Headline only, Title/chapter light blue, Logo
LAYOUT_COVER, LAYOUT_CONTENT = "slideLayout1.xml", "slideLayout35.xml"
LAYOUT_DIVIDER, LAYOUT_END = "slideLayout4.xml", "slideLayout43.xml"

# thesis figure palette (fig_system_pipeline.tex, fig_transport.tex)
BLUE, CYAN, PINK, GREEN, GREY = "1954A6", "24A0D8", "D85497", "B0C92B", "63666A"
INK, MUTED, LIGHT, FAINT = "262626", "6E6E6E", "A9A9A9", "F0F0F0"
# KTH palette (template theme), used for the chrome only
KTH_BLUE, KTH_GREY = "004791", "A5A5A5"


def tint(hex_c, pct, base="FFFFFF"):
    a = [int(hex_c[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x * pct / 100 + y * (1 - pct / 100)):02X}" for x, y in zip(a, b))


GREEN_D = tint(GREEN, 70, "000000")


def emu(v):
    return int(round(v * EMU))


# ───────────────────────────── figure assets ─────────────────────────────
def pdf_png(rel, dpi=600):
    """Render a thesis PDF figure to PNG in assets/, again whenever the PDF is newer than the PNG."""
    out = HERE / (Path(rel).stem + ".png")
    if not out.exists() or out.stat().st_mtime < (FIGS / rel).stat().st_mtime:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile",
                        str(FIGS / rel), str(out.with_suffix(""))], check=True)
    return out


# ───────────────────────────── XML builders ─────────────────────────────
class Slide:
    def __init__(self, layout=LAYOUT_CONTENT):
        self.layout = layout
        self.shapes = []
        self.media = []          # (rId, type, target)
        self.next_id = 10
        self.clicks = []         # list of lists of (kind, spid, extra)
        self.videos = []
        self.pending_media = []
        self.notes = ""

    def nid(self):
        self.next_id += 1
        return self.next_id

    def rel(self, kind, target):
        rid = f"rId{len(self.media) + 2}"
        self.media.append((rid, kind, target))
        return rid

    def add(self, xml, click=None, is_sp=True, play=None):
        """Add a shape; with `click`, it appears on that click, or with `play` (ms) a video plays."""
        self.shapes.append(xml)
        sid = int(re.search(r'<p:cNvPr id="(\d+)"', xml).group(1))
        if click is not None:
            while len(self.clicks) <= click:
                self.clicks.append([])
            self.clicks[click].append(("play", sid, play) if play else ("appear", sid, is_sp))
        if play:
            self.videos.append(sid)
        return sid


def runs(text, size=16, color=INK, bold=False, italic=False):
    """Plain text, or a list of (text, opts) with opts keys size/color/bold/italic/sub/sup/math."""
    parts = text if isinstance(text, list) else [(text, {})]
    out = []
    for t, o in parts:
        sz = o.get("size", size)
        attrs = f'lang="en-GB" sz="{int(sz * 100)}"'
        if o.get("bold", bold):
            attrs += ' b="1"'
        if o.get("italic", italic):
            attrs += ' i="1"'
        if o.get("sub"):
            attrs += ' baseline="-25000"'
        if o.get("sup"):
            attrs += ' baseline="30000"'
        font = ('<a:latin typeface="Cambria Math"/><a:ea typeface="Cambria Math"/>'
                '<a:cs typeface="Cambria Math"/><a:sym typeface="Cambria Math"/>') if o.get("math") else ""
        out.append(f'<a:r><a:rPr {attrs} dirty="0"><a:solidFill><a:srgbClr val="{o.get("color", color)}"/>'
                   f'</a:solidFill>{font}</a:rPr><a:t>{escape(t)}</a:t></a:r>')
    return "".join(out)


def para(text, align="l", gap=0, **kw):
    """One paragraph; `gap` is the space before it, in points."""
    ppr = (f'<a:pPr algn="{align}"><a:spcBef><a:spcPts val="{int(gap * 100)}"/></a:spcBef></a:pPr>' if gap
           else f'<a:pPr algn="{align}"/>')
    return f'<a:p>{ppr}{runs(text, **kw)}</a:p>'


def xfrm(x, y, w, h, flip=""):
    return f'<a:xfrm{flip}><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'


def ph_title(s, text, geom=None, size=None, color=None, ph="title"):
    sp_pr = f"<p:spPr>{xfrm(*geom)}</p:spPr>" if geom else "<p:spPr/>"
    sz = f' sz="{int(size * 100)}"' if size else ""
    fill = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ""
    rpr = f'<a:rPr lang="en-GB"{sz} dirty="0">{fill}</a:rPr>' if fill else f'<a:rPr lang="en-GB"{sz} dirty="0"/>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{s.nid()}" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/>'
            f'</p:cNvSpPr><p:nvPr><p:ph type="{ph}"/></p:nvPr></p:nvSpPr>{sp_pr}<p:txBody><a:bodyPr/>'
            f'<a:lstStyle/><a:p><a:r>{rpr}<a:t>{escape(text)}</a:t></a:r></a:p>'
            f'</p:txBody></p:sp>')


def ph_body(s, idx, paras, name="Subtitle", geom=None, size=None, ph="body"):
    sz = f' sz="{int(size * 100)}"' if size else ""
    body = "".join(f'<a:p><a:r><a:rPr lang="en-GB"{sz} dirty="0"/><a:t>{escape(p)}</a:t></a:r></a:p>'
                   for p in paras)
    sp_pr = f"<p:spPr>{xfrm(*geom)}</p:spPr>" if geom else "<p:spPr/>"
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{s.nid()}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/>'
            f'</p:cNvSpPr><p:nvPr><p:ph type="{ph}" idx="{idx}"/></p:nvPr></p:nvSpPr>'
            f'{sp_pr}<p:txBody><a:bodyPr/><a:lstStyle/>{body}</p:txBody></p:sp>')


def footer(s):
    """The slide-number placeholder; the KTH layouts carry it as sldNum idx 12."""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{s.nid()}" name="Slide Number"/><p:cNvSpPr><a:spLocks noGrp="1"/>'
            f'</p:cNvSpPr><p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr><p:spPr/>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{{619F89D8-7AE3-494A-97F3-03D680869632}}" '
            f'type="slidenum"><a:rPr lang="en-GB"/><a:t>1</a:t></a:fld><a:endParaRPr lang="en-GB"/></a:p>'
            f'</p:txBody></p:sp>')


def box(s, x, y, w, h, text, fill, line, size=16, color=INK, bold=False, radius=8000,
        lw=1.25, dash=False, name="Box", align="ctr", italic=False, geom="roundRect"):
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    ln_xml = (f'<a:ln w="{emu(lw / 72)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>'
              + ('<a:prstDash val="dash"/>' if dash else "") + "</a:ln>") if line else "<a:ln><a:noFill/></a:ln>"
    paras = text if isinstance(text, tuple) else (text,)
    body = "".join(para(p, align=align, size=size, color=color, bold=bold, italic=italic) for p in paras)
    av = f'<a:avLst><a:gd name="adj" fmla="val {radius}"/></a:avLst>' if geom == "roundRect" else "<a:avLst/>"
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{s.nid()}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>{xfrm(x, y, w, h)}<a:prstGeom prst="{geom}">{av}</a:prstGeom>{fill_xml}{ln_xml}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="64008" tIns="27432" rIns="64008" bIns="27432" '
            f'anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>')


def label(s, x, y, w, h, text, size=14, color=MUTED, italic=False, bold=False, align="l",
          anchor="t", fill=None, name="Label", gap=0):
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    paras = text if isinstance(text, tuple) else (text,)
    body = "".join(para(p, align=align, gap=gap if i else 0, size=size, color=color, italic=italic, bold=bold)
                   for i, p in enumerate(paras))
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{s.nid()}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>{xfrm(x, y, w, h)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="45720" tIns="0" rIns="45720" bIns="0" anchor="{anchor}">'
            f'<a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>')


def arrow(s, x1, y1, x2, y2, color=GREY, lw=1.75, head=True, name="Arrow"):
    flip = (' flipH="1"' if x2 < x1 else "") + (' flipV="1"' if y2 < y1 else "")
    tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if head else ""
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{s.nid()}" name="{name}"/><p:cNvCxnSpPr/><p:nvPr/>'
            f'</p:nvCxnSpPr><p:spPr>{xfrm(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1), flip)}'
            f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom><a:ln w="{emu(lw / 72)}">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{tail}</a:ln></p:spPr></p:cxnSp>')


def rule(s, x1, x2, y, color="D2D2D2", lw=0.75):
    """A horizontal table rule."""
    return arrow(s, x1, y, x2, y, color=color, lw=lw, head=False, name="Rule")


def picture(s, path, x, y, w, h, descr, name="Figure"):
    rid = s.rel("image", f"../media/{path.name}")
    s.pending_media.append(path)
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{s.nid()}" name="{name}" descr="{escape(descr)}"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr>{xfrm(x, y, w, h)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def video(s, mp4, poster, x, y, w, h, descr, name="Video"):
    """An embedded video with a poster frame."""
    vid = s.rel("video", f"../media/{mp4.name}")
    med = s.rel("http://schemas.microsoft.com/office/2007/relationships/media", f"../media/{mp4.name}")
    img = s.rel("image", f"../media/{poster.name}")
    s.pending_media += [mp4, poster]
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{s.nid()}" name="{name}" descr="{escape(descr)}">'
            f'<a:hlinkClick r:id="" action="ppaction://media"/></p:cNvPr><p:cNvPicPr>'
            f'<a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr><a:videoFile r:link="{vid}"/><p:extLst>'
            f'<p:ext uri="{{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}}"><p14:media xmlns:p14="http://schemas.'
            f'microsoft.com/office/powerpoint/2010/main" r:embed="{med}"/></p:ext></p:extLst></p:nvPr>'
            f'</p:nvPicPr><p:blipFill><a:blip r:embed="{img}"/><a:stretch><a:fillRect/></a:stretch>'
            f'</p:blipFill><p:spPr>{xfrm(x, y, w, h)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'</p:spPr></p:pic>')


def fit(path, x, y, w, h):
    """Largest rectangle of the image's aspect inside (x, y, w, h), centred."""
    iw, ih = Image.open(path).size
    sc = min(w / iw, h / ih)
    fw, fh = iw * sc, ih * sc
    return x + (w - fw) / 2, y + (h - fh) / 2, fw, fh


def timing(s):
    """Click sequence: appear effects and video plays, plus a media node per video."""
    if not s.clicks:
        return ""
    ctn = [2]

    def nxt():
        ctn[0] += 1
        return ctn[0]
    pars = []
    for group in s.clicks:
        effects = []
        for i, (kind, sid, extra) in enumerate(group):
            node = "clickEffect" if i == 0 else "withEffect"
            if kind == "appear":
                effects.append(
                    f'<p:par><p:cTn id="{nxt()}" presetID="1" presetClass="entr" presetSubtype="0" '
                    f'fill="hold" grpId="0" nodeType="{node}"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                    f'<p:childTnLst><p:set><p:cBhvr><p:cTn id="{nxt()}" dur="1" fill="hold"><p:stCondLst>'
                    f'<p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
                    f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                    f'<p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par>')
            else:
                effects.append(
                    f'<p:par><p:cTn id="{nxt()}" presetID="1" presetClass="mediacall" presetSubtype="0" '
                    f'fill="hold" nodeType="{node}"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                    f'<p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="{nxt()}" '
                    f'dur="{extra}" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr>'
                    f'</p:cmd></p:childTnLst></p:cTn></p:par>')
        a, b = nxt(), nxt()
        pars.append(f'<p:par><p:cTn id="{a}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
                    f'</p:stCondLst><p:childTnLst><p:par><p:cTn id="{b}" fill="hold"><p:stCondLst>'
                    f'<p:cond delay="0"/></p:stCondLst><p:childTnLst>{"".join(effects)}</p:childTnLst>'
                    f'</p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    media = []
    for sid in s.videos:
        media.append(
            f'<p:video><p:cMediaNode vol="80000"><p:cTn id="{nxt()}" fill="hold" display="0"><p:stCondLst>'
            f'<p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
            f'</p:cMediaNode></p:video>')
        a, b, c, d, e = nxt(), nxt(), nxt(), nxt(), nxt()
        media.append(
            f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="{a}" restart="whenNotActive" fill="hold" '
            f'evtFilter="cancelBubble" nodeType="interactiveSeq"><p:stCondLst><p:cond evt="onClick" delay="0">'
            f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cond></p:stCondLst><p:endSync evt="end" delay="0">'
            f'<p:rtn val="all"/></p:endSync><p:childTnLst><p:par><p:cTn id="{b}" fill="hold"><p:stCondLst>'
            f'<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{c}" fill="hold"><p:stCondLst>'
            f'<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{d}" presetID="2" '
            f'presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst>'
            f'<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="togglePause"><p:cBhvr>'
            f'<p:cTn id="{e}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr>'
            f'</p:cmd></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
            f'</p:par></p:childTnLst></p:cTn><p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl>'
            f'<p:spTgt spid="{sid}"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>')
    bld = "".join(f'<p:bldP spid="{sid}" grpId="0"/>' for g in s.clicks for kind, sid, is_sp in g
                  if kind == "appear" and is_sp)
    return (f'<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" '
            f'nodeType="mainSeq"><p:childTnLst>{"".join(pars)}</p:childTnLst></p:cTn><p:prevCondLst>'
            f'<p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>'
            f'</p:nextCondLst></p:seq>{"".join(media)}</p:childTnLst></p:cTn></p:par></p:tnLst>'
            + (f'<p:bldLst>{bld}</p:bldLst>' if bld else "") + '</p:timing>')


def slide_xml(s):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>'
            '<a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
            f'</a:xfrm></p:grpSpPr>{"".join(s.shapes)}</p:spTree></p:cSld><p:clrMapOvr>'
            f'<a:masterClrMapping/></p:clrMapOvr>{timing(s)}</p:sld>')


# ───────────────────────────── content area ─────────────────────────────
CX, CW = 0.66, 12.02          # content x and width (master body placeholder)
TOP, BOTTOM = 2.05, 6.90      # usable vertical band below the 36 pt heading at y 1.20
SECTIONS = ["Motivation", "Background", "Method", "Results", "Conclusions"]


def progress(s, section):
    """The section bar to the right of the KTH logo, current section in KTH blue."""
    parts = []
    for i, name in enumerate(SECTIONS):
        if i:
            parts.append(("    →    ", {"color": KTH_GREY}))
        parts.append((name, {"color": KTH_BLUE if name == section else KTH_GREY, "bold": name == section}))
    s.add(label(s, 1.40, 0.40, 11.28, 0.32, parts, size=13, align="r", anchor="ctr", name="Progress"))


def content(title, section=None, subtitle=None, backup=False):
    """A headline-only slide; backup slides have grey headings and no section bar."""
    s = Slide()
    s.add(ph_title(s, title, color=MUTED if backup else None))
    if section:
        progress(s, section)
    if subtitle:
        s.add(label(s, CX, 1.86, CW, 0.36, subtitle, size=18, color=MUTED, name="Subtitle"))
    s.add(footer(s))
    return s


def claim(s, text, y=6.45):
    """The one-sentence result of a results slide, under its evidence."""
    s.add(label(s, CX, y, CW, 0.40, text, size=18, color=INK, align="ctr", anchor="ctr", name="Claim"))


def cite(s, text, y=6.66):
    """Author-year sources of a background slide, bottom left."""
    s.add(label(s, CX, y, CW, 0.26, text, size=11, color=MUTED, name="Citation"))


def eqimg(s, name, x, y, scale=1.0, align="l", descr=None, click=None):
    """A display equation from make_math.py at its natural size (600 dpi), times `scale`."""
    path = HERE / f"eq_{name}.png"
    iw, ih = Image.open(path).size
    w, h = iw / 600 * scale, ih / 600 * scale
    x = x - w / 2 if align == "c" else x - w if align == "r" else x
    s.add(picture(s, path, x, y, w, h, descr or f"Equation: {name}", name="Equation"), click=click, is_sp=False)
    return w, h


def callout(s, x, y, w, h, tag, lines, color, size=18):
    """A research-question box: tinted fill, a coloured bar on the left, a tag and the text."""
    s.add(box(s, x, y, w, h, "", tint(color, 9), None, radius=0, geom="rect", name="Callout"))
    s.add(box(s, x, y, 0.07, h, "", color, None, radius=0, geom="rect", name="Callout bar"))
    s.add(label(s, x + 0.25, y, 1.30, h, tag, size=size, color=tint(color, 80, "000000"), bold=True,
                anchor="ctr", name="Callout tag"))
    s.add(label(s, x + 1.60, y, w - 1.75, h, lines, size=size, color=INK, anchor="ctr", name="Callout text"))


# ───────────────────────────── roadmap (simplified Fig. 5.1) ─────────────────────────────
ROAD_GROUPS = {"prior": ["demo", "train", "prior"], "req": ["phi", "comp", "score"],
               "sampler": ["samp"], "plan": ["plan", "exec"]}


def roadmap(s, highlight=None):
    """The system pipeline of the thesis, simplified, in the content band. `highlight` greys out every
    other group, for the section roadmap slides."""
    on = set(sum((ROAD_GROUPS[g] for g in (highlight or ROAD_GROUPS)), []))
    k = CW / 12.45
    X = lambda x: CX + (x - 0.45) * k          # noqa: E731  (drawn on a 0.45..12.90 grid)
    Y = lambda y: y + 0.15                     # noqa: E731

    def b(key, x, y, w, h, text, c, strong=False):
        fill, line, tc = (tint(c, 22 if strong else 8), c, INK) if key in on else (FAINT, "D2D2D2", LIGHT)
        s.add(box(s, X(x), Y(y), w * k, h, text, fill, line, size=16, color=tc, lw=1.5, name=key))

    def band(x, y, w, h, text):
        s.add(box(s, X(x), Y(y), w * k, h, "", None, tint(GREY, 60), lw=0.75, dash=True, radius=3000,
                  name="Band"))
        s.add(label(s, X(x) + 0.25, Y(y) - 0.14, 0.3 + 0.09 * len(text), 0.28, text, size=12, fill="FFFFFF",
                    name="Band label"))

    def a(x1, y1, x2, y2, key, c):
        s.add(arrow(s, X(x1), Y(y1), X(x2), Y(y2), color=c if key in on else "D2D2D2", lw=2))

    band(0.45, 1.95, 9.15, 1.15, "Offline, once")
    band(0.45, 3.40, 9.15, 1.15, "Per requirement, at inference")
    band(9.85, 1.95, 3.05, 4.75, "Per instance")
    b("demo", 0.70, 2.18, 2.50, 0.70, "Demonstrations", BLUE)
    b("train", 3.75, 2.18, 2.50, 0.70, "Flow-matching training", BLUE)
    b("prior", 6.80, 2.18, 2.50, 0.70, "Learned prior", BLUE, strong=True)
    b("phi", 0.70, 3.63, 2.50, 0.70, [("STL requirement ", {}), ("φ", {"italic": True})], PINK)
    b("comp", 3.75, 3.63, 2.50, 0.70, "Compiler", PINK)
    b("score", 6.80, 3.63, 2.50, 0.70, [("Robustness score ", {}), ("ρ", {"italic": True})], PINK, strong=True)
    b("samp", 10.10, 2.18, 2.55, 2.15, "Guided sampler", CYAN, strong=True)
    b("plan", 10.10, 4.78, 2.55, 0.62, "Plan", CYAN)
    b("exec", 10.10, 5.85, 2.55, 0.62, "Execution", GREEN)
    a(3.20, 2.53, 3.75, 2.53, "train", BLUE); a(6.25, 2.53, 6.80, 2.53, "prior", BLUE)
    a(3.20, 3.98, 3.75, 3.98, "comp", PINK); a(6.25, 3.98, 6.80, 3.98, "score", PINK)
    a(9.30, 2.53, 10.10, 2.53, "samp", BLUE); a(9.30, 3.98, 10.10, 3.98, "samp", PINK)
    a(11.375, 4.33, 11.375, 4.78, "plan", CYAN); a(11.375, 5.40, 11.375, 5.85, "exec", GREEN)


def section_roadmap(title, section, group, notes):
    """A roadmap slide that opens a part of the talk, with its group of the pipeline highlighted."""
    s = content(title, section)
    roadmap(s, highlight=[group])
    s.notes = notes
    return s


# ───────────────────────────── the slides ─────────────────────────────
def slides():
    out = []
    M = {"math": True}
    SUB = {"sub": True}

    # ── Motivation ──
    # title
    s = Slide(LAYOUT_COVER)
    s.add(ph_title(s, "STL-FM: Trajectory Planning Through STL-Guided Flow Matching", ph="ctrTitle",
                   geom=(1.00, 3.35, 11.33, 1.25), size=32))
    s.add(label(s, 1.00, 4.62, 11.33, 0.40,
                "Imposing temporal requirements on a generative motion prior at inference time",
                size=19, color="DEF0FF", align="ctr", name="Thesis subtitle"))
    s.add(ph_body(s, 1, ["Gawtam Chithra Ramesh"], ph="subTitle", geom=(2.33, 5.20, 8.67, 0.42), size=20))
    s.add(label(s, 2.33, 5.72, 8.67, 1.10,
                ("Master’s thesis defence, carried out at ABB Robotics",
                 "Examiner: Dimos V. Dimarogonas",
                 "Supervisors: Luzia Knödler, Shaohang Han, Matthew Lock and Jonathan Styrud"),
                size=13, color="FFFFFF", align="ctr", name="Credits"))
    s.notes = ("A robot learns its motion from demonstrations. This thesis imposes a requirement on "
               "that learned motion afterwards, at inference, without retraining.")
    out.append(s)

    # the ABB example (the author's slide; photo and quote from the ABB customer story)
    s = content("Adhesive bonding with an ABB YuMi", "Motivation")
    img = HERE / "abb_yumi_ge_healthcare.png"
    px, py, pw, ph = fit(img, 9.00, TOP, 3.68, 4.45)
    s.add(picture(s, img, px, py, pw, ph, "Single-arm YuMi holding a part under a glue dispenser"), is_sp=False)
    s.add(label(s, px - 0.30, py + ph + 0.06, pw + 0.60, 0.40,
                ("Photo and quote: ABB customer story,", "GE Healthcare, Helsinki"), size=11, align="ctr"))
    s.add(label(s, CX, 2.30, 8.0, 0.95, ("A single-arm YuMi applies a bead of fast-setting glue", "to a prototype part."),
                size=20, color=INK))
    s.add(label(s, CX, 3.40, 8.0, 0.95, ("The part changes on a rapid schedule,", "so the program changes with it."),
                size=20, color=INK))
    s.add(label(s, CX, 4.70, 8.0, 0.95, "“Even in half an hour, we can get some major changes done to the code.”",
                size=20, color=GREY, italic=True))
    s.notes = ("A real cell from ABB. At GE Healthcare in Helsinki a single-arm YuMi picks a prototype component from a "
               "jig, applies a bead of fast-setting glue that is hard to apply by hand, and returns the part. The "
               "prototypes change on a rapid schedule. The customer's own words: even in half an hour they can get "
               "major changes done to the code. Every change of the product or the process requires a change of the "
               "program. [ABB customer story, IRB 14050 at GE Healthcare]")
    out.append(s)

    # today's practice, built up click by click
    s = content("Current practice", "Motivation")
    OK_C, BAD_C = tint(GREEN, 70, "000000"), PINK

    def panel(k, head, sub, axis, click):
        x0 = CX + 4.12 * k
        for x in [label(s, x0, 2.17, 3.85, 0.34, head, size=17, color=INK, bold=True),
                  label(s, x0, 2.51, 3.85, 0.30, sub, size=13),
                  arrow(s, x0, 5.30, x0 + 3.75, 5.30, color=GREY, lw=1.25),
                  label(s, x0 + 2.75, 5.35, 1.0, 0.28, axis, size=12, align="r")]:
            s.add(x, click=click, is_sp=not x.startswith("<p:cxnSp"))
        return x0

    def band(x0, a, b, col, text, click, dashed=False):
        x = box(s, x0 + a, 3.15, b - a, 2.10, "", None if dashed else tint(col, 22), col if dashed else None,
                lw=1.0, dash=dashed, radius=0, name="Band")
        s.add(x, click=click)
        s.add(label(s, x0 + a - 0.30, 2.87, b - a + 0.60, 0.26, text, size=11, color=col, align="ctr"), click=click)

    def row(x0, y, a, b, ok, note, click):
        col = OK_C if ok else BAD_C
        for x in [arrow(s, x0, y, x0 + 3.55, y, color="D2D2D2", lw=0.75, head=False),
                  box(s, x0 + a, y - 0.09, b - a, 0.18, "", col, None, radius=50000, name="Bar"),
                  label(s, x0 + 3.50, y - 0.20, 0.40, 0.40, "✓" if ok else "✗", size=16, color=col,
                        align="ctr", anchor="ctr"),
                  label(s, x0, y + 0.12, 3.5, 0.28, note, size=12, color=col)]:
            s.add(x, click=click, is_sp=not x.startswith("<p:cxnSp"))

    x0 = panel(0, "Adhesive A", "taught once, then replayed", "time", None)
    band(x0, 1.10, 1.90, CYAN, "open time", None)
    row(x0, 3.30, 1.40, 3.00, True, "run 1", None)
    row(x0, 4.00, 1.40, 3.00, True, "run 2, identical", 0)
    row(x0, 4.70, 1.40, 3.00, True, "run 3, identical", 0)
    x1 = panel(1, "Adhesive B, faster curing", "same program", "time", 1)
    band(x1, 0.45, 1.05, CYAN, "open time", 1)
    row(x1, 3.30, 1.40, 3.00, False, "seated too late", 1)
    row(x1, 4.10, 0.60, 2.20, True, "timing reprogrammed", 2)
    x2 = panel(2, "Bead moved", "same program", "position", 3)
    band(x2, 1.65, 2.15, GREY, "taught bead", 3, dashed=True)
    band(x2, 2.65, 3.15, "E07B00", "bead now", 3)
    row(x2, 3.30, 1.72, 2.08, False, "placed off the bead", 3)
    row(x2, 4.10, 2.72, 3.08, True, "path reprogrammed", 4)
    s.add(label(s, CX, 5.85, CW, 0.40, "Each change in the product or the process requires a change in the code",
                size=19, color=INK, align="ctr"), click=5)
    s.add(label(s, CX, 6.30, CW, 0.36, "The timing and the position are not stated explicitly, and the program encodes them only "
                "implicitly", size=15, align="ctr"), click=5)
    s.notes = ("How such a cell works today. The motion is taught or programmed once and replayed exactly, run after "
               "run, and every run seats the part inside the adhesive's open time. [Click] A faster-curing adhesive "
               "shortens the open time. The same program now seats the part too late. [Click] An engineer changes the "
               "timing in the code. [Click] The bead is laid at a different position. The same program places the part off "
               "the bead. [Click] An engineer changes the path in the code. [Click] Each change of product or process "
               "requires a code change, because the requirements, when to seat and where, are not stated explicitly, "
               "and the program encodes them only implicitly. [§1.1; ABB customer story]")
    out.append(s)

    # from programming to a generative model, one column per click
    s = content("From programming to generation", "Motivation")
    cols = [("Program", "fig_prog_1.png", "One motion, coded by hand", None),
            ("Imitate", "fig_prog_2.png", "One predicted motion for each state", 0),
            ("Generate", "fig_prog_3.png", "Plausible samples, which a requirement stated after training accepts or rejects", 1)]
    for k, (head, img, line, click) in enumerate(cols):
        x0 = CX + 4.12 * k
        path = HERE / img
        items = [label(s, x0, 2.12, 3.85, 0.38, head, size=19, color=INK, bold=True, anchor="ctr"),
                 picture(s, path, *fit(path, x0, 2.60, 3.85, 2.70), f"{head}: {line if isinstance(line, str) else ' '.join(line)}"),
                 label(s, x0, 5.45, 3.85, 0.80, line, size=15, color=INK)]
        if k == 2:
            items.append(label(s, x0 + 1.70, 4.95, 2.10, 0.28, "zone stated after training", size=11, color=PINK, align="r"))
        if k > 0:
            items.append(arrow(s, x0 - 0.25, 3.95, x0 - 0.03, 3.95, color=GREY, lw=2))
        for it in items:
            s.add(it, click=click, is_sp=it.startswith("<p:sp>"))
    s.notes = ("There are three ways to obtain the motion. One: program it. One motion, coded by hand, and every change is a code "
               "change, as on the previous slide. [Click] Two: record demonstrations instead, and train a "
               "network on them. Ordinary regression predicts the most likely motion for each "
               "state; it generalizes to states near the demonstrations, but it returns a single trajectory, and the "
               "same input returns the same trajectory every time. It also blends distinct demonstrated motions into "
               "an average. [Click] Three: a generative model represents the distribution of plausible motions, and "
               "two draws give two different, plausible trajectories. The method depends on this property, because "
               "selection by a requirement stated after training is possible only where alternatives exist. Here a zone stated after "
               "training rules out three samples and leaves five. [§3.3.1; ALVINN, Ross et al.; §1.4]")
    out.append(s)

    # the requirement changes
    s = content("Requirements that change after training", "Motivation")
    img = HERE / "fig_requirements_slide.png"
    s.add(picture(s, img, *fit(img, CX, TOP, CW, BOTTOM - TOP),
                  "The same samples of the learned prior, accepted or rejected differently by a "
                  "fast-curing and a slow-curing adhesive"), is_sp=False)
    s.notes = ("This slide states the timing explicitly. In a load-and-bond cell the robot seats a component on an adhesive "
               "bead. It must seat within the adhesive's open time, hold for a minimum duration, and keep clear of "
               "the operator's side. Left, samples of a model trained on demonstrations. The same samples satisfy "
               "the requirement for one adhesive and violate it for another. The window and the hold depend on the adhesive, "
               "so they can change after the demonstrations are recorded. [§1.1, eq. 1.1]")
    out.append(s)

    # the problem
    s = content("Problem", "Motivation")
    img = pdf_png("FlowMatching/fig_motivation_gap.pdf")
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 2.90), "The requirement does not enter the "
                  "generative model, so one of three samples meets it"), is_sp=False)
    for x in [box(s, 0.90, 5.15, 11.55, 0.92,
                  [("Given demonstrations recorded before training and a requirement ", {}), ("φ", M),
                   (" stated after it, generate a trajectory that is plausible under the demonstrations and "
                    "satisfies ", {}), ("φ", M), (", without retraining.", {})],
                  tint(CYAN, 8), CYAN, size=18, lw=1.5, align="l"),
              label(s, 0.90, 6.20, 11.55, 0.32, "Training-time conditioning learns the requirement from paired data and can require retraining "
                    "outside its distribution", size=13)]:
        s.add(x, click=0)
    s.notes = ("A demonstration records the instant of seating, not the required window: it witnesses that the "
               "requirement can be satisfied without determining it. A model trained on demonstrations alone has no "
               "input for the requirement, so a sample can seat too late and still end on the housing, and a "
               "benchmark that judges the final state counts it as a success. [Click] The problem: given "
               "demonstrations recorded before training and a requirement stated after it, generate a trajectory "
               "that is plausible under the demonstrations and satisfies the requirement, without retraining. "
               "Training-time conditioning, such as TeLoGraF, learns the requirement from paired data and degrades "
               "outside its training distribution. [§1.1, §1.2, Problem 4.1]")
    out.append(s)

    # aim and research questions (Section 1.2 and 1.3)
    s = content("Aim and research questions", "Motivation")
    s.add(label(s, CX, 2.15, CW, 0.32, "Aim", size=16, color=INK, bold=True))
    s.add(label(s, CX, 2.50, CW, 0.45, "A method for imposing STL requirements on a trained generative model at "
                "inference time", size=19, color=INK))
    s.add(label(s, CX, 2.95, CW, 0.32, "The trained model is called the learned prior, because it provides the motion "
                "that the requirement does not specify", size=15))
    callout(s, CX, 3.45, CW, 0.80, "RQ1", "Does a demonstration determine the requirement?", BLUE, size=20)
    callout(s, CX, 4.38, CW, 0.80, "RQ2", "Does the robustness score alone determine a trajectory?", PINK, size=20)
    callout(s, CX, 5.31, CW, 0.80, "Method", "STL-FM, robustness guidance of the learned prior", CYAN, size=20)
    s.notes = ("The aim: a method for imposing STL requirements on a trained generative model at "
               "inference time. Two open questions concern the requirement itself rather "
               "than the performance of a planner: whether a demonstration determines the requirement, and whether "
               "the robustness score alone determines a trajectory. The first two contributions answer them by proof. "
               "The third contribution is the method, STL-FM, which guides the learned prior, "
               "an unconditional model trained once by flow matching, by the gradient of STL robustness at one "
               "constant strength, and which is evaluated experimentally. [§1.2, §1.3; Ch. 4, App. A; Ch. 5]")
    out.append(s)

    # the approach, the roadmap once
    s = content("Approach", "Motivation")
    roadmap(s)
    s.notes = ("The trained model is called the learned prior, because it provides the motion the requirement does not "
               "specify. The prior is trained once, offline, on demonstrations. Each requirement is compiled into a "
               "robustness score at inference. The guided sampler combines the two into a plan, which a controller "
               "executes. The bar at the top of each slide shows the section. [§1.3, Fig. 5.1]")
    out.append(s)

    # ── Background ──
    out.append(section_roadmap("Stating the requirement", "Background", "req",
                               "First, how the requirement is written and how it is scored."))

    # STL formula
    s = content("Signal Temporal Logic", "Background")
    s.add(label(s, CX, 2.45, CW, 0.60,
                [("Seat within [a, b]", {"color": BLUE}), (",  ", {}), ("hold for d", {"color": GREEN_D}),
                 (",  ", {}), ("avoid the operator zone", {"color": PINK})], size=28, align="ctr", anchor="ctr"))
    s.add(arrow(s, 6.67, 3.20, 6.67, 3.85, color=LIGHT, lw=2), click=0, is_sp=False)
    eqimg(s, "bond", 6.67, 4.05, align="c", click=0,
          descr="phi equals eventually within a b, always within 0 d, seated, and always within 0 T, not operator")
    s.add(label(s, CX, 5.30, CW, 0.40,
                "The requirement bounds when the part is seated and where the robot may not go",
                size=17, align="ctr"), click=1)
    cite(s, "Maler and Nickovic 2004")
    s.notes = ("Signal Temporal Logic expresses time bounds over real-valued signals, such as a robot "
               "trajectory. [Click] Eventually, the diamond, means at some instant of its window. Always, "
               "the box, means at every instant. The requirement says: at some instant in [a, b] the "
               "part becomes seated and stays seated for d, and at every instant the robot stays out of "
               "the operator zone. [Click] The requirement bounds only the timing of the seating and the "
               "region to avoid. The grasp, the approach and the rest of the motion are hard to write "
               "as a formula and are learned from the demonstrations. [§1.1, eq. 1.1; §3.2]")
    out.append(s)

    # the evaluated fragment
    s = content("Evaluated fragment", "Background")
    eqimg(s, "fragment", 6.67, 2.15, align="c", descr="Syntax of the evaluated fragment")
    cols = [(0.70, 2.00), (2.80, 3.90), (6.80, 5.85)]
    for (x, w), h in zip(cols, ["Construct", "Reads as", "In the load-and-bond requirement"]):
        s.add(label(s, x, 2.88, w, 0.30, h, size=14))
    rows = [
        ([("μ", M)], [("a predicate, ", {}), ("h(x) ≥ 0", M)],
         [("seated", {"italic": True}), (", the part within tolerance of the seat", {})]),
        ([("¬μ", M)], [("μ", M), (" does not hold", {})],
         [("¬", M), ("operator", {"italic": True}), (", outside the operator zone", {})]),
        ([("φ", M), ("1", SUB), (" ∧ ", M), ("φ", M), ("2", SUB)], "both hold",
         "seated on time and outside the zone"),
        ([("◇", M), ("[a,b]", SUB), (" φ", M)],
         [("φ", M), (" at some instant of [a, b]", {})], "the part is seated within the open time"),
        ([("◻", M), ("[a,b]", SUB), (" φ", M)],
         [("φ", M), (" at every instant of [a, b]", {})], "held for d, outside the zone throughout"),
    ]
    for k, (sym, reads, ex) in enumerate(rows):
        y = 3.22 + 0.58 * k
        s.add(rule(s, 0.70, 12.65, y))
        s.add(label(s, cols[0][0], y + 0.08, cols[0][1], 0.44, sym, size=22, color=INK, anchor="ctr"))
        s.add(label(s, cols[1][0], y + 0.08, cols[1][1], 0.44, reads, size=17, color=INK, anchor="ctr"))
        s.add(label(s, cols[2][0], y + 0.08, cols[2][1], 0.44, ex, size=17, color=INK, anchor="ctr"))
    s.add(rule(s, 0.70, 12.65, 3.22 + 0.58 * 5))
    s.notes = ("The evaluated fragment. A predicate is a margin function of the state that is "
               "non-negative when the predicate holds, for example the part within a tolerance of the seat. "
               "Negation, conjunction and the two bounded temporal operators build every requirement evaluated "
               "in this talk. [§3.2; Remark rem:fragment]")
    out.append(s)

    # robustness
    s = content("Quantitative robustness", "Background")
    eqimg(s, "robustness", 6.67, 2.10, scale=0.85, align="c", descr="Robustness of the evaluated fragment")
    eqimg(s, "soundness", 6.67, 3.42, scale=0.95, align="c", descr="Soundness: positive robustness implies satisfaction")
    img = HERE / "fig_robustness_cell.png"
    s.add(picture(s, img, *fit(img, CX, 3.92, CW, 2.68),
                  "Three executions in the load-and-bond cell with robustness +2.6, -8.6 and -6.0 cm"),
          is_sp=False)
    cite(s, "Donzé and Maler 2010.  Values in the figure are illustrative.")
    s.notes = ("Robustness replaces the Boolean verdict with a real number, defined by recursion over the formula. A "
               "predicate gives its margin h, negation changes the sign, conjunction and always take a minimum, "
               "eventually a maximum over its window. Soundness: a positive score certifies satisfaction. Below, "
               "three executions in the cell. (a) The part is seated inside the window and held, so the margin is "
               "positive. (b) At the end of the window the part is still 8.6 cm from the seat. (c) The robot crosses "
               "6 cm into the operator zone. The margin is a distance, in the units of the predicate, not a time. "
               "[§3.2, def:robustness, eq:robustness-sound]")
    out.append(s)

    # differentiable
    s = content("Smooth robustness", "Background")
    eqimg(s, "smooth", 6.67, 2.15, align="c", descr="Log-sum-exp surrogate of max and min")
    img = HERE / "fig_robustness_gradient.png"
    s.add(picture(s, img, *fit(img, CX, 2.98, CW, 3.25),
                  "Gradient of the robustness score on a late plan, exact and smoothed"), is_sp=False)
    s.add(label(s, CX, 6.28, CW, 0.32, [("Guidance uses the surrogate at ", {}), ("κ", M), (" = 10.  Satisfaction is "
                "always scored with the exact semantics.", {})], size=15, align="ctr"))
    cite(s, "Leung et al. 2021; Kapoor et al. 2025 (STLCG++)")
    s.notes = ("The exact min and max have a gradient on a single argument. With the exact semantics the gradient "
               "acts on a single waypoint, here the state at the end of the open time. Log-sum-exp replaces max and "
               "min, and at sharpness kappa = 10 in the experiments it spreads the gradient over a few neighbouring "
               "waypoints. The formula is compiled by recursion over its syntax tree into this differentiable score, "
               "with no learned component, so a new requirement requires only a new syntax tree. The smoothed score is "
               "sound only up to a margin, so satisfaction is always scored exactly. Implementation: stljax, the JAX "
               "library of STLCG++. [§3.2.3, eq:logsumexp; §4.2, alg:build-rho, prop:smoothing-bias]")
    out.append(s)

    out.append(section_roadmap("Learning the prior", "Background", "prior",
                               "Second, the learned prior that generates the motion."))

    # flow matching, Fig. 3.1 animated
    s = content("Flow matching", "Background")
    mp4, poster = HERE / "fig_transport_anim.mp4", HERE / "fig_transport_anim_poster.png"
    s.add(video(s, mp4, poster, *fit(poster, CX, 2.15, 4.45, 4.40),
                "Animation of flow matching as transport from noise to two modes"),
          click=0, play=6800)
    ex = 5.55
    s.add(label(s, ex, 2.25, 7.1, 0.32, "Training", size=16, color=INK, bold=True))
    eqimg(s, "fm_loss", ex, 2.65, scale=0.86, descr="Flow-matching loss with the linear path")
    s.add(label(s, ex, 3.70, 7.1, 0.32, "Sampling", size=16, color=INK, bold=True))
    eqimg(s, "fm_ode", ex, 4.10, scale=0.86, descr="Generative ordinary differential equation")
    s.add(label(s, ex, 4.90, 7.1, 1.10, ("K = 64 Euler steps. The prior is unconditional, trained once on",
                                         "demonstrations, and its only conditioning is the start state."), size=15))
    cite(s, "Lipman et al. 2023; Liu et al. 2022")
    s.notes = ("[Click to play] A point of this space is a whole trajectory. Flow matching trains a velocity field "
               "v_theta by regression onto the straight-line target tau_1 minus tau_0, from noise to data. Sampling "
               "integrates the field from s = 0 to s = 1, here in K = 64 Euler steps. The density deforms from one "
               "Gaussian into two modes, two plausible behaviours, here passing a fixture on either side. The prior "
               "is unconditional, trained once on demonstrations, and its only conditioning is the start state. "
               "[§3.3, def:fm, eq:fm-loss, eq:fm-ode-bg, Fig. 3.1; §5.1.1]")
    out.append(s)

    # generation from noise, the diffusion clip kept from the earlier deck
    s = content("Generation from noise", "Background")
    mp4, poster = HERE / "diffusion_clip.mp4", HERE / "diffusion_clip_poster.png"
    s.add(video(s, mp4, poster, *fit(poster, CX, 2.15, CW, 4.60), "Generation of a robot trajectory from noise"),
          click=0, play=19500)
    s.notes = ("[Click to play] Generation from noise, applied to a robot trajectory. This clip shows a "
               "diffusion model. Flow matching produces the same kind of result along straight-line "
               "paths. The prior used here is unconditional, trained once on demonstrations, and its only "
               "conditioning is the start state. [§3.3; §5.1.1]")
    out.append(s)

    # related work, one overview figure per class
    s = content("Related work", "Background")

    def tile(img, x, y, w, h, head, cite_text, frame=None):
        s.add(label(s, x, y, w, 0.30, head, size=15, color=INK, bold=True))
        s.add(label(s, x, y + 0.29, w, 0.26, cite_text, size=12, italic=True))
        path = HERE / f"rw_{img}.png"
        fx, fy, fw, fh = fit(path, x, y + 0.62, w, h)
        s.add(picture(s, path, x, fy, fw, fh, f"{head}: overview figure of {cite_text}"), is_sp=False)
        if frame:
            s.add(box(s, x - 0.12, y - 0.10, w + 0.24, h + 0.85, "", None, frame, lw=2.0, radius=3000,
                      name="Highlight"))

    tile("telograf", CX, 2.08, 5.80, 1.45, "Training-time conditioning", "TeLoGraF, Meng and Fan 2025")
    tile("zstp", 6.80, 2.08, 2.80, 1.45, "Decompose-and-stitch", "ZSTP, Liu et al. 2025")
    tile("kurtz", 9.90, 2.08, 2.78, 1.45, "Trajectory optimization", "Kurtz and Lin 2021")
    tile("safediffuser", CX, 4.36, 3.80, 1.62, "Safe-set enforcement", "SafeDiffuser, Xiao et al. 2023")
    tile("ctg", 4.95, 4.36, 3.80, 1.62, "Inference-time robustness guidance", "CTG, Zhong et al. 2022",
         frame=CYAN)
    s.add(box(s, 9.30, 5.02, 3.38, 1.05, ("STL-FM", "on a flow-matching prior"),
              tint(CYAN, 8), CYAN, size=15, lw=1.5))
    s.add(arrow(s, 8.87, 5.545, 9.30, 5.545, color=CYAN, lw=2))
    s.add(label(s, CX, 6.68, CW, 0.24, "Overview figures reproduced from the cited papers", size=11))
    s.notes = ("Previous work differs in where the requirement enters. Training-time conditioning, such "
               "as TeLoGraF, learns the requirement from paired data and degrades outside the "
               "conditioning distribution. Decompose-and-stitch, such as ZSTP, splits the formula into "
               "timed waypoints before generation and fixes each operator's timing in advance. "
               "Trajectory optimization uses robustness with a known dynamics model, specified by hand. "
               "Safe-set enforcement, such as SafeDiffuser, keeps samples in a time-invariant safe set, "
               "which expresses no dwell or order. STL-FM belongs to inference-time robustness guidance, "
               "with CTG. Unlike CTG, it guides a flow-matching prior, whose velocity is bounded, so one "
               "constant strength is well posed where diffusion needs a schedule. It also evaluates "
               "long-horizon dwell, sequence and avoidance, including nested operators. [Ch. 2, §2.7]")
    out.append(s)

    # comparison table (on trial, author's request 2026-10-21); every cell from Chapter 2
    s = content("Comparison of approaches", "Background")
    tx = [CX, 4.30, 7.45, 10.05]
    tw = [3.55, 3.05, 2.50, 2.63]
    for x, w, h in zip(tx, tw, ["Approach", "Requirement enters", "Rest of the motion from", "Property"]):
        s.add(label(s, x, 2.12, w, 0.30, h, size=14))
    rows = [("Trajectory optimization", "Kurtz and Lin 2021",
             "cost or constraint, with a known dynamics model", "dynamics model, costs and feasibility constraints",
             "specified by hand"),
            ("Control barrier functions", "Lindemann and Dimarogonas 2019",
             "time-varying barrier functions, quadratic program", "dynamics model and control cost",
             "boundedness conjoined to the requirement"),
            ("Training-time conditioning", "TeLoGraF, Meng and Fan 2025",
             "training, from requirement–demonstration pairs", "conditioned flow-matching model",
             "degrades outside the conditioning distribution"),
            ("Decompose-and-stitch", "ZSTP, Liu et al. 2025",
             "timed waypoints, before generation", "pretrained diffusion model, between waypoints",
             "timing of each operator fixed in advance"),
            ("Safe-set enforcement", "SafeDiffuser, Xiao et al. 2023",
             "barrier invariance in each denoising step", "diffusion model",
             "time-invariant safe set, no temporal operators"),
            ("Inference-time robustness guidance", "CTG, Zhong et al. 2022",
             "robustness gradient, during sampling", "diffusion model",
             "strength coupled to the noise level, no certificate"),
            ("STL-FM", "this thesis",
             "robustness gradient at the predicted endpoint, during sampling", "learned prior, trained by flow matching",
             "one constant strength, no retraining, no certificate")]
    rh = 0.58
    for r, (cls, src, enters, rest, prop) in enumerate(rows):
        y = 2.48 + rh * r
        ours = cls == "STL-FM"
        s.add(rule(s, CX, 12.68, y))
        s.add(label(s, tx[0], y + 0.05, tw[0], rh - 0.08,
                    ([(cls, {"bold": True, "color": BLUE if ours else INK})], [(src, {"size": 11, "color": MUTED})]),
                    size=14, anchor="ctr"))
        for x, w, t in zip(tx[1:], tw[1:], [enters, rest, prop]):
            s.add(label(s, x, y + 0.05, w, rh - 0.08, t, size=13, color=BLUE if ours else INK, anchor="ctr"))
    s.add(rule(s, CX, 12.68, 2.48 + rh * len(rows)))
    s.add(label(s, CX, 6.62, CW, 0.26, "Entries summarize the cited works", size=11))
    s.notes = ("The table compares each approach by where the requirement enters and by what determines the rest of the motion. "
               "Trajectory optimization and control synthesis with barrier functions represent the requirement "
               "explicitly, as STL-FM does, and the dynamics model and costs determine what the score leaves free; "
               "the barrier-function formulation of Lindemann and Dimarogonas also conjoins a boundedness clause to "
               "the requirement, and later work extends it to disjunctions and nested operators. Training-time "
               "conditioning learns the requirement from requirement-demonstration pairs. Decompose-and-stitch "
               "fixes the timing of each operator before generation. Safe-set enforcement gives an invariance "
               "certificate, but for a time-invariant safe set. CTG shares the guidance mechanism, on a diffusion "
               "model. STL-FM takes the rest of the motion from a learned prior, at one constant strength, and gives "
               "no certificate; a barrier-based tracker could execute an STL-FM plan, which is future work. "
               "[Ch. 2: rw-modelbased, rw-guidance, rw-decompose, rw-conditioning, rw-constraints, positioning]")
    out.append(s)

    # ── Method ──
    out.append(section_roadmap("Guiding the prior", "Method", "sampler",
                               "Third, the guided sampler that combines the learned prior with the robustness score."))

    # guided velocity
    s = content("Guided velocity field", "Method")
    eqimg(s, "guided", 6.67, 2.20, align="c", descr="The guided velocity field, prior velocity plus a constant "
          "times the conditioned requirement gradient at the predicted endpoint")
    s.add(label(s, CX, 3.75, CW, 0.32, "with the penalized objective and the conditioned gradient", size=15,
                align="ctr"))
    eqimg(s, "conditioning", 6.67, 4.15, align="c", descr="Penalized objective and masked, normalized gradient")
    s.add(label(s, CX, 5.40, CW, 0.75,
                ([("λ", M), ("0", SUB), (" ≥ 0 is one constant strength for the whole flow.", {})],
                 "No component of the sampling loop is trained, and the requirement is not an input to the network."),
                size=17, color=INK, align="ctr"))
    s.notes = ("The sampler integrates the guided velocity from the same Gaussian start as the prior. The "
               "prior velocity moves the iterate toward trajectories likely under the learned prior. The "
               "requirement term moves it toward satisfaction. The gradient is taken of a penalized objective, the "
               "robustness minus a small finite-difference smoothness penalty, masked to the position coordinates, "
               "and normalized to unit length, so lambda_0 is a step size that transfers across requirements. This is a "
               "soft realization of the constrained problem, not a solution with a certificate. "
               "[§4.3, eq:guided-velocity; §4.5, eq:smoothness-penalty, eq:grad-normalize]")
    out.append(s)

    # one sampler step, at the predicted endpoint
    s = content("Guided sampler", "Method")
    s.add(label(s, CX, 2.15, CW, 0.36,
                [("For k = 0, …, K − 1 with s = kΔs, Δs = 1/K and K = 64, from ", {}), ("τ", M),
                 (" ~ N(0, I) with the start state pinned", {})], size=17, color=INK, align="ctr"))
    eqimg(s, "step", 6.67, 2.70, align="c", descr="One step of the guided sampler")
    s.add(label(s, CX, 4.95, CW, 1.10,
                ("The gradient is taken with respect to the predicted endpoint, not through the network.",
                 [("Early in the flow the iterate ", {}), ("τ", M), ("(s) is mostly noise, whereas ", {}), ("τ̂", M),
                  ("(s) is the prior’s estimate of the finished trajectory.", {})]),
                size=16, align="ctr"))
    cite(s, "The full sampler is in backup")
    s.notes = ("One step of the sampler. Early in the flow the iterate is mostly noise, and the gradient of its "
               "robustness points in a direction unrelated to any plausible trajectory. The predicted endpoint is the "
               "prior's running estimate of the finished trajectory, obtained from the straight-line path. The "
               "requirement is scored on that estimate, and the gradient is taken with respect to it, not through the "
               "network. Then mask and normalize, take a constant-strength Euler step, and re-pin the start state. "
               "[§4.4, eq:predicted-endpoint; §4.7, alg:guided-ode]")
    out.append(s)

    # ── Results ──
    OL = "2D/openloop/openloop_{}.pdf"
    out.append(section_roadmap("Evaluating the plans", "Results", "plan",
                               "Finally, the evaluation: what the plans satisfy, and what their executions achieve."))

    # setup
    s = content("Experimental setup", "Results")
    for k, (rel, cap) in enumerate([("2D/scene_arena.pdf", ("Planar navigation", "100 runs per class, plans only")),
                                    ("OGBench/scene_cube.pdf", ("Cube manipulation", "10 runs per class, executed"))]):
        img = pdf_png(rel)
        x0 = CX + 2.80 * k
        s.add(picture(s, img, *fit(img, x0, 2.15, 2.60, 2.75), cap[0]), is_sp=False)
        s.add(label(s, x0, 5.05, 2.60, 0.30, cap[0], size=16, color=INK, bold=True, align="ctr"))
        s.add(label(s, x0, 5.37, 2.60, 0.30, cap[1], size=13, align="ctr"))
    gx, cw = 6.28, [3.15, 0.95, 1.35, 0.95]
    heads = ["Planner", "Learned prior", "Requirement", "Endpoint pin"]
    rows = [("Endpoint-inpaint planner", ["✓", "", "✓"], "9A9A9A"), ("STL-FM", ["✓", "✓", ""], BLUE),
            ("STL Optimizer (no-prior)", ["", "✓", ""], PINK)]
    xs = [gx + sum(cw[:i]) for i in range(4)]
    for x, w, h in zip(xs, cw, heads):
        s.add(label(s, x, 2.30, w, 0.55, h, size=14, align="l" if h == "Planner" else "ctr", anchor="b"))
    for r, (name, marks, col) in enumerate(rows):
        y = 3.00 + 0.80 * r
        s.add(rule(s, gx, gx + sum(cw), y - 0.08))
        s.add(label(s, xs[0], y, cw[0], 0.62, name, size=15, color=col, bold=True, anchor="ctr"))
        for x, w, m in zip(xs[1:], cw[1:], marks):
            s.add(label(s, x, y, w, 0.62, m, size=22, color=INK, align="ctr", anchor="ctr"))
    s.add(rule(s, gx, gx + sum(cw), 5.32))
    s.add(label(s, gx, 5.50, 6.2, 0.60, "STL-FM with endpoint pin differs from STL-FM in satisfaction rate by at most 0.05 on any of the six classes (backup)",
                size=13))
    s.notes = ("Two settings. Planar navigation: 100 runs per class on one fixed instance per class, plans "
               "only. Cube manipulation in OGBench: 10 runs per class on three classes, each plan executed in "
               "the simulator. Each baseline differs from STL-FM in one component. The endpoint-inpaint planner "
               "replaces the requirement by a pinned endpoint instead of the robustness gradient. The "
               "STL Optimizer (no-prior) keeps the requirement and removes the prior; it descends the "
               "violation penalty with a smoothness penalty and a velocity limit. A fourth planner, STL-FM "
               "with endpoint pin, differs from STL-FM in satisfaction rate by at most 0.05 on any of the six classes. "
               "[§5.1.2-5.1.3, tab:families, tab:planners]")
    out.append(s)

    # one prior, six classes
    s = content("Six requirement classes", "Results")
    classes = [("reach", "Reach"), ("nested", "Nested reach-and-dwell"), ("recurrence", "Recurrence"),
               ("sequence", "Sequence"), ("seqavoid", "Sequence with avoidance"), ("composite", "Composite")]
    for k, (key, name) in enumerate(classes):
        img = pdf_png(OL.format(f"{key}_guided"))
        col, row_ = k % 3, k // 3
        x0, y0 = 1.10 + 3.80 * col, 2.05 + 2.17 * row_
        s.add(label(s, x0, y0, 3.4, 0.30, name, size=15, color=INK, bold=True, align="ctr"))
        s.add(picture(s, img, *fit(img, x0, y0 + 0.30, 3.4, 1.83), f"STL-FM plans, {name}"), is_sp=False)
    claim(s, [("One learned prior and one constant strength ", {}), ("λ", M), ("0", SUB),
              (" are used for all six requirement classes", {})])
    s.notes = ("The same prior and the same lambda_0 for all six classes. A new requirement requires only a new "
               "syntax tree. Satisfaction rates of STL-FM: reach 0.96, nested reach-and-dwell 1.00, "
               "recurrence 0.98, sequence 0.89, sequence with avoidance 0.89, composite 0.78. A sweep of one "
               "requirement's own parameters is future work, so this does not test adaptation to a changed "
               "parameter. If asked about roughness: on nested reach-and-dwell 47 percent of turns exceed a "
               "right angle. [tab:families; tab:openloop; §4.2; §6.1; §7.2]")
    out.append(s)

    # navigation satisfaction
    s = content("Logic satisfaction in navigation", "Results")
    img = HERE / "fig_nav_satisfaction.png"
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 4.30), "Satisfaction rate per class for three planners"),
          is_sp=False)
    claim(s, "Logic satisfaction alone does not distinguish STL-FM from the STL Optimizer")
    s.notes = ("Over 100 runs per class. The endpoint-inpaint planner satisfies reach on every run and no other "
               "class on any run: the pin fixes the end, and the prior generates the remainder of the trajectory, "
               "which contains no dwell, order or avoidance. STL-FM satisfies the five history-dependent classes at "
               "0.78 to 1.00. The STL Optimizer satisfies every class on every run, so satisfaction "
               "alone does not separate it from STL-FM. Evidence about the prior must come from other properties of "
               "the plans. Plan time: 0.42 to 1.15 s for STL-FM, 5.67 to 28.22 s for the STL Optimizer. "
               "[tab:openloop, tab:anytime, §6.1]")
    out.append(s)

    # time to first satisfaction, in budget and in seconds
    s = content("Time to satisfaction", "Results")
    img = HERE / "fig_time_budget.png"
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 3.78), "First satisfaction as a percentage of the budget and in "
                  "estimated seconds, per class, for STL-FM and the STL Optimizer"), is_sp=False)
    s.add(label(s, CX, 5.88, CW, 0.30, "Medians over satisfying runs. Budgets of 64 steps for STL-FM and 1,500 to 6,000 "
                "for the optimizer. Estimated first satisfaction, 0.10 to 1.07 s against 0.83 to 6.75 s", size=12,
                align="ctr"))
    claim(s, "The STL Optimizer satisfies the requirement earlier in its budget but later in wall-clock time")
    s.notes = ("When in its budget each planner first satisfies the requirement, over the runs whose final plan "
               "satisfies it. STL-FM takes 64 integration steps and the STL Optimizer 1,500 to 6,000 "
               "gradient steps, according to the class. On nested reach-and-dwell, recurrence, sequence, sequence "
               "with avoidance and composite, STL-FM first satisfies the requirement at 83 to 94 percent of its "
               "budget, and on reach at 30 percent. The optimizer first satisfies it at 4 to 24 percent. In seconds "
               "the order reverses. Assuming every step of a planner takes the same time, STL-FM first satisfies the "
               "requirement after 0.10 to 1.07 seconds and the optimizer after 0.83 to 6.75, and on every class the "
               "optimizer is the later. A whole plan takes 0.42 to 1.15 seconds for STL-FM and 5.67 to 28.22 seconds "
               "for the optimizer. In the cube study STL-FM plans in 0.24 seconds and the optimizer in 0.96. In the "
               "kitchen STL-FM plans in 0.25 seconds under both priors, against 0.16 and 0.21 seconds for the "
               "unguided prior. Times are medians over 20 separate timing runs per class on a laptop GPU, an NVIDIA "
               "RTX A500, without recording the robustness at every step. A repeated measurement of the cube and "
               "kitchen times was up to 20 percent slower, with the same order of the planners. "
               "[§5.2.3, tab:anytime; §5.3; §5.4; app:anytime]")
    out.append(s)

    # optimizing robustness alone
    s = content("Arena excursion", "Results")
    for k, (key, cap) in enumerate([("seqavoid_stlonly", "STL Optimizer"),
                                    ("seqavoid_guided", "STL-FM")]):
        img = pdf_png(OL.format(key))
        x0 = 1.20 + 5.70 * k
        s.add(label(s, x0, 2.10, 5.2, 0.34, cap, size=17, color=INK, bold=True, align="ctr"))
        s.add(picture(s, img, *fit(img, x0, 2.48, 5.2, 3.55), f"{cap}, sequence with avoidance"), is_sp=False)
    s.add(label(s, CX, 6.07, CW, 0.28, "Sequence with avoidance, 25 of 100 plans per planner, arena clipped "
                "at its edge", size=13, align="ctr"))
    claim(s, "Every plan of the STL Optimizer for sequence with avoidance leaves the arena")
    s.notes = ("The STL Optimizer removes the prior and optimizes robustness directly. It descends "
               "the violation penalty with a smoothness penalty and a velocity limit. It satisfies every requirement "
               "class on every run. On sequence with avoidance every one of its plans leaves "
               "the arena, at a median largest coordinate of 10.27 against a half-width of 5.0. The "
               "excursion lies at steps 31 to 63, which no reach window covers. Deleting the avoidance "
               "conjuncts leaves the plans outside the arena, so the avoidance conjuncts do not cause the excursion. Its "
               "plans also leave the arena on sequence. "
               "Plans that use the prior cross the arena edge in at most 4 of 100 runs per class, by a small margin. "
               "[§5.1.3; §5.2.2; §6.1; app:noobs-ablation]")
    out.append(s)


    # the formal result, illustrated
    s = content("Underdetermination by robustness", "Results")
    img = HERE / "fig_sparse_unbounded.png"
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 3.95),
                  "The robustness gradient acts on a few waypoints, and tails after the last window "
                  "leave the score unchanged"), is_sp=False)
    s.add(label(s, CX, 6.04, CW, 0.30, "At most m of 64 to 256 waypoints determine the score, with m between 1 and 5",
                size=15, align="ctr"))
    claim(s, "Robustness alone does not determine a trajectory (backup)")
    s.notes = ("Robustness is computed from a few predicate evaluations combined by min and max. A formula "
               "with m predicate occurrences is determined by at most m waypoints, and m is between 1 and 5 "
               "here, against horizons of 64 to 256. Under the exact semantics the gradient is zero at "
               "every other waypoint, and the score is flat along a subspace of dimension at least "
               "(H - m) d. At steps that only avoidance constrains, the set of maximizers is unbounded. "
               "A planner guided by robustness therefore needs a component besides the requirement to "
               "determine the rest of the trajectory. Here that is the learned prior. Its contribution is "
               "measured, not assumed, because the prior does not meet the idealized conditions of "
               "the theorem in backup. [Contribution 2; §4.1.1; prop:sparse-gradient, thm:prior-resolves, "
               "prop:no-maximizer; rem:prior-idealization]")
    out.append(s)

    # cube: requirement and STL-FM execution
    s = content("Cube manipulation", "Results")
    s.add(label(s, CX, 2.20, 6.4, 0.32, "Sequence requirement", size=16, color=INK, bold=True))
    s.add(label(s, CX, 2.62, 6.4, 0.80, ("Grasp the cube within 20 steps,", "place it between steps 20 and 100"),
                size=20, color=INK))
    eqimg(s, "cube", CX, 3.70, descr="phi equals eventually within 0 20 pick and eventually within 20 100 place")
    s.add(label(s, CX, 4.50, 6.75, 0.70, ("pick, the effector within 5 cm of the cube",
                                         "place, the cube within 4 cm of the target, the environment’s tolerance"),
                size=14))
    mp4, poster = HERE / "cube_stlfm_june.mp4", HERE / "cube_stlfm_june_poster.png"
    s.add(video(s, mp4, poster, *fit(poster, 7.45, TOP, 5.23, 3.95), "STL-FM plan executed in the cube task"),
          click=0, play=12700)
    s.add(label(s, 7.45, 6.06, 5.23, 0.28, "STL-FM plan, executed", size=13, align="ctr"))
    claim(s, "STL-FM completes 10 of 30 executions, the STL Optimizer none")
    s.notes = ("OGBench single cube. The prior generates the effector and the cube position over 128 steps, so "
               "the requirement and the environment's success criterion refer to the same cube. Place is a "
               "4 cm ball about the target, the environment's own tolerance; pick holds when the effector is "
               "within 5 cm of the cube. [Click to play] A proportional controller tracks the effector and a "
               "gripper state machine follows the plan. STL-FM completes 10 of 30 runs, the STL "
               "Optimizer none. The endpoint-inpaint planner completes 1. "
               "[§5.3, tab:closedloop]")
    out.append(s)

    # cube: logic versus task
    s = content("Logic satisfaction and task success", "Results")
    img = HERE / "fig_cube_logic_task.png"
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 4.30), "Logic satisfaction and task success in the cube study"),
          is_sp=False)
    claim(s, "Logic satisfaction and task success each occur without the other")
    s.notes = ("Left, pooled over the three classes. Right, STL-FM per class. On nested reach-and-dwell STL-FM "
               "satisfies the requirement in 1 of 10 runs and completes the task in 9. The requirement constrains the "
               "grasp and the placement to hold over windows that close by step 30, whereas success requires only "
               "that the cube arrive. On sequence it satisfies 10 of 10 and completes 1. A requirement written on "
               "the generated variables constrains only those variables. The kitchen study shows the same gap "
               "more strongly (backup). [tab:closedloop, §6.2]")
    out.append(s)

    # ── Conclusions ──
    s = content("Conclusions", "Conclusions")
    answers = [
        ("RQ1", BLUE, "Does a demonstration determine the requirement?",
         "A demonstration witnesses a requirement without determining it, so the requirement "
         "is stated separately from the demonstrations."),
        ("RQ2", PINK, "Does the robustness score alone determine a trajectory?",
         "The robustness score alone does not determine a trajectory. Its gradient depends on at most m waypoints, "
         "and its maximizers are unbounded where only avoidance applies. Without the "
         "prior, plans for the sequencing requirements leave the arena, and the planned cube moves without contact."),
        ("Method", CYAN, "STL-FM guides the learned prior at one constant strength, without retraining",
         "STL-FM satisfies the dwell, sequence and avoidance requirements at rates of 0.78 to 1.00 per class and "
         "completes 10 of 30 cube executions, against none for the STL Optimizer."),
    ]
    for i, (tag, col, q, a) in enumerate(answers):
        callout(s, CX, 2.08 + 1.34 * i, CW, 1.22, tag, ([(q, {"bold": True})], a), col, size=15)
    s.add(label(s, CX, 6.16, CW, 0.40, "Logic satisfaction and task success do not coincide. A requirement constrains only the "
                "variables the prior generates.", size=15, color=INK, align="ctr"))
    s.notes = ("Back to the two questions. RQ1: a demonstration witnesses a requirement without determining it, so the "
               "requirement is stated as a formula and the demonstrations provide plausibility. RQ2: the robustness "
               "score alone does not determine a trajectory; its gradient acts on a few waypoints and its maximizers "
               "are unbounded where only avoidance applies. The learned prior provides the rest of the trajectory, as the "
               "navigation excursion and the cube carry gap show, and its contribution is not smoothness. The method: "
               "STL-FM guides the learned prior at one constant strength, without retraining, and covers nested and recurrent operators. "
               "Finally, satisfying the requirement on the plan is not completing the task: a requirement written on the "
               "generated variables constrains only those variables. STL-FM is a soft realization without a "
               "certificate. [§7.1; §6.1-6.3]")
    out.append(s)

    # future work
    s = content("Future work", "Conclusions")
    items = [("A differentiable dynamics model", "so that a requirement can constrain contact and object pose"),
             ("Execution on the physical platform", "plans for the GoFA door task, executed and scored on the robot"),
             ("A sweep of a requirement’s parameters", "the same prior under changed windows and dwell times"),
             ("A barrier-filtered controller for execution", "for an execution-time guarantee")]
    for i, (head, line) in enumerate(items):
        y = 2.15 + 0.88 * i
        s.add(label(s, CX, y, 0.45, 0.36, f"{i + 1}.", size=17, color=INK, bold=True))
        s.add(label(s, CX + 0.45, y, 7.0, 0.90, ([(head, {"bold": True})], line), size=16, color=INK))
    img = FIGS / "Kitchen/kitchen_planned_vs_executed.png"
    fx, fy, fw, fh = fit(img, 8.25, 2.20, 4.43, 3.80)
    s.add(picture(s, img, fx, fy, fw, fh, "Kitchen study, planned against executed robustness"), is_sp=False)
    s.add(label(s, 8.25, fy + fh + 0.08, 4.43, 0.50, ("Kitchen study, planned against executed", "robustness "
                "(backup)"), size=12, align="ctr"))
    s.notes = ("First, a differentiable dynamics or world model, so that a requirement can be written on contact, "
               "an object's pose or a hinge angle and constrain the executed behaviour. In the kitchen study under "
               "the complete-v2 prior every plan satisfies the requirement, and no execution does. Second, completion "
               "of the physical study: the GoFA prior is trained and the requirement compiled, but no plan has been "
               "executed. Third, a sweep of a requirement's own parameters with the prior held fixed, such as the "
               "open time or the dwell, which tests adaptation without retraining directly. Fourth, a "
               "barrier-filtered controller paired with the planner, for an execution-time guarantee. [§7.2; §2.6]")
    out.append(s)

    # end
    s = Slide(LAYOUT_END)
    s.add(footer(s))
    out.append(s)

    # ── Backup, after the end slide ──
    s = Slide(LAYOUT_DIVIDER)
    s.add(ph_title(s, "Supplementary material"))
    s.add(ph_body(s, 1, ["Answers to likely questions"]))
    s.add(footer(s))
    out.append(s)

    # plausible samples that violate the requirement
    s = content("Plausible samples that violate the requirement", backup=True)
    img = pdf_png("FlowMatching/fig_motivation_plausible.pdf")
    s.add(picture(s, img, *fit(img, CX, TOP, CW, 4.75), "Demonstrations and samples of the learned prior "
                  "against the seating window"), is_sp=False)
    s.notes = ("Backup for the problem slide. The demonstrations record the instant of seating. Samples of the learned "
               "prior can satisfy the window, seat too late, or release too early, and still end with the component "
               "on the housing. [§1.1, Fig. 1.1(b)]")
    out.append(s)

    # results tables, cropped from the compiled thesis (make_backup_crops.py)
    def crop_slide(title, names, notes, stack=False):
        sl = content(title, backup=True)
        imgs = [HERE / f"{n}.png" for n in names]
        if len(imgs) == 1:
            sl.add(picture(sl, imgs[0], *fit(imgs[0], CX + 0.4, TOP, CW - 0.8, 4.80), title), is_sp=False)
        elif stack:
            h = 4.80 / len(imgs) - 0.15
            for i, im in enumerate(imgs):
                sl.add(picture(sl, im, *fit(im, CX + 0.4, TOP + i * (h + 0.30), CW - 0.8, h), title), is_sp=False)
        else:
            w = CW / len(imgs) - 0.2
            for i, im in enumerate(imgs):
                sl.add(picture(sl, im, *fit(im, CX + i * (w + 0.4), TOP, w, 4.80), title), is_sp=False)
        sl.notes = notes
        return sl

    # formal results in plain language, one key formula each, without numbers or pointers to the thesis
    MS, MSUP, B = {"math": True, "sub": True}, {"math": True, "sup": True}, {"bold": True}

    def statement_slide(title, eq, descr, lines, closing, notes, size=18):
        sl = content(title, backup=True)
        _, h = eqimg(sl, eq, 6.67, 2.15, align="c", descr=descr)
        y = 2.15 + h + 0.40
        sl.add(label(sl, CX, y, CW, 6.15 - y, lines, size=size, color=INK, gap=9))
        sl.add(label(sl, CX, 6.30, CW, 0.40, closing, size=15))
        sl.notes = notes
        return sl

    out.append(statement_slide(
        "Requirements witnessed by one demonstration", "witness",
        "Satisfaction set of a requirement, and a strictly increasing chain of satisfaction sets from the "
        "witness alone to the whole trajectory space",
        ([("A trajectory ", {}), ("τ⋆", M), (" witnesses a requirement ", {}), ("φ", M), (" if it satisfies ", {}),
          ("φ", M), (", that is, if ", {}), ("τ⋆", M), (" lies in the satisfaction set ", {}), ("𝒮", M), ("φ", MS),
          (". Two requirements are equivalent if they have the same satisfaction set.", {})],
         "Any one trajectory witnesses uncountably many inequivalent requirements.",
         [("Their satisfaction sets form strictly increasing chains, from ", {}), ("{τ⋆}", M),
          (", “do exactly this”, to the whole trajectory space ", {}), ("𝒯", M), (", “do anything”.", {})],
         "Consequently, no map from a single demonstration to a requirement is determined by the demonstration."),
        "RQ1 therefore has a negative answer, and the requirement is stated separately from the demonstrations, "
        "as an STL formula.",
        "This result answers RQ1. Any trajectory witnesses uncountably many requirements, ordered from 'do exactly "
        "this' to 'do anything', so no map from one demonstration to a requirement is determined by its "
        "argument. The chains already contain standard STL formulae, from a tight ball at every step to a "
        "tautology. The requirement is therefore stated, not inferred. [App. A, def:requirement, "
        "prop:witness-underdetermines]"))
    out.append(statement_slide(
        "Sparsity of the robustness gradient", "sparse",
        "The gradient vanishes off the active set, the active set has at most m waypoints, and the flat subspace "
        "has dimension at least (H minus m) d",
        ([("The result concerns a formula ", {}), ("φ", M), (" with ", {}), ("m", M),
          (" predicate occurrences, scored with the exact semantics at a trajectory ", {}), ("τ", M),
          (" where every min and max selection is unique.", {})],
         [("Near ", {}), ("τ", M), (" the score depends on at most ", {}), ("m", M), (" waypoints, the active set ", {}),
          ("𝒜(τ)", M), (".", {})],
         [("The gradient is zero at every other waypoint, and the score is constant along a subspace ", {}),
          ("N(τ)", M), (" whose dimension in the position coordinates is at least ", {}), ("(H − m)d", M), (".", {})],
         [("Gradient ascent on the score leaves every coordinate in ", {}), ("N(τ)", M),
          (" at its initial value for as long as the active set is unchanged.", {})],
         [("Here ", {}), ("H", M), (" is the horizon, ", {}), ("d", M),
          (" the dimension of the position coordinates, and ", {}), ("π", M), ("t", MS),
          (" the waypoint at step ", {}), ("t", M), (".", {})]),
        [("In the experiments ", {}), ("m", M), (" lies between 1 and 5, against horizons of 64 to 256.", {})],
        "The first half of RQ2. Under the exact semantics the gradient is supported on at most m active "
        "waypoints, and the score is flat along a subspace of dimension at least (H - m) d. Under the smooth "
        "surrogate the gradient at the other waypoints is not zero, but it is suppressed exponentially in their "
        "robustness deficit. [App. A, prop:sparse-gradient, lem:smooth-concentration]"))
    out.append(statement_slide(
        "Maximizers of a reach requirement", "spurious",
        "The reach requirement and its predicate, and the maximizing set as a union over the window of the "
        "trajectories that are at the centre at that step",
        ([("The reach requirement ", {}), ("φ", M), (" holds if the position lies within a ball of radius ", {}),
          ("r", M), (" about ", {}), ("c", M), (" at some step of ", {}), ("[a, b]", M), (".", {})],
         [("Its largest score ", {}), ("r", M), (" is attained by every trajectory that is at ", {}), ("c", M),
          (" at some step of ", {}), ("[a, b]", M), (", whatever it does at the other steps.", {})],
         [("The maximizing set ", {}), ("𝒪", M), ("φ", MS),
          (" is therefore a union of affine subspaces, each of dimension ", {}), ("(H − 1)d", M),
          (" in the position coordinates.", {})],
         [("It contains trajectories of arbitrarily large velocity and acceleration, and no rule internal to ", {}),
          ("ρ", M), ("φ", MS), (" selects among them.", {})]),
        "Maximality of the score implies nothing about plausibility.",
        "For a reach requirement the maximizers include trajectories of arbitrarily large velocity. This is why "
        "guidance uses a penalized objective with a smoothness term rather than the score alone. "
        "[App. A, prop:spurious-maxima, eq:optimal-set; §4.5]"))
    out.append(statement_slide(
        "Unbounded maximizers under avoidance", "nomax",
        "Pure safety requirement, its robustness as a minimum of clearances, and a supremum of plus infinity",
        ([("The predicate ", {}), ("μ", M), (" is an unsafe ball of radius ", {}), ("r", M), (" about ", {}),
          ("c", M), (".", {})],
         [("For the pure safety requirement ", {}), ("◻", M), ("[0,H−1]", MS), (" ¬μ", M),
          (" the score is unbounded above, so no maximizer exists.", {})],
         "With at least one reach conjunct the supremum is finite and attained.",
         "At a step covered only by avoidance conjuncts, displacing the waypoint of a maximizer far from every "
         "unsafe centre leaves the score unchanged, so the set of maximizers is unbounded.",
         "In neither case does the requirement bound the trajectory."),
        "The coordinates that the requirement leaves free are determined by a component other than the "
        "requirement, in STL-FM the learned prior.",
        "The second half of RQ2. Pure safety has no maximizer. With a reach conjunct the maximizers exist but are "
        "unbounded at time indices covered only by avoidance. In neither case does the requirement bound the "
        "trajectory. Control-synthesis formulations obtain the bound from the dynamics and costs, or conjoin a "
        "boundedness clause (Lindemann and Dimarogonas 2019). If asked about the STL Optimizer: it "
        "minimizes the violation penalty rather than ascending the score, so for it the result says only that no "
        "term of the requirement returns those coordinates to any region. [App. A, prop:no-maximizer, "
        "rem:violation-penalty; §2.2]"))
    out.append(statement_slide(
        "Maximization over plausible trajectories", "constrained",
        "Maximize the robustness score subject to the trajectory lying on the manifold of plausible trajectories",
        ([("The plausible trajectories are idealized as a compact ", {}), ("C", M), ("1", MSUP), (" submanifold ", {}),
          ("ℳ", M), (" of the trajectory space ", {}), ("𝒯", M), (", and the score is maximized on ", {}), ("ℳ", M),
          (" only.", {})],
         [("Existence. ", B), ("The maximum is attained on ", {}), ("ℳ", M),
          (", even where the unconstrained supremum is unattained or infinite, as for pure safety. Compactness of ",
           {}), ("ℳ", M), (" provides the bound that the requirement lacks.", {})],
         [("Determinacy. ", B), ("For a generic embedding of ", {}), ("ℳ", M), (" the maximizers on ", {}),
          ("ℳ", M), (" are isolated, except where ", {}), ("ℳ", M), (" is tangent to the flat directions. In ", {}),
          ("𝒯", M), (" they are not isolated, as the sparsity and reach results show.", {})],
         [("Plausibility. ", B), ("Every constrained maximizer lies in ", {}), ("ℳ", M),
          (", so the implausible maximizers of a reach requirement are excluded whenever they lie off ", {}),
          ("ℳ", M), (".", {})]),
        "The learned prior satisfies neither hypothesis, so whether it provides the bound is measured in the "
        "experiments, not assumed.",
        "Under idealized conditions, a compact manifold of plausible trajectories, the constrained problem "
        "attains its maximum and its maximizers are isolated. The learned prior satisfies neither hypothesis. A "
        "flow-matching sampler has support on the whole trajectory space, and the guided sampler realizes a soft "
        "penalty rather than the hard constraint. The contribution of the prior is therefore measured in the "
        "experiments, not assumed. [App. A, eq:constrained-problem, thm:prior-resolves, rem:prior-idealization]"))

    # constant guidance strength (the former talk slide, rebuilt from the thesis expressions)
    s = content("Constant guidance strength", backup=True)
    eqimg(s, "bounded", 6.67, 2.25, align="c", descr="Diffusion score, flow-matching target velocity, and the bound "
          "on the guided velocity")
    s.add(label(s, CX, 4.55, CW, 0.80,
                ([("Both terms are of the same bounded order at every flow time, so the ratio of guidance to prior is ", {}),
                  ("Θ(λ", M), ("0", SUB), (")", M)],
                 [("and a constant ", {}), ("λ", M), ("0", SUB), (" is well posed without a schedule.  ", {}), ("λ", M),
                  ("0", SUB), (" = 50 in navigation and cube, without retuning.", {})]),
                size=17, color=INK, align="ctr"))
    s.add(label(s, CX, 5.55, CW, 0.70,
                ("On a diffusion substrate the guidance weight is coupled to the noise schedule,",
                 [("λ(t) ∝ σ", {}), ("t", SUB), ("k", {"sup": True}), (" with k ∈ {1, 2}.", {})]),
                size=15, align="ctr"))
    s.notes = ("Why one constant strength is well posed. The diffusion score grows like 1 over sigma_t squared as the "
               "noise vanishes, so a constant guidance weight has an influence that varies with the noise level, and "
               "diffusion guidance needs a schedule. Under the straight-line path the flow-matching target is tau_1 "
               "minus tau_0, of order one at every flow time, and the conditioned gradient has unit norm, so the "
               "guided velocity is bounded uniformly in s. One lambda_0 therefore has the same meaning throughout "
               "the flow. The claim is that a constant is well posed, not that it suffices in every setting. The same "
               "lambda_0 = 50 is used in navigation and cube without retuning. [eq:tweedie; §3.3; "
               "§4.6, eq:guided-bounded; tab:diffusion-vs-fm]")
    out.append(s)

    out.append(statement_slide(
        "Compilation and smoothing bias", "smoothing_bias",
        "Log-sum-exp brackets the exact maximum and minimum within log n over kappa, and a compiled score above "
        "L kappa to the minus one log n implies satisfaction",
        ("A formula is compiled by a post-order traversal of its syntax tree, with no learned component.",
         [("A predicate returns its margin ", {}), ("h", M), (" at every step, and negation changes the sign.", {})],
         "Conjunction and always return smin, disjunction and eventually smax, and until a nested combination "
         "of both.",
         [("Over ", {}), ("n", M), (" arguments the surrogate lies within ", {}), ("log n / κ", M),
          (" of the exact extremum, so the compiled score converges to the exact score as ", {}), ("κ", M),
          (" grows.", {})],
         [("At finite ", {}), ("κ", M), (" a compiled score above ", {}), ("Lκ", M), ("−1", MSUP), (" log n", M),
          (" implies satisfaction, where ", {}), ("L", M), (" is the depth of the syntax tree and ", {}), ("n", M),
          (" the largest arity of its nodes.", {})]),
        [("Guidance uses ", {}), ("κ", M), (" = 10, and satisfaction is always scored with the exact semantics.", {})],
        "The compilation is a post-order traversal of the syntax tree with no learned component. Smoothing "
        "replaces min and max by log-sum-exp. The bias is bounded by log n over kappa per node, and "
        "soundness is recovered exactly as kappa grows. kappa = 10 in the experiments, and satisfaction is "
        "scored with the exact semantics. [§4.2, alg:build-rho, prop:smoothing-bias]", size=16))
    out.append(statement_slide(
        "Steps of the guided sampler", "sampler",
        "Predicted endpoint, and the constant-strength step of the guided sampler",
        ([("The sampler takes the requirement score ", {}), ("ρ", M), ("φ", MS), (", the start state, the prior "
          "field ", {}), ("v", M), ("θ", MS), (", the guidance strength ", {}), ("λ", M), ("0", SUB),
          (", the smoothness weight ", {}), ("γ", M), (" and the number of steps ", {}), ("K", M), (".", {})],
         [("1.   ", B), ("τ", M), (" is drawn from ", {}), ("𝒩(0, I)", M), (", and its start state is pinned.", {})],
         [("2.   ", B), ("At each step ", {}), ("k = 0, …, K − 1", M), (", with ", {}), ("s = kΔs", M),
          (" and ", {}), ("Δs = 1/K", M), (", the prior velocity ", {}), ("v", M), ("θ", MS), ("(τ, s)", M),
          (" is evaluated.", {})],
         [("3.   ", B), ("The predicted endpoint ", {}), ("τ̂", M), (" is formed from the straight-line path.", {})],
         [("4.   ", B), ("The gradient ", {}), ("g", M), (" of the penalized objective is taken at ", {}), ("τ̂", M),
          (", masked to the position coordinates and normalized.", {})],
         [("5.   ", B), ("The iterate is advanced by the prior step plus ", {}), ("λ", M), ("0", SUB),
          (" g Δs", M), (", and the start state is pinned again.", {})]),
        "An optional clamp on the guidance increment is part of the sampler and is off in all reported runs.",
        "The sampler in full. The predicted endpoint, the penalized requirement gradient, masking and "
        "normalization, the constant-strength update and the re-pinned start state are the steps of the "
        "guided-sampler slide. The optional clamp is off in all reported runs. [§4.7, alg:guided-ode]"))

    # reproducing the STL Optimizer
    s = content("Reproducing the STL Optimizer",
                subtitle="Removes the learned prior and optimizes the robustness score directly, instead of "
                         "sampling from a trained generative model",
                backup=True)
    steps = [
        ("Controls, not states", "A free control sequence u, one 2D step per time index, starts from small "
         "random noise"),
        ("Single-integrator dynamics", "p[t+1] = p[t] + u[t]·Δt turns the controls into the trajectory that "
         "gets scored"),
        ("Same compiled score", "The requirement is scored by the masked, differentiable ρφ that STL-FM's "
         "guidance also uses (stljax / STLCG++)"),
        ("Violation objective, no prior", "Plain gradient descent on max(0, −ρφ); a finite-difference "
         "smoothness penalty and a velocity limit stand in for a learned prior"),
        ("Budget", "1,500–6,000 gradient steps, with the smoothing sharpness annealed from soft to sharp"),
    ]
    for r, (head, line) in enumerate(steps):
        y = 2.40 + 0.70 * r
        s.add(label(s, 0.70, y, 3.30, 0.66, head, size=16, color=INK, bold=True, anchor="ctr"))
        s.add(label(s, 4.10, y, 8.58, 0.66, line, size=15, color=INK, anchor="ctr"))
    s.add(label(s, CX, 6.30, CW, 0.55,
                "The robustness engine is shared with STL-FM; the optimization built around it, single-integrator "
                "dynamics and the violation penalty, is a standard direct-optimization baseline, not something "
                "STLCG++ itself proposes.", size=14))
    s.notes = ("How the STL Optimizer is actually computed, since it is named for what it scores rather than for "
               "how it works. Controls "
               "for a single integrator start as small random noise and are integrated into a trajectory at every "
               "gradient step, p of t plus 1 equals p of t plus u of t times delta t. That trajectory is scored by "
               "the same masked, differentiable robustness construction that stljax slash STLCG plus plus "
               "provides, and that STL-FM's own guidance term uses at every one of its integration steps. What "
               "differs is the objective: plain gradient descent on the violation penalty, max of zero and minus "
               "rho, with a hand-specified finite-difference smoothness penalty and a velocity limit taking the "
               "place of a learned prior, run for 1,500 to 6,000 steps with the log-sum-exp temperature annealed "
               "from soft to sharp. STLCG++ supplies the differentiable score; it does not propose this "
               "optimization design, which follows standard direct STL trajectory optimization "
               "(Belta and Vasile 2020). [§5.1.3]")
    out.append(s)

    out.append(crop_slide("Navigation results, all four planners", ["bk_tab_openloop", "bk_tab_anytime"],
               "The upper table gives satisfaction and mean robustness over 100 runs, and a star marks entries whose "
               "plans all leave the arena. Classes 1 to 6 are reach, nested reach-and-dwell, recurrence, sequence, "
               "sequence with avoidance and composite, and classes 7 to 10 are choice of target, choice of sequence, "
               "ordered visit and avoidance until reach. The lower table gives, per class, when each planner first "
               "satisfies the requirement and when it reaches its best robustness, as percentages of its budget, and "
               "the wall-clock plan time in seconds. STL-FM with endpoint pin differs from STL-FM by at most 0.05 on "
               "classes 1 to 6. [tab:openloop, tab:anytime; tab:families]",
               stack=True))

    # disjunction and until, classes 7 to 10 (not in the report the examiner received)
    s = content("Disjunction and until in navigation", backup=True)
    extra = [("choice", "Choice of target", "◇μ₁ ∨ ◇μ₂"), ("choiceseq", "Choice of sequence", "(◇μ₁ ∧ ◇μ₃) ∨ (◇μ₂ ∧ ◇μ₃)"),
             ("ordered", "Ordered visit", "(¬μ₂ U μ₁) ∧ ◇μ₂"), ("avoiduntil", "Avoidance until reach", "(¬μ₃ ∧ ¬μ₄) U μ₁")]
    for k, (key, name, form) in enumerate(extra):
        img = pdf_png(OL.format(f"{key}_guided"))
        x0 = CX + 3.03 * k
        s.add(label(s, x0, 2.00, 2.90, 0.28, name, size=13, color=INK, bold=True, align="ctr"))
        s.add(label(s, x0, 2.28, 2.90, 0.26, form, size=12, color=INK, align="ctr"))
        s.add(picture(s, img, *fit(img, x0 + 0.35, 2.56, 2.20, 1.85), f"STL-FM plans, {name}"), is_sp=False)
    cols = [("Class", 2.30, "l"), ("Endpoint-inpaint", 1.55, "ctr"), ("STL-FM", 1.30, "ctr"),
            ("STL-FM with pin", 1.55, "ctr"), ("STL Optimizer", 1.65, "ctr"), ("Plan time, STL-FM", 1.80, "ctr"),
            ("Plan time, STL Optimizer", 1.87, "ctr")]
    rows = [("Choice of target", "0.18", "0.98", "0.97", "0.98", "0.54 s", "23.02 s"),
            ("Choice of sequence", "0.02", "0.96", "0.94", "1.00†", "0.75 s", "22.92 s"),
            ("Ordered visit", "0.05", "0.27", "0.96", "0.00†", "5.72 s", "–"),
            ("Avoidance until reach", "0.03", "0.97", "0.98", "1.00†", "4.69 s", "32.03 s")]
    xs = [CX]
    for _, w, _a in cols[:-1]:
        xs.append(xs[-1] + w)
    y = 4.52
    for (h, w, al), x in zip(cols, xs):
        s.add(label(s, x, y, w, 0.30, h, size=12, color=INK, bold=True, align=al))
    s.add(rule(s, CX, CX + sum(c[1] for c in cols), y + 0.33))
    for i, row in enumerate(rows):
        yy = y + 0.40 + 0.31 * i
        for (h, w, al), x, v in zip(cols, xs, row):
            s.add(label(s, x, yy, w, 0.30, v, size=12, color=INK, align=al))
    s.add(rule(s, CX, CX + sum(c[1] for c in cols), y + 0.40 + 0.31 * 4 + 0.02))
    s.add(label(s, CX, 6.30, CW, 0.30, "Satisfaction over 100 runs, and plan time as a median over satisfying timing runs. "
                "† every plan leaves the arena. The STL Optimizer fails ordered visit at a local optimum "
                "of its objective", size=12, color=MUTED))
    s.notes = ("Added after the report: four navigation classes that use disjunction, choice of target and choice of "
               "sequence, and until, ordered visit and avoidance until reach, instantiated in the scene of the "
               "composite class. Panels show STL-FM, 25 of 100 runs. Under STL-FM the satisfied branch of a "
               "disjunction varies between runs. On choice of target 52 plans reach the distant target and 54 the "
               "near one, and on choice of sequence 14 take the branch through the first target and 84 the shorter "
               "branch, whereas the STL Optimizer always takes the branch through the near target. On "
               "ordered visit the first target lies 7.95 world units from the start and the second only 1.96, and the "
               "until operator forbids entering the second before the first. The STL Optimizer enters the "
               "near target first in every run. It fails at a local optimum and not because the instance is "
               "infeasible: the reach conjunct for the second target attains its value at an early waypoint near it, "
               "where its gradient is opposite to that of the until conjunct. Started from a plan that visits the "
               "first target first, it satisfies the instance, and with the second target's window moved to steps 31 "
               "to 63 it satisfies 19 of 20 runs. STL-FM satisfies 0.27 of runs, and STL-FM with endpoint pin 0.96, "
               "because the pinned final state satisfies the reach conjunct at the final index. The plan time of "
               "STL-FM on the two until classes, 4.7 and 5.7 s against 0.42 to 1.15 s elsewhere, is attributed to the "
               "compiled until, which is evaluated once for every end index of its window. Over all ten classes the "
               "estimated time to first satisfaction is 0.10 to 2.56 s for STL-FM and 0.83 to 7.29 s for the "
               "optimizer, excluding ordered visit. [§5.2.1, tab:openloop; §5.2.3, tab:anytime; app:ordered-visit, "
               "tab:ordered-visit; tab:families]")
    out.append(s)

    s = content("Robustness against budget", backup=True)
    for k, (key, name) in enumerate(classes):
        img = pdf_png(f"2D/anytime_{key}.pdf")
        col, row_ = k % 5, k // 5
        x0, y0 = CX + 2.42 * col, 2.05 + 2.30 * row_
        s.add(label(s, x0, y0, 2.32, 0.30, name, size=12, color=INK, bold=True, align="ctr"))
        s.add(picture(s, img, *fit(img, x0, y0 + 0.30, 2.32, 1.95), f"Robustness against budget, {name}"),
              is_sp=False)
    s.notes = ("Robustness against progress through each planner's own budget, one panel per class, as the median "
               "over 100 runs with an interquartile band. The step axis is normalized per planner, so the comparison "
               "is of shape and not of cost. The dashed line is the satisfaction threshold. STL-FM reaches its "
               "largest robustness at 95 to 100 percent of its budget on the five history-dependent classes of the "
               "fragment, and the STL Optimizer at 10 to 57 percent on the classes it satisfies. "
               "[fig:anytime, fig:anytime-ext]")
    out.append(s)
    out.append(crop_slide("Cube results, all three classes", ["bk_tab_closedloop"],
               "In the table, sat is logic satisfaction on the plan, task is success on the rollout, and gap is the "
               "median carry gap in centimetres. Classes 2, 4 and 5 are nested reach-and-dwell, sequence and sequence "
               "with avoidance. The pooled row gives the medians quoted in the talk, 12.5 cm for the STL "
               "Optimizer and 6.9 cm for STL-FM. [tab:closedloop; tab:families]"))

    # kitchen
    s = content("Kitchen study", backup=True)
    img = FIGS / "Kitchen/kitchen_planned_vs_executed.png"
    s.add(picture(s, img, *fit(img, CX, 2.75, 7.90, 4.00), "Planned against executed robustness, eighty runs"),
          is_sp=False)
    eqimg(s, "kitchen", CX + 3.95, 2.15, align="c", descr="phi equals eventually microwave and eventually kettle")
    img2 = FIGS / "Kitchen/scene_kitchen.png"
    s.add(picture(s, img2, *fit(img2, 8.85, TOP, 3.83, 3.00), "The kitchen"), is_sp=False)
    s.add(label(s, 8.85, 5.15, 3.83, 1.70, ("Complete-v2 prior, unguided,", "mean robustness of plan +0.23",
                                            "and of execution −0.45, a fall of 0.68",
                                            "against a margin of at most 0.3", "",
                                            "Task success in 0 of 80 executions"), size=14, color=INK))
    s.notes = ("D4RL kitchen. The requirement: open the microwave within steps 60 to 130, then move the kettle onto its "
               "burner within 140 to 230, with predicates on the fixtures' own state at the environment's tolerance. "
               "Two priors, complete-v2 and mixed, and two planners, the unguided prior and STL-FM, 20 runs each. Under "
               "complete-v2 every plan satisfies the requirement under both planners, because the demonstrations "
               "operate the fixtures in the required order, so guidance performs no selection. Under mixed, 6 of 20 "
               "without and 2 of 20 with guidance, no effect detected. No execution satisfies the "
               "requirement: the planned microwave crosses the threshold in every complete-v2 plan, the executed one "
               "in none. The prior generates the state, not the actions that produce it. [§5.4, tab:kitchen, §6.2]")
    out.append(s)

    # physical platform
    s = content("Physical platform", backup=True)
    img = FIGS / "GoFA/gofa_cell_wide.png"
    s.add(picture(s, img, *fit(img, CX, TOP, 6.45, 3.75), "The GoFA work cell"), is_sp=False)
    eqimg(s, "gofa", CX + 3.22, 6.05, align="c", descr="phi equals always between grasp and place, roll, pitch and "
          "yaw below 5 degrees")
    img2 = FIGS / "GoFA/gofa_prior_vs_demo.png"
    s.add(picture(s, img2, *fit(img2, 7.40, TOP, 2.70, 4.80), "Prior samples against the demonstration, "
                  "joint by joint"), is_sp=False)
    s.add(label(s, 10.30, 2.20, 2.38, 3.80, ("ABB GoFA CRB 15000,", "five door-opening", "demonstrations,",
                                             "six joint angles and", "the gripper state,", "H = 128", "", "No demonstration",
                                             "satisfies the carry", "requirement"),
                size=15, color=INK))
    s.notes = ("ABB GoFA CRB 15000-12/1.27 with a parallel gripper. Five door-opening demonstrations of 894 to 1872 "
               "frames at 15 fps. The prior generates six joint angles and the gripper state over 128 steps. The "
               "carry requirement states that between grasp and release the tool must not rotate by more than "
               "5 degrees about any axis, compiled through differentiable forward kinematics. No recorded "
               "demonstration satisfies it. Distance to the demonstration falls from 0.451 to 0.315 in the first "
               "10,000 steps and then stays flat; only smoothness keeps improving; diversity falls about sevenfold, "
               "measured on four samples per checkpoint. No plan has been executed on the robot. The carry interval "
               "is a proxy read from the gripper trace. [§5.5, tab:gofa-checkpoints, §6.3]")
    out.append(s)

    # roughness of guided plans
    s = content("Roughness of guided plans", backup=True)
    rows = [("Demonstrations", "0.6°", "2 %"), ("Unguided prior, start pinned", "6.4°", "4 %"),
            ("Unguided prior, both endpoints pinned", "8.2°", "7 %"),
            ("STL-FM, nested reach-and-dwell", "30.9°", "47 %"), ("STL-FM, recurrence", "9.9°", ""),
            ("STL-FM, composite", "", "18.5 %"), ("STL Optimizer, pooled", "0.3°", "")]
    cx = [0.70, 6.20, 8.60]; cw = [5.3, 2.2, 2.2]
    for x, w, h in zip(cx, cw, ["Trajectories", "Median turn angle", "Turns above 90°"]):
        s.add(label(s, x, 2.12, w, 0.32, h, size=14, align="l" if x < 1 else "ctr"))
    for r, row_ in enumerate(rows):
        y = 2.52 + 0.47 * r
        s.add(rule(s, 0.70, 10.80, y))
        for x, w, v in zip(cx, cw, row_):
            s.add(label(s, x, y + 0.05, w, 0.38, v, size=17, color=BLUE if row_[0].startswith("STL") else INK,
                        align="l" if x < 1 else "ctr", anchor="ctr"))
    s.add(rule(s, 0.70, 10.80, 2.52 + 0.47 * len(rows)))
    s.add(label(s, 0.70, 5.95, 12.0, 0.90,
                ("The evaluation does not distinguish two explanations. Either the prior is undertrained, or guidance",
                 "moves iterates away from plausible trajectories faster than the prior moves them back. The evidence",
                 "for the contribution of the prior is the carry gap and the arena excursion."), size=15))
    s.notes = ("Moving steps are steps longer than 0.05 world units. The prior does not reproduce the smoothness of its "
               "demonstrations, and guidance raises the turn angle on nested reach-and-dwell, where nearly half the "
               "turns exceed a right angle. On sequence and sequence with avoidance the guided plans are no rougher than "
               "the prior. The STL Optimizer is smoother than the demonstrations because of its "
               "hand-specified smoothness penalty. Two explanations remain open, and the evaluation does not "
               "distinguish them. The evidence for the contribution of the prior is the cube carry gap and the navigation "
               "excursion. [§5.2, §6.1]")
    out.append(s)

    # limitations
    s = content("Limitations", backup=True)
    lims = [("Fixed requirement instances", "every rate is measured on one instance per class"),
            ("No certificate", "the guided sampler is a soft realization, so it gives a rate, not a guarantee"),
            ("Sampled-state semantics", "robustness does not constrain the path between two sampled states"),
            ("Requirement-neutral prior", "a modelling assumption, although demonstrations can retain task structure"),
            ("Reproducibility", "runs with identical seeds agree on the satisfaction count in 27 of 28 cells and differ by one run in the other"),
            ("Physical carry interval", "a proxy read from the gripper trace, longer than the planning horizon")]
    for r, (head, line) in enumerate(lims):
        y = 2.10 + 0.64 * r
        s.add(label(s, 0.70, y, 4.0, 0.56, head, size=17, color=INK, bold=True, anchor="ctr"))
        s.add(label(s, 4.80, y, 7.88, 0.56, line, size=16, color=INK, anchor="ctr"))
    s.notes = "The limitations, one line each. [§6.3]"
    out.append(s)

    return out


# ───────────────────────────── package assembly ─────────────────────────────
NOTES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
    '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1" '
    'noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
    '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
    '{paras}</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')


def notes_xml(text):
    paras = "".join(f'<a:p><a:r><a:rPr lang="en-GB" dirty="0"/><a:t>{escape(p)}</a:t></a:r></a:p>'
                    for p in text.split("\n"))
    return NOTES_XML.replace("{paras}", paras)


def build():
    work = Path(tempfile.mkdtemp(prefix="stlfm_deck_"))
    u = work / "u"
    with zipfile.ZipFile(SRC) as z:
        z.extractall(u)
    ct_path = u / "[Content_Types].xml"
    # the template's main part is a template; the output is a presentation, and it carries videos
    ct = ct_path.read_text(encoding="utf-8").replace(
        "presentationml.template.main+xml", "presentationml.presentation.main+xml")
    if 'Extension="mp4"' not in ct:
        ct = ct.replace("<Default ", '<Default Extension="mp4" ContentType="video/mp4"/><Default ', 1)
    ct_path.write_text(ct, encoding="utf-8")
    (u / "ppt/notesSlides/_rels").mkdir(parents=True, exist_ok=True)

    made = []
    for i, s in enumerate(slides(), start=1):
        name = add_slide.create_slide_from_layout(u, s.layout)
        made.append(name)
        (u / "ppt/slides" / name).write_text(slide_xml(s), encoding="utf-8")
        rels = [f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                f'relationships/slideLayout" Target="../slideLayouts/{s.layout}"/>']
        for rid, kind, target in s.media:
            typ = kind if kind.startswith("http") else \
                f"http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}"
            rels.append(f'<Relationship Id="{rid}" Type="{typ}" Target="{target}"/>')
        for p in s.pending_media:
            shutil.copy2(p, u / "ppt/media" / p.name)
        if s.notes:
            num = re.search(r"\d+", name).group(0)
            nname = f"notesSlideS{num}.xml"
            (u / "ppt/notesSlides" / nname).write_text(notes_xml(s.notes), encoding="utf-8")
            (u / "ppt/notesSlides/_rels" / f"{nname}.rels").write_text(
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://'
                'schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://'
                'schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../'
                f'notesMasters/notesMaster1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.'
                f'org/officeDocument/2006/relationships/slide" Target="../slides/{name}"/></Relationships>',
                encoding="utf-8")
            rels.append(f'<Relationship Id="rId{len(s.media) + 2}" Type="http://schemas.openxmlformats.org/'
                        f'officeDocument/2006/relationships/notesSlide" Target="../notesSlides/{nname}"/>')
            ct = ct_path.read_text(encoding="utf-8")
            ct = ct.replace("</Types>", f'<Override PartName="/ppt/notesSlides/{nname}" ContentType="'
                            'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
                            "</Types>")
            ct_path.write_text(ct, encoding="utf-8")
        (u / "ppt/slides/_rels" / f"{name}.rels").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.'
            f'openxmlformats.org/package/2006/relationships">{"".join(rels)}</Relationships>', encoding="utf-8")

    # keep only the new slides, in order
    pres = (u / "ppt/presentation.xml").read_text(encoding="utf-8")
    prels = (u / "ppt/_rels/presentation.xml.rels").read_text(encoding="utf-8")
    ids = []
    for name in made:
        rid = re.search(rf'Id="(rId\d+)"[^>]*Target="slides/{name}"', prels).group(1)
        sid = re.search(rf'<p:sldId id="(\d+)" r:id="{rid}"/>', pres).group(1)
        ids.append(f'<p:sldId id="{sid}" r:id="{rid}"/>')
    pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", f"<p:sldIdLst>{''.join(ids)}</p:sldIdLst>", pres, flags=re.S)
    pres = re.sub(r"<p:ext uri=\"\{521415D9-36F7-43E2-AB2F-B90AF26B5E84\}\">.*?</p:ext>", "", pres, flags=re.S)
    # the template embeds a subset of Figtree; PowerPoint draws runs whose glyphs the subset lacks as
    # garbage, so drop it and let PowerPoint use an installed Figtree or substitute a font
    pres = re.sub(r"<p:embeddedFontLst>.*?</p:embeddedFontLst>", "", pres, flags=re.S)
    pres = pres.replace(' embedTrueTypeFonts="1"', "")
    prels = re.sub(r'<Relationship [^>]*relationships/font"[^>]*/>', "", prels)
    (u / "ppt/_rels/presentation.xml.rels").write_text(prels, encoding="utf-8")
    shutil.rmtree(u / "ppt/fonts", ignore_errors=True)
    (u / "ppt/presentation.xml").write_text(pres, encoding="utf-8")

    subprocess.run([sys.executable, str(SKILL / "scripts/clean.py"), str(u)], check=True,
                   stdout=subprocess.DEVNULL)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(u.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(u).as_posix())
    shutil.rmtree(work)
    print(f"wrote {OUT} ({len(made)} slides)")


if __name__ == "__main__":
    build()
