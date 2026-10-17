"""designs.py - every letter design lives here (Pillow only).

A design is a function  f(text) -> "L" image  (white = ink, black = empty).
Add your own: write a function, then add ("Name", function) to DESIGNS.
Or drop .ttf / .otf files into ./fonts - each one becomes a design automatically.
"""
import os, math, textwrap, threading
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

APP = "Alyster Designer tool"
S = 360  # working canvas size
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, "fonts"), os.path.join(HERE, "fonts_builtin"), "C:/Windows/Fonts", "/usr/share/fonts",
             "/usr/local/share/fonts", "/Library/Fonts", "/System/Library/Fonts",
             os.path.expanduser("~/.fonts"), os.path.expanduser("~/Library/Fonts"),
             os.path.expanduser("~/.local/share/fonts")]
FONT_WANT = {
    "bold": ["georgiab", "timesbd", "playfairdisplaybold", "dejavuserifbold", "liberationserifbold", "notoserifbold", "freeserifbold"],
    "reg": ["georgia", "times", "dejavuserif", "liberationserifregular", "notoserifregular", "freeserif"],
    "italic": ["georgiai", "timesi", "dejavuserifitalic", "liberationserifitalic", "notoserifitalic", "freeserifitalic"],
    "script": ["pacifico", "pacificoregular", "lobster", "lobsterregular", "brushsci", "segoesc", "lhandw",
               "dancingscript", "greatvibesregular", "satisfyregular", "georgiai", "timesi", "dejavuserifitalic", "liberationserifitalic"],
    "sans": ["poppinsbold", "arialbd", "archivoblack", "dejavusansbold", "liberationsansbold"],
    "geo": ["poppinsbold", "arialbd", "dejavusansbold"],
    "mono": ["dejavusansmonobold", "consolab", "courbd", "liberationmonobold"],
}

# ------------------------------------------------------------------ fonts
def norm(s): return "".join(c for c in s.lower() if c.isalnum())
_IDX = None
def font_index():
    global _IDX
    if _IDX is None:
        _IDX = {}
        for d in FONT_DIRS:
            for r, _, fs in os.walk(d):
                for f in fs:
                    if f.lower().endswith((".ttf", ".otf")):
                        _IDX.setdefault(norm(os.path.splitext(f)[0]), os.path.join(r, f))
    return _IDX

def find_font(key):
    idx = font_index()
    for c in FONT_WANT.get(key, []):
        if norm(c) in idx: return idx[norm(c)]
    return None

def get_font(key, size):
    path = key if os.path.isfile(key) else find_font(key)
    for p in [path, "DejaVuSerif-Bold.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"]:
        if p:
            try: return ImageFont.truetype(p, size)
            except OSError: pass
    try: return ImageFont.load_default(size)
    except TypeError: return ImageFont.load_default()

_ctx = threading.local()
_sizes = {}
MAX_CHARS = 5000

def _line_size(key):
    """One font size for every letter of a word, so they line up."""
    if key not in _sizes:
        size = int(S * .95)
        while size > 24:
            f = get_font(key, size)
            try:
                _, t, _, b = f.getbbox("Hg", anchor="ms"); wl, _, wr, _ = f.getbbox("W", anchor="ms")
                if b - t < S * .9 and wr - wl < S * .9: break
            except Exception: break
            size -= 6
        _sizes[key] = size
    return _sizes[key]

def glyph(txt, key="bold"):
    if getattr(_ctx, "multi", False):  # inside a word: shared size + shared baseline
        f = get_font(key, _line_size(key)); im = Image.new("L", (S, S), 0)
        try:
            capH = -f.getbbox("H", anchor="ms")[1]; desc = f.getbbox("g", anchor="ms")[3]
            ImageDraw.Draw(im).text((S / 2, S / 2 + (capH - desc) / 2), txt, font=f, fill=255, anchor="ms"); return im
        except Exception: pass
    size = int(S * .95)
    while size > 24:
        f = get_font(key, size); l, t, r, b = f.getbbox(txt)
        if r - l < S * .86 and b - t < S * .86: break
        size -= 8
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).text((S / 2 - (l + r) / 2, S / 2 - (t + b) / 2), txt, font=f, fill=255)
    return im

