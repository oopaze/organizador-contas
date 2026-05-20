import { apiRequest } from '../client';

export interface UploadLoanPaymentFileResult {
  id: number;
  url: string;
}

export async function uploadLoanPaymentFile(file: File): Promise<UploadLoanPaymentFileResult> {
  const formData = new FormData();
  formData.append('file', file);

  return apiRequest<UploadLoanPaymentFileResult>('/loans/loan_payments/upload_file/', {
    method: 'POST',
    body: formData,
    headers: {}, // let the browser set Content-Type with boundary
  });
}
