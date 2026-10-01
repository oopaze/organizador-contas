import { useState } from 'react';
import { FlatList, Text, View } from 'react-native';
import { useQueryClient } from '@tanstack/react-query';
import EllipsisVertical from 'lucide-react-native/icons/ellipsis-vertical';
import Pencil from 'lucide-react-native/icons/pencil';
import Trash from 'lucide-react-native/icons/trash';
import { EmptyState } from './empty-state';
import { AlertDialog } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { DropdownMenu } from './ui/dropdown-menu';
import { Skeleton } from './ui/skeleton';
import { cn } from './ui/utils';
import { getCategoryColor } from '../lib/category-colors';
import { parseIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import { invalidateFinancialData } from '../lib/invalidate-financial-data';
import { deleteSubTransaction, paySubTransaction, type SubTransaction } from '../services';

export interface SubTransactionsListProps {
  subTransactions?: SubTransaction[];
  onChanged?: () => void;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
  onEditSubTransaction?: (subTransaction: SubTransaction) => void;
  /** Nome exibido quando a subtransação não tem ator (ex.: "Ana Silva (Eu)"). */
  selfLabel?: string;
}

function formatDate(value: string): string {
  return parseIsoDate(value).toLocaleDateString('pt-BR');
}

function installmentLabel(installmentInfo?: string): string {
  if (!installmentInfo || installmentInfo === 'not installment') return 'À vista';
  return installmentInfo.replace('installment ', '').replace(' of ', '/');
}

function actorLabel(subTransaction: SubTransaction, selfLabel?: string): string {
  if (subTransaction.actor && typeof subTransaction.actor === 'object') {
    return subTransaction.actor.name;
  }
  return selfLabel ?? 'Eu';
}

interface SubTransactionRowProps {
  subTransaction: SubTransaction;
  selfLabel?: string;
  onEdit?: (subTransaction: SubTransaction) => void;
  onPay: (subTransaction: SubTransaction) => void;
  onDelete: (subTransaction: SubTransaction) => void;
}

function SubTransactionRow({
  subTransaction,
  selfLabel,
  onEdit,
  onPay,
  onDelete,
}: SubTransactionRowProps) {
  const amount = parseFloat(subTransaction.amount) || 0;
  const color = getCategoryColor(subTransaction.category);
  const isPaid = Boolean(subTransaction.paid_at);

  return (
    <View className="gap-2 rounded-lg border border-zinc-200 bg-white p-3">
      <View className="flex-row items-start justify-between gap-3">
        <View className="flex-1 gap-1">
          <Text className="text-sm font-medium text-zinc-900">{subTransaction.description}</Text>
          {subTransaction.user_provided_description ? (
            <Text className="text-xs text-zinc-500">{subTransaction.user_provided_description}</Text>
          ) : null}

          <View className="flex-row flex-wrap items-center gap-1.5">
            <Text className="text-xs text-zinc-500">#{subTransaction.id}</Text>
            <Text className="text-xs text-zinc-500">{formatDate(subTransaction.date)}</Text>
            {subTransaction.category ? (
              <Badge variant="outline" className={cn(color.bg, color.border)}>
                <Text className={cn('text-xs font-medium', color.text)}>{subTransaction.category}</Text>
              </Badge>
            ) : null}
            <Badge variant="outline">
              <Text className="text-xs font-medium text-zinc-700">
                {installmentLabel(subTransaction.installment_info)}
              </Text>
            </Badge>
            <Badge variant="secondary" className={isPaid ? 'bg-green-100' : 'bg-red-100'}>
              <Text className={cn('text-xs font-medium', isPaid ? 'text-green-800' : 'text-red-800')}>
                {isPaid ? 'Pago' : 'Pendente'}
              </Text>
            </Badge>
          </View>

          <Text className="text-xs text-zinc-500">{actorLabel(subTransaction, selfLabel)}</Text>
        </View>

        <Text
          className={cn(
            'text-sm font-semibold',
            amount < 0 ? 'text-green-600' : 'text-red-600'
          )}
        >
          {formatCurrency(Math.abs(amount))}
        </Text>
      </View>

      <View className="flex-row justify-end gap-1">
        {onEdit ? (
          <Button
            variant="ghost"
            size="icon"
            accessibilityLabel="Editar subtransação"
            onPress={() => onEdit(subTransaction)}
          >
            <Pencil size={16} color="#18181b" />
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="icon"
          accessibilityLabel="Excluir subtransação"
          onPress={() => onDelete(subTransaction)}
        >
          <Trash size={16} color="#dc2626" />
        </Button>
        <DropdownMenu
          trigger={
            <Button variant="ghost" size="icon" accessibilityLabel="Mais opções">
              <EllipsisVertical size={16} color="#18181b" />
            </Button>
          }
          items={[
            {
              label: isPaid ? 'Despagar' : 'Pagar',
              onPress: () => onPay(subTransaction),
            },
          ]}
        />
      </View>
    </View>
  );
}

export function SubTransactionsList({
  subTransactions,
  onChanged,
  loading,
  error,
  onRetry,
  onEditSubTransaction,
  selfLabel,
}: SubTransactionsListProps) {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);
  const [payTarget, setPayTarget] = useState<SubTransaction | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<SubTransaction | null>(null);
  const [working, setWorking] = useState(false);

  const items = subTransactions ?? [];

  const handleConfirmPay = async () => {
    if (!payTarget || working) return;

    const wasPaid = Boolean(payTarget.paid_at);
    setWorking(true);
    setActionError(null);
    try {
      await paySubTransaction(payTarget.id);
      setPayTarget(null);
      await invalidateFinancialData(queryClient);
      onChanged?.();
    } catch {
      setPayTarget(null);
      setActionError(
        wasPaid
          ? 'Falha ao desmarcar a subtransação como paga. Verifique a conexão e tente de novo.'
          : 'Falha ao pagar a subtransação. Verifique a conexão e tente de novo.'
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
      await deleteSubTransaction(deleteTarget.id);
      setDeleteTarget(null);
      await invalidateFinancialData(queryClient);
      onChanged?.();
    } catch {
      setDeleteTarget(null);
      setActionError('Falha ao excluir a subtransação. Verifique a conexão e tente de novo.');
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

      {loading && items.length === 0 ? (
        <View testID="sub-transactions-loading" className="gap-3">
          {[0, 1].map((index) => (
            <Skeleton key={index} className="h-20 w-full" />
          ))}
        </View>
      ) : error && items.length === 0 ? (
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
      ) : items.length === 0 ? (
        <EmptyState title="Nenhuma subtransação encontrada" />
      ) : (
        <FlatList
          data={items}
          scrollEnabled={false}
          keyExtractor={(item) => String(item.id)}
          ItemSeparatorComponent={() => <View className="h-3" />}
          renderItem={({ item }) => (
            <SubTransactionRow
              subTransaction={item}
              selfLabel={selfLabel}
              onEdit={onEditSubTransaction}
              onPay={setPayTarget}
              onDelete={setDeleteTarget}
            />
          )}
        />
      )}

      <AlertDialog
        visible={payTarget !== null}
        onCancel={() => setPayTarget(null)}
        onConfirm={() => void handleConfirmPay()}
        title={payTarget?.paid_at ? 'Despagar subtransação' : 'Pagar subtransação'}
        description={
          payTarget?.paid_at
            ? `Tem certeza que deseja marcar a subtransação "${payTarget?.description}" como não paga?`
            : `Tem certeza que deseja marcar a subtransação "${payTarget?.description}" como paga?`
        }
        confirmLabel={payTarget?.paid_at ? 'Despagar' : 'Pagar'}
        cancelLabel="Cancelar"
      />

      <AlertDialog
        visible={deleteTarget !== null}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={() => void handleConfirmDelete()}
        title="Excluir subtransação"
        description={`Tem certeza que deseja excluir a subtransação "${deleteTarget?.description}"? Esta ação não pode ser desfeita.`}
        confirmLabel="Excluir"
        cancelLabel="Cancelar"
        destructive
      />
    </View>
  );
}
