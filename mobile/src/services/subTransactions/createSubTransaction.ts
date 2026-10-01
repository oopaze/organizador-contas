import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, mockActors, incrementIds, delay } from '../mockData';

type CreateSubTransactionData = Omit<SubTransaction, 'id' | 'created_at' | 'updated_at' | 'date'>;

async function createSubTransactionMock(data: CreateSubTransactionData): Promise<SubTransaction> {
  await delay();
  const actor = data.actor_id ? mockActors.find(a => a.id === data.actor_id) : undefined;
  const newSubTransaction: SubTransaction = {
    ...data,
    id: incrementIds.nextSubTransactionId++,
    actor,
    date: "2026-01-01",
  };
  mockSubTransactions.push(newSubTransaction);
  return newSubTransaction;
}

async function createSubTransactionReal(data: CreateSubTransactionData): Promise<SubTransaction> {
  return apiRequest<SubTransaction>('/transactions/sub_transactions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createSubTransaction(data: CreateSubTransactionData): Promise<SubTransaction> {
  return USE_MOCK_API ? await createSubTransactionMock(data) : await createSubTransactionReal(data);
}