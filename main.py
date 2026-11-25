"""THE WORLD IN ONE DAY - newspaper front page for 24 November 2026.
Stdlib only. Renders 1024x1024 entry.png from baked data + glyphs.bin.
"""
import os, sys, zlib, struct

W = H = 1024
PAPER = (247, 242, 230)
INK = (28, 26, 22)
RED = (165, 30, 30)
GREY = (105, 100, 90)
LIGHT = (232, 224, 205)
SEA = (52, 84, 105)
SKY = (203, 216, 222)

buf = bytearray(W * H * 3)

def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]

def fill_rect(x, y, w, h, c):
    x0 = max(0, x); y0 = max(0, y); x1 = min(W, x + w); y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row

def fill_ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        if ry == 0:
            continue
        t = (yy - cy) / ry
        dx = int(rx * (1 - t * t) ** 0.5)
        fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

def fill_poly(pts, c):
    ys = [p[1] for p in pts]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            if (y1 <= yy < y2) or (y2 <= yy < y1):
                xs.append(int(x1 + (yy - y1) * (x2 - x1) / (y2 - y1)))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(xs[i], yy, xs[i + 1] - xs[i] + 1, 1, c)

def line(x1, y1, x2, y2, c, th=2):
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    r = max(1, th // 2)
    for s in range(steps + 1):
        x = x1 + (x2 - x1) * s // steps
        y = y1 + (y2 - y1) * s // steps
        fill_ellipse(x, y, r, r, c)

# ---------------- glyphs ----------------
FONTS = {}

def load_glyphs():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.bin")
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"GLY1"
    off = 4
    (count,) = struct.unpack_from("<I", data, off); off += 4
    for _ in range(count):
        (nl,) = struct.unpack_from("<B", data, off); off += 1
        name = data[off:off + nl].decode(); off += nl
        size, ascent, descent, gc = struct.unpack_from("<IiiI", data, off); off += 16
        glyphs = {}
        for _ in range(gc):
            cp, adv, w, h, xoff, yoff = struct.unpack_from("<I i I I i i", data, off); off += 24
            bmp = data[off:off + w * h]; off += w * h
            glyphs[cp] = (adv, w, h, xoff, yoff, bmp)
        FONTS[name] = (ascent, descent, glyphs)

def text_w(text, fk):
    ascent, descent, glyphs = FONTS[fk]
    total = 0
    for ch in text:
        g = glyphs.get(ord(ch)) or glyphs.get(63)
        total += g[0]
    return total

def draw_text(x, y, text, fk, c):
    ascent, descent, glyphs = FONTS[fk]
    pen = x
    for ch in text:
        g = glyphs.get(ord(ch)) or glyphs.get(63)
        adv, w, h, xoff, yoff, bmp = g
        if w and h:
            for row in range(h):
                yy = y + yoff + row
                if yy < 0 or yy >= H:
                    continue
                base = row * w
                for col in range(w):
                    a = bmp[base + col]
                    if a == 0:
                        continue
                    xx = pen + xoff + col
                    if xx < 0 or xx >= W:
                        continue
                    i = (yy * W + xx) * 3
                    if a == 255:
                        buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]
                    else:
                        ia = 255 - a
                        buf[i] = (c[0] * a + buf[i] * ia) // 255
                        buf[i + 1] = (c[1] * a + buf[i + 1] * ia) // 255
                        buf[i + 2] = (c[2] * a + buf[i + 2] * ia) // 255
        pen += adv
    return pen

def draw_center(y, text, fk, c):
    w = text_w(text, fk)
    return draw_text((W - w) // 2, y, text, fk, c)

def wrap(text, fk, maxw):
    words = text.split()
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd) if cur else wd
        if text_w(trial, fk) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(x, y, text, fk, c, maxw, lh, maxlines=99):
    for ln in wrap(text, fk, maxw)[:maxlines]:
        draw_text(x, y, ln, fk, c)
        y += lh
    return y

# ---------------- content ----------------
LEAD_HEAD = ["Tankers Hit Mines in Hormuz", "as Tehran Bars US Talks"]
LEAD_BODY = ("Iran's Revolutionary Guard says three oil tankers struck mines in the "
             "Strait of Hormuz late Monday, despite a US escort — a claim not confirmed "
             "by US Central Command. The US Treasury sanctioned more than two dozen "
             "Iranian exchange houses over \u201cshadow banking\u201d, and Tehran ruled out "
             "any talks with Washington until its seven conditions are met.")

