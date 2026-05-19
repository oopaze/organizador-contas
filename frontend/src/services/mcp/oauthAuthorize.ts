import { apiRequest } from '../client';

export interface MCPClientInfo {
  client_id: string;
  name: string;
  redirect_uris: string[];
}

export interface AuthorizeParams {
  client_id: string;
  redirect_uri: string;
  code_challenge: string;
  code_challenge_method: string;
  scope: string;
  state: string;
}

export interface AuthorizeResponse {
  redirect_to: string;
}

export async function fetchMCPClient(clientId: string): Promise<MCPClientInfo> {
  return apiRequest<MCPClientInfo>(`/api/v1/mcp/oauth/client/${encodeURIComponent(clientId)}/`);
}

export async function approveMCPAuthorization(
  params: AuthorizeParams,
): Promise<AuthorizeResponse> {
  return apiRequest<AuthorizeResponse>('/api/v1/mcp/oauth/authorize/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}
