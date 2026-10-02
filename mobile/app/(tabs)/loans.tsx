import { useCallback, useState } from 'react';
import { Linking, Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import ChevronRight from 'lucide-react-native/icons/chevron-right';
import CircleCheck from 'lucide-react-native/icons/circle-check';
import Clock from 'lucide-react-native/icons/clock';
import Download from 'lucide-react-native/icons/download';
import HandCoins from 'lucide-react-native/icons/hand-coins';
import Pencil from 'lucide-react-native/icons/pencil';
import Plus from 'lucide-react-native/icons/plus';
import Share2 from 'lucide-react-native/icons/share-2';
import Trash from 'lucide-react-native/icons/trash';
import TrendingUp from 'lucide-react-native/icons/trending-up';
import Wallet from 'lucide-react-native/icons/wallet';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AddLoanDialog } from '../../src/components/add-loan-dialog';
import { AddLoanPaymentDialog } from '../../src/components/add-loan-payment-dialog';
import { EditLoanDialog } from '../../src/components/edit-loan-dialog';
import { EditLoanPaymentDialog } from '../../src/components/edit-loan-payment-dialog';
import { EmptyState } from '../../src/components/empty-state';
import { InlineMessage } from '../../src/components/inline-message';
import { LoanPaymentsList } from '../../src/components/loan-payments-list';
import { ShareActorDialog } from '../../src/components/share-actor-dialog';
import { StatCard } from '../../src/components/stat-card';
import { UploadPixReceiptDialog } from '../../src/components/upload-pix-receipt-dialog';
import { AlertDialog } from '../../src/components/ui/alert-dialog';
import { Badge } from '../../src/components/ui/badge';
import { Button } from '../../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../src/components/ui/card';
import { DropdownMenu } from '../../src/components/ui/dropdown-menu';
import { Skeleton } from '../../src/components/ui/skeleton';
import { cn } from '../../src/components/ui/utils';
import { parseIsoDate } from '../../src/lib/date';
import { resolveFileUrl } from '../../src/lib/file-url';
import { formatCurrency } from '../../src/lib/format';
import { formatSubmitError } from '../../src/lib/transaction-form';
import { useOnlineStatus } from '../../src/lib/use-online-status';
import {
  deleteLoan,
  getLoanPayments,
  getLoans,
  getLoanStats,
  type Loan,
  type LoanPayment,
} from '../../src/services';

const STATUS_LABEL: Record<Loan['status'], string> = {
  active: 'Pendente',
  settled: 'Pago',
  cancelled: 'Cancelado',
};

const STATUS_CLASS: Record<Loan['status'], { container: string; text: string }> = {
  active: { container: 'border-orange-200 bg-orange-100', text: 'text-orange-800' },
  settled: { container: 'border-green-200 bg-green-100', text: 'text-green-800' },
  cancelled: { container: 'border-zinc-200 bg-zinc-100', text: 'text-zinc-600' },
};

function actorName(loan: Loan): string {
  return loan.actor?.name ?? `Actor #${loan.actor_id}`;
}

interface LoanFieldProps {
  label: string;
  value: string;
  valueClassName?: string;
}

function LoanField({ label, value, valueClassName }: LoanFieldProps) {
  return (
    <View className="min-w-[40%] flex-1 gap-0.5">
      <Text className="text-xs text-zinc-500">{label}</Text>
      <Text className={cn('text-sm font-semibold text-zinc-900', valueClassName)}>{value}</Text>
    </View>
  );
}

interface LoanCardProps {
  loan: Loan;
  expanded: boolean;
  payments?: LoanPayment[];
  paymentsLoading: boolean;
  paymentsError: boolean;
  onToggle: () => void;
  onRetryPayments: () => void;
  onUploadPix: () => void;
  onAddPayment: () => void;
  onEditPayment: (payment: LoanPayment) => void;
  onOpenFile: (url: string) => void;
  onShare: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onChanged: () => void;
}

