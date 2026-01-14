import { apiRequest, USE_MOCK_API } from '../client';
import { Transaction } from '../types';
import { mockTransactions, delay } from '../mockData';

async function getTransactionMock(id: number): Promise<Transaction> {
  await delay();
  const transaction = mockTransactions.find(t => t.id === id);
  if (!transaction) throw new Error('Transaction not found');
  return transaction;
}

async function getTransactionReal(id: number): Promise<Transaction> {
  return apiRequest<Transaction>(`/transactions/transactions/${id}/`);
}

export async function getTransaction(id: number): Promise<Transaction> {
  return USE_MOCK_API ? await getTransactionMock(id) : await getTransactionReal(id);
}
