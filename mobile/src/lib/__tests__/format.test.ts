import { formatCurrency, formatPercent } from '../format';

// O Intl do Node (ICU 78) usa espaço não separável (U+00A0) depois de "R$" em pt-BR.
const NBSP = '\u00A0';

test('formata valores string em pt-BR', () => {
  expect(formatCurrency('1234.56')).toBe(`R$${NBSP}1.234,56`);
  expect(formatCurrency('89.9')).toBe(`R$${NBSP}89,90`);
  expect(formatCurrency(0)).toBe(`R$${NBSP}0,00`);
});

test('formata valores negativos com sinal', () => {
  expect(formatCurrency('-89.9')).toBe(`-R$${NBSP}89,90`);
});

test('formata percentual em pt-BR', () => {
  expect(formatPercent(12.34)).toBe('12,3%');
});
