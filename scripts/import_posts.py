#!/usr/bin/env python3
"""Import Medium posts and Substack articles (from their RSS feeds) into the Jekyll `_blogs` collection.

- Each post becomes _blogs/<slug>.md with front matter + the post HTML. Substack's feed lists articles only, not Notes.
- A Substack article names its Substack page as the original (canonical_url), since Substack has no setting to
  point at this site. Medium has one, so Medium posts are left to it (see the README).
- Images are downloaded to assets/images/blogs/<slug>/ as WebP (needs Pillow), with width/height set so the page
  does not jump as they load, and links rewritten. The first image is also saved as og.jpg for link previews,
  since not every preview fetcher reads WebP.
- An image with no alt text takes its caption as alt; write a real description by hand where it matters.
- Posts that already exist are skipped, so manual edits are kept. Medium is read first, so an article published on
  both under the same address is imported once, from Medium.
- A feed that cannot be read is reported and skipped; the run fails only if no feed could be read.

Usage: python3 scripts/import_posts.py [--force]
"""
import html
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

MEDIUM_FEED = "https://medium.com/feed/@nabbo"
SUBSTACK_FEED = "https://nabbo.substack.com/feed"
IMAGE_HOSTS = ("cdn-images", "miro.medium.com", "substackcdn.com", "substack-post-media")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "_blogs")
IMG_DIR = os.path.join(ROOT, "assets", "images", "blogs")
NS = {"content": "http://purl.org/rss/1.0/modules/content/"}
UA = {"User-Agent": "Mozilla/5.0 (post-import; +https://nabajitb.github.io)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


def slug_from_link(link):
    path = urllib.parse.urlparse(link).path.rstrip("/").split("/")[-1]
    return re.sub(r"-[0-9a-f]{8,}$", "", path)


def slugify(text):
    text = re.sub(r"<[^>]+>", "", html.unescape(text)).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60] or "section"


def ext_for(url, ctype):
    m = re.search(r"\.(png|jpe?g|gif|webp|svg)$", url, re.I)
    if m:
        return m.group(1).lower().replace("jpeg", "jpg")
    for k, v in (("png", "png"), ("jpeg", "jpg"), ("gif", "gif"), ("webp", "webp"), ("svg", "svg")):
        if k in ctype:
            return v
    return "jpg"


def to_webp(data):
    """PNG/JPEG bytes -> (WebP bytes, width, height). Raises if Pillow is missing or the data is not an image."""
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGBA" if "A" in im.getbands() or "transparency" in im.info else "RGB")
    im.thumbnail((1600, 1600))
    out = io.BytesIO()
    im.save(out, "WEBP", quality=82, method=6)
    return out.getvalue(), im.width, im.height


def to_og_jpeg(data):
    """Image bytes -> JPEG bytes for the link-preview card (transparency flattened onto white)."""
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    flat = Image.new("RGB", im.size, "white")
    flat.paste(im, mask=im.getchannel("A"))
    flat.thumbnail((1200, 1200))
    out = io.BytesIO()
    flat.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    return out.getvalue()


def caption_alts(body):
    """Give each <img alt=""> inside a <figure> its <figcaption> text as alt."""
    def fix(m):
        cap = re.search(r"<figcaption>(.*?)</figcaption>", m.group(0), flags=re.S)
        if not cap:
            return m.group(0)
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cap.group(1)))).strip()
        return m.group(0).replace('alt=""', 'alt="%s"' % html.escape(text, quote=True), 1) if text else m.group(0)
    return re.sub(r"<figure>.*?</figure>", fix, body, flags=re.S)


def medium_markup(body):
    # Drop Medium's tracking pixel.
    body = re.sub(r'<img[^>]+medium\.com/_/stat[^>]*>', "", body)

    # Medium uses h3/h4 for section headings; shift up so the site TOC sees h2/h3.
    body = re.sub(r"<(/?)h4>", r"<\1h3_>", body)
    body = re.sub(r"<(/?)h3>", r"<\1h2>", body)
    return body.replace("<h3_>", "<h3>").replace("</h3_>", "</h3>")


