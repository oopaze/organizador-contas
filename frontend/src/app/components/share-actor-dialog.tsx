import React, { useEffect, useRef, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Check, Copy } from 'lucide-react';
import { toast } from 'sonner';
import { getActorShareToken } from '@/services/actors/getActorShareToken';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  actorId: number | null;
  actorName: string;
}

async function copyToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // fall through to legacy
    }
  }
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    return document.execCommand('copy');
  } catch {
    return false;
  } finally {
    document.body.removeChild(ta);
  }
}

export const ShareActorDialog: React.FC<Props> = ({ open, onOpenChange, actorId, actorName }) => {
  const [shareUrl, setShareUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open || !actorId) return;
    let cancelled = false;
    setLoading(true);
    setIsCopied(false);
    setShareUrl('');
    getActorShareToken(actorId)
      .then(async (token) => {
        if (cancelled) return;
        const url = `${window.location.origin}/share/actor?token=${token}`;
        setShareUrl(url);
        const copied = await copyToClipboard(url);
        if (!cancelled && copied) {
          setIsCopied(true);
          toast.success('Link copiado!');
        }
      })
      .catch(() => {
        if (!cancelled) toast.error('Falha ao gerar link');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, actorId]);

  const handleCopy = async () => {
    if (!shareUrl) return;
    const copied = await copyToClipboard(shareUrl);
    if (copied) {
      setIsCopied(true);
      toast.success('Link copiado!');
    } else {
      inputRef.current?.select();
      toast.info('Selecione e copie manualmente');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Compartilhar com {actorName}</DialogTitle>
          <DialogDescription>
            Envie este link para {actorName} visualizar gastos e empréstimos.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Input
              ref={inputRef}
              value={loading ? 'Gerando link…' : shareUrl}
              readOnly
              className="flex-1 text-sm"
              onClick={() => inputRef.current?.select()}
            />
            <Button
              type="button"
              size="icon"
              variant={isCopied ? 'default' : 'outline'}
              onClick={handleCopy}
              disabled={loading || !shareUrl}
              className="shrink-0"
            >
              {isCopied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            {isCopied
              ? '✓ Link copiado! Cole e envie para compartilhar.'
              : 'Toque no link acima para selecionar, depois copie manualmente.'}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};
