import { apiUploadRequest, USE_MOCK_API } from '../client';
import { Bill } from '../types';
import { delay, incrementIds, mockBills } from '../mockData';

async function uploadSheetMock(): Promise<Bill> {
  await delay(1000);
  const today = new Date().toISOString().split('T')[0];
  const newBill: Bill = {
    id: incrementIds.nextBillId++,
    file_name: 'planilha.xlsx',
    upload_date: today,
    total_amount: '0.00',
    due_date: today,
  };
  mockBills.push(newBill);
  return newBill;
}

/** Recebe o multipart montado pelo diálogo (parte `file` no formato do RN). */
export async function uploadSheet(formData: FormData): Promise<Bill> {
  return USE_MOCK_API
    ? await uploadSheetMock()
    : await apiUploadRequest<Bill>('/file_reader/upload-sheet/', formData);
}
