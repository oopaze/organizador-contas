import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, mockSubTransactions, delay } from '../mockData';

export interface ActorDetailFilters {
  due_date?: string; // Format: YYYY-MM-DD
}

async function getActorMock(id: number, filters?: ActorDetailFilters): Promise<Actor> {
  await delay();
  const actor = mockActors.find(a => a.id === id);
  if (!actor) throw new Error('Actor not found');

  // Include subtransactions linked to this actor
  let subTransactions = mockSubTransactions.filter(st => st.actor_id === id);

  // Filter by due_date if provided (match by month/year)
  if (filters?.due_date) {
    const [year, month] = filters.due_date.split('-');
    subTransactions = subTransactions.filter(st => {
      const stDate = st.date;
      return stDate.startsWith(`${year}-${month}`);
    });
  }

  const totalSpent = subTransactions.reduce((sum, st) => sum + parseFloat(st.amount), 0);

  return {
    ...actor,
    sub_transactions: subTransactions,
    total_spent: totalSpent,
  };
}

async function getActorReal(id: number, filters?: ActorDetailFilters): Promise<Actor> {
  const params = new URLSearchParams();
  if (filters?.due_date) {
    params.append('due_date', filters.due_date);
  }
  const queryString = params.toString();
  const url = queryString ? `/transactions/actors/${id}/?${queryString}` : `/transactions/actors/${id}/`;
  return apiRequest<Actor>(url);
}

export async function getActor(id: number, filters?: ActorDetailFilters): Promise<Actor> {
  return USE_MOCK_API ? await getActorMock(id, filters) : await getActorReal(id, filters);
}
