import { render, screen } from '@testing-library/react-native';
import { EmptyState } from '../empty-state';

test('renderiza título e descrição', async () => {
  await render(<EmptyState title="Nada por aqui" description="Sem lançamentos neste mês" />);
  expect(screen.getByText('Nada por aqui')).toBeTruthy();
  expect(screen.getByText('Sem lançamentos neste mês')).toBeTruthy();
});
