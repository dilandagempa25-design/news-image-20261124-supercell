"""Build-time glyph generator (uses Pillow; NOT imported by main.py).

Produces glyphs.bin with format:
  magic: b'GLY1'
  u32: number of font entries
  per font entry:
    u8 name_len, name bytes (utf-8)
    u32 size (px)
    i32 ascent, i32 descent  (line height = ascent+descent)
    u32 glyph_count
    per glyph:
      u32 codepoint
      i32 advance
      u32 w, u32 h
      i32 xoff, i32 yoff  (offset from pen origin / baseline: bitmap top = baseline - ascent + yoff)
      w*h bytes alpha bitmap (row-major)
Fonts: serif_bold, serif, sans_bold, sans at several sizes.
Chars: ASCII 32-126 plus extra punctuation.
"""
from PIL import Image, ImageDraw, ImageFont
import struct, os

FONTS = [
    ("serif_bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    ("serif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ("sans_bold", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ("sans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
]
SIZES = {
    "serif_bold": [52, 30, 21, 17],
    "serif": [15, 13],
    "sans_bold": [13, 11],
    "sans": [12, 11, 10],
}
EXTRA = [0x2018, 0x2019, 0x201C, 0x201D, 0x2013, 0x2014, 0x2022, 0x2191, 0x2193, 0x00A3, 0x20AC]
CHARS = list(range(32, 127)) + EXTRA

def main():
    out = bytearray()
    out += b"GLY1"
    entries = []
    for name, path in FONTS:
        for size in SIZES[name]:
            entries.append((name, path, size))
    out += struct.pack("<I", len(entries))
    for name, path, size in entries:
        font = ImageFont.truetype(path, size)
        ascent, descent = font.getmetrics()
        glyphs = []
        for cp in CHARS:
            ch = chr(cp)
            adv = int(round(font.getlength(ch))) if cp != 32 else int(round(font.getlength(" ")))
            # render single glyph on padded canvas
            pad = size
            img = Image.new("L", (size * 3, size * 3), 0)
            d = ImageDraw.Draw(img)
            d.text((pad, pad), ch, font=font, fill=255)
            bbox = img.getbbox()
            if bbox is None or cp == 32:
                glyphs.append((cp, adv, 0, 0, 0, 0, b""))
            else:
                crop = img.crop(bbox)
                xoff = bbox[0] - pad
                yoff = bbox[1] - pad
                glyphs.append((cp, adv, crop.width, crop.height, xoff, yoff, crop.tobytes()))
        key = f"{name}{size}".encode()
        out += struct.pack("<B", len(key)) + key
        out += struct.pack("<IiiI", size, ascent, descent, len(glyphs))
        for cp, adv, w, h, xoff, yoff, data in glyphs:
            out += struct.pack("<I i I I i i", cp, adv, w, h, xoff, yoff)
            out += data
        print(f"{key.decode()} size={size} ascent={ascent} descent={descent} glyphs={len(glyphs)}")
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.bin")
    with open(dest, "wb") as f:
        f.write(out)
    print("wrote", dest, len(out), "bytes")

if __name__ == "__main__":
    main()
