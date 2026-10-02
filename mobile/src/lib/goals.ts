import { formatCurrency } from './format';

/**
 * Dica em reais da meta percentual a partir do salário configurado.
 * Sem percentual não há o que calcular; sem salário, pede para configurá-lo.
 */
export function goalHint(percentInput: string, salaryInput: string): string {
  const percent = parseFloat(percentInput);
  if (!percent) return '';
  const salary = parseFloat(salaryInput);
  if (!salary) return 'Configure o salário para ver o valor';
  return `= ${formatCurrency((salary * percent) / 100)}`;
}
