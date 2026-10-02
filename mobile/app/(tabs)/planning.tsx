import { useCallback, useEffect, useMemo, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import ChevronLeft from 'lucide-react-native/icons/chevron-left';
import ChevronRight from 'lucide-react-native/icons/chevron-right';
import Plus from 'lucide-react-native/icons/plus';
import Target from 'lucide-react-native/icons/target';
import { SafeAreaView } from 'react-native-safe-area-context';
import { EmptyState } from '../../src/components/empty-state';
import { IntentionDialog } from '../../src/components/intention-dialog';
import { IntentionList } from '../../src/components/intention-list';
import { StatCard } from '../../src/components/stat-card';
import { Button } from '../../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../src/components/ui/card';
import { Sheet } from '../../src/components/ui/sheet';
import { Skeleton } from '../../src/components/ui/skeleton';
import { cn } from '../../src/components/ui/utils';
import { getCategoryLabel } from '../../src/lib/category-colors';
import { formatCurrency, formatPercent } from '../../src/lib/format';
import { invalidateFinancialData } from '../../src/lib/invalidate-financial-data';
import { useOnlineStatus } from '../../src/lib/use-online-status';
import {
  ensureCardBills,
  ensureSalary,
  getIntentions,
  getLedger,
  getProjection,
  type LedgerResult,
  type ProjectionGoals,
  type PurchaseIntention,
} from '../../src/services';

const MONTH_LABELS = [
  'Jan',
  'Fev',
  'Mar',
  'Abr',
  'Mai',
  'Jun',
  'Jul',
  'Ago',
  'Set',
  'Out',
  'Nov',
  'Dez',
];

const PIE_COLORS = [
  '#ef4444',
  '#3b82f6',
  '#8b5cf6',
  '#10b981',
  '#ec4899',
  '#f97316',
  '#06b6d4',
  '#84cc16',
];

const ESSENTIAL_PREFIXES = ['housing', 'bill', 'transport', 'health', 'education'];

function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function addMonths(monthValue: string, offset: number): string {
  const [year, month] = monthValue.split('-').map(Number);
  const date = new Date(year, month - 1 + offset, 1);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
}

function lastDayOf(month: string): number {
  const [year, monthNumber] = month.split('-').map(Number);
  return new Date(year, monthNumber, 0).getDate();
}

function shortMonth(monthValue: string): string {
  const [year, month] = monthValue.split('-').map(Number);
  return `${String(month).padStart(2, '0')}/${String(year).slice(2)}`;
}

interface RangeMonthPickerProps {
  start: string;
  end: string;
  onChangeStart: (value: string) => void;
  onChangeEnd: (value: string) => void;
}

/** O popover de dois meses do web vira um sheet com ano + grade de meses por limite. */
function RangeMonthPicker({ start, end, onChangeStart, onChangeEnd }: RangeMonthPickerProps) {
  const [open, setOpen] = useState(false);
  const [target, setTarget] = useState<'start' | 'end'>('start');
  const current = target === 'start' ? start : end;
  const [year, month] = current.split('-').map(Number);
  const [viewYear, setViewYear] = useState(year);

  const openSheet = () => {
    setTarget('start');
    setViewYear(Number(start.slice(0, 4)));
    setOpen(true);
  };

  const switchTarget = (next: 'start' | 'end') => {
    setTarget(next);
    setViewYear(Number((next === 'start' ? start : end).slice(0, 4)));
  };

  const pick = (index: number) => {
    const picked = `${viewYear}-${String(index + 1).padStart(2, '0')}`;
    if (target === 'start') {
      onChangeStart(picked);
    } else {
      onChangeEnd(picked);
    }
  };

  const shiftRange = (offset: number) => {
    onChangeStart(addMonths(start, offset));
    onChangeEnd(addMonths(end, offset));
  };

  return (
    <>
      <View className="flex-row items-center justify-center gap-2">
        <Button
          variant="outline"
          size="icon"
          accessibilityLabel="Período anterior"
          onPress={() => shiftRange(-1)}
        >
          <ChevronLeft size={16} color="#18181b" />
        </Button>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Selecionar período"
          onPress={openSheet}
          className="min-w-[170px] items-center rounded-md px-3 py-2 active:bg-zinc-100"
        >
          <Text className="text-base font-semibold text-zinc-900">
            {shortMonth(start)} → {shortMonth(end)}
          </Text>
        </Pressable>
        <Button
          variant="outline"
          size="icon"
          accessibilityLabel="Próximo período"
          onPress={() => shiftRange(1)}
        >
          <ChevronRight size={16} color="#18181b" />
        </Button>
      </View>

      <Sheet visible={open} onClose={() => setOpen(false)} title="Selecionar período">
        <View className="px-4">
          <View className="mb-4 flex-row gap-2">
            <Button
              size="sm"
              variant={target === 'start' ? 'default' : 'outline'}
              className="flex-1"
              onPress={() => switchTarget('start')}
            >
              Mês inicial
            </Button>
            <Button
              size="sm"
              variant={target === 'end' ? 'default' : 'outline'}
              className="flex-1"
              onPress={() => switchTarget('end')}
            >
              Mês final
            </Button>
          </View>

          <Text className="mb-3 text-center text-sm text-zinc-500">
            {shortMonth(start)} → {shortMonth(end)}
          </Text>

          <View className="mb-3 flex-row items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              accessibilityLabel="Ano anterior"
              onPress={() => setViewYear((value) => value - 1)}
            >
              <ChevronLeft size={16} color="#18181b" />
            </Button>
            <Text className="text-base font-semibold text-zinc-900">{viewYear}</Text>
            <Button
              variant="ghost"
              size="icon"
              accessibilityLabel="Próximo ano"
              onPress={() => setViewYear((value) => value + 1)}
            >
              <ChevronRight size={16} color="#18181b" />
            </Button>
          </View>

          <View className="flex-row flex-wrap">
            {MONTH_LABELS.map((label, index) => {
              const selected = viewYear === year && index + 1 === month;
              return (
                <Pressable
                  key={label}
                  accessibilityRole="button"
                  accessibilityLabel={`${label} ${viewYear}`}
                  accessibilityState={{ selected }}
                  onPress={() => pick(index)}
                  className={cn(
                    'w-1/3 items-center rounded-md py-3',
                    selected ? 'bg-emerald-600' : 'active:bg-zinc-100'
                  )}
                >
                  <Text
                    className={cn(
                      'text-sm',
                      selected ? 'font-medium text-white' : 'text-zinc-700'
                    )}
                  >
                    {label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
      </Sheet>
    </>
  );
}

interface GoalRowProps {
  label: string;
  current: number;
  target: number;
  goalLabel: string;
  over: boolean;
}

function GoalRow({ label, current, target, goalLabel, over }: GoalRowProps) {
  return (
    <View className="flex-row items-start justify-between gap-3">
      <View className="flex-1">
        <Text className="text-sm font-medium text-zinc-900">{label}</Text>
        <Text className="text-xs text-zinc-500">
          {goalLabel} = {formatCurrency(target)}
        </Text>
      </View>
      <View className="items-end">
        <Text className={cn('text-sm font-semibold', over ? 'text-red-600' : 'text-zinc-900')}>
          {formatCurrency(current)}
        </Text>
        <Text className={cn('text-xs', over ? 'text-red-600' : 'text-zinc-500')}>
          {over ? 'acima da meta' : `restam ${formatCurrency(target - current)}`}
        </Text>
      </View>
    </View>
  );
}

interface GoalsCardProps {
  goals: ProjectionGoals;
  ledger: LedgerResult;
  salary: number;
  months: number;
}

function GoalsCard({ goals, ledger, salary, months }: GoalsCardProps) {
  const periodMonths = Math.max(1, months);
  const periodIncome = salary * periodMonths;

  const entries = (ledger.entries || []).filter((entry) => entry.direction === 'outgoing');
  const totalSpending = entries.reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0);
  const essentialSpending = entries
    .filter((entry) =>
      ESSENTIAL_PREFIXES.some((prefix) => (entry.category || '').startsWith(prefix))
    )
    .reduce((sum, entry) => sum + parseFloat(entry.amount || '0'), 0);

  const spendingPercent = parseFloat(goals.spending_goal_percent || '0');
  const savingsPercent = parseFloat(goals.savings_goal_percent || '0');
  const essentialsPercent = parseFloat(goals.essentials_goal_percent || '0');

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
      <CardContent className="gap-3">
        {spendingPercent > 0 ? (
          <GoalRow
            label="Gasto"
            current={totalSpending}
            target={(periodIncome * spendingPercent) / 100}
            goalLabel={`meta ${spendingPercent}%`}
            over={totalSpending > (periodIncome * spendingPercent) / 100}
          />
        ) : null}
        {essentialsPercent > 0 ? (
          <GoalRow
            label="Essenciais"
            current={essentialSpending}
            target={(periodIncome * essentialsPercent) / 100}
            goalLabel={`meta ${essentialsPercent}%`}
            over={essentialSpending > (periodIncome * essentialsPercent) / 100}
          />
        ) : null}
        {savingsPercent > 0 ? (
          <View className="flex-row items-center justify-between gap-3">
            <Text className="text-sm font-medium text-zinc-900">Guardar</Text>
            <Text className="text-xs text-zinc-500">
              meta {savingsPercent}% = {formatCurrency((periodIncome * savingsPercent) / 100)}
            </Text>
          </View>
        ) : null}
        <View className="flex-row items-center justify-between border-t border-zinc-100 pt-3">
          <Text className="text-sm font-medium text-zinc-900">Sobra do período</Text>
          <Text
            className={cn('text-sm font-semibold', leftover < 0 ? 'text-red-600' : 'text-emerald-600')}
          >
            {formatCurrency(leftover)}
          </Text>
        </View>
      </CardContent>
    </Card>
  );
}

export default function PlanningScreen() {
  const queryClient = useQueryClient();
  const isOnline = useOnlineStatus();

  const [startMonth, setStartMonth] = useState(currentMonth);
  const [endMonth, setEndMonth] = useState(() => addMonths(currentMonth(), 11));
  const [refreshing, setRefreshing] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [editingIntention, setEditingIntention] = useState<PurchaseIntention | null>(null);

  const rangeFilters = useMemo(
    () => ({ start: startMonth, end: endMonth }),
    [startMonth, endMonth]
  );
  const ledgerFilters = useMemo(
    () => ({
      start: `${startMonth}-01`,
      end: `${endMonth}-${String(lastDayOf(endMonth)).padStart(2, '0')}`,
    }),
    [startMonth, endMonth]
  );

  const intentionsQuery = useQuery({
    queryKey: ['intentions', rangeFilters],
    queryFn: () => getIntentions(rangeFilters),
  });

  const projectionQuery = useQuery({
    queryKey: ['projection', rangeFilters],
    queryFn: () => getProjection(rangeFilters),
  });

  const ledgerQuery = useQuery({
    queryKey: ['ledger', ledgerFilters],
    queryFn: () => getLedger(ledgerFilters),
  });

  const refetchAll = useCallback(
    () =>
      Promise.all([
        queryClient.refetchQueries({ queryKey: ['intentions', rangeFilters], exact: true }),
        queryClient.refetchQueries({ queryKey: ['projection', rangeFilters], exact: true }),
        queryClient.refetchQueries({ queryKey: ['ledger', ledgerFilters], exact: true }),
      ]),
    [queryClient, rangeFilters, ledgerFilters]
  );

  /** Escritas de intenção invalidam intenções/projeção/ledger e releem a tela. */
  const handleChanged = useCallback(() => {
    void queryClient.invalidateQueries({ queryKey: ['intentions'] });
    void queryClient.invalidateQueries({ queryKey: ['projection'] });
    void invalidateFinancialData(queryClient);
    void refetchAll();
  }, [queryClient, refetchAll]);

  // ensureSalary/ensureCardBills são best-effort: nunca bloqueiam a leitura
  // nem mostram erro de tela; só invalidam as queries quando dão certo.
  useEffect(() => {
    let cancelled = false;

    const runEnsure = async () => {
      try {
        const results = await Promise.allSettled([
          ensureSalary(startMonth),
          ensureCardBills(startMonth),
        ]);
        if (cancelled || !results.some((result) => result.status === 'fulfilled')) return;
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['intentions'] }),
          queryClient.invalidateQueries({ queryKey: ['projection'] }),
          queryClient.invalidateQueries({ queryKey: ['ledger'] }),
        ]);
      } catch {
        // best-effort silencioso
      }
    };

    void runEnsure();
    return () => {
      cancelled = true;
    };
  }, [startMonth, endMonth, queryClient]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await Promise.allSettled([ensureSalary(startMonth), ensureCardBills(startMonth)]);
      await refetchAll();
    } catch {
      // erros de leitura viram estado/banner; o refresh só encerra o indicador
    } finally {
      setRefreshing(false);
    }
  }, [startMonth, refetchAll]);

  const changeStart = (value: string) => {
    if (!value) return;
    setStartMonth(value);
    if (value > endMonth) setEndMonth(value);
  };

  const changeEnd = (value: string) => {
    if (!value) return;
    setEndMonth(value < startMonth ? startMonth : value);
  };

  const openCreate = () => {
    setEditingIntention(null);
    setFormOpen(true);
  };

  const openEdit = (intention: PurchaseIntention) => {
    setEditingIntention(intention);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingIntention(null);
  };

  const intentions = intentionsQuery.data ?? [];
  const ledger = ledgerQuery.data;
  const projection = projectionQuery.data;

  const loading =
    intentionsQuery.isLoading || projectionQuery.isLoading || ledgerQuery.isLoading;
  const hasData =
    intentionsQuery.data !== undefined ||
    projectionQuery.data !== undefined ||
    ledgerQuery.data !== undefined;
  const hasError = intentionsQuery.isError || projectionQuery.isError || ledgerQuery.isError;
  const showErrorState = !loading && hasError && !hasData;
  const showStaleNotice = hasError && hasData && isOnline;

  const projected = parseFloat(ledger?.summary.projected_balance || '0');
  const salary = parseFloat(projection?.months?.[0]?.salary || '0');

  const spendingByCategory = Object.entries(
    (ledger?.entries || [])
      .filter((entry) => entry.direction === 'outgoing')
      .reduce<Record<string, number>>((acc, entry) => {
        const key = entry.category || 'other';
        acc[key] = (acc[key] || 0) + parseFloat(entry.amount || '0');
        return acc;
      }, {})
  ).map(([category, total]) => ({ name: getCategoryLabel(category), value: total }));

  const projectionData = (projection?.months || []).map((monthData) => ({
    month: shortMonth(monthData.month),
    salario: parseFloat(monthData.salary),
    gastos: parseFloat(monthData.expenses),
    intencoes: parseFloat(monthData.intentions_total),
    sobra: parseFloat(monthData.leftover),
  }));

  const intentionsImpactTotal = (projection?.months || []).reduce(
    (sum, monthData) => sum + parseFloat(monthData.intentions_total),
    0
  );
  const periodLeftover = (projection?.months || []).reduce(
    (sum, monthData) => sum + parseFloat(monthData.leftover),
    0
  );
  const periodIncome = salary * (projection?.total_months || 0);
  const impactPercent = periodIncome > 0 ? (intentionsImpactTotal / periodIncome) * 100 : 0;
  const spendingGoal = projection?.goals?.spending_goal_percent
    ? (salary * parseFloat(projection.goals.spending_goal_percent)) / 100
    : null;

  const plannedInRange = intentions.filter(
    (intention) =>
      intention.status === 'planned' &&
      intention.month.slice(0, 7) >= startMonth &&
      intention.month.slice(0, 7) <= endMonth
  ).length;

  return (
    <SafeAreaView edges={['top']} className="flex-1 bg-zinc-50">
      <ScrollView
        contentContainerClassName="gap-6 p-4 pb-24"
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#059669']}
            tintColor="#059669"
          />
        }
      >
        <View className="gap-3">
          <View className="flex-row items-center gap-2">
            <Target size={24} color="#3f3f46" />
            <Text className="text-2xl font-bold text-zinc-900">Planejamento</Text>
          </View>
          <RangeMonthPicker
            start={startMonth}
            end={endMonth}
            onChangeStart={changeStart}
            onChangeEnd={changeEnd}
          />
        </View>

        {showStaleNotice ? (
          <View className="rounded-md bg-amber-100 px-3 py-2">
            <Text className="text-center text-sm text-amber-900">
              Não foi possível atualizar — mostrando dados salvos
            </Text>
          </View>
        ) : null}

        {loading ? (
          <View className="flex-row flex-wrap gap-3">
            {[0, 1, 2].map((index) => (
              <View
                key={index}
                className="w-[47%] grow gap-3 rounded-xl border border-zinc-200 bg-white p-4"
              >
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-7 w-28" />
                <Skeleton className="h-3 w-32" />
              </View>
            ))}
          </View>
        ) : showErrorState ? (
          <EmptyState
            title="Falha ao carregar o planejamento"
            description="Verifique a conexão e tente de novo."
            action={
              <Button variant="outline" onPress={() => void refetchAll()}>
                Tentar novamente
              </Button>
            }
          />
        ) : (
          <>
            <View className="flex-row flex-wrap gap-3">
              <View className="w-[47%] grow">
                <StatCard
                  title="Saldo do período"
                  value={formatCurrency(projected)}
                  subtitle="Salário e contas do período já incluídos"
                  tone={projected < 0 ? 'negative' : 'default'}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Intenções no período"
                  value={formatCurrency(intentionsImpactTotal)}
                  subtitle={`${plannedInRange} planejada(s) em ${projection?.total_months || 0} mês(es)`}
                  tone="warning"
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Sobra no período"
                  value={formatCurrency(periodLeftover)}
                  subtitle={`Soma das sobras de ${projection?.total_months || 0} mês(es)`}
                  tone={periodLeftover < 0 ? 'negative' : 'positive'}
                />
              </View>
            </View>

            {projection?.goals && ledger ? (
              <GoalsCard
                goals={projection.goals}
                ledger={ledger}
                salary={salary}
                months={projection.total_months || 1}
              />
            ) : null}

            <Card>
              <CardHeader>
                <CardTitle>Gastos por categoria no período</CardTitle>
                <CardDescription>
                  O que já foi lançado no período, como % da renda do período
                </CardDescription>
              </CardHeader>
              <CardContent>
                {spendingByCategory.length === 0 ? (
                  <Text className="py-10 text-center text-sm text-zinc-500">
                    Nenhum gasto no período
                  </Text>
                ) : (
                  <View className="flex-row flex-wrap gap-x-4 gap-y-2">
                    {spendingByCategory.map((entry, index) => (
                      <View key={entry.name} className="flex-row items-center gap-1.5">
                        <View
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}
                        />
                        <Text className="text-xs text-zinc-500">
                          {entry.name}{' '}
                          <Text className="font-medium text-zinc-900">
                            {formatCurrency(entry.value)}
                          </Text>
                          {periodIncome > 0
                            ? ` (${formatPercent((entry.value / periodIncome) * 100)} da renda do período)`
                            : ''}
                        </Text>
                      </View>
                    ))}
                  </View>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Projeção</CardTitle>
                <CardDescription>
                  {shortMonth(startMonth)} → {shortMonth(endMonth)}, na sua renda fixa
                </CardDescription>
              </CardHeader>
              <CardContent className="gap-4">
                {projectionData.length === 0 ? (
                  <Text className="py-6 text-center text-sm text-zinc-500">
                    Nenhum mês no período
                  </Text>
                ) : (
                  <View className="gap-2">
                    {projectionData.map((monthData) => (
                      <View
                        key={monthData.month}
                        className="gap-1 rounded-md border border-zinc-100 p-3"
                      >
                        <View className="flex-row items-center justify-between gap-2">
                          <Text className="text-sm font-medium text-zinc-900">
                            {monthData.month}
                          </Text>
                          <Text
                            className={cn(
                              'text-sm font-semibold',
                              monthData.sobra < 0 ? 'text-red-600' : 'text-emerald-600'
                            )}
                          >
                            Sobra {formatCurrency(monthData.sobra)}
                          </Text>
                        </View>
                        <View className="flex-row flex-wrap gap-x-4 gap-y-1">
                          <Text className="text-xs text-zinc-500">
                            Salário {formatCurrency(monthData.salario)}
                          </Text>
                          <Text className="text-xs text-zinc-500">
                            Gastos {formatCurrency(monthData.gastos)}
                          </Text>
                          <Text className="text-xs text-zinc-500">
                            Intenções {formatCurrency(monthData.intencoes)}
                          </Text>
                        </View>
                      </View>
                    ))}
                  </View>
                )}

                {spendingGoal != null && spendingGoal > 0 ? (
                  <Text className="text-center text-xs text-zinc-500">
                    Meta de gasto do mês: {formatCurrency(spendingGoal)}
                  </Text>
                ) : null}

                {intentionsImpactTotal > 0 ? (
                  <Text className="text-center text-xs text-zinc-500">
                    Em {projection?.total_months || 0} mês(es), as intenções somam{' '}
                    <Text className="font-semibold text-amber-700">
                      {formatCurrency(intentionsImpactTotal)}
                    </Text>{' '}
                    ({formatPercent(impactPercent)} da sua renda do período)
                  </Text>
                ) : null}
              </CardContent>
            </Card>

            <Card className="border-amber-300">
              <CardHeader className="flex-row items-start justify-between gap-3">
                <View className="flex-1">
                  <CardTitle>Intenções do período</CardTitle>
                  <CardDescription>
                    {shortMonth(startMonth)} → {shortMonth(endMonth)} · vire transação quando
                    decidir comprar
                  </CardDescription>
                </View>
                <Button
                  size="sm"
                  className="bg-amber-500 active:bg-amber-600"
                  onPress={openCreate}
                >
                  <Plus size={16} color="#ffffff" />
                  <Text className="text-sm font-medium text-white">Nova intenção</Text>
                </Button>
              </CardHeader>
              <CardContent>
                <IntentionList
                  intentions={intentionsQuery.data}
                  loading={intentionsQuery.isLoading}
                  error={
                    intentionsQuery.isError ? 'Falha ao carregar as intenções' : undefined
                  }
                  onRetry={() => void intentionsQuery.refetch()}
                  onEdit={openEdit}
                  onChanged={handleChanged}
                />
              </CardContent>
            </Card>
          </>
        )}
      </ScrollView>

      <IntentionDialog
        visible={formOpen}
        intention={editingIntention}
        defaultMonth={startMonth}
        onClose={closeForm}
        onSaved={handleChanged}
      />
    </SafeAreaView>
  );
}
