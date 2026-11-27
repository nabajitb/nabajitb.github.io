# AGENTS.md

Guide for coding agents working on **https://nabajitb.github.io**, the personal site of Nabajit Borah
(computational biologist, "nabbo"). Read this before changing anything. `README.md` has the human-facing notes;
this file is the fuller map.

## Stack and build

- Jekyll site, served by **GitHub Pages from `master`** using the `github-pages` gem (Jekyll 3.x). The `Gemfile`
  (Jekyll 4) is only for local runs and Pages ignores it, so do not rely on Jekyll 4-only features or extra plugins.
- Allowed plugins (whitelisted by Pages): `jekyll-feed`, `jekyll-seo-tag`, `jekyll-sitemap`, `jekyll-redirect-from`.
- No bundler, no npm, no build step for CSS/JS. CSS and JS are plain files under `assets/`, loaded directly.
- Local run: `bundle install && bundle exec jekyll serve`.
- CI: `.github/workflows/build.yml` runs the real Pages build on every PR and push to `master`. It fails if a key page
  is missing (`index`, `work`, `publications`, `blogs`, `photos`, `projects/pik3ca-benchmark`, `feed/blogs.xml`,
  `sitemap.xml`) or if any photo lacks either thumbnail size.
- `.github/workflows/posts-sync.yml` runs `scripts/import_posts.py` every Monday 03:17 UTC and commits new posts.
- `scripts/` is excluded from the site build (see `exclude` in `_config.yml`).

## Repository map

| Path | Purpose |
| --- | --- |
| `_config.yml` | Site settings, social handles, Bluesky config, nav order, collections, defaults |
| `_layouts/default.html` | Shell: head/SEO, fonts, theme script, header nav, footer, global JS (theme toggle, external links, copy-email, scroll reveals) |
| `_layouts/page.html` | Wraps content in `<article class="page">`; prints an `h1` unless `show_title: false` |
| `_layouts/blog_post.html` | Post page: meta line, auto table of contents (3+ headings), origin link, optional KaTeX (`math: true`) |
| `_includes/pub.html` | One publication entry |
| `index.md` | Home: profile, About, Currently, Bluesky Reading and Books lists |
| `work.md` | Projects (thesis block + other projects), experience, education, skills |
| `publications.md` | Book chapters (`_data/publications.yml`) and talks (`_data/talks.yml`) |
| `blogs.md` | Writing index ("Writing" in nav, URL `/blogs/`) |
| `photos.md` | Photo wall |
| `projects/pik3ca-benchmark.md` | Master's thesis page, with its own CSS/JS and data |
| `cv.md` | `/cv/` redirects to `assets/Nabajit-Borah-CV.pdf` (replace the PDF, keep the name) |
| `404.html` | "This page misfolded" page, protein animation in aggregate mode |
| `feed.xml` | Replaces jekyll-feed's empty `/feed.xml` with the blogs feed |
| `_data/*.yml` | Content: `projects`, `experience`, `publications`, `talks`, `photos` |
| `_blogs/` | Posts collection (imported, see Writing below) |
| `assets/css/style.css` | All global styles and the design tokens |
| `assets/css/photos.css`, `assets/js/photos.js` | Photos page only |
| `assets/css/pik3ca.css`, `assets/js/pik3ca.js`, `assets/data/pik3ca/` | Thesis page only |
| `assets/js/protein.js` | Animated background: a "school" of ubiquitin Cα traces moving as boids |
| `assets/js/reading.js` | Home Reading/Books lists from Bluesky's public API |
| `assets/images/` | `profile.webp`, `icons/*.svg`, `photos/`, `blogs/<slug>/`, `projects/pik3ca/` |
| `scripts/` | Python helpers (thumbnails, post import, OG card, favicon, PIK3CA trajectory pipeline) |

## Page front matter switches

Read by `_layouts/default.html` / `page.html`:

- `layout: page` for normal pages.
- `show_title: false`: the page writes its own heading (usually `## Section`); a hidden `h1` is added for a11y.
- `protein: true` (home: full school, `body.home`), `protein: aggregate` (404), otherwise subpages get a sparse school.
- `background: none`: no protein canvas at all (photos, thesis page).
- `extra_css: /path.css` and `extra_js: [list]`: page-specific assets, cache-busted with `?v=<build time>`.
- `description`, `image`: used by jekyll-seo-tag for link previews. Default card is `assets/og.png`.
- `redirect_from`: old URLs (e.g. `work.md` keeps `/about/`, `/research/`, `/experience/`).

Nav comes from `navigation` in `_config.yml`. Nav labels are rendered lowercase. "Writing" hides itself when there
are no posts.

