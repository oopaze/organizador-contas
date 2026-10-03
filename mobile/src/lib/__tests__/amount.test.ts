import { amountToText, toDecimalString } from '../amount';

test('converte vírgula para ponto', () => {
  expect(toDecimalString('54,90')).toBe('54.90');
  expect(toDecimalString(' 89 ')).toBe('89');
});

test('mantém decimal com ponto', () => {
  expect(toDecimalString('18.50')).toBe('18.50');
});

test('recusa texto que não é número', () => {
  expect(toDecimalString('')).toBeNull();
  expect(toDecimalString('abc')).toBeNull();
  expect(toDecimalString('1,2,3')).toBeNull();
  expect(toDecimalString('1.234,5')).toBeNull();
});

test('normaliza o valor da API (number) para o texto do input', () => {
  expect(amountToText(89.9)).toBe('89.9');
  expect(amountToText('89.90')).toBe('89.90');
  expect(amountToText(0)).toBe('0');
  expect(amountToText(null)).toBe('');
  expect(amountToText(undefined)).toBe('');
});
