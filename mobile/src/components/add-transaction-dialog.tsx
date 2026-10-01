import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { toIsoDate } from '../lib/date';
import { CATEGORY_OPTIONS, formatSubmitError, ISO_DATE_PATTERN, TYPE_OPTIONS } from '../lib/transaction-form';
import { createTransaction, type TransactionType } from '../services';

interface FormState {
  transaction_identifier: string;
  total_amount: string;
  due_date: string;
  transaction_type: TransactionType;
  is_salary: boolean;
  is_recurrent: boolean;
  recurrence_count: string;
  category: string;
}

type FormErrors = Partial<Record<keyof FormState, string>>;

function initialForm(): FormState {
  return {
    transaction_identifier: '',
    total_amount: '',
    due_date: toIsoDate(new Date()),
    transaction_type: 'outgoing',
    is_salary: false,
    is_recurrent: false,
    recurrence_count: '',
    category: '',
  };
}

function validate(form: FormState): FormErrors {
  const errors: FormErrors = {};
  if (!form.transaction_identifier.trim()) {
    errors.transaction_identifier = 'Informe um identificador';
  }
  if (!isPositiveAmount(form.total_amount)) {
    errors.total_amount = 'Informe um valor válido';
  }
  if (!ISO_DATE_PATTERN.test(form.due_date)) {
    errors.due_date = 'Informe uma data válida (AAAA-MM-DD)';
  }
  if (form.is_recurrent && !(parseInt(form.recurrence_count, 10) >= 1)) {
    errors.recurrence_count = 'Informe a quantidade de parcelas';
  }
  return errors;
}

export interface AddTransactionDialogProps {
  visible: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function AddTransactionDialog({ visible, onClose, onCreated }: AddTransactionDialogProps) {
  const [form, setForm] = useState<FormState>(initialForm);
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (visible) {
      setForm(initialForm());
      setErrors({});
      setError(null);
      setSaving(false);
    }
  }, [visible]);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async () => {
    if (saving) return;
    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      await createTransaction({
        transaction_identifier: form.transaction_identifier.trim(),
        total_amount: toDecimalString(form.total_amount) as string,
        due_date: form.due_date,
        transaction_type: form.transaction_type,
        is_salary: form.is_salary,
        is_recurrent: form.is_recurrent,
        recurrence_count:
          form.is_recurrent && form.recurrence_count
            ? parseInt(form.recurrence_count, 10)
            : undefined,
        category: form.category || undefined,
      });
      onCreated();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao adicionar transação'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Adicionar Receita"
      description="Adicione uma nova fonte de receita"
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

      <Input
        label="Identificador"
        placeholder="Ex: Salário, Freelance"
        value={form.transaction_identifier}
        onChangeText={(value) => update('transaction_identifier', value)}
      />
      {errors.transaction_identifier ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.transaction_identifier}</Text>
      ) : null}

      <Input
        label="Valor"
        keyboardType="decimal-pad"
        placeholder="0,00"
        value={form.total_amount}
        onChangeText={(value) => update('total_amount', value)}
      />
      {errors.total_amount ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.total_amount}</Text>
      ) : null}

      <Input
        label="Data de Vencimento"
        placeholder="AAAA-MM-DD"
        value={form.due_date}
        onChangeText={(value) => update('due_date', value)}
      />
      {errors.due_date ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.due_date}</Text>
      ) : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Tipo</Text>
        <Select
          value={form.transaction_type}
          onValueChange={(value) => update('transaction_type', value as TransactionType)}
          options={TYPE_OPTIONS}
        />
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Categoria (opcional)</Text>
        <Select
          value={form.category || 'none'}
          onValueChange={(value) => update('category', value === 'none' ? '' : value)}
          options={CATEGORY_OPTIONS}
          placeholder="Selecione uma categoria"
        />
      </View>

      <View className="flex-row items-center gap-2">
        <Checkbox
          checked={form.is_salary}
          onCheckedChange={(checked) => update('is_salary', checked)}
          accessibilityLabel="É salário?"
        />
        <Text className="text-sm text-zinc-900">É salário?</Text>
      </View>

      <View className="flex-row items-center gap-2">
        <Checkbox
          checked={form.is_recurrent}
          onCheckedChange={(checked) =>
            setForm((current) => ({
              ...current,
              is_recurrent: checked,
              recurrence_count: checked ? current.recurrence_count : '',
            }))
          }
          accessibilityLabel="É recorrente?"
        />
        <Text className="text-sm text-zinc-900">É recorrente?</Text>
      </View>

      {form.is_recurrent ? (
        <>
          <Input
            label="Quantidade de Parcelas"
            keyboardType="number-pad"
            placeholder="Ex: 12"
            value={form.recurrence_count}
            onChangeText={(value) => update('recurrence_count', value)}
          />
          {errors.recurrence_count ? (
            <Text className="-mt-2 text-sm text-red-600">{errors.recurrence_count}</Text>
          ) : null}
        </>
      ) : null}
    </Dialog>
  );
}
