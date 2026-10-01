import { fireEvent, render, screen } from '@testing-library/react-native';
import { Button } from '../button';
import { Dialog } from '../dialog';

test('mostra conteúdo quando visível e fecha no botão', async () => {
  const onClose = jest.fn();
  await render(
    <Dialog visible onClose={onClose} title="Nova transação">
      <Button onPress={onClose}>Fechar</Button>
    </Dialog>
  );
  expect(screen.getByText('Nova transação')).toBeTruthy();
  await fireEvent.press(screen.getByText('Fechar'));
  expect(onClose).toHaveBeenCalled();
});

test('mostra descrição e rodapé quando visíveis', async () => {
  await render(
    <Dialog
      visible
      onClose={() => {}}
      title="Apagar"
      description="Essa ação não pode ser desfeita."
      footer={<Button>Confirmar</Button>}
    />
  );
  expect(screen.getByText('Essa ação não pode ser desfeita.')).toBeTruthy();
  expect(screen.getByText('Confirmar')).toBeTruthy();
});

test('não renderiza quando invisível', async () => {
  await render(<Dialog visible={false} onClose={() => {}} title="Nova transação" />);
  expect(screen.queryByText('Nova transação')).toBeNull();
});
