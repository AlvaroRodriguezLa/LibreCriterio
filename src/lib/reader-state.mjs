/** Small, pure contracts shared by the browser reader and its tests. */
export const READER_PREFERENCES_KEY = 'lc.reader.preferences.v1';
export const READER_PROGRESS_KEY = 'lc.reader.progress.v1';
export const DEFAULT_PREFERENCES = Object.freeze({ size: '20', font: 'serif', theme: 'paper', focus: false });
const sizes = new Set(['18', '20', '22', '24']);
const fonts = new Set(['serif', 'sans']);
const themes = new Set(['paper', 'light', 'dark']);
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function parsed(value) {
 if (typeof value !== 'string' || value.length > 65536) return null;
 try { return JSON.parse(value); } catch { return null; }
}
export function normalizePreferences(value) {
 const candidate = record(value) ? value : {};
 const size = typeof candidate.size === 'number' ? String(candidate.size) : candidate.size;
 return {
  size: sizes.has(size) ? size : DEFAULT_PREFERENCES.size,
  font: fonts.has(candidate.font) ? candidate.font : DEFAULT_PREFERENCES.font,
  theme: themes.has(candidate.theme) ? candidate.theme : DEFAULT_PREFERENCES.theme,
  focus: typeof candidate.focus === 'boolean' ? candidate.focus : DEFAULT_PREFERENCES.focus,
 };
}
export function parsePreferences(value) { return normalizePreferences(parsed(value)); }
export function sanitizeHeadingId(value) {
 if (typeof value !== 'string') return '';
 const id = value.normalize('NFC');
 return /^[\p{L}\p{N}][\p{L}\p{N}\p{M}_-]{0,179}$/u.test(id) ? id : '';
}
export function normalizeManifest(value) {
 if (!Array.isArray(value)) return [];
 const seen = new Set();
 return value.flatMap(item => {
  if (!record(item) || typeof item.slug !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(item.slug) || seen.has(item.slug)) return [];
  // The manifest uses site-relative URLs; persisted state is never allowed to supply a URL.
  if (typeof item.url !== 'string' || !/^\/(?!\/)/.test(item.url) || /[\u0000-\u0020\\]/.test(item.url)) return [];
  if (typeof item.title !== 'string' || !item.title.trim() || !Number.isInteger(item.number) || item.number < 1) return [];
  seen.add(item.slug);
  return [{ slug: item.slug, title: item.title.trim().slice(0, 300), number: item.number, url: item.url, partId: typeof item.partId === 'string' ? item.partId.slice(0, 80) : '' }];
 });
}
const knownSlugs = manifest => new Set(manifest.map(chapter => typeof chapter === 'string' ? chapter : chapter.slug));
export function mergeCompleted(manifest, ...lists) {
 const known = knownSlugs(manifest);
 const completed = new Set(lists.flatMap(list => Array.isArray(list) ? list : []).filter(slug => typeof slug === 'string' && known.has(slug)));
 return [...known].filter(slug => completed.has(slug));
}
export function normalizeProgress(value, manifest) {
 const candidate = record(value) ? value : {};
 const known = knownSlugs(manifest);
 let bookmark = null;
 if (record(candidate.bookmark) && known.has(candidate.bookmark.slug)) {
  const item = candidate.bookmark;
  const ratio = typeof item.ratio === 'number' && Number.isFinite(item.ratio) ? Math.min(1, Math.max(0, item.ratio)) : 0;
  const updatedAt = typeof item.updatedAt === 'number' && Number.isFinite(item.updatedAt) && item.updatedAt >= 0 ? Math.trunc(item.updatedAt) : 0;
  bookmark = { slug: item.slug, headingId: sanitizeHeadingId(item.headingId), ratio, updatedAt };
 }
 return { bookmark, completedSlugs: mergeCompleted(manifest, candidate.completedSlugs) };
}
export function parseProgress(value, manifest) { return normalizeProgress(parsed(value), manifest); }
export function hasExplicitHash(hash) { return typeof hash === 'string' && hash.startsWith('#') && hash.length > 1; }
export function shouldOfferResume(bookmark, currentSlug, hash = '') {
 return !hasExplicitHash(hash) && !!bookmark && bookmark.slug === currentSlug && bookmark.ratio > 0.02;
}
export function buildResumeHref(bookmark, manifest) {
 if (!bookmark) return null;
 const chapter = manifest.find(item => item.slug === bookmark.slug);
 if (!chapter) return null;
 const heading = sanitizeHeadingId(bookmark.headingId);
 return chapter.url.split('#')[0] + (heading ? '#' + encodeURIComponent(heading) : '');
}
/** Progress reports position, never whether somebody has understood/read a chapter. */
export function calculateChapterProgress(scrollY, viewportHeight, start, end) {
 if (![scrollY, viewportHeight, start, end].every(Number.isFinite) || viewportHeight <= 0 || end <= start) return 0;
 const height = end - start;
 if (height <= viewportHeight) return scrollY + viewportHeight >= end ? 1 : 0;
 return Math.min(1, Math.max(0, (scrollY - start) / (height - viewportHeight)));
}

/** Storage is injected so blocked browser storage and resets can be tested without a DOM. */
export function readStorageValue(getStorage, key) {
 try { const value = getStorage()?.getItem(key); return typeof value === 'string' ? value : null; } catch { return null; }
}
export function writeStorageValue(getStorage, key, value) {
 try { const storage = getStorage(); if (!storage) return false; storage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
}
export function removeStorageValue(getStorage, key) {
 try { const storage = getStorage(); if (!storage) return false; storage.removeItem(key); return true; } catch { return false; }
}
