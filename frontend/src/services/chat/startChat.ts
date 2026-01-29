import { apiRequest } from '../client';
import { StartChatResponse } from '../types';

export interface StartChatRequest {
  content: string;
}

export async function startChat(content: string): Promise<StartChatResponse> {
  return apiRequest<StartChatResponse>('/ai/chat/start/', {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

