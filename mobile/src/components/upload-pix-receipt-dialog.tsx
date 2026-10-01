import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import FileText from 'lucide-react-native/icons/file-text';
import Upload from 'lucide-react-native/icons/upload';
import X from 'lucide-react-native/icons/x';
import { AI_MODEL_OPTIONS, DEFAULT_AI_MODEL } from '../lib/ai-models';
import { formatCurrency } from '../lib/format';
import { pickFile, toUploadFilePart, type PickedFile } from '../lib/pick-file';
import { formatUploadError } from '../lib/transaction-form';
import {
  getLoans,
  uploadPixReceipt,
  type Loan,
  type UploadPixReceiptResult,
} from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';

export interface UploadPixReceiptDialogProps {
  visible: boolean;
  onClose: () => void;
  onUploaded: (result: UploadPixReceiptResult) => void;
  preselectedLoanId?: number;
  onParseFailed?: (fileId: number, loanId: number) => void;
}

export function UploadPixReceiptDialog({
  visible,
  onClose,
  onUploaded,
  preselectedLoanId,
  onParseFailed,
}: UploadPixReceiptDialogProps) {
  const [loading, setLoading] = useState(false);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loanId, setLoanId] = useState<number | undefined>(preselectedLoanId);
  const [selectedFile, setSelectedFile] = useState<PickedFile | null>(null);
  const [hasPassword, setHasPassword] = useState(false);
  const [password, setPassword] = useState('');
  const [model, setModel] = useState(DEFAULT_AI_MODEL);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible) return;

    setLoading(false);
    setSelectedFile(null);
    setHasPassword(false);
    setPassword('');
    setModel(DEFAULT_AI_MODEL);
    setError(null);
    setLoanId(preselectedLoanId);

    if (preselectedLoanId) return;

    let cancelled = false;
    getLoans({ status: 'active' })
      .then((list) => {
        if (!cancelled) setLoans(list);
      })
      .catch(() => {
        if (!cancelled) setError('Falha ao carregar empréstimos');
      });
    return () => {
      cancelled = true;
    };
  }, [visible, preselectedLoanId]);

  const handleSelectFile = async () => {
    setError(null);
    try {
      const file = await pickFile(['application/pdf']);
      if (file) setSelectedFile(file);
    } catch {
      setError('Não foi possível abrir o seletor de arquivos');
    }
  };

  const handleSubmit = async () => {
    if (loading) return;
    if (!selectedFile) {
      setError('Selecione um arquivo PDF');
      return;
    }
    if (!loanId) {
      setError('Selecione um empréstimo');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', toUploadFilePart(selectedFile) as unknown as Blob);
      formData.append('loan_id', String(loanId));
      formData.append('model', model);
      if (hasPassword && password) formData.append('password', password);

      const result = await uploadPixReceipt(formData);
      onUploaded(result);
      onClose();
    } catch (submitError) {
      const data = (
        submitError as { response?: { data?: { file_id?: number; error?: string } } }
      )?.response?.data ?? {};

      if (data.file_id && onParseFailed) {
        onClose();
        onParseFailed(Number(data.file_id), loanId);
      } else if (data.file_id) {
        setError(`${data.error ?? 'Falha ao processar o comprovante'}. Use entrada manual.`);
      } else {
        setError(formatUploadError(submitError, 'Falha ao processar o comprovante'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={loading ? () => {} : onClose}
      title="Subir comprovante PIX"
      description="A IA vai extrair valor, data e ID do comprovante e criar o pagamento."
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            onPress={() => void handleSubmit()}
            disabled={loading || !selectedFile || !loanId}
          >
            {loading ? 'Enviando...' : 'Enviar comprovante'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      {!preselectedLoanId ? (
        <View className="gap-2">
          <Text className="text-sm font-medium text-zinc-900">Empréstimo</Text>
          <Select
            value={loanId ? String(loanId) : undefined}
            onValueChange={(value) => setLoanId(Number(value))}
            options={loans.map((loan) => ({
              value: String(loan.id),
              label: `${loan.actor?.name ?? `Actor #${loan.actor_id}`} — ${formatCurrency(
                loan.principal_amount
              )} (faltam ${formatCurrency(loan.remaining)})`,
            }))}
            placeholder="Selecione o empréstimo"
          />
        </View>
      ) : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Arquivo PDF</Text>
        <View className="items-center gap-2 rounded-lg border-2 border-dashed border-zinc-300 p-6">
          {selectedFile ? (
            <>
              <FileText size={32} color="#16a34a" />
              <Text className="font-medium text-zinc-900">{selectedFile.name}</Text>
              {selectedFile.size !== null ? (
                <Text className="text-sm text-zinc-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </Text>
              ) : null}
              <View className="flex-row gap-2">
                <Button variant="ghost" size="sm" onPress={() => void handleSelectFile()}>
                  Trocar arquivo
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-11 w-11"
                  accessibilityLabel="Remover arquivo"
                  onPress={() => setSelectedFile(null)}
                >
                  <X size={16} color="#71717a" />
                </Button>
              </View>
            </>
          ) : (
            <>
              <Upload size={32} color="#a1a1aa" />
              <Text className="text-sm text-zinc-500">Selecione o comprovante em PDF</Text>
              <Button variant="outline" size="sm" onPress={() => void handleSelectFile()}>
                Selecionar arquivo
              </Button>
            </>
          )}
        </View>
      </View>

      <View className="flex-row items-center gap-2">
        <Checkbox
          checked={hasPassword}
          onCheckedChange={setHasPassword}
          accessibilityLabel="O PDF tem senha?"
        />
        <Text className="flex-1 text-sm text-zinc-900">O PDF tem senha?</Text>
      </View>

      {hasPassword ? (
        <Input
          label="Senha do PDF"
          placeholder="Digite a senha do PDF"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
      ) : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Modelo de IA</Text>
        <Select value={model} onValueChange={setModel} options={AI_MODEL_OPTIONS} />
      </View>
    </Dialog>
  );
}
