import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Plug, Copy, Check, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { listMCPConnections, revokeMCPConnection, MCPConnection } from '@/services/mcp/mcpConnections';

const MCP_URL = 'https://api.poupix.connectakit.com.br/mcp';

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
            Funciona com qualquer cliente que suporte MCP via HTTP (Claude, ChatGPT, Cursor…).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="text-sm space-y-3 list-decimal list-inside text-muted-foreground">
            <li>
              No seu assistente, abra as configurações de conectores e escolha{' '}
              <strong>adicionar conector personalizado / MCP</strong>.
            </li>
            <li>
              Dê o nome <strong>Poupix</strong> e cole a <strong>URL do MCP</strong> acima.
            </li>
            <li>
              O Poupix vai abrir a tela de autorização — entre na sua conta e clique em{' '}
              <strong>Autorizar</strong>. O acesso é por usuário e você pode revogar quando quiser.
            </li>
            <li>
              Volte ao assistente: as ferramentas de transações, subtransações e projeção já
              aparecem para ele usar.
            </li>
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
