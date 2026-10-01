import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { QuickAddDialog } from '../quick-add-dialog';

jest.mock('../../services', () => ({
  getActors: jest.fn().mockResolvedValue([]),
  quickAddTransaction: jest.fn(),
}));

import { quickAddTransaction } from '../../services';

const mockedQuickAdd = quickAddTransaction as jest.Mock;

function buildResult(openBillTotal: string | null) {
  return {
    transaction: {},
    sub_transaction_id: 1,
    open_bill_total: openBillTotal,
  };
}

beforeEach(() => {
  jest.clearAllMocks();
});

test('dinheiro: converte a vírgula do valor e envia o lançamento', async () => {
  mockedQuickAdd.mockResolvedValue(buildResult(null));
  const onCreated = jest.fn();
  await render(<QuickAddDialog visible onClose={() => {}} onCreated={onCreated} />);

  await fireEvent.changeText(screen.getByLabelText('Valor'), '54,90');
  await fireEvent.changeText(screen.getByLabelText('Descrição'), 'Padaria');
  await fireEvent.press(screen.getByText('Lançar'));

  await waitFor(() =>
    expect(mockedQuickAdd).toHaveBeenCalledWith(
      expect.objectContaining({
        direction: 'outgoing',
        payment_method: 'cash',
        amount: '54.90',
        description: 'Padaria',
        installments: 1,
        is_paid: false,
      })
    )
  );
  expect(onCreated).toHaveBeenCalledTimes(1);
});

test('cartão: exige o cartão e envia crédito com o total da fatura em aberto', async () => {
  mockedQuickAdd.mockResolvedValue(buildResult('354.90'));
  await render(<QuickAddDialog visible onClose={() => {}} onCreated={() => {}} />);

  await fireEvent.changeText(screen.getByLabelText('Valor'), '54,90');
  await fireEvent.changeText(screen.getByLabelText('Descrição'), 'Padaria');
  await fireEvent.press(screen.getByText('Cartão'));
  await fireEvent.press(screen.getByText('Lançar'));

  expect(mockedQuickAdd).not.toHaveBeenCalled();
  expect(screen.getByText('Informe o cartão')).toBeTruthy();

  await fireEvent.changeText(screen.getByLabelText('Cartão'), 'Nubank');
  await fireEvent.press(screen.getByText('Lançar'));

  await waitFor(() =>
    expect(mockedQuickAdd).toHaveBeenCalledWith(
      expect.objectContaining({ payment_method: 'credit', card_label: 'Nubank' })
    )
  );
  expect(await screen.findByText(/Fatura em aberto: R\$\s?354,90/)).toBeTruthy();
});
