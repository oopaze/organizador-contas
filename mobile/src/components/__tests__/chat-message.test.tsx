import { render, screen } from '@testing-library/react-native';
import { ChatMessage } from '../chat-message';

test('renderiza mensagem do usuário', async () => {
  await render(<ChatMessage role="user" content="Quanto gastei em outubro?" />);

  expect(screen.getByText('Quanto gastei em outubro?')).toBeTruthy();
});

test('renderiza markdown na mensagem do assistente', async () => {
  await render(<ChatMessage role="assistant" content="Gaste **R$ 100** no mês" />);

  expect(screen.getByText(/R\$ 100/)).toBeTruthy();
});
