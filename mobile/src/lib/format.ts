export function formatCurrency(value: string | number): string {
  const numeric = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(numeric)) return 'R$ 0,00';
  return numeric.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

export function formatPercent(value: number): string {
  return `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`;
}
