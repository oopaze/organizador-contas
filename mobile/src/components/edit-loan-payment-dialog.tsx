import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { formatSubmitError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { updateLoanPayment, type LoanPayment } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';

interface FormErrors {
  amount?: string;
  paidAt?: string;
}

export interface EditLoanPaymentDialogProps {
  visible: boolean;
  /** Pagamento em edição; ausente mantém o diálogo fechado. */
  payment: LoanPayment | null;
  onClose: () => void;
  /** Chamado após salvar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function EditLoanPaymentDialog({
  visible,
  payment,
  onClose,
  onSaved,
}: EditLoanPaymentDialogProps) {
  const [amount, setAmount] = useState('');
  const [paidAt, setPaidAt] = useState('');
  const [note, setNote] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setAmount(payment ? String(parseFloat(payment.amount || '0')) : '');
    setPaidAt(payment?.paid_at ?? '');
    setNote(payment?.note ?? '');
    setErrors({});
    setError(null);
    setSaving(false);
  }, [visible, payment]);

  const handleSubmit = async () => {
    if (saving || !payment) return;

    const nextErrors: FormErrors = {};
    if (!isPositiveAmount(amount)) nextErrors.amount = 'Informe um valor válido';
    if (!ISO_DATE_PATTERN.test(paidAt)) {
      nextErrors.paidAt = 'Informe uma data válida (AAAA-MM-DD)';
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      await updateLoanPayment(payment.id, {
        amount: toDecimalString(amount) as string,
        paid_at: paidAt,
        note: note.trim(),
      });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao atualizar pagamento'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Editar pagamento"
      description="Altere as informações do pagamento recebido."
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
        value={amount}
        onChangeText={setAmount}
      />
      {errors.amount ? <Text className="-mt-2 text-sm text-red-600">{errors.amount}</Text> : null}

      <Input
        label="Data do pagamento"
        placeholder="AAAA-MM-DD"
        value={paidAt}
        onChangeText={setPaidAt}
      />
      {errors.paidAt ? <Text className="-mt-2 text-sm text-red-600">{errors.paidAt}</Text> : null}

      <Input label="Nota" value={note} onChangeText={setNote} />
    </Dialog>
  );
}
