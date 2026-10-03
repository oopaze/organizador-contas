/**
 * Normaliza o valor digitado pelo usuário para a string decimal com ponto
 * enviada à API (`"54,90"` → `"54.90"`). Devolve `null` quando não é número.
 */
export function toDecimalString(value: string): string | null {
  const normalized = value.trim().replace(/\s+/g, '').replace(/,/g, '.');
  if (!/^-?\d+(\.\d+)?$/.test(normalized)) return null;
  return normalized;
}

/**
 * Texto para exibição/edição de um valor que a API devolve como number
 * (o DRF serializa Decimal como number no JSON, ex.: `89.9`) ou como string.
 */
export function amountToText(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return '';
  return String(value);
}

/** `true` quando o texto vira um decimal maior que zero. */
export function isPositiveAmount(value: string): boolean {
  const decimal = toDecimalString(value);
  return decimal !== null && Number(decimal) > 0;
}
