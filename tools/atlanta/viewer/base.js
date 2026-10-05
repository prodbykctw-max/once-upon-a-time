// WHERE THE ASSETS ARE, as one knob instead of '../' in four files.
//
// Served from the repo the page sits at tools/atlanta/viewer/index.html, with
// `art/` and `world/` as its SIBLINGS one level up — so every asset path needs
// a '../'. A published bundle (the shareable preview link) is flat: the page is
// at the root and `art/`/`world/` sit beside it, so the same '../' would walk
// off the top of the site and 404 every texture.
//
// Detected from the document's own directory rather than passed in, because a
// build flag means two index.html files to keep in step and they would drift.
const dir = location.pathname.replace(/[^/]*$/, '');
export const AB = globalThis.__ASSET_BASE ?? (/\/viewer\/$/.test(dir) ? '../' : '');

/** Resolve a repo-relative asset path ('art/...', 'world/...') for this host. */
export const asset = (p) => AB + p;
