import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, delay } from '../mockData';

async function getSubTransactionMock(id: number): Promise<SubTransaction> {
  await delay();
  const subTransaction = mockSubTransactions.find(st => st.id === id);
  if (!subTransaction) throw new Error('Sub-transaction not found');
  return subTransaction;
}

async function getSubTransactionReal(id: number): Promise<SubTransaction> {
  return apiRequest<SubTransaction>(`/transactions/sub_transactions/${id}/`);
}

export async function getSubTransaction(id: number): Promise<SubTransaction> {
  return USE_MOCK_API ? await getSubTransactionMock(id) : await getSubTransactionReal(id);
}
