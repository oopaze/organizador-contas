import { formatHHmm, formatMonthYear, parseIsoDate, toIsoDate } from '../date';

test('parseIsoDate não desloca o dia na virada de mês', () => {
  const date = parseIsoDate('2026-10-01');
  expect(date.getDate()).toBe(1);
  expect(date.getMonth()).toBe(9);
  expect(date.getFullYear()).toBe(2026);
});

test('toIsoDate devolve data local sem UTC', () => {
  expect(toIsoDate(new Date(2026, 9, 1, 23, 30))).toBe('2026-10-01');
});

test('formatHHmm devolve a hora local com dois dígitos', () => {
  expect(formatHHmm(new Date(2026, 9, 1, 14, 5))).toBe('14:05');
});

test('formatMonthYear escreve mês e ano em pt-BR', () => {
  expect(formatMonthYear(new Date(2026, 9, 1))).toBe('outubro de 2026');
});
