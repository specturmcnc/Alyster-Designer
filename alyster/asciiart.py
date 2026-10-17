"""asciiart.py - turn an "L" image (white = ink) into rows of characters."""
import io, math
from PIL import Image, ImageOps
from designs import finish

RAMPS = {"Classic": " .:-=+*#%@", "Blocks": " ░▒▓█", "Braille": " ⠁⠃⠇⡇⣇⣧⣷⣿", "Solid": " █"}


def to_ascii(im, cols, ramp):
    w, h = im.size
    rows = max(1, round(cols * h / w * .5))
    px = im.resize((cols, rows), Image.LANCZOS).load()
    n = len(ramp)
    return ["".join(ramp[min(n - 1, px[x, y] * n // 256)] for x in range(cols)) for y in range(rows)]


def from_bytes(data, cols, ramp):
    """Uploaded photo or hand drawing (any format). Dark-on-light is flipped so the ink is dense."""
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGBA", im.size, "white")
        bg.alpha_composite(im.convert("RGBA"))
        im = bg
    im = im.convert("L")
    im.thumbnail((800, 800))
    if sum(im.resize((32, 32)).getdata()) / 1024 > 127:
        im = ImageOps.invert(im)
    return to_ascii(finish(im.point(lambda v: v if v > 24 else 0)), cols, ramp)


def gif_frames(data, cols, ramp, max_frames=150):
    """Animated GIF -> [{"lines": [...], "dur": ms}, ...]. Transparent areas count as empty."""
    cols = min(cols, 200)  # keeps big GIFs fast
    im = Image.open(io.BytesIO(data))
    n = getattr(im, "n_frames", 1)
    step = max(1, math.ceil(n / max_frames))
    out, inv = [], None
    for i in range(0, n, step):
        im.seek(i)
        fr = Image.new("RGBA", im.size, "black")
        fr.alpha_composite(im.convert("RGBA"))
        g = fr.convert("L")
        g.thumbnail((400, 400))
        if inv is None:  # decide once, so frames don't flicker
            inv = sum(g.resize((32, 32)).getdata()) / 1024 > 127
        if inv:
            g = ImageOps.invert(g)
        out.append({"lines": to_ascii(g, cols, ramp), "dur": max(30, int(im.info.get("duration", 100)) * step)})
    return out
