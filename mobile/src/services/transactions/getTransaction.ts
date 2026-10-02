import { apiRequest, USE_MOCK_API } from '../client';
import { TransactionDetail } from '../types';
import { mockTransactions, delay } from '../mockData';

async function getTransactionMock(id: number): Promise<TransactionDetail> {
  await delay();
  const transaction = mockTransactions.find(t => t.id === id);
  if (!transaction) throw new Error('Transaction not found');
  return { ...transaction, sub_transactions: [] };
}

async function getTransactionReal(id: number): Promise<TransactionDetail> {
  return apiRequest<TransactionDetail>(`/transactions/transactions/${id}/`);
}

export async function getTransaction(id: number): Promise<TransactionDetail> {
  return USE_MOCK_API ? await getTransactionMock(id) : await getTransactionReal(id);
}
