import { fireEvent, render, screen } from '@testing-library/react-native';
import { Input } from '../input';

test('mostra label e emite o texto digitado', async () => {
  const onChangeText = jest.fn();
  await render(<Input label="Valor" onChangeText={onChangeText} />);
  await fireEvent.changeText(screen.getByLabelText('Valor'), '54,90');
  expect(onChangeText).toHaveBeenCalledWith('54,90');
});
