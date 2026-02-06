// Shared types for API
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  profile?: {
    id: number;
    first_name: string;
    last_name: string;
    bio: string;
    salary: number;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface Actor {
  id: number;
  name: string;
  sub_transactions?: SubTransaction[];
  total_spent?: number;
}

export type TransactionType = 'incoming' | 'outgoing';

export interface Transaction {
  id: number;
  due_date: string;
  total_amount: string;
  transaction_identifier: string;
  transaction_type: TransactionType;
  is_salary: boolean;
  is_recurrent: boolean;
  recurrence_count?: number;
  file?: number;
  created_at?: string;
  amount_from_actor?: number;
  paid_at?: string;
  subtransactions_paid?: boolean;
  is_paid?: boolean;
  category?: string;
}

export interface SubTransaction {
  id: number;
  date: string;
  description: string;
  amount: string;
  installment_info?: string;
  transaction_identifier?: string;
  transaction_id: number;
  actor_id?: number;
  actor?: Actor | number;
  user_provided_description?: string;
  paid_at?: string;
  category?: string;
}

export interface TransactionDetail extends Transaction {
  sub_transactions: SubTransaction[];
  installment_number?: number;
  main_transaction?: number | null;
  paid_at?: string;
  subtransactions_paid?: boolean;
  is_paid?: boolean;
}

export interface Bill {
  id: number;
  file_name: string;
  upload_date: string;
  total_amount: string;
  due_date: string;
}

export interface TransactionFilters {
  transaction_type?: 'incoming' | 'outgoing';
  due_date?: string;
}

export interface TransactionStats {
  incoming_total: number;
  outgoing_total: number;
  incoming_total_paid: number;
  balance: number;
  outgoing_from_actors: number;
  outgoing_from_actors_paid: number;
}

export interface ActorStats {
  total_spent: number;
  total_spent_paid: number;
  biggest_spender: string;
  biggest_spender_amount: number;
  smallest_spender: string;
  smallest_spender_amount: number;
  average_spent: number;
  active_actors: number;
}

// Chat types
export interface AICall {
  id: number;
  created_at: string;
  updated_at: string;
  total_tokens: number;
  input_used_tokens: number;
  output_used_tokens: number;
  input_cost: number;
  output_cost: number;
  model: string;
}

export interface ChatMessage {
  id: number;
  role: 'human' | 'assistant';
  content: string;
  ai_call: AICall | null;
  created_at: string;
  updated_at: string;
}

export interface ChatConversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface StartChatResponse {
  conversation: ChatConversation;
  user_message: ChatMessage;
  ai_message: ChatMessage;
}

export interface SendMessageResponse {
  user_message: ChatMessage;
  ai_message: ChatMessage;
}

// AI Insights types
export interface ModelStats {
  count: number;
  total_tokens: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_spent: number;
}

export interface EmbeddingModelStats {
  count: number;
  total_tokens: number;
  total_prompt_tokens: number;
}

export interface AmountSpent {
  input: number;
  output: number;
  total: number;
}

export interface AICallsStats {
  total_calls: number;
  total_tokens: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_errors: number;
  models_stats: Record<string, ModelStats>;
  amount_spent: AmountSpent;
}

export interface AICallItem {
  id: number;
  created_at: string;
  updated_at: string;
  prompt: string;
  response: unknown;
  total_tokens: number;
  input_used_tokens: number;
  output_used_tokens: number;
  model: string;
  is_error: boolean;
  related_to: 'file' | 'message' | 'conversation' | 'guessing_categories' | 'unknown';
  model_prices: {
    input: number;
    output: number;
    total: number;
  };
  file_url: string | null;
  conversation_title: string | null;
  user_message_content: string | null;
  ai_message_content: string | null;
}

export interface EmbeddingsStats {
  total_embeddings: number;
  total_tokens: number;
  total_prompt_tokens: number;
  total_errors: number;
  models_stats: Record<string, EmbeddingModelStats>;
  amount_spent: number;
}

export interface EmbeddingItem {
  id: number;
  created_at: string;
  updated_at: string;
  model: string;
  total_tokens: number;
  prompt_used_tokens: number;
  price: number;
}