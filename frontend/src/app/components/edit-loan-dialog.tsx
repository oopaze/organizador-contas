import React, { useEffect, useState } from 'react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { toast } from 'sonner';
import { Loan, updateLoan } from '@/services';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  loan: Loan | null;
  onSuccess: () => void;
}

export const EditLoanDialog: React.FC<Props> = ({ open, onOpenChange, loan, onSuccess }) => {
  const [principal, setPrincipal] = useState('');
  const [lentAt, setLentAt] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'active' | 'settled' | 'cancelled'>('active');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (loan) {
      setPrincipal(loan.principal_amount);
      setLentAt(loan.lent_at);
      setDescription(loan.description);
      setStatus(loan.status);
    }
  }, [loan]);

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen && loan) {
      setPrincipal(loan.principal_amount);
      setLentAt(loan.lent_at);
      setDescription(loan.description);
      setStatus(loan.status);
    }
    onOpenChange(isOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!loan) return;

    setLoading(true);
    try {
      await updateLoan(loan.id, {
        principal_amount: principal,
        lent_at: lentAt,
        description,
        status,
      });
      toast.success('Empréstimo atualizado');
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Falha ao atualizar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar empréstimo</DialogTitle>
          <DialogDescription>Altere as informações do empréstimo.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-loan-principal">Valor (R$)</Label>
              <Input
                id="edit-loan-principal"
                type="number"
                step="0.01"
                min="0"
                value={principal}
                onChange={(e) => setPrincipal(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-loan-lent-at">Data</Label>
              <Input
                id="edit-loan-lent-at"
                type="date"
                value={lentAt}
                onChange={(e) => setLentAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-loan-description">Descrição</Label>
              <Input
                id="edit-loan-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-loan-status">Status</Label>
              <Select
                value={status}
                onValueChange={(v) => setStatus(v as 'active' | 'settled' | 'cancelled')}
              >
                <SelectTrigger id="edit-loan-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Ativo</SelectItem>
                  <SelectItem value="settled">Quitado</SelectItem>
                  <SelectItem value="cancelled">Cancelado</SelectItem>
                </SelectContent>
              </Select>
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
