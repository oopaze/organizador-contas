import React, { useEffect, useState } from 'react';
import { Actor, getActors, createSubTransaction } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Label } from '@/app/components/ui/label';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { TRANSACTION_CATEGORIES } from '@/lib/category-colors';

interface AddSubTransactionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  transactionId: number;
  onSuccess: () => void;
}

export const AddSubTransactionDialog: React.FC<AddSubTransactionDialogProps> = ({
  open,
  onOpenChange,
  transactionId,
  onSuccess,
}) => {
  const [actors, setActors] = useState<Actor[]>([]);
  const [loadingActors, setLoadingActors] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    description: '',
    user_provided_description: '',
    amount: '',
    installment_info: '',
    actor_id: '',
    category: '',
  });

  useEffect(() => {
    if (open) {
      fetchActors();
      // Reset form when dialog opens
      setFormData({
        description: '',
        user_provided_description: '',
        amount: '',
        installment_info: '',
        actor_id: '',
        category: '',
      });
    }
  }, [open]);

  const fetchActors = async () => {
    setLoadingActors(true);
    try {
      const actorsList = await getActors();
      setActors(actorsList);
    } catch (error) {
      toast.error('Falha ao carregar atores');
      console.error('Error fetching actors:', error);
    } finally {
      setLoadingActors(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setSaving(true);
    try {
      await createSubTransaction({
        description: formData.description,
        user_provided_description: formData.user_provided_description || undefined,
        amount: formData.amount,
        installment_info: formData.installment_info || undefined,
        transaction_id: transactionId,
        actor_id: formData.actor_id ? parseInt(formData.actor_id, 10) : undefined,
        category: formData.category || undefined,
      });
      toast.success('Subtransação adicionada com sucesso');
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      toast.error('Falha ao adicionar subtransação');
      console.error('Error creating subtransaction:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Adicionar Subtransação</DialogTitle>
          <DialogDescription>
            Adicione uma nova subtransação a esta transação.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="description">Nome</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Ex: Americanas S/A"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="user_provided_description">Descrição (opcional)</Label>
              <Input
                id="user_provided_description"
                value={formData.user_provided_description}
                onChange={(e) => setFormData({ ...formData, user_provided_description: e.target.value })}
                placeholder="Ex: Compras de meu cachorro"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="amount">Valor</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                placeholder="0.00"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="installment_info">Parcela (opcional)</Label>
              <Input
                id="installment_info"
                value={formData.installment_info}
                onChange={(e) => setFormData({ ...formData, installment_info: e.target.value })}
                placeholder="Ex: 1/12"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Categoria (opcional)</Label>
              <Select
                value={formData.category || 'none'}
                onValueChange={(value) => setFormData({ ...formData, category: value === 'none' ? '' : value })}
              >
                <SelectTrigger>
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
              <Label htmlFor="actor">Ator (opcional)</Label>
              {loadingActors ? (
                <div className="flex items-center gap-2 py-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Carregando atores...</span>
                </div>
              ) : (
                <Select value={formData.actor_id} onValueChange={(value) => setFormData({ ...formData, actor_id: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um ator" />
                  </SelectTrigger>
                  <SelectContent>
                    {actors.map((actor) => (
                      <SelectItem key={actor.id} value={actor.id.toString()}>
                        {actor.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={saving || loadingActors}>
              {saving ? 'Adicionando...' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

