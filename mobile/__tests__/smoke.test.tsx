import { render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';

test('smoke', async () => {
  await render(<Text>Poupix</Text>);
  expect(screen.getByText('Poupix')).toBeTruthy();
});
