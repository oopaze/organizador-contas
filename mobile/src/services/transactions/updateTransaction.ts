import { apiRequest, USE_MOCK_API } from '../client';
import { Transaction } from '../types';
import { mockTransactions, delay } from '../mockData';

async function updateTransactionMock(id: number, data: Partial<Transaction>): Promise<Transaction> {
  await delay();
  const index = mockTransactions.findIndex(t => t.id === id);
  if (index === -1) throw new Error('Transaction not found');
  mockTransactions[index] = { ...mockTransactions[index], ...data };
  return mockTransactions[index];
}

async function updateTransactionReal(id: number, data: Partial<Transaction>): Promise<Transaction> {
  return apiRequest<Transaction>(`/transactions/transactions/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function updateTransaction(id: number, data: Partial<Transaction>): Promise<Transaction> {
  return USE_MOCK_API ? await updateTransactionMock(id, data) : await updateTransactionReal(id, data);
}
