import { apiRequest, USE_MOCK_API } from '../client';
import { Bill } from '../types';
import { mockBills, delay } from '../mockData';

async function getBillsMock(): Promise<Bill[]> {
  await delay();
  return [...mockBills];
}

async function getBillsReal(): Promise<Bill[]> {
  return apiRequest<Bill[]>('/file_reader/bills/');
}

export async function getBills(): Promise<Bill[]> {
  return USE_MOCK_API ? await getBillsMock() : await getBillsReal();
}
