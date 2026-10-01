import { render, screen } from '@testing-library/react-native';
import { Card, CardContent, CardTitle } from '../card';

test('renderiza título e conteúdo', async () => {
  await render(
    <Card>
      <CardTitle>Saldo</CardTitle>
      <CardContent>R$ 1.000,00</CardContent>
    </Card>
  );
  expect(screen.getByText('Saldo')).toBeTruthy();
  expect(screen.getByText('R$ 1.000,00')).toBeTruthy();
});
