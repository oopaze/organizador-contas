import { toDecimalString } from '../amount';

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