## Design system

The look is "field notes": warm paper and ink in light mode, a deep-sea abyss with bioluminescent cyan in dark mode.
Keep it quiet, typographic and editorial. No emojis, no gradients-for-decoration, no new colour families.

### Colour tokens (`assets/css/style.css`, `:root` and `:root[data-theme="dark"]`)

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--paper` | `#f7f3ec` | `#0a0f16` | Page background |
| `--paper-header` | `rgba(247,243,236,.82)` | `rgba(10,15,22,.8)` | Translucent sticky header |
| `--ink` | `#15120e` | `#e8e3d8` | Body text |
| `--ink-soft` | `#575145` | `#8b94a3` | Secondary text, dates, labels |
| `--line` | `#c4bba9` | `#232c38` | Rules, borders, bracket marks |
| `--accent` | `#0f5868` (deep-water teal) | `#5fd4e0` (cyan) | Links, selection, highlights |
| `--accent-ink` | `#0a4552` | `#8ce4ed` | Hover/strong accent |
| `--seal` | `#9a2f22` (vermilion) | `#e05a48` | Kickers, small red marks |
| `--surface` | ink at 4% | bone at 5% | Subtle fills |
| `--ss-helix / --ss-strand / --ss-loop / --ss-backbone` | red / teal / grey | red / cyan / slate | Protein colours, read by `protein.js` |
| `--code-*` | | | Syntax highlighting |

Rules:
- **Always use the variables**, never hardcode a hex in new CSS. Every new token needs both a light and a dark value.
- Theme is set on `<html data-theme="light|dark">` before first paint. It follows the system unless the user clicks
  the toggle (stored as `localStorage['theme-choice']`). A `themechange` event fires on switch; canvases/charts that
  read CSS variables in JS must listen for it and redraw.
- All themed properties transition together (0.45s) so the flip feels like one piece.
- The thesis page has its own validated chart palette (`--pk-*` in `pik3ca.css`, separate light/dark steps). Reuse
  those for any chart on that page.
- Photos page lightbox is always dark (`#08090b`-ish, bone text) regardless of theme, by design.

### Type

- `--font-display`: **Fraunces** (headings, names; uses `opsz`, `SOFT`, `WONK` axes).
- `--font-body`: **Newsreader** (body, optical size pinned at 18 to keep the font file small).
- `--font-mono`: **IBM Plex Mono** (labels, dates, data, nav, kickers, small caps-style uppercase notes).
- Loaded from Google Fonts in `default.html`. If you need a new weight/axis, extend that one URL; do not add fonts.

### Layout and motion

- Content column `--max-width: 880px`; `--radius: 6px`; easing `--ease-out: cubic-bezier(0.22,1,0.36,1)`.
- Breakpoints: 760px (phone layout), 560px, 350px. Nav stays visible in the header on phones (no hamburger).
- Tap targets at least 44px on phones (use a `::after` with negative inset to grow small links, as `.ph-random` does).
- Paper grain overlay (`.grain`) sits over everything at low opacity.
- Scroll reveals are added by JS (`.reveal` / `.visible`), so the page is fully visible without JS.
- Respect `prefers-reduced-motion` in every animation you add.
- Section headings are `## Name` inside `.page`; CSS draws their rule/marker. Lists of items use `.pub-item`
  (titles, `[link]` brackets in mono).

### Writing voice

Plain, precise, first person, lowercase in UI chrome (nav, footer, `cv` pill). Commit/PR titles follow
`Area: what changed` (e.g. `Reading: keep the Bluesky list in the browser for 2 minutes instead of 10`).

## Photos page (most common task)

How it works:
- `_data/photos.yml` is the single source. **List order is display order**, arranged around the colour wheel:
  reds → oranges/browns → yellows → greens → teals/blues → purples/pinks, then near-greys/blacks at the end.
- `photos.js` rotates that list to a random start point and random direction on each visit, so order still matters:
  neighbours must be close in colour.
- Each entry renders a tile in `.ph-wall` (4 columns desktop, 3 on phones, 4:5 crop) and a sliver in the
  `.ph-spectrum` strip. Clicking opens a full-screen viewer (arrows, swipe, Esc). Caption = `place · Mon YYYY`.
- The intro line shows `{{ site.data.photos.size }} frames` automatically.

Entry format:

```yaml
- file: "157"            # string, zero-padded 3 digits; matches assets/images/photos/157.webp
  alt: "Short literal description of the photo"   # required, plain, no "photo of"
  place: "Hauz Khas, New Delhi"                   # optional
  date: 2026-11-20                                # optional, YYYY-MM-DD
  color: "#5d4d37"       # dominant colour, lowercase hex; tile background while loading + spectrum sliver
  w: 1280                # pixel width of the full .webp
  h: 1600                # pixel height of the full .webp
```

