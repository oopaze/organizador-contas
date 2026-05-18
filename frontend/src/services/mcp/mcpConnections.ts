import { apiRequest } from '../client';

export interface MCPConnection {
  client_id: string;
  name: string;
}

export interface MCPConnectionsResponse {
  connections: MCPConnection[];
}

export async function listMCPConnections(): Promise<MCPConnection[]> {
  const data = await apiRequest<MCPConnectionsResponse>('/api/v1/mcp/connections/');
  return data.connections;
}

export async function revokeMCPConnection(clientId: string): Promise<void> {
  await apiRequest<void>(`/api/v1/mcp/connections/${clientId}/revoke/`, {
    method: 'POST',
  });
}
