import { render, screen } from '@testing-library/react-native';
import { StatCard } from '../stat-card';

test('mostra título, valor e subtítulo', async () => {
  await render(<StatCard title="Saldo" value="R$ 1.234,56" subtitle="outubro" />);
  expect(screen.getByText('Saldo')).toBeTruthy();
  expect(screen.getByText('R$ 1.234,56')).toBeTruthy();
  expect(screen.getByText('outubro')).toBeTruthy();
});
