import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { 
  Transaction, 
  TransactionFilters,
  getTransactions,
} from '@/services';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';

import { LogOut, Plus, TrendingUp, TrendingDown, Wallet, Upload, ChevronLeft, ChevronRight } from 'lucide-react';
import { TransactionsList } from './TransactionsList';
import { AddTransactionDialog } from './AddTransactionDialog';
import { UploadBillDialog } from './UploadBillDialog';
import { toast } from 'sonner';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
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
      const transactionsData = await getTransactions(filters);
      setTransactions(transactionsData);
    } catch (error) {
      toast.error('Falha ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedMonth]);

  // Calculate totals for selected month
  const totalExpenses = transactions
    .filter(t => t.transaction_type === 'outgoing')
    .reduce((sum, t) => sum + parseFloat(t.total_amount || '0'), 0);
  
  const totalIncome = transactions
    .filter(t => t.transaction_type === 'incoming')
    .reduce((sum, t) => sum + parseFloat(t.total_amount || '0'), 0);

  const balance = totalIncome - totalExpenses;

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
    const date = new Date(year, month - 2, 1); // month - 1 for 0-indexed, then -1 more for previous
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  // Navigate to next month
  const goToNextMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month, 1); // month - 1 for 0-indexed, then +1 for next = just month
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
                <Wallet className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Gerenciador de Contas</h1>
                <p className="text-sm text-gray-500">Bem-vindo, {user?.profile?.first_name}!</p>
              </div>
            </div>
            <Button variant="outline" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Saldo</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {balance.toFixed(2)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {balance >= 0 ? 'Saldo positivo' : 'Saldo negativo'}
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
      </main>

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
    </div>
  );
};