Steps to add photos:
1. Pick the next unused numbers. Files currently run `001`–`156` with gaps (`090`, `100`, `122`, `124` were
   removed). Never reuse or rename an existing number; ids are used as `#f-NNN` anchors.
2. Convert each original to WebP at `assets/images/photos/NNN.webp`: long side at most **1600px**, keep the aspect
   ratio, RGB, quality around 80, strip EXIF/GPS. Existing files are 1080–1600px on the long side, ~100–600 KB.
   Portrait 4:5 suits the wall best; other ratios get center-cropped in the grid but show whole in the viewer.
3. Run `python3 scripts/make_photo_thumbs.py` from the repo root (needs Pillow). It writes the missing
   `thumbs/NNN.webp` (640px wide) and `thumbs-400/NNN.webp` (400px wide). CI fails without both.
4. Compute `color`, `w`, `h` and insert each entry into `_data/photos.yml` **at the position matching its hue**, not
   at the end. There is no script for this in the repo; use something like:

   ```python
   from PIL import Image
   import colorsys
   im = Image.open("assets/images/photos/157.webp").convert("RGB")
   w, h = im.size
   small = im.resize((64, 64)).quantize(colors=5)
   pal = small.getpalette(); count, idx = max(small.getcolors())
   r, g, b = pal[idx*3:idx*3+3]
   hue, light, sat = colorsys.rgb_to_hls(r/255, g/255, b/255)
   print(f'color: "#{r:02x}{g:02x}{b:02x}"  w: {w}  h: {h}  hue: {hue*360:.0f}  sat: {sat:.2f}')
   ```

   Then place it next to entries with similar hue (and similar lightness within that run). Low-saturation shots
   (sat below ~0.1, i.e. greys, blacks, overcast) go in the grey block at the end.
5. Write an honest `alt` for every photo. Ask the owner for `place`/`date` if not known; omit rather than guess.
6. Check locally or at least confirm the build passes. Do not touch `photos.js`/`photos.css` just to add photos.

Removing a photo: delete its entry, `NNN.webp`, `thumbs/NNN.webp` and `thumbs-400/NNN.webp`.

## Other content tasks

- **Project / experience / publication / talk**: edit the matching `_data/*.yml` (field comments at the top of each
  file). A project with `thesis:` set appears in the Theses block on `/work/`; others are compact rows.
- **Currently line / About**: `index.md`.
- **CV**: replace `assets/Nabajit-Borah-CV.pdf`, same name.
- **Writing**: posts are imported, not hand-written. `scripts/import_posts.py` pulls Medium (`@nabbo`) and Substack
  (`nabbo.substack.com`) RSS into `_blogs/<slug>.md` with images as WebP in `assets/images/blogs/<slug>/` plus
  `og.jpg`. Existing posts are skipped so hand edits survive. Post bodies are wrapped in `{% raw %}`. Substack posts
  carry `canonical_url` to Substack and `sitemap: false`.
- **Reading / Books** (home): no repo change needed. They come live from Bluesky posts by `nabajitb.bsky.social`
  tagged `#reading` (book done: `#completed`), cached 2 minutes in the browser. Config in `_config.yml` `bluesky:`.
- **Link preview cards**: `scripts/make_og.py` (thesis), default `assets/og.png`. Favicon via
  `scripts/make_favicon.py`. Both need Fraunces + IBM Plex Mono TTFs passed with `--fonts DIR`.
- **PIK3CA thesis page**: heavy custom page. Charts are hand-built SVG from `assets/data/pik3ca/*.json`; 3D viewers
  use py2Dmol pinned to a commit from jsDelivr. Trajectory data is produced by `scripts/pik3ca_traj/` (see README).
  Don't restyle it with global changes without checking it.

## Conventions and gotchas

- Use `relative_url` for every internal link/asset in Liquid.
- External links and PDFs get `target="_blank"` automatically by `default.html`; don't add it by hand.
- Images: WebP with explicit `width`/`height` to avoid layout shift; `loading="lazy"` below the fold.
- JS is vanilla ES5-style IIFEs, no frameworks, no build. Pages must work (content visible) with JS off.
- Accessibility is checked: alt text, `aria-label`s on icon links, focus-visible styles, skip link, keyboard support.
- Keep CSS for one page in that page's own file (`extra_css`), global things in `style.css`.
- The owner's email appears intentionally on the home page (copy button); don't add it elsewhere.
- Large binaries: keep photos under ~600 KB each; don't commit originals (JPG/HEIC/RAW) or `_site/`.
