import { apiRequest } from '../client';
import { SendMessageResponse } from '../types';

export async function sendMessageToConversation(
  conversationId: number,
  content: string
): Promise<SendMessageResponse> {
  return apiRequest<SendMessageResponse>(`/ai/chat/${conversationId}/ask`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

