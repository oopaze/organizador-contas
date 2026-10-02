import type { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { SubTransaction, Transaction } from '../../services';
import { TransactionsList } from '../transactions-list';

jest.mock('../../services', () => ({
  deleteTransaction: jest.fn(),
  deleteSubTransaction: jest.fn(),
  payTransaction: jest.fn(),
  paySubTransaction: jest.fn(),
  getTransaction: jest.fn(),
}));

import {
  deleteTransaction,
  getTransaction,
  payTransaction,
} from '../../services';

const mockedDelete = deleteTransaction as jest.Mock;
const mockedGetTransaction = getTransaction as jest.Mock;
const mockedPay = payTransaction as jest.Mock;

function buildTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    id: 1,
    due_date: '2026-10-01',
    total_amount: '18.50',
    transaction_identifier: 'Padaria',
    transaction_type: 'outgoing',
    is_salary: false,
    is_recurrent: false,
    is_paid: false,
    category: 'food',
    ...overrides,
  };
}

function buildSubTransaction(overrides: Partial<SubTransaction> = {}): SubTransaction {
  return {
    id: 7,
    date: '2026-10-02',
    description: 'Mercado',
    amount: '89.90',
    transaction_id: 1,
    category: 'food_grocery',
    ...overrides,
  };
}

async function renderList(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity } },
  });
  const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries');
  const result = await render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
  return { ...result, invalidateSpy };
}

beforeEach(() => {
  jest.clearAllMocks();
});

test('mostra a transação com data, categoria, status e valor de terceiros', async () => {
  await renderList(
    <TransactionsList
      transactions={[buildTransaction({ amount_from_actor: 20 })]}
      onChanged={() => {}}
    />
  );

  expect(screen.getByText('Padaria')).toBeTruthy();
  expect(screen.getByText('01/10/2026')).toBeTruthy();
  expect(screen.getByText('food')).toBeTruthy();
  expect(screen.getByText('Despesa')).toBeTruthy();
  expect(screen.getByText('Pendente')).toBeTruthy();
  expect(screen.getByText(/Terceiros: R\$\s?20,00/)).toBeTruthy();
});

test('filtra as transações pelo tipo da aba', async () => {
  await renderList(
    <TransactionsList
      type="expenses"
      transactions={[
        buildTransaction(),
        buildTransaction({
          id: 2,
          transaction_identifier: 'Salário',
          transaction_type: 'incoming',
        }),
      ]}
      onChanged={() => {}}
    />
  );

  expect(screen.getByText('Padaria')).toBeTruthy();
  expect(screen.queryByText('Salário')).toBeNull();
});

test('mostra o vazio certo para o tipo da aba', async () => {
  await renderList(
    <TransactionsList type="income" transactions={[buildTransaction()]} onChanged={() => {}} />
  );

  expect(screen.getByText('Nenhuma receita encontrada')).toBeTruthy();
});

test('paga a transação com confirmação, invalida as queries e avisa a tela', async () => {
  mockedPay.mockResolvedValue({ message: 'success' });
  const onChanged = jest.fn();
  const { invalidateSpy } = await renderList(
    <TransactionsList transactions={[buildTransaction()]} onChanged={onChanged} />
  );

  await fireEvent.press(screen.getByLabelText('Mais opções'));
  await fireEvent.press(screen.getByText('Pagar'));
  await fireEvent.press(screen.getByText('Pagar'));

  await waitFor(() =>
    expect(mockedPay).toHaveBeenCalledWith(1, { updateSubTransactions: true })
  );
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['transactions'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['stats'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['ledger'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['subTransactions'] });
});

test('exclui a transação após confirmação', async () => {
  mockedDelete.mockResolvedValue(undefined);
  const onChanged = jest.fn();
  await renderList(
    <TransactionsList transactions={[buildTransaction()]} onChanged={onChanged} />
  );

  await fireEvent.press(screen.getByLabelText('Excluir transação'));
  await fireEvent.press(screen.getByText('Excluir'));

  await waitFor(() => expect(mockedDelete).toHaveBeenCalledWith(1));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
});

test('mostra erro na lista quando a escrita falha', async () => {
  mockedPay.mockRejectedValue(new Error('Network request failed'));
  await renderList(<TransactionsList transactions={[buildTransaction()]} onChanged={() => {}} />);

  await fireEvent.press(screen.getByLabelText('Mais opções'));
  await fireEvent.press(screen.getByText('Pagar'));
  await fireEvent.press(screen.getByText('Pagar'));

  expect(await screen.findByText(/Falha ao pagar a transação/)).toBeTruthy();
});

test('expande a transação e carrega as subtransações via query', async () => {
  mockedGetTransaction.mockResolvedValue({
    ...buildTransaction(),
    sub_transactions: [buildSubTransaction()],
  });
  await renderList(<TransactionsList transactions={[buildTransaction()]} onChanged={() => {}} />);

  await fireEvent.press(screen.getByText('Padaria'));

  await waitFor(() => expect(mockedGetTransaction).toHaveBeenCalledWith(1));
  expect(await screen.findByText('Mercado')).toBeTruthy();
});

test('mostra estado vazio quando não há transações', async () => {
  await renderList(<TransactionsList transactions={[]} onChanged={() => {}} />);

  expect(screen.getByText('Nenhuma transação encontrada')).toBeTruthy();
});

test('mostra estado de carregando', async () => {
  await renderList(<TransactionsList transactions={undefined} loading onChanged={() => {}} />);

  expect(screen.getByTestId('transactions-loading')).toBeTruthy();
});