def _line(fn, txt, memo):
    """One line of text: run the design per character, set the results side by side."""
    parts = []
    for ch in txt:
        if ch not in memo:
            im = None if ch.isspace() else fn(ch); bb = im.getbbox() if im else None
            memo[ch] = im.crop((bb[0], 0, bb[2], S)) if bb else None
        parts.append(memo[ch])
    gap, sp = int(S * .07), int(S * .30)
    W = sum(sp if p is None else p.width for p in parts) + gap * max(0, len(parts) - 1)
    out = Image.new("L", (max(W, 1), S), 0); x = 0
    for p in parts:
        if p is not None: out.paste(p, (x, 0)); x += p.width + gap
        else: x += sp + gap
    return out

def compose(fn, txt, wrap=14):
    """Any amount of text: new lines are kept, long lines wrap every `wrap` letters, lines stack."""
    if len(txt.strip()) == 1: return fn(txt.strip())
    lines = []
    for raw in txt.split("\n"):
        lines += textwrap.wrap(raw, wrap, break_long_words=True, break_on_hyphens=False) or [""]
    memo = {}; _ctx.multi = True
    try: ims = [_line(fn, l, memo) if l else None for l in lines]
    finally: _ctx.multi = False
    # keep huge texts from using huge memory: shrink everything by one shared factor
    est = (max(len(l) for l in lines) * S * .7 + 1) * (len(lines) * S * 1.1)
    f = min(1.0, math.sqrt(12e6 / est))
    if f < 1: ims = [None if i is None else i.resize((max(1, int(i.width * f)), max(1, int(i.height * f))), Image.LANCZOS) for i in ims]
    gap, blank_h = int(S * .12 * f), int(S * .5 * f)
    W = max([i.width for i in ims if i] or [1]); H = sum((i.height if i else blank_h) + gap for i in ims)
    out = Image.new("L", (W, max(1, H)), 0); y = 0
    for i in ims:
        if i: out.paste(i, ((W - i.width) // 2, y)); y += i.height + gap
        else: y += blank_h + gap
    return out

# ------------------------------------------------------------------ helpers
def erode(m, n): return m.filter(ImageFilter.MinFilter(n | 1))
def dilate(m, n): return m.filter(ImageFilter.MaxFilter(n | 1))
def sub(a, b): return ImageChops.subtract(a, b)
def clip(a, b): return ImageChops.multiply(a, b)
def add(*ims):
    r = ims[0]
    for i in ims[1:]: r = ImageChops.lighter(r, i)
    return r
def blank(): return Image.new("L", (S, S), 0)

def star(d, cx, cy, r):
    k = r * .22
    d.polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r),
               (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)], fill=255)

def leaf(d, x, y, L, ang, w):
    ca, sa = math.cos(ang), math.sin(ang); pts = []
    for sgn, rng in ((1, range(21)), (-1, range(20, -1, -1))):
        for i in rng:
            t = i / 20; px, py = t * L, sgn * w * math.sin(math.pi * t)
            pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
    d.polygon(pts, fill=255)

# ------------------------------------------------------------------ DESIGNS
def d_bold(t): return glyph(t, "bold")
def d_classic(t): return glyph(t, "reg")
def d_italic(t): return glyph(t, "italic")
def d_script(t): return glyph(t, "script")
def d_heavy(t): return dilate(glyph(t, "bold"), 9)
def d_light(t): return erode(glyph(t, "reg"), 3)
def d_outline(t):
    m = glyph(t, "bold"); return sub(m, erode(m, 13))
def d_double(t):
    m = glyph(t, "bold"); inner = erode(m, 21)
    return add(sub(m, erode(m, 9)), sub(inner, erode(inner, 9)))
def d_inline(t):
    m = glyph(t, "bold"); return sub(m, sub(erode(m, 15), erode(m, 25)))