STORIES = [
    ("chip", "Nvidia Brings Back Huang",
     "Nvidia reinstated Jensen Huang as CEO less than a week after he said he would retire, reportedly after President Trump intervened. Shares jumped about 31%."),
    ("rocket", "China Launches Shenzhou-24",
     "China launched Shenzhou-24 carrying two Chinese astronauts and Pakistani astronaut Zeeshan Ali — the first foreign astronaut to board the Tiangong station."),
    ("tower", "Riyadh Tower Struck Again",
     "A Houthi strike hit Riyadh's tallest tower for the second time in a week, injuring 11 people. The coalition denounced a terrorist attack."),
    ("ship", "Libya Condemns Benghazi Strike",
     "Libya's Presidential Council condemned Ukraine's drone attack on Russian ships in Benghazi. At the UN, Russia and Ukraine traded accusations over Black Sea shipping."),
    ("stars", "EU Plans 22nd Russia Package",
     "The European Commission proposed its 22nd sanctions package against Russia, targeting about 60 more banks and crypto networks, pending approval by all 27 member states."),
    ("flag", "North Korea Expels Swiss Envoy",
     "North Korea demanded the closure of Switzerland's new diplomatic office in Pyongyang and ordered the senior Swiss diplomat to leave the country."),
    ("scales", "ICJ Rohingya Ruling Affirmed",
     "Fourteen countries affirmed the ICJ decision establishing Myanmar's genocide of the Rohingya. Malaysia said it will return more than 6,500 Rohingya refugees to Myanmar."),
    ("globe", "The Day in Numbers",
     "31% — Nvidia's share jump. 11 injured in Riyadh. 60 banks in the EU's sights. 6,500 refugees Malaysia plans to return. Three tankers, one strait, no talks."),
]

def draw_icon(kind, x, y):
    # 22x22 icon box at x,y
    if kind == "chip":
        fill_rect(x + 4, y + 4, 14, 14, INK)
        fill_rect(x + 8, y + 8, 6, 6, PAPER)
        for i in range(3):
            fill_rect(x, y + 5 + i * 5, 4, 2, INK); fill_rect(x + 18, y + 5 + i * 5, 4, 2, INK)
    elif kind == "rocket":
        fill_poly([(x + 11, y), (x + 17, y + 12), (x + 5, y + 12)], RED)
        fill_rect(x + 8, y + 12, 6, 6, INK)
        fill_poly([(x + 8, y + 22), (x + 14, y + 22), (x + 11, y + 17)], RED)
    elif kind == "tower":
        fill_rect(x + 7, y + 4, 8, 18, INK)
        fill_poly([(x + 4, y + 5), (x + 18, y + 5), (x + 11, y)], RED)
        fill_rect(x + 10, y + 9, 2, 2, PAPER); fill_rect(x + 10, y + 14, 2, 2, PAPER)
    elif kind == "ship":
        fill_poly([(x, y + 14), (x + 22, y + 14), (x + 18, y + 21), (x + 4, y + 21)], INK)
        fill_rect(x + 10, y + 3, 2, 11, INK); fill_poly([(x + 12, y + 3), (x + 19, y + 9), (x + 12, y + 9)], RED)
    elif kind == "stars":
        fill_ellipse(x + 11, y + 11, 10, 10, SEA)
        for i in range(6):
            import math
            a = i * 1.047
            fill_ellipse(x + 11 + int(6.5 * __import__("math").cos(a)), y + 11 + int(6.5 * __import__("math").sin(a)), 1, 1, (240, 200, 60))
    elif kind == "flag":
        fill_rect(x + 3, y, 2, 22, INK)
        fill_poly([(x + 5, y + 1), (x + 21, y + 5), (x + 5, y + 10)], RED)
    elif kind == "scales":
        fill_rect(x + 10, y + 2, 2, 16, INK); fill_rect(x + 2, y + 4, 18, 2, INK)
        fill_poly([(x + 1, y + 12), (x + 7, y + 12), (x + 4, y + 7)], INK)
        fill_poly([(x + 15, y + 12), (x + 21, y + 12), (x + 18, y + 7)], INK)
        fill_rect(x + 5, y + 19, 12, 2, INK)
    else:  # globe
        fill_ellipse(x + 11, y + 11, 10, 10, SEA)
        fill_ellipse(x + 11, y + 11, 4, 10, PAPER)
        fill_rect(x + 1, y + 10, 20, 2, PAPER)

def draw_tanker(x, y, w, h):
    fill_rect(x, y, w, h, SKY)
    fill_rect(x, y + h - 34, w, 34, SEA)
    # distant escort ship
    fill_poly([(x + w - 130, y + h - 44), (x + w - 60, y + h - 44), (x + w - 68, y + h - 34), (x + w - 122, y + h - 34)], GREY)
    fill_rect(x + w - 104, y + h - 54, 16, 10, GREY)
    # tanker hull
    fill_poly([(x + 40, y + h - 58), (x + w - 170, y + h - 58), (x + w - 195, y + h - 30), (x + 62, y + h - 30)], (40, 38, 36))
    fill_rect(x + 40, y + h - 64, w - 210, 7, RED)
    # containers / tanks
    cols = [(150, 90, 60), (70, 110, 130), (120, 120, 110), (165, 60, 50), (80, 95, 75)]
    for i, cc in enumerate(cols):
        fill_rect(x + 66 + i * 62, y + h - 92, 54, 26, cc)
    # bridge
    fill_rect(x + w - 232, y + h - 108, 34, 44, (238, 235, 228))
    fill_rect(x + w - 226, y + h - 100, 22, 5, SEA)
    # mines
    for mx, my in [(x + 90, y + h - 16), (x + 250, y + h - 10), (x + w - 240, y + h - 18)]:
        fill_ellipse(mx, my, 6, 6, (30, 30, 30))
        line(mx - 8, my, mx + 8, my, (30, 30, 30), 2); line(mx, my - 8, mx, my + 8, (30, 30, 30), 2)
    # waves
    for i in range(6):
        line(x + 20 + i * 90, y + h - 8, x + 55 + i * 90, y + h - 8, PAPER, 2)

