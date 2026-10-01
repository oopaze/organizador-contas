import type { QueryClient } from '@tanstack/react-query';

/**
 * Invalida tudo que depende de uma escrita em transação/subtransação
 * (pagar, despagar, excluir). A tela escuta essas chaves e refaz a leitura.
 */
export async function invalidateFinancialData(queryClient: QueryClient): Promise<void> {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['transactions'] }),
    queryClient.invalidateQueries({ queryKey: ['stats'] }),
    queryClient.invalidateQueries({ queryKey: ['ledger'] }),
    queryClient.invalidateQueries({ queryKey: ['subTransactions'] }),
  ]);
}
