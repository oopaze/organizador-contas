import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { Transaction } from '../../services';
import { EditTransactionDialog } from '../edit-transaction-dialog';

jest.mock('../../services', () => ({
  updateTransaction: jest.fn(),
}));

function buildTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    id: 1,
    due_date: '2026-10-01',
    total_amount: '100.50',
    transaction_identifier: 'Fatura',
    transaction_type: 'outgoing',
    is_salary: false,
    is_recurrent: false,
    ...overrides,
  };
}

test('exibe e salva o valor decimal quando a API o serializa como número', async () => {
  // DRF serializa Decimal como number no JSON (ex.: 100.5), não como string.
  const totalAmountFromApi = 100.5 as unknown as string;
  const { updateTransaction } = jest.requireMock('../../services');
  updateTransaction.mockResolvedValue({});

  await render(
    <EditTransactionDialog
      visible
      onClose={() => {}}
      onUpdated={() => {}}
      transaction={buildTransaction({ total_amount: totalAmountFromApi })}
    />
  );

  expect(screen.getByDisplayValue('100.5')).toBeTruthy();

  await fireEvent.press(screen.getByText('Salvar'));

  await waitFor(() =>
    expect(updateTransaction).toHaveBeenCalledWith(
      1,
      expect.objectContaining({ total_amount: '100.5' })
    )
  );
});
