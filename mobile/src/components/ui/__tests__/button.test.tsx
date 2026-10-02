import { fireEvent, render, screen } from '@testing-library/react-native';
import { Button } from '../button';

test('dispara onPress quando não está desabilitado', async () => {
  const onPress = jest.fn();
  await render(<Button onPress={onPress}>Salvar</Button>);
  await fireEvent.press(screen.getByText('Salvar'));
  expect(onPress).toHaveBeenCalledTimes(1);
});

test('não dispara onPress quando desabilitado', async () => {
  const onPress = jest.fn();
  await render(
    <Button disabled onPress={onPress}>
      Salvar
    </Button>
  );
  await fireEvent.press(screen.getByText('Salvar'));
  expect(onPress).not.toHaveBeenCalled();
});
