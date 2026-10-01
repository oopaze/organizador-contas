import { useCallback, useEffect, useRef, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import type { LucideIcon } from 'lucide-react-native';
import Check from 'lucide-react-native/icons/check';
import Copy from 'lucide-react-native/icons/copy';
import Link2 from 'lucide-react-native/icons/link-2';
import Plug from 'lucide-react-native/icons/plug';
import Settings from 'lucide-react-native/icons/settings';
import ShieldCheck from 'lucide-react-native/icons/shield-check';
import Sparkles from 'lucide-react-native/icons/sparkles';
import Trash from 'lucide-react-native/icons/trash';
import { InlineMessage } from '../src/components/inline-message';
import { AlertDialog } from '../src/components/ui/alert-dialog';
import { Badge } from '../src/components/ui/badge';
import { Button } from '../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../src/components/ui/card';
import { Skeleton } from '../src/components/ui/skeleton';
import { formatUploadError } from '../src/lib/transaction-form';
import { API_BASE_URL } from '../src/services/client';
import {
  listMCPConnections,
  revokeMCPConnection,
  type MCPConnection,
} from '../src/services/mcp/mcpConnections';

/** Mesma URL do PWA, derivada da base da API para builds apontados a outro backend. */
const MCP_URL = `${API_BASE_URL}/mcp`;

interface SetupStep {
  icon: LucideIcon;
  title: string;
  description: string;
}

const SETUP_STEPS: SetupStep[] = [
  {
    icon: Settings,
    title: 'Abra os conectores do seu assistente',
    description:
      'Claude, ChatGPT, Cursor… em Configurações → Conectores, escolha adicionar conector personalizado / MCP.',
  },
  {
    icon: Link2,
    title: 'Cole a URL do MCP',
    description: 'Dê o nome Poupix e cole a URL abaixo no campo de endereço do servidor.',
  },
  {
    icon: ShieldCheck,
    title: 'Autorize o acesso',
    description:
      'O Poupix abre a tela de consentimento: entre na sua conta e clique em Autorizar.',
  },
  {
    icon: Sparkles,
    title: 'Pronto para conversar',
    description:
      'As ferramentas de transações, subtransações e projeção já ficam disponíveis no assistente.',
  },
];

export default function IntegrationsScreen() {
  const [connections, setConnections] = useState<MCPConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);
  const [revokingId, setRevokingId] = useState<string | null>(null);
  const [revokeError, setRevokeError] = useState<string | null>(null);
  const [revokeTarget, setRevokeTarget] = useState<MCPConnection | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (copyTimer.current) clearTimeout(copyTimer.current);
    };
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      setConnections(await listMCPConnections());
    } catch (error) {
      setLoadError(formatUploadError(error, 'Falha ao carregar conexões'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleCopy = async () => {
    setCopyError(null);
    try {
      await Clipboard.setStringAsync(MCP_URL);
      setCopied(true);
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopyError('Não foi possível copiar a URL');
    }
  };

  const handleConfirmRevoke = async () => {
    const target = revokeTarget;
    setRevokeTarget(null);
    if (!target) return;

    setRevokingId(target.client_id);
    setRevokeError(null);
    try {
      await revokeMCPConnection(target.client_id);
      await refresh();
    } catch (error) {
      setRevokeError(formatUploadError(error, 'Falha ao revogar acesso'));
    } finally {
      setRevokingId(null);
    }
  };

  return (
    <ScrollView className="flex-1 bg-zinc-50" contentContainerClassName="gap-6 p-4 pb-24">
      <View className="flex-row items-center gap-3">
        <Plug size={32} color="#059669" />
        <Text className="min-w-0 flex-1 text-sm text-zinc-500">
          Conecte seu assistente de IA ao Poupix via MCP.
        </Text>
      </View>

      <Card>
        <CardHeader>
          <CardTitle>URL do MCP</CardTitle>
          <CardDescription>
            É só esse link. Cole no seu assistente na opção de adicionar um conector MCP.
          </CardDescription>
        </CardHeader>
        <CardContent className="gap-3">
          {copyError ? <InlineMessage>{copyError}</InlineMessage> : null}
          <View className="flex-row items-center gap-2">
            <Text
              selectable
              accessibilityLabel="URL do MCP"
              className="min-w-0 flex-1 rounded-md border border-zinc-300 bg-zinc-100 px-3 py-2 font-mono text-xs text-zinc-700"
            >
              {MCP_URL}
            </Text>
            <Button size="sm" className="shrink-0" onPress={() => void handleCopy()}>
              {copied ? <Check size={16} color="#ffffff" /> : <Copy size={16} color="#ffffff" />}
              <Text className="text-sm font-medium text-white">
                {copied ? 'Copiado!' : 'Copiar'}
              </Text>
            </Button>
          </View>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Como configurar</CardTitle>
          <CardDescription>Funciona com qualquer cliente que suporte MCP via HTTP.</CardDescription>
        </CardHeader>
        <CardContent>
          <View className="gap-6">
            {SETUP_STEPS.map((step, index) => (
              <View key={step.title} className="flex-row gap-4">
                <View className="h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600">
                  <Text className="text-sm font-semibold text-white">{index + 1}</Text>
                </View>
                <View className="min-w-0 flex-1 gap-1.5">
                  <View className="flex-row items-center gap-2">
                    <step.icon size={16} color="#059669" />
                    <Text className="shrink text-sm font-medium text-zinc-900">{step.title}</Text>
                  </View>
                  <Text className="text-sm text-zinc-500">{step.description}</Text>
                  {index === 1 ? (
                    <Text
                      selectable
                      className="mt-1 rounded-md bg-zinc-100 px-3 py-2 font-mono text-xs text-zinc-800"
                    >
                      {MCP_URL}
                    </Text>
                  ) : null}
                </View>
              </View>
            ))}
          </View>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <View className="flex-row items-center gap-2">
            <Plug size={20} color="#18181b" />
            <CardTitle>Conexões ativas</CardTitle>
          </View>
          <CardDescription>Aplicativos com acesso autorizado aos seus dados.</CardDescription>
        </CardHeader>
        <CardContent className="gap-3">
          {loadError ? (
            <View className="gap-3">
              <InlineMessage>{loadError}</InlineMessage>
              <Button
                variant="outline"
                size="sm"
                className="self-start"
                onPress={() => void refresh()}
              >
                Tentar novamente
              </Button>
            </View>
          ) : null}
          {revokeError ? <InlineMessage>{revokeError}</InlineMessage> : null}

          {loading ? (
            <View className="gap-3">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </View>
          ) : connections.length === 0 ? (
            <Text className="py-4 text-center text-sm text-zinc-500">
              Nenhuma conexão ativa ainda.
            </Text>
          ) : (
            <View className="gap-3">
              {connections.map((connection) => (
                <View
                  key={connection.client_id}
                  className="gap-3 rounded-lg border border-zinc-200 p-4"
                >
                  <View className="min-w-0 flex-1 gap-1">
                    <View className="flex-row flex-wrap items-center gap-2">
                      <Text className="text-base font-medium text-zinc-900">{connection.name}</Text>
                      <Badge variant="outline" className="border-green-200">
                        <Text className="text-xs text-green-600">Ativo</Text>
                      </Badge>
                    </View>
                    <Text className="font-mono text-xs text-zinc-500">{connection.client_id}</Text>
                  </View>
                  <Button
                    variant="outline"
                    size="sm"
                    className="self-start border-red-200"
                    disabled={revokingId === connection.client_id}
                    onPress={() => {
                      setRevokeError(null);
                      setRevokeTarget(connection);
                    }}
                  >
                    <Trash size={16} color="#dc2626" />
                    <Text className="text-sm font-medium text-red-600">
                      {revokingId === connection.client_id ? 'Revogando…' : 'Revogar'}
                    </Text>
                  </Button>
                </View>
              ))}
            </View>
          )}
        </CardContent>
      </Card>

      <AlertDialog
        visible={revokeTarget !== null}
        onConfirm={() => void handleConfirmRevoke()}
        onCancel={() => setRevokeTarget(null)}
        title="Revogar acesso"
        description="Revogar acesso desse aplicativo?"
        destructive
      />
    </ScrollView>
  );
}
