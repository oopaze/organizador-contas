import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Progress } from '@/app/components/ui/progress';
import type { LedgerResult, ProjectionGoals } from '@/services';

const ESSENTIAL_PREFIXES = ['housing', 'bill', 'transport', 'health', 'education'];

const formatMoney = (value: number) =>
  `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

interface GoalBarProps {
  label: string;
  current: number;
  goal: number;
  colorClass: string;
  direction: 'max' | 'min';
}

const GoalBar: React.FC<GoalBarProps> = ({ label, current, goal, colorClass, direction }) => {
  const percent = goal > 0 ? Math.min(100, (current / goal) * 100) : 0;
  const offTrack = goal > 0 && (direction === 'max' ? current > goal : current < goal);
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className={`text-sm ${offTrack ? 'font-semibold text-red-600' : 'text-muted-foreground'}`}>
          {formatMoney(current)} / {formatMoney(goal)}
          {offTrack && (direction === 'max' ? ' (acima da meta)' : ' (abaixo da meta)')}
        </span>
      </div>
      <Progress value={percent} className={`h-2 ${colorClass}`} />
    </div>
  );
};

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
  const saved = periodIncome - totalSpending;

  const spendingPercent = parseFloat(goals?.spending_goal_percent || '0');
  const savingsPercent = parseFloat(goals?.savings_goal_percent || '0');
  const essentialsPercent = parseFloat(goals?.essentials_goal_percent || '0');

  if (!spendingPercent && !savingsPercent && !essentialsPercent) {
    return null;
  }

  if (periodIncome <= 0) {
    return null;
  }

  const target = (percent: number) => (periodIncome * percent) / 100;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          Metas do período{periodMonths > 1 ? ` (${periodMonths} meses)` : ''}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {spendingPercent > 0 && (
          <GoalBar
            label={`Gasto (teto ${spendingPercent}%)`}
            current={totalSpending}
            goal={target(spendingPercent)}
            colorClass="bg-red-500"
            direction="max"
          />
        )}
        {savingsPercent > 0 && (
          <GoalBar
            label={`Guardado (meta ${savingsPercent}%)`}
            current={saved}
            goal={target(savingsPercent)}
            colorClass="bg-emerald-500"
            direction="min"
          />
        )}
        {essentialsPercent > 0 && (
          <GoalBar
            label={`Essenciais (teto ${essentialsPercent}%)`}
            current={essentialSpending}
            goal={target(essentialsPercent)}
            colorClass="bg-blue-500"
            direction="max"
          />
        )}
      </CardContent>
    </Card>
  );
};
