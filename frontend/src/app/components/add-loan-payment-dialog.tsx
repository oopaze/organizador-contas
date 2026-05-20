import React, { useState, useEffect, useRef } from 'react';
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
import { toast } from 'sonner';
import { FileText, Upload, X } from 'lucide-react';
import { createLoanPayment, uploadLoanFile } from '@/services';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  loanId: number | null;
  preselectedFileId?: number;
  onSuccess: () => void;
}

const ACCEPTED_TYPES = 'application/pdf,image/png,image/jpeg,image/jpg,image/webp';

export const AddLoanPaymentDialog: React.FC<Props> = ({
  open,
  onOpenChange,
  loanId,
  preselectedFileId,
  onSuccess,
}) => {
  const [amount, setAmount] = useState('');
  const [paidAt, setPaidAt] = useState(new Date().toISOString().slice(0, 10));
  const [note, setNote] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setAmount('');
    setNote('');
    setPaidAt(new Date().toISOString().slice(0, 10));
    setSelectedFile(null);
  };

  useEffect(() => {
    if (open) reset();
  }, [open]);

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) reset();
    onOpenChange(isOpen);
  };

  const handleFile = (f: File) => {
    const isAccepted =
      f.type === 'application/pdf' ||
      f.type.startsWith('image/');
    if (!isAccepted) {
      toast.error('Use PDF ou imagem (PNG/JPG/WebP)');
      return;
    }
    setSelectedFile(f);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!loanId || !amount || !paidAt) {
      toast.error('Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      let fileId = preselectedFileId;
      if (selectedFile && !fileId) {
        const uploaded = await uploadLoanFile(selectedFile);
        fileId = uploaded.id;
      }

      await createLoanPayment({
        loan_id: loanId,
        amount,
        paid_at: paidAt,
        note,
        file_id: fileId,
      });
      toast.success('Pagamento registrado');
      onSuccess();
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Falha ao salvar pagamento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Adicionar pagamento</DialogTitle>
          <DialogDescription>
            {preselectedFileId
              ? 'Comprovante já enviado — preencha os dados manualmente.'
              : 'Registre um pagamento recebido. Você pode anexar o comprovante (PDF ou imagem).'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="payment-amount">Valor (R$)</Label>
              <Input
                id="payment-amount"
                type="number"
                step="0.01"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-paid-at">Data do pagamento</Label>
              <Input
                id="payment-paid-at"
                type="date"
                value={paidAt}
                onChange={(e) => setPaidAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment-note">Nota</Label>
              <Input
                id="payment-note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>
            {!preselectedFileId && (
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
            )}
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
              {loading ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
