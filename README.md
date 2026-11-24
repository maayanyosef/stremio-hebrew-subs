# Maayan Hebrew Subs — private Stremio subtitle addon

Serves my own subtitle files (Hebrew, or any language) to Stremio for any movie or series episode,
keyed by IMDb id. Static files are built by a GitHub Action and hosted on GitHub Pages.

## Add a subtitle

1. Drop the `.srt` (UTF-8) into `subs/` using this layout:

   | What | Path | Stremio id |
   |---|---|---|
   | Series episode | `subs/<imdb id>/s<season>e<episode>/<lang>.srt` | `tt23112594:1:6` |
   | Movie | `subs/<imdb id>/<lang>.srt` | `tt0111161` |

   - `<imdb id>` is the `tt…` id from the IMDb URL of the **show/movie** (not the episode).
   - `<season>`/`<episode>` are plain numbers, e.g. `s1e6` (leading zeros are fine: `s01e06`).
   - `<lang>` is a 3-letter ISO 639-2 code: `heb`, `eng`, `ara`, `rus`, `spa`…
   - Several files for the same language? Add a label: `heb.srt`, `heb.sylix.srt`, `heb.web-dl.srt`.

   Example: `subs/tt23112594/s1e9/heb.srt` → VisionQuest S01E09 Hebrew.

2. Commit and push to `main` (or upload through the GitHub web UI: *Add file → Upload files*).
   The **Build and deploy addon** Action runs `scripts/build.py` and publishes in ~1 minute.
   Stremio caches subtitle lists for a few minutes.

Test locally with `python3 scripts/build.py` (output in `site/`).

## Install in Stremio

Paste the manifest URL into Stremio → Add-ons → search box, or open the `stremio://` link
(see the addon's home page).

## How it's served

- `scripts/build.py` writes `site/manifest.json`, `site/subtitles/<type>/<id>.json`, `site/index.json`
  and copies the SRTs to `site/files/…`.
- Stremio normally requests `/subtitles/<type>/<id>/videoHash=…&videoSize=…&filename=….json`.
  A static host can't answer those, so `edge/worker.js` (Cloudflare Workers / Deno Deploy, free)
  strips the extra args and answers from `index.json`. Use the worker's URL + `/manifest.json`
  as the install URL. The SRT links themselves point at GitHub Pages.
