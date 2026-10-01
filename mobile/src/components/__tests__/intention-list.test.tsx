jest.mock('../../services', () => ({
  convertIntention: jest.fn(),
  deleteIntention: jest.fn(),
}));

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import type { PurchaseIntention } from '../../services';
import { convertIntention, deleteIntention } from '../../services';
import { IntentionList } from '../intention-list';

const mockedConvert = convertIntention as jest.Mock;
const mockedDelete = deleteIntention as jest.Mock;

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

test('mostra intenção com valor formatado', async () => {
  await render(<IntentionList intentions={[buildIntention()]} onChanged={() => {}} />);

  expect(screen.getByText('Notebook')).toBeTruthy();
  expect(screen.getByText(/R\$\s?4\.500,00/)).toBeTruthy();
});

test('marca a parcela de intenção anterior (carry-over)', async () => {
  await render(
    <IntentionList intentions={[buildIntention({ carry_over: true })]} onChanged={() => {}} />
  );

  expect(screen.getByText('Parcela de intenção anterior')).toBeTruthy();
});

test('converte a intenção após confirmação', async () => {
  mockedConvert.mockResolvedValue(buildIntention({ status: 'bought', transaction_id: 9 }));
  const onChanged = jest.fn();
  await render(<IntentionList intentions={[buildIntention()]} onChanged={onChanged} />);

  await fireEvent.press(screen.getByText('Virar transação'));
  expect(screen.getByText('Virar transação?')).toBeTruthy();
  await fireEvent.press(screen.getByText('Confirmar'));

  await waitFor(() => expect(mockedConvert).toHaveBeenCalledWith(1));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
});

test('exclui a intenção descartada após confirmação', async () => {
  mockedDelete.mockResolvedValue(undefined);
  const onChanged = jest.fn();
  await render(
    <IntentionList intentions={[buildIntention({ status: 'dismissed' })]} onChanged={onChanged} />
  );

  expect(screen.getByText('Descartada')).toBeTruthy();
  expect(screen.queryByText('Virar transação')).toBeNull();
  expect(screen.queryByText('Editar')).toBeNull();

  await fireEvent.press(screen.getByLabelText('Excluir'));
  expect(screen.getByText('Excluir intenção?')).toBeTruthy();
  await fireEvent.press(screen.getByText('Confirmar'));

  await waitFor(() => expect(mockedDelete).toHaveBeenCalledWith(1));
  await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
});

test('não oferece converter nem editar para intenção comprada', async () => {
  await render(
    <IntentionList
      intentions={[buildIntention({ status: 'bought', transaction_id: 9 })]}
      onChanged={() => {}}
    />
  );

  expect(screen.getByText('Comprada')).toBeTruthy();
  expect(screen.queryByText('Virar transação')).toBeNull();
  expect(screen.queryByText('Editar')).toBeNull();
  expect(screen.queryByLabelText('Excluir')).toBeNull();
});

test('mostra o erro do backend inline quando a conversão falha', async () => {
  mockedConvert.mockRejectedValue(new Error('Intenção já convertida'));
  await render(<IntentionList intentions={[buildIntention()]} onChanged={() => {}} />);

  await fireEvent.press(screen.getByText('Virar transação'));
  await fireEvent.press(screen.getByText('Confirmar'));

  expect(await screen.findByText('Intenção já convertida')).toBeTruthy();
});
