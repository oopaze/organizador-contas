import React, { useState, useEffect } from 'react';
import { Transaction, TransactionType, updateTransaction } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Checkbox } from '@/app/components/ui/checkbox';
import { toast } from 'sonner';

interface EditTransactionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  transaction: Transaction | null;
}

export const EditTransactionDialog: React.FC<EditTransactionDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
  transaction,
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    transaction_identifier: '',
    total_amount: '',
    due_date: '',
    transaction_type: 'outgoing' as TransactionType,
    is_salary: false,
    is_recurrent: false,
  });

  useEffect(() => {
    if (transaction) {
      setFormData({
        transaction_identifier: transaction.transaction_identifier,
        total_amount: transaction.total_amount,
        due_date: transaction.due_date,
        transaction_type: transaction.transaction_type,
        is_salary: transaction.is_salary,
        is_recurrent: transaction.is_recurrent,
      });
    }
  }, [transaction]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transaction) return;
    
    setLoading(true);
    try {
      await updateTransaction(transaction.id, formData);
      toast.success('Transação atualizada com sucesso!');
      onSuccess();
    } catch (error) {
      toast.error('Falha ao atualizar transação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar Transação</DialogTitle>
          <DialogDescription>
            Atualize os dados da transação
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-identifier">Identificador</Label>
              <Input
                id="edit-identifier"
                placeholder="Ex: Salário, Freelance"
                value={formData.transaction_identifier}
                onChange={(e) => setFormData({ ...formData, transaction_identifier: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-amount">Valor</Label>
              <Input
                id="edit-amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                value={formData.total_amount}
                onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-due_date">Data de Vencimento</Label>
              <Input
                id="edit-due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-type">Tipo</Label>
              <Select
                value={formData.transaction_type}
                onValueChange={(value: TransactionType) => 
                  setFormData({ ...formData, transaction_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="incoming">Receita</SelectItem>
                  <SelectItem value="outgoing">Despesa</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="edit-is_salary"
                checked={formData.is_salary}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, is_salary: checked as boolean })
                }
              />
              <Label htmlFor="edit-is_salary" className="cursor-pointer">
                É salário?
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="edit-is_recurrent"
                checked={formData.is_recurrent}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_recurrent: checked as boolean })
                }
              />
              <Label htmlFor="edit-is_recurrent" className="cursor-pointer">
                É recorrente?
              </Label>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
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

