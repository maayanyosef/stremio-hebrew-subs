#!/usr/bin/env python3
"""Build the static Stremio addon into ./site from the SRT files under ./subs.

Layout:
  subs/<imdb id>/<lang>[.<label>].srt                 -> movie   (id tt1234567)
  subs/<imdb id>/s<season>e<episode>/<lang>[.<label>].srt -> series episode (id tt1234567:S:E)
<lang> is an ISO 639-2 code such as heb, eng, ara, rus.
"""
import json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBS, SITE = ROOT / "subs", ROOT / "site"
BASE_URL = os.environ.get("BASE_URL", "https://maayanyosef.github.io/stremio-hebrew-subs").rstrip("/")

MANIFEST = {
    "id": "com.maayanyosef.hebrewsubs",
    "version": "1.0.0",
    "name": "Maayan Hebrew Subs",
    "description": "Private subtitles (Hebrew and more) for movies and series, served from github.com/maayanyosef/stremio-hebrew-subs",
    "resources": ["subtitles"],
    "types": ["movie", "series"],
    "idPrefixes": ["tt"],
    "catalogs": [],
    "behaviorHints": {"configurable": False, "configurationRequired": False},
}

EP_RE = re.compile(r"^s(\d+)e(\d+)$", re.I)
SRT_RE = re.compile(r"^([a-z]{2,3})(?:\.[^/]+)?\.srt$", re.I)

def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "files").mkdir(parents=True)
    index = {}  # stremio id -> {"type":..., "subtitles":[...]}
    for path in sorted(SUBS.rglob("*.srt")):
        rel = path.relative_to(SUBS)
        parts = rel.parts
        m = SRT_RE.match(parts[-1])
        if not m or not parts[0].startswith("tt"):
            sys.exit(f"Bad file name/location: subs/{rel} (see README)")
        lang = m.group(1).lower()
        if len(parts) == 2:
            sid, typ = parts[0], "movie"
        elif len(parts) == 3 and EP_RE.match(parts[1]):
            s, e = EP_RE.match(parts[1]).groups()
            sid, typ = f"{parts[0]}:{int(s)}:{int(e)}", "series"
        else:
            sys.exit(f"Bad file name/location: subs/{rel} (see README)")
        dest = SITE / "files" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        entry = index.setdefault(sid, {"type": typ, "subtitles": []})
        entry["subtitles"].append({
            "id": "maayan-" + "-".join(rel.with_suffix("").parts),
            "url": f"{BASE_URL}/files/{rel.as_posix()}",
            "lang": lang,
        })
    (SITE / "manifest.json").write_text(json.dumps(MANIFEST, indent=2))
    (SITE / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False))
    for sid, entry in index.items():
        d = SITE / "subtitles" / entry["type"]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}.json").write_text(json.dumps({"subtitles": entry["subtitles"]}))
    (SITE / ".nojekyll").write_text("")
    (SITE / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>{MANIFEST["name"]}</title>'
        f'<h1>{MANIFEST["name"]}</h1><p>Install: <a href="stremio://{BASE_URL.split("://",1)[1]}/manifest.json">stremio link</a> '
        f'or paste <code>{BASE_URL}/manifest.json</code> into Stremio’s addon search.</p>')
    print(f"Built {len(index)} ids, {sum(len(e['subtitles']) for e in index.values())} subtitle files")

if __name__ == "__main__":
    main()
