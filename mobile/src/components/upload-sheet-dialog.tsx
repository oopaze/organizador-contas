import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import FileSpreadsheet from 'lucide-react-native/icons/file-spreadsheet';
import Upload from 'lucide-react-native/icons/upload';
import X from 'lucide-react-native/icons/x';
import { AI_MODEL_OPTIONS, DEFAULT_AI_MODEL } from '../lib/ai-models';
import { pickFile, toUploadFilePart, type PickedFile } from '../lib/pick-file';
import { formatUploadError } from '../lib/transaction-form';
import { uploadSheet } from '../services';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Select } from './ui/select';
import { Textarea } from './ui/textarea';

const ACCEPTED_EXTENSIONS = ['.csv', '.xlsx', '.xls'];
const SHEET_MIME_TYPES = [
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

export interface UploadSheetDialogProps {
  visible: boolean;
  onClose: () => void;
  onUploaded: () => void;
}

export function UploadSheetDialog({ visible, onClose, onUploaded }: UploadSheetDialogProps) {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<PickedFile | null>(null);
  const [selectedModel, setSelectedModel] = useState(DEFAULT_AI_MODEL);
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible) return;
    setLoading(false);
    setSelectedFile(null);
    setSelectedModel(DEFAULT_AI_MODEL);
    setDescription('');
    setError(null);
  }, [visible]);

  const handleSelectFile = async () => {
    setError(null);
    try {
      const file = await pickFile(SHEET_MIME_TYPES);
      if (!file) return;
      const name = file.name.toLowerCase();
      if (!ACCEPTED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
        setError('Por favor, selecione um arquivo CSV ou Excel (.xlsx, .xls)');
        return;
      }
      setSelectedFile(file);
    } catch {
      setError('Não foi possível abrir o seletor de arquivos');
    }
  };

  const handleSubmit = async () => {
    if (loading || !selectedFile) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', toUploadFilePart(selectedFile) as unknown as Blob);
      formData.append('model', selectedModel);
      if (description.trim()) {
        formData.append('user_provided_description', description.trim());
      }

      await uploadSheet(formData);
      onUploaded();
    } catch (submitError) {
      setError(formatUploadError(submitError, 'Falha ao enviar planilha'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={loading ? () => {} : onClose}
      title="Upload de Planilha"
      description="Faça upload de uma planilha CSV ou Excel com suas transações"
      footer={
        <>
          <Button variant="outline" onPress={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button onPress={() => void handleSubmit()} disabled={loading || !selectedFile}>
            {loading ? 'Enviando...' : 'Enviar Planilha'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Arquivo (CSV, Excel)</Text>
        <View className="items-center gap-2 rounded-lg border-2 border-dashed border-zinc-300 p-6">
          {selectedFile ? (
            <>
              <FileSpreadsheet size={32} color="#16a34a" />
              <Text className="font-medium text-zinc-900">{selectedFile.name}</Text>
              {selectedFile.size !== null ? (
                <Text className="text-sm text-zinc-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
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
              <Text className="text-sm text-zinc-500">CSV, Excel (.xlsx, .xls)</Text>
              <Button variant="outline" size="sm" onPress={() => void handleSelectFile()}>
                Selecionar arquivo
              </Button>
            </>
          )}
        </View>
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Modelo de IA</Text>
        <Select value={selectedModel} onValueChange={setSelectedModel} options={AI_MODEL_OPTIONS} />
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Descrição (opcional)</Text>
        <Textarea
          accessibilityLabel="Descrição (opcional)"
          placeholder="Ex: Planilha de gastos do mês de janeiro, valores em reais"
          value={description}
          onChangeText={setDescription}
        />
        <Text className="text-xs text-zinc-500">
          Adicione contexto sobre a planilha para ajudar a IA a interpretar os dados
        </Text>
      </View>
    </Dialog>
  );
}
