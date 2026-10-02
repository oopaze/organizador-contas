import { apiRequest, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

interface PayTransactionResponse {
  message: string;
}

interface PayTransactionOptions {
  updateSubTransactions?: boolean;
}

async function payTransactionMock(id: number, _options?: PayTransactionOptions): Promise<PayTransactionResponse> {
  await delay();
  // In mock mode, we just return success
  return { message: 'success' };
}

async function payTransactionReal(id: number, options?: PayTransactionOptions): Promise<PayTransactionResponse> {
  return apiRequest<PayTransactionResponse>(`/transactions/transactions/${id}/pay/`, {
    method: 'POST',
    body: JSON.stringify({
      update_sub_transactions: options?.updateSubTransactions ?? false,
    }),
  });
}

export async function payTransaction(id: number, options?: PayTransactionOptions): Promise<PayTransactionResponse> {
  return USE_MOCK_API ? await payTransactionMock(id, options) : await payTransactionReal(id, options);
}

