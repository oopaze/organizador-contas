import { apiRequest } from '../client';
import { EmbeddingsStats } from '../types';
import { AIDateFilters } from './getAICallsStats';

export async function getEmbeddingsStats(filters?: AIDateFilters): Promise<EmbeddingsStats> {
  const params = new URLSearchParams();
  if (filters?.due_date_start) params.append('due_date_start', filters.due_date_start);
  if (filters?.due_date_end) params.append('due_date_end', filters.due_date_end);

  const query = params.toString();
  return apiRequest<EmbeddingsStats>(`/ai/embeddings/stats/${query ? `?${query}` : ''}`);
}

