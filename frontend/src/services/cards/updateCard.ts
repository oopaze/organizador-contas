import { apiRequest } from '../client';
import { Card, CardInput } from '../types';

export async function updateCard(id: number, data: Partial<CardInput>): Promise<Card> {
  return apiRequest<Card>(`/cards/cards/${id}/`, { method: 'PATCH', body: JSON.stringify(data) });
}
