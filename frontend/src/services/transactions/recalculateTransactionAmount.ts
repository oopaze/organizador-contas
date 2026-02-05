import { apiRequest, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

interface RecalculateAmountResponse {
  message: string;
}

async function recalculateTransactionAmountMock(_id: number): Promise<RecalculateAmountResponse> {
  await delay();
  // In mock mode, we just return success
  return { message: 'success' };
}

async function recalculateTransactionAmountReal(id: number): Promise<RecalculateAmountResponse> {
  return apiRequest<RecalculateAmountResponse>(`/transactions/transactions/${id}/recalculate_amount/`, {
    method: 'POST',
  });
}

export async function recalculateTransactionAmount(id: number): Promise<RecalculateAmountResponse> {
  return USE_MOCK_API ? await recalculateTransactionAmountMock(id) : await recalculateTransactionAmountReal(id);
}

