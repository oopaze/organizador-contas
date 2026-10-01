import { apiUploadRequest, USE_MOCK_API } from '../client';
import { Bill } from '../types';
import { mockBills, incrementIds, delay } from '../mockData';

export interface UploadBillResult {
  message: string;
  transaction_ids?: number[];
}

async function uploadBillMock(file: File): Promise<UploadBillResult> {
  await delay(1000);
  const newBill: Bill = {
    id: incrementIds.nextBillId++,
    file_name: file.name,
    upload_date: new Date().toISOString().split('T')[0],
    total_amount: '0.00',
    due_date: new Date().toISOString().split('T')[0],
  };
  mockBills.push(newBill);
  return { message: 'Fatura enviada com sucesso!', transaction_ids: [] };
}

async function uploadBillReal(file: File, password?: string, model?: string, createInFutureMonths?: boolean, cardId?: number): Promise<UploadBillResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (password) {
    formData.append('password', password);
  }
  if (model) {
    formData.append('model', model);
  }
  if (createInFutureMonths) {
    formData.append('create_in_future_months', 'true');
  }
  if (cardId) {
    formData.append('card_id', String(cardId));
  }
  return apiUploadRequest<UploadBillResult>('/file_reader/upload/', formData);
}

export async function uploadBill(file: File, password?: string, model?: string, createInFutureMonths?: boolean, cardId?: number): Promise<UploadBillResult> {
  return USE_MOCK_API ? await uploadBillMock(file) : await uploadBillReal(file, password, model, createInFutureMonths, cardId);
}
