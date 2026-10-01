import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, delay } from '../mockData';

async function updateSubTransactionMock(id: number, data: Partial<SubTransaction>): Promise<SubTransaction> {
  await delay();
  const index = mockSubTransactions.findIndex(st => st.id === id);
  if (index === -1) throw new Error('Sub-transaction not found');
  mockSubTransactions[index] = { ...mockSubTransactions[index], ...data };
  return mockSubTransactions[index];
}

async function updateSubTransactionReal(id: number, data: Partial<Omit<SubTransaction, 'id'>>): Promise<SubTransaction> {
  return apiRequest<SubTransaction>(`/transactions/sub_transactions/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function updateSubTransaction(id: number, data: Partial<Omit<SubTransaction, 'id'>> & { actor_amount?: number, should_divide_for_actor?: boolean }): Promise<SubTransaction> {
  return USE_MOCK_API ? await updateSubTransactionMock(id, data) : await updateSubTransactionReal(id, data);
}
