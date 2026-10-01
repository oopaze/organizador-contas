jest.mock('expo-clipboard', () => ({
  setStringAsync: jest.fn().mockResolvedValue(true),
}));
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));
jest.mock('../../services/mcp/mcpConnections', () => ({
  listMCPConnections: jest.fn(),
  revokeMCPConnection: jest.fn(),
}));

import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as Clipboard from 'expo-clipboard';
import {
  listMCPConnections,
  revokeMCPConnection,
} from '../../services/mcp/mcpConnections';
import IntegrationsScreen from '../../../app/integrations';

const mockedList = listMCPConnections as jest.MockedFunction<typeof listMCPConnections>;
const mockedRevoke = revokeMCPConnection as jest.MockedFunction<typeof revokeMCPConnection>;

beforeEach(() => {
  jest.clearAllMocks();
});

test('mostra a URL do MCP e copia ao tocar', async () => {
  mockedList.mockResolvedValue([]);

  await render(<IntegrationsScreen />);
  await fireEvent.press(screen.getByText('Copiar'));

  expect(Clipboard.setStringAsync).toHaveBeenCalledWith(
    'https://api.poupix.connectakit.com.br/mcp'
  );
  await waitFor(() => expect(screen.getByText('Copiado!')).toBeTruthy());
});

test('lista as conexões ativas e revoga com confirmação', async () => {
  mockedList.mockResolvedValue([{ client_id: 'client-1', name: 'Claude' }]);
  mockedRevoke.mockResolvedValue(undefined);

  await render(<IntegrationsScreen />);
  expect(await screen.findByText('Claude')).toBeTruthy();
  expect(screen.getByText('client-1')).toBeTruthy();

  await fireEvent.press(screen.getByText('Revogar'));
  expect(screen.getByText('Revogar acesso desse aplicativo?')).toBeTruthy();
  await fireEvent.press(screen.getByText('Confirmar'));

  await waitFor(() => expect(mockedRevoke).toHaveBeenCalledWith('client-1'));
  await waitFor(() => expect(mockedList).toHaveBeenCalledTimes(2));
});

test('mostra o estado vazio quando não há conexões', async () => {
  mockedList.mockResolvedValue([]);

  await render(<IntegrationsScreen />);

  expect(await screen.findByText('Nenhuma conexão ativa ainda.')).toBeTruthy();
});

test('mostra erro inline quando a lista falha', async () => {
  mockedList.mockRejectedValue(new Error());

  await render(<IntegrationsScreen />);

  expect(await screen.findByText('Falha ao carregar conexões')).toBeTruthy();
});
