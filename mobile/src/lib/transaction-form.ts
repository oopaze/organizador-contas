import type { TransactionType } from '../services';
import { TRANSACTION_CATEGORIES } from './category-colors';

export const CATEGORY_OPTIONS = [
  { value: 'none', label: 'Nenhuma' },
  ...TRANSACTION_CATEGORIES.map((category) => ({ value: category.key, label: category.value })),
];

export const TYPE_OPTIONS = [
  { value: 'incoming', label: 'Receita' },
  { value: 'outgoing', label: 'Despesa' },
] satisfies { value: TransactionType; label: string }[];

export const ISO_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

/** Mensagem do backend quando disponível; caso contrário, o texto padrão do diálogo. */
export function formatSubmitError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

/**
 * Erro de upload: mantém a mensagem real do backend (senha incorreta, arquivo
 * inválido) e traduz falha de rede para o aviso honesto do app.
 */
export function formatUploadError(error: unknown, fallback: string): string {
  const message = error instanceof Error ? error.message : '';
  if (/network request failed|failed to fetch|upload failed/i.test(message)) {
    return 'Sem conexão — tente de novo quando voltar.';
  }
  return message || fallback;
}
