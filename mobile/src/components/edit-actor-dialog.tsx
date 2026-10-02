import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { formatSubmitError } from '../lib/transaction-form';
import { updateActor, type Actor } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';

export interface EditActorDialogProps {
  visible: boolean;
  /** Ator em edição; ausente mantém o diálogo fechado. */
  actor: Actor | null;
  onClose: () => void;
  /** Chamado após salvar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function EditActorDialog({ visible, actor, onClose, onSaved }: EditActorDialogProps) {
  const [name, setName] = useState('');
  const [nameError, setNameError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setName(actor?.name ?? '');
    setNameError(null);
    setError(null);
    setSaving(false);
  }, [visible, actor]);

  const handleSubmit = async () => {
    if (saving || !actor) return;

    if (!name.trim()) {
      setNameError('Informe o nome do ator');
      return;
    }
    setNameError(null);
    setSaving(true);
    setError(null);

    try {
      await updateActor(actor.id, { name: name.trim() });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao atualizar ator'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Editar Ator"
      description="Altere as informações do ator"
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <Input label="Nome" placeholder="Ex: José, João" value={name} onChangeText={setName} />
      {nameError ? <Text className="-mt-2 text-sm text-red-600">{nameError}</Text> : null}
    </Dialog>
  );
}
