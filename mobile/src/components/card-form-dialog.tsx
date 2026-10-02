import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { formatUploadError } from '../lib/transaction-form';
import { createCard, updateCard, type Card } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';

export interface CardFormDialogProps {
  visible: boolean;
  onClose: () => void;
  onSaved: () => void;
  /** Cartão em edição; ausente cria um novo. */
  card?: Card | null;
}

function clampDueDay(value: string): number {
  return Math.min(31, Math.max(1, parseInt(value, 10) || 1));
}

export function CardFormDialog({ visible, onClose, onSaved, card }: CardFormDialogProps) {
  const [name, setName] = useState('');
  const [dueDay, setDueDay] = useState('1');
  const [nameError, setNameError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setName(card?.name ?? '');
    setDueDay(String(card?.due_day ?? 1));
    setNameError(null);
    setError(null);
    setSaving(false);
  }, [visible, card]);

  const handleSubmit = async () => {
    if (saving) return;

    if (!name.trim()) {
      setNameError('Informe o nome do cartão');
      return;
    }
    setNameError(null);
    setSaving(true);
    setError(null);

    const payload = { name: name.trim(), due_day: clampDueDay(dueDay) };
    try {
      if (card) {
        await updateCard(card.id, payload);
      } else {
        await createCard(payload);
      }
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatUploadError(submitError, 'Falha ao salvar o cartão'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title={card ? 'Editar cartão' : 'Novo cartão'}
      description="O dia de vencimento ancora a fatura do mês no app."
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

      <Input label="Nome" placeholder="Ex: Nubank" value={name} onChangeText={setName} />
      {nameError ? <Text className="-mt-2 text-sm text-red-600">{nameError}</Text> : null}

      <Input
        label="Dia de vencimento"
        keyboardType="number-pad"
        value={dueDay}
        onChangeText={setDueDay}
      />
    </Dialog>
  );
}
