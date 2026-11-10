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

<div class="ph-essay">
{% for p in site.data.photos %}
{% assign m = forloop.index0 | modulo: 10 %}
{% assign d = "" %}{% if p.date %}{% assign d = p.date | date: "%b %Y" %}{% endif %}
{% capture caption %}{{ p.place }}{% if p.place and p.date %} · {% endif %}{{ d }}{% endcapture %}
{% assign side = false %}{% if m == 3 or m == 7 %}{% assign side = true %}{% endif %}
{% case m %}
{% when 0 %}<div class="ph-row ph-solo">
{% when 1 %}<div class="ph-row ph-pair">
{% when 3 %}<div class="ph-row ph-side">
{% when 4 %}<div class="ph-row ph-trio">
{% when 7 %}<div class="ph-row ph-side ph-flip">
{% when 8 %}<div class="ph-row ph-pair ph-flip">
{% endcase %}
  <figure class="ph-photo" id="f-{{ p.file }}" style="--c:{{ p.color }}">
    <a href="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" data-caption="{{ caption | strip | escape }}">
      <img src="{{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }}" srcset="{{ '/assets/images/photos/thumbs/' | append: p.file | append: '.webp' | relative_url }} 640w, {{ '/assets/images/photos/' | append: p.file | append: '.webp' | relative_url }} {{ p.w }}w" sizes="(max-width: 760px) 92vw, 480px" alt="{{ p.alt | escape }}" width="{{ p.w }}" height="{{ p.h }}"{% if forloop.index > 1 %} loading="lazy"{% endif %} decoding="async">
    </a>
    <figcaption><i aria-hidden="true"></i><span>{{ p.color | remove: '#' }}</span>{% unless side %}{% assign c = caption | strip %}{% if c != "" %}<span>{{ c }}</span>{% endif %}{% endunless %}</figcaption>
  </figure>
  {% if side %}<div class="ph-aside">
    <span class="ph-no">{{ forloop.index | prepend: '00' | slice: -2, 2 }}</span>
    {% if p.place %}<span class="ph-place">{{ p.place }}</span>{% endif %}
    {% if d != "" %}<span class="ph-date">{{ d }}</span>{% endif %}
  </div>{% endif %}
{% case m %}{% when 0, 2, 3, 6, 7, 9 %}</div>{% endcase %}
{% endfor %}
</div>
