"""export.py - draw coloured text as PNG / animated GIF."""
import io
from PIL import Image, ImageDraw
import designs
from colors import N, bucket, color_at

BG = {"dark": (8, 3, 5, 255), "white": (255, 255, 255, 255), "transparent": (0, 0, 0, 0)}


def draw_frame(lines, stops, direction="x", bg="dark", cell=14):
    h, w = len(lines), len(lines[0])
    while True:
        font = designs.get_font("mono", cell)
        cw, lh, pad = font.getlength("M"), round(cell * 1.12), cell
        W, H = int(cw * w) + 2 * pad, lh * h + 2 * pad
        if W * H <= 30e6 or cell <= 4:
            break
        cell -= 1
    img = Image.new("RGBA", (W, H), BG.get(bg, BG["dark"]))
    d = ImageDraw.Draw(img)
    cols = [color_at(stops, i / (N - 1)) + (255,) for i in range(N)]
    for y, row in enumerate(lines):
        x = 0
        while x < w:
            s = bucket(direction, x, y, w, h); x2 = x
            while x2 < w and bucket(direction, x2, y, w, h) == s:
                x2 += 1
            run = row[x:x2]
            if run.strip(" ⠀"):
                d.text((pad + x * cw, pad + y * lh), run, font=font, fill=cols[s])
            x = x2
    return img


def to_png(frame, **kw):
    buf = io.BytesIO(); draw_frame(frame["lines"], **kw).save(buf, "PNG"); return buf.getvalue()


def to_gif(frames, **kw):
    if kw.get("bg") == "transparent":
        kw["bg"] = "dark"  # GIF can't do soft transparency
    ims = [draw_frame(f["lines"], **kw).convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=96) for f in frames]
    buf = io.BytesIO()
    ims[0].save(buf, "GIF", save_all=True, append_images=ims[1:], duration=[f["dur"] for f in frames], loop=0, disposal=2)
    return buf.getvalue()
