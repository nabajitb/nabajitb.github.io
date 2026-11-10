// Photos page: tiles start as noise and resolve into the photograph, the way a diffusion
// model denoises an image. Nothing is generated: each step blends noise with a small copy
// of the real photo, then the canvas fades out over the photo itself.
(function () {
  var grid = document.querySelector('.ph-grid');
  if (!grid) return;

  var tiles = Array.prototype.slice.call(grid.querySelectorAll('.ph-tile'));
  var items = tiles.map(function (a) {
    var img = a.querySelector('img');
    return { el: a, img: img, full: a.href, thumb: img.getAttribute('src'), alt: img.alt, caption: a.getAttribute('data-caption') || '' };
  });
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- Noise to photo -------------------------------------------------------------------

  function gauss() { return (Math.random() + Math.random() + Math.random() - 1.5) * 1.63; } // roughly N(0, 1)

  function makeNoise(n) {
    var e = new Float32Array(n * 3);
    for (var i = 0; i < e.length; i++) e[i] = gauss();
    return e;
  }

  function paint(ctx, w, h, x0, eps, a) {
    // a = 0 is pure noise, a = 1 is the photo. Some fresh noise each step makes it shimmer.
    var out = ctx.createImageData(w, h), d = out.data, n = w * h, sig = 1 - a;
    for (var i = 0; i < n; i++) {
      for (var c = 0; c < 3; c++) {
        var e = eps[i * 3 + c] * 0.82 + gauss() * 0.18;
        var v = (x0 ? a * x0[i * 4 + c] : 0) + sig * (128 + 74 * e);
        d[i * 4 + c] = v < 0 ? 0 : v > 255 ? 255 : v;
      }
      d[i * 4 + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
  }

  // Draw the image into a w x h box the way object-fit: cover would, and return its pixels.
  function sample(img, w, h) {
    var c = document.createElement('canvas');
    c.width = w; c.height = h;
    var iw = img.naturalWidth, ih = img.naturalHeight, s = Math.max(w / iw, h / ih);
    var ctx = c.getContext('2d');
    ctx.drawImage(img, (w - iw * s) / 2, (h - ih * s) / 2, iw * s, ih * s);
    return ctx.getImageData(0, 0, w, h).data;
  }

  function addNoise(host, w, h) {
    var c = document.createElement('canvas');
    c.className = 'ph-noise';
    c.width = w; c.height = h;
    c.setAttribute('aria-hidden', 'true');
    host.appendChild(c);
    var state = { canvas: c, ctx: c.getContext('2d'), w: w, h: h, eps: makeNoise(w * h), run: 0 };
    paint(state.ctx, w, h, null, state.eps, 0);
    return state;
  }

  function whenLoaded(img, cb) {
    if (img.complete && img.naturalWidth) cb();
    else img.addEventListener('load', cb, { once: true });
  }

  function denoise(state, img, steps, ms, onStep, onDone) {
    var run = ++state.run, x0;
    try { x0 = sample(img, state.w, state.h); } catch (e) { state.canvas.classList.add('done'); if (onDone) onDone(); return; }
    var start = null, last = -1;
    function frame(t) {
      if (run !== state.run) return; // a newer shuffle took over
      if (start === null) start = t;
      var s = Math.min(steps, Math.floor((t - start) / ms * steps));
      if (s !== last) {
        last = s;
        var a = s / steps;
        paint(state.ctx, state.w, state.h, x0, state.eps, a * a * (3 - 2 * a));
        if (onStep) onStep(s, steps);
      }
      if (s < steps) requestAnimationFrame(frame);
      else { state.canvas.classList.add('done'); if (onDone) onDone(); }
    }
    requestAnimationFrame(frame);
  }

  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var it = items[tiles.indexOf(e.target)];
        whenLoaded(it.img, function () { denoise(it.noise, it.img, 16, 1000 + Math.random() * 500); });
      });
    }, { threshold: 0.2 });
    items.forEach(function (it) {
      it.noise = addNoise(it.el, 40, 50);
      io.observe(it.el);
    });
  }

  // --- Featured photo and shuffle ---------------------------------------------------------

  var feature = document.querySelector('.ph-feature');
  var fImg = feature.querySelector('img');
  var meta = document.querySelector('.ph-meta');
  var current = -1;
  var fNoise = reduce ? null : addNoise(feature, 64, 80);

  function pick() {
    var i;
    do { i = Math.floor(Math.random() * items.length); } while (items.length > 1 && i === current);
    return i;
  }

  function showFeature(i) {
    current = i;
    var it = items[i];
    feature.href = it.full;
    fImg.alt = it.alt;
    if (!fNoise) { fImg.src = it.thumb; meta.textContent = it.caption; return; }
    fNoise.run++;
    fNoise.eps = makeNoise(fNoise.w * fNoise.h);
    paint(fNoise.ctx, fNoise.w, fNoise.h, null, fNoise.eps, 0);
    fNoise.canvas.classList.remove('done');
    meta.textContent = 'denoising';
    var probe = new Image();
    probe.onload = function () {
      if (current !== i) return;
      fImg.src = it.thumb;
      denoise(fNoise, probe, 28, 1700, function (s, n) {
        meta.textContent = 'denoising · step ' + (s < 10 ? '0' : '') + s + '/' + n;
      }, function () { if (current === i) meta.textContent = it.caption; });
    };
    probe.src = it.thumb;
  }

  document.querySelector('.ph-shuffle').addEventListener('click', function () { showFeature(pick()); });
  showFeature(pick());

  // --- Full-screen viewer -----------------------------------------------------------------

  var lb = document.createElement('div');
  lb.className = 'ph-lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photo viewer');
  lb.innerHTML =
    '<div class="ph-lb-stage">' +
      '<div class="ph-lb-top"><button type="button" class="ph-lb-rand">Shuffle ↻</button><button type="button" class="ph-lb-close" aria-label="Close">✕</button></div>' +
      '<button type="button" class="ph-lb-prev" aria-label="Previous photo">←</button>' +
      '<img alt="">' +
      '<button type="button" class="ph-lb-next" aria-label="Next photo">→</button>' +
    '</div>' +
    '<div class="ph-lb-bar"><span class="ph-lb-cap"></span><span class="ph-lb-count"></span></div>';
  document.body.appendChild(lb);

  var lbImg = lb.querySelector('img'), lbCap = lb.querySelector('.ph-lb-cap'), lbCount = lb.querySelector('.ph-lb-count');
  var at = 0, opener = null;

  function show(i) {
    at = (i + items.length) % items.length;
    var it = items[at], want = at;
    lbImg.src = it.thumb; // instant, already cached
    lbImg.alt = it.alt;
    var big = new Image();
    big.onload = function () { if (at === want && lb.classList.contains('open')) lbImg.src = it.full; };
    big.src = it.full;
    lbCap.textContent = it.caption;
    lbCount.textContent = (at + 1) + ' / ' + items.length;
  }

  function open(i, from) {
    opener = from || null;
    lb.classList.add('open');
    document.documentElement.style.overflow = 'hidden';
    show(i);
    lb.querySelector('.ph-lb-close').focus();
  }

  function close() {
    lb.classList.remove('open');
    document.documentElement.style.overflow = '';
    if (opener) opener.focus();
  }

  tiles.forEach(function (a, i) {
    a.addEventListener('click', function (e) { e.preventDefault(); open(i, a); });
  });
  feature.addEventListener('click', function (e) { e.preventDefault(); if (current >= 0) open(current, feature); });

  lb.querySelector('.ph-lb-close').addEventListener('click', close);
  lb.querySelector('.ph-lb-prev').addEventListener('click', function () { show(at - 1); });
  lb.querySelector('.ph-lb-next').addEventListener('click', function () { show(at + 1); });
  lb.querySelector('.ph-lb-rand').addEventListener('click', function () {
    var i;
    do { i = Math.floor(Math.random() * items.length); } while (i === at);
    show(i);
  });
  lb.querySelector('.ph-lb-stage').addEventListener('click', function (e) { if (e.target === e.currentTarget) close(); });

  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(at - 1);
    else if (e.key === 'ArrowRight') show(at + 1);
    else if (e.key === 'Tab') { // keep focus inside the viewer
      var b = lb.querySelectorAll('button'), first = b[0], lastB = b[b.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastB.focus(); }
      else if (!e.shiftKey && document.activeElement === lastB) { e.preventDefault(); first.focus(); }
    }
  });

  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    x0 = null;
    if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1));
  });
})();
