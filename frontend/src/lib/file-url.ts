const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://api.poupix.connectakit.com.br';

/** Resolves a stored file URL to something the browser can open.
 *
 * Backend returns either an absolute URL (S3/Wasabi in prod) or a
 * relative MEDIA_URL path like /files/foo.pdf (local dev). Relative
 * paths need the API base prepended so the link doesn't resolve
 * against the frontend's origin.
 */
export function resolveFileUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${API_BASE_URL}${url}`;
  return `${API_BASE_URL}/${url}`;
}
