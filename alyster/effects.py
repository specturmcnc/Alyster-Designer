"""effects.py - text animations. apply() turns one picture (list of strings) into one animation frame.
Add your own: write a function, add it to FX."""
import random

GL = "⣿⠿⡇#%01▒"
EMPTY = " ⠀"
NAMES = ["none", "glitch", "reveal", "typewriter", "dissolve", "decode", "scan", "rain", "wave", "flicker", "melt", "sparkle", "shake", "slide", "matrix"]


def _glitch(L, i, p, rnd):
    R = len(L)
    for _ in range(2):
        if rnd.random() < .6:
            y, sh = rnd.randrange(R), rnd.randrange(11) - 5
            s = "".join(L[y]); q = (" " * sh + s[:len(s) - sh]) if sh > 0 else (s[-sh:] + " " * -sh)
            L[y] = list(q)
    return [[GL[rnd.randrange(len(GL))] if c not in EMPTY and rnd.random() < .015 else c for c in r] for r in L]


def _reveal(L, i, p, rnd):
    up = int(len(L) * p)
    return [r if y <= up else [" "] * len(r) for y, r in enumerate(L)]


def _typewriter(L, i, p, rnd):
    W = len(L[0]); k = int(p * len(L) * W); out = []
    for y, r in enumerate(L):
        row = [c if y * W + x < k else " " for x, c in enumerate(r)]
        if p < 1 and y * W <= k < (y + 1) * W: row[k - y * W] = "█"
        out.append(row)
    return out


def _thr(L):
    r = random.Random(1234); return [[r.random() for _ in row] for row in L]


def _dissolve(L, i, p, rnd):
    t = _thr(L); return [[c if t[y][x] < p else " " for x, c in enumerate(r)] for y, r in enumerate(L)]


def _decode(L, i, p, rnd):
    t = _thr(L)
    return [[c if (t[y][x] < p or c in EMPTY) else GL[rnd.randrange(len(GL))] for x, c in enumerate(r)] for y, r in enumerate(L)]


def _scan(L, i, p, rnd):
    y0 = (i * 2) % len(L)
    return [[("─" if c in EMPTY else "█") for c in r] if y == y0 else r for y, r in enumerate(L)]


def _rain(L, i, p, rnd):
    R = len(L); out = []
    for y, r in enumerate(L):
        row = []
        for x, c in enumerate(r):
            h = int(i * .8 + x * 7) % (R + 8)
            row.append(" " if y > h else "@" if y == h else c if y > h - 6 else (c if c in EMPTY else "·"))
        out.append(row)
    return out


def _wave(L, i, p, rnd):
    import math
    out = []
    for y, r in enumerate(L):
        sh = round(2 * math.sin(i * .5 + y * .4)); s = "".join(r)
        out.append(list((" " * sh + s[:len(s) - sh]) if sh > 0 else (s[-sh:] + " " * -sh) if sh < 0 else s))
    return out


def _flicker(L, i, p, rnd):
    return [[" " if c not in EMPTY and rnd.random() < .08 else c for c in r] for r in L]


def _melt(L, i, p, rnd):
    R, W = len(L), len(L[0]); out = [[" "] * W for _ in range(R)]
    for x in range(W):
        d = int(random.Random(x * 31).random() * R * .7 * p)
        for y in range(R):
            if L[y][x] not in EMPTY:
                out[min(R - 1, y + d)][x] = L[y][x]
    return out


def _sparkle(L, i, p, rnd):
    return [["✦" if c not in EMPTY and rnd.random() < .05 else c for c in r] for r in L]


def _shake(L, i, p, rnd):
    out = []
    for r in L:
        sh = rnd.randrange(-2, 3); s = "".join(r)
        out.append(list((" " * sh + s[:len(s) - sh]) if sh > 0 else (s[-sh:] + " " * -sh) if sh < 0 else s))
    return out


def _slide(L, i, p, rnd):
    W = len(L[0]); o = int(W * (1 - p)); out = []
    for r in L:
        s = "".join(r); out.append(list((" " * o + s)[:W]))
    return out


def _matrix(L, i, p, rnd):
    R = len(L); out = []
    for y, r in enumerate(L):
        out.append([c if (y > int(i * (1 + x % 3) * .7 + x * 5) % (R + 6) or c in EMPTY) else "01"[rnd.randrange(2)] for x, c in enumerate(r)])
    return out


FX = {"glitch": _glitch, "reveal": _reveal, "typewriter": _typewriter, "dissolve": _dissolve, "decode": _decode,
      "scan": _scan, "rain": _rain, "wave": _wave, "flicker": _flicker, "melt": _melt, "sparkle": _sparkle, "shake": _shake, "slide": _slide, "matrix": _matrix}


def apply(lines, fx, i, n):
    if fx not in FX or not lines:
        return lines
    p = min(1.0, i / max(1, int(n * .75)))  # progress 0..1, holds at the end
    return ["".join(r) for r in FX[fx]([list(x) for x in lines], i, p, random.Random(i * 7919 + 13))]


def animate(base, fx, n=30, dur=80):
    """base = [{"lines":[...], "dur":ms}]. A single picture becomes n frames; a GIF keeps its own frames."""
    if fx not in FX:
        return base
    if len(base) == 1:
        return [{"lines": apply(base[0]["lines"], fx, i, n), "dur": dur} for i in range(n)]
    return [{"lines": apply(f["lines"], fx, i, len(base)), "dur": f["dur"]} for i, f in enumerate(base)]
