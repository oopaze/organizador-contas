import { fireEvent, render, screen } from '@testing-library/react-native';
import { AddTransactionDialog } from '../add-transaction-dialog';

jest.mock('../../services', () => ({
  createTransaction: jest.fn(),
  getActors: jest.fn().mockResolvedValue([]),
  createActor: jest.fn(),
}));

test('não envia com valor inválido e mostra erro', async () => {
  const { createTransaction } = jest.requireMock('../../services');
  await render(<AddTransactionDialog visible onClose={() => {}} onCreated={() => {}} />);
  await fireEvent.press(screen.getByText('Salvar'));
  expect(createTransaction).not.toHaveBeenCalled();
  expect(screen.getByText('Informe um valor válido')).toBeTruthy();
});
