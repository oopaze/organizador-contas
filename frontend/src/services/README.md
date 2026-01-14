# Services Architecture

This directory contains all API service calls organized to mirror the backend structure.

## Structure

```
services/
├── index.ts              # Central export (import everything from here)
├── types.ts              # All TypeScript interfaces
├── client.ts             # Single API client with mock toggle
├── mockData.ts           # Mock data storage for testing
│
├── auth/                 # Authentication endpoints
│   ├── login.ts         # POST /auth/login/
│   ├── register.ts      # POST /user/register/
│   └── refresh.ts       # POST /auth/refresh/
│
├── user/                 # User management endpoints
│   ├── getCurrentUser.ts # GET /user/me/
│   └── updateProfile.ts  # PUT /user/me/profile/
│
├── transactions/         # Transaction endpoints
│   ├── getTransactions.ts    # GET /transactions/transactions/
│   ├── getTransaction.ts     # GET /transactions/transactions/:id/
│   ├── createTransaction.ts  # POST /transactions/transactions/
│   ├── updateTransaction.ts  # PUT /transactions/transactions/:id/
│   └── deleteTransaction.ts  # DELETE /transactions/transactions/:id/
│
├── subTransactions/      # Sub-transaction endpoints
│   ├── getSubTransactions.ts    # GET /transactions/sub_transactions/
│   ├── getSubTransaction.ts     # GET /transactions/sub_transactions/:id/
│   ├── createSubTransaction.ts  # POST /transactions/sub_transactions/
│   ├── updateSubTransaction.ts  # PUT /transactions/sub_transactions/:id/
│   └── deleteSubTransaction.ts  # DELETE /transactions/sub_transactions/:id/
│
├── actors/               # Actor (payee) endpoints
│   ├── getActors.ts     # GET /transactions/actors/
│   ├── getActor.ts      # GET /transactions/actors/:id/
│   ├── createActor.ts   # POST /transactions/actors/
│   ├── updateActor.ts   # PUT /transactions/actors/:id/
│   └── deleteActor.ts   # DELETE /transactions/actors/:id/
│
└── bills/                # Bill endpoints
    ├── getBills.ts      # GET /pdf_reader/bills/
    ├── getBill.ts       # GET /pdf_reader/bills/:id/
    └── uploadBill.ts    # POST /pdf_reader/upload/
```

## Usage

### Import from the central index

```typescript
import { 
  login, 
  getTransactions, 
  createActor,
  User,
  Transaction,
  tokenManager 
} from '@/services';
```

### Switching between Mock and Real API

Edit `/src/services/client.ts`:

```typescript
// For mock mode (no backend needed)
export const USE_MOCK_API = true;

// For real backend
export const USE_MOCK_API = false;
```

## Design Principles

1. **One request per file** - Each endpoint has its own dedicated file
2. **Consistent naming** - Files named after the function they export
3. **Single client** - All requests use the same client with mock toggle
4. **Type safety** - All types defined in `types.ts`
5. **Easy testing** - Mock implementations live alongside real ones

## File Pattern

Each service file follows this pattern:

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { SomeType } from '../types';
import { mockData, delay } from '../mockData';

// Mock implementation
async function someActionMock(params): Promise<SomeType> {
  await delay();
  // Mock logic here
  return mockData;
}

// Real API implementation
async function someActionReal(params): Promise<SomeType> {
  return apiRequest<SomeType>('/endpoint/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// Exported function that switches based on USE_MOCK_API
export async function someAction(params): Promise<SomeType> {
  return USE_MOCK_API ? await someActionMock(params) : await someActionReal(params);
}
```

## Mock Data

Mock data is stored in `mockData.ts` and includes:
- Sample users, transactions, sub-transactions, actors, and bills
- Auto-increment IDs for creating new records
- Network delay simulation for realistic testing

All mock data is stored in memory and resets on page refresh.
