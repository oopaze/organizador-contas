jest.mock('../../services', () => ({
  createCard: jest.fn(),
  updateCard: jest.fn(),
}));

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { createCard, updateCard } from '../../services';
import { CardFormDialog } from '../card-form-dialog';

const mockedCreate = createCard as jest.Mock;
const mockedUpdate = updateCard as jest.Mock;

beforeEach(() => {
  jest.clearAllMocks();
});

test('cria o cartão normalizando o dia de vencimento', async () => {
  mockedCreate.mockResolvedValue({ id: 1 });
  const onSaved = jest.fn();
  const onClose = jest.fn();
  await render(<CardFormDialog visible onClose={onClose} onSaved={onSaved} />);

  await fireEvent.changeText(screen.getByLabelText('Nome'), 'Nubank');
  await fireEvent.changeText(screen.getByLabelText('Dia de vencimento'), '45');
  await fireEvent.press(screen.getByText('Salvar'));

  await waitFor(() =>
    expect(mockedCreate).toHaveBeenCalledWith({ name: 'Nubank', due_day: 31 })
  );
  expect(onSaved).toHaveBeenCalledTimes(1);
  expect(onClose).toHaveBeenCalledTimes(1);
});

test('não salva sem nome e mostra o erro no diálogo', async () => {
  await render(<CardFormDialog visible onClose={() => {}} onSaved={() => {}} />);

  await fireEvent.press(screen.getByText('Salvar'));

  expect(mockedCreate).not.toHaveBeenCalled();
  expect(screen.getByText('Informe o nome do cartão')).toBeTruthy();
});

test('edita o cartão existente com os campos preenchidos', async () => {
  mockedUpdate.mockResolvedValue({ id: 7 });
  await render(
    <CardFormDialog
      visible
      card={{ id: 7, name: 'Nubank', due_day: 5, is_active: true }}
      onClose={() => {}}
      onSaved={() => {}}
    />
  );

  expect(screen.getByText('Editar cartão')).toBeTruthy();
  await fireEvent.changeText(screen.getByLabelText('Dia de vencimento'), '0');
  await fireEvent.press(screen.getByText('Salvar'));

  await waitFor(() => expect(mockedUpdate).toHaveBeenCalledWith(7, { name: 'Nubank', due_day: 1 }));
});

test('mostra erro de rede inline quando o salvamento falha', async () => {
  mockedCreate.mockRejectedValue(new Error('Network request failed'));
  await render(<CardFormDialog visible onClose={() => {}} onSaved={() => {}} />);

  await fireEvent.changeText(screen.getByLabelText('Nome'), 'Nubank');
  await fireEvent.press(screen.getByText('Salvar'));

  expect(await screen.findByText('Sem conexão — tente de novo quando voltar.')).toBeTruthy();
});
