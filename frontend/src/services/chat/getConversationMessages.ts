import { apiRequest } from '../client';
import { ChatMessage } from '../types';

export async function getConversationMessages(conversationId: number): Promise<ChatMessage[]> {
  return apiRequest<ChatMessage[]>(`/ai/chat/${conversationId}/messages`);
}

