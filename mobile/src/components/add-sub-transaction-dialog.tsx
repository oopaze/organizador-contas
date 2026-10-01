import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { CATEGORY_OPTIONS, formatSubmitError } from '../lib/transaction-form';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { toDecimalString } from '../lib/amount';
import { createSubTransaction, getActors, type Actor } from '../services';

interface FormState {
  description: string;
  user_provided_description: string;
  amount: string;
  installment_info: string;
  actor_id: string;
  category: string;
}

function initialForm(): FormState {
  return {
    description: '',
    user_provided_description: '',
    amount: '',
    installment_info: '',
    actor_id: '',
    category: '',
  };
}

export interface AddSubTransactionDialogProps {
  visible: boolean;
  onClose: () => void;
  onCreated: () => void;
  transactionId: number;
}

export function AddSubTransactionDialog({
  visible,
  onClose,
  onCreated,
  transactionId,
}: AddSubTransactionDialogProps) {
  const [form, setForm] = useState<FormState>(initialForm);
  const [actors, setActors] = useState<Actor[]>([]);
  const [loadingActors, setLoadingActors] = useState(false);
  const [actorsError, setActorsError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Partial<Record<'description' | 'amount', string>>>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setForm(initialForm());
    setErrors({});
    setError(null);
    setSaving(false);

    let cancelled = false;
    setLoadingActors(true);
    setActorsError(null);
    getActors()
      .then((list) => {
        if (!cancelled) setActors(list);
      })
      .catch(() => {
        if (!cancelled) {
          setActors([]);
          setActorsError('Falha ao carregar atores');
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingActors(false);
      });

    return () => {
      cancelled = true;
    };
  }, [visible]);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async () => {
    if (saving) return;
    const nextErrors: Partial<Record<'description' | 'amount', string>> = {};
    if (!form.description.trim()) nextErrors.description = 'Informe o nome';
    if (toDecimalString(form.amount) === null) nextErrors.amount = 'Informe um valor válido';
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      await createSubTransaction({
        description: form.description.trim(),
        user_provided_description: form.user_provided_description.trim() || undefined,
        amount: toDecimalString(form.amount) as string,
        installment_info: form.installment_info.trim() || undefined,
        transaction_id: transactionId,
        actor_id: form.actor_id ? parseInt(form.actor_id, 10) : undefined,
        category: form.category || undefined,
      });
      onCreated();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao adicionar subtransação'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Adicionar Subtransação"
      description="Adicione uma nova subtransação a esta transação."
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={saving || loadingActors}>
            {saving ? 'Adicionando...' : 'Adicionar'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <Input
        label="Nome"
        placeholder="Ex: Americanas S/A"
        value={form.description}
        onChangeText={(value) => update('description', value)}
      />
      {errors.description ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.description}</Text>
      ) : null}

      <Input
        label="Descrição (opcional)"
        placeholder="Ex: Compras de meu cachorro"
        value={form.user_provided_description}
        onChangeText={(value) => update('user_provided_description', value)}
      />

      <Input
        label="Valor"
        keyboardType="decimal-pad"
        placeholder="0,00"
        value={form.amount}
        onChangeText={(value) => update('amount', value)}
      />
      {errors.amount ? <Text className="-mt-2 text-sm text-red-600">{errors.amount}</Text> : null}

      <Input
        label="Parcela (opcional)"
        placeholder="Ex: 1/12"
        value={form.installment_info}
        onChangeText={(value) => update('installment_info', value)}
      />

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Categoria (opcional)</Text>
        <Select
          value={form.category || 'none'}
          onValueChange={(value) => update('category', value === 'none' ? '' : value)}
          options={CATEGORY_OPTIONS}
          placeholder="Selecione uma categoria"
        />
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Ator (opcional)</Text>
        {loadingActors ? (
          <Text className="text-sm text-zinc-500">Carregando atores...</Text>
        ) : (
          <Select
            value={form.actor_id || 'none'}
            onValueChange={(value) => update('actor_id', value === 'none' ? '' : value)}
            options={[
              { value: 'none', label: 'Nenhum' },
              ...actors.map((actor) => ({ value: String(actor.id), label: actor.name })),
            ]}
            placeholder="Selecione um ator"
          />
        )}
        {actorsError ? <Text className="text-sm text-red-600">{actorsError}</Text> : null}
      </View>
    </Dialog>
  );
}
