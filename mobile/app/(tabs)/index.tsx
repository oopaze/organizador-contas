import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import CircleCheck from 'lucide-react-native/icons/circle-check';
import Clock from 'lucide-react-native/icons/clock';
import FileSpreadsheet from 'lucide-react-native/icons/file-spreadsheet';
import Plus from 'lucide-react-native/icons/plus';
import TrendingDown from 'lucide-react-native/icons/trending-down';
import TrendingUp from 'lucide-react-native/icons/trending-up';
import Upload from 'lucide-react-native/icons/upload';
import Users from 'lucide-react-native/icons/users';
import Wallet from 'lucide-react-native/icons/wallet';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AddSubTransactionDialog } from '../../src/components/add-sub-transaction-dialog';
import { AddTransactionDialog } from '../../src/components/add-transaction-dialog';
import { EditSubTransactionDialog } from '../../src/components/edit-sub-transaction-dialog';
import { EditTransactionDialog } from '../../src/components/edit-transaction-dialog';
import { EmptyState } from '../../src/components/empty-state';
import { InlineMessage } from '../../src/components/inline-message';
import { LedgerList } from '../../src/components/ledger-list';
import { MonthPicker } from '../../src/components/month-picker';
import { QuickAddDialog } from '../../src/components/quick-add-dialog';
import { ReconcileBillDialog } from '../../src/components/reconcile-bill-dialog';
import { StatCard } from '../../src/components/stat-card';
import { TransactionsList } from '../../src/components/transactions-list';
import { UploadBillDialog } from '../../src/components/upload-bill-dialog';
import { UploadSheetDialog } from '../../src/components/upload-sheet-dialog';
import { Button } from '../../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../src/components/ui/card';
import { Dialog } from '../../src/components/ui/dialog';
import { Skeleton } from '../../src/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../src/components/ui/tabs';
import { cn } from '../../src/components/ui/utils';
import { useUser } from '../../src/contexts/user-context';
import { formatCurrency } from '../../src/lib/format';
import { invalidateFinancialData } from '../../src/lib/invalidate-financial-data';
import { useOnlineStatus } from '../../src/lib/use-online-status';
import {
  ensureCardBills,
  ensureSalary,
  getLedger,
  getTransactionStats,
  getTransactions,
  guessSubTransactionsCategory,
  recalculateTransactionAmount,
  type ApplyReconciliationResult,
  type SubTransaction,
  type Transaction,
} from '../../src/services';

type PaymentStatus = 'all' | 'paid' | 'unpaid';

function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function monthRange(month: string): { start: string; end: string } {
  const [year, monthNumber] = month.split('-').map(Number);
  const lastDay = new Date(year, monthNumber, 0).getDate();
  return {
    start: `${month}-01`,
    end: `${month}-${String(lastDay).padStart(2, '0')}`,
  };
}

interface PaymentFilterButtonProps {
  label: string;
  active: boolean;
  activeClassName?: string;
  icon?: ReactNode;
  onPress: () => void;
}

function PaymentFilterButton({ label, active, activeClassName, icon, onPress }: PaymentFilterButtonProps) {
  return (
    <Button
      size="sm"
      variant={active ? 'default' : 'outline'}
      className={cn(active && activeClassName)}
      onPress={onPress}
    >
      {icon}
      <Text className={cn('text-sm font-medium', active ? 'text-white' : 'text-zinc-900')}>{label}</Text>
    </Button>
  );
}

