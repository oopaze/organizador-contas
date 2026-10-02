import { apiRequest } from '../client';
import { Card } from '../types';

export async function setCardActive(id: number, isActive: boolean): Promise<Card> {
  return apiRequest<Card>(`/cards/cards/${id}/set_active/`, {
    method: 'POST',
    body: JSON.stringify({ is_active: isActive }),
  });
}
