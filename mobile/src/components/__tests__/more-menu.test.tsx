import { fireEvent, render, screen } from '@testing-library/react-native';
import { MoreMenu } from '../more-menu';

test('navega para os destinos ocultos', async () => {
  const onNavigate = jest.fn();
  await render(<MoreMenu onNavigate={onNavigate} onLogout={jest.fn()} />);

  await fireEvent.press(screen.getByText('Conectores'));
  expect(onNavigate).toHaveBeenCalledWith('/integrations');

  await fireEvent.press(screen.getByText('Chat IA'));
  expect(onNavigate).toHaveBeenCalledWith('/chat');

  await fireEvent.press(screen.getByText('Configurações'));
  expect(onNavigate).toHaveBeenCalledWith('/settings');

  // Insights IA continua no web (Task 19 cancelada): não pode aparecer no menu.
  expect(screen.queryByText('Insights IA')).toBeNull();
  expect(onNavigate).not.toHaveBeenCalledWith('/ai-insights');
});

test('aciona a ação Sair', async () => {
  const onLogout = jest.fn();
  await render(<MoreMenu onNavigate={jest.fn()} onLogout={onLogout} />);

  await fireEvent.press(screen.getByText('Sair'));

  expect(onLogout).toHaveBeenCalledTimes(1);
});