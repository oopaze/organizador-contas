import { apiRequest } from '../client';
import { ProjectionResult } from '../types';

export async function getProjection(params: {
  start?: string;
  end?: string;
} = {}): Promise<ProjectionResult> {
  const query = new URLSearchParams();
  if (params.start) query.append('start', params.start);
  if (params.end) query.append('end', params.end);
  const suffix = query.toString();
  return apiRequest<ProjectionResult>(`/planning/projection/${suffix ? `?${suffix}` : ''}`);
}
