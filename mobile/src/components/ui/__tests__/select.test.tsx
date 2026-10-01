import { fireEvent, render, screen } from '@testing-library/react-native';
import { Select } from '../select';

test('mostra o label selecionado e emite a escolha', async () => {
  const onValueChange = jest.fn();
  await render(
    <Select
      value="cash"
      onValueChange={onValueChange}
      options={[
        { value: 'cash', label: 'Dinheiro' },
        { value: 'credit', label: 'Cartão' },
      ]}
    />
  );
  expect(screen.getByText('Dinheiro')).toBeTruthy();
  await fireEvent.press(screen.getByText('Dinheiro'));
  await fireEvent.press(screen.getByText('Cartão'));
  expect(onValueChange).toHaveBeenCalledWith('credit');
});

test('mostra o placeholder quando não há valor', async () => {
  await render(
    <Select
      value={undefined}
      onValueChange={() => {}}
      options={[{ value: 'cash', label: 'Dinheiro' }]}
      placeholder="Selecione a categoria"
    />
  );
  expect(screen.getByText('Selecione a categoria')).toBeTruthy();
});
