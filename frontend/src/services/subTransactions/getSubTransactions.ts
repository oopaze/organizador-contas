import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, delay } from '../mockData';

async function getSubTransactionsMock(): Promise<SubTransaction[]> {
  await delay();
  return [...mockSubTransactions];
}

async function getSubTransactionsReal(): Promise<SubTransaction[]> {
  return apiRequest<SubTransaction[]>('/transactions/sub_transactions/');
}

export async function getSubTransactions(): Promise<SubTransaction[]> {
  return USE_MOCK_API ? await getSubTransactionsMock() : await getSubTransactionsReal();
}
