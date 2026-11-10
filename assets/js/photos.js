// Photos page: rows rise in on scroll, "random" jumps to a photo, and a photo opens full screen.
(function () {
  var essay = document.querySelector('.ph-essay');
  if (!essay) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var figures = Array.prototype.slice.call(essay.querySelectorAll('.ph-photo'));
  var items = figures.map(function (f) {
    var a = f.querySelector('a'), img = f.querySelector('img');
    return { el: f, link: a, full: a.href, alt: img.alt, caption: a.getAttribute('data-caption') || '', img: img };
  });

  // Rows rise in as they are reached.
  if (!reduce && 'IntersectionObserver' in window) {
    essay.classList.add('ph-anim');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    essay.querySelectorAll('.ph-row').forEach(function (r) { io.observe(r); });
  }

  // Random: scroll to a photo picked at random.
  var random = document.querySelector('.ph-random'), last = -1;
  if (random) {
    random.hidden = false; // only shown when it can work
    random.addEventListener('click', function (e) {
      e.preventDefault();
      var i;
      do { i = Math.floor(Math.random() * items.length); } while (items.length > 1 && i === last);
      last = i;
      items[i].el.closest('.ph-row').classList.add('in');
      items[i].el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    });
  }

  // Full-screen viewer.
  var lb = document.createElement('div');
  lb.className = 'ph-lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photo viewer');
  lb.innerHTML =
    '<div class="ph-lb-stage">' +
      '<button type="button" class="ph-lb-close" aria-label="Close">✕</button>' +
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
    lbImg.src = it.img.currentSrc || it.full; // whatever the page already has, instantly
    lbImg.alt = it.alt;
    var big = new Image();
    big.onload = function () { if (at === want && lb.classList.contains('open')) lbImg.src = it.full; };
    big.src = it.full;
    lbCap.textContent = it.caption;
    lbCount.textContent = (at + 1) + ' / ' + items.length;
  }

  function open(i, from) {
    opener = from;
    lb.classList.add('open');
    document.documentElement.style.overflow = 'hidden';
    show(i);
    lb.querySelector('.ph-lb-close').focus();
  }

  function close() {
    lb.classList.remove('open');
    document.documentElement.style.overflow = '';
    if (opener) opener.focus({ preventScroll: true });
  }

  items.forEach(function (it, i) {
    it.link.addEventListener('click', function (e) { e.preventDefault(); open(i, it.link); });
  });
  lb.querySelector('.ph-lb-close').addEventListener('click', close);
  lb.querySelector('.ph-lb-prev').addEventListener('click', function () { show(at - 1); });
  lb.querySelector('.ph-lb-next').addEventListener('click', function () { show(at + 1); });
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

  var startX = null;
  lb.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1));
  });
})();
