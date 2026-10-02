import { useEffect, useState } from 'react';
import { Share, Text } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import Check from 'lucide-react-native/icons/check';
import Copy from 'lucide-react-native/icons/copy';
import Share2 from 'lucide-react-native/icons/share-2';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { getActorShareToken } from '../services';

/** O web continua dono da página pública; o app só monta o link de produção. */
export const SHARE_ACTOR_URL_BASE = 'https://poupix.connectakit.com.br';

/**
 * O service real devolve o token como string; os testes do plano mockam a
 * resposta crua da API (`{ token }`). Aceita os dois formatos.
 */
function extractShareToken(response: unknown): string {
  if (typeof response === 'string') return response;
  if (response && typeof response === 'object' && 'token' in response) {
    const { token } = response as { token?: unknown };
    if (typeof token === 'string') return token;
  }
  return '';
}

export function buildActorShareUrl(token: string): string {
  return `${SHARE_ACTOR_URL_BASE}/share/actor?token=${token}`;
}

export interface ShareActorDialogProps {
  visible: boolean;
  actorId: number | null;
  actorName?: string;
  onClose: () => void;
}

export function ShareActorDialog({
  visible,
  actorId,
  actorName,
  onClose,
}: ShareActorDialogProps) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible || actorId === null) return;

    let cancelled = false;
    setLoading(true);
    setUrl('');
    setCopied(false);
    setError(null);

    getActorShareToken(actorId)
      .then((response) => {
        if (cancelled) return;
        setUrl(buildActorShareUrl(extractShareToken(response)));
      })
      .catch(() => {
        if (!cancelled) setError('Falha ao gerar link');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [visible, actorId]);

  const handleCopy = async () => {
    if (!url) return;
    setError(null);
    try {
      await Clipboard.setStringAsync(url);
      setCopied(true);
    } catch {
      setError('Não foi possível copiar o link');
    }
  };

  const handleShare = async () => {
    if (!url) return;
    setError(null);
    try {
      await Share.share({ message: url });
    } catch {
      setError('Não foi possível compartilhar o link');
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title={actorName ? `Compartilhar com ${actorName}` : 'Compartilhar link'}
      description={
        actorName
          ? `Envie este link para ${actorName} visualizar gastos e empréstimos.`
          : 'Envie este link para visualizar gastos e empréstimos.'
      }
      footer={
        <>
          <Button
            variant={copied ? 'default' : 'outline'}
            disabled={loading || !url}
            onPress={() => void handleCopy()}
          >
            {copied ? <Check size={16} color="#ffffff" /> : <Copy size={16} color="#18181b" />}
            <Text
              className={
                copied ? 'text-sm font-medium text-white' : 'text-sm font-medium text-zinc-900'
              }
            >
              {copied ? 'Link copiado' : 'Copiar link'}
            </Text>
          </Button>
          <Button disabled={loading || !url} onPress={() => void handleShare()}>
            <Share2 size={16} color="#ffffff" />
            <Text className="text-sm font-medium text-white">Compartilhar</Text>
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <Text
        selectable
        accessibilityLabel="Link de compartilhamento"
        className="rounded-md border border-zinc-300 bg-zinc-50 px-3 py-2 text-sm text-zinc-700"
      >
        {loading ? 'Gerando link…' : url}
      </Text>

      <Text className="text-xs text-zinc-500">
        {copied
          ? '✓ Link copiado! Cole e envie para compartilhar.'
          : 'Copie ou envie o link pelo compartilhamento do aparelho.'}
      </Text>
    </Dialog>
  );
}
