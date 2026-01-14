# Migration Guide: Service Restructure

## What Changed?

The API services have been **restructured to follow your backend architecture** with one request per file and a single shared client.

## Before vs After

### ❌ Before (Old Structure)

```
services/
├── api.ts          # Everything in one file
└── mockApi.ts      # Separate mock implementation
```

```typescript
// Old import style
import { api } from '@/services/api';

// Usage
await api.login(credentials);
await api.getTransactions();
await api.createActor({ name: 'Amazon' });
```

### ✅ After (New Structure)

```
services/
├── index.ts              # Central export point
├── types.ts              # All TypeScript types
├── client.ts             # Single API client (mock toggle)
├── mockData.ts           # Mock data storage
├── auth/                 # Auth endpoints (login, register, refresh)
├── user/                 # User endpoints (getCurrentUser, updateProfile)
├── transactions/         # Transaction CRUD
├── subTransactions/      # Sub-transaction CRUD
├── actors/               # Actor CRUD
└── bills/                # Bills endpoints
```

```typescript
// New import style - import directly from '@/services'
import { login, getTransactions, createActor } from '@/services';

// Usage (cleaner!)
await login(credentials);
await getTransactions();
await createActor({ name: 'Amazon' });
```

## Key Benefits

### 1. **Follows Backend Structure**
Each service file maps 1:1 with a backend endpoint:
- `services/auth/login.ts` → `POST /auth/login/`
- `services/transactions/getTransactions.ts` → `GET /transactions/transactions/`
- `services/actors/createActor.ts` → `POST /transactions/actors/`

### 2. **One Request Per File**
Easy to find, edit, and maintain individual endpoints.

### 3. **Single Client**
All requests (mock and real) use the same client from `client.ts`.

### 4. **Easy Mock Toggle**
Switch between mock and real API in one place:

```typescript
// In /src/services/client.ts
export const USE_MOCK_API = true;  // or false
```

### 5. **Better Type Safety**
All types centralized in `types.ts`:

```typescript
import { User, Transaction, Actor } from '@/services';
```

### 6. **Cleaner Imports**
Everything exports from `services/index.ts`:

```typescript
// Import everything you need in one line
import { 
  login, 
  register, 
  getTransactions, 
  createActor,
  User,
  Transaction,
  tokenManager 
} from '@/services';
```

## File Mapping Guide

| Backend Endpoint | Service File | Function |
|-----------------|--------------|----------|
| `POST /auth/login/` | `auth/login.ts` | `login()` |
| `POST /user/register/` | `auth/register.ts` | `register()` |
| `POST /auth/refresh/` | `auth/refresh.ts` | `refreshToken()` |
| `GET /user/me/` | `user/getCurrentUser.ts` | `getCurrentUser()` |
| `PUT /user/me/profile/` | `user/updateProfile.ts` | `updateProfile()` |
| `GET /transactions/transactions/` | `transactions/getTransactions.ts` | `getTransactions()` |
| `GET /transactions/transactions/:id/` | `transactions/getTransaction.ts` | `getTransaction()` |
| `POST /transactions/transactions/` | `transactions/createTransaction.ts` | `createTransaction()` |
| `PUT /transactions/transactions/:id/` | `transactions/updateTransaction.ts` | `updateTransaction()` |
| `DELETE /transactions/transactions/:id/` | `transactions/deleteTransaction.ts` | `deleteTransaction()` |
| `GET /transactions/sub_transactions/` | `subTransactions/getSubTransactions.ts` | `getSubTransactions()` |
| `POST /transactions/sub_transactions/` | `subTransactions/createSubTransaction.ts` | `createSubTransaction()` |
| `DELETE /transactions/sub_transactions/:id/` | `subTransactions/deleteSubTransaction.ts` | `deleteSubTransaction()` |
| `GET /transactions/actors/` | `actors/getActors.ts` | `getActors()` |
| `POST /transactions/actors/` | `actors/createActor.ts` | `createActor()` |
| `GET /pdf_reader/bills/` | `bills/getBills.ts` | `getBills()` |
| `POST /pdf_reader/upload/` | `bills/uploadBill.ts` | `uploadBill()` |

## How to Add New Endpoints

### Step 1: Add the type (if needed)
Edit `/src/services/types.ts`:

```typescript
export interface NewType {
  id: number;
  name: string;
}
```

### Step 2: Create the service file
Create `/src/services/newFolder/newAction.ts`:

```typescript
import { apiRequest, USE_MOCK_API } from '../client';
import { NewType } from '../types';
import { mockData, delay } from '../mockData';

async function newActionMock(params): Promise<NewType> {
  await delay();
  // Mock implementation
  return mockData;
}

async function newActionReal(params): Promise<NewType> {
  return apiRequest<NewType>('/api/endpoint/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function newAction(params): Promise<NewType> {
  return USE_MOCK_API ? await newActionMock(params) : await newActionReal(params);
}
```

### Step 3: Export it
Edit `/src/services/index.ts`:

```typescript
export { newAction } from './newFolder/newAction';
```

### Step 4: Use it
In your component:

```typescript
import { newAction } from '@/services';

const result = await newAction(params);
```

## Testing

### Mock Mode (Default)
```typescript
// /src/services/client.ts
export const USE_MOCK_API = true;
```
- No backend needed
- Uses sample data from `mockData.ts`
- Data resets on page refresh
- Great for development and testing

### Real Backend Mode
```typescript
// /src/services/client.ts
export const USE_MOCK_API = false;
```
- Connects to real backend at `VITE_API_BASE_URL`
- Requires backend running
- Data persists in database

## Updated Components

All components have been updated to use the new service structure:

- ✅ `AuthContext.tsx` - Uses `login`, `register`, `getCurrentUser`
- ✅ `Dashboard.tsx` - Uses `getTransactions`, `getSubTransactions`
- ✅ `TransactionsList.tsx` - Uses `deleteTransaction`, `deleteSubTransaction`
- ✅ `AddTransactionDialog.tsx` - Uses `createTransaction`
- ✅ `AddSubTransactionDialog.tsx` - Uses `getActors`, `createActor`, `createSubTransaction`

## Questions?

- 📁 See `/src/services/README.md` for detailed service architecture
- 📖 Check individual service files for implementation examples
- 🔧 Toggle mock mode in `/src/services/client.ts`
