import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import FileText from 'lucide-react-native/icons/file-text';
import Upload from 'lucide-react-native/icons/upload';
import X from 'lucide-react-native/icons/x';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { toIsoDate } from '../lib/date';
import { pickFile, toUploadFilePart, type PickedFile } from '../lib/pick-file';
import { formatUploadError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { createLoanPayment, uploadLoanFile } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { LOAN_FILE_MIME_TYPES } from './add-loan-dialog';

interface FormErrors {
  amount?: string;
  paidAt?: string;
}

export interface AddLoanPaymentDialogProps {
  visible: boolean;
  loanId: number | null;
  /** Arquivo já enviado pelo comprovante PIX; pula o upload e só pede os dados. */
  preselectedFileId?: number;
  onClose: () => void;
  /** Chamado após criar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function AddLoanPaymentDialog({
  visible,
  loanId,
  preselectedFileId,
  onClose,
  onSaved,
}: AddLoanPaymentDialogProps) {
  const [amount, setAmount] = useState('');
  const [paidAt, setPaidAt] = useState(toIsoDate(new Date()));
  const [note, setNote] = useState('');
  const [selectedFile, setSelectedFile] = useState<PickedFile | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setAmount('');
    setPaidAt(toIsoDate(new Date()));
    setNote('');
    setSelectedFile(null);
    setErrors({});
    setError(null);
    setSaving(false);
  }, [visible]);

  const handleSelectFile = async () => {
    setError(null);
    try {
      const file = await pickFile(LOAN_FILE_MIME_TYPES);
      if (file) setSelectedFile(file);
    } catch {
      setError('Não foi possível abrir o seletor de arquivos');
    }
  };

  const handleSubmit = async () => {
    if (saving || !loanId) return;

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
      let fileId = preselectedFileId;
      if (selectedFile && !fileId) {
        const formData = new FormData();
        formData.append('file', toUploadFilePart(selectedFile) as unknown as Blob);
        const uploaded = await uploadLoanFile(formData);
        fileId = uploaded.id;
      }

      await createLoanPayment({
        loan_id: loanId,
        amount: toDecimalString(amount) as string,
        paid_at: paidAt,
        note: note.trim(),
        file_id: fileId,
      });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatUploadError(submitError, 'Falha ao salvar pagamento'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Adicionar pagamento"
      description={
        preselectedFileId
          ? 'Comprovante já enviado — preencha os dados manualmente.'
          : 'Registre um pagamento recebido. Você pode anexar o comprovante (PDF ou imagem).'
      }
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={saving || !loanId}>
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

      {!preselectedFileId ? (
        <View className="gap-2">
          <Text className="text-sm font-medium text-zinc-900">Comprovante (opcional)</Text>
          {selectedFile ? (
            <View className="flex-row items-center justify-between gap-2 rounded-md border border-zinc-200 bg-zinc-50 p-2">
              <View className="flex-1 flex-row items-center gap-2">
                <FileText size={16} color="#4f46e5" />
                <Text className="flex-1 text-sm text-zinc-900" numberOfLines={1}>
                  {selectedFile.name}
                </Text>
              </View>
              <Button
                variant="ghost"
                size="sm"
                accessibilityLabel="Remover arquivo"
                onPress={() => setSelectedFile(null)}
              >
                <X size={16} color="#71717a" />
              </Button>
            </View>
          ) : (
            <Button variant="outline" onPress={() => void handleSelectFile()}>
              <Upload size={16} color="#18181b" />
              <Text className="text-sm font-medium text-zinc-900">Anexar PDF ou imagem</Text>
            </Button>
          )}
        </View>
      ) : null}
    </Dialog>
  );
}
