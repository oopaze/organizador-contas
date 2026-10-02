import { apiRequest, USE_MOCK_API } from '../client';
import { SubTransaction } from '../types';
import { mockSubTransactions, delay } from '../mockData';

export type UpdateSubTransactionData = Omit<Partial<SubTransaction>, 'actor'> & {
  /** `null` remove o ator da subtransação (como no PWA). */
  actor?: SubTransaction['actor'] | null;
  actor_amount?: number;
  should_divide_for_actor?: boolean;
};

async function updateSubTransactionMock(id: number, data: UpdateSubTransactionData): Promise<SubTransaction> {
  await delay();
  const index = mockSubTransactions.findIndex(st => st.id === id);
  if (index === -1) throw new Error('Sub-transaction not found');
  const { actor, ...rest } = data;
  mockSubTransactions[index] = {
    ...mockSubTransactions[index],
    ...rest,
    ...(actor === null ? { actor: undefined } : actor !== undefined ? { actor } : {}),
  };
  return mockSubTransactions[index];
}

async function updateSubTransactionReal(id: number, data: UpdateSubTransactionData): Promise<SubTransaction> {
  return apiRequest<SubTransaction>(`/transactions/sub_transactions/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function updateSubTransaction(id: number, data: UpdateSubTransactionData): Promise<SubTransaction> {
  return USE_MOCK_API ? await updateSubTransactionMock(id, data) : await updateSubTransactionReal(id, data);
}
