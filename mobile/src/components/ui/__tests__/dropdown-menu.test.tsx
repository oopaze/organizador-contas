import { fireEvent, render, screen } from '@testing-library/react-native';
import { Button } from '../button';
import { DropdownMenu } from '../dropdown-menu';

test('abre pelo trigger e dispara o item escolhido', async () => {
  const onPress = jest.fn();
  await render(
    <DropdownMenu
      trigger={<Button>Opções</Button>}
      items={[
        { label: 'Pagar', onPress },
        { label: 'Apagar', onPress: jest.fn(), destructive: true },
      ]}
    />
  );
  expect(screen.queryByText('Pagar')).toBeNull();
  await fireEvent.press(screen.getByText('Opções'));
  expect(screen.getByText('Pagar')).toBeTruthy();
  await fireEvent.press(screen.getByText('Pagar'));
  expect(onPress).toHaveBeenCalledTimes(1);
  expect(screen.queryByText('Pagar')).toBeNull();
});
