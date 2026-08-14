"""Optimasi PNG murni stdlib (tanpa dependency) — tool dev one-off.

Cara pakai:
    python3 tools/optimize_png.py <file.png> [--no-downscale] [--out out.png]

Langkah:
1. Decode PNG (8-bit RGB/RGBA/gray) manual via zlib.
2. Opsional box-downscale 2x (rata-rata 2x2) — aman untuk tekstur
   background yang dipakai dengan opacity rendah.
3. Re-encode: filter terbaik per scanline (coba ke-5 filter, pilih yang
   zlib-nya terkecil per baris) + level 9.

Catatan: hanya mendukung bitdepth 8, colortype 0/2/6 (gray/RGB/RGBA).
"""

from __future__ import annotations

import struct
import sys
import zlib


def decode_png(path: str):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", "bukan PNG"
    pos, idat = 8, b""
    w = h = depth = ctype = None
    while pos < len(d):
        ln = struct.unpack(">I", d[pos : pos + 4])[0]
        typ = d[pos + 4 : pos + 8]
        data = d[pos + 8 : pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", data[:10])
        elif typ == b"IDAT":
            idat += data
        pos += 12 + ln
    assert depth == 8, f"bitdepth {depth} tidak didukung"
    assert ctype in (0, 2, 6), f"colortype {ctype} tidak didukung"
    raw = zlib.decompress(idat)
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    stride = w * bpp
    rows = []
    prev = bytearray(stride)
    p = 0
    for _y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p : p + stride])
        p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pv = a + b - c
                pa, pb, pc = abs(pv - a), abs(pv - b), abs(pv - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, ctype, rows


def box_downscale(w: int, h: int, bpp: int, rows: list[bytes]):
    """Rata-rata blok 2x2 (box filter) — ukuran jadi w//2 x h//2."""
    nw, nh = w // 2, h // 2
    out = []
    for y in range(nh):
        r1 = rows[2 * y]
        r2 = rows[2 * y + 1]
        line = bytearray(nw * bpp)
        for x in range(nw):
            for c in range(bpp):
                v = (
                    r1[(2 * x) * bpp + c]
                    + r1[(2 * x + 1) * bpp + c]
                    + r2[(2 * x) * bpp + c]
                    + r2[(2 * x + 1) * bpp + c]
                )
                line[x * bpp + c] = v >> 2
        out.append(bytes(line))
    return nw, nh, out


def _filter_row(f: int, line: bytes, prev: bytes, bpp: int) -> bytes:
    n = len(line)
    if f == 0:
        return b"\x00" + line
    out = bytearray(n + 1)
    out[0] = f
    if f == 1:  # Sub
        for i in range(n):
            a = line[i - bpp] if i >= bpp else 0
            out[i + 1] = (line[i] - a) & 255
    elif f == 2:  # Up
        for i in range(n):
            out[i + 1] = (line[i] - prev[i]) & 255
    elif f == 3:  # Average
        for i in range(n):
            a = line[i - bpp] if i >= bpp else 0
            out[i + 1] = (line[i] - ((a + prev[i]) >> 1)) & 255
    else:  # 4 Paeth
        for i in range(n):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            pv = a + b - c
            pa, pb, pc = abs(pv - a), abs(pv - b), abs(pv - c)
            pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            out[i + 1] = (line[i] - pr) & 255
    return bytes(out)


def encode_png(w: int, h: int, ctype: int, rows: list[bytes], level: int = 9) -> bytes:
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    chunks = [b"\x89PNG\r\n\x1a\n"]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0)
    chunks.append(struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr)))
    # pilih filter terbaik per baris (heuristik: ukuran terkompresi terkecil)
    prev = bytes(w * bpp)
    best_rows = []
    for line in rows:
        best = min(
            range(5),
            key=lambda f: len(zlib.compress(_filter_row(f, line, prev, bpp), level)),
        )
        best_rows.append(_filter_row(best, line, prev, bpp))
        prev = line
    idat = zlib.compress(b"".join(best_rows), level)
    chunks.append(struct.pack(">I", len(idat)) + b"IDAT" + idat + struct.pack(">I", zlib.crc32(b"IDAT" + idat)))
    iend = b""
    chunks.append(struct.pack(">I", 0) + b"IEND" + iend + struct.pack(">I", zlib.crc32(b"IEND")))
    return b"".join(chunks)


def main() -> None:
    argv = sys.argv[1:]
    downscale = "--no-downscale" not in argv
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
        argv = [a for a in argv if a not in ("--out", out)]
    argv = [a for a in argv if not a.startswith("--")]
    src = argv[0]
    w, h, ctype, rows = decode_png(src)
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    if downscale and w >= 4 and h >= 4:
        w, h, rows = box_downscale(w, h, bpp, rows)
    data = encode_png(w, h, ctype, rows)
    dst = out or (src[:-4] + ".opt.png" if src.endswith(".png") else src + ".opt")
    with open(dst, "wb") as f:
        f.write(data)
    import os

    print(f"{src}: {os.path.getsize(src) / 1024:.1f} KB -> {len(data) / 1024:.1f} KB "
          f"({w}x{h}, -{100 * (1 - len(data) / os.path.getsize(src)):.0f}%)")


if __name__ == "__main__":
    main()
