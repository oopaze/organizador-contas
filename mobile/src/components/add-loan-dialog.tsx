import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import FileText from 'lucide-react-native/icons/file-text';
import Upload from 'lucide-react-native/icons/upload';
import X from 'lucide-react-native/icons/x';
import { isPositiveAmount, toDecimalString } from '../lib/amount';
import { toIsoDate } from '../lib/date';
import { pickFile, toUploadFilePart, type PickedFile } from '../lib/pick-file';
import { formatUploadError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { createLoan, getActors, uploadLoanFile, type Actor } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';

/** Mesmos tipos aceitos pelo PWA no comprovante do empréstimo. */
export const LOAN_FILE_MIME_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/webp',
];

interface FormErrors {
  actor?: string;
  principal?: string;
  lentAt?: string;
}

export interface AddLoanDialogProps {
  visible: boolean;
  onClose: () => void;
  /** Chamado após criar com sucesso para a tela reler os dados. */
  onSaved: () => void;
}

export function AddLoanDialog({ visible, onClose, onSaved }: AddLoanDialogProps) {
  const [actors, setActors] = useState<Actor[]>([]);
  const [actorId, setActorId] = useState('');
  const [principal, setPrincipal] = useState('');
  const [lentAt, setLentAt] = useState(toIsoDate(new Date()));
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<PickedFile | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;

    setActorId('');
    setPrincipal('');
    setLentAt(toIsoDate(new Date()));
    setDescription('');
    setSelectedFile(null);
    setErrors({});
    setError(null);
    setSaving(false);

    let cancelled = false;
    getActors()
      .then((list) => {
        if (!cancelled) setActors(list);
      })
      .catch(() => {
        if (!cancelled) {
          setActors([]);
          setError('Falha ao carregar atores');
        }
      });

    return () => {
      cancelled = true;
    };
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
    if (saving) return;

    const nextErrors: FormErrors = {};
    if (!actorId) nextErrors.actor = 'Selecione um ator';
    if (!isPositiveAmount(principal)) nextErrors.principal = 'Informe um valor válido';
    if (!ISO_DATE_PATTERN.test(lentAt)) {
      nextErrors.lentAt = 'Informe uma data válida (AAAA-MM-DD)';
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      let fileId: number | undefined;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', toUploadFilePart(selectedFile) as unknown as Blob);
        const uploaded = await uploadLoanFile(formData);
        fileId = uploaded.id;
      }

      await createLoan({
        actor_id: Number(actorId),
        principal_amount: toDecimalString(principal) as string,
        lent_at: lentAt,
        description: description.trim(),
        file_id: fileId,
      });
      onSaved();
      onClose();
    } catch (submitError) {
      setError(formatUploadError(submitError, 'Falha ao criar empréstimo'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Novo empréstimo"
      description="Registre dinheiro emprestado a alguém. Você pode anexar o comprovante do PIX original."
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={saving}>
            {saving ? 'Salvando...' : 'Criar empréstimo'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Para quem</Text>
        <Select
          value={actorId || undefined}
          onValueChange={setActorId}
          options={actors.map((actor) => ({ value: String(actor.id), label: actor.name }))}
          placeholder="Selecione um ator"
        />
        {errors.actor ? <Text className="text-sm text-red-600">{errors.actor}</Text> : null}
      </View>

      <Input
        label="Valor emprestado (R$)"
        keyboardType="decimal-pad"
        value={principal}
        onChangeText={setPrincipal}
      />
      {errors.principal ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.principal}</Text>
      ) : null}

      <Input
        label="Data do empréstimo"
        placeholder="AAAA-MM-DD"
        value={lentAt}
        onChangeText={setLentAt}
      />
      {errors.lentAt ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.lentAt}</Text>
      ) : null}

      <Input label="Descrição (opcional)" value={description} onChangeText={setDescription} />

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
    </Dialog>
  );
}
