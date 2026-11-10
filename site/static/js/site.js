// Collection tabs. Without JavaScript, all three panels simply show one after another.
(function () {
  var list = document.querySelector('[role="tablist"]');
  if (!list) return;
  var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
  var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });

  function select(i, focus) {
    tabs.forEach(function (t, j) {
      var on = i === j;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      panels[j].hidden = !on;
    });
    if (focus) tabs[i].focus();
  }

  list.hidden = false;
  panels.forEach(function (p) { p.tabIndex = 0; });
  select(0, false);

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(i, false); });
    t.addEventListener('keydown', function (e) {
      var n = tabs.length, k = e.key;
      if (k === 'ArrowRight') { select((i + 1) % n, true); e.preventDefault(); }
      else if (k === 'ArrowLeft') { select((i - 1 + n) % n, true); e.preventDefault(); }
      else if (k === 'Home') { select(0, true); e.preventDefault(); }
      else if (k === 'End') { select(n - 1, true); e.preventDefault(); }
    });
  });
})();
