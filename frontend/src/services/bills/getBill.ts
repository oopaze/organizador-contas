import { apiRequest, USE_MOCK_API } from '../client';
import { Bill, SubTransaction } from '../types';
import { mockBills, mockSubTransactions, delay } from '../mockData';

async function getBillMock(id: number): Promise<Bill & { transactions: SubTransaction[] }> {
  await delay();
  const bill = mockBills.find(b => b.id === id);
  if (!bill) throw new Error('Bill not found');
  return {
    ...bill,
    transactions: mockSubTransactions.filter(st => st.transaction_id === 3),
  };
}

async function getBillReal(id: number): Promise<Bill & { transactions: SubTransaction[] }> {
  return apiRequest<Bill & { transactions: SubTransaction[] }>(`/pdf_reader/bills/${id}/`);
}

export async function getBill(id: number): Promise<Bill & { transactions: SubTransaction[] }> {
  return USE_MOCK_API ? await getBillMock(id) : await getBillReal(id);
}
