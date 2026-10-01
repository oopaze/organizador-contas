import { fireEvent, render, screen } from '@testing-library/react-native';
import { Checkbox } from '../checkbox';

test('inverte o valor ao tocar', async () => {
  const onCheckedChange = jest.fn();
  await render(
    <Checkbox checked={false} onCheckedChange={onCheckedChange} accessibilityLabel="Pago" />
  );
  await fireEvent.press(screen.getByLabelText('Pago'));
  expect(onCheckedChange).toHaveBeenCalledWith(true);
});
