import { fireEvent, render, screen } from '@testing-library/react-native';
import { Switch } from '../switch';

test('inverte o valor ao tocar', async () => {
  const onValueChange = jest.fn();
  await render(
    <Switch value={false} onValueChange={onValueChange} accessibilityLabel="Modo On" />
  );
  await fireEvent(screen.getByLabelText('Modo On'), 'valueChange', true);
  expect(onValueChange).toHaveBeenCalledWith(true);
});
