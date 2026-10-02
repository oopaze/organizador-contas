import { render, screen } from '@testing-library/react-native';
import { OfflineBanner } from '../offline-banner';

test('sem cache salvo, avisa que não há dados', async () => {
  await render(<OfflineBanner persistedAt={null} />);
  expect(screen.getByText('Sem conexão — sem dados salvos ainda')).toBeTruthy();
});

test('com cache salvo, mostra o horário dos dados', async () => {
  const timestamp = new Date(2026, 9, 1, 14, 5).getTime();
  await render(<OfflineBanner persistedAt={timestamp} />);
  expect(screen.getByText('Sem conexão — dados de 14:05')).toBeTruthy();
});
