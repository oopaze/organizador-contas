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
