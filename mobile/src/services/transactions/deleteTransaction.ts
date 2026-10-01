import { apiRequest, USE_MOCK_API } from '../client';
import { mockTransactions, delay } from '../mockData';

async function deleteTransactionMock(id: number): Promise<void> {
  await delay();
  const index = mockTransactions.findIndex(t => t.id === id);
  if (index === -1) throw new Error('Transaction not found');
  mockTransactions.splice(index, 1);
}

async function deleteTransactionReal(id: number): Promise<void> {
  return apiRequest<void>(`/transactions/transactions/${id}/`, {
    method: 'DELETE',
  });
}

export async function deleteTransaction(id: number): Promise<void> {
  return USE_MOCK_API ? await deleteTransactionMock(id) : await deleteTransactionReal(id);
}
