import { apiRequest } from '../client';
import { AICallItem } from '../types';
import { AIDateFilters } from './getAICallsStats';

export async function getAICalls(filters?: AIDateFilters): Promise<AICallItem[]> {
  const params = new URLSearchParams();
  if (filters?.due_date_start) params.append('due_date_start', filters.due_date_start);
  if (filters?.due_date_end) params.append('due_date_end', filters.due_date_end);
  if (filters?.model) params.append('model', filters.model);

  const query = params.toString();
  return apiRequest<AICallItem[]>(`/ai/ai-calls/${query ? `?${query}` : ''}`);
}

