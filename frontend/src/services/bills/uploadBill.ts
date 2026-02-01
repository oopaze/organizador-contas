import { apiUploadRequest, USE_MOCK_API } from '../client';
import { Bill } from '../types';
import { mockBills, incrementIds, delay } from '../mockData';

async function uploadBillMock(file: File): Promise<Bill> {
  await delay(1000);
  const newBill: Bill = {
    id: incrementIds.nextBillId++,
    file_name: file.name,
    upload_date: new Date().toISOString().split('T')[0],
    total_amount: '0.00',
    due_date: new Date().toISOString().split('T')[0],
  };
  mockBills.push(newBill);
  return newBill;
}

async function uploadBillReal(file: File, password?: string, model?: string): Promise<Bill> {
  const formData = new FormData();
  formData.append('file', file);
  if (password) {
    formData.append('password', password);
  }
  if (model) {
    formData.append('model', model);
  }
  return apiUploadRequest<Bill>('/file_reader/upload/', formData);
}

export async function uploadBill(file: File, password?: string, model?: string): Promise<Bill> {
  return USE_MOCK_API ? await uploadBillMock(file) : await uploadBillReal(file, password, model);
}