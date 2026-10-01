import { useState } from 'react';
import { Text, View } from 'react-native';
import Pencil from 'lucide-react-native/icons/pencil';
import Trash from 'lucide-react-native/icons/trash';
import WandSparkles from 'lucide-react-native/icons/wand-sparkles';
import { EmptyState } from './empty-state';
import { InlineMessage } from './inline-message';
import { AlertDialog } from './ui/alert-dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';
import { cn } from './ui/utils';
import { parseIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import { formatSubmitError } from '../lib/transaction-form';
import { convertIntention, deleteIntention, type PurchaseIntention } from '../services';

const statusLabel: Record<PurchaseIntention['status'], string> = {
  planned: 'Planejada',
  bought: 'Comprada',
  dismissed: 'Descartada',
};

const statusBadgeClassName: Record<PurchaseIntention['status'], string> = {
  planned: 'border-amber-300 bg-amber-50',
  bought: 'border-emerald-400',
  dismissed: 'border-zinc-200',
};

const statusTextClassName: Record<PurchaseIntention['status'], string> = {
  planned: 'text-amber-700',
  bought: 'text-emerald-700',
  dismissed: 'text-zinc-500',
};

export interface IntentionListProps {
  intentions?: PurchaseIntention[];
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
  /** Abre o diálogo de edição; sem ele o botão Editar não aparece. */
  onEdit?: (intention: PurchaseIntention) => void;
  /** Chamado após converter/apagar com sucesso para a tela reler os dados. */
  onChanged: () => void;
}

type PendingAction = { action: 'convert' | 'delete'; intention: PurchaseIntention };

export function IntentionList({
  intentions,
  loading,
  error,
  onRetry,
  onEdit,
  onChanged,
}: IntentionListProps) {
  const [confirming, setConfirming] = useState<PendingAction | null>(null);
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const list = intentions ?? [];

  const runConfirmed = async () => {
    if (!confirming || working) return;
    const { action, intention } = confirming;

    setWorking(true);
    setActionError(null);
    try {
      if (action === 'convert') {
        await convertIntention(intention.id);
      } else {
        await deleteIntention(intention.id);
      }
      setConfirming(null);
      onChanged();
    } catch (submitError) {
      setConfirming(null);
      setActionError(
        formatSubmitError(
          submitError,
          action === 'convert' ? 'Falha ao converter a intenção' : 'Falha ao excluir a intenção'
        )
      );
    } finally {
      setWorking(false);
    }
  };

  if (loading && list.length === 0) {
    return (
      <View testID="intentions-loading" className="gap-4 py-2">
        {[0, 1].map((index) => (
          <View key={index} className="gap-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-3 w-28" />
          </View>
        ))}
      </View>
    );
  }

  if (error && list.length === 0) {
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

  if (list.length === 0) {
    return <EmptyState title="Nenhuma intenção no período" />;
  }

  return (
    <View className="gap-3">
      {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}

      <View>
        {list.map((intention) => {
          const perInstallment =
            parseFloat(intention.amount || '0') / Math.max(1, intention.installments);

          return (
            <View
              key={intention.id}
              className="gap-2 border-b border-zinc-100 py-3 last:border-b-0"
            >
              <View className="flex-row flex-wrap items-center gap-2">
                <Text className="max-w-full text-sm font-medium text-zinc-900">
                  {intention.name}
                </Text>
                <Badge variant="outline" className={statusBadgeClassName[intention.status]}>
                  <Text className={cn('text-xs font-medium', statusTextClassName[intention.status])}>
                    {statusLabel[intention.status]}
                  </Text>
                </Badge>
                {intention.carry_over ? (
                  <Badge variant="outline" className="border-blue-300 bg-blue-50">
                    <Text className="text-xs font-medium text-blue-700">
                      Parcela de intenção anterior
                    </Text>
                  </Badge>
                ) : null}
                <Text className="text-sm font-semibold text-amber-700">
                  {formatCurrency(intention.amount)}
                </Text>
              </View>

              <Text className="text-xs text-zinc-500">
                {parseIsoDate(intention.month).toLocaleDateString('pt-BR')}
                {intention.installments > 1
                  ? ` · ${intention.installments}x de ${formatCurrency(perInstallment)}`
                  : ''}
              </Text>

              <View className="flex-row flex-wrap items-center gap-2">
                {intention.status === 'planned' ? (
                  <>
                    <Button
                      size="sm"
                      className="bg-amber-500 active:bg-amber-600"
                      onPress={() => setConfirming({ action: 'convert', intention })}
                    >
                      <WandSparkles size={16} color="#ffffff" />
                      <Text className="text-sm font-medium text-white">Virar transação</Text>
                    </Button>
                    {onEdit ? (
                      <Button size="sm" variant="outline" onPress={() => onEdit(intention)}>
                        <Pencil size={16} color="#18181b" />
                        <Text className="text-sm font-medium text-zinc-900">Editar</Text>
                      </Button>
                    ) : null}
                  </>
                ) : null}
                {intention.status !== 'bought' ? (
                  <Button
                    size="icon"
                    variant="ghost"
                    accessibilityLabel="Excluir"
                    onPress={() => setConfirming({ action: 'delete', intention })}
                  >
                    <Trash size={16} color="#ef4444" />
                  </Button>
                ) : null}
              </View>
            </View>
          );
        })}
      </View>

      <AlertDialog
        visible={confirming !== null}
        onConfirm={() => void runConfirmed()}
        onCancel={() => setConfirming(null)}
        title={confirming?.action === 'convert' ? 'Virar transação?' : 'Excluir intenção?'}
        description={
          confirming
            ? confirming.action === 'convert'
              ? `"${confirming.intention.name}" vira uma transação com as parcelas no extrato. Não dá para desfazer.`
              : `"${confirming.intention.name}" será excluída. Não dá para desfazer.`
            : undefined
        }
        destructive={confirming?.action === 'delete'}
      />
    </View>
  );
}
