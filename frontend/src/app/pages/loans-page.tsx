import React, { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Plus, Upload, ChevronRight, Pencil, Trash2, Wallet, TrendingUp, Clock, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

import { Loan, LoanStats, Actor, getLoans, getLoanStats, getActors, deleteLoan } from '@/services';
import { AddLoanDialog } from '@/app/components/add-loan-dialog';
import { EditLoanDialog } from '@/app/components/edit-loan-dialog';
import { UploadPixReceiptDialog } from '@/app/components/upload-pix-receipt-dialog';
import { LoanPaymentsTable } from '@/app/components/loan-payments-table';

export const LoansPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [stats, setStats] = useState<LoanStats | null>(null);
  const [actors, setActors] = useState<Record<number, Actor>>({});
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [addOpen, setAddOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [editing, setEditing] = useState<Loan | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [ls, st, ac] = await Promise.all([getLoans(), getLoanStats(), getActors()]);
      setLoans(ls);
      setStats(st);
      setActors(Object.fromEntries(ac.map((a) => [a.id, a])));
    } catch {
      toast.error('Falha ao carregar empréstimos');
    } finally {
      setLoading(false);
    }
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

  if (loading) {
    return <div className="p-6 space-y-4">{Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Empréstimos</h1>
        <div className="flex gap-2">
          <Button onClick={() => setUploadOpen(true)} variant="outline">
            <Upload className="w-4 h-4 mr-2" /> Subir comprovante PIX
          </Button>
          <Button onClick={() => setAddOpen(true)}>
            <Plus className="w-4 h-4 mr-2" /> Novo empréstimo
          </Button>
        </div>
      </div>

      {stats && (
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
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead></TableHead>
                <TableHead>Para</TableHead>
                <TableHead>Emprestado</TableHead>
                <TableHead>Pago</TableHead>
                <TableHead>Falta</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loans.map((l) => (
                <React.Fragment key={l.id}>
                  <TableRow>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => toggle(l.id)}>
                        <ChevronRight className={`w-4 h-4 transition-transform ${expanded.has(l.id) ? 'rotate-90' : ''}`} />
                      </Button>
                    </TableCell>
                    <TableCell>{actors[l.actor_id]?.name ?? `Actor #${l.actor_id}`}</TableCell>
                    <TableCell>R$ {l.principal_amount}</TableCell>
                    <TableCell>R$ {l.total_paid}</TableCell>
                    <TableCell>R$ {l.remaining}</TableCell>
                    <TableCell>{l.status}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => setEditing(l)}><Pencil className="w-4 h-4" /></Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(l.id)}><Trash2 className="w-4 h-4" /></Button>
                    </TableCell>
                  </TableRow>
                  {expanded.has(l.id) && (
                    <TableRow>
                      <TableCell colSpan={7} className="bg-gray-50">
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

      <AddLoanDialog open={addOpen} onOpenChange={setAddOpen} onSuccess={refresh} />
      <EditLoanDialog open={!!editing} onOpenChange={(v) => { if (!v) setEditing(null); }} loan={editing} onSuccess={refresh} />
      <UploadPixReceiptDialog open={uploadOpen} onOpenChange={setUploadOpen} onSuccess={refresh} />
    </div>
  );
};