def d_racing(t):
    m = glyph(t, "sans"); st = blank(); d = ImageDraw.Draw(st)
    for y in range(0, S, 26): d.rectangle([0, y, S, y + 12], fill=255)
    out = clip(m, st); d = ImageDraw.Draw(out)
    for i, y in enumerate((.70, .76, .82)): d.rectangle([S * .02, S * y, S * (.30 - i * .04), S * y + 8], fill=255)
    return out
def d_split(t):
    m = glyph(t, "bold"); b = blank()
    ImageDraw.Draw(b).polygon([(0, S * .25), (S, S * .75), (S, S * .83), (0, S * .33)], fill=255)
    return sub(m, b)
def d_sparkle(t):
    m = glyph(t, "reg"); s = blank(); d = ImageDraw.Draw(s)
    if getattr(_ctx, "multi", False):  # in a word: one small star on each letter's corner
        bb = m.getbbox()
        if bb: star(d, bb[2], bb[1], S * .06)
        return add(m, s)
    star(d, S * .5, S * .34, S * .07); star(d, S * .5, S * .68, S * .07)
    return ImageChops.difference(m, s)
def d_shadow(t):
    m = glyph(t, "bold"); return add(ImageChops.offset(m, 14, 14).point(lambda v: int(v * .42)), m)
def d_ribbon(t):
    m = glyph(t, "bold"); g = blank(); d = ImageDraw.Draw(g)
    for x in range(S): d.line([(x, 0), (x, S)], fill=int(90 + 165 * math.sin(math.pi * x / S) ** .8))
    return clip(m, g)
def d_brush(t):
    m = glyph(t, "script"); m = dilate(m, 7)
    n = Image.effect_noise((S, S), 90); rough = ImageChops.add(m.filter(ImageFilter.GaussianBlur(3)), n, 2.0)
    rough = rough.point(lambda v: 255 if v > 132 else 0)
    return clip(rough, dilate(m, 13))
def d_leaf(t):
    m = glyph(t, "bold"); d = ImageDraw.Draw(m)
    if getattr(_ctx, "multi", False): return m
    leaf(d, S * .72, S * .16, S * .16, -.9, S * .035); leaf(d, S * .82, S * .16, S * .14, -.3, S * .03)
    leaf(d, S * .22, S * .90, S * .16, 3.9, S * .035); leaf(d, S * .16, S * .84, S * .14, 3.3, S * .03)
    return m
def d_swash(t):
    m = erode(glyph(t, "script"), 3); d = ImageDraw.Draw(m)
    d.arc([S * .0, S * .35, S * 1.0, S * .98], 168, 352, fill=255, width=5)
    d.arc([S * .05, S * .40, S * .95, S * .96], 200, 330, fill=255, width=2)
    return m
def d_halftone(t):
    m = glyph(t, "bold"); p = blank(); d = ImageDraw.Draw(p)
    for y in range(0, S, 14):
        for x in range(0, S, 14): d.ellipse([x, y, x + 9, y + 9], fill=255)
    return clip(m, p)
def d_hatch(t):
    m = glyph(t, "bold"); p = blank(); d = ImageDraw.Draw(p)
    for k in range(-S, S * 2, 12): d.line([(k, 0), (k - S, S)], fill=255, width=5)
    return add(clip(m, p), sub(m, erode(m, 7)))
def d_neon(t):
    m = glyph(t, "sans"); ring = sub(m, erode(m, 11))
    return add(m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * .6)), ring)
def d_pixel(t):
    m = glyph(t, "bold").resize((20, 20), Image.BILINEAR).point(lambda v: 255 if v > 90 else 0)
    return m.resize((S, S), Image.NEAREST)

def d_geo(t): return glyph(t, "geo")
def d_calligraphy(t):
    m = dilate(glyph(t, "italic"), 5)  # thicken, then shave the horizontals -> pen contrast
    r = ImageChops.darker(ImageChops.darker(m, ImageChops.offset(m, 0, 4)), ImageChops.offset(m, 0, -4))
    return r.filter(ImageFilter.GaussianBlur(1)).point(lambda v: 255 if v > 110 else 0)
