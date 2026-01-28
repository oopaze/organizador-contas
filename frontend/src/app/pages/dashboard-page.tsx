import React, { useState, useEffect } from 'react';
import {
  Transaction,
  TransactionFilters,
  TransactionStats,
  getTransactions,
  getTransactionStats,
} from '@/services';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';

import { Plus, TrendingUp, TrendingDown, Wallet, Upload, ChevronLeft, ChevronRight, Users } from 'lucide-react';
import { TransactionsList } from '@/app/components/transactions-list';
import { AddTransactionDialog } from '@/app/components/add-transaction-dialog';
import { UploadBillDialog } from '@/app/components/upload-bill-dialog';
import { toast } from 'sonner';

export const DashboardPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<TransactionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showUploadBill, setShowUploadBill] = useState(false);

  // Month/Year filter
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const filters: TransactionFilters = {
        due_date: selectedMonth,
      };
      const dueDate = `${selectedMonth}-01`; // Convert YYYY-MM to YYYY-MM-DD for stats

      const [transactionsData, statsData] = await Promise.all([
        getTransactions(filters),
        getTransactionStats({ due_date: dueDate }),
      ]);

      setTransactions(transactionsData);
      setStats(statsData);
    } catch (error) {
      toast.error('Falha ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedMonth]);

  // Use stats from API
  const totalExpenses = stats?.outgoing_total || 0;
  const totalIncome = stats?.incoming_total || 0;
  const balance = stats?.balance || 0;

  const handleTransactionAdded = () => {
    setShowAddTransaction(false);
    loadData();
    toast.success('Receita adicionada com sucesso!');
  };

  const handleBillUploaded = () => {
    setShowUploadBill(false);
    loadData();
    toast.success('Fatura enviada com sucesso!');
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
      <div className="flex gap-4 mb-8">
        <Button onClick={() => setShowAddTransaction(true)} variant="outline" className="flex-1 sm:flex-none">
          <Plus className="w-4 h-4 mr-2" />
          Adicionar Receita
        </Button>

        <Button onClick={() => setShowUploadBill(true)} variant="outline" className="flex-1 sm:flex-none">
          <Upload className="w-4 h-4 mr-2" />
          Upload Fatura
        </Button>
      </div>

      {/* Transactions List */}
      <Card>
        <CardHeader>
          <CardTitle>Atividade Recente</CardTitle>
          <CardDescription>Visualize e gerencie suas transações</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">Todas</TabsTrigger>
              <TabsTrigger value="expenses">Despesas</TabsTrigger>
              <TabsTrigger value="income">Receitas</TabsTrigger>
            </TabsList>

            <TabsContent value="expenses">
              <TransactionsList
                type="expenses"
                transactions={transactions}
                onUpdate={loadData}
                loading={loading}
              />
            </TabsContent>

            <TabsContent value="income">
              <TransactionsList
                type="income"
                transactions={transactions}
                onUpdate={loadData}
                loading={loading}
              />
            </TabsContent>

            <TabsContent value="all">
              <TransactionsList
                type="all"
                transactions={transactions}
                onUpdate={loadData}
                loading={loading}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Dialogs */}
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
    </>
  );
};

