(() => {
  "use strict";

  const slug = new URLSearchParams(window.location.search).get("island");
  const books = window.MitoMapaFormatData?.books ?? [];
  const route = books.some(book => book.slug === slug) ? `isla/${slug}/cuento` : "islas";
  window.location.replace(`index-en.html?lang=en#${route}`);
})();
