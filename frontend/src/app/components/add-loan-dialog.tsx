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
import { Actor, getActors, createLoan } from '@/services';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const AddLoanDialog: React.FC<Props> = ({ open, onOpenChange, onSuccess }) => {
  const [actors, setActors] = useState<Actor[]>([]);
  const [actorId, setActorId] = useState<number | ''>('');
  const [principal, setPrincipal] = useState('');
  const [lentAt, setLentAt] = useState(new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      getActors().then(setActors).catch(() => toast.error('Falha ao carregar atores'));
    }
  }, [open]);

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) {
      setActorId('');
      setPrincipal('');
      setDescription('');
      setLentAt(new Date().toISOString().slice(0, 10));
    }
    onOpenChange(isOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!actorId || !principal || !lentAt) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      await createLoan({
        actor_id: Number(actorId),
        principal_amount: principal,
        lent_at: lentAt,
        description,
      });
      toast.success('Empréstimo criado');
      setActorId('');
      setPrincipal('');
      setDescription('');
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Falha ao criar empréstimo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Novo empréstimo</DialogTitle>
          <DialogDescription>Registre dinheiro emprestado a alguém.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="loan-actor">Para quem</Label>
              <Select
                value={actorId ? String(actorId) : ''}
                onValueChange={(v) => setActorId(Number(v))}
              >
                <SelectTrigger id="loan-actor">
                  <SelectValue placeholder="Selecione um ator" />
                </SelectTrigger>
                <SelectContent>
                  {actors.map((a) => (
                    <SelectItem key={a.id} value={String(a.id)}>
                      {a.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-principal">Valor emprestado (R$)</Label>
              <Input
                id="loan-principal"
                type="number"
                step="0.01"
                min="0"
                value={principal}
                onChange={(e) => setPrincipal(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-lent-at">Data do empréstimo</Label>
              <Input
                id="loan-lent-at"
                type="date"
                value={lentAt}
                onChange={(e) => setLentAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-description">Descrição (opcional)</Label>
              <Input
                id="loan-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
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
              {loading ? 'Salvando...' : 'Criar empréstimo'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
