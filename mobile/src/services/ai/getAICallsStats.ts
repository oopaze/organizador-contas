import { apiRequest } from '../client';
import { AICallsStats } from '../types';

export interface AIDateFilters {
  due_date_start?: string;
  due_date_end?: string;
  model?: string;
}

export async function getAICallsStats(filters?: AIDateFilters): Promise<AICallsStats> {
  const params = new URLSearchParams();
  if (filters?.due_date_start) params.append('due_date_start', filters.due_date_start);
  if (filters?.due_date_end) params.append('due_date_end', filters.due_date_end);
  if (filters?.model) params.append('model', filters.model);

  const query = params.toString();
  return apiRequest<AICallsStats>(`/ai/ai-calls/stats/${query ? `?${query}` : ''}`);
}

