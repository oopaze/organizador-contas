import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { formatSubmitError } from '../lib/transaction-form';
import { InlineMessage } from './inline-message';
import { MonthPicker } from './month-picker';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { createIntention, updateIntention, type PurchaseIntention } from '../services';

function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

interface FormErrors {
  name?: string;
  amount?: string;
}

export interface IntentionDialogProps {
  visible: boolean;
  onClose: () => void;
  onSaved: () => void;
  /** Intenção em edição; ausente cria uma nova. */
  intention?: PurchaseIntention | null;
  /** Mês inicial do formulário de criação (`YYYY-MM`). */
  defaultMonth?: string;
}

export function IntentionDialog({
  visible,
  onClose,
  onSaved,
  intention,
  defaultMonth,
}: IntentionDialogProps) {
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [when, setWhen] = useState(defaultMonth ?? currentMonth());
  const [installments, setInstallments] = useState('1');
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setName(intention?.name ?? '');
    setAmount(intention ? String(parseFloat(intention.amount || '0')) : '');
    setWhen(intention ? intention.month.slice(0, 7) : defaultMonth ?? currentMonth());
    setInstallments(String(intention?.installments || 1));
    setErrors({});
    setError(null);
    setSaving(false);
  }, [visible, intention, defaultMonth]);

  const handleSubmit = async () => {
    if (saving) return;

    const nextErrors: FormErrors = {};
    if (!name.trim()) nextErrors.name = 'Informe o que você quer comprar';
    if (!isPositiveAmount(amount)) nextErrors.amount = 'Informe um valor válido';
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    const payload = {
      name: name.trim(),
      amount: toDecimalString(amount) as string,
      month: `${when}-01`,
      installments: Math.max(1, parseInt(installments, 10) || 1),
    };

    try {
      if (intention) {
        await updateIntention(intention.id, payload);
      } else {
        await createIntention(payload);
      }
      onSaved();
      onClose();
    } catch (submitError) {
      setError(
        formatSubmitError(
          submitError,
          intention ? 'Falha ao atualizar a intenção' : 'Falha ao adicionar a intenção'
        )
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title={intention ? 'Editar intenção' : 'Nova intenção de compra'}
      description="Dá para parcelar: a projeção mostra o impacto mês a mês."
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button
            onPress={() => void handleSubmit()}
            disabled={saving}
            className="bg-amber-500 active:bg-amber-600"
          >
            {saving ? 'Salvando...' : intention ? 'Salvar alterações' : 'Adicionar intenção'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <Input
        label="O que você quer comprar"
        placeholder="Ex: Notebook"
        value={name}
        onChangeText={setName}
      />
      {errors.name ? <Text className="-mt-2 text-sm text-red-600">{errors.name}</Text> : null}

      <View className="flex-row gap-4">
        <View className="flex-1 gap-2">
          <Input
            label="Valor total"
            keyboardType="decimal-pad"
            placeholder="0,00"
            value={amount}
            onChangeText={setAmount}
          />
          {errors.amount ? <Text className="text-sm text-red-600">{errors.amount}</Text> : null}
        </View>
        <View className="flex-1">
          <Input
            label="Parcelas"
            keyboardType="number-pad"
            value={installments}
            onChangeText={setInstallments}
          />
        </View>
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Mês da primeira parcela</Text>
        <MonthPicker value={when} onChange={setWhen} />
      </View>
    </Dialog>
  );
}
