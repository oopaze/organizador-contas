import React, { useState } from 'react';
import { createTransaction, TransactionType } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Checkbox } from '@/app/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/app/components/ui/radio-group';
import { toast } from 'sonner';

interface AddTransactionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const AddTransactionDialog: React.FC<AddTransactionDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    transaction_identifier: '',
    total_amount: '',
    due_date: new Date().toISOString().split('T')[0],
    transaction_type: 'outgoing' as TransactionType,
    is_salary: false,
    is_recurrent: false,
    recurrence_count: '',
    create_in_future_months: 'current_only' as 'current_only' | 'future_months',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const dataToSubmit = {
        ...formData,
        recurrence_count: formData.is_recurrent && formData.recurrence_count
          ? parseInt(formData.recurrence_count, 10)
          : undefined,
      };
      await createTransaction(dataToSubmit);
      setFormData({
        transaction_identifier: '',
        total_amount: '',
        due_date: new Date().toISOString().split('T')[0],
        transaction_type: 'incoming',
        is_salary: false,
        is_recurrent: false,
        recurrence_count: '',
        create_in_future_months: 'current_only',
      });
      onSuccess();
    } catch (error) {
      toast.error('Falha ao adicionar transação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Adicionar Receita</DialogTitle>
          <DialogDescription>
            Adicione uma nova fonte de receita
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="identifier">Identificador</Label>
              <Input
                id="identifier"
                placeholder="Ex: Salário, Freelance"
                value={formData.transaction_identifier}
                onChange={(e) => setFormData({ ...formData, transaction_identifier: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="amount">Valor</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                value={formData.total_amount}
                onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date">Data de Vencimento</Label>
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Tipo</Label>
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
                id="is_salary"
                checked={formData.is_salary}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, is_salary: checked as boolean })
                }
              />
              <Label htmlFor="is_salary" className="cursor-pointer">
                É salário?
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_recurrent"
                checked={formData.is_recurrent}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_recurrent: checked as boolean, recurrence_count: checked ? formData.recurrence_count : '' })
                }
              />
              <Label htmlFor="is_recurrent" className="cursor-pointer">
                É recorrente?
              </Label>
            </div>

            {formData.is_recurrent && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="recurrence_count">Quantidade de Parcelas</Label>
                  <Input
                    id="recurrence_count"
                    type="number"
                    min="1"
                    placeholder="Ex: 12"
                    value={formData.recurrence_count}
                    onChange={(e) => setFormData({ ...formData, recurrence_count: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-3">
                  <Label>Criar transações em:</Label>
                  <RadioGroup
                    value={formData.create_in_future_months}
                    onValueChange={(value: 'current_only' | 'future_months') =>
                      setFormData({ ...formData, create_in_future_months: value })
                    }
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="current_only" id="current_only" />
                      <Label htmlFor="current_only" className="cursor-pointer font-normal">
                        Somente neste mês
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="future_months" id="future_months" />
                      <Label htmlFor="future_months" className="cursor-pointer font-normal">
                        Também nos meses futuros
                      </Label>
                    </div>
                  </RadioGroup>
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adicionando...' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
