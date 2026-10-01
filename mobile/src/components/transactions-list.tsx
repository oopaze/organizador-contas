import { useMemo, useState } from 'react';
import { FlatList, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import ChevronRight from 'lucide-react-native/icons/chevron-right';
import EllipsisVertical from 'lucide-react-native/icons/ellipsis-vertical';
import Pencil from 'lucide-react-native/icons/pencil';
import Plus from 'lucide-react-native/icons/plus';
import Trash from 'lucide-react-native/icons/trash';
import { EmptyState } from './empty-state';
import { SubTransactionsList } from './sub-transactions-list';
import { AlertDialog } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Collapsible } from './ui/collapsible';
import { Dialog } from './ui/dialog';
import { DropdownMenu } from './ui/dropdown-menu';
import { Skeleton } from './ui/skeleton';
import { cn } from './ui/utils';
import { getCategoryColor } from '../lib/category-colors';
import { parseIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import { invalidateFinancialData } from '../lib/invalidate-financial-data';
import {
  deleteTransaction,
  getTransaction,
  payTransaction,
  type SubTransaction,
  type Transaction,
} from '../services';

export type TransactionsListType = 'all' | 'expenses' | 'income';

export interface TransactionsListProps {
  type?: TransactionsListType;
  transactions?: Transaction[];
  onChanged: () => void;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
  onAddSubTransaction?: (transaction: Transaction) => void;
  onEditTransaction?: (transaction: Transaction) => void;
  onRecalculateTransaction?: (transaction: Transaction) => void;
  onGuessCategories?: (transaction: Transaction) => void;
  onEditSubTransaction?: (subTransaction: SubTransaction) => void;
  /** Nome exibido quando a subtransação não tem ator (ex.: "Ana Silva (Eu)"). */
  selfLabel?: string;
}

const TYPE_TO_TRANSACTION_TYPE: Record<TransactionsListType, Transaction['transaction_type'] | undefined> = {
  expenses: 'outgoing',
  income: 'incoming',
  all: undefined,
};

const TYPE_TO_LABEL: Record<TransactionsListType, string> = {
  expenses: 'despesa',
  income: 'receita',
  all: 'transação',
};

function formatDate(value: string): string {
  return parseIsoDate(value).toLocaleDateString('pt-BR');
}

interface SubTransactionsSectionProps {
  transactionId: number;
  onChanged?: () => void;
  onEditSubTransaction?: (subTransaction: SubTransaction) => void;
  selfLabel?: string;
}

function SubTransactionsSection({
  transactionId,
  onChanged,
  onEditSubTransaction,
  selfLabel,
}: SubTransactionsSectionProps) {
  const query = useQuery({
    queryKey: ['subTransactions', transactionId],
    queryFn: async () => (await getTransaction(transactionId)).sub_transactions,
  });

  return (
    <SubTransactionsList
      subTransactions={query.data}
      loading={query.isLoading}
      error={query.isError ? 'Falha ao carregar subtransações' : undefined}
      onRetry={() => void query.refetch()}
      onChanged={onChanged}
      onEditSubTransaction={onEditSubTransaction}
      selfLabel={selfLabel}
    />
  );
}

interface TransactionCardProps {
  transaction: Transaction;
  expanded: boolean;
  onToggle: () => void;
  onPay: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  onAddSubTransaction?: (transaction: Transaction) => void;
  onEditTransaction?: (transaction: Transaction) => void;
  onRecalculateTransaction?: (transaction: Transaction) => void;
  onGuessCategories?: (transaction: Transaction) => void;
  onEditSubTransaction?: (subTransaction: SubTransaction) => void;
  onChanged?: () => void;
  selfLabel?: string;
}

function TransactionCard({
  transaction,
  expanded,
  onToggle,
  onPay,
  onDelete,
  onAddSubTransaction,
  onEditTransaction,
  onRecalculateTransaction,
  onGuessCategories,
  onEditSubTransaction,
  onChanged,
  selfLabel,
}: TransactionCardProps) {
  const isIncoming = transaction.transaction_type === 'incoming';
  const color = getCategoryColor(transaction.category);
  const amountFromActor = transaction.amount_from_actor ?? 0;

  const menuItems = [
    {
      label: transaction.is_paid ? 'Despagar' : 'Pagar',
      onPress: () => onPay(transaction),
    },
    ...(onRecalculateTransaction
      ? [{ label: 'Recalcular', onPress: () => onRecalculateTransaction(transaction) }]
      : []),
    ...(onGuessCategories
      ? [{ label: 'Adivinhar Categorias', onPress: () => onGuessCategories(transaction) }]
      : []),
  ];

  return (
    <View className="gap-2 rounded-lg border border-zinc-200 bg-white p-3">
      <Collapsible
        open={expanded}
        onOpenChange={onToggle}
        trigger={
          <View className="gap-2">
            <View className="flex-row items-center gap-2">
              <ChevronRight
                size={16}
                color="#71717a"
                style={{ transform: [{ rotate: expanded ? '90deg' : '0deg' }] }}
              />
              <Text numberOfLines={1} className="flex-1 text-sm font-medium text-zinc-900">
                {transaction.transaction_identifier}
              </Text>
              <Text
                className={cn(
                  'text-sm font-semibold',
                  isIncoming ? 'text-green-600' : 'text-red-600'
                )}
              >
                {formatCurrency(transaction.total_amount)}
              </Text>
            </View>

            <View className="flex-row flex-wrap items-center gap-1.5">
              <Text className="text-xs text-zinc-500">#{transaction.id}</Text>
              <Text className="text-xs text-zinc-500">{formatDate(transaction.due_date)}</Text>

              {transaction.category ? (
                <Badge variant="outline" className={cn(color.bg, color.border)}>
                  <Text className={cn('text-xs font-medium', color.text)}>
                    {transaction.category}
                  </Text>
                </Badge>
              ) : null}

              {transaction.is_salary ? (
                <Badge variant="secondary" className="bg-green-100">
                  <Text className="text-xs font-medium text-green-800">Salário</Text>
                </Badge>
              ) : isIncoming ? (
                <Badge variant="secondary">Receita</Badge>
              ) : (
                <Badge variant="secondary">Despesa</Badge>
              )}

              {transaction.transaction_type === 'outgoing' ? (
                transaction.is_paid ? (
                  <Badge variant="secondary" className="bg-green-100">
                    <Text className="text-xs font-medium text-green-800">Pago</Text>
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="bg-red-100">
                    <Text className="text-xs font-medium text-red-800">Pendente</Text>
                  </Badge>
                )
              ) : null}

              {amountFromActor > 0 ? (
                <Text className="text-xs text-zinc-500">
                  Terceiros: {formatCurrency(amountFromActor)}
                </Text>
              ) : null}
            </View>
          </View>
        }
      >
        <View className="mt-3 rounded-md border border-zinc-200 bg-zinc-50 p-3">
          <SubTransactionsSection
            transactionId={transaction.id}
            onChanged={onChanged}
            onEditSubTransaction={onEditSubTransaction}
            selfLabel={selfLabel}
          />
        </View>
      </Collapsible>

      <View className="flex-row justify-end gap-1">
        {onAddSubTransaction ? (
          <Button
            variant="ghost"
            size="icon"
            accessibilityLabel="Adicionar subtransação"
            onPress={() => onAddSubTransaction(transaction)}
          >
            <Plus size={16} color="#18181b" />
          </Button>
        ) : null}
        {onEditTransaction ? (
          <Button
            variant="ghost"
            size="icon"
            accessibilityLabel="Editar transação"
            onPress={() => onEditTransaction(transaction)}
          >
            <Pencil size={16} color="#18181b" />
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="icon"
          accessibilityLabel="Excluir transação"
          onPress={() => onDelete(transaction)}
        >
          <Trash size={16} color="#dc2626" />
        </Button>
        {transaction.transaction_type === 'outgoing' ? (
          <DropdownMenu
            trigger={
              <Button variant="ghost" size="icon" accessibilityLabel="Mais opções">
                <EllipsisVertical size={16} color="#18181b" />
              </Button>
            }
            items={menuItems}
          />
        ) : null}
      </View>
    </View>
  );
}

export function TransactionsList({
  type = 'all',
  transactions,
  onChanged,
  loading,
  error,
  onRetry,
  onAddSubTransaction,
  onEditTransaction,
  onRecalculateTransaction,
  onGuessCategories,
  onEditSubTransaction,
  selfLabel,
}: TransactionsListProps) {
  const queryClient = useQueryClient();
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const [actionError, setActionError] = useState<string | null>(null);
  const [payTarget, setPayTarget] = useState<Transaction | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Transaction | null>(null);
  const [paySubTransactions, setPaySubTransactions] = useState(true);
  const [working, setWorking] = useState(false);

  const filtered = useMemo(() => {
    const items = transactions ?? [];
    if (type === 'all') return items;
    return items.filter(
      (transaction) => transaction.transaction_type === TYPE_TO_TRANSACTION_TYPE[type]
    );
  }, [transactions, type]);

  const toggleExpanded = (id: number) => {
    setExpandedIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const openPayDialog = (transaction: Transaction) => {
    setPaySubTransactions(true);
    setPayTarget(transaction);
  };

  const closePayDialog = () => {
    if (working) return;
    setPayTarget(null);
    setPaySubTransactions(true);
  };

  const handleConfirmPay = async () => {
    if (!payTarget || working) return;

    const wasPaid = Boolean(payTarget.is_paid);
    setWorking(true);
    setActionError(null);
    try {
      await payTransaction(payTarget.id, { updateSubTransactions: paySubTransactions });
      setPayTarget(null);
      setPaySubTransactions(true);
      await invalidateFinancialData(queryClient);
      onChanged();
    } catch {
      setPayTarget(null);
      setActionError(
        wasPaid
          ? 'Falha ao desmarcar a transação como paga. Verifique a conexão e tente de novo.'
          : 'Falha ao pagar a transação. Verifique a conexão e tente de novo.'
      );
    } finally {
      setWorking(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget || working) return;

    setWorking(true);
    setActionError(null);
    try {
      await deleteTransaction(deleteTarget.id);
      setDeleteTarget(null);
      await invalidateFinancialData(queryClient);
      onChanged();
    } catch {
      setDeleteTarget(null);
      setActionError('Falha ao excluir a transação. Verifique a conexão e tente de novo.');
    } finally {
      setWorking(false);
    }
  };

  return (
    <View className="gap-3">
      {actionError ? (
        <View className="rounded-md bg-red-100 px-3 py-2">
          <Text className="text-sm text-red-800">{actionError}</Text>
        </View>
      ) : null}

      {loading && filtered.length === 0 ? (
        <View testID="transactions-loading" className="gap-3">
          {[0, 1, 2].map((index) => (
            <Skeleton key={index} className="h-24 w-full" />
          ))}
        </View>
      ) : error && filtered.length === 0 ? (
        <EmptyState
          title={error}
          action={
            onRetry ? (
              <Button variant="outline" onPress={onRetry}>
                Tentar novamente
              </Button>
            ) : undefined
          }
        />
      ) : filtered.length === 0 ? (
        <EmptyState title={`Nenhuma ${TYPE_TO_LABEL[type]} encontrada`} />
      ) : (
        <FlatList
          data={filtered}
          scrollEnabled={false}
          keyExtractor={(item) => String(item.id)}
          ItemSeparatorComponent={() => <View className="h-3" />}
          renderItem={({ item }) => (
            <TransactionCard
              transaction={item}
              expanded={expandedIds.has(item.id)}
              onToggle={() => toggleExpanded(item.id)}
              onPay={openPayDialog}
              onDelete={setDeleteTarget}
              onAddSubTransaction={onAddSubTransaction}
              onEditTransaction={onEditTransaction}
              onRecalculateTransaction={onRecalculateTransaction}
              onGuessCategories={onGuessCategories}
              onEditSubTransaction={onEditSubTransaction}
              onChanged={onChanged}
              selfLabel={selfLabel}
            />
          )}
        />
      )}

      <Dialog
        visible={payTarget !== null}
        onClose={closePayDialog}
        title={payTarget?.is_paid ? 'Despagar transação' : 'Pagar transação'}
        description={
          payTarget?.is_paid
            ? `Tem certeza que deseja marcar a transação "${payTarget?.transaction_identifier}" como não paga?`
            : `Tem certeza que deseja marcar a transação "${payTarget?.transaction_identifier}" como paga?`
        }
        footer={
          <>
            <Button variant="outline" onPress={closePayDialog} disabled={working}>
              Cancelar
            </Button>
            <Button onPress={() => void handleConfirmPay()} disabled={working}>
              {working ? 'Aguarde...' : payTarget?.is_paid ? 'Despagar' : 'Pagar'}
            </Button>
          </>
        }
      >
        <View className="flex-row items-start gap-2">
          <Checkbox
            checked={paySubTransactions}
            onCheckedChange={setPaySubTransactions}
            accessibilityLabel="Atualizar subtransações"
          />
          <Text className="flex-1 text-sm text-zinc-700">
            {payTarget?.is_paid
              ? 'Marcar todas as subtransações como não pagas também'
              : 'Marcar todas as subtransações como pagas também'}
          </Text>
        </View>
      </Dialog>

      <AlertDialog
        visible={deleteTarget !== null}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={() => void handleConfirmDelete()}
        title="Excluir transação"
        description={`Tem certeza que deseja excluir a transação "${deleteTarget?.transaction_identifier}"? Esta ação não pode ser desfeita.`}
        confirmLabel="Excluir"
        cancelLabel="Cancelar"
        destructive
      />
    </View>
  );
}
