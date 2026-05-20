import React, { useEffect, useRef, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Input } from '@/app/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { toast } from 'sonner';
import { FileText, Upload, X } from 'lucide-react';
import { Actor, getActors, createLoan, uploadLoanFile } from '@/services';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

const ACCEPTED_TYPES = 'application/pdf,image/png,image/jpeg,image/jpg,image/webp';

export const AddLoanDialog: React.FC<Props> = ({ open, onOpenChange, onSuccess }) => {
  const [actors, setActors] = useState<Actor[]>([]);
  const [actorId, setActorId] = useState<number | ''>('');
  const [principal, setPrincipal] = useState('');
  const [lentAt, setLentAt] = useState(new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      getActors().then(setActors).catch(() => toast.error('Falha ao carregar atores'));
    }
  }, [open]);

  const reset = () => {
    setActorId('');
    setPrincipal('');
    setDescription('');
    setLentAt(new Date().toISOString().slice(0, 10));
    setSelectedFile(null);
  };

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) reset();
    onOpenChange(isOpen);
  };

  const handleFile = (f: File) => {
    const isAccepted = f.type === 'application/pdf' || f.type.startsWith('image/');
    if (!isAccepted) {
      toast.error('Use PDF ou imagem (PNG/JPG/WebP)');
      return;
    }
    setSelectedFile(f);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!actorId || !principal || !lentAt) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      let fileId: number | undefined;
      if (selectedFile) {
        const uploaded = await uploadLoanFile(selectedFile);
        fileId = uploaded.id;
      }

      await createLoan({
        actor_id: Number(actorId),
        principal_amount: principal,
        lent_at: lentAt,
        description,
        file_id: fileId,
      });
      toast.success('Empréstimo criado');
      reset();
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Falha ao criar empréstimo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Novo empréstimo</DialogTitle>
          <DialogDescription>
            Registre dinheiro emprestado a alguém. Você pode anexar o comprovante do PIX original.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="loan-actor">Para quem</Label>
              <Select
                value={actorId ? String(actorId) : ''}
                onValueChange={(v) => setActorId(Number(v))}
              >
                <SelectTrigger id="loan-actor">
                  <SelectValue placeholder="Selecione um ator" />
                </SelectTrigger>
                <SelectContent>
                  {actors.map((a) => (
                    <SelectItem key={a.id} value={String(a.id)}>
                      {a.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-principal">Valor emprestado (R$)</Label>
              <Input
                id="loan-principal"
                type="number"
                step="0.01"
                min="0"
                value={principal}
                onChange={(e) => setPrincipal(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-lent-at">Data do empréstimo</Label>
              <Input
                id="loan-lent-at"
                type="date"
                value={lentAt}
                onChange={(e) => setLentAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loan-description">Descrição (opcional)</Label>
              <Input
                id="loan-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Comprovante (opcional)</Label>
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_TYPES}
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
              {selectedFile ? (
                <div className="flex items-center justify-between gap-2 rounded-md border p-2 bg-gray-50 min-w-0">
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
                    <span className="text-sm truncate block min-w-0" title={selectedFile.name}>
                      {selectedFile.name}
                    </span>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="shrink-0"
                    onClick={() => setSelectedFile(null)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="w-4 h-4 mr-2" /> Anexar PDF ou imagem
                </Button>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Criar empréstimo'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
