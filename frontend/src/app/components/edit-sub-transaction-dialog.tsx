import React, { useEffect, useState } from 'react';
import { Actor, SubTransaction, getActors, updateSubTransaction } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Label } from '@/app/components/ui/label';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface EditSubTransactionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subTransaction: SubTransaction | null;
  onSuccess: () => void;
}

export const EditSubTransactionDialog: React.FC<EditSubTransactionDialogProps> = ({
  open,
  onOpenChange,
  subTransaction,
  onSuccess,
}) => {
  const [actors, setActors] = useState<Actor[]>([]);
  const [selectedActorId, setSelectedActorId] = useState<string>('');
  const [userProvidedDescription, setUserProvidedDescription] = useState<string>('');
  const [loadingActors, setLoadingActors] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open && subTransaction) {
      fetchActors();
      // Pre-select current actor if exists
      if (subTransaction.actor_id) {
        setSelectedActorId(subTransaction.actor_id.toString());
      } else {
        setSelectedActorId('');
      }
      // Pre-fill user provided description
      setUserProvidedDescription(subTransaction.user_provided_description || '');
    }
  }, [open, subTransaction]);

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
    if (!subTransaction) return;

    setSaving(true);
    try {
      await updateSubTransaction(subTransaction.id, {
        user_provided_description: userProvidedDescription.trim() || undefined,
        actor: selectedActorId ? parseInt(selectedActorId, 10) : undefined,
      });
      toast.success('Subtransação atualizada com sucesso');
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      toast.error('Falha ao atualizar subtransação');
      console.error('Error updating subtransaction:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveActor = async () => {
    if (!subTransaction) return;

    setSaving(true);
    try {
      await updateSubTransaction(subTransaction.id, {
        user_provided_description: userProvidedDescription.trim() || undefined,
        actor_id: undefined,
      });
      toast.success('Ator removido com sucesso');
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      toast.error('Falha ao remover ator');
      console.error('Error removing actor:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar Subtransação</DialogTitle>
          <DialogDescription>
            Atualize a descrição e vincule um ator à subtransação.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="userProvidedDescription">Descrição</Label>
              <Input
                id="userProvidedDescription"
                value={userProvidedDescription}
                onChange={(e) => setUserProvidedDescription(e.target.value)}
                placeholder="Descrição para a subtransação"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="actor">Ator</Label>
              {loadingActors ? (
                <div className="flex items-center gap-2 py-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Carregando atores...</span>
                </div>
              ) : (
                <Select value={selectedActorId} onValueChange={setSelectedActorId}>
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
              {actors.length === 0 && !loadingActors && (
                <p className="text-sm text-muted-foreground">
                  Nenhum ator cadastrado. Crie um ator primeiro.
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2">
            {subTransaction?.actor_id && (
              <Button
                type="button"
                variant="destructive"
                onClick={handleRemoveActor}
                disabled={saving}
              >
                Remover Ator
              </Button>
            )}
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={saving || loadingActors}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

