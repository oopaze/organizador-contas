import { apiRequest } from '../client';
import { Card } from '../types';

export async function getCards(): Promise<Card[]> {
  return apiRequest<Card[]>('/cards/cards/');
}
