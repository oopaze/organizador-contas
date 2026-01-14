// Mock data storage for testing without backend
import { User, Actor, Transaction, SubTransaction, Bill } from './types';

// Mock data storage
export let mockUsers: User[] = [
  {
    id: 1,
    email: 'demo@example.com',
    first_name: 'Demo',
    last_name: 'User',
    phone: '+1234567890',
  },
];

export let mockActors: Actor[] = [
  { id: 1, name: 'Amazon' },
  { id: 2, name: 'Netflix' },
  { id: 3, name: 'Supermarket' },
  { id: 4, name: 'Gas Station' },
  { id: 5, name: 'Restaurant' },
];

export let mockTransactions: Transaction[] = [
  {
    id: 1,
    due_date: '2026-01-15',
    total_amount: '5000.00',
    transaction_identifier: 'Salário Mensal',
    transaction_type: 'incoming',
    is_salary: true,
    created_at: '2026-01-01',
  },
  {
    id: 2,
    due_date: '2026-01-20',
    total_amount: '2500.00',
    transaction_identifier: 'Projeto Freelance',
    transaction_type: 'incoming',
    is_salary: false,
    created_at: '2026-01-05',
  },
  {
    id: 3,
    due_date: '2026-01-25',
    total_amount: '1200.00',
    transaction_identifier: 'Fatura Cartão de Crédito',
    transaction_type: 'outgoing',
    is_salary: false,
    created_at: '2026-01-01',
  },
  {
    id: 4,
    due_date: '2025-12-15',
    total_amount: '5000.00',
    transaction_identifier: 'Salário Dezembro',
    transaction_type: 'incoming',
    is_salary: true,
    created_at: '2025-12-01',
  },
  {
    id: 5,
    due_date: '2025-12-25',
    total_amount: '1500.00',
    transaction_identifier: 'Fatura Dezembro',
    transaction_type: 'outgoing',
    is_salary: false,
    created_at: '2025-12-01',
  },
];

export let mockSubTransactions: SubTransaction[] = [
  // Janeiro 2026
  {
    id: 1,
    date: '2026-01-05',
    description: 'Compras no Supermercado',
    amount: '156.50',
    transaction_id: 3,
    actor_id: 3,
    actor: { id: 3, name: 'Supermarket' },
  },
  {
    id: 2,
    date: '2026-01-07',
    description: 'Assinatura Netflix',
    amount: '15.99',
    installment_info: '1/1',
    transaction_id: 3,
    actor_id: 2,
    actor: { id: 2, name: 'Netflix' },
  },
  {
    id: 3,
    date: '2026-01-08',
    description: 'Combustível',
    amount: '45.00',
    transaction_id: 3,
    actor_id: 4,
    actor: { id: 4, name: 'Gas Station' },
  },
  {
    id: 4,
    date: '2026-01-10',
    description: 'Jantar Fora',
    amount: '85.00',
    transaction_id: 3,
    actor_id: 5,
    actor: { id: 5, name: 'Restaurant' },
  },
  {
    id: 5,
    date: '2026-01-12',
    description: 'Amazon Prime',
    amount: '14.99',
    installment_info: '1/12',
    transaction_id: 3,
    actor_id: 1,
    actor: { id: 1, name: 'Amazon' },
  },
  {
    id: 6,
    date: '2026-01-13',
    description: 'Compras',
    amount: '120.75',
    transaction_id: 3,
    actor_id: 3,
    actor: { id: 3, name: 'Supermarket' },
  },
  // Dezembro 2025
  {
    id: 7,
    date: '2025-12-05',
    description: 'Compras de Natal',
    amount: '350.00',
    transaction_id: 5,
    actor_id: 3,
    actor: { id: 3, name: 'Supermarket' },
  },
  {
    id: 8,
    date: '2025-12-10',
    description: 'Presente de Natal',
    amount: '200.00',
    transaction_id: 5,
    actor_id: 1,
    actor: { id: 1, name: 'Amazon' },
  },
  {
    id: 9,
    date: '2025-12-15',
    description: 'Ceia de Natal',
    amount: '450.00',
    transaction_id: 5,
    actor_id: 3,
    actor: { id: 3, name: 'Supermarket' },
  },
  {
    id: 10,
    date: '2025-12-20',
    description: 'Combustível',
    amount: '150.00',
    transaction_id: 5,
    actor_id: 4,
    actor: { id: 4, name: 'Gas Station' },
  },
];

export let mockBills: Bill[] = [
  {
    id: 1,
    file_name: 'credit_card_jan_2026.pdf',
    upload_date: '2026-01-01',
    total_amount: '1200.00',
    due_date: '2026-01-25',
  },
];

// Auto-increment IDs
export const incrementIds = {
  nextUserId: 2,
  nextActorId: 6,
  nextTransactionId: 6,
  nextSubTransactionId: 11,
  nextBillId: 2,
};

// Helper function to simulate network delay
export const delay = (ms: number = 500) => new Promise(resolve => setTimeout(resolve, ms));