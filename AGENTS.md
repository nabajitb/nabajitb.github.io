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
- The local Gemfile runs Jekyll 4.3 but Pages runs Jekyll 3 / older Liquid, so a local build can pass while Pages
  fails. Trust the CI build. `Gemfile.lock` is gitignored.
- `_config.yml` defaults: global `permalink: /:title/` (set `permalink:` explicitly on new pages), every page gets
  `image: /assets/og.png`, the `blogs` collection gets `layout: blog_post` and lives at `/blogs/:name/`, and its feed
  is `/feed/blogs.xml`.

## Repository map

| Path | Purpose |
| --- | --- |
| `_config.yml` | Site settings, social handles, Bluesky config, nav order, collections, defaults |
| `_layouts/default.html` | Shell: head/SEO, fonts, theme script, header nav, footer, global JS (theme toggle, external links, copy-email, scroll reveals) |
| `_layouts/page.html` | Wraps content in `<article class="page">`; prints an `h1` unless `show_title: false` |
| `_layouts/blog_post.html` | Post page: meta line, auto table of contents (3+ headings), origin link, optional KaTeX (`math: true`) |
| `_includes/pub.html` | One publication entry |
| `index.md` | Home: profile, About, Currently, Bluesky Reading and Books lists |
| `work.md` | Projects and experience (from `_data`), plus hand-written HTML for education, skills, leadership, volunteering and "Beyond the lab" |
| `publications.md` | Book chapters (`_data/publications.yml`) and talks (`_data/talks.yml`) |
| `blogs.md` | Writing index ("Writing" in nav, URL `/blogs/`) |
| `photos.md` | Photo wall |
| `projects/pik3ca-benchmark.md` | Master's thesis page, with its own CSS/JS and data |
| `assets/thesis.pdf` | Full thesis, linked from the thesis page |
| `cv.md` | No layout, only `redirect_to` (jekyll-redirect-from): `/cv/` redirects to `assets/Nabajit-Borah-CV.pdf` (replace the PDF, keep the name) |
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
- `show_title: false`: the page writes its own heading (usually `## Section`). If the page has a `title` and its
  content has no `<h1`, a visually hidden `h1` is added for a11y.
- `protein: true` (home: full school), `protein: aggregate` (404: one clump); any other page gets a sparse school.
  Any `protein:` value also puts `class="home"` on `<body>` (so the 404 shares home styles).
- `background: none`: no protein canvas at all (photos, thesis page).
- `extra_css: /path.css` and `extra_js: [list]`: page-specific assets, cache-busted with `?v=<build time>`.
  (`protein.js` loads on every page without cache-busting and exits early when there is no canvas.)
- `description`, `image`: used by jekyll-seo-tag for link previews. Default card is `assets/og.png`. `image` can be a
  string or an object with `path` and `alt` (the thesis page uses the object form to give the card alt text).
- `sitemap: false`: keeps a page out of `sitemap.xml` (used on `404.html`, `cv.md`, `feed.xml`, Substack posts).
- `redirect_from`: old URLs (e.g. `work.md` keeps `/about/`, `/research/`, `/experience/`). `redirect_to` sends a
  page elsewhere (`cv.md`).

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
| `--surface` | `rgba(31,27,22,.04)` | `rgba(232,227,216,.05)` | Subtle fills |
| `--ss-helix / --ss-strand / --ss-loop / --ss-backbone` | red / teal / grey | red / cyan / slate | Protein colours, read by `protein.js` |
| `--code-*` | | | Syntax highlighting |

Rules:
- **Always use the variables**, never hardcode a hex in new global CSS. Every new token needs both a light and a dark
  value. Intended exceptions: the print stylesheet (`@media print`, plain `#fff`/`#000`), `photos.css` (captions and
  lightbox), and `pik3ca.css` (its own `--pk-*` palette with its own dark block).
- Theme is set on `<html data-theme="light|dark">` before first paint. It follows the system unless the user clicks
  the toggle (stored as `localStorage['theme-choice']`). A `themechange` event fires on switch; canvases/charts that
  read CSS variables in JS must listen for it and redraw.
- All themed properties transition together (0.45s, a universal `*` rule) so the flip feels like one piece. An element
  that sets its own `transition:` shorthand replaces that rule, so include `color 0.45s ease` (and background/border
  as needed) in it, or that element will snap instead of fading on theme change.
- The thesis page has its own validated chart palette (`--pk-*` in `pik3ca.css`, separate light/dark steps). Reuse
  those for any chart on that page.
- Photos page lightbox is always dark (`#08090b`-ish, bone text) regardless of theme, by design.

### Type

- `--font-display`: **Fraunces** (headings, names). CSS uses its `opsz` axis and `'WONK' 1`. The font URL pins `SOFT`
  at 0, so setting `SOFT` in CSS does nothing unless the URL changes.
- `--font-body`: **Newsreader** (body, optical size pinned at 18 to keep the font file small).
- `--font-mono`: **IBM Plex Mono** (labels, dates, data, nav, kickers, small caps-style uppercase notes).
- Loaded from Google Fonts in `default.html`. If you need a new weight/axis, extend that one URL; do not add fonts.

### Layout and motion

- Content column `--max-width: 880px`; `--radius: 6px`; easing `--ease-out: cubic-bezier(0.22,1,0.36,1)`.
- Breakpoints: 760px (phone layout), 560px, 350px. Nav stays visible in the header on phones (no hamburger).
- Tap targets at least 44px on phones (use a `::after` with negative inset to grow small links, as `.ph-random` does).
- Paper grain overlay (`.grain`) sits over everything at low opacity.
- Scroll reveals are added by JS (`.reveal` / `.visible`), so the page is fully visible without JS. Only elements
  matching the selector list in `default.html` animate: `.page > *` (not the profile), `.profile-info > *`,
  `.profile-photo`, `.section > *`, `.thesis`, `.project-row`.
- Cross-page fades use `@view-transition { navigation: auto }` (off under reduced motion). There is a print
  stylesheet that hides header, footer, canvas, grain and the table of contents.
