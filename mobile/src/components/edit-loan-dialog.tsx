import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { formatSubmitError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { updateLoan, type Loan } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';

const STATUS_OPTIONS = [
  { value: 'active', label: 'Ativo' },
  { value: 'settled', label: 'Quitado' },
  { value: 'cancelled', label: 'Cancelado' },
];

interface FormErrors {
  principal?: string;
  lentAt?: string;
}

export interface EditLoanDialogProps {
  visible: boolean;
  /** Empréstimo em edição; ausente mantém o diálogo fechado. */
  loan: Loan | null;
  onClose: () => void;
  /** Chamado após salvar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function EditLoanDialog({ visible, loan, onClose, onSaved }: EditLoanDialogProps) {
  const [principal, setPrincipal] = useState('');
  const [lentAt, setLentAt] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<Loan['status']>('active');
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setPrincipal(loan ? String(parseFloat(loan.principal_amount || '0')) : '');
    setLentAt(loan?.lent_at ?? '');
    setDescription(loan?.description ?? '');
    setStatus(loan?.status ?? 'active');
    setErrors({});
    setError(null);
    setSaving(false);
  }, [visible, loan]);

  const handleSubmit = async () => {
    if (saving || !loan) return;

    const nextErrors: FormErrors = {};
    if (!isPositiveAmount(principal)) nextErrors.principal = 'Informe um valor válido';
    if (!ISO_DATE_PATTERN.test(lentAt)) {
      nextErrors.lentAt = 'Informe uma data válida (AAAA-MM-DD)';
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      await updateLoan(loan.id, {
        principal_amount: toDecimalString(principal) as string,
        lent_at: lentAt,
        description: description.trim(),
        status,
      });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao atualizar empréstimo'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Editar empréstimo"
      description="Altere as informações do empréstimo."
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
        label="Valor (R$)"
        keyboardType="decimal-pad"
        value={principal}
        onChangeText={setPrincipal}
      />
      {errors.principal ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.principal}</Text>
      ) : null}

      <Input label="Data" placeholder="AAAA-MM-DD" value={lentAt} onChangeText={setLentAt} />
      {errors.lentAt ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.lentAt}</Text>
      ) : null}

      <Input label="Descrição" value={description} onChangeText={setDescription} />

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Status</Text>
        <Select
          value={status}
          onValueChange={(value) => setStatus(value as Loan['status'])}
          options={STATUS_OPTIONS}
        />
      </View>
    </Dialog>
  );
}
