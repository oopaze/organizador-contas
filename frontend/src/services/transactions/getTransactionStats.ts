import { apiRequest, USE_MOCK_API } from '../client';
import { TransactionStats } from '../types';
import { mockTransactions, mockSubTransactions, delay } from '../mockData';

export interface TransactionStatsFilters {
  due_date?: string; // Format: YYYY-MM-DD
}

async function getTransactionStatsMock(filters?: TransactionStatsFilters): Promise<TransactionStats> {
  await delay();
  
  let transactions = [...mockTransactions];
  let subTransactions = [...mockSubTransactions];
  
  // Filter by due_date if provided (match by month/year)
  if (filters?.due_date) {
    const [year, month] = filters.due_date.split('-');
    transactions = transactions.filter(t => t.due_date.startsWith(`${year}-${month}`));
    subTransactions = subTransactions.filter(st => st.date.startsWith(`${year}-${month}`));
  }
  
  const incoming_total = transactions
    .filter(t => t.transaction_type === 'incoming')
    .reduce((sum, t) => sum + parseFloat(t.total_amount || '0'), 0);
  
  const outgoing_total = transactions
    .filter(t => t.transaction_type === 'outgoing')
    .reduce((sum, t) => sum + parseFloat(t.total_amount || '0'), 0);
  
  const outgoing_from_actors = subTransactions
    .filter(st => st.actor_id !== undefined && st.actor_id !== null)
    .reduce((sum, st) => sum + parseFloat(st.amount || '0'), 0);
  
  return {
    incoming_total,
    outgoing_total,
    balance: incoming_total - outgoing_total,
    outgoing_from_actors,
  };
}

async function getTransactionStatsReal(filters?: TransactionStatsFilters): Promise<TransactionStats> {
  const params = new URLSearchParams();
  if (filters?.due_date) {
    params.append('due_date', filters.due_date);
  }
  const queryString = params.toString();
  const url = queryString ? `/transactions/transactions/stats/?${queryString}` : '/transactions/transactions/stats/';
  return apiRequest<TransactionStats>(url);
}

export async function getTransactionStats(filters?: TransactionStatsFilters): Promise<TransactionStats> {
  return USE_MOCK_API ? await getTransactionStatsMock(filters) : await getTransactionStatsReal(filters);
}

