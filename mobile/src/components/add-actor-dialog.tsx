import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { formatSubmitError } from '../lib/transaction-form';
import { createActor } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';

export interface AddActorDialogProps {
  visible: boolean;
  onClose: () => void;
  /** Chamado após criar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function AddActorDialog({ visible, onClose, onSaved }: AddActorDialogProps) {
  const [name, setName] = useState('');
  const [nameError, setNameError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setName('');
    setNameError(null);
    setError(null);
    setSaving(false);
  }, [visible]);

  const handleSubmit = async () => {
    if (saving) return;

    if (!name.trim()) {
      setNameError('Informe o nome do ator');
      return;
    }
    setNameError(null);
    setSaving(true);
    setError(null);

    try {
      await createActor({ name: name.trim() });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao criar ator'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Adicionar Ator"
      description="Crie um novo ator para vincular às suas subtransações"
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={saving}>
            {saving ? 'Criando...' : 'Criar'}
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