function LoanCard({
  loan,
  expanded,
  payments,
  paymentsLoading,
  paymentsError,
  onToggle,
  onRetryPayments,
  onUploadPix,
  onAddPayment,
  onEditPayment,
  onOpenFile,
  onShare,
  onEdit,
  onDelete,
  onChanged,
}: LoanCardProps) {
  const fileUrl = resolveFileUrl(loan.file_url);
  const remaining = parseFloat(loan.remaining) || 0;

  return (
    <View className="rounded-lg border border-zinc-200 bg-white">
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={expanded ? 'Recolher pagamentos' : 'Ver pagamentos'}
        accessibilityState={{ expanded }}
        onPress={onToggle}
        className="flex-row items-center gap-2 px-3 pt-3 pb-2 active:opacity-70"
      >
        <ChevronRight
          size={16}
          color="#71717a"
          style={{ transform: [{ rotate: expanded ? '90deg' : '0deg' }] }}
        />
        <Text className="flex-1 text-sm font-medium text-zinc-900">{actorName(loan)}</Text>
        <Badge variant="outline" className={STATUS_CLASS[loan.status].container}>
          <Text className={cn('text-xs font-medium', STATUS_CLASS[loan.status].text)}>
            {STATUS_LABEL[loan.status]}
          </Text>
        </Badge>
      </Pressable>

      <View className="flex-row flex-wrap gap-x-4 gap-y-2 px-3 pb-3 pl-8">
        <LoanField
          label="Data"
          value={parseIsoDate(loan.lent_at).toLocaleDateString('pt-BR')}
        />
        <LoanField label="Emprestado" value={formatCurrency(loan.principal_amount)} />
        <LoanField label="Pago" value={formatCurrency(loan.total_paid)} />
        <LoanField
          label="Falta"
          value={formatCurrency(remaining)}
          valueClassName={remaining > 0 ? 'text-orange-600' : 'text-green-600'}
        />
      </View>

      <View className="flex-row flex-wrap items-center justify-end gap-1 border-t border-zinc-100 px-2 py-1">
        <DropdownMenu
          trigger={
            <Button
              variant="ghost"
              size="icon"
              accessibilityLabel="Adicionar pagamento"
              className="h-11 w-11"
            >
              <Plus size={16} color="#18181b" />
            </Button>
          }
          items={[
            { label: 'Subir comprovante PIX', onPress: onUploadPix },
            { label: 'Entrada manual', onPress: onAddPayment },
          ]}
        />
        {fileUrl ? (
          <Button
            variant="ghost"
            size="icon"
            className="h-11 w-11"
            accessibilityLabel="Baixar comprovante do empréstimo"
            onPress={() => onOpenFile(fileUrl)}
          >
            <Download size={16} color="#4f46e5" />
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="icon"
          className="h-11 w-11"
          accessibilityLabel="Compartilhar empréstimo"
          onPress={onShare}
        >
          <Share2 size={16} color="#71717a" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-11 w-11"
          accessibilityLabel="Editar empréstimo"
          onPress={onEdit}
        >
          <Pencil size={16} color="#18181b" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-11 w-11"
          accessibilityLabel="Remover empréstimo"
          onPress={onDelete}
        >
          <Trash size={16} color="#dc2626" />
        </Button>
      </View>

      {expanded ? (
        <View className="gap-2 border-t border-zinc-100 bg-zinc-50 p-3">
          <Text className="text-sm font-medium text-zinc-500">Pagamentos</Text>
          <LoanPaymentsList
            payments={payments}
            loading={paymentsLoading}
            error={paymentsError ? 'Falha ao carregar pagamentos' : null}
            onRetry={onRetryPayments}
            onEdit={onEditPayment}
            onChanged={onChanged}
          />
        </View>
      ) : null}
    </View>
  );
}

export default function LoansScreen() {
  const queryClient = useQueryClient();
  const isOnline = useOnlineStatus();

  const [refreshing, setRefreshing] = useState(false);
  const [expandedLoanId, setExpandedLoanId] = useState<number | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [editingLoan, setEditingLoan] = useState<Loan | null>(null);
  const [uploadFor, setUploadFor] = useState<number | undefined>(undefined);
  const [manualFor, setManualFor] = useState<number | null>(null);
  const [manualFileId, setManualFileId] = useState<number | undefined>(undefined);
  const [editingPayment, setEditingPayment] = useState<LoanPayment | null>(null);
  const [loanToDelete, setLoanToDelete] = useState<Loan | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [sharingActor, setSharingActor] = useState<{ id: number; name: string } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const loansQuery = useQuery({
    queryKey: ['loans'],
    queryFn: () => getLoans(),
  });

  const statsQuery = useQuery({
    queryKey: ['loanStats'],
    queryFn: getLoanStats,
  });

  const paymentsQuery = useQuery({
    queryKey: ['loanPayments', expandedLoanId],
    queryFn: () => getLoanPayments({ loan_id: expandedLoanId ?? 0 }),
    enabled: expandedLoanId !== null,
  });

  const refetchAll = useCallback(
    () =>
      Promise.all([
        queryClient.refetchQueries({ queryKey: ['loans'], exact: true }),
        queryClient.refetchQueries({ queryKey: ['loanStats'], exact: true }),
        queryClient.refetchQueries({
          queryKey: ['loanPayments', expandedLoanId],
          exact: true,
        }),
      ]),
    [queryClient, expandedLoanId]
  );

  /** Escritas de empréstimo/pagamento invalidam as queries e releem a tela. */
  const handleChanged = useCallback(() => {
    void queryClient.invalidateQueries({ queryKey: ['loans'] });
    void queryClient.invalidateQueries({ queryKey: ['loanStats'] });
    void queryClient.invalidateQueries({ queryKey: ['loanPayments'] });
    void refetchAll();
  }, [queryClient, refetchAll]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refetchAll();
    } finally {
      setRefreshing(false);
    }
  }, [refetchAll]);

  const toggleLoan = (id: number) => {
    setExpandedLoanId((current) => (current === id ? null : id));
  };

  const handleOpenFile = (url: string) => {
    setActionError(null);
    Linking.openURL(url).catch(() => setActionError('Não foi possível abrir o arquivo'));
  };

  const handleConfirmDelete = async () => {
    if (!loanToDelete || deleting) return;

    const target = loanToDelete;
    setDeleting(true);
    setActionError(null);
    try {
      await deleteLoan(target.id);
      if (expandedLoanId === target.id) setExpandedLoanId(null);
      setLoanToDelete(null);
      handleChanged();
    } catch (submitError) {
      setLoanToDelete(null);
      setActionError(formatSubmitError(submitError, 'Falha ao remover o empréstimo'));
    } finally {
      setDeleting(false);
    }
  };

  const loans = loansQuery.data ?? [];
  const stats = statsQuery.data;
  const loading = loansQuery.isLoading || statsQuery.isLoading;
  const hasData = loansQuery.data !== undefined || statsQuery.data !== undefined;
  const hasError = loansQuery.isError || statsQuery.isError;
  const showErrorState = !loading && hasError && !hasData;
  const showStaleNotice = hasError && hasData && isOnline;

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
            <HandCoins size={24} color="#3f3f46" />
            <Text className="text-2xl font-bold text-zinc-900">Empréstimos</Text>
          </View>
          <Button onPress={() => setAddOpen(true)}>
            <Plus size={16} color="#ffffff" />
            <Text className="text-sm font-medium text-white">Novo empréstimo</Text>
          </Button>
        </View>

        {showStaleNotice ? (
          <View className="rounded-md bg-amber-100 px-3 py-2">
            <Text className="text-center text-sm text-amber-900">
              Não foi possível atualizar — mostrando dados salvos
            </Text>
          </View>
        ) : null}

        {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}

        {loading ? (
          <View className="gap-3">
            <View className="flex-row flex-wrap gap-3">
              {[0, 1, 2, 3].map((index) => (
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
            <Skeleton className="h-40 w-full" />
          </View>
        ) : showErrorState ? (
          <EmptyState
            title="Falha ao carregar empréstimos"
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
                  title="Emprestado"
                  value={formatCurrency(stats?.total_lent ?? 0)}
                  subtitle={`${formatCurrency(stats?.active_principal ?? 0)} ativos`}
                  icon={<Wallet size={16} color="#71717a" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Recebido"
                  value={formatCurrency(stats?.total_received ?? 0)}
                  subtitle={`${stats?.payments_count ?? 0} pagamentos`}
                  tone="positive"
                  icon={<TrendingUp size={16} color="#16a34a" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="A Receber"
                  value={formatCurrency(stats?.total_outstanding ?? 0)}
                  subtitle={`${stats?.active_count ?? 0} empréstimos pendentes`}
                  tone="warning"
                  icon={<Clock size={16} color="#ea580c" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Quitados"
                  value={formatCurrency(stats?.settled_principal ?? 0)}
                  subtitle={`${stats?.settled_count ?? 0} empréstimos quitados`}
                  tone="positive"
                  icon={<CircleCheck size={16} color="#16a34a" />}
                />
              </View>
            </View>

            <Card>
              <CardHeader>
                <View className="flex-row items-center gap-2">
                  <HandCoins size={20} color="#3f3f46" />
                  <CardTitle>Empréstimos</CardTitle>
                </View>
                <CardDescription>
                  Acompanhe o dinheiro que você emprestou e os pagamentos recebidos
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loansQuery.isError && loans.length === 0 ? (
                  <View className="gap-3">
                    <InlineMessage>Falha ao carregar empréstimos</InlineMessage>
                    <Button
                      variant="outline"
                      size="sm"
                      className="self-start"
                      onPress={() => void loansQuery.refetch()}
                    >
                      Tentar novamente
                    </Button>
                  </View>
                ) : loans.length === 0 ? (
                  <EmptyState title="Nenhum empréstimo registrado ainda." />
                ) : (
                  <View className="gap-3">
                    {loans.map((loan) => {
                      const expanded = expandedLoanId === loan.id;
                      return (
                        <LoanCard
                          key={loan.id}
                          loan={loan}
                          expanded={expanded}
                          payments={expanded ? paymentsQuery.data : undefined}
                          paymentsLoading={expanded && paymentsQuery.isLoading}
                          paymentsError={expanded && paymentsQuery.isError}
                          onToggle={() => toggleLoan(loan.id)}
                          onRetryPayments={() => void paymentsQuery.refetch()}
                          onUploadPix={() => setUploadFor(loan.id)}
                          onAddPayment={() => setManualFor(loan.id)}
                          onEditPayment={setEditingPayment}
                          onOpenFile={handleOpenFile}
                          onShare={() =>
                            setSharingActor({ id: loan.actor_id, name: actorName(loan) })
                          }
                          onEdit={() => setEditingLoan(loan)}
                          onDelete={() => setLoanToDelete(loan)}
                          onChanged={handleChanged}
                        />
                      );
                    })}
                  </View>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </ScrollView>

      <AddLoanDialog visible={addOpen} onClose={() => setAddOpen(false)} onSaved={handleChanged} />

      <EditLoanDialog
        visible={editingLoan !== null}
        loan={editingLoan}
        onClose={() => setEditingLoan(null)}
        onSaved={handleChanged}
      />

      <UploadPixReceiptDialog
        visible={uploadFor !== undefined}
        preselectedLoanId={uploadFor}
        onClose={() => setUploadFor(undefined)}
        onUploaded={handleChanged}
        onParseFailed={(fileId, loanId) => {
          setManualFor(loanId);
          setManualFileId(fileId);
        }}
      />

      <AddLoanPaymentDialog
        visible={manualFor !== null}
        loanId={manualFor}
        preselectedFileId={manualFileId}
        onClose={() => {
          setManualFor(null);
          setManualFileId(undefined);
        }}
        onSaved={handleChanged}
      />

      <EditLoanPaymentDialog
        visible={editingPayment !== null}
        payment={editingPayment}
        onClose={() => setEditingPayment(null)}
        onSaved={handleChanged}
      />

      <ShareActorDialog
        visible={sharingActor !== null}
        actorId={sharingActor?.id ?? null}
        actorName={sharingActor?.name}
        onClose={() => setSharingActor(null)}
      />

      <AlertDialog
        visible={loanToDelete !== null}
        onCancel={() => setLoanToDelete(null)}
        onConfirm={() => void handleConfirmDelete()}
        title="Remover empréstimo"
        description={`Remover o empréstimo de ${loanToDelete ? actorName(loanToDelete) : ''}? Os pagamentos vinculados também serão removidos.`}
        confirmLabel="Remover"
        cancelLabel="Cancelar"
        destructive
      />
    </SafeAreaView>
  );
}
