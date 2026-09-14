import React, { useState, useRef, useEffect } from 'react';
import { uploadBill, getCards, createCard, Card } from '@/services';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Input } from '@/app/components/ui/input';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';

import { toast } from 'sonner';
import { Upload, FileText, X } from 'lucide-react';

const AI_MODELS = {
  'deepseek-chat': { name: 'DeepSeek Chat', provider: 'DeepSeek' },
  'deepseek-reasoner': { name: 'DeepSeek Reasoner', provider: 'DeepSeek' },
  'gemini-2.5-flash-lite': { name: 'Gemini 2.5 Flash Lite', provider: 'Google' },
  'gemini-2.5-pro': { name: 'Gemini 2.5 Pro', provider: 'Google' },
  'gpt-5': { name: 'GPT-5', provider: 'OpenAI' },
  'gpt-5-nano': { name: 'GPT-5 Nano', provider: 'OpenAI' },
  'gpt-5-mini': { name: 'GPT-5 Mini', provider: 'OpenAI' },
} as const;

type AIModelKey = keyof typeof AI_MODELS;

interface UploadBillDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: (transactionIds: number[]) => void;
}

export const UploadBillDialog: React.FC<UploadBillDialogProps> = ({
  open,
  onOpenChange,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [hasPassword, setHasPassword] = useState(false);
  const [pdfPassword, setPdfPassword] = useState('');
  const [selectedModel, setSelectedModel] = useState<AIModelKey>('gemini-2.5-flash-lite');
  const [createInFutureMonths, setCreateInFutureMonths] = useState(false);
  const [cards, setCards] = useState<Card[]>([]);
  const [cardId, setCardId] = useState('none');
  const [creatingCard, setCreatingCard] = useState(false);
  const [newCardName, setNewCardName] = useState('');
  const [newCardDueDay, setNewCardDueDay] = useState('1');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    getCards().then(setCards).catch(() => setCards([]));
  }, [open]);

  useEffect(() => {
    if (!selectedFile || cards.length === 0) return;
    const fileName = selectedFile.name.toLowerCase();
    const match = cards.find((card) => fileName.includes(card.name.toLowerCase()));
    if (match) setCardId(String(match.id));
  }, [selectedFile, cards]);

  const handleCreateCard = async () => {
    try {
      const created = await createCard({
        name: newCardName.trim(),
        due_day: Math.min(31, Math.max(1, parseInt(newCardDueDay, 10) || 1)),
      });
      setCards((current) => [...current, created]);
      setCardId(String(created.id));
      setCreatingCard(false);
      setNewCardName('');
      toast.success('Cartão adicionado!');
    } catch {
      toast.error('Falha ao criar o cartão');
    }
  };

  const handleFileSelect = (file: File) => {
    if (file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      toast.error('Por favor, selecione um arquivo PDF');
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error('Por favor, selecione um arquivo');
      return;
    }

    setLoading(true);
    const password = hasPassword ? pdfPassword : undefined;
    await uploadBill(
      selectedFile,
      password,
      selectedModel,
      createInFutureMonths,
      cardId === 'none' || cardId === '__new__' ? undefined : Number(cardId)
    ).then((result) => {
      toast.success('Fatura enviada com sucesso!');
      setSelectedFile(null);
      setHasPassword(false);
      setPdfPassword('');
      setSelectedModel('gemini-2.5-flash-lite');
      setCreateInFutureMonths(false);
      onSuccess(result?.transaction_ids || []);
    }).catch((error) => {
      toast.error(error?.response?.data?.error || 'Falha ao enviar fatura. Verifique se a senha está correta.');
    }).finally(() => {
      setLoading(false);
    });
  };

  const handleClose = (isOpen: boolean) => {
    if (!isOpen) {
      setSelectedFile(null);
      setHasPassword(false);
      setPdfPassword('');
      setSelectedModel('gemini-2.5-flash-lite');
      setCreateInFutureMonths(false);
    }
    onOpenChange(isOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload de Fatura</DialogTitle>
          <DialogDescription>
            Faça upload da sua fatura de cartão de crédito em PDF
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Arquivo PDF</Label>
              <div
                className={`
                  border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
                  transition-colors duration-200
                  ${dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'}
                  ${selectedFile ? 'bg-green-50 border-green-300' : ''}
                `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleInputChange}
                  className="hidden"
                />
                
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="w-8 h-8 text-green-600" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <Upload className="w-10 h-10 text-gray-400" />
                    <p className="text-gray-600">
                      Arraste e solte seu arquivo PDF aqui
                    </p>
                    <p className="text-sm text-gray-400">
                      ou clique para selecionar
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="createInFutureMonths"
                checked={createInFutureMonths}
                onCheckedChange={(checked) => setCreateInFutureMonths(checked === true)}
              />
              <Label htmlFor="createInFutureMonths" className="cursor-pointer">
                Criar transações também nos meses futuros?
              </Label>
            </div>

            <div className="space-y-2">
              <Label>Cartão</Label>
              <Select
                value={cardId}
                onValueChange={(value) => {
                  if (value === '__new__') {
                    setCreatingCard(true);
                    setNewCardName(selectedFile?.name?.replace(/\.pdf$/i, '') ?? '');
                    setNewCardDueDay('1');
                  } else {
                    setCardId(value);
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o cartão" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Sem cartão</SelectItem>
                  {cards.filter((card) => card.is_active).map((card) => (
                    <SelectItem key={card.id} value={String(card.id)}>
                      {card.name} (vence dia {card.due_day})
                    </SelectItem>
                  ))}
                  <SelectItem value="__new__">+ novo cartão</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {creatingCard && (
              <div className="space-y-3 rounded-md border p-3">
                <div className="space-y-2">
                  <Label htmlFor="new-card-name">Nome do cartão</Label>
                  <Input id="new-card-name" value={newCardName} onChange={(e) => setNewCardName(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-card-due">Dia de vencimento</Label>
                  <Input
                    id="new-card-due"
                    type="number"
                    min="1"
                    max="31"
                    value={newCardDueDay}
                    onChange={(e) => setNewCardDueDay(e.target.value)}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="ghost" size="sm" onClick={() => setCreatingCard(false)}>
                    Cancelar
                  </Button>
                  <Button type="button" size="sm" onClick={handleCreateCard} disabled={!newCardName.trim()}>
                    Criar cartão
                  </Button>
                </div>
              </div>
            )}

            <div className="flex items-center space-x-2">
              <Checkbox
                id="hasPassword"
                checked={hasPassword}
                onCheckedChange={(checked) => setHasPassword(checked === true)}
              />
              <Label htmlFor="hasPassword" className="cursor-pointer">
                O PDF tem senha?
              </Label>
            </div>

            {hasPassword && (
              <div className="space-y-2">
                <Label htmlFor="pdfPassword">Senha do PDF</Label>
                <Input
                  id="pdfPassword"
                  placeholder="Digite a senha do PDF"
                  value={pdfPassword}
                  onChange={(e) => setPdfPassword(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label>Modelo de IA</Label>
              <Select value={selectedModel} onValueChange={(value) => setSelectedModel(value as AIModelKey)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o modelo" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(AI_MODELS).map(([key, { name }]) => (
                    <SelectItem key={key} value={key}>{name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => handleClose(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading || !selectedFile}>
              {loading ? 'Enviando...' : 'Enviar Fatura'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

