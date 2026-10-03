import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import {
  CATEGORY_OPTIONS,
  formatSubmitError,
  ISO_DATE_PATTERN,
  TYPE_OPTIONS,
} from '../lib/transaction-form';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { amountToText, isPositiveAmount, toDecimalString } from '../lib/amount';
import { TRANSACTION_CATEGORIES } from '../lib/category-colors';
import { updateTransaction, type Transaction, type TransactionType } from '../services';

function findCategoryKey(category: string | undefined): string {
  if (!category) return '';
  const byKey = TRANSACTION_CATEGORIES.find((option) => option.key === category);
  if (byKey) return byKey.key;
  const byValue = TRANSACTION_CATEGORIES.find((option) => option.value === category);
  if (byValue) return byValue.key;
  return '';
}

interface FormState {
  transaction_identifier: string;
  total_amount: string;
  due_date: string;
  transaction_type: TransactionType;
  is_salary: boolean;
  category: string;
}

type FormErrors = Partial<Record<'transaction_identifier' | 'total_amount' | 'due_date', string>>;

function formFromTransaction(transaction: Transaction): FormState {
  return {
    transaction_identifier: transaction.transaction_identifier ?? '',
    total_amount: amountToText(transaction.total_amount),
    due_date: transaction.due_date ?? '',
    transaction_type: transaction.transaction_type ?? 'outgoing',
    is_salary: transaction.is_salary ?? false,
    category: findCategoryKey(transaction.category),
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
  return errors;
}

export interface EditTransactionDialogProps {
  visible: boolean;
  onClose: () => void;
  onUpdated: () => void;
  transaction: Transaction;
}

export function EditTransactionDialog({
  visible,
  onClose,
  onUpdated,
  transaction,
}: EditTransactionDialogProps) {
  const [form, setForm] = useState<FormState>(() => formFromTransaction(transaction));
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (visible) {
      setForm(formFromTransaction(transaction));
      setErrors({});
      setError(null);
      setSaving(false);
    }
  }, [visible, transaction]);

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
      await updateTransaction(transaction.id, {
        transaction_identifier: form.transaction_identifier.trim(),
        total_amount: toDecimalString(form.total_amount) as string,
        due_date: form.due_date,
        transaction_type: form.transaction_type,
        is_salary: form.is_salary,
        category: form.category || undefined,
      });
      onUpdated();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao atualizar transação'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Editar Transação"
      description="Atualize os dados da transação"
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
        <Text className="text-sm font-medium text-zinc-900">Categoria</Text>
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
    </Dialog>
  );
}
