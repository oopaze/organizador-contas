import { apiRequest, USE_MOCK_API } from '../client';
import { Transaction } from '../types';
import { mockTransactions, incrementIds, delay } from '../mockData';

async function createTransactionMock(data: Omit<Transaction, 'id'>): Promise<Transaction> {
  await delay();
  const newTransaction: Transaction = {
    ...data,
    id: incrementIds.nextTransactionId++,
    created_at: new Date().toISOString(),
  };
  mockTransactions.push(newTransaction);
  return newTransaction;
}

async function createTransactionReal(data: Omit<Transaction, 'id'>): Promise<Transaction> {
  return apiRequest<Transaction>('/transactions/transactions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createTransaction(data: Omit<Transaction, 'id'>): Promise<Transaction> {
  return USE_MOCK_API ? await createTransactionMock(data) : await createTransactionReal(data);
}