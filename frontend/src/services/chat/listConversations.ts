import { apiRequest } from '../client';
import { ChatConversation } from '../types';

export async function listConversations(): Promise<ChatConversation[]> {
  return apiRequest<ChatConversation[]>('/ai/chat/list/');
}

