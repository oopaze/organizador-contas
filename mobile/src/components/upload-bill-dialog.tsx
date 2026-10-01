import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import FileText from 'lucide-react-native/icons/file-text';
import Upload from 'lucide-react-native/icons/upload';
import X from 'lucide-react-native/icons/x';
import { AI_MODEL_OPTIONS, DEFAULT_AI_MODEL } from '../lib/ai-models';
import { pickFile, toUploadFilePart, type PickedFile } from '../lib/pick-file';
import { formatSubmitError, formatUploadError } from '../lib/transaction-form';
import { createCard, getCards, uploadBill, type Card } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';

export interface UploadBillDialogProps {
  visible: boolean;
  onClose: () => void;
  onUploaded: (transactionIds: number[]) => void;
}

export function UploadBillDialog({ visible, onClose, onUploaded }: UploadBillDialogProps) {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<PickedFile | null>(null);
  const [hasPassword, setHasPassword] = useState(false);
  const [pdfPassword, setPdfPassword] = useState('');
  const [selectedModel, setSelectedModel] = useState(DEFAULT_AI_MODEL);
  const [createInFutureMonths, setCreateInFutureMonths] = useState(false);
  const [cards, setCards] = useState<Card[]>([]);
  const [cardId, setCardId] = useState('none');
  const [cardTouched, setCardTouched] = useState(false);
  const [creatingCard, setCreatingCard] = useState(false);
  const [newCardName, setNewCardName] = useState('');
  const [newCardDueDay, setNewCardDueDay] = useState('1');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible) return;

    setLoading(false);
    setSelectedFile(null);
    setHasPassword(false);
    setPdfPassword('');
    setSelectedModel(DEFAULT_AI_MODEL);
    setCreateInFutureMonths(false);
    setCardId('none');
    setCardTouched(false);
    setCreatingCard(false);
    setNewCardName('');
    setNewCardDueDay('1');
    setError(null);

    let cancelled = false;
    getCards()
      .then((list) => {
        if (!cancelled) setCards(list);
      })
      .catch(() => {
        if (!cancelled) setCards([]);
      });
    return () => {
      cancelled = true;
    };
  }, [visible]);

  useEffect(() => {
    if (!selectedFile || cards.length === 0 || cardId !== 'none' || cardTouched) return;
    const fileName = selectedFile.name.toLowerCase();
    const match = cards
      .filter((card) => card.is_active)
      .find((card) => fileName.includes(card.name.toLowerCase()));
    if (match) setCardId(String(match.id));
  }, [selectedFile, cards, cardId, cardTouched]);

  const handleSelectFile = async () => {
    setError(null);
    try {
      const file = await pickFile(['application/pdf']);
      if (file) setSelectedFile(file);
    } catch {
      setError('Não foi possível abrir o seletor de arquivos');
    }
  };

  const handleCreateCard = async () => {
    if (!newCardName.trim()) return;
    setError(null);
    try {
      const created = await createCard({
        name: newCardName.trim(),
        due_day: Math.min(31, Math.max(1, parseInt(newCardDueDay, 10) || 1)),
      });
      setCards((current) => [...current, created]);
      setCardId(String(created.id));
      setCardTouched(true);
      setCreatingCard(false);
      setNewCardName('');
      setNewCardDueDay('1');
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao criar o cartão'));
    }
  };

  const handleClose = () => {
    if (loading) return;
    onClose();
  };

  const handleSubmit = async () => {
    if (loading || !selectedFile) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', toUploadFilePart(selectedFile) as unknown as Blob);
      if (hasPassword && pdfPassword) formData.append('password', pdfPassword);
      formData.append('model', selectedModel);
      if (createInFutureMonths) formData.append('create_in_future_months', 'true');
      if (cardId !== 'none' && cardId !== '__new__') formData.append('card_id', cardId);

      const result = await uploadBill(formData);
      onUploaded(result?.transaction_ids ?? []);
    } catch (submitError) {
      setError(
        formatUploadError(
          submitError,
          'Falha ao enviar fatura. Verifique se a senha está correta.'
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={handleClose}
      title="Upload de Fatura"
      description="Faça upload da sua fatura de cartão de crédito em PDF"
      footer={
        <>
          <Button variant="outline" onPress={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={loading || !selectedFile}>
            {loading ? 'Enviando...' : 'Enviar Fatura'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

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
              <Text className="text-sm text-zinc-500">Selecione o PDF da sua fatura</Text>
              <Button variant="outline" size="sm" onPress={() => void handleSelectFile()}>
                Selecionar arquivo
              </Button>
            </>
          )}
        </View>
      </View>

      <View className="flex-row items-center gap-2">
        <Checkbox
          checked={createInFutureMonths}
          onCheckedChange={setCreateInFutureMonths}
          accessibilityLabel="Criar transações também nos meses futuros?"
        />
        <Text className="flex-1 text-sm text-zinc-900">
          Criar transações também nos meses futuros?
        </Text>
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Cartão</Text>
        <Select
          value={cardId}
          onValueChange={(value) => {
            setCardTouched(true);
            if (value === '__new__') {
              setCreatingCard(true);
              setNewCardName(selectedFile?.name?.replace(/\.pdf$/i, '') ?? '');
              setNewCardDueDay('1');
            } else {
              setCardId(value);
            }
          }}
          options={[
            { value: 'none', label: 'Sem cartão' },
            ...cards
              .filter((card) => card.is_active)
              .map((card) => ({
                value: String(card.id),
                label: `${card.name} (vence dia ${card.due_day})`,
              })),
            { value: '__new__', label: '+ novo cartão' },
          ]}
        />
      </View>

      {creatingCard ? (
        <View className="gap-3 rounded-md border border-zinc-200 p-3">
          <Input
            label="Nome do cartão"
            value={newCardName}
            onChangeText={setNewCardName}
          />
          <Input
            label="Dia de vencimento"
            keyboardType="number-pad"
            value={newCardDueDay}
            onChangeText={setNewCardDueDay}
          />
          <View className="flex-row justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              disabled={loading}
              onPress={() => {
                setCreatingCard(false);
                setCardTouched(false);
              }}
            >
              Cancelar
            </Button>
            <Button
              size="sm"
              disabled={!newCardName.trim() || loading}
              onPress={() => void handleCreateCard()}
            >
              Criar cartão
            </Button>
          </View>
        </View>
      ) : null}

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
          value={pdfPassword}
          onChangeText={setPdfPassword}
        />
      ) : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Modelo de IA</Text>
        <Select value={selectedModel} onValueChange={setSelectedModel} options={AI_MODEL_OPTIONS} />
      </View>
    </Dialog>
  );
}
