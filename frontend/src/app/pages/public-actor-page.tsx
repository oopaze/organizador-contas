import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Button } from '@/app/components/ui/button';
import { Users, ChevronRight, ChevronLeft, Wallet, CheckCircle2, Clock, HandCoins, Download } from 'lucide-react';
import { resolveFileUrl } from '@/lib/file-url';
import { Badge } from '@/app/components/ui/badge';
import { getPublicActor, PublicActorResponse } from '@/services/actors/getPublicActor';
import { getCategoryClassName, getCategoryLabel } from '@/lib/category-colors';

export const PublicActorPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [expandedLoans, setExpandedLoans] = useState<Set<number>>(new Set());
  const toggleLoan = (id: number) => {
    setExpandedLoans((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };
  const [actor, setActor] = useState<PublicActorResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Month/Year filter from URL or current month
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const monthParam = searchParams.get('month');
    if (monthParam) return monthParam;
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const formatMonthDisplay = (monthValue: string) => {
    const [year, month] = monthValue.split('-').map(Number);
    const date = new Date(year, month - 1, 1);
    const label = date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    return label.charAt(0).toUpperCase() + label.slice(1);
  };

  const goToPreviousMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month - 2, 1);
    const newMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    setSelectedMonth(newMonth);
    setSearchParams({ token: token || '', month: newMonth });
  };

  const goToNextMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month, 1);
    const newMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    setSelectedMonth(newMonth);
    setSearchParams({ token: token || '', month: newMonth });
  };

  const fetchActor = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const dueDate = `${selectedMonth}-01`;
      const data = await getPublicActor(token, dueDate);
      setActor(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar dados');
    } finally {
      setLoading(false);
    }
  }, [token, selectedMonth]);

  useEffect(() => {
    fetchActor();
  }, [fetchActor]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <p className="text-muted-foreground text-sm">
              Este link pode ter expirado ou ser inválido.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Users className="h-6 w-6" />
            {loading ? <Skeleton className="h-8 w-32" /> : actor?.name}
          </h1>
          <p className="text-muted-foreground mt-1">Resumo de gastos compartilhado</p>
        </div>

        {/* Month Navigation */}
        <div className="mb-6 flex justify-center">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" onClick={goToPreviousMonth}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
              {formatMonthDisplay(selectedMonth)}
            </span>
            <Button variant="outline" size="icon" onClick={goToNextMonth}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Stats — Cartão de Crédito (somente quando há gastos) */}
        {(loading || (actor?.sub_transactions && actor.sub_transactions.length > 0)) && (
          <>
            <div className="flex items-center gap-2 mb-2 mt-6">
              <Wallet className="h-4 w-4 text-muted-foreground" />
              <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Cartão de Crédito
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total em Cartão</CardTitle>
                  <Wallet className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {loading ? <Skeleton className="h-8 w-24" /> : `R$ ${(actor?.total_spent || 0).toFixed(2)}`}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Pago em Cartão</CardTitle>
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {loading ? <Skeleton className="h-8 w-24" /> : `R$ ${(actor?.total_spent_paid || 0).toFixed(2)}`}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Restante em Cartão</CardTitle>
                  <Clock className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${(actor?.total_remaining || 0) > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                    {loading ? <Skeleton className="h-8 w-24" /> : `R$ ${(actor?.total_remaining || 0).toFixed(2)}`}
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}

        {/* Stats — Empréstimos */}
        {actor?.loans && actor.loans.length > 0 && (() => {
          const totalLent = actor.loans.reduce((s, l) => s + Number(l.principal_amount || 0), 0);
          const totalReceived = actor.loans.reduce((s, l) => s + Number(l.total_paid || 0), 0);
          const totalOutstanding = actor.loans.reduce((s, l) => s + Number(l.remaining || 0), 0);
          return (
            <>
              <div className="flex items-center gap-2 mb-2 mt-6">
                <HandCoins className="h-4 w-4 text-muted-foreground" />
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  Empréstimos
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Emprestado</CardTitle>
                    <HandCoins className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">R$ {totalLent.toFixed(2)}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Recebido</CardTitle>
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">R$ {totalReceived.toFixed(2)}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">A Receber</CardTitle>
                    <Clock className="h-4 w-4 text-orange-600" />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${totalOutstanding > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                      R$ {totalOutstanding.toFixed(2)}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          );
        })()}

        {/* Gastos em Cartão (somente quando há sub_transactions) */}
        {(loading || (actor?.sub_transactions && actor.sub_transactions.length > 0)) && (
        <Card>
          <CardHeader>
            <CardTitle>Gastos em Cartão</CardTitle>
            <CardDescription>Detalhamento dos gastos no período</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead>Parcela</TableHead>
                    <TableHead className="text-right">Valor</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[1, 2, 3].map((i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                      <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
                      <TableCell className="text-center"><Skeleton className="h-4 w-16 mx-auto" /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : actor?.sub_transactions?.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                Nenhum gasto encontrado neste período
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead>Parcela</TableHead>
                    <TableHead className="text-right">Valor</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {actor?.sub_transactions?.map((subTransaction) => (
                    <TableRow key={subTransaction.id}>
                      <TableCell>
                        <div className="font-medium">{subTransaction.description}</div>
                        <div className="text-xs text-muted-foreground">{subTransaction.transaction.description}</div>
                      </TableCell>
                      <TableCell>
                        {subTransaction.category ? (
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium border ${getCategoryClassName(subTransaction.category)}`}
                          >
                            {getCategoryLabel(subTransaction.category)}
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {subTransaction.installment_info && subTransaction.installment_info !== 'not installment' ? (
                          <Badge variant="outline" className="text-xs">
                            {subTransaction.installment_info.replace('installment ', '').replace(' of ', '/')}
                          </Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">À vista</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        R$ {subTransaction.amount.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-center">
                        {subTransaction.paid_at ? (
                          <span className="inline-flex items-center gap-1 text-green-600 text-xs font-medium">
                            <CheckCircle2 className="h-3 w-3" /> Pago
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-orange-600 text-xs font-medium">
                            <Clock className="h-3 w-3" /> Pendente
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
        )}

        {/* Loans Section */}
        {actor?.loans && actor.loans.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <div className="flex items-center gap-2">
                <HandCoins className="h-5 w-5" />
                <CardTitle>Empréstimos</CardTitle>
              </div>
              <CardDescription>
                Empréstimos vinculados a este ator
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40px]"></TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead className="text-right">Emprestado</TableHead>
                    <TableHead className="text-right">Pago</TableHead>
                    <TableHead className="text-right">Falta</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                    <TableHead className="text-center">Comprovante</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {actor.loans.map((loan) => {
                    const statusLabel =
                      loan.status === 'settled' ? 'Pago' :
                      loan.status === 'cancelled' ? 'Cancelado' : 'Pendente';
                    const statusClass =
                      loan.status === 'settled' ? 'bg-green-100 text-green-800' :
                      loan.status === 'cancelled' ? 'bg-gray-100 text-gray-600' : 'bg-orange-100 text-orange-800';
                    const isExpanded = expandedLoans.has(loan.id);
                    const hasPayments = loan.payments && loan.payments.length > 0;
                    return (
                      <React.Fragment key={loan.id}>
                        <TableRow>
                          <TableCell>
                            {hasPayments ? (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => toggleLoan(loan.id)}
                                title={isExpanded ? 'Ocultar pagamentos' : 'Ver pagamentos'}
                              >
                                <ChevronRight
                                  className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                                />
                              </Button>
                            ) : null}
                          </TableCell>
                          <TableCell className="text-sm">{loan.lent_at}</TableCell>
                          <TableCell className="text-sm">{loan.description || '—'}</TableCell>
                          <TableCell className="text-right font-medium">
                            R$ {Number(loan.principal_amount).toFixed(2)}
                          </TableCell>
                          <TableCell className="text-right text-green-700">
                            R$ {Number(loan.total_paid).toFixed(2)}
                          </TableCell>
                          <TableCell className="text-right text-orange-700">
                            R$ {Number(loan.remaining).toFixed(2)}
                          </TableCell>
                          <TableCell className="text-center">
                            <Badge className={statusClass}>{statusLabel}</Badge>
                          </TableCell>
                          <TableCell className="text-center">
                            {loan.file_url ? (
                              <a
                                href={resolveFileUrl(loan.file_url) ?? '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-indigo-600 hover:underline text-xs"
                              >
                                <Download className="w-3 h-3" /> Baixar
                              </a>
                            ) : (
                              <span className="text-xs text-muted-foreground">—</span>
                            )}
                          </TableCell>
                        </TableRow>
                        {isExpanded && hasPayments && (
                          <TableRow>
                            <TableCell colSpan={8} className="bg-gray-50 p-3">
                              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                                Pagamentos
                              </p>
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    <TableHead>Data</TableHead>
                                    <TableHead className="text-right">Valor</TableHead>
                                    <TableHead>Nota</TableHead>
                                    <TableHead className="text-center">Comprovante</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {loan.payments!.map((p) => (
                                    <TableRow key={p.id}>
                                      <TableCell className="text-sm">{p.paid_at}</TableCell>
                                      <TableCell className="text-right text-sm">
                                        R$ {Number(p.amount).toFixed(2)}
                                      </TableCell>
                                      <TableCell className="text-sm">{p.note || '—'}</TableCell>
                                      <TableCell className="text-center">
                                        {p.file_url ? (
                                          <a
                                            href={resolveFileUrl(p.file_url) ?? '#'}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-indigo-600 hover:underline text-xs"
                                          >
                                            <Download className="w-3 h-3" /> Baixar
                                          </a>
                                        ) : (
                                          <span className="text-xs text-muted-foreground">—</span>
                                        )}
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableCell>
                          </TableRow>
                        )}
                      </React.Fragment>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-muted-foreground">
          Powered by <span className="font-semibold">Poupix</span>
        </div>
      </div>
    </div>
  );
};

