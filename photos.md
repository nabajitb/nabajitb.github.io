---
layout: page
title: Photos
description: "Trees, skies and old buildings, mostly from a phone."
permalink: /photos/
show_title: false
background: none  # no protein animation behind the photographs
extra_css: /assets/css/photos.css
extra_js:
  - /assets/js/photos.js
---

<div class="ph-hero">
  <a class="ph-feature" href="#" aria-label="Open the featured photo">
    <img alt="" width="4" height="5">
  </a>
  <div class="ph-hero-text">
    <h1>Photos</h1>
    <p class="ph-intro">Things I stopped to look at. Mostly trees, skies and old buildings, from a phone.</p>
    <p class="ph-meta" aria-live="polite"></p>
    <button class="ph-shuffle" type="button">Shuffle <span aria-hidden="true">↻</span></button>
  </div>
</div>

<div class="ph-grid">
{% for p in site.data.photos %}{% capture caption %}{{ p.place }}{% if p.place and p.date %} · {% endif %}{% if p.date %}{{ p.date | date: "%b %Y" }}{% endif %}{% endcapture %}
  <a class="ph-tile" href="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" data-w="{{ p.w }}" data-h="{{ p.h }}" data-caption="{{ caption | strip | escape }}">
    <img src="{{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }}" alt="{{ p.alt | escape }}" width="{{ p.w }}" height="{{ p.h }}" loading="lazy" decoding="async">
    {% assign c = caption | strip %}{% if c != "" %}<span class="ph-tile-cap">{{ c }}</span>{% endif %}
  </a>
{% endfor %}
</div>
