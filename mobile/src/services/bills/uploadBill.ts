import { apiUploadRequest, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

export interface UploadBillResult {
  message: string;
  transaction_ids?: number[];
}

async function uploadBillMock(): Promise<UploadBillResult> {
  await delay(1000);
  return { message: 'Fatura enviada com sucesso!', transaction_ids: [] };
}

/** Recebe o multipart montado pelo diálogo (parte `file` no formato do RN). */
export async function uploadBill(formData: FormData): Promise<UploadBillResult> {
  return USE_MOCK_API
    ? await uploadBillMock()
    : await apiUploadRequest<UploadBillResult>('/file_reader/upload/', formData);
}
