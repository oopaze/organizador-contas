import { apiRequest, USE_MOCK_API } from '../client';
import { ActorStats } from '../types';

export interface ActorStatsFilters {
  due_date_start?: string;
  due_date_end?: string;
}

async function getActorStatsMock(filters?: ActorStatsFilters): Promise<ActorStats> {
  // Simple mock data
  await new Promise(resolve => setTimeout(resolve, 300));
  return {
    total_spent: 500.00,
    total_spent_paid: 300.00,
    biggest_spender: 'Mock User',
    biggest_spender_amount: 250.00,
    smallest_spender: 'Mock User 2',
    smallest_spender_amount: 50.00,
    average_spent: 125.00,
    active_actors: 4,
  };
}

async function getActorStatsReal(filters?: ActorStatsFilters): Promise<ActorStats> {
  const params = new URLSearchParams();
  if (filters?.due_date_start) {
    params.append('due_date_start', filters.due_date_start);
  }
  if (filters?.due_date_end) {
    params.append('due_date_end', filters.due_date_end);
  }
  const queryString = params.toString();
  const url = queryString ? `/transactions/actors/stats/?${queryString}` : '/transactions/actors/stats/';
  return apiRequest<ActorStats>(url);
}

export async function getActorStats(filters?: ActorStatsFilters): Promise<ActorStats> {
  return USE_MOCK_API ? await getActorStatsMock(filters) : await getActorStatsReal(filters);
}

