#!/usr/bin/env python3
"""Build the 《第十個夏天》 IELTS-BL reader site (GitHub Pages static site).

Parses StoryNN-學習版.md files into data.js and emits index.html + manifest + icons.
Design/layout mirrors rcitest123.github.io/ielts-boss; palette reworked to BL pink/lavender.
"""
import json, os, re, sys

SRC = os.path.expanduser("~/workspace/your_files/ielts-bl-tenth-summer")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
os.makedirs(OUT, exist_ok=True)

WORD_RE = re.compile(r"([A-Za-z][A-Za-z\-']*)（([^）]*)）")

def parse_chapter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"# Story(\d+) 學習版 · (.+)", text)
    n, title = int(m.group(1)), m.group(2).strip()
    body, _, vocab_part = text.partition("## 本章詞彙表")
    lines = [ln.strip() for ln in body.splitlines()]
    # drop header + Step line
    lines = [ln for ln in lines if ln and not ln.startswith("#") and not ln.startswith("Step1")]
    paras, chars = [], 0
    for ln in lines:
        segs, pos = [], 0
        for wm in WORD_RE.finditer(ln):
            if wm.start() > pos:
                segs.append([0, ln[pos:wm.start()]])
            segs.append([1, wm.group(1), wm.group(2)])
            pos = wm.end()
        if pos < len(ln):
            segs.append([0, ln[pos:]])
        paras.append(segs)
        chars += len(ln)
    vocab = []
    for ln in vocab_part.splitlines():
        ln = ln.strip()
        if ln.startswith("|") and "---" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) == 3 and cells[0].isdigit():
                vocab.append([cells[1], cells[2]])
    return {"n": n, "t": title, "wc": len(vocab), "mins": max(1, round(chars / 450)),
            "paras": paras, "vocab": vocab}

chapters = []
for i in range(1, 101):
    p = os.path.join(SRC, f"Story{i:02d}-學習版.md")
    chapters.append(parse_chapter(p))
total = sum(c["wc"] for c in chapters)
print(f"chapters={len(chapters)} totalWords={total} "
      f"wc range={min(c['wc'] for c in chapters)}-{max(c['wc'] for c in chapters)}")

book = {"title": "第十個夏天", "totalWords": total, "chapters": chapters}
with open(os.path.join(OUT, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.BOOK=")
    json.dump(book, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

# ---------------- icons (PIL: pink->lavender gradient + 夏) ----------------
from PIL import Image, ImageDraw, ImageFont
def make_icon(size, path):
    img = Image.new("RGB", (size, size))
    px = img.load()
    c1, c2 = (240, 147, 184), (167, 139, 207)  # sakura pink -> lavender
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", int(size * 0.52))
    t = "夏"
    w = d.textlength(t, font=fnt)
    d.text(((size - w) / 2, size * 0.16), t, font=fnt, fill=(255, 255, 255))
    img.save(path)
make_icon(512, os.path.join(OUT, "icon-512.png"))
make_icon(192, os.path.join(OUT, "icon-192.png"))
make_icon(180, os.path.join(OUT, "apple-touch-icon.png"))
make_icon(64, os.path.join(OUT, "favicon.png"))

manifest = {
    "name": "第十個夏天・雅思單字 BL 小說",
    "short_name": "第十個夏天",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#FBF6F9",
    "theme_color": "#C2437B",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    ],
}
with open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("data.js + icons + manifest written to", OUT)
