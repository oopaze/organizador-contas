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
}

export interface SubTransaction {
  id: number;
  date: string;
  description: string;
  amount: string;
  installment_info?: string;
  transaction_identifier: string;
  transaction_id: number;
  actor_id?: number;
  actor?: Actor | number;
  user_provided_description?: string;
}

export interface TransactionDetail extends Transaction {
  sub_transactions: SubTransaction[];
  installment_number?: number;
  main_transaction?: number | null;
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
  balance: number;
  outgoing_from_actors: number;
}