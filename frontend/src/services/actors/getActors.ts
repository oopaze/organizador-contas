import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, mockSubTransactions, delay } from '../mockData';

export interface ActorFilters {
  due_date?: string; // Format: YYYY-MM-DD
  without_sub_transactions?: boolean;
}

async function getActorsMock(filters?: ActorFilters): Promise<Actor[]> {
  await delay();

  // For mock, calculate total_spent for each actor based on their subtransactions
  return mockActors.map(actor => {
    let subTransactions = mockSubTransactions.filter(st => st.actor_id === actor.id);

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
      total_spent: totalSpent,
    };
  });
}

async function getActorsReal(filters?: ActorFilters): Promise<Actor[]> {
  const params = new URLSearchParams();
  if (filters?.due_date) {
    params.append('due_date', filters.due_date);
  }
  const queryString = params.toString();
  const url = queryString ? `/transactions/actors/?${queryString}` : '/transactions/actors/';
  return apiRequest<Actor[]>(url);
}

export async function getActors(filters?: ActorFilters): Promise<Actor[]> {
  return USE_MOCK_API ? await getActorsMock(filters) : await getActorsReal(filters);
}
