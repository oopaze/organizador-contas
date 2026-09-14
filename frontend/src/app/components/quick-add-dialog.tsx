import React, { useEffect, useState } from 'react';
import { getActors, quickAddTransaction, TransactionType, Actor } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Checkbox } from '@/app/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/app/components/ui/radio-group';
import { toast } from 'sonner';
import { TRANSACTION_CATEGORIES } from '@/lib/category-colors';

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
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'credit'>('cash');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(today());
  const [category, setCategory] = useState('');
  const [actorId, setActorId] = useState('none');
  const [isPaid, setIsPaid] = useState(true);
  const [cardLabel, setCardLabel] = useState('');

  useEffect(() => {
    if (!open) return;
    getActors().then(setActors).catch(() => setActors([]));
  }, [open]);

  const reset = () => {
    setDirection('outgoing');
    setPaymentMethod('cash');
    setAmount('');
    setDescription('');
    setDate(today());
    setCategory('');
    setActorId('none');
    setIsPaid(true);
    setCardLabel('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await quickAddTransaction({
        direction,
        payment_method: paymentMethod,
        amount,
        description,
        date,
        category: category || undefined,
        actor_id: actorId === 'none' ? undefined : Number(actorId),
        is_paid: paymentMethod === 'cash' ? isPaid : undefined,
        card_label: paymentMethod === 'credit' ? cardLabel.trim() : undefined,
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
            Lance agora; a fatura depois só confere.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Tipo</Label>
              <RadioGroup
                value={direction}
                onValueChange={(value) => setDirection(value as TransactionType)}
                className="flex gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="outgoing" id="direction-outgoing" />
                  <Label htmlFor="direction-outgoing" className="cursor-pointer">Despesa</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="incoming" id="direction-incoming" />
                  <Label htmlFor="direction-incoming" className="cursor-pointer">Receita</Label>
                </div>
              </RadioGroup>
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
              <Label>Pagamento</Label>
              <RadioGroup
                value={paymentMethod}
                onValueChange={(value) => setPaymentMethod(value as 'cash' | 'credit')}
                className="flex gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="cash" id="payment-cash" />
                  <Label htmlFor="payment-cash" className="cursor-pointer">Dinheiro/Débito/Pix</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="credit" id="payment-credit" />
                  <Label htmlFor="payment-credit" className="cursor-pointer">Cartão</Label>
                </div>
              </RadioGroup>
            </div>

            {paymentMethod === 'credit' ? (
              <div className="space-y-2">
                <Label htmlFor="quick-card">Cartão</Label>
                <Input
                  id="quick-card"
                  placeholder="Ex: Nubank"
                  value={cardLabel}
                  onChange={(e) => setCardLabel(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Compra entra na fatura em aberto; nasce não paga.
                </p>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="quick-paid"
                  checked={isPaid}
                  onCheckedChange={(checked) => setIsPaid(checked === true)}
                />
                <Label htmlFor="quick-paid" className="cursor-pointer">
                  Já paguei/recebi
                </Label>
                <span className="text-xs text-muted-foreground">
                  desmarque para agendar (previsão)
                </span>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="quick-category">Categoria (opcional)</Label>
              <Select
                value={category || 'none'}
                onValueChange={(value) => setCategory(value === 'none' ? '' : value)}
              >
                <SelectTrigger id="quick-category">
                  <SelectValue placeholder="Selecione uma categoria" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Nenhuma</SelectItem>
                  {TRANSACTION_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.key} value={cat.key}>
                      {cat.value}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