export default function HomeScreen() {
  const { user } = useUser();
  const queryClient = useQueryClient();
  const isOnline = useOnlineStatus();
  const modoOn = user?.profile?.modo_on === true;
  const selfLabel = useMemo(() => {
    const name = `${user?.profile?.first_name ?? ''} ${user?.profile?.last_name ?? ''}`.trim();
    return name ? `${name} (Eu)` : 'Eu';
  }, [user]);

  const [selectedMonth, setSelectedMonth] = useState(currentMonth);
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus>('all');
  const [includeUnpaid, setIncludeUnpaid] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [refreshing, setRefreshing] = useState(false);

  const [addTransactionOpen, setAddTransactionOpen] = useState(false);
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const [uploadBillOpen, setUploadBillOpen] = useState(false);
  const [uploadSheetOpen, setUploadSheetOpen] = useState(false);
  const [reconcileIds, setReconcileIds] = useState<number[]>([]);
  const [editTarget, setEditTarget] = useState<Transaction | null>(null);
  const [addSubTarget, setAddSubTarget] = useState<number | null>(null);
  const [editSubTarget, setEditSubTarget] = useState<SubTransaction | null>(null);
  const [recalculateTarget, setRecalculateTarget] = useState<Transaction | null>(null);
  const [guessTarget, setGuessTarget] = useState<Transaction | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [actionWorking, setActionWorking] = useState(false);

  const { start, end } = useMemo(() => monthRange(selectedMonth), [selectedMonth]);
  const transactionFilters = useMemo(
    () => ({ due_date: selectedMonth, payment_status: paymentStatus }),
    [selectedMonth, paymentStatus]
  );
  const statsFilters = useMemo(() => ({ due_date: `${selectedMonth}-01` }), [selectedMonth]);
  const ledgerFilters = useMemo(
    () => ({ start, end, include_unpaid: includeUnpaid }),
    [start, end, includeUnpaid]
  );

  const transactionsQuery = useQuery({
    queryKey: ['transactions', transactionFilters],
    queryFn: () => getTransactions(transactionFilters),
  });

  const statsQuery = useQuery({
    queryKey: ['stats', statsFilters],
    queryFn: () => getTransactionStats(statsFilters),
  });

  const ledgerQuery = useQuery({
    queryKey: ['ledger', ledgerFilters],
    queryFn: () => getLedger(ledgerFilters),
    enabled: modoOn,
  });

  const refetchAll = useCallback(
    () =>
      Promise.all([
        queryClient.refetchQueries({ queryKey: ['transactions', transactionFilters], exact: true }),
        queryClient.refetchQueries({ queryKey: ['stats', statsFilters], exact: true }),
        ...(modoOn
          ? [queryClient.refetchQueries({ queryKey: ['ledger', ledgerFilters], exact: true })]
          : []),
      ]),
    [queryClient, transactionFilters, statsFilters, ledgerFilters, modoOn]
  );

  /** Escritas dos diálogos (inclusive subtransações) invalidam tudo e releem a tela. */
  const handleDataChanged = useCallback(() => {
    void invalidateFinancialData(queryClient);
    void refetchAll();
  }, [queryClient, refetchAll]);

  const openRecalculateDialog = (transaction: Transaction) => {
    setActionError(null);
    setActionFeedback(null);
    setRecalculateTarget(transaction);
  };

  const openGuessDialog = (transaction: Transaction) => {
    setActionError(null);
    setActionFeedback(null);
    setGuessTarget(transaction);
  };

  const closeActionDialog = () => {
    if (actionWorking) return;
    setRecalculateTarget(null);
    setGuessTarget(null);
    setActionError(null);
  };

  const handleConfirmRecalculate = async () => {
    if (!recalculateTarget || actionWorking) return;

    setActionWorking(true);
    setActionError(null);
    try {
      await recalculateTransactionAmount(recalculateTarget.id);
      setRecalculateTarget(null);
      await invalidateFinancialData(queryClient);
      await refetchAll();
      setActionFeedback('Valor recalculado com sucesso');
    } catch {
      setActionError('Falha ao recalcular valor. Verifique a conexão e tente de novo.');
    } finally {
      setActionWorking(false);
    }
  };

  const handleConfirmGuess = async () => {
    if (!guessTarget || actionWorking) return;

    setActionWorking(true);
    setActionError(null);
    try {
      const response = await guessSubTransactionsCategory(guessTarget.id);
      setGuessTarget(null);
      await invalidateFinancialData(queryClient);
      await refetchAll();
      setActionFeedback(response.message || 'Categorias atualizadas com sucesso');
    } catch {
      setActionError('Falha ao adivinhar categorias. Verifique a conexão e tente de novo.');
    } finally {
      setActionWorking(false);
    }
  };

  const handleBillUploaded = useCallback(
    (transactionIds: number[]) => {
      setUploadBillOpen(false);
      handleDataChanged();
      if (modoOn && transactionIds.length > 0) {
        setReconcileIds(transactionIds);
      } else {
        setActionFeedback('Fatura enviada com sucesso!');
      }
    },
    [handleDataChanged, modoOn]
  );

  const handleSheetUploaded = useCallback(() => {
    setUploadSheetOpen(false);
    handleDataChanged();
    setActionFeedback('Planilha enviada com sucesso!');
  }, [handleDataChanged]);

  const handleReconciled = useCallback(
    (result: ApplyReconciliationResult) => {
      setReconcileIds([]);
      handleDataChanged();
      const closed = result.closed_open_bills.length;
      setActionFeedback(
        `Conciliado: ${result.merged} ${result.merged === 1 ? 'par' : 'pares'}` +
          (closed
            ? `, ${closed} fatura${closed > 1 ? 's' : ''} em aberto fechada${
                closed > 1 ? 's' : ''
              }`
            : '')
      );
    },
    [handleDataChanged]
  );

  const listActions = {
    onAddSubTransaction: (transaction: Transaction) => setAddSubTarget(transaction.id),
    onEditTransaction: (transaction: Transaction) => setEditTarget(transaction),
    onRecalculateTransaction: openRecalculateDialog,
    onGuessCategories: openGuessDialog,
    onEditSubTransaction: (subTransaction: SubTransaction) => setEditSubTarget(subTransaction),
    onChanged: refetchAll,
  };

  // ensureSalary/ensureCardBills são best-effort: nunca bloqueiam a leitura
  // nem mostram erro de tela; só invalidam as queries quando dão certo.
  useEffect(() => {
    let cancelled = false;

    const runEnsure = async () => {
      try {
        const results = await Promise.allSettled([
          ensureSalary(selectedMonth),
          ensureCardBills(selectedMonth),
        ]);
        if (cancelled || !results.some((result) => result.status === 'fulfilled')) return;
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['transactions'] }),
          queryClient.invalidateQueries({ queryKey: ['stats'] }),
          ...(modoOn ? [queryClient.invalidateQueries({ queryKey: ['ledger'] })] : []),
        ]);
      } catch {
        // best-effort silencioso
      }
    };

    void runEnsure();
    return () => {
      cancelled = true;
    };
  }, [selectedMonth, modoOn, queryClient]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await Promise.allSettled([ensureSalary(selectedMonth), ensureCardBills(selectedMonth)]);
      await refetchAll();
    } catch {
      // erros de leitura viram estado/banner; o refresh só encerra o indicador
    } finally {
      setRefreshing(false);
    }
  }, [selectedMonth, refetchAll]);

  const stats = statsQuery.data;
  const balance = stats?.balance ?? 0;
  const totalIncome = stats?.incoming_total ?? 0;
  const totalExpenses = stats?.outgoing_total ?? 0;
  const fromActors = stats?.outgoing_from_actors ?? 0;
  const realBalance = balance - fromActors;

  const hasError =
    transactionsQuery.isError || statsQuery.isError || (modoOn && ledgerQuery.isError);
  const hasCachedData = statsQuery.data !== undefined || transactionsQuery.data !== undefined;
  const cardsLoading = statsQuery.isLoading;
  const showErrorState = !cardsLoading && hasError && !hasCachedData;
  const showStaleNotice = hasError && hasCachedData && isOnline;

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
        <View className="flex-row items-center justify-between gap-2">
          <MonthPicker value={selectedMonth} onChange={setSelectedMonth} />
          {modoOn ? (
            <Button
              variant="outline"
              size="icon"
              accessibilityLabel="Adicionar receita"
              onPress={() => setAddTransactionOpen(true)}
            >
              <Plus size={16} color="#18181b" />
            </Button>
          ) : null}
        </View>

        {actionFeedback ? <InlineMessage tone="success">{actionFeedback}</InlineMessage> : null}

        {cardsLoading ? (
          <View className="flex-row flex-wrap gap-3">
            {[0, 1, 2, 3].map((index) => (
              <View
                key={index}
                className="w-[47%] grow gap-3 rounded-xl border border-zinc-200 bg-white p-4"
              >
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-7 w-24" />
                <Skeleton className="h-3 w-20" />
              </View>
            ))}
          </View>
        ) : showErrorState ? (
          <EmptyState
            title="Não foi possível carregar seus dados"
            description="Verifique a conexão e tente de novo."
            action={
              <Button variant="outline" onPress={() => void refetchAll()}>
                Tentar novamente
              </Button>
            }
          />
        ) : (
          <View className="flex-row flex-wrap gap-3">
            <View className="w-[47%] grow">
              <StatCard
                title="Saldo"
                value={formatCurrency(balance)}
                subtitle={
                  <Text className="mt-1 text-sm text-zinc-500">
                    {formatCurrency(realBalance)} <Text className="text-xs">seu saldo real</Text>
                  </Text>
                }
                icon={<Wallet size={16} color="#71717a" />}
              />
            </View>
            <View className="w-[47%] grow">
              <StatCard
                title="Receitas"
                value={formatCurrency(totalIncome)}
                subtitle="No período selecionado"
                tone="positive"
                icon={<TrendingUp size={16} color="#16a34a" />}
              />
            </View>
            <View className="w-[47%] grow">
              <StatCard
                title="Despesas"
                value={formatCurrency(totalExpenses)}
                subtitle="No período selecionado"
                tone="negative"
                icon={<TrendingDown size={16} color="#dc2626" />}
              />
            </View>
            <View className="w-[47%] grow">
              <StatCard
                title="A Receber"
                value={formatCurrency(fromActors)}
                subtitle="Gastos de terceiros no seu cartão"
                tone="warning"
                icon={<Users size={16} color="#ea580c" />}
              />
            </View>
          </View>
        )}

        <View className="flex-row gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onPress={() => setUploadBillOpen(true)}
          >
            <Upload size={16} color="#18181b" />
            <Text className="text-base font-medium text-zinc-900">Upload Fatura</Text>
          </Button>
          <Button
            variant="outline"
            className="flex-1"
            onPress={() => setUploadSheetOpen(true)}
          >
            <FileSpreadsheet size={16} color="#18181b" />
            <Text className="text-base font-medium text-zinc-900">Upload Planilha</Text>
          </Button>
        </View>

        {showStaleNotice ? (
          <View className="rounded-md bg-amber-100 px-3 py-2">
            <Text className="text-center text-sm text-amber-900">
              Não foi possível atualizar — mostrando dados salvos
            </Text>
          </View>
        ) : null}

        <Card>
          <CardHeader className="gap-4">
            <View>
              <CardTitle>Atividade Recente</CardTitle>
              <CardDescription>Visualize e gerencie suas transações</CardDescription>
            </View>

            <View className="flex-row gap-2">
              <PaymentFilterButton
                label="Todas"
                active={paymentStatus === 'all'}
                onPress={() => setPaymentStatus('all')}
              />
              <PaymentFilterButton
                label="Pagas"
                active={paymentStatus === 'paid'}
                activeClassName="bg-green-600 active:bg-green-700"
                icon={<CircleCheck size={16} color={paymentStatus === 'paid' ? '#ffffff' : '#18181b'} />}
                onPress={() => setPaymentStatus('paid')}
              />
              <PaymentFilterButton
                label="Pendentes"
                active={paymentStatus === 'unpaid'}
                activeClassName="bg-orange-600 active:bg-orange-700"
                icon={<Clock size={16} color={paymentStatus === 'unpaid' ? '#ffffff' : '#18181b'} />}
                onPress={() => setPaymentStatus('unpaid')}
              />
            </View>
          </CardHeader>

          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full">
                <TabsTrigger value="all">Todas</TabsTrigger>
                <TabsTrigger value="expenses">Despesas</TabsTrigger>
                <TabsTrigger value="income">Receitas</TabsTrigger>
                {modoOn ? <TabsTrigger value="ledger">Extrato</TabsTrigger> : null}
              </TabsList>

              <TabsContent value="all">
                <TransactionsList
                  type="all"
                  transactions={transactionsQuery.data}
                  loading={transactionsQuery.isLoading}
                  error={
                    transactionsQuery.isError
                      ? 'Não foi possível carregar as transações'
                      : undefined
                  }
                  onRetry={() => void transactionsQuery.refetch()}
                  selfLabel={selfLabel}
                  {...listActions}
                />
              </TabsContent>
              <TabsContent value="expenses">
                <TransactionsList
                  type="expenses"
                  transactions={transactionsQuery.data}
                  loading={transactionsQuery.isLoading}
                  error={
                    transactionsQuery.isError
                      ? 'Não foi possível carregar as transações'
                      : undefined
                  }
                  onRetry={() => void transactionsQuery.refetch()}
                  selfLabel={selfLabel}
                  {...listActions}
                />
              </TabsContent>
              <TabsContent value="income">
                <TransactionsList
                  type="income"
                  transactions={transactionsQuery.data}
                  loading={transactionsQuery.isLoading}
                  error={
                    transactionsQuery.isError
                      ? 'Não foi possível carregar as transações'
                      : undefined
                  }
                  onRetry={() => void transactionsQuery.refetch()}
                  selfLabel={selfLabel}
                  {...listActions}
                />
              </TabsContent>

              {modoOn ? (
                <TabsContent value="ledger">
                  <View className="mb-3 flex-row justify-end">
                    <Button
                      size="sm"
                      variant={includeUnpaid ? 'default' : 'outline'}
                      onPress={() => setIncludeUnpaid((value) => !value)}
                    >
                      {includeUnpaid ? 'Incluindo previsto' : 'Só realizado'}
                    </Button>
                  </View>
                  <LedgerList
                    ledger={ledgerQuery.data}
                    loading={ledgerQuery.isLoading}
                    error={
                      ledgerQuery.isError ? 'Não foi possível carregar o extrato' : undefined
                    }
                    onRetry={() => void ledgerQuery.refetch()}
                  />
                </TabsContent>
              ) : null}
            </Tabs>
          </CardContent>
        </Card>
      </ScrollView>

      <Pressable
        accessibilityRole="button"
        accessibilityLabel={modoOn ? 'Lançamento rápido' : 'Adicionar receita'}
        onPress={() => (modoOn ? setQuickAddOpen(true) : setAddTransactionOpen(true))}
        className="absolute bottom-6 right-5 h-14 w-14 items-center justify-center rounded-full bg-emerald-600 shadow-lg active:bg-emerald-700"
      >
        <Plus size={24} color="#ffffff" />
      </Pressable>

      <AddTransactionDialog
        visible={addTransactionOpen}
        onClose={() => setAddTransactionOpen(false)}
        onCreated={handleDataChanged}
      />

      {modoOn ? (
        <QuickAddDialog
          visible={quickAddOpen}
          onClose={() => setQuickAddOpen(false)}
          onCreated={handleDataChanged}
        />
      ) : null}

      {editTarget ? (
        <EditTransactionDialog
          key={editTarget.id}
          visible
          transaction={editTarget}
          onClose={() => setEditTarget(null)}
          onUpdated={handleDataChanged}
        />
      ) : null}

      {addSubTarget !== null ? (
        <AddSubTransactionDialog
          key={addSubTarget}
          visible
          transactionId={addSubTarget}
          onClose={() => setAddSubTarget(null)}
          onCreated={handleDataChanged}
        />
      ) : null}

      {editSubTarget ? (
        <EditSubTransactionDialog
          key={editSubTarget.id}
          visible
          subTransaction={editSubTarget}
          onClose={() => setEditSubTarget(null)}
          onUpdated={handleDataChanged}
        />
      ) : null}

      <Dialog
        visible={recalculateTarget !== null}
        onClose={closeActionDialog}
        title="Recalcular valor"
        description={`Tem certeza que deseja recalcular o valor da transação "${recalculateTarget?.transaction_identifier ?? ''}" com base nas subtransações? Esta ação não pode ser desfeita.`}
        footer={
          <>
            <Button variant="outline" onPress={closeActionDialog} disabled={actionWorking}>
              Cancelar
            </Button>
            <Button
              onPress={() => void handleConfirmRecalculate()}
              disabled={actionWorking}
            >
              {actionWorking ? 'Aguarde...' : 'Recalcular'}
            </Button>
          </>
        }
      >
        {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}
      </Dialog>

      <Dialog
        visible={guessTarget !== null}
        onClose={closeActionDialog}
        title="Adivinhar Categorias"
        description={`Tem certeza que deseja usar IA para adivinhar as categorias das subtransações da transação "${guessTarget?.transaction_identifier ?? ''}"?`}
        footer={
          <>
            <Button variant="outline" onPress={closeActionDialog} disabled={actionWorking}>
              Cancelar
            </Button>
            <Button onPress={() => void handleConfirmGuess()} disabled={actionWorking}>
              {actionWorking ? 'Aguarde...' : 'Adivinhar'}
            </Button>
          </>
        }
      >
        {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}
      </Dialog>

      <UploadBillDialog
        visible={uploadBillOpen}
        onClose={() => setUploadBillOpen(false)}
        onUploaded={handleBillUploaded}
      />

      <UploadSheetDialog
        visible={uploadSheetOpen}
        onClose={() => setUploadSheetOpen(false)}
        onUploaded={handleSheetUploaded}
      />

      {modoOn && reconcileIds.length > 0 ? (
        <ReconcileBillDialog
          visible
          transactionIds={reconcileIds}
          onClose={() => setReconcileIds([])}
          onReconciled={handleReconciled}
        />
      ) : null}
    </SafeAreaView>
  );
}
