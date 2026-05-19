import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Input } from '@/app/components/ui/input';
import { toast } from 'sonner';
import { createLoanPayment } from '@/services';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  loanId: number | null;
  preselectedFileId?: number;
  onSuccess: () => void;
}

export const AddLoanPaymentDialog: React.FC<Props> = ({
  open,
  onOpenChange,
  loanId,
  preselectedFileId,
  onSuccess,
}) => {
  const [amount, setAmount] = useState('');
  const [paidAt, setPaidAt] = useState(new Date().toISOString().slice(0, 10));
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setAmount('');
      setNote('');
      setPaidAt(new Date().toISOString().slice(0, 10));
    }
  }, [open]);

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) {
      setAmount('');
      setNote('');
      setPaidAt(new Date().toISOString().slice(0, 10));
    }
    onOpenChange(isOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!loanId || !amount || !paidAt) {
      toast.error('Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      await createLoanPayment({
        loan_id: loanId,
        amount,
        paid_at: paidAt,
        note,
        file_id: preselectedFileId,
      });
      toast.success('Pagamento registrado');
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Falha ao salvar pagamento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Adicionar pagamento</DialogTitle>
          <DialogDescription>
            {preselectedFileId
              ? 'Comprovante já enviado — preencha os dados manualmente.'
              : 'Registre um pagamento recebido.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="payment-amount">Valor (R$)</Label>
              <Input
                id="payment-amount"
                type="number"
                step="0.01"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-paid-at">Data do pagamento</Label>
              <Input
                id="payment-paid-at"
                type="date"
                value={paidAt}
                onChange={(e) => setPaidAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-note">Nota</Label>
              <Input
                id="payment-note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
