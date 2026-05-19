import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { Plug, Copy, Check, ExternalLink, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { listMCPConnections, revokeMCPConnection, MCPConnection } from '@/services/mcp/mcpConnections';

const MCP_URL = 'https://api.poupix.connectakit.com.br/mcp';
const CLAUDE_DEEPLINK = `claude://mcp/install?url=${encodeURIComponent(MCP_URL)}&name=Poupix`;

export const IntegrationsPage: React.FC = () => {
  const [connections, setConnections] = useState<MCPConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showChatGPTHelp, setShowChatGPTHelp] = useState(false);
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
          <h1 className="text-2xl font-semibold">Integrações</h1>
          <p className="text-muted-foreground">Conecte assistentes de IA para conversar com seus dados financeiros.</p>
        </div>
      </div>

      {/* Claude Integration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-orange-600 font-bold text-sm">C</span>
            </div>
            <CardTitle>Claude</CardTitle>
          </div>
          <CardDescription>
            Adicione o Poupix como MCP server no Claude Desktop ou Claude.ai.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Clique no botão abaixo para abrir o Claude Desktop e adicionar o Poupix automaticamente como um servidor MCP.
            O Claude poderá consultar suas transações, atores e outros dados financeiros.
          </p>
          <a href={CLAUDE_DEEPLINK}>
            <Button className="gap-2">
              <ExternalLink className="w-4 h-4" />
              Conectar ao Claude
            </Button>
          </a>
        </CardContent>
      </Card>

      {/* ChatGPT Integration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-green-600 font-bold text-sm">G</span>
            </div>
            <CardTitle>ChatGPT</CardTitle>
          </div>
          <CardDescription>
            Adicione como Custom Connector no ChatGPT (Plus, Pro, Team ou Enterprise).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Conecte o Poupix ao ChatGPT usando o protocolo MCP via HTTP. Requer uma conta ChatGPT com suporte a conectores.
          </p>
          <Button variant="outline" className="gap-2" onClick={() => setShowChatGPTHelp(true)}>
            <ExternalLink className="w-4 h-4" />
            Como conectar
          </Button>
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
              Nenhuma integração conectada ainda.
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

      {/* ChatGPT Help Dialog */}
      <Dialog open={showChatGPTHelp} onOpenChange={setShowChatGPTHelp}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Conectar ao ChatGPT</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <ol className="text-sm space-y-2 list-decimal list-inside text-muted-foreground">
              <li>
                Abra{' '}
                <a
                  href="https://chat.openai.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground underline"
                >
                  chat.openai.com
                </a>{' '}
                → <strong>Settings</strong> → <strong>Connectors</strong>
              </li>
              <li>
                Clique em <strong>Add custom connector</strong>
              </li>
              <li>Cole a URL abaixo no campo "Server URL"</li>
              <li>
                Conclua o fluxo de OAuth — você será redirecionado ao Poupix para autorizar
              </li>
            </ol>
            <div className="flex gap-2">
              <input
                readOnly
                value={MCP_URL}
                className="flex-1 px-3 py-2 border rounded-md font-mono text-xs bg-muted"
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
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};
