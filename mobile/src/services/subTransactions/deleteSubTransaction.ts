import { apiRequest, USE_MOCK_API } from '../client';
import { mockSubTransactions, delay } from '../mockData';

async function deleteSubTransactionMock(id: number): Promise<void> {
  await delay();
  const index = mockSubTransactions.findIndex(st => st.id === id);
  if (index === -1) throw new Error('Sub-transaction not found');
  mockSubTransactions.splice(index, 1);
}

async function deleteSubTransactionReal(id: number): Promise<void> {
  return apiRequest<void>(`/transactions/sub_transactions/${id}/`, {
    method: 'DELETE',
  });
}

export async function deleteSubTransaction(id: number): Promise<void> {
  return USE_MOCK_API ? await deleteSubTransactionMock(id) : await deleteSubTransactionReal(id);
}
