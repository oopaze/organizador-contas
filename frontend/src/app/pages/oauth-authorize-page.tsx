import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Wallet } from 'lucide-react';
import { useAuth } from '@/contexts/auth-context';
import {
  fetchMCPClient,
  approveMCPAuthorization,
  MCPClientInfo,
} from '@/services/mcp/oauthAuthorize';

const REQUIRED_PARAMS = ['client_id', 'redirect_uri', 'code_challenge'] as const;

export const OAuthAuthorizePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [client, setClient] = useState<MCPClientInfo | null>(null);
  const [loadingClient, setLoadingClient] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);

  const clientId = searchParams.get('client_id');
  const redirectUri = searchParams.get('redirect_uri');
  const state = searchParams.get('state') ?? '';
  const codeChallenge = searchParams.get('code_challenge');
  const codeChallengeMethod = searchParams.get('code_challenge_method') ?? 'S256';
  const scope = searchParams.get('scope') ?? 'mcp:read';

  const missingParam = REQUIRED_PARAMS.find(k => !searchParams.get(k));

  // Auth gate — preserve full querystring through login.
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      const next = encodeURIComponent(location.pathname + location.search);
      navigate(`/login?next=${next}`, { replace: true });
    }
  }, [authLoading, isAuthenticated, navigate, location]);

  // Fetch client info once we know required params exist and user is authed.
  useEffect(() => {
    if (missingParam || !isAuthenticated || !clientId) return;
    setLoadingClient(true);
    fetchMCPClient(clientId)
      .then(setClient)
      .catch(() => setError('Aplicativo não reconhecido.'))
      .finally(() => setLoadingClient(false));
  }, [clientId, isAuthenticated, missingParam]);

  const redirectMatches =
    client && redirectUri && client.redirect_uris.includes(redirectUri);

  async function handleApprove() {
    if (!clientId || !redirectUri || !codeChallenge) return;
    setApproving(true);
    setError(null);
    try {
      const { redirect_to } = await approveMCPAuthorization({
        client_id: clientId,
        redirect_uri: redirectUri,
        code_challenge: codeChallenge,
        code_challenge_method: codeChallengeMethod,
        scope,
        state,
      });
      window.location.assign(redirect_to);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao autorizar');
      setApproving(false);
    }
  }

  function handleDeny() {
    if (!redirectUri) return;
    const sep = redirectUri.includes('?') ? '&' : '?';
    const qs = new URLSearchParams({ error: 'access_denied', state }).toString();
    window.location.assign(`${redirectUri}${sep}${qs}`);
  }

  if (authLoading || !isAuthenticated) {
    return <Shell><Skeleton className="h-32 w-full" /></Shell>;
  }

  if (missingParam) {
    return (
      <Shell>
        <ErrorCard
          title="Solicitação de autorização inválida"
          message={`Parâmetro ausente: ${missingParam}.`}
        />
      </Shell>
    );
  }

  if (loadingClient) {
    return <Shell><Skeleton className="h-48 w-full" /></Shell>;
  }

  if (!client) {
    return <Shell><ErrorCard title="Aplicativo não reconhecido" message={error ?? ''} /></Shell>;
  }

  return (
    <Shell>
      <Card>
        <CardHeader>
          <CardTitle>Autorizar {client.name}</CardTitle>
          <CardDescription>
            Este aplicativo poderá ler suas finanças no Poupix em modo somente leitura.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border bg-muted/40 p-4 text-sm">
            <div className="font-medium">Permissão solicitada</div>
            <div className="text-muted-foreground">
              Leitura das suas transações, categorias e atores ({scope}).
            </div>
          </div>

          {!redirectMatches && (
            <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
              URL de retorno não permitida para este aplicativo.
            </div>
          )}

          {error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={handleDeny} disabled={approving}>
              Negar
            </Button>
            <Button
              onClick={handleApprove}
              disabled={!redirectMatches || approving}
            >
              {approving ? 'Autorizando…' : 'Autorizar'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </Shell>
  );
};

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-100 p-4">
    <div className="w-full max-w-md">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-14 h-14 bg-emerald-600 rounded-full mb-3">
          <Wallet className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Poupix</h1>
      </div>
      {children}
    </div>
  </div>
);

const ErrorCard: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {message && <CardDescription>{message}</CardDescription>}
    </CardHeader>
    <CardContent>
      <a href="/" className="text-sm text-emerald-700 underline">Voltar ao Poupix</a>
    </CardContent>
  </Card>
);
