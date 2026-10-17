"""colors.py - gradient maths shared by the PNG / GIF export (the page uses the same formula)."""
N = 48  # colour steps across the picture


def parse_stops(text):
    out = []
    for h in (text or "").split(","):
        h = h.strip()
        if len(h) == 7 and h[0] == "#":
            try:
                out.append(tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)))
            except ValueError:
                pass
    return out if len(out) >= 2 else [(255, 77, 141), (77, 124, 255)]


def color_at(stops, t):
    seg = max(0.0, min(1.0, t)) * (len(stops) - 1)
    k = min(int(seg), len(stops) - 2)
    f = seg - k
    return tuple(round(stops[k][j] + (stops[k + 1][j] - stops[k][j]) * f) for j in range(3))


def bucket(direction, x, y, w, h):
    tx, ty = x / max(1, w - 1), y / max(1, h - 1)
    t = tx if direction == "x" else ty if direction == "y" else (tx + ty) / 2
    return min(N - 1, int(t * N))
