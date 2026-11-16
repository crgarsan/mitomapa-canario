(() => {
  const key = 'mitomapa-language';
  const page = document.documentElement.lang === 'en' ? 'en' : 'es';
  const locationURL = new URL(window.location.href);
  const explicit = locationURL.searchParams.get('lang');
  try {
    const preferred = localStorage.getItem(key);
    if (explicit === page) {
      localStorage.setItem(key, page);
    } else if (page === 'es' && preferred === 'en' && !explicit) {
      window.location.replace('index-en.html' + locationURL.search + locationURL.hash);
      return;
    } else if (page === 'en') {
      localStorage.setItem(key, page);
    }
  } catch (_) {
    // The explicit language links also work when browser storage is unavailable.
  }

  function linkToCurrentSection(event) {
    const link = event.target.closest?.('.language-switch a');
    if (link) link.hash = window.location.hash || '#inicio';
  }

  document.addEventListener('pointerdown', linkToCurrentSection);
  document.addEventListener('focusin', linkToCurrentSection);
  document.addEventListener('click', linkToCurrentSection);
})();
