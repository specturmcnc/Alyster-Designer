#!/usr/bin/env python3
"""Alyster Designer tool - local web server.  Run:  python server.py   ->  http://localhost:8000"""
import argparse, io, json, mimetypes, os, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import designs, export
from asciiart import RAMPS, from_bytes, gif_frames, to_ascii
from colors import parse_stops
from effects import NAMES as FX_NAMES, animate

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def clamp(v, lo, hi, default):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return default


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def json(self, obj, code=200):
        self.send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def png(self, im):
        buf = io.BytesIO(); im.save(buf, "PNG"); self.send(200, buf.getvalue(), "image/png")

    def args(self):
        q = parse_qs(urlparse(self.path).query)
        g = lambda k, d=None: q.get(k, [d])[0]
        n = len(designs.all_designs())
        fx = g("fx", "none")
        return {
            "text": ((g("text", "S") or "S").strip()[:designs.MAX_CHARS] or "S"),
            "id": clamp(g("id"), 0, n - 1, 0), "wrap": clamp(g("wrap"), 4, 60, 14),
            "cols": clamp(g("cols"), 20, 600, 70), "size": clamp(g("size"), 40, 800, 150),
            "ramp": RAMPS.get(g("ramp", "Classic"), RAMPS["Classic"]),
            "fx": fx if fx in FX_NAMES else "none", "src": g("src", "design"),
            "stops": parse_stops(g("stops")), "dir": g("dir", "x") if g("dir") in ("x", "y", "d") else "x",
            "bg": g("bg", "dark"), "cell": clamp(g("cell"), 6, 40, 14), "frame": clamp(g("frame"), 0, 10_000, 0),
            "format": g("format", "png"),
        }

    def frames_for(self, a, data):
        if a["src"] == "lines":
            L = [str(t)[:600] for t in json.loads(data.decode("utf-8"))["lines"][:300]] or [" "]
            w = max(len(t) for t in L) or 1
            base = [{"lines": [t.ljust(w) for t in L], "dur": 100}]
        elif a["src"] == "gif":
            base = gif_frames(data, a["cols"], a["ramp"])
        elif a["src"] == "image":
            base = [{"lines": from_bytes(data, a["cols"], a["ramp"]), "dur": 100}]
        else:
            base = [{"lines": to_ascii(designs.render(a["text"], a["id"], a["wrap"]), a["cols"], a["ramp"]), "dur": 100}]
        return animate(base, a["fx"])

    def route(self, path, data=b""):
        a = self.args()
        if path == "/api/designs":
            return self.json({"designs": [{"id": i, "name": n} for i, (n, _) in enumerate(designs.all_designs())],
                              "ramps": list(RAMPS), "effects": FX_NAMES})
        if path == "/api/thumb":
            return self.png(designs.thumb(designs.render(a["text"].split("\n")[0][:10], a["id"]), a["size"]))
        if path == "/api/frames":
            return self.json({"frames": self.frames_for(a, data)})
        if path == "/api/export":
            frames = self.frames_for(a, data)
            kw = dict(stops=a["stops"], direction=a["dir"], bg=a["bg"], cell=a["cell"])
            if a["format"] == "gif":
                return self.send(200, export.to_gif(frames, **kw), "image/gif")
            return self.send(200, export.to_png(frames[a["frame"] % len(frames)], **kw), "image/png")
        self.json({"error": "unknown endpoint"}, 404)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path.startswith("/api/"):
                return self.route(path)
            rel = "index.html" if path == "/" else path.lstrip("/")
            full = os.path.normpath(os.path.join(STATIC, rel))
            if not full.startswith(STATIC) or not os.path.isfile(full):
                return self.send(404, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
            with open(full, "rb") as f:
                self.send(200, f.read(), ctype + ("; charset=utf-8" if ctype.startswith("text/") or ctype.endswith("javascript") else ""))
        except Exception as e:
            self.json({"error": str(e)}, 500)

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", 0))
            if size > 30_000_000:
                return self.json({"error": "file too large (30 MB max)"}, 413)
            self.route(urlparse(self.path).path, self.rfile.read(size))
        except Exception as e:
            self.json({"error": f"could not process that: {e}"}, 400)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    o = ap.parse_args()
    url = f"http://localhost:{o.port}"
    print(f"Alyster Designer tool running at {url}   (Ctrl+C to stop)")
    if not o.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", o.port), Handler).serve_forever()
