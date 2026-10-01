import { fireEvent, render, screen } from '@testing-library/react-native';
import { MoreMenu } from '../more-menu';

test('navega para os destinos ocultos', async () => {
  const onNavigate = jest.fn();
  await render(<MoreMenu onNavigate={onNavigate} onLogout={jest.fn()} />);

  await fireEvent.press(screen.getByText('Conectores'));
  expect(onNavigate).toHaveBeenCalledWith('/integrations');

  await fireEvent.press(screen.getByText('Chat IA'));
  expect(onNavigate).toHaveBeenCalledWith('/chat');

  await fireEvent.press(screen.getByText('Insights IA'));
  expect(onNavigate).toHaveBeenCalledWith('/ai-insights');

  await fireEvent.press(screen.getByText('Configurações'));
  expect(onNavigate).toHaveBeenCalledWith('/settings');
});

test('aciona a ação Sair', async () => {
  const onLogout = jest.fn();
  await render(<MoreMenu onNavigate={jest.fn()} onLogout={onLogout} />);

  await fireEvent.press(screen.getByText('Sair'));

  expect(onLogout).toHaveBeenCalledTimes(1);
});