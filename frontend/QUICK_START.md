# Quick Start Guide

## 🚀 Run the App (Mock Mode - No Backend Needed!)

```bash
# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev

# 3. Open in browser
# Visit http://localhost:5173

# 4. Login
# Email: demo@example.com
# Password: password123
```

That's it! The app runs with mock data - no backend required.

---

## 🔄 Switch to Real Backend

### Option 1: Edit client.ts
```typescript
// File: /src/services/client.ts
export const USE_MOCK_API = false;  // Change from true to false
```

### Option 2: Set environment variable
```bash
# File: .env
VITE_API_BASE_URL=http://localhost:8000
```

Then restart the dev server.

---

## 📁 Project Structure

```
src/
├── app/
│   ├── components/       # React components
│   │   ├── Dashboard.tsx
│   │   ├── LoginPage.tsx
│   │   ├── TransactionsList.tsx
│   │   ├── AddTransactionDialog.tsx
│   │   └── AddSubTransactionDialog.tsx
│   └── App.tsx
│
├── contexts/
│   └── AuthContext.tsx   # Auth state management
│
├── services/             # ⭐ API services (NEW STRUCTURE)
│   ├── index.ts         # Import everything from here!
│   ├── types.ts         # TypeScript types
│   ├── client.ts        # API client (toggle mock mode here)
│   ├── mockData.ts      # Sample data
│   │
│   ├── auth/            # Authentication
│   ├── user/            # User management
│   ├── transactions/    # Transactions CRUD
│   ├── subTransactions/ # Sub-transactions CRUD
│   ├── actors/          # Actors (payees) CRUD
│   └── bills/           # Bills & PDF upload
│
└── styles/
```

---

## 📝 Common Tasks

### Add a new expense
1. Click "Add Expense" in the Dashboard
2. Fill in the form (date, amount, description, payee)
3. Click "Add Expense"

### Add a new income
1. Click "Add Income" in the Dashboard
2. Fill in the form (identifier, amount, due date)
3. Click "Add Income"

### Create a new payee
1. Open "Add Expense" dialog
2. In the Payee dropdown, select "Add New Payee"
3. Enter the payee name
4. Click "Create Payee"

### Delete a transaction
1. Go to the "All Transactions" or "Income" tab
2. Click the trash icon next to the transaction
3. Confirm deletion

### Delete an expense
1. Go to the "Expenses" tab
2. Click the trash icon next to the expense
3. Confirm deletion

---

## 🛠 Development

### Import services in your components

```typescript
// Import what you need from '@/services'
import { 
  login,
  getTransactions, 
  createActor,
  User,
  Transaction 
} from '@/services';

// Use them directly
const transactions = await getTransactions();
const newActor = await createActor({ name: 'Amazon' });
```

### Add a new API endpoint

1. **Create the service file**
   ```typescript
   // /src/services/yourFolder/yourAction.ts
   import { apiRequest, USE_MOCK_API } from '../client';
   
   async function yourActionMock() {
     // Mock implementation
   }
   
   async function yourActionReal() {
     return apiRequest('/your/endpoint/');
   }
   
   export async function yourAction() {
     return USE_MOCK_API ? yourActionMock() : yourActionReal();
   }
   ```

2. **Export it from index.ts**
   ```typescript
   // /src/services/index.ts
   export { yourAction } from './yourFolder/yourAction';
   ```

3. **Use it in your component**
   ```typescript
   import { yourAction } from '@/services';
   const result = await yourAction();
   ```

---

## 🐛 Troubleshooting

### "Failed to load data"
- **Mock Mode**: Check browser console for errors
- **Real Mode**: Ensure backend is running on `http://localhost:8000`

### "Session expired" / 401 errors
- **Mock Mode**: Clear localStorage and refresh
- **Real Mode**: Login again

### Changes not reflected
- Save all files and refresh the browser
- Check that you're importing from `@/services`

### CORS errors (Real Mode only)
Add CORS headers to your backend:
```python
# Django example
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

---

## 📚 More Info

- **Service Architecture**: See `/src/services/README.md`
- **Migration Guide**: See `/MIGRATION_GUIDE.md`
- **Full Documentation**: See `/README.md`

---

## 🎯 Quick Reference

| Action | File to Edit | What to Change |
|--------|-------------|----------------|
| Toggle mock/real API | `/src/services/client.ts` | `USE_MOCK_API = true/false` |
| Change backend URL | `.env` | `VITE_API_BASE_URL=...` |
| Add mock data | `/src/services/mockData.ts` | Add to arrays |
| Add new endpoint | `/src/services/yourFolder/` | Create new file |
| Import types | Any component | `import { Type } from '@/services'` |

---

Happy coding! 🎉
