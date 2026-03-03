import { apiRequest } from '../client';

interface ShareTokenResponse {
  token: string;
}

export async function getActorShareToken(actorId: number): Promise<string> {
  const response = await apiRequest<ShareTokenResponse>(
    `/transactions/actors/${actorId}/share_token/`,
    { method: 'GET' }
  );
  return response.token;
}

