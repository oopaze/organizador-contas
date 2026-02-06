import { apiRequest } from '../client';
import { EmbeddingItem } from '../types';

export async function getEmbeddings(): Promise<EmbeddingItem[]> {
  return apiRequest<EmbeddingItem[]>('/ai/embeddings/');
}

