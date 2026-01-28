import React, { useState, useEffect } from 'react';
import { Actor, updateActor } from '@/services';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { toast } from 'sonner';

interface EditActorDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  actor: Actor | null;
}

export const EditActorDialog: React.FC<EditActorDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
  actor,
}) => {
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');

  useEffect(() => {
    if (actor) {
      setName(actor.name);
    }
  }, [actor]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!actor) return;
    
    if (!name.trim()) {
      toast.error('O nome do ator é obrigatório');
      return;
    }

    setLoading(true);

    try {
      await updateActor(actor.id, { name: name.trim() });
      toast.success('Ator atualizado com sucesso');
      onOpenChange(false);
      onSuccess();
    } catch (error) {
      console.error('Error updating actor:', error);
      toast.error('Falha ao atualizar ator');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setName(actor?.name || '');
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar Ator</DialogTitle>
          <DialogDescription>
            Altere as informações do ator
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-actor-name">Nome</Label>
              <Input
                id="edit-actor-name"
                placeholder="Ex: José, João"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
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
            <Button type="submit" disabled={loading || !name.trim()}>
              {loading ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

