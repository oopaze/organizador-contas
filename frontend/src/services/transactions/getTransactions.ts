import { apiRequest, USE_MOCK_API } from '../client';
import { Transaction, TransactionFilters } from '../types';
import { mockTransactions, delay } from '../mockData';

async function getTransactionsMock(filters?: TransactionFilters): Promise<Transaction[]> {
  await delay();
  let result = [...mockTransactions];
  
  if (filters?.transaction_type) {
    result = result.filter(t => t.transaction_type === filters.transaction_type);
  }
  
  if (filters?.due_date) {
    // Filter by month/year (YYYY-MM format)
    result = result.filter(t => t.due_date.startsWith(filters.due_date!));
  }
  
  return result;
}

async function getTransactionsReal(filters?: TransactionFilters): Promise<Transaction[]> {
  const params = new URLSearchParams();
  if (filters?.transaction_type) params.append('transaction_type', filters.transaction_type);
  if (filters?.due_date) {
    const [year, month] = filters.due_date.split('-');
    params.append('due_date__month', `${month}`);
    params.append('due_date__year', `${year}`);
  }
  
  const query = params.toString();
  return apiRequest<Transaction[]>(`/transactions/transactions/?${query}`);
}

export async function getTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
  return USE_MOCK_API ? await getTransactionsMock(filters) : await getTransactionsReal(filters);
}