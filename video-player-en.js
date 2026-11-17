(() => {
  "use strict";

  const slug = new URLSearchParams(window.location.search).get("island");
  const books = window.MitoMapaFormatData?.books;
  const book = /^[a-z0-9-]+$/.test(slug ?? "") && Array.isArray(books)
    ? books.find(item => item.slug === slug)
    : null;
  const media = `en/media/${slug}/`;
  if (!book || book.video !== media + "story.mp4" ||
      typeof book.title !== "string" || typeof book.island !== "string") {
    document.getElementById("video-unavailable").hidden = false;
    return;
  }

  document.title = `${book.title} · MitoMapa Canario`;
  document.getElementById("video-title").textContent = book.title;
  const island = document.getElementById("video-island");
  island.textContent = book.island;
  island.hidden = false;

  const video = document.getElementById("story-video");
  if (book.poster === media + "poster.webp") video.poster = book.poster;
  const hls = document.createElement("source");
  hls.src = `en/video-hls/${slug}/story.m3u8`;
  hls.type = "application/vnd.apple.mpegurl";
  const mp4 = document.createElement("source");
  mp4.src = book.video;
  mp4.type = "video/mp4";
  video.append(hls, mp4);
  if (book.captions === media + "captions.vtt") {
    const captions = document.createElement("track");
    captions.src = book.captions;
    captions.kind = "captions";
    captions.srclang = "en";
    captions.label = "English";
    video.append(captions);
  }
  video.hidden = false;

  const back = document.getElementById("back-to-story");
  back.href = `index-en.html?lang=en#isla/${slug}/cuento`;
  back.textContent = "Back to the story";
  const download = document.getElementById("download-video");
  download.href = book.video;
  download.download = `MitoMapa_${slug}_EN.mp4`;
  download.hidden = false;
})();
