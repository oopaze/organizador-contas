import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';
import { Collapsible } from '../collapsible';

test('mostra conteúdo só quando aberto', async () => {
  await render(
    <Collapsible open onOpenChange={() => {}} trigger={<></>}>
      <Text>Pagamentos</Text>
    </Collapsible>
  );
  expect(screen.getByText('Pagamentos')).toBeTruthy();
});

test('não mostra conteúdo quando fechado', async () => {
  await render(
    <Collapsible open={false} onOpenChange={() => {}} trigger={<></>}>
      <Text>Pagamentos</Text>
    </Collapsible>
  );
  expect(screen.queryByText('Pagamentos')).toBeNull();
});

test('cabeça alterna o estado controlado', async () => {
  const onOpenChange = jest.fn();
  await render(
    <Collapsible open={false} onOpenChange={onOpenChange} trigger={<Text>Extrato</Text>}>
      <Text>Pagamentos</Text>
    </Collapsible>
  );
  await fireEvent.press(screen.getByText('Extrato'));
  expect(onOpenChange).toHaveBeenCalledWith(true);
});