def d_stencil(t):
    m = glyph(t, "sans"); b = blank(); d = ImageDraw.Draw(b)
    for y in (.36, .64): d.rectangle([0, S * y - 5, S, S * y + 5], fill=255)
    d.rectangle([S * .5 - 5, 0, S * .5 + 5, S], fill=255)
    return sub(m, b)
def d_bevel(t):
    cur = glyph(t, "bold"); out = cur.point(lambda v: v // 5)
    for _ in range(4):
        cur = erode(cur, 7); out = ImageChops.add(out, cur.point(lambda v: v // 5))
    return out
def d_echo(t):
    m = glyph(t, "bold"); out = blank()
    for k in range(6, 0, -1):
        out = ImageChops.lighter(out, ImageChops.offset(m, -k * 12, 0).point(lambda v, k=k: int(v * (.5 - k * .07))))
    return ImageChops.lighter(out, m)
def d_fade(t):
    m = glyph(t, "bold"); g = blank(); d = ImageDraw.Draw(g)
    for y in range(S): d.line([(0, y), (S, y)], fill=int(40 + 215 * (1 - y / S)))
    return clip(m, g)
def d_stamp(t):
    m = glyph(t, "sans")
    specks = Image.effect_noise((S // 4, S // 4), 80).resize((S, S), Image.NEAREST).point(lambda v: 255 if v > 215 else 0)
    return sub(m, specks)
def d_dotted(t):
    m = glyph(t, "sans"); ring = sub(m, erode(m, 11)); p = blank(); d = ImageDraw.Draw(p)
    for y in range(0, S, 10):
        for x in range(0, S, 10): d.ellipse([x, y, x + 6, y + 6], fill=255)
    return clip(ring, p)

DESIGNS = [("Bold serif", d_bold), ("Classic", d_classic), ("Italic", d_italic), ("Script", d_script),
           ("Heavy", d_heavy), ("Light", d_light), ("Outline", d_outline), ("Double line", d_double),
           ("Inline", d_inline), ("Racing", d_racing), ("Split", d_split), ("Sparkle", d_sparkle),
           ("Shadow", d_shadow), ("Ribbon", d_ribbon), ("Brush", d_brush), ("Leaf", d_leaf),
           ("Swash", d_swash), ("Halftone", d_halftone), ("Hatch", d_hatch), ("Neon", d_neon), ("Pixel", d_pixel),
           ("Geometric", d_geo), ("Calligraphy", d_calligraphy), ("Stencil", d_stencil),
           ("Bevel", d_bevel), ("Echo", d_echo), ("Fade", d_fade), ("Stamp", d_stamp), ("Dotted", d_dotted)]

def custom_designs():
    out = []; d = os.path.join(HERE, "fonts")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.lower().endswith((".ttf", ".otf")):
                p = os.path.join(d, f); out.append(("Font: " + os.path.splitext(f)[0][:14], lambda t, p=p: glyph(t, p)))
    return out

def all_designs(): return DESIGNS + custom_designs()

def finish(im, margin=10):
    b = im.getbbox()
    if not b: return im
    return im.crop((max(0, b[0] - margin), max(0, b[1] - margin), min(im.width, b[2] + margin), min(im.height, b[3] + margin)))

_cache = {}
def render(txt, i, wrap=14):
    k = (txt, i, wrap)
    if len(_cache) > 400: _cache.clear()
    if k not in _cache: _cache[k] = finish(compose(all_designs()[i][1], txt, wrap))
    return _cache[k]

def thumb(im, box=132):
    v = ImageOps.invert(im).convert("RGB"); v.thumbnail((box, box))
    h = box if im.width / im.height < 1.4 else max(int(box * .6), v.height + 6)
    c = Image.new("RGB", (box, h), "white"); c.paste(v, ((box - v.width) // 2, (h - v.height) // 2)); return c
