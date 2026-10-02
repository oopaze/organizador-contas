import { apiRequest } from '../client';
import { ApplyReconciliationInput } from '../types';

export interface ApplyReconciliationResult {
  merged: number;
  categorized: number;
  unmatched_remaining: number;
  closed_open_bills: number[];
  merged_into_bill_id: number | null;
}

export async function applyReconciliation(input: ApplyReconciliationInput): Promise<ApplyReconciliationResult> {
  return apiRequest<ApplyReconciliationResult>('/transactions/transactions/reconcile/apply/', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
