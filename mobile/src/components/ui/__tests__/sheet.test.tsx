import { BackHandler } from 'react-native';
import { render } from '@testing-library/react-native';
import { Sheet } from '../sheet';

test('fecha no botão voltar do Android quando visível', async () => {
  const onClose = jest.fn();
  const spy = jest.spyOn(BackHandler, 'addEventListener');

  await render(<Sheet visible onClose={onClose} title="Conversas" />);

  expect(spy).toHaveBeenCalled();
  const handler = spy.mock.calls[spy.mock.calls.length - 1][1] as unknown as () => boolean;
  expect(handler()).toBe(true);
  expect(onClose).toHaveBeenCalled();

  spy.mockRestore();
});

test('não registra handler de voltar quando fechado', async () => {
  const spy = jest.spyOn(BackHandler, 'addEventListener');

  await render(<Sheet visible={false} onClose={() => {}} title="Conversas" />);

  expect(spy).not.toHaveBeenCalled();

  spy.mockRestore();
});
