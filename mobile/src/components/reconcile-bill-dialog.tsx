import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { parseIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import { formatSubmitError } from '../lib/transaction-form';
import {
  applyReconciliation,
  previewReconciliation,
  type ApplyReconciliationResult,
  type ReconcilePreview,
} from '../services';
import { InlineMessage } from './inline-message';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';

export interface ReconcileBillDialogProps {
  visible: boolean;
  onClose: () => void;
  transactionIds: number[];
  onReconciled: (result: ApplyReconciliationResult) => void;
}

function formatDate(iso: string): string {
  return parseIsoDate(iso).toLocaleDateString('pt-BR');
}

export function ReconcileBillDialog({
  visible,
  onClose,
  transactionIds,
  onReconciled,
}: ReconcileBillDialogProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [preview, setPreview] = useState<ReconcilePreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [selectedPairs, setSelectedPairs] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (!visible) return;
    setCurrentIndex(0);
    setPreview(null);
    setFailed(false);
    setApplying(false);
    setApplyError(null);
    setSelectedPairs({});
  }, [visible, transactionIds.length]);

  useEffect(() => {
    if (!visible) return;
    const billTransactionId = transactionIds[currentIndex];
    if (billTransactionId === undefined) return;

    let cancelled = false;
    setLoading(true);
    setFailed(false);
    previewReconciliation(billTransactionId)
      .then((data) => {
        if (cancelled) return;
        setPreview(data);
        setSelectedPairs(
          Object.fromEntries(data.pairs.map((pair) => [pair.bill_sub_transaction_id, true]))
        );
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [visible, currentIndex, transactionIds, reloadKey]);

  const suggestedCategory = (billSubTransactionId: number) =>
    preview?.suggested_categories.find((item) => item.sub_transaction_id === billSubTransactionId)
      ?.category;

  const checkedBillIds = (preview?.pairs ?? [])
    .filter((pair) => selectedPairs[pair.bill_sub_transaction_id])
    .map((pair) => pair.bill_sub_transaction_id);

  const handleApply = async () => {
    if (!preview || applying) return;

    setApplying(true);
    setApplyError(null);
    try {
      const result = await applyReconciliation({
        bill_transaction_id: preview.bill.id,
        pairs: preview.pairs
          .filter((pair) => selectedPairs[pair.bill_sub_transaction_id])
          .map((pair) => ({
            bill_sub_transaction_id: pair.bill_sub_transaction_id,
            real_sub_transaction_id: pair.real_sub_transaction_id,
          })),
        categories: preview.suggested_categories.filter((item) =>
          checkedBillIds.includes(item.sub_transaction_id)
        ),
      });

      if (currentIndex + 1 < transactionIds.length) {
        setCurrentIndex((index) => index + 1);
      } else {
        onReconciled(result);
      }
    } catch (submitError) {
      setApplyError(formatSubmitError(submitError, 'Falha ao conciliar'));
    } finally {
      setApplying(false);
    }
  };

  const hasContent = (preview?.pairs.length ?? 0) > 0 || (preview?.unmatched_bill.length ?? 0) > 0;
  const description = [
    preview
      ? `Fatura ${preview.bill.identifier} · vencimento ${formatDate(preview.bill.due_date)}`
      : 'Confira os lançamentos do tempo real com a fatura.',
    transactionIds.length > 1 ? `(${currentIndex + 1}/${transactionIds.length})` : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <Dialog
      visible={visible}
      onClose={applying ? () => {} : onClose}
      title="Conciliar Fatura"
      description={description}
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={applying}>
            {hasContent ? 'Cancelar' : 'Fechar'}
          </Button>
          {!loading && !failed && hasContent ? (
            <Button onPress={() => void handleApply()} disabled={applying}>
              {applying ? 'Conciliando...' : `Conciliar ${checkedBillIds.length}`}
            </Button>
          ) : null}
        </>
      }
    >
      {applyError ? <InlineMessage>{applyError}</InlineMessage> : null}

      {loading ? (
        <Text className="py-6 text-center text-sm text-zinc-500">Carregando...</Text>
      ) : null}

      {!loading && failed ? (
        <View className="items-center gap-3 py-6">
          <Text className="text-sm text-zinc-500">Falha ao carregar a conciliação.</Text>
          <Button
            variant="outline"
            onPress={() => {
              setFailed(false);
              setReloadKey((key) => key + 1);
            }}
          >
            Tentar de novo
          </Button>
        </View>
      ) : null}

      {!loading && !failed && preview && !hasContent ? (
        <Text className="py-6 text-center text-sm text-zinc-500">Nada para conciliar</Text>
      ) : null}

      {!loading && !failed && preview && hasContent ? (
        <View className="gap-4 py-2">
          {preview.pairs.length > 0 ? (
            <View className="gap-2">
              <Text className="text-sm font-medium text-zinc-900">Pares encontrados</Text>
              {preview.pairs.map((pair) => {
                const category = suggestedCategory(pair.bill_sub_transaction_id);
                return (
                  <View key={pair.bill_sub_transaction_id} className="rounded-lg border border-zinc-200 p-3">
                    <View className="flex-row items-start gap-3">
                      <Checkbox
                        checked={selectedPairs[pair.bill_sub_transaction_id] ?? false}
                        onCheckedChange={(checked) =>
                          setSelectedPairs((current) => ({
                            ...current,
                            [pair.bill_sub_transaction_id]: checked,
                          }))
                        }
                        accessibilityLabel={`Conciliar ${pair.bill.description}`}
                      />
                      <View className="flex-1 gap-1">
                        <View className="flex-row items-center justify-between gap-2">
                          <Text className="font-medium text-zinc-900">Fatura</Text>
                          <Text className="text-sm text-zinc-900">
                            {formatCurrency(pair.bill.amount)}
                          </Text>
                        </View>
                        <Text className="text-sm text-zinc-500">
                          {formatDate(pair.bill.date)} · {pair.bill.description}
                        </Text>
                        <View className="flex-row items-center justify-between gap-2">
                          <Text className="font-medium text-zinc-900">Tempo real</Text>
                          <Text className="text-sm text-zinc-900">
                            {formatCurrency(pair.real.amount)}
                          </Text>
                        </View>
                        <Text className="text-sm text-zinc-500">
                          {formatDate(pair.real.date)} · {pair.real.description}
                        </Text>
                        <View className="flex-row flex-wrap items-center gap-2 pt-1">
                          <Badge variant="outline" className="border-emerald-300">
                            {`${Math.round((pair.confidence || 0) * 100)}% de confiança`}
                          </Badge>
                          {category ? (
                            <Badge variant="secondary">{`Categoria: ${category}`}</Badge>
                          ) : null}
                        </View>
                        {pair.reason ? (
                          <Text className="text-xs text-zinc-500">{pair.reason}</Text>
                        ) : null}
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          ) : null}

          {preview.unmatched_bill.length > 0 ? (
            <View className="gap-2">
              <Text className="text-sm font-medium text-zinc-900">Só na fatura</Text>
              {preview.unmatched_bill.map((sub) => (
                <View
                  key={sub.id}
                  className="flex-row items-center justify-between rounded-lg border border-zinc-200 p-2"
                >
                  <Text className="flex-1 text-sm text-zinc-900">
                    {formatDate(sub.date)} · {sub.description}
                  </Text>
                  <Text className="ml-2 text-sm text-zinc-900">{formatCurrency(sub.amount)}</Text>
                </View>
              ))}
            </View>
          ) : null}

          {preview.unmatched_real.length > 0 ? (
            <View className="gap-2">
              <Text className="text-sm font-medium text-zinc-900">Só no tempo real</Text>
              {preview.unmatched_real.map((sub) => (
                <View
                  key={sub.id}
                  className="flex-row items-center justify-between rounded-lg border border-zinc-200 p-2"
                >
                  <Text className="flex-1 text-sm text-zinc-900">
                    {formatDate(sub.date)} · {sub.description}
                  </Text>
                  <Text className="ml-2 text-sm text-zinc-900">{formatCurrency(sub.amount)}</Text>
                </View>
              ))}
            </View>
          ) : null}
        </View>
      ) : null}
    </Dialog>
  );
}
