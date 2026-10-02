import { apiRequest } from '../client';
import { UploadPixReceiptResult } from '../types';

/** Recebe o multipart montado pelo diálogo (parte `file` no formato do RN). */
export async function uploadPixReceipt(formData: FormData): Promise<UploadPixReceiptResult> {
  return apiRequest<UploadPixReceiptResult>('/loans/loan_payments/upload_receipt/', {
    method: 'POST',
    body: formData,
    headers: {},
  });
}
