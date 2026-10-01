import { goalHint } from '../../lib/goals';

// O Intl do Node (ICU 78) usa espaço não separável (U+00A0) depois de "R$" em pt-BR.
const NBSP = '\u00A0';

test('calcula a dica em reais a partir do salário', () => {
  expect(goalHint('30', '1000')).toBe(`= R$${NBSP}300,00`);
});

test('pede salário quando ele não está configurado', () => {
  expect(goalHint('30', '')).toBe('Configure o salário para ver o valor');
});
