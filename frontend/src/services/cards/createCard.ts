import { apiRequest } from '../client';
import { Card, CardInput } from '../types';

export async function createCard(data: CardInput): Promise<Card> {
  return apiRequest<Card>('/cards/cards/', { method: 'POST', body: JSON.stringify(data) });
}
