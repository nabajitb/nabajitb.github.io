---
layout: page
title: Photos
description: "Eighty photographs arranged by colour, from red through gold, green and blue to grey."
permalink: /photos/
show_title: false
background: none  # no protein animation behind the photographs
extra_css: /assets/css/photos.css
extra_js:
  - /assets/js/photos.js
---

## Photos

<p class="ph-note">{{ site.data.photos.size }} frames, arranged by colour. <a class="ph-random" href="#" hidden>random →</a></p>

<div class="ph-spectrum" role="navigation" aria-label="Jump to a photo by its colour">
{% for p in site.data.photos %}<a href="#f-{{ p.file }}" style="background:{{ p.color }}" aria-label="{{ p.alt | escape }}"></a>{% endfor %}
</div>

<div class="ph-wall">
{% for p in site.data.photos %}{% capture caption %}{{ p.place }}{% if p.place and p.date %} · {% endif %}{% if p.date %}{{ p.date | date: "%b %Y" }}{% endif %}{% endcapture %}{% assign c = caption | strip %}
  <a class="ph-photo" id="f-{{ p.file }}" href="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" data-caption="{{ c | escape }}" style="--c:{{ p.color }}">
    <img src="{{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }}" alt="{{ p.alt | escape }}" width="{{ p.w }}" height="{{ p.h }}"{% if forloop.index > 8 %} loading="lazy"{% endif %} decoding="async">
    {% if c != "" %}<span class="ph-cap">{{ c }}</span>{% endif %}
  </a>
{% endfor %}
</div>
