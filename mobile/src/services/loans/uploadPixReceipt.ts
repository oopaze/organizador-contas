import { apiRequest } from '../client';
import { UploadPixReceiptResult } from '../types';

export async function uploadPixReceipt(args: {
  file: File;
  loanId: number;
  model: string;
  password?: string;
}): Promise<UploadPixReceiptResult> {
  const formData = new FormData();
  formData.append('file', args.file);
  formData.append('loan_id', String(args.loanId));
  formData.append('model', args.model);
  if (args.password) formData.append('password', args.password);

  return apiRequest<UploadPixReceiptResult>('/loans/loan_payments/upload_receipt/', {
    method: 'POST',
    body: formData,
    headers: {},  // let the browser set Content-Type with boundary
  });
}
