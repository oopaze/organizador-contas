import { useState } from 'react';
import { View, Text } from 'react-native';
import { useQueryClient } from '@tanstack/react-query';
import EllipsisVertical from 'lucide-react-native/icons/ellipsis-vertical';
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
import { paySubTransaction, type SubTransaction } from '../services';

export interface ActorSubTransactionsListProps {
  subTransactions?: SubTransaction[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  /** Chamado após pagar/despagar com sucesso para a tela reler o ator. */
  onChanged?: () => void;
}

function formatDate(value: string): string {
  return parseIsoDate(value).toLocaleDateString('pt-BR');
}

function installmentLabel(installmentInfo?: string): string {
  if (!installmentInfo || installmentInfo === 'not installment') return 'À vista';
  return installmentInfo.replace('installment ', '').replace(' of ', '/');
}

function SubTransactionCard({
  subTransaction,
  onPay,
}: {
  subTransaction: SubTransaction;
  onPay: (subTransaction: SubTransaction) => void;
}) {
  const amount = parseFloat(subTransaction.amount) || 0;
  const color = getCategoryColor(subTransaction.category);
  const isPaid = Boolean(subTransaction.paid_at);

  return (
    <View className="gap-2 rounded-lg border border-zinc-200 bg-white p-3">
      <View className="flex-row items-start justify-between gap-3">
        <View className="flex-1 gap-1">
          <Text className="text-sm font-medium text-zinc-900">{subTransaction.description}</Text>
          {subTransaction.user_provided_description ? (
            <Text className="text-xs text-zinc-500">
              {subTransaction.user_provided_description}
            </Text>
          ) : null}

          <View className="flex-row flex-wrap items-center gap-1.5">
            <Text className="text-xs text-zinc-500">{formatDate(subTransaction.date)}</Text>
            {subTransaction.transaction_identifier ? (
              <Text className="text-xs text-zinc-500">
                Fonte: {subTransaction.transaction_identifier}
              </Text>
            ) : null}
            {subTransaction.category ? (
              <Badge variant="outline" className={cn(color.bg, color.border)}>
                <Text className={cn('text-xs font-medium', color.text)}>
                  {subTransaction.category}
                </Text>
              </Badge>
            ) : null}
            <Badge variant="outline">
              <Text className="text-xs font-medium text-zinc-700">
                {installmentLabel(subTransaction.installment_info)}
              </Text>
            </Badge>
            <Badge variant="secondary" className={isPaid ? 'bg-green-100' : 'bg-red-100'}>
              <Text
                className={cn('text-xs font-medium', isPaid ? 'text-green-800' : 'text-red-800')}
              >
                {isPaid ? 'Pago' : 'Pendente'}
              </Text>
            </Badge>
          </View>
        </View>

        <Text
          className={cn('text-sm font-semibold', amount < 0 ? 'text-green-600' : 'text-red-600')}
        >
          {formatCurrency(Math.abs(amount))}
        </Text>
      </View>

      <View className="flex-row justify-end">
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

export function ActorSubTransactionsList({
  subTransactions,
  loading,
  error,
  onRetry,
  onChanged,
}: ActorSubTransactionsListProps) {
  const queryClient = useQueryClient();
  const [payTarget, setPayTarget] = useState<SubTransaction | null>(null);
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

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
          : 'Falha ao marcar a subtransação como paga. Verifique a conexão e tente de novo.'
      );
    } finally {
      setWorking(false);
    }
  };

  if (loading && items.length === 0) {
    return (
      <View testID="actor-sub-transactions-loading" className="gap-3">
        {[0, 1].map((index) => (
          <Skeleton key={index} className="h-20 w-full" />
        ))}
      </View>
    );
  }

  if (error && items.length === 0) {
    return (
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
    );
  }

  if (items.length === 0) {
    return <EmptyState title="Nenhuma subtransação vinculada a este ator" />;
  }

  return (
    <View className="gap-3">
      {actionError ? (
        <View className="rounded-md bg-red-100 px-3 py-2">
          <Text className="text-sm text-red-800">{actionError}</Text>
        </View>
      ) : null}

      {items.map((subTransaction) => (
        <SubTransactionCard
          key={subTransaction.id}
          subTransaction={subTransaction}
          onPay={setPayTarget}
        />
      ))}

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
    </View>
  );
}
