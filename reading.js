(() => {
  const button = document.getElementById('theme-toggle');
  if (!button) return;
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  let saved = null;
  try { saved = localStorage.getItem('iczsc-reading-theme'); } catch (_) {}
  let dark = saved ? saved === 'dark' : media.matches;
  const apply = () => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    button.setAttribute('aria-pressed', String(dark));
    button.textContent = dark ? '纸色阅读' : '深夜阅读';
    button.setAttribute('aria-label', dark ? '切换至纸色阅读' : '切换至深夜阅读');
  };
  apply(); button.hidden = false;
  button.addEventListener('click', () => {
    dark = !dark; saved = dark ? 'dark' : 'light'; apply();
    try { localStorage.setItem('iczsc-reading-theme', saved); } catch (_) {}
  });
  media.addEventListener('change', event => { if (!saved) { dark = event.matches; apply(); } });
})();
