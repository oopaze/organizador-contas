import { apiRequest } from '../client';

export interface UploadLoanFileResult {
  id: number;
  url: string;
}

/** Saves an arbitrary file (PDF/image) and returns its id, for linking
 * to a Loan (origin receipt) or a LoanPayment (manual entry receipt). */
export async function uploadLoanFile(file: File): Promise<UploadLoanFileResult> {
  const formData = new FormData();
  formData.append('file', file);

  return apiRequest<UploadLoanFileResult>('/loans/loan_payments/upload_file/', {
    method: 'POST',
    body: formData,
    headers: {}, // let the browser set Content-Type with boundary
  });
}
