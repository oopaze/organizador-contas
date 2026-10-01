import type { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { SubTransaction } from '../../services';
import { SubTransactionsList } from '../sub-transactions-list';

jest.mock('../../services', () => ({
  deleteTransaction: jest.fn(),
  deleteSubTransaction: jest.fn(),
  payTransaction: jest.fn(),
  paySubTransaction: jest.fn(),
  getTransaction: jest.fn(),
}));

import { deleteSubTransaction, paySubTransaction } from '../../services';

const mockedDelete = deleteSubTransaction as jest.Mock;
const mockedPay = paySubTransaction as jest.Mock;

function buildSubTransaction(overrides: Partial<SubTransaction> = {}): SubTransaction {
  return {
    id: 7,
    date: '2026-10-02',
    description: 'Mercado',
    amount: '89.90',
    installment_info: 'installment 2 of 5',
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

test('mostra os dados da subtransação com categoria, parcela, ator e status', async () => {
  await renderList(
    <SubTransactionsList
      subTransactions={[buildSubTransaction()]}
      onChanged={() => {}}
      selfLabel="Ana Silva (Eu)"
    />
  );

  expect(screen.getByText('Mercado')).toBeTruthy();
  expect(screen.getByText(/R\$\s?89,90/)).toBeTruthy();
  expect(screen.getByText('food_grocery')).toBeTruthy();
  expect(screen.getByText('2/5')).toBeTruthy();
  expect(screen.getByText('Pendente')).toBeTruthy();
  expect(screen.getByText('Ana Silva (Eu)')).toBeTruthy();
});

test('paga a subtransação após confirmação, invalida as queries e avisa a tela', async () => {
  mockedPay.mockResolvedValue({ message: 'success' });
  const onChanged = jest.fn();
  const { invalidateSpy } = await renderList(
    <SubTransactionsList subTransactions={[buildSubTransaction()]} onChanged={onChanged} />
  );

  await fireEvent.press(screen.getByLabelText('Mais opções'));
  await fireEvent.press(screen.getByText('Pagar'));
  await fireEvent.press(screen.getByText('Pagar'));

  await waitFor(() => expect(mockedPay).toHaveBeenCalledWith(7));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['transactions'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['stats'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['ledger'] });
  expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['subTransactions'] });
});

test('exclui a subtransação após confirmação', async () => {
  mockedDelete.mockResolvedValue(undefined);
  const onChanged = jest.fn();
  await renderList(
    <SubTransactionsList subTransactions={[buildSubTransaction()]} onChanged={onChanged} />
  );

  await fireEvent.press(screen.getByLabelText('Excluir subtransação'));
  await fireEvent.press(screen.getByText('Excluir'));

  await waitFor(() => expect(mockedDelete).toHaveBeenCalledWith(7));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
});

test('mostra erro na lista quando a escrita falha', async () => {
  mockedPay.mockRejectedValue(new Error('Network request failed'));
  await renderList(<SubTransactionsList subTransactions={[buildSubTransaction()]} />);

  await fireEvent.press(screen.getByLabelText('Mais opções'));
  await fireEvent.press(screen.getByText('Pagar'));
  await fireEvent.press(screen.getByText('Pagar'));

  expect(await screen.findByText(/Falha ao pagar a subtransação/)).toBeTruthy();
});

test('mostra estado vazio quando não há subtransações', async () => {
  await renderList(<SubTransactionsList subTransactions={[]} />);

  expect(screen.getByText('Nenhuma subtransação encontrada')).toBeTruthy();
});

test('mostra estado de carregando', async () => {
  await renderList(<SubTransactionsList subTransactions={undefined} loading />);

  expect(screen.getByTestId('sub-transactions-loading')).toBeTruthy();
});

test('mostra erro de leitura com ação de tentar novamente', async () => {
  const onRetry = jest.fn();
  await renderList(
    <SubTransactionsList
      subTransactions={undefined}
      error="Falha ao carregar subtransações"
      onRetry={onRetry}
    />
  );

  expect(screen.getByText('Falha ao carregar subtransações')).toBeTruthy();
  await fireEvent.press(screen.getByText('Tentar novamente'));
  expect(onRetry).toHaveBeenCalledTimes(1);
});
