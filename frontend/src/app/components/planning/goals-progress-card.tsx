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
}

const GoalBar: React.FC<GoalBarProps> = ({ label, current, goal, colorClass }) => {
  const percent = goal > 0 ? Math.min(100, (current / goal) * 100) : 0;
  const over = goal > 0 && current > goal;
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className={`text-sm ${over ? 'font-semibold text-red-600' : 'text-muted-foreground'}`}>
          {formatMoney(current)} / {formatMoney(goal)}
          {over && ' (acima da meta)'}
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
  const entries = (ledger?.entries || []).filter((entry) => entry.direction === 'outgoing');
  const totalSpending =
    entries.reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0) / periodMonths;
  const essentialSpending =
    entries
      .filter((entry) => ESSENTIAL_PREFIXES.some((prefix) => (entry.category || '').startsWith(prefix)))
      .reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0) / periodMonths;
  const saved = salary - totalSpending;

  const spendingGoal = parseFloat(goals?.monthly_spending_goal || '0');
  const savingsGoal = parseFloat(goals?.monthly_savings_goal || '0');
  const essentialsGoal = parseFloat(goals?.monthly_essentials_goal || '0');

  if (!spendingGoal && !savingsGoal && !essentialsGoal) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Metas do mês</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {spendingGoal > 0 && (
          <GoalBar
            label="Gasto do mês"
            current={totalSpending}
            goal={spendingGoal}
            colorClass="bg-red-500"
          />
        )}
        {savingsGoal > 0 && (
          <GoalBar
            label="Guardado"
            current={saved}
            goal={savingsGoal}
            colorClass="bg-emerald-500"
          />
        )}
        {essentialsGoal > 0 && (
          <GoalBar
            label="Essenciais"
            current={essentialSpending}
            goal={essentialsGoal}
            colorClass="bg-blue-500"
          />
        )}
      </CardContent>
    </Card>
  );
};
