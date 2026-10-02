jest.mock('../../services', () => ({
  createIntention: jest.fn(),
  updateIntention: jest.fn(),
}));

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { PurchaseIntention } from '../../services';
import { createIntention, updateIntention } from '../../services';
import { IntentionDialog } from '../intention-dialog';

const mockedCreate = createIntention as jest.Mock;
const mockedUpdate = updateIntention as jest.Mock;

function buildIntention(overrides: Partial<PurchaseIntention> = {}): PurchaseIntention {
  return {
    id: 1,
    name: 'Notebook',
    amount: '4500.00',
    month: '2026-10-01',
    installments: 1,
    status: 'planned',
    transaction_id: null,
    ...overrides,
  };
}

beforeEach(() => {
  jest.clearAllMocks();
});

test('não envia com campos inválidos e mostra erro', async () => {
  await render(
    <IntentionDialog visible onClose={() => {}} onSaved={() => {}} defaultMonth="2026-10" />
  );

  await fireEvent.press(screen.getByText('Adicionar intenção'));

  expect(mockedCreate).not.toHaveBeenCalled();
  expect(screen.getByText('Informe o que você quer comprar')).toBeTruthy();
  expect(screen.getByText('Informe um valor válido')).toBeTruthy();
});

test('cria a intenção com valor decimal e parcelas', async () => {
  mockedCreate.mockResolvedValue(buildIntention({ installments: 3 }));
  const onSaved = jest.fn();
  const onClose = jest.fn();
  await render(
    <IntentionDialog visible onClose={onClose} onSaved={onSaved} defaultMonth="2026-10" />
  );

  await fireEvent.changeText(screen.getByLabelText('O que você quer comprar'), 'Notebook');
  await fireEvent.changeText(screen.getByLabelText('Valor total'), '4500,00');
  await fireEvent.changeText(screen.getByLabelText('Parcelas'), '3');
  await fireEvent.press(screen.getByText('Adicionar intenção'));

  await waitFor(() =>
    expect(mockedCreate).toHaveBeenCalledWith({
      name: 'Notebook',
      amount: '4500.00',
      month: '2026-10-01',
      installments: 3,
    })
  );
  expect(onSaved).toHaveBeenCalledTimes(1);
  expect(onClose).toHaveBeenCalledTimes(1);
});

test('edita a intenção existente com os campos preenchidos', async () => {
  mockedUpdate.mockResolvedValue(buildIntention());
  const onSaved = jest.fn();
  await render(
    <IntentionDialog
      visible
      intention={buildIntention({ amount: '4500.00', installments: 3 })}
      onClose={() => {}}
      onSaved={onSaved}
    />
  );

  expect(screen.getByText('Editar intenção')).toBeTruthy();
  await fireEvent.changeText(screen.getByLabelText('Valor total'), '4300,00');
  await fireEvent.press(screen.getByText('Salvar alterações'));

  await waitFor(() =>
    expect(mockedUpdate).toHaveBeenCalledWith(1, {
      name: 'Notebook',
      amount: '4300.00',
      month: '2026-10-01',
      installments: 3,
    })
  );
  expect(onSaved).toHaveBeenCalledTimes(1);
});
