const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'https://api.poupix.connectakit.com.br';

/**
 * Resolve a URL de arquivo guardada no backend (absoluta em produção,
 * relativa no dev local) para algo que o app consiga abrir.
 */
export function resolveFileUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${API_BASE_URL}${url}`;
  return `${API_BASE_URL}/${url}`;
}
