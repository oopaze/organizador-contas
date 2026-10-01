import { fireEvent, render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../tabs';

function Example({ value, onValueChange = () => {} }: { value: string; onValueChange?: (value: string) => void }) {
  return (
    <Tabs value={value} onValueChange={onValueChange}>
      <TabsList>
        <TabsTrigger value="all">Todas</TabsTrigger>
        <TabsTrigger value="ledger">Extrato</TabsTrigger>
      </TabsList>
      <TabsContent value="all">
        <Text>Conteúdo todas</Text>
      </TabsContent>
      <TabsContent value="ledger">
        <Text>Conteúdo extrato</Text>
      </TabsContent>
    </Tabs>
  );
}

test('mostra só o conteúdo da aba ativa', async () => {
  await render(<Example value="all" />);
  expect(screen.getByText('Conteúdo todas')).toBeTruthy();
  expect(screen.queryByText('Conteúdo extrato')).toBeNull();
});

test('emite a aba escolhida ao tocar na cabeça', async () => {
  const onValueChange = jest.fn();
  await render(<Example value="all" onValueChange={onValueChange} />);
  await fireEvent.press(screen.getByText('Extrato'));
  expect(onValueChange).toHaveBeenCalledWith('ledger');
});
