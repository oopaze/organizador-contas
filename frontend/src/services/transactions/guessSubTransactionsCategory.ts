import { apiRequest, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

interface GuessSubTransactionsCategoryResponse {
  message: string;
}

async function guessSubTransactionsCategoryMock(_id: number): Promise<GuessSubTransactionsCategoryResponse> {
  await delay();
  // In mock mode, we just return success
  return { message: '2 sub transações atualizadas com sucesso' };
}

async function guessSubTransactionsCategoryReal(id: number): Promise<GuessSubTransactionsCategoryResponse> {
  return apiRequest<GuessSubTransactionsCategoryResponse>(`/transactions/transactions/${id}/guess_sub_transactions_category/`, {
    method: 'POST',
  });
}

export async function guessSubTransactionsCategory(id: number): Promise<GuessSubTransactionsCategoryResponse> {
  return USE_MOCK_API ? await guessSubTransactionsCategoryMock(id) : await guessSubTransactionsCategoryReal(id);
}

