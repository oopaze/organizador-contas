# Service Layer Architecture

## Overview

The service layer has been completely restructured to mirror your backend API organization with **one request per file** and a **single shared client**.

## Directory Tree

```
src/services/
│
├── 📄 index.ts                      # Central export point - import everything from here
├── 📄 types.ts                      # All TypeScript interfaces (User, Transaction, etc.)
├── 📄 client.ts                     # Single API client with mock mode toggle
├── 📄 mockData.ts                   # Mock data storage and utilities
├── 📄 README.md                     # Service architecture documentation
│
├── 📁 auth/                         # Authentication endpoints
│   ├── login.ts                    # POST /auth/login/
│   ├── register.ts                 # POST /user/register/
│   └── refresh.ts                  # POST /auth/refresh/
│
├── 📁 user/                         # User management endpoints
│   ├── getCurrentUser.ts           # GET /user/me/
│   └── updateProfile.ts            # PUT /user/me/profile/
│
├── 📁 transactions/                 # Transaction endpoints
│   ├── getTransactions.ts          # GET /transactions/transactions/
│   ├── getTransaction.ts           # GET /transactions/transactions/:id/
│   ├── createTransaction.ts        # POST /transactions/transactions/
│   ├── updateTransaction.ts        # PUT /transactions/transactions/:id/
│   └── deleteTransaction.ts        # DELETE /transactions/transactions/:id/
│
├── 📁 subTransactions/              # Sub-transaction endpoints
│   ├── getSubTransactions.ts       # GET /transactions/sub_transactions/
│   ├── getSubTransaction.ts        # GET /transactions/sub_transactions/:id/
│   ├── createSubTransaction.ts     # POST /transactions/sub_transactions/
│   ├── updateSubTransaction.ts     # PUT /transactions/sub_transactions/:id/
│   └── deleteSubTransaction.ts     # DELETE /transactions/sub_transactions/:id/
│
├── 📁 actors/                       # Actor (payee) endpoints
│   ├── getActors.ts                # GET /transactions/actors/
│   ├── getActor.ts                 # GET /transactions/actors/:id/
│   ├── createActor.ts              # POST /transactions/actors/
│   ├── updateActor.ts              # PUT /transactions/actors/:id/
│   └── deleteActor.ts              # DELETE /transactions/actors/:id/
│
└── 📁 bills/                        # Bill endpoints
    ├── getBills.ts                 # GET /pdf_reader/bills/
    ├── getBill.ts                  # GET /pdf_reader/bills/:id/
    └── uploadBill.ts               # POST /pdf_reader/upload/
```

## Core Files

### 1. `index.ts` - Central Export Hub

All services are exported from this single file for easy importing:

```typescript
// Central export file for all API services
export * from './types';
export { tokenManager, USE_MOCK_API } from './client';

// Auth services
export { login } from './auth/login';
export { register } from './auth/register';
export { refreshToken } from './auth/refresh';

// User services
export { getCurrentUser } from './user/getCurrentUser';
export { updateProfile } from './user/updateProfile';

// ... and so on
```

**Usage:**
```typescript
import { login, getTransactions, User, Transaction } from '@/services';
```

### 2. `types.ts` - Type Definitions

All TypeScript interfaces in one place:

```typescript
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface Transaction {
  id: number;
  due_date: string;
  total_amount: string;
  transaction_identifier: string;
  transaction_type: 'credit_card' | 'debit' | 'income' | 'other';
  created_at?: string;
}

// ... etc
```

### 3. `client.ts` - Single API Client

The unified client that handles both mock and real API requests:

```typescript
// Toggle between mock and real API
export const USE_MOCK_API = true;

// Token management (works for both mock and real)
export const tokenManager = {
  getAccessToken: () => localStorage.getItem(USE_MOCK_API ? 'mock_access_token' : 'access_token'),
  setTokens: (access, refresh) => { /* ... */ },
  clearTokens: () => { /* ... */ }
};

// Standard API request handler
export async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // Handles authentication, retries, error handling
}

// File upload handler
export async function apiUploadRequest<T>(endpoint: string, formData: FormData): Promise<T> {
  // Handles file uploads with authentication
}
```

### 4. `mockData.ts` - Mock Data Storage

Sample data for testing without a backend:

