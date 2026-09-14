import React, { useEffect, useState } from 'react';
import { previewReconciliation, applyReconciliation, ReconcilePreview } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Checkbox } from '@/app/components/ui/checkbox';
import { toast } from 'sonner';

interface ReconcileBillDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  billTransactionIds: number[];
  onSuccess: () => void;
}

const formatMoney = (value: string) => `R$ ${parseFloat(value || '0').toFixed(2)}`;

const formatDate = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR');

export const ReconcileBillDialog: React.FC<ReconcileBillDialogProps> = ({
  open,
  onOpenChange,
  billTransactionIds,
  onSuccess,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [preview, setPreview] = useState<ReconcilePreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [failed, setFailed] = useState(false);
  const [selectedPairs, setSelectedPairs] = useState<Record<number, boolean>>({});

  const loadPreview = () => {
    setLoading(true);
    setFailed(false);
    previewReconciliation(billTransactionIds[currentIndex])
      .then((data) => {
        setPreview(data);
        setSelectedPairs(
          Object.fromEntries(data.pairs.map((pair) => [pair.bill_sub_transaction_id, true]))
        );
      })
      .catch(() => {
        setFailed(true);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    if (open && billTransactionIds.length > 0) {
      setCurrentIndex(0);
    }
  }, [open, billTransactionIds.length]);

  useEffect(() => {
    if (open && billTransactionIds.length > 0) {
      loadPreview();
    }
  }, [open, currentIndex]);

  const suggestedCategory = (billSubTransactionId: number) =>
    preview?.suggested_categories.find((item) => item.sub_transaction_id === billSubTransactionId)?.category;

  const checkedBillIds = (preview?.pairs || [])
    .filter((pair) => selectedPairs[pair.bill_sub_transaction_id])
    .map((pair) => pair.bill_sub_transaction_id);

  const handleApply = async () => {
    if (!preview) return;
    setApplying(true);
    try {
      const result = await applyReconciliation({
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

      const closed = result.closed_open_bills.length;
      toast.success(
        `Conciliado: ${result.merged} ${result.merged === 1 ? 'par' : 'pares'}` +
          (closed ? `, ${closed} fatura${closed > 1 ? 's' : ''} em aberto fechada${closed > 1 ? 's' : ''}` : '')
      );

      if (currentIndex + 1 < billTransactionIds.length) {
        setCurrentIndex((index) => index + 1);
      } else {
        onSuccess();
      }
    } catch (error) {
      const apiError = error as { response?: { data?: { error?: string } } };
      toast.error(apiError?.response?.data?.error || 'Falha ao conciliar');
    } finally {
      setApplying(false);
    }
  };

  const hasContent = (preview?.pairs.length || 0) > 0 || (preview?.unmatched_bill.length || 0) > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Conciliar Fatura</DialogTitle>
          <DialogDescription>
            {preview
              ? `Fatura ${preview.bill.identifier} · vencimento ${formatDate(preview.bill.due_date)}`
              : 'Confira os lançamentos do tempo real com a fatura.'}
            {billTransactionIds.length > 1 && ` (${currentIndex + 1}/${billTransactionIds.length})`}
          </DialogDescription>
        </DialogHeader>

        {loading && <p className="py-6 text-center text-sm text-muted-foreground">Carregando...</p>}

        {!loading && failed && (
          <div className="py-6 text-center space-y-3">
            <p className="text-sm text-muted-foreground">Falha ao carregar a conciliação.</p>
            <Button variant="outline" onClick={loadPreview}>Tentar de novo</Button>
          </div>
        )}

        {!loading && !failed && preview && !hasContent && (
          <p className="py-6 text-center text-sm text-muted-foreground">Nada para conciliar</p>
        )}

        {!loading && !failed && preview && hasContent && (
          <div className="space-y-4 py-2">
            {preview.pairs.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Pares encontrados</p>
                {preview.pairs.map((pair) => {
                  const category = suggestedCategory(pair.bill_sub_transaction_id);
                  return (
                    <div key={pair.bill_sub_transaction_id} className="rounded-lg border p-3">
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={selectedPairs[pair.bill_sub_transaction_id] ?? false}
                          onCheckedChange={(checked) =>
                            setSelectedPairs((current) => ({
                              ...current,
                              [pair.bill_sub_transaction_id]: checked === true,
                            }))
                          }
                        />
                        <div className="min-w-0 flex-1 space-y-1 text-sm">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium">Fatura</span>
                            <span>{formatMoney(pair.bill.amount)}</span>
                          </div>
                          <p className="text-muted-foreground">
                            {formatDate(pair.bill.date)} · {pair.bill.description}
                          </p>
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium">Tempo real</span>
                            <span>{formatMoney(pair.real.amount)}</span>
                          </div>
                          <p className="text-muted-foreground">
                            {formatDate(pair.real.date)} · {pair.real.description}
                          </p>
                          <div className="flex flex-wrap items-center gap-2 pt-1">
                            <Badge variant="outline" className="border-emerald-300 text-emerald-700">
                              {Math.round((pair.confidence || 0) * 100)}% de confiança
                            </Badge>
                            {category && <Badge variant="secondary">Categoria: {category}</Badge>}
                          </div>
                          {pair.reason && (
                            <p className="text-xs text-muted-foreground">{pair.reason}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {preview.unmatched_bill.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Só na fatura</p>
                {preview.unmatched_bill.map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between rounded-lg border p-2 text-sm">
                    <span className="truncate">
                      {formatDate(sub.date)} · {sub.description}
                    </span>
                    <span className="ml-2 shrink-0">{formatMoney(sub.amount)}</span>
                  </div>
                ))}
              </div>
            )}

            {preview.unmatched_real.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Só no tempo real</p>
                {preview.unmatched_real.map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between rounded-lg border p-2 text-sm">
                    <span className="truncate">
                      {formatDate(sub.date)} · {sub.description}
                    </span>
                    <span className="ml-2 shrink-0">{formatMoney(sub.amount)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {hasContent ? 'Cancelar' : 'Fechar'}
          </Button>
          {!loading && !failed && hasContent && (
            <Button onClick={handleApply} disabled={applying}>
              {applying ? 'Conciliando...' : `Conciliar ${checkedBillIds.length}`}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
