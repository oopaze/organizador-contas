import { apiRequest } from '../client';
import { StartChatResponse } from '../types';

export interface StartChatRequest {
  content: string;
  model?: string;
}

export async function startChat(content: string, model?: string): Promise<StartChatResponse> {
  return apiRequest<StartChatResponse>('/ai/chat/start/', {
    method: 'POST',
    body: JSON.stringify({ content, model }),
  });
}

