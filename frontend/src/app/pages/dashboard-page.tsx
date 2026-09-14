import React, { useState, useEffect } from 'react';
import {
  Transaction,
  TransactionFilters,
  TransactionStats,
  LedgerResult,
  getTransactions,
  getTransactionStats,
  getLedger,
  ensureSalary,
  ensureCardBills,
} from '@/services';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';

import { Plus, TrendingUp, TrendingDown, Wallet, Upload, ChevronLeft, ChevronRight, Users, FileSpreadsheet, CheckCircle2, Clock } from 'lucide-react';
import { TransactionsList } from '@/app/components/transactions-list';
import { AddTransactionDialog } from '@/app/components/add-transaction-dialog';
import { QuickAddDialog } from '@/app/components/quick-add-dialog';
import { LedgerList } from '@/app/components/ledger-list';
import { UploadBillDialog } from '@/app/components/upload-bill-dialog';
import { ReconcileBillDialog } from '@/app/components/reconcile-bill-dialog';
import { UploadSheetDialog } from '@/app/components/upload-sheet-dialog';
import { toast } from 'sonner';
import { useUser } from '@/contexts/user-context';
import { TransactionStatsFilters } from '@/services/transactions/getTransactionStats';

export const DashboardPage: React.FC = () => {
  const { user } = useUser();
  const modoOn = user?.profile?.modo_on === true;
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<TransactionStats | null>(null);
  const [ledger, setLedger] = useState<LedgerResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [transactionsLoading, setTransactionsLoading] = useState(true);
  const [ledgerLoading, setLedgerLoading] = useState(true);
  const [includeUnpaid, setIncludeUnpaid] = useState(true);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [showUploadBill, setShowUploadBill] = useState(false);
  const [showUploadSheet, setShowUploadSheet] = useState(false);
  const [showReconcile, setShowReconcile] = useState(false);
  const [reconcileBillIds, setReconcileBillIds] = useState<number[]>([]);

  // Month/Year filter
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  // Payment status filter
  const [paymentStatus, setPaymentStatus] = useState<'all' | 'paid' | 'unpaid'>('all');

  const loadTransactions = async (filters: TransactionFilters) => {
    setTransactionsLoading(true);
    getTransactions(filters).then(data => {
      setTransactions(data);
    }).catch(error => {
      toast.error('Falha ao carregar transações');
    }).finally(() => {
      setTransactionsLoading(false);
    });
  }

  const loadStats = async (filters: TransactionStatsFilters) => {
    setStatsLoading(true);
    getTransactionStats(filters).then(data => {
      setStats(data);
    }).catch(error => {
      toast.error('Falha ao carregar estatísticas');
    }).finally(() => {
      setStatsLoading(false);
    });
  }

  const loadLedger = async () => {
    setLedgerLoading(true);
    const [year, month] = selectedMonth.split('-').map(Number);
    const lastDay = new Date(year, month, 0).getDate();
    getLedger({
      start: `${selectedMonth}-01`,
      end: `${selectedMonth}-${String(lastDay).padStart(2, '0')}`,
      include_unpaid: includeUnpaid,
    }).then(data => {
      setLedger(data);
    }).catch(error => {
      toast.error('Falha ao carregar extrato');
    }).finally(() => {
      setLedgerLoading(false);
    });
  }

  const loadData = async () => {
    try {
      await ensureSalary(selectedMonth).catch(() => undefined);
      await ensureCardBills(selectedMonth).catch(() => undefined);

      const filters: TransactionFilters = {
        due_date: selectedMonth,
        payment_status: paymentStatus,
      };
      const dueDate = `${selectedMonth}-01`; // Convert YYYY-MM to YYYY-MM-DD for stats

      const requests = [
        loadTransactions(filters),
        loadStats({ due_date: dueDate }),
      ];
      if (modoOn) {
        requests.push(loadLedger());
      }

      await Promise.all(requests);
    } catch (error) {
      toast.error('Falha ao carregar dados');
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedMonth, paymentStatus, includeUnpaid, modoOn]);

  // Use stats from API
  const totalExpenses = stats?.outgoing_total || 0;
  const totalIncome = stats?.incoming_total || 0;
  const balance = stats?.balance || 0;

  const handleTransactionAdded = () => {
    setShowAddTransaction(false);
    loadData();
    toast.success('Receita adicionada com sucesso!');
  };

  const handleBillUploaded = (transactionIds: number[]) => {
    setShowUploadBill(false);
    loadData();
    if (modoOn && transactionIds.length > 0) {
      setReconcileBillIds(transactionIds);
      setShowReconcile(true);
    } else {
      toast.success('Fatura enviada com sucesso!');
    }
  };

  const handleSheetUploaded = () => {
    setShowUploadSheet(false);
    loadData();
    toast.success('Planilha enviada com sucesso!');
  };

  // Format selected month for display (e.g., "Janeiro 2026")
  const formatMonthDisplay = (monthValue: string) => {
    const [year, month] = monthValue.split('-').map(Number);
    const date = new Date(year, month - 1, 1);
    const label = date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    return label.charAt(0).toUpperCase() + label.slice(1);
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month - 2, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  // Navigate to next month
  const goToNextMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <>
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

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Saldo</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {balance.toFixed(2)}
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              R$ {(balance - (stats?.outgoing_from_actors || 0)).toFixed(2)} <span className="text-xs">seu saldo real</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receitas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              R$ {totalIncome.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              No período selecionado
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Despesas</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              R$ {totalExpenses.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              No período selecionado
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">A Receber</CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              R$ {(stats?.outgoing_from_actors || 0).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Gastos de terceiros no seu cartão
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-4 mb-8">
        {modoOn && (
          <Button onClick={() => setShowQuickAdd(true)} className="flex-1 sm:flex-none bg-emerald-600 hover:bg-emerald-700">
            <Plus className="w-4 h-4 mr-2" />
            Lançamento
          </Button>
        )}

        <Button onClick={() => setShowAddTransaction(true)} variant="outline" className="flex-1 sm:flex-none">
          <Plus className="w-4 h-4 mr-2" />
          Adicionar Receita
        </Button>

        <Button onClick={() => setShowUploadBill(true)} variant="outline" className="flex-1 sm:flex-none">
          <Upload className="w-4 h-4 mr-2" />
          Upload Fatura
        </Button>

        <Button onClick={() => setShowUploadSheet(true)} variant="outline" className="flex-1 sm:flex-none">
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Upload Planilha
        </Button>
      </div>

      {/* Transactions List */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <CardTitle>Atividade Recente</CardTitle>
              <CardDescription>Visualize e gerencie suas transações</CardDescription>
            </div>

            {/* Payment Status Filter */}
            <div className="flex gap-2">
              <Button
                variant={paymentStatus === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPaymentStatus('all')}
              >
                Todas
              </Button>
              <Button
                variant={paymentStatus === 'paid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPaymentStatus('paid')}
                className={paymentStatus === 'paid' ? 'bg-green-600 hover:bg-green-700' : ''}
              >
                <CheckCircle2 className="w-4 h-4 mr-1" />
                Pagas
              </Button>
              <Button
                variant={paymentStatus === 'unpaid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPaymentStatus('unpaid')}
                className={paymentStatus === 'unpaid' ? 'bg-orange-600 hover:bg-orange-700' : ''}
              >
                <Clock className="w-4 h-4 mr-1" />
                Pendentes
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">Todas</TabsTrigger>
              <TabsTrigger value="expenses">Despesas</TabsTrigger>
              <TabsTrigger value="income">Receitas</TabsTrigger>
              {modoOn && <TabsTrigger value="ledger">Extrato</TabsTrigger>}
            </TabsList>

            <TabsContent value="expenses">
              <TransactionsList
                type="expenses"
                transactions={transactions}
                onUpdate={loadData}
                loading={transactionsLoading}
              />
            </TabsContent>

            <TabsContent value="income">
              <TransactionsList
                type="income"
                transactions={transactions}
                onUpdate={loadData}
                loading={transactionsLoading}
              />
            </TabsContent>

            <TabsContent value="all">
              <TransactionsList
                type="all"
                transactions={transactions}
                onUpdate={loadData}
                loading={transactionsLoading}
              />
            </TabsContent>

            {modoOn && (
              <TabsContent value="ledger">
                <div className="flex justify-end mb-3">
                  <Button
                    variant={includeUnpaid ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setIncludeUnpaid((value) => !value)}
                  >
                    {includeUnpaid ? 'Incluindo previsto' : 'Só realizado'}
                  </Button>
                </div>
                <LedgerList entries={ledger?.entries || []} loading={ledgerLoading} />
              </TabsContent>
            )}
          </Tabs>
        </CardContent>
      </Card>

      {/* Dialogs */}
      {modoOn && (
        <QuickAddDialog
          open={showQuickAdd}
          onOpenChange={setShowQuickAdd}
          onSuccess={() => {
            setShowQuickAdd(false);
            loadData();
            toast.success('Lançamento criado!');
          }}
        />
      )}
      <AddTransactionDialog
        open={showAddTransaction}
        onOpenChange={setShowAddTransaction}
        onSuccess={handleTransactionAdded}
      />
      <UploadBillDialog
        open={showUploadBill}
        onOpenChange={setShowUploadBill}
        onSuccess={handleBillUploaded}
      />
      {modoOn && (
        <ReconcileBillDialog
          open={showReconcile}
          onOpenChange={setShowReconcile}
          billTransactionIds={reconcileBillIds}
          onSuccess={() => {
            setShowReconcile(false);
            loadData();
            toast.success('Conciliação concluída!');
          }}
        />
      )}
      <UploadSheetDialog
        open={showUploadSheet}
        onOpenChange={setShowUploadSheet}
        onSuccess={handleSheetUploaded}
      />
    </>
  );
};

