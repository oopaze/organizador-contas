import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Plug, Copy, Check, Trash2, Settings, Link2, ShieldCheck, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { listMCPConnections, revokeMCPConnection, MCPConnection } from '@/services/mcp/mcpConnections';

const MCP_URL = 'https://api.poupix.connectakit.com.br/mcp';

const SETUP_STEPS = [
  {
    icon: Settings,
    title: 'Abra os conectores do seu assistente',
    description: 'Claude, ChatGPT, Cursor… em Configurações → Conectores, escolha adicionar conector personalizado / MCP.',
  },
  {
    icon: Link2,
    title: 'Cole a URL do MCP',
    description: 'Dê o nome Poupix e cole a URL abaixo no campo de endereço do servidor.',
  },
  {
    icon: ShieldCheck,
    title: 'Autorize o acesso',
    description: 'O Poupix abre a tela de consentimento: entre na sua conta e clique em Autorizar.',
  },
  {
    icon: Sparkles,
    title: 'Pronto para conversar',
    description: 'As ferramentas de transações, subtransações e projeção já ficam disponíveis no assistente.',
  },
];

export const IntegrationsPage: React.FC = () => {
  const [connections, setConnections] = useState<MCPConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      setConnections(await listMCPConnections());
    } catch {
      toast.error('Falha ao carregar conexões');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleRevoke(clientId: string) {
    if (!confirm('Revogar acesso desse aplicativo?')) return;
    setRevokingId(clientId);
    try {
      await revokeMCPConnection(clientId);
      toast.success('Acesso revogado com sucesso');
      await refresh();
    } catch {
      toast.error('Falha ao revogar acesso');
    } finally {
      setRevokingId(null);
    }
  }

  function copyUrl() {
    navigator.clipboard.writeText(MCP_URL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Plug className="h-8 w-8 text-emerald-600" />
        <div>
          <h1 className="text-2xl font-semibold">Conectores</h1>
          <p className="text-muted-foreground">
            Conecte seu assistente de IA ao Poupix via MCP.
          </p>
        </div>
      </div>

      {/* MCP URL */}
      <Card>
        <CardHeader>
          <CardTitle>URL do MCP</CardTitle>
          <CardDescription>
            É só esse link. Cole no seu assistente na opção de adicionar um conector MCP.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              readOnly
              value={MCP_URL}
              onFocus={(e) => e.target.select()}
              className="flex-1 min-w-0 px-3 py-2 border rounded-md font-mono text-xs bg-muted"
            />
            <Button size="sm" onClick={copyUrl} className="gap-2 shrink-0">
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  Copiado!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copiar
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* How to configure */}
      <Card>
        <CardHeader>
          <CardTitle>Como configurar</CardTitle>
          <CardDescription>
            Funciona com qualquer cliente que suporte MCP via HTTP.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="relative space-y-6 before:absolute before:left-4 before:top-2 before:bottom-2 before:w-px before:bg-border">
            {SETUP_STEPS.map((step, index) => (
              <li key={step.title} className="relative flex gap-4">
                <div className="z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-sm font-semibold text-white">
                  {index + 1}
                </div>
                <div className="min-w-0 flex-1 space-y-1.5 pt-0.5">
                  <div className="flex items-center gap-2 text-sm font-medium text-gray-900">
                    <step.icon className="h-4 w-4 shrink-0 text-emerald-600" />
                    {step.title}
                  </div>
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                  {index === 1 && (
                    <div className="pt-1">
                      <code className="block break-all rounded-md bg-muted px-3 py-2 font-mono text-xs text-gray-800">
                        {MCP_URL}
                      </code>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {/* Active Connections */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Plug className="h-5 w-5" />
            <CardTitle>Conexões ativas</CardTitle>
          </div>
          <CardDescription>Aplicativos com acesso autorizado aos seus dados.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && (
            <div className="space-y-3">
              {[1, 2].map(i => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          )}
          {!loading && connections.length === 0 && (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Nenhuma conexão ativa ainda.
            </p>
          )}
          {!loading && connections.length > 0 && (
            <div className="space-y-3">
              {connections.map(c => (
                <div
                  key={c.client_id}
                  className="flex flex-col gap-3 border rounded-lg p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium">{c.name}</span>
                      <Badge variant="outline" className="text-xs text-green-600 border-green-200">
                        Ativo
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground font-mono break-all">{c.client_id}</div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2 text-destructive hover:text-destructive border-destructive/30 hover:border-destructive w-full sm:w-auto sm:shrink-0"
                    onClick={() => handleRevoke(c.client_id)}
                    disabled={revokingId === c.client_id}
                  >
                    <Trash2 className="w-4 h-4" />
                    {revokingId === c.client_id ? 'Revogando…' : 'Revogar'}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
