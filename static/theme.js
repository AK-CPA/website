// Light/dark toggle. The initial theme is set inline in <head> to avoid a flash.
(function () {
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  function current() { return document.documentElement.getAttribute('data-theme') || 'light'; }
  function label() { btn.textContent = current() === 'dark' ? 'light mode' : 'dark mode'; }
  btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    label();
  });
  label();
})();
