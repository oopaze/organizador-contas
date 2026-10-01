import { fireEvent, render, screen } from '@testing-library/react-native';
import { Sheet } from '../sheet';

test('renderiza conteúdo quando visível e fecha no requestClose do Android', async () => {
  const onClose = jest.fn();
  await render(
    <Sheet visible onClose={onClose} title="Conversas">
      <></>
    </Sheet>
  );

  expect(screen.getByText('Conversas')).toBeTruthy();

  fireEvent(screen.getByTestId('sheet-modal'), 'requestClose');
  expect(onClose).toHaveBeenCalled();
});

test('não renderiza conteúdo quando fechado', async () => {
  await render(
    <Sheet visible={false} onClose={() => {}} title="Conversas">
      <></>
    </Sheet>
  );

  expect(screen.queryByText('Conversas')).toBeNull();
});
