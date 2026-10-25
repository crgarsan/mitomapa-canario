/* Acceso legado a la valoración, compatible con la CSP de la web. */
(() => {
  "use strict";
  // In eXe's blob/data preview, keep its HTML link handler and the fallback.
  if (!["http:", "https:", "file:"].includes(window.location.protocol)) return;
  const destination = new URL("index.html", window.location.href);
  destination.hash = "studentFeedback";
  window.location.replace(destination.href);
})();
