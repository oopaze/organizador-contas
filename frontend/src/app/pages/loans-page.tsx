import React, { useCallback, useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';
import {
  Plus, ChevronRight, Pencil, Trash2,
  Wallet, TrendingUp, Clock, CheckCircle2,
  HandCoins, Upload, FilePlus,
} from 'lucide-react';
import { toast } from 'sonner';

import { Loan, LoanStats, getLoans, getLoanStats, deleteLoan } from '@/services';
import { AddLoanDialog } from '@/app/components/add-loan-dialog';
import { EditLoanDialog } from '@/app/components/edit-loan-dialog';
import { UploadPixReceiptDialog } from '@/app/components/upload-pix-receipt-dialog';
import { AddLoanPaymentDialog } from '@/app/components/add-loan-payment-dialog';
import { LoanPaymentsTable } from '@/app/components/loan-payments-table';

const STATUS_LABEL: Record<Loan['status'], string> = {
  active: 'Pendente',
  settled: 'Pago',
  cancelled: 'Cancelado',
};

const STATUS_CLASS: Record<Loan['status'], string> = {
  active: 'bg-orange-100 text-orange-800',
  settled: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-600',
};

export const LoansPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [stats, setStats] = useState<LoanStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [loansLoading, setLoansLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [addOpen, setAddOpen] = useState(false);
  const [editing, setEditing] = useState<Loan | null>(null);
  const [uploadFor, setUploadFor] = useState<number | undefined>(undefined);
  const [manualFor, setManualFor] = useState<number | null>(null);
  const [manualFileId, setManualFileId] = useState<number | undefined>(undefined);
  const [menuFor, setMenuFor] = useState<{ id: number; top: number; left: number } | null>(null);

  useEffect(() => {
    if (!menuFor) return;
    const close = () => setMenuFor(null);
    window.addEventListener('scroll', close, true);
    window.addEventListener('resize', close);
    return () => {
      window.removeEventListener('scroll', close, true);
      window.removeEventListener('resize', close);
    };
  }, [menuFor]);

  const openMenu = (loanId: number, e: React.MouseEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMenuFor({
      id: loanId,
      top: rect.bottom + 4,
      left: rect.right - 224, // 224px = w-56
    });
  };

  const refresh = useCallback(async () => {
    setStatsLoading(true);
    setLoansLoading(true);

    getLoanStats()
      .then(setStats)
      .catch(() => toast.error('Falha ao carregar estatísticas'))
      .finally(() => setStatsLoading(false));

    getLoans()
      .then(setLoans)
      .catch(() => toast.error('Falha ao carregar empréstimos'))
      .finally(() => setLoansLoading(false));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const handleDelete = async (id: number) => {
    if (!confirm('Remover este empréstimo? Os pagamentos vinculados também serão removidos.')) return;
    try { await deleteLoan(id); toast.success('Empréstimo removido'); refresh(); }
    catch { toast.error('Falha ao remover'); }
  };

  const toggle = (id: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Empréstimos</h1>
        <Button onClick={() => setAddOpen(true)} className="w-full sm:w-auto">
          <Plus className="w-4 h-4 mr-2" /> Novo empréstimo
        </Button>
      </div>

      {statsLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-4 rounded-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-7 w-32 mb-2" />
                <Skeleton className="h-3 w-28" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Emprestado</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {Number(stats.total_lent).toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                R$ {Number(stats.active_principal).toFixed(2)} <span className="text-xs">ativos</span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recebido</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">R$ {Number(stats.total_received).toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.payments_count} pagamentos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">A Receber</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">R$ {Number(stats.total_outstanding).toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.active_count} empréstimos pendentes
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Quitados</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">R$ {Number(stats.settled_principal).toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.settled_count} empréstimos quitados
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <HandCoins className="h-5 w-5" />
            <CardTitle>Empréstimos</CardTitle>
          </div>
          <CardDescription>
            Acompanhe o dinheiro que você emprestou e os pagamentos recebidos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Para</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Emprestado</TableHead>
                <TableHead>Pago</TableHead>
                <TableHead>Falta</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[160px] text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loansLoading ? (
                [1, 2, 3].map((i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-16 rounded-full" /></TableCell>
                    <TableCell className="text-right"><Skeleton className="h-8 w-24 ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : loans.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-sm text-gray-500 py-8">
                    Nenhum empréstimo registrado ainda.
                  </TableCell>
                </TableRow>
              ) : loans.map((l) => (
                <React.Fragment key={l.id}>
                  <TableRow>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => toggle(l.id)}>
                        <ChevronRight className={`w-4 h-4 transition-transform ${expanded.has(l.id) ? 'rotate-90' : ''}`} />
                      </Button>
                    </TableCell>
                    <TableCell>{l.actor?.name ?? `Actor #${l.actor_id}`}</TableCell>
                    <TableCell className="text-sm">{l.lent_at}</TableCell>
                    <TableCell>R$ {l.principal_amount}</TableCell>
                    <TableCell>R$ {l.total_paid}</TableCell>
                    <TableCell>R$ {l.remaining}</TableCell>
                    <TableCell>
                      <Badge className={STATUS_CLASS[l.status]}>{STATUS_LABEL[l.status]}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="inline-flex items-center justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Adicionar pagamento"
                          onClick={(e) => openMenu(l.id, e)}
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setEditing(l)} title="Editar"><Pencil className="w-4 h-4" /></Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(l.id)} title="Remover"><Trash2 className="w-4 h-4 text-red-600" /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                  {expanded.has(l.id) && (
                    <TableRow>
                      <TableCell colSpan={8} className="bg-gray-50">
                        <LoanPaymentsTable payments={l.payments ?? []} onChange={refresh} />
                      </TableCell>
                    </TableRow>
                  )}
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {menuFor && createPortal(
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setMenuFor(null)}
          />
          <div
            className="fixed z-50 w-56 rounded-md border bg-popover p-1 shadow-md"
            style={{ top: menuFor.top, left: menuFor.left }}
          >
            <button
              type="button"
              className="flex w-full items-center rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground"
              onClick={() => { const id = menuFor.id; setMenuFor(null); setUploadFor(id); }}
            >
              <Upload className="w-4 h-4 mr-2" /> Subir comprovante PIX
            </button>
            <button
              type="button"
              className="flex w-full items-center rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground"
              onClick={() => { const id = menuFor.id; setMenuFor(null); setManualFor(id); }}
            >
              <FilePlus className="w-4 h-4 mr-2" /> Entrada manual
            </button>
          </div>
        </>,
        document.body
      )}

      <AddLoanDialog open={addOpen} onOpenChange={setAddOpen} onSuccess={refresh} />
      <EditLoanDialog open={!!editing} onOpenChange={(v) => { if (!v) setEditing(null); }} loan={editing} onSuccess={refresh} />
      <UploadPixReceiptDialog
        open={uploadFor !== undefined}
        onOpenChange={(v) => { if (!v) setUploadFor(undefined); }}
        onSuccess={refresh}
        preselectedLoanId={uploadFor}
        onParseFailed={(fileId, loanId) => {
          setManualFor(loanId);
          setManualFileId(fileId);
        }}
      />
      <AddLoanPaymentDialog
        open={manualFor !== null}
        onOpenChange={(v) => { if (!v) { setManualFor(null); setManualFileId(undefined); } }}
        onSuccess={refresh}
        loanId={manualFor}
        preselectedFileId={manualFileId}
      />
    </div>
  );
};
