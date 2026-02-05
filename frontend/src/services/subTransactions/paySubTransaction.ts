import { apiRequest, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

interface PaySubTransactionResponse {
  message: string;
}

async function paySubTransactionMock(_id: number): Promise<PaySubTransactionResponse> {
  await delay();
  // In mock mode, we just return success
  return { message: 'success' };
}

async function paySubTransactionReal(id: number): Promise<PaySubTransactionResponse> {
  return apiRequest<PaySubTransactionResponse>(`/transactions/sub_transactions/${id}/pay/`, {
    method: 'POST',
  });
}

export async function paySubTransaction(id: number): Promise<PaySubTransactionResponse> {
  return USE_MOCK_API ? await paySubTransactionMock(id) : await paySubTransactionReal(id);
}