def drop_blocks(body, cls):
    """Remove every <div> or <p> carrying the class `cls`, with everything nested inside it."""
    start = 0
    while True:
        m = re.compile(r'<(div|p)\b[^>]*\bclass="([^"]*)"[^>]*>').search(body, start)
        if not m:
            return body
        if cls not in m.group(2).split():
            start = m.end()
            continue
        depth, end = 1, None
        for t in re.finditer(r"<(/?)%s\b[^>]*>" % m.group(1), body[m.end():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = m.end() + t.end()
                break
        if end is None:          # unbalanced markup: leave the rest alone
            return body
        body = body[:m.start()] + body[end:]
        start = m.start()


def substack_markup(body):
    # Subscribe forms and share buttons only work on Substack.
    for cls in ("subscription-widget-wrap-editor", "subscription-widget-wrap", "captioned-button-wrap", "button-wrapper"):
        body = drop_blocks(body, cls)

    # An image arrives wrapped in a link, a <picture> and two icon buttons; keep the image and its caption.
    def fix_figure(m):
        img = re.search(r"<img\b[^>]*>", m.group(0))
        if not img:
            return m.group(0)
        src = re.search(r'\bsrc="([^"]+)"', img.group(0)).group(1)
        alt = re.search(r'\balt="([^"]*)"', img.group(0))
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", m.group(0), flags=re.S)
        out = '<figure><img src="%s" alt="%s">' % (src, alt.group(1) if alt else "")
        if cap and cap.group(1).strip():
            out += "<figcaption>%s</figcaption>" % cap.group(1).strip()
        return out + "</figure>"
    body = re.sub(r'<div class="captioned-image-container">\s*<figure>.*?</figure>\s*</div>', fix_figure, body, flags=re.S)

    # Any other image: drop the attributes that point back at Substack's servers or fix its size.
    body = re.sub(r"</?picture[^>]*>|<source\b[^>]*>", "", body)
    body = re.sub(r"<img\b[^>]*>", lambda m: re.sub(
        r'\s(?:srcset|sizes|data-attrs|width|height|class|title|fetchpriority)="[^"]*"', "", m.group(0)), body)

    # A preformatted block keeps its line breaks but wraps, as it does on Substack.
    body = re.sub(r'<div class="preformatted-block"[^>]*>\s*(?:<label\b[^>]*>.*?</label>)?\s*<pre[^>]*>(.*?)</pre>\s*</div>',
                  r'<pre class="prose">\1</pre>', body, flags=re.S)
    body = re.sub(r'\sdata-color="[^"]*"', "", body)

    body = re.sub(r"<div>\s*(<hr\s*/?>)\s*</div>", r"\1", body)
    body = re.sub(r"<p>\s*</p>", "", body)

    # Whatever heading sizes the article uses, the largest becomes h2 and the next h3, for the site's contents list.
    levels = sorted(set(int(n) for n in re.findall(r"<h([1-6])\b", body)))
    rank = {n: "h%d" % min(i + 2, 6) for i, n in enumerate(levels)}
    return re.sub(r"<(/?)h([1-6])\b[^>]*>", lambda m: "<%s%s>" % (m.group(1), rank[int(m.group(2))]), body)


def clean_body(body, slug, cover=None):
    """Shared clean-up. `cover` is the address of a cover image to use for the link preview instead of the first image."""
    # Embedly iframes -> direct embed (e.g. YouTube).
    def fix_iframe(m):
        src = html.unescape(m.group(1))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
        real = q.get("src", [src])[0]
        return ('<div class="embed"><iframe src="%s" title="Embedded media" loading="lazy" allowfullscreen '
                'frameborder="0"></iframe></div>' % html.escape(real, quote=True))
    body = re.sub(r'<iframe[^>]*src="([^"]+)"[^>]*>.*?</iframe>', fix_iframe, body, flags=re.S)

    seen = {}

    def add_id(m):
        tag, inner = m.group(1), m.group(2)
        base = slugify(inner)
        seen[base] = seen.get(base, 0) + 1
        hid = base if seen[base] == 1 else "%s-%d" % (base, seen[base])
        return '<%s id="%s">%s</%s>' % (tag, hid, inner, tag)
    body = re.sub(r"<(h2|h3)>(.*?)</\1>", add_id, body, flags=re.S)

    # Download images.
    os.makedirs(os.path.join(IMG_DIR, slug), exist_ok=True)
    count = [0]
    images = []
    if cover:
        try:
            data, _ = fetch(cover)
            with open(os.path.join(IMG_DIR, slug, "og.jpg"), "wb") as f:
                f.write(to_og_jpeg(data))
            images.append("/assets/images/blogs/%s/og.jpg" % slug)
        except Exception as e:      # no cover is fine: the first image in the text is used instead
            print("  cover image skipped (%s)" % e)

    def fix_img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        if not any(h in src for h in IMAGE_HOSTS):
            return tag
        count[0] += 1
        data, ctype = fetch(html.unescape(src))
        ext, size = ext_for(src, ctype), ""
        if ext in ("png", "jpg"):
            if not images:
                with open(os.path.join(IMG_DIR, slug, "og.jpg"), "wb") as f:
                    f.write(to_og_jpeg(data))
                images.append("/assets/images/blogs/%s/og.jpg" % slug)
            data, w, h = to_webp(data)
            ext, size = "webp", 'width="%d" height="%d" ' % (w, h)
        name = "%d.%s" % (count[0], ext)
        with open(os.path.join(IMG_DIR, slug, name), "wb") as f:
            f.write(data)
        local = "/assets/images/blogs/%s/%s" % (slug, name)
        images.append(local)
        tag = tag.replace(src, local)
        return tag.replace("<img ", '<img loading="lazy" ' + size, 1)
    body = caption_alts(re.sub(r"<img[^>]*>", fix_img, body))

    return body.strip(), images


def first_paragraph(body):
    """Opening ~220 characters of body text, for the list-page excerpt."""
    paras = re.findall(r"<p>(.*?)</p>", body, flags=re.S)
    text = " ".join(html.unescape(re.sub(r"<br\s*/?>", " ", re.sub(r"</?(?!br)[a-z][^>]*>", "", p))) for p in paras)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= 220:
        return text
    return text[:220].rsplit(" ", 1)[0] + "…"


SOURCES = [
    # name, feed, front-matter key for the original's address, markup clean-up, whether the original is canonical
    ("Medium", MEDIUM_FEED, "medium_url", medium_markup, False),
    ("Substack", SUBSTACK_FEED, "substack_url", substack_markup, True),
]


def import_feed(name, feed, key, markup, canonical, force):
    xml, _ = fetch(feed)
    items = ET.fromstring(xml).findall("./channel/item")
    added = 0
    for it in items:
        link = it.findtext("link").split("?")[0]
        slug = slug_from_link(link)
        out = os.path.join(POSTS_DIR, slug + ".md")
        if os.path.exists(out) and not force:
            continue
        title = it.findtext("title").strip()
        date = parsedate_to_datetime(it.findtext("pubDate"))
        tags = [c.text for c in it.findall("category")]
        raw = it.findtext("content:encoded", namespaces=NS) or ""
        cover = it.find("enclosure")
        cover = cover.get("url") if cover is not None and (cover.get("type") or "").startswith("image/") else None
        body, images = clean_body(markup(raw), slug, cover)
        # Substack gives each article a subtitle; Medium has none, so its posts open with their first lines.
        subtitle = re.sub(r"\s+", " ", it.findtext("description") or "").strip() if canonical else ""

        fm = ["---",
              "title: %s" % json.dumps(title, ensure_ascii=False),
              "date: %s" % date.strftime("%Y-%m-%d %H:%M:%S %z"),
              "tags: %s" % json.dumps(tags, ensure_ascii=False),
              "%s: %s" % (key, json.dumps(link))]
        if canonical:
            fm.append("canonical_url: %s" % json.dumps(link))
            fm.append("sitemap: false")      # the sitemap lists originals only
        fm.append("excerpt: %s" % json.dumps(subtitle or first_paragraph(body), ensure_ascii=False))
        if images:
            fm.append("image: %s" % json.dumps(images[0]))
        fm.append("---")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + "\n\n{% raw %}\n" + body + "\n{% endraw %}\n")
        print("added", slug, "from", name, "(%d images)" % len(images))
        added += 1
    return added


def main():
    force = "--force" in sys.argv
    os.makedirs(POSTS_DIR, exist_ok=True)
    added, failed = 0, []
    for name, feed, key, markup, canonical in SOURCES:
        try:
            added += import_feed(name, feed, key, markup, canonical, force)
        except Exception as e:
            failed.append(name)
            # "::warning::" shows as a warning on the GitHub Actions run without stopping the other feed.
            print("::warning::Could not import from %s: %s" % (name, e))
    print("done: %d new post(s)" % added)
    if len(failed) == len(SOURCES):
        sys.exit(1)


if __name__ == "__main__":
    main()