```typescript
export let mockUsers: User[] = [
  { id: 1, email: 'demo@example.com', first_name: 'Demo', last_name: 'User' }
];

export let mockTransactions: Transaction[] = [ /* ... */ ];
export let mockSubTransactions: SubTransaction[] = [ /* ... */ ];
export let mockActors: Actor[] = [ /* ... */ ];

// Auto-increment IDs for creating new records
export const incrementIds = {
  nextUserId: 2,
  nextActorId: 6,
  nextTransactionId: 4,
  // ... etc
};

// Simulated network delay
export const delay = (ms: number = 500) => new Promise(resolve => setTimeout(resolve, ms));
```

## Service File Pattern

Every service file follows this consistent pattern:

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { SomeType } from '../types';
import { mockData, incrementIds, delay } from '../mockData';

// Mock implementation (for testing without backend)
async function someActionMock(params): Promise<SomeType> {
  await delay(); // Simulate network delay
  
  // Implement mock logic using mockData
  const result = mockData.find(item => item.id === params.id);
  if (!result) throw new Error('Not found');
  
  return result;
}

// Real API implementation (for production)
async function someActionReal(params): Promise<SomeType> {
  return apiRequest<SomeType>('/api/endpoint/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// Exported function that switches based on USE_MOCK_API
export async function someAction(params): Promise<SomeType> {
  return USE_MOCK_API 
    ? await someActionMock(params) 
    : await someActionReal(params);
}
```

## Example Service Files

### GET Request Example (`getTransactions.ts`)

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { Transaction } from '../types';
import { mockTransactions, delay } from '../mockData';

async function getTransactionsMock(): Promise<Transaction[]> {
  await delay();
  return [...mockTransactions]; // Return copy to prevent mutations
}

async function getTransactionsReal(): Promise<Transaction[]> {
  return apiRequest<Transaction[]>('/transactions/transactions/');
}

export async function getTransactions(): Promise<Transaction[]> {
  return USE_MOCK_API ? await getTransactionsMock() : await getTransactionsReal();
}
```

### POST Request Example (`createActor.ts`)

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, incrementIds, delay } from '../mockData';

async function createActorMock(data: Omit<Actor, 'id'>): Promise<Actor> {
  await delay();
  
  const newActor: Actor = {
    ...data,
    id: incrementIds.nextActorId++, // Auto-increment ID
  };
  
  mockActors.push(newActor);
  return newActor;
}

async function createActorReal(data: Omit<Actor, 'id'>): Promise<Actor> {
  return apiRequest<Actor>('/transactions/actors/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createActor(data: Omit<Actor, 'id'>): Promise<Actor> {
  return USE_MOCK_API ? await createActorMock(data) : await createActorReal(data);
}
```

### DELETE Request Example (`deleteTransaction.ts`)

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { mockTransactions, delay } from '../mockData';

async function deleteTransactionMock(id: number): Promise<void> {
  await delay();
  
  const index = mockTransactions.findIndex(t => t.id === id);
  if (index === -1) throw new Error('Transaction not found');
  
  mockTransactions.splice(index, 1);
}

async function deleteTransactionReal(id: number): Promise<void> {
  return apiRequest<void>(`/transactions/transactions/${id}/`, {
    method: 'DELETE',
  });
}

export async function deleteTransaction(id: number): Promise<void> {
  return USE_MOCK_API ? await deleteTransactionMock(id) : await deleteTransactionReal(id);
}
```

## Usage in Components

### Before (Old Way)

```typescript
import { api } from '@/services/api';

// Inside component
const transactions = await api.getTransactions();
await api.createActor({ name: 'Amazon' });
await api.deleteTransaction(id);
```

### After (New Way)

```typescript
import { getTransactions, createActor, deleteTransaction } from '@/services';

// Inside component  
const transactions = await getTransactions();
await createActor({ name: 'Amazon' });
await deleteTransaction(id);
```

**Benefits:**
- ✅ Cleaner imports
- ✅ Better tree-shaking (only imports what you use)
- ✅ Better IDE autocomplete
- ✅ Easier to test individual functions

## Mock vs Real API

### Mock Mode (Default)

```typescript
// /src/services/client.ts
export const USE_MOCK_API = true;
```

**Characteristics:**
- ✅ No backend required
- ✅ Instant responses (simulated delay)
- ✅ Perfect for development
- ✅ Data stored in memory (resets on refresh)
- ✅ Pre-loaded with sample data

**Use Cases:**
- Frontend development
- UI/UX testing
- Demos and presentations
- When backend is unavailable

### Real API Mode

```typescript
// /src/services/client.ts
export const USE_MOCK_API = false;
```

**Characteristics:**
- 🔌 Requires backend running
- 🔑 Uses JWT authentication
- 💾 Data persists in database
- 🌐 Real network requests
- ⚡ Auto-refresh on 401 errors

**Configuration:**
```env
# .env file
VITE_API_BASE_URL=http://localhost:8000
```

**Use Cases:**
- Production environment
- Integration testing
- Backend development
- Real data persistence

## Adding New Endpoints

### Step-by-Step Guide

1. **Define the type** (if needed) in `types.ts`:
   ```typescript
   export interface NewModel {
     id: number;
     name: string;
   }
   ```

2. **Add mock data** (if needed) in `mockData.ts`:
   ```typescript
   export let mockNewModels: NewModel[] = [
     { id: 1, name: 'Example' }
   ];
   ```

3. **Create the service file**:
   ```typescript
   // /src/services/newFolder/getNewModels.ts
   import { apiRequest, USE_MOCK_API } from '../client';
   import { NewModel } from '../types';
   import { mockNewModels, delay } from '../mockData';
   
   async function getNewModelsMock(): Promise<NewModel[]> {
     await delay();
     return [...mockNewModels];
   }
   
   async function getNewModelsReal(): Promise<NewModel[]> {
     return apiRequest<NewModel[]>('/api/newmodels/');
   }
   
   export async function getNewModels(): Promise<NewModel[]> {
     return USE_MOCK_API ? getNewModelsMock() : getNewModelsReal();
   }
   ```

4. **Export from index.ts**:
   ```typescript
   export { getNewModels } from './newFolder/getNewModels';
   ```

5. **Use in components**:
   ```typescript
   import { getNewModels, NewModel } from '@/services';
   
   const models = await getNewModels();
   ```

## Best Practices

### ✅ DO:
- Import from `@/services` (central index)
- Follow the file naming convention: `getResource.ts`, `createResource.ts`, etc.
- Include both mock and real implementations
- Add type safety with TypeScript
- Handle errors appropriately
- Use the shared `apiRequest` helper

### ❌ DON'T:
- Import from service files directly (use index.ts)
- Mix business logic in service files (keep them thin)
- Forget to export new services from index.ts
- Skip the mock implementation (useful for testing)
- Hardcode API URLs (use client.ts)

## Component Updates

All components have been migrated to the new structure:

| Component | Updated Imports |
|-----------|-----------------|
| `AuthContext.tsx` | `login`, `register`, `getCurrentUser`, `tokenManager` |
| `Dashboard.tsx` | `getTransactions`, `getSubTransactions` |
| `TransactionsList.tsx` | `deleteTransaction`, `deleteSubTransaction` |
| `AddTransactionDialog.tsx` | `createTransaction` |
| `AddSubTransactionDialog.tsx` | `getActors`, `createActor`, `createSubTransaction` |

## Testing

### Unit Testing Services

```typescript
// Mock mode makes testing easy
import { USE_MOCK_API } from '@/services/client';
import { getTransactions, createTransaction } from '@/services';

test('should get transactions', async () => {
  const transactions = await getTransactions();
  expect(transactions).toBeInstanceOf(Array);
});

test('should create transaction', async () => {
  const newTransaction = await createTransaction({
    transaction_identifier: 'Test',
    total_amount: '100.00',
    due_date: '2026-01-15',
    transaction_type: 'income'
  });
  
  expect(newTransaction.id).toBeDefined();
});
```

## Migration Checklist

- [x] Created modular service structure
- [x] One request per file
- [x] Single shared client
- [x] Mock mode toggle in one place
- [x] All types centralized
- [x] Components updated to use new imports
- [x] Old `api.ts` and `mockApi.ts` deleted
- [x] Documentation created

## Quick Reference

| Need to... | Edit File... | Change... |
|------------|-------------|-----------|
| Toggle mock/real | `/src/services/client.ts` | `USE_MOCK_API = true/false` |
| Add mock data | `/src/services/mockData.ts` | Add to arrays |
| Add new endpoint | `/src/services/folder/action.ts` | Create new file |
| Export new service | `/src/services/index.ts` | Add export line |
| Add new type | `/src/services/types.ts` | Add interface |
| Change backend URL | `.env` | `VITE_API_BASE_URL=...` |

---

**Questions or issues?** Check the other documentation files or review the service implementation examples.
