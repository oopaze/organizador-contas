import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { SubTransaction } from '../../services';
import { EditSubTransactionDialog } from '../edit-sub-transaction-dialog';

jest.mock('../../services', () => ({
  getActors: jest.fn().mockResolvedValue([]),
  updateSubTransaction: jest.fn(),
}));

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

test('abre a edição com o valor decimal da API serializado como número', async () => {
  // DRF serializa Decimal como number no JSON (ex.: 89.9), não como string.
  const amountFromApi = 89.9 as unknown as string;
  const { updateSubTransaction } = jest.requireMock('../../services');
  updateSubTransaction.mockResolvedValue({});

  await render(
    <EditSubTransactionDialog
      visible
      onClose={() => {}}
      onUpdated={() => {}}
      subTransaction={buildSubTransaction({ amount: amountFromApi })}
    />
  );

  expect(screen.getByText('Editar Subtransação')).toBeTruthy();
  expect(screen.getByDisplayValue('89.9')).toBeTruthy();

  await fireEvent.press(screen.getByText('Salvar'));

  await waitFor(() =>
    expect(updateSubTransaction).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ amount: '89.9' })
    )
  );
});
