import { fireEvent, render, screen } from '@testing-library/react-native';
import { AlertDialog } from '../alert-dialog';

test('confirma e cancela pelos botões', async () => {
  const onConfirm = jest.fn();
  const onCancel = jest.fn();
  await render(
    <AlertDialog
      visible
      onConfirm={onConfirm}
      onCancel={onCancel}
      title="Apagar transação"
      description="Essa ação não pode ser desfeita."
      destructive
    />
  );
  expect(screen.getByText('Apagar transação')).toBeTruthy();
  expect(screen.getByText('Essa ação não pode ser desfeita.')).toBeTruthy();

  await fireEvent.press(screen.getByText('Confirmar'));
  expect(onConfirm).toHaveBeenCalledTimes(1);

  await fireEvent.press(screen.getByText('Cancelar'));
  expect(onCancel).toHaveBeenCalledTimes(1);
});

test('respeita labels customizados', async () => {
  await render(
    <AlertDialog
      visible
      onConfirm={() => {}}
      onCancel={() => {}}
      title="Apagar"
      confirmLabel="Apagar agora"
      cancelLabel="Voltar"
    />
  );
  expect(screen.getByText('Apagar agora')).toBeTruthy();
  expect(screen.getByText('Voltar')).toBeTruthy();
});
