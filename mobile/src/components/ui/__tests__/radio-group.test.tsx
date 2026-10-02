import { fireEvent, render, screen } from '@testing-library/react-native';
import { RadioGroup, RadioGroupItem } from '../radio-group';

test('emite o valor da opção escolhida', async () => {
  const onValueChange = jest.fn();
  await render(
    <RadioGroup value="cash" onValueChange={onValueChange}>
      <RadioGroupItem value="cash" accessibilityLabel="Dinheiro" />
      <RadioGroupItem value="credit" accessibilityLabel="Cartão" />
    </RadioGroup>
  );
  await fireEvent.press(screen.getByLabelText('Cartão'));
  expect(onValueChange).toHaveBeenCalledWith('credit');
});
