import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';
import { Button } from '../button';
import { Popover } from '../popover';

test('abre pelo trigger e fecha no toque de fora', async () => {
  await render(
    <Popover trigger={<Button>Outubro</Button>}>
      <Text>Seletor de mês</Text>
    </Popover>
  );
  expect(screen.queryByText('Seletor de mês')).toBeNull();

  await fireEvent.press(screen.getByText('Outubro'));
  expect(screen.getByText('Seletor de mês')).toBeTruthy();

  await fireEvent.press(screen.getByLabelText('Fechar'));
  expect(screen.queryByText('Seletor de mês')).toBeNull();
});
