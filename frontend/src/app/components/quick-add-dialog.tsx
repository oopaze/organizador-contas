import React, { useEffect, useState } from 'react';
import { getActors, quickAddTransaction, TransactionType, Actor } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { toast } from 'sonner';
import { TrendingDown, TrendingUp } from 'lucide-react';

interface QuickAddDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

const today = () => new Date().toISOString().split('T')[0];

export const QuickAddDialog: React.FC<QuickAddDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [actors, setActors] = useState<Actor[]>([]);
  const [direction, setDirection] = useState<TransactionType>('outgoing');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(today());
  const [installments, setInstallments] = useState('1');
  const [actorId, setActorId] = useState('none');

  useEffect(() => {
    if (!open) return;
    getActors().then(setActors).catch(() => setActors([]));
  }, [open]);

  const reset = () => {
    setDirection('outgoing');
    setAmount('');
    setDescription('');
    setDate(today());
    setInstallments('1');
    setActorId('none');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await quickAddTransaction({
        direction,
        amount,
        description,
        date,
        installments: Math.max(1, parseInt(installments, 10) || 1),
        actor_id: actorId === 'none' ? undefined : Number(actorId),
        is_paid: false,
      });
      reset();
      onSuccess();
    } catch (error) {
      const apiError = error as { response?: { data?: { error?: string } } };
      toast.error(apiError?.response?.data?.error || 'Falha ao lançar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo Lançamento</DialogTitle>
          <DialogDescription>
            Entra como não pago; a categoria é sugerida pela IA e você paga depois.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-2">
              <Button
                type="button"
                variant={direction === 'outgoing' ? 'default' : 'outline'}
                onClick={() => setDirection('outgoing')}
              >
                <TrendingDown className="w-4 h-4 mr-2" />
                Despesa
              </Button>
              <Button
                type="button"
                variant={direction === 'incoming' ? 'default' : 'outline'}
                onClick={() => setDirection('incoming')}
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Receita
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quick-amount">Valor</Label>
              <Input
                id="quick-amount"
                type="number"
                step="0.01"
                inputMode="decimal"
                placeholder="0,00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quick-description">Descrição</Label>
              <Input
                id="quick-description"
                placeholder="Ex: Padaria"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quick-date">Data</Label>
                <Input
                  id="quick-date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quick-installments">Parcelas</Label>
                <Input
                  id="quick-installments"
                  type="number"
                  min="1"
                  max="48"
                  inputMode="numeric"
                  value={installments}
                  onChange={(e) => setInstallments(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quick-actor">Ator (opcional)</Label>
              <Select value={actorId} onValueChange={setActorId}>
                <SelectTrigger id="quick-actor">
                  <SelectValue placeholder="Selecione um ator" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Nenhum</SelectItem>
                  {actors.map((actor) => (
                    <SelectItem key={actor.id} value={String(actor.id)}>
                      {actor.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Lançando...' : 'Lançar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
