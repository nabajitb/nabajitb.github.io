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

<div class="ph-head">
  <h1>Photos</h1>
  <button class="ph-random" type="button" hidden>random</button>
</div>

<div class="ph-roll">
{% for p in site.data.photos %}{% capture caption %}{{ p.place }}{% if p.place and p.date %} · {% endif %}{% if p.date %}{{ p.date | date: "%b %Y" }}{% endif %}{% endcapture %}{% assign c = caption | strip %}
  <figure class="ph-photo">
    <img src="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" srcset="{{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }} 640w, {{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }} {{ p.w }}w" sizes="(max-width: 760px) 100vw, 720px" alt="{{ p.alt | escape }}" width="{{ p.w }}" height="{{ p.h }}"{% if forloop.index > 2 %} loading="lazy"{% endif %} decoding="async">
    {% if c != "" %}<figcaption>{{ c }}</figcaption>{% endif %}
  </figure>
{% endfor %}
</div>
