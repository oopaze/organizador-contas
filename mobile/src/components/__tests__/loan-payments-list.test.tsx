jest.mock('../../services', () => ({
  deleteLoanPayment: jest.fn(),
}));

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { deleteLoanPayment, type LoanPayment } from '../../services';
import { LoanPaymentsList } from '../loan-payments-list';

const mockedDelete = deleteLoanPayment as jest.Mock;

function buildPayment(overrides: Partial<LoanPayment> = {}): LoanPayment {
  return {
    id: 1,
    loan_id: 3,
    amount: '250.00',
    paid_at: '2026-10-01',
    note: '',
    file_id: null,
    file_url: null,
    created_at: null,
    updated_at: null,
    ...overrides,
  };
}

beforeEach(() => {
  jest.clearAllMocks();
});

test('mostra pagamentos com valor formatado', async () => {
  await render(
    <LoanPaymentsList
      payments={[{ id: 1, amount: '250.00', paid_at: '2026-10-01' } as never]}
      onChanged={() => {}}
    />
  );

  expect(screen.getByText(/R\$\s?250,00/)).toBeTruthy();
});

test('apaga o pagamento com confirmação e avisa a tela', async () => {
  mockedDelete.mockResolvedValue(undefined);
  const onChanged = jest.fn();

  await render(<LoanPaymentsList payments={[buildPayment()]} onChanged={onChanged} />);

  await fireEvent.press(screen.getByLabelText('Remover pagamento'));
  await fireEvent.press(screen.getByText('Excluir'));

  await waitFor(() => expect(mockedDelete).toHaveBeenCalledWith(1));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
});
