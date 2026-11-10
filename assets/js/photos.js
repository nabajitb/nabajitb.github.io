// Photos page: the "random" link scrolls to a photo picked at random.
(function () {
  var button = document.querySelector('.ph-random');
  var photos = document.querySelectorAll('.ph-photo');
  if (!button || !photos.length) return;
  var last = -1;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  button.hidden = false; // only shown when it can work
  button.addEventListener('click', function () {
    var i;
    do { i = Math.floor(Math.random() * photos.length); } while (photos.length > 1 && i === last);
    last = i;
    photos[i].scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
  });
})();
