---
layout: page
title: Photos
description: "Photographs of trees, skies, streets and old buildings, arranged by colour, starting from a different one on every visit."
permalink: /photos/
show_title: false
background: none  # no protein animation behind the photographs
extra_css: /assets/css/photos.css
extra_js:
  - /assets/js/photos.js
---

## Photos

<p class="ph-note">{{ site.data.photos.size }} frames, arranged by colour. <a class="ph-random" href="#" hidden>random →</a></p>

{% comment %}Each tile lists two thumbnail widths (scripts/make_photo_thumbs.py makes both); a phone's three-column wall takes the 400px one.{% endcomment %}
{% comment %}The strip repeats the grid's links, so it is skipped by the Tab key and screen readers.{% endcomment %}
<div class="ph-spectrum" aria-hidden="true">
{% for p in site.data.photos %}<a href="#f-{{ p.file }}" style="background:{{ p.color }}" tabindex="-1"></a>{% endfor %}
</div>

<div class="ph-wall">
{% for p in site.data.photos %}{% capture caption %}{{ p.place }}{% if p.place and p.date %} · {% endif %}{% if p.date %}{{ p.date | date: "%b %Y" }}{% endif %}{% endcapture %}{% assign c = caption | strip %}
  <a class="ph-photo" id="f-{{ p.file }}" href="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" data-caption="{{ c | escape }}" style="--c:{{ p.color }}">
    <img src="{{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }}" srcset="{{ '/assets/images/photos/thumbs-400/' | append: p.file | append: '.webp' | relative_url }} 400w, {{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }} 640w" sizes="(max-width: 760px) 33vw, (max-width: 1128px) 25vw, 265px" alt="{{ p.alt | escape }}" width="{{ p.w }}" height="{{ p.h }}"{% if forloop.index > 8 %} loading="lazy"{% endif %} decoding="async">
    {% if c != "" %}<span class="ph-cap">{{ c }}</span>{% endif %}
  </a>
{% endfor %}
</div>
