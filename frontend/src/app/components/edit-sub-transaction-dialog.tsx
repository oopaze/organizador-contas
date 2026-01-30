import React, { useEffect, useState } from 'react';
import { Actor, SubTransaction, getActors, updateSubTransaction } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Label } from '@/app/components/ui/label';
import { Checkbox } from '@/app/components/ui/checkbox';
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
  const [selectedActorId, setSelectedActorId] = useState<string>((subTransaction?.actor as Actor)?.id?.toString() ?? '');
  const [userProvidedDescription, setUserProvidedDescription] = useState<string>(subTransaction?.user_provided_description ?? '');
  const [date, setDate] = useState<string>(subTransaction?.date ?? '');
  const [description, setDescription] = useState<string>(subTransaction?.description ?? '');
  const [amount, setAmount] = useState<string>(subTransaction?.amount ?? '');
  const [installmentInfo, setInstallmentInfo] = useState<string>(subTransaction?.installment_info ?? '');
  const [shouldDivideForActor, setShouldDivideForActor] = useState(false);
  const [actorAmount, setActorAmount] = useState<string>('');
  const [loadingActors, setLoadingActors] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
      fetchActors();
  }, []);

  const fetchActors = async () => {
    setLoadingActors(true);
    try {
      const actorsList = await getActors();
      setActors(actorsList);
      console.log({selectedActorId, subTransaction });
    } catch (error) {
      toast.error('Falha ao carregar atores');
      console.error('Error fetching actors:', error);
    } finally {
      setLoadingActors(false);
    }
  };

  const isActorAmountValid = (): boolean => {
    if (!shouldDivideForActor) return true;
    if (!actorAmount) return false;
    const actorAmountNum = parseFloat(actorAmount);
    const amountNum = parseFloat(amount);
    return actorAmountNum > 0 && actorAmountNum <= amountNum;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subTransaction) return;

    // Validate actor amount
    if (shouldDivideForActor && !isActorAmountValid()) {
      toast.error('O valor do ator deve ser maior que 0 e menor ou igual ao valor total');
      return;
    }

    setSaving(true);
    try {
      await updateSubTransaction(subTransaction.id, {
        date: date ?? undefined,
        description: description.trim() ?? undefined,
        user_provided_description: userProvidedDescription.trim() ?? undefined,
        amount: String(amount).trim() ?? undefined,
        installment_info: installmentInfo.trim() ?? undefined,
        actor: selectedActorId ? parseInt(selectedActorId, 10) : undefined,
        should_divide_for_actor: shouldDivideForActor ?? undefined,
        actor_amount: shouldDivideForActor && actorAmount ? parseFloat(actorAmount) : undefined,
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
            Atualize os dados da subtransação.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="date">Data</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Nome</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Ex: Americanas S/A"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="userProvidedDescription">Descrição</Label>
              <Input
                id="userProvidedDescription"
                value={userProvidedDescription}
                onChange={(e) => setUserProvidedDescription(e.target.value)}
                placeholder="Ex: Compras de meu cachorro"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="amount">Valor</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="installmentInfo">Parcela</Label>
              <Input
                id="installmentInfo"
                value={installmentInfo}
                onChange={(e) => setInstallmentInfo(e.target.value)}
                placeholder="Ex: 1/12"
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
                <Select value={selectedActorId} defaultValue={selectedActorId} onValueChange={(value) => {
                  if (value === 'null') {
                    setShouldDivideForActor(false);
                    setActorAmount('');
                    setSelectedActorId('');
                    return 
                  }
                  setSelectedActorId(value);
                }}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um ator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="null">Nenhum</SelectItem>
                    {actors.map((actor) => (
                      <SelectItem key={actor.id}  value={actor.id.toString()}>
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

            {/* Show divide option only when an actor is selected */}
            {selectedActorId && (
              <>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="shouldDivideForActor"
                    checked={shouldDivideForActor}
                    onCheckedChange={(checked) => {
                      setShouldDivideForActor(checked === true);
                      if (!checked) {
                        setActorAmount('');
                      }
                    }}
                  />
                  <Label
                    htmlFor="shouldDivideForActor"
                    className="text-sm font-normal cursor-pointer"
                  >
                    Atribuir valor parcial ao ator
                  </Label>
                </div>

                {shouldDivideForActor && (
                  <div className="space-y-2">
                    <Label htmlFor="actorAmount">Valor do Ator</Label>
                    <Input
                      id="actorAmount"
                      type="number"
                      step="0.01"
                      min="0.01"
                      max={amount || undefined}
                      value={actorAmount}
                      onChange={(e) => setActorAmount(e.target.value)}
                      placeholder="0.00"
                    />
                    {actorAmount && parseFloat(actorAmount) <= 0 && (
                      <p className="text-xs text-destructive">
                        O valor deve ser maior que 0.
                      </p>
                    )}
                    {actorAmount && amount && parseFloat(actorAmount) > parseFloat(amount) && (
                      <p className="text-xs text-destructive">
                        O valor não pode ser maior que o valor total ({amount}).
                      </p>
                    )}
                    {actorAmount && amount && parseFloat(actorAmount) > 0 && parseFloat(actorAmount) <= parseFloat(amount) && (
                      <p className="text-xs text-muted-foreground">
                        O valor restante ({(parseFloat(amount) - parseFloat(actorAmount)).toFixed(2)}) permanecerá na subtransação original.
                      </p>
                    )}
                  </div>
                )}
              </>
            )}
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
            <Button type="submit" disabled={saving || loadingActors || !isActorAmountValid()}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

