import { Actor } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.poupix.connectakit.com.br';

export interface PublicActorResponse extends Actor {
  sub_transactions: Array<{
    id: number;
    description: string;
    amount: number;
    paid_at: string | null;
    category: string | null;
    transaction: {
      id: number;
      description: string;
      due_date: string;
    };
  }>;
}

export async function getPublicActor(token: string, dueDate?: string): Promise<PublicActorResponse> {
  const params = new URLSearchParams();
  if (dueDate) {
    params.append('due_date', dueDate);
  }
  
  const queryString = params.toString();
  const url = `${API_BASE_URL}/api/transactions/public/actors/${token}/${queryString ? `?${queryString}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Actor not found' }));
    throw new Error(error.error || 'Actor not found');
  }

  return response.json();
}

