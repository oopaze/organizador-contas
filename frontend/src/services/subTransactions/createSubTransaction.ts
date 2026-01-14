import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, mockActors, incrementIds, delay } from '../mockData';

async function createSubTransactionMock(data: Omit<SubTransaction, 'id'>): Promise<SubTransaction> {
  await delay();
  const actor = data.actor_id ? mockActors.find(a => a.id === data.actor_id) : undefined;
  const newSubTransaction: SubTransaction = {
    ...data,
    id: incrementIds.nextSubTransactionId++,
    actor,
  };
  mockSubTransactions.push(newSubTransaction);
  return newSubTransaction;
}

async function createSubTransactionReal(data: Omit<SubTransaction, 'id'>): Promise<SubTransaction> {
  return apiRequest<SubTransaction>('/transactions/sub_transactions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createSubTransaction(data: Omit<SubTransaction, 'id'>): Promise<SubTransaction> {
  return USE_MOCK_API ? await createSubTransactionMock(data) : await createSubTransactionReal(data);
}