import React, { useState, useRef, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Input } from '@/app/components/ui/input';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { toast } from 'sonner';
import { Upload, FileText, X } from 'lucide-react';
import { Loan, getLoans, uploadPixReceipt } from '@/services';

const AI_MODELS = {
  'deepseek-chat': 'DeepSeek Chat',
  'deepseek-reasoner': 'DeepSeek Reasoner',
  'gemini-2.5-flash-lite': 'Gemini 2.5 Flash Lite',
  'gemini-2.5-pro': 'Gemini 2.5 Pro',
  'gpt-5': 'GPT-5',
  'gpt-5-nano': 'GPT-5 Nano',
  'gpt-5-mini': 'GPT-5 Mini',
} as const;

type AIModelKey = keyof typeof AI_MODELS;

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  preselectedLoanId?: number;
}

export const UploadPixReceiptDialog: React.FC<Props> = ({
  open, onOpenChange, onSuccess, preselectedLoanId,
}) => {
  const [loading, setLoading] = useState(false);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loanId, setLoanId] = useState<number | undefined>(preselectedLoanId);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [hasPassword, setHasPassword] = useState(false);
  const [password, setPassword] = useState('');
  const [model, setModel] = useState<AIModelKey>('gemini-2.5-flash-lite');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      getLoans({ status: 'active' }).then(setLoans).catch(() => toast.error('Falha ao carregar empréstimos'));
      setLoanId(preselectedLoanId);
    }
  }, [open, preselectedLoanId]);

  const reset = () => {
    setSelectedFile(null);
    setHasPassword(false);
    setPassword('');
    setModel('gemini-2.5-flash-lite');
    setLoanId(preselectedLoanId);
  };

  const handleFile = (f: File) => {
    if (f.type === 'application/pdf') setSelectedFile(f);
    else toast.error('Por favor, selecione um arquivo PDF');
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation(); setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return toast.error('Selecione um arquivo PDF');
    if (!loanId) return toast.error('Selecione um empréstimo');

    setLoading(true);
    try {
      const result = await uploadPixReceipt({
        file: selectedFile,
        loanId,
        model,
        password: hasPassword ? password : undefined,
      });
      toast.success(`Pagamento de R$ ${result.payment.amount} registrado`);
      reset();
      onSuccess();
      onOpenChange(false);
    } catch (err: unknown) {
      const data = (err as { response?: { data?: { file_id?: string; error?: string } } })?.response?.data ?? {};
      if (data.file_id) {
        toast.error(`IA não conseguiu extrair: ${data.error}. Adicione manualmente.`);
      } else {
        toast.error(data.error || 'Falha ao processar o comprovante');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) reset(); onOpenChange(v); }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Subir comprovante PIX</DialogTitle>
          <DialogDescription>
            A IA vai extrair valor, data e ID do comprovante e criar o pagamento.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Empréstimo</Label>
              <Select value={loanId ? String(loanId) : ''} onValueChange={(v) => setLoanId(Number(v))}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o empréstimo" />
                </SelectTrigger>
                <SelectContent>
                  {loans.map((l) => (
                    <SelectItem key={l.id} value={String(l.id)}>
                      Actor #{l.actor_id} — R$ {l.principal_amount} (faltam R$ {l.remaining})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Arquivo PDF</Label>
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-200 ${
                  dragActive ? 'border-indigo-500 bg-indigo-50' :
                  selectedFile ? 'bg-green-50 border-green-300' : 'border-gray-300 hover:border-gray-400'
                }`}
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
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                />
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="w-8 h-8 text-green-600" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <Upload className="w-10 h-10 text-gray-400" />
                    <p className="text-gray-600">Arraste e solte seu PDF aqui</p>
                    <p className="text-sm text-gray-400">ou clique para selecionar</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="hasPwd"
                checked={hasPassword}
                onCheckedChange={(v) => setHasPassword(v === true)}
              />
              <Label htmlFor="hasPwd" className="cursor-pointer">O PDF tem senha?</Label>
            </div>

            {hasPassword && (
              <div className="space-y-2">
                <Label htmlFor="pdfPassword">Senha do PDF</Label>
                <Input
                  id="pdfPassword"
                  placeholder="Digite a senha do PDF"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label>Modelo de IA</Label>
              <Select value={model} onValueChange={(v) => setModel(v as AIModelKey)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {Object.entries(AI_MODELS).map(([k, name]) => (
                    <SelectItem key={k} value={k}>{name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => { reset(); onOpenChange(false); }}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading || !selectedFile || !loanId}>
              {loading ? 'Enviando...' : 'Enviar comprovante'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
