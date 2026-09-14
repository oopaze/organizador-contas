import { apiRequest } from '../client';
import { ReconcilePreview } from '../types';

export async function previewReconciliation(billTransactionId: number): Promise<ReconcilePreview> {
  return apiRequest<ReconcilePreview>('/transactions/transactions/reconcile/preview/', {
    method: 'POST',
    body: JSON.stringify({ bill_transaction_id: billTransactionId }),
  });
}