- Respect `prefers-reduced-motion` in every animation you add.
- Section headings are `## Name` inside `.page`. CSS numbers direct-child `h2`s automatically (`01`, `02`, ... via a
  counter), so adding or removing a `##` renumbers the rest of the page. An `h2` inside a wrapper `div` is not
  numbered; hidden ones still count (the home page's Reading and Books headings). Post body headings are never
  numbered. Use `###` for sub-headings that should not be numbered.
- List rows (`.pub-item`) on publications and talks are numbered `[1]`, `[2]` in seal red by a CSS counter, like
  references. On `/publications/` the count runs on from chapters into talks (a `.section` wrapper would restart it).
  Writing rows use `.pub-item.post-item`, which drops the number ("posts are not citations"). Links in a row's
  `.pub-links` line get `[ ]` brackets in mono.
- Chips use `<ul class="tag-list"><li>..</li></ul>`; side-by-side groups use `.skill-grid`; dated rows use
  `.timeline-item` with `.timeline-header` / `.timeline-title` / `.timeline-date` / `.timeline-place`.

### Writing voice

Plain, precise, first person, lowercase in UI chrome (nav, footer, `cv` pill). Commit/PR titles follow
`Area: what changed` (e.g. `Reading: keep the Bluesky list in the browser for 2 minutes instead of 10`).

## Photos page (most common task)

How it works:
- `_data/photos.yml` is the single source. **List order is display order**, arranged around the colour wheel:
  reds → oranges/browns → yellows → greens → teals/blues → purples/pinks (hue rising from ~0° to ~350°), then a
  block of near-neutral shots (saturation under ~0.1) running from light grey to near black.
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
   ratio, RGB, quality around 80, strip EXIF/GPS. Existing files are 1080–1600px on the long side, mostly 100–600 KB (max ~780 KB).
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

   Then place it between the entries whose hue brackets its own. Low-saturation shots (sat below ~0.1: greys,
   blacks, overcast) go in the grey block at the end, placed by lightness (lighter first). The sort is by eye, not
   exact, so a few entries sit slightly out of strict hue order; leave existing entries where they are.
5. Write an honest `alt` for every photo. Ask the owner for `place`/`date` if not known; omit rather than guess.
6. Check locally or at least confirm the build passes. Do not touch `photos.js`/`photos.css` just to add photos.

Removing a photo: delete its entry, `NNN.webp`, `thumbs/NNN.webp` and `thumbs-400/NNN.webp`.

## Other content tasks

- **Project / experience / publication / talk**: edit the matching `_data/*.yml`. List order is display order (no
  sorting). Fields the pages actually render:
  - Thesis project (`thesis:` set; Theses block on `/work/`): `when`, `thesis`, `title`, `summary`, `cta`, `link`
    (through `relative_url`). Other projects (compact rows): `when`, `title`, `outcome`, `where`, `methods`, optional
    `link` (used as is). `problem` is never shown.
  - Experience: `title`, `place`, `dates`, newest first (`start` and `log` are unused).
  - Publications: `title`, `authors` (HTML, own name in `<strong>`), `venue`, `doi` (`year`, `selected` unused).
  - Talks: `title`, `authors`, `venue`, `award`, `link`. The link label is hard-coded "linkedin post" in
    `publications.md`; change it there if a link goes elsewhere (`short`, `date` unused).
- **Currently line / About / profile photo**: `index.md` (photo is `assets/images/profile.webp`, 640x640 square).
  A job change touches two places: the Currently div in `index.md` and the top entry of `_data/experience.yml`.
- **Education, skills, leadership, volunteering, languages, interests**: edit the HTML in `work.md` directly.
- **CV**: replace `assets/Nabajit-Borah-CV.pdf`, same name.
- **Writing**: posts are imported, not hand-written. `scripts/import_posts.py` pulls Medium (`@nabbo`) and Substack
  (`nabbo.substack.com`) RSS into `_blogs/<slug>.md` with images as WebP in `assets/images/blogs/<slug>/` plus
  `og.jpg`. Only PNG/JPEG become WebP (GIF/SVG are kept as they are), and images on hosts outside `IMAGE_HOSTS` stay
  remote. Existing posts are skipped so hand edits (e.g. alt text) survive; `--force` re-imports everything and
  overwrites them, so avoid it. Uncaptioned images import with `alt=""`: write real alt text by hand.
  The weekly workflow can also be run by hand (`workflow_dispatch`); it commits only `_blogs` and
  `assets/images/blogs`, and fails only if both feeds fail. Post bodies are wrapped in `{% raw %}` and hard-code
  `/assets/...` paths (fine because `baseurl` is empty). Substack posts
  carry `canonical_url` to Substack and `sitemap: false`. Front matter fields: `title`, `date`, `tags`, `excerpt`,
  `image` (the og.jpg), and `medium_url` or `substack_url` (drives the "read on ..." link). `date` and `excerpt` feed
  `feed.xml` (newest 20) and `/feed/blogs.xml`. Add `math: true` for KaTeX (cdnjs 0.16.9; delimiters `\( \)`,
  `\[ \]` and `$$`, not single `$`).
- **Reading / Books** (home): no repo change needed. They come live from Bluesky posts by `nabajitb.bsky.social`
  tagged `#reading` (book done: `#completed`), cached 2 minutes in the browser. Config in `_config.yml` `bluesky:`.
- **Link preview cards**: `scripts/make_og.py` (thesis), default `assets/og.png`. Favicon via
  `scripts/make_favicon.py` (needs `fonttools` + Pillow; favicon seal is `#c4412f`, a touch brighter so it holds up at
  16px). Both take `--fonts DIR` and open exact filenames: `Fraunces.ttf` (variable), plus `PlexMono-Regular.ttf` and
  `PlexMono-Medium.ttf` for the OG card. google/fonts ships them under other names, so rename them. Only the thesis
  card has a script; the default `assets/og.png` has none.
- **Protein background** (`protein.js`): ubiquitin (1UBQ) Cα traces drawn as tubes coloured by `--ss-*`, moving as
  boids. Clicking empty page space gathers the school there for 6s. It re-reads colours on `themechange`.
- **PIK3CA thesis page**: heavy custom page. `pik3ca.js` draws SVG charts and loads `pik3ca.json`,
  `poses/poses.json`, `mutation_map.json` and PDBs from `assets/data/pik3ca/` (don't rename them); 3D viewers use
  py2Dmol pinned to a commit from jsDelivr. `scripts/pik3ca_traj/build_site_assets.py` regenerates `pik3ca.json`,
  `traj/*.pdb`, the figure WebPs and `assets/thesis.pdf` (pages 13-76 of the source PDF, so hand edits to that PDF
  get overwritten). It needs the thesis folder outside the repo (`pose_eval.py` hard-codes a path on the owner's Mac)
  plus pandas/scipy/pypdf/sklearn, so it cannot be re-run here. Nothing in the repo makes `poses/*` or
  `mutation_map.*`. Don't restyle the page with global changes without checking it.

## Conventions and gotchas

- Use `relative_url` for every internal link/asset in Liquid you write (imported post bodies and non-thesis project
  `link`s are raw paths; that works only because `baseurl` is empty).
- External links and PDFs get `target="_blank"` automatically by `default.html`; don't add it by hand.
- Images: WebP with explicit `width`/`height` to avoid layout shift; `loading="lazy"` below the fold.
- JS is vanilla ES5-style IIFEs, no frameworks, no build. Pages must work (content visible) with JS off.
- Accessibility matters (nothing checks it automatically; CI only checks pages and thumbnails exist): alt text, `aria-label`s on icon links, focus-visible styles, skip link, keyboard support.
- Keep CSS for one page in that page's own file (`extra_css`), global things in `style.css`.
- The owner's email appears intentionally on the home page (copy button); don't add it elsewhere.
- Large binaries: keep photos under ~800 KB each; don't commit originals (JPG/HEIC/RAW) or `_site/`.
