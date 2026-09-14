import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import type { LedgerResult, ProjectionGoals } from '@/services';

const ESSENTIAL_PREFIXES = ['housing', 'bill', 'transport', 'health', 'education'];

const formatMoney = (value: number) =>
  `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const GoalRow: React.FC<{
  label: string;
  current: number;
  target: number;
  goalLabel: string;
  over: boolean;
}> = ({ label, current, target, goalLabel, over }) => (
  <div className="flex items-start justify-between gap-3">
    <div>
      <span className="text-sm font-medium">{label}</span>
      <p className="text-xs text-muted-foreground">
        {goalLabel} = {formatMoney(target)}
      </p>
    </div>
    <div className="text-right">
      <span className={`text-sm font-semibold ${over ? 'text-red-600' : 'text-gray-900'}`}>
        {formatMoney(current)}
      </span>
      <p className={`text-xs ${over ? 'text-red-600' : 'text-muted-foreground'}`}>
        {over ? 'acima da meta' : `restam ${formatMoney(target - current)}`}
      </p>
    </div>
  </div>
);

export const GoalsProgressCard: React.FC<{
  goals: ProjectionGoals;
  ledger: LedgerResult;
  salary: number;
  months: number;
}> = ({ goals, ledger, salary, months }) => {
  const periodMonths = Math.max(1, months);
  const periodIncome = salary * periodMonths;

  const entries = (ledger?.entries || []).filter((entry) => entry.direction === 'outgoing');
  const totalSpending = entries.reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0);
  const essentialSpending = entries
    .filter((entry) => ESSENTIAL_PREFIXES.some((prefix) => (entry.category || '').startsWith(prefix)))
    .reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0);

  const spendingPercent = parseFloat(goals?.spending_goal_percent || '0');
  const savingsPercent = parseFloat(goals?.savings_goal_percent || '0');
  const essentialsPercent = parseFloat(goals?.essentials_goal_percent || '0');

  if ((!spendingPercent && !savingsPercent && !essentialsPercent) || periodIncome <= 0) {
    return null;
  }

  const leftover = periodIncome - totalSpending;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          Metas do período{periodMonths > 1 ? ` (${periodMonths} meses)` : ''}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {spendingPercent > 0 && (
          <GoalRow
            label="Gasto"
            current={totalSpending}
            target={(periodIncome * spendingPercent) / 100}
            goalLabel={`meta ${spendingPercent}%`}
            over={totalSpending > (periodIncome * spendingPercent) / 100}
          />
        )}
        {essentialsPercent > 0 && (
          <GoalRow
            label="Essenciais"
            current={essentialSpending}
            target={(periodIncome * essentialsPercent) / 100}
            goalLabel={`meta ${essentialsPercent}%`}
            over={essentialSpending > (periodIncome * essentialsPercent) / 100}
          />
        )}
        {savingsPercent > 0 && (
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm font-medium">Guardar</span>
            <span className="text-xs text-muted-foreground">
              meta {savingsPercent}% = {formatMoney((periodIncome * savingsPercent) / 100)}
            </span>
          </div>
        )}
        <div className="flex items-center justify-between border-t pt-3">
          <span className="text-sm font-medium">Sobra do período</span>
          <span className={`text-sm font-semibold ${leftover < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
            {formatMoney(leftover)}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
