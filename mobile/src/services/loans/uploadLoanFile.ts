import { apiRequest } from '../client';

export interface UploadLoanFileResult {
  id: number;
  url: string;
}

/** Recebe o multipart montado pelo diálogo (parte `file` no formato do RN). */
export async function uploadLoanFile(formData: FormData): Promise<UploadLoanFileResult> {
  return apiRequest<UploadLoanFileResult>('/loans/loan_payments/upload_file/', {
    method: 'POST',
    body: formData,
    headers: {},
  });
}
