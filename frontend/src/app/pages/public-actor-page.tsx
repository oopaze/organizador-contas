import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Button } from '@/app/components/ui/button';
import { Users, ChevronRight, ChevronLeft, Wallet, CheckCircle2, Clock } from 'lucide-react';
import { getPublicActor, PublicActorResponse } from '@/services/actors/getPublicActor';
import { getCategoryClassName, getCategoryLabel } from '@/lib/category-colors';

export const PublicActorPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
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
    setSearchParams({ month: newMonth });
  };

  const goToNextMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month, 1);
    const newMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    setSelectedMonth(newMonth);
    setSearchParams({ month: newMonth });
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

        {/* Stats Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Gasto</CardTitle>
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
              <CardTitle className="text-sm font-medium">Já Pago</CardTitle>
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
              <CardTitle className="text-sm font-medium">Restante</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${(actor?.total_remaining || 0) > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                {loading ? <Skeleton className="h-8 w-24" /> : `R$ ${(actor?.total_remaining || 0).toFixed(2)}`}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Transactions Table */}
        <Card>
          <CardHeader>
            <CardTitle>Itens</CardTitle>
            <CardDescription>Detalhamento dos gastos</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead className="text-right">Valor</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[1, 2, 3].map((i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-20" /></TableCell>
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

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-muted-foreground">
          Powered by <span className="font-semibold">Poupix</span>
        </div>
      </div>
    </div>
  );
};

