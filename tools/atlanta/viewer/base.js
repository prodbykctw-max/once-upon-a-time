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

/**
 * Resolve a path relative to the REPO ROOT, not to this tool's folder.
 *
 * Jandé's sprite sheets are the shipped game's own, in `web/` at the top of the
 * repo — two levels up from the viewer, not one. Referencing them through
 * `asset()` would look in tools/atlanta/web/ and 404. Copying them into the
 * tool's own art folder would work and duplicate 471 KB of her art in the repo
 * for no reason; one more base is cheaper and keeps a single copy.
 */
// THREE levels, not two: the page sits at tools/atlanta/viewer/, so '../../'
// lands on tools/ and 404s. Counted off the 404 rather than off the comment.
export const ROOT = globalThis.__ROOT_BASE ?? (/\/viewer\/$/.test(dir) ? '../../../' : '');
export const rootAsset = (p) => ROOT + p;