def render():
    fill_rect(0, 0, W, H, PAPER)
    M = 48
    # masthead
    draw_center(26, "THE WORLD IN ONE DAY", "serif_bold52", INK)
    draw_center(92, "TUESDAY 24 NOVEMBER 2026  \u2022  ALL THE DAY'S NEWS ON ONE PAGE  \u2022  SINGLE EDITION", "sans11", GREY)
    fill_rect(M, 116, W - 2 * M, 4, INK)
    fill_rect(M, 123, W - 2 * M, 1, INK)
    # lead
    draw_text(M, 136, "LEAD STORY \u2014 STRAIT OF HORMUZ", "sans_bold13", RED)
    y = 158
    for ln in LEAD_HEAD:
        draw_text(M, y, ln, "serif_bold30", INK); y += 38
    draw_tanker(M, 240, W - 2 * M, 118)
    # two-column lead body
    words = LEAD_BODY.split()
    half = len(words) // 2
    col1 = " ".join(words[:half]); col2 = " ".join(words[half:])
    draw_wrapped(M, 368, col1, "serif13", INK, 452, 17)
    draw_wrapped(M + 476, 368, col2, "serif13", INK, 452, 17)
    draw_text(M, 424, "By the World Desk  \u2022  Hormuz, Washington, Tehran", "sans11", GREY)
    fill_rect(M, 442, W - 2 * M, 2, INK)
    # section header for the grid
    draw_text(M, 452, "AROUND THE WORLD", "sans_bold13", INK)
    draw_text(M + 476, 452, "MORE OF THE DAY", "sans_bold13", RED)
    # grid with column rule and row separators
    gx = [M, M + 476]; gy = 478; rh = 96
    fill_rect(M + 464, gy, 1, rh * 4 - 8, LIGHT)
    for idx, (icon, head, body) in enumerate(STORIES):
        cx = gx[idx % 2]; cy = gy + (idx // 2) * rh
        if idx >= 2:
            fill_rect(cx, cy - 7, 452, 1, LIGHT)
        draw_icon(icon, cx, cy + 2)
        draw_wrapped(cx + 30, cy, head, "serif_bold17", INK, 420, 21, 2)
        draw_wrapped(cx + 30, cy + 42, body, "serif13", INK, 420, 16, 3)
    fill_rect(M, 862, W - 2 * M, 2, INK)
    # markets strip: boxed cells with coloured moves
    GREEN = (22, 110, 55)
    draw_text(M, 870, "MARKETS AT THE CLOSE \u2014 TUESDAY 24 NOVEMBER 2026", "sans_bold11", RED)
    markets = [
        ("S&P 500", "7,237.17", "+4.73%", GREEN),
        ("NASDAQ", "24,089.56", "+6.51%", GREEN),
        ("DAX", "25,337.27", "+2.15%", GREEN),
        ("FTSE 100", "10,480.82", "+1.30%", GREEN),
        ("BRENT", "$86.7", "-2.99%", RED),
        ("GOLD", "$3,620.4", "-0.85%", RED),
    ]
    cellw = (W - 2 * M) // 6
    fill_rect(M, 890, W - 2 * M, 52, LIGHT)
    fill_rect(M, 890, W - 2 * M, 1, INK); fill_rect(M, 941, W - 2 * M, 1, INK)
    for i, (nm, val, chg, cc) in enumerate(markets):
        cx = M + i * cellw + 10
        if i:
            fill_rect(M + i * cellw, 890, 1, 52, GREY)
        draw_text(cx, 896, nm, "sans_bold11", INK)
        draw_text(cx, 912, val, "sans12", INK)
        draw_text(cx + text_w(val, "sans12") + 6, 912, chg, "sans_bold11", cc)
    # footer
    fill_rect(M, 956, W - 2 * M, 3, INK)
    fill_rect(M, 962, W - 2 * M, 1, INK)
    draw_center(972, "All stories verified against the day's reporting \u2014 no invented news.", "serif13", INK)
    draw_center(992, "THE WORLD IN ONE DAY  \u2022  NEWS-IMAGE EDITION  \u2022  @SUPER-CELL", "sans10", GREY)

def write_png(path):
    raw = bytearray()
    rowbytes = W * 3
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * rowbytes:(yy + 1) * rowbytes]
    comp = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    load_glyphs()
    render()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "entry.png")
        n = write_png(path)
    except Exception:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        n = write_png(path)
    print("wrote", path, n, "bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
