import React, { useEffect, useState } from 'react';
import {
  convertIntention,
  createIntention,
  deleteIntention,
  ensureSalary,
  getIntentions,
  getLedger,
  getProjection,
  LedgerResult,
  ProjectionResult,
  PurchaseIntention,
  updateIntention,
} from '@/services';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Badge } from '@/app/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { toast } from 'sonner';
import { ChevronLeft, ChevronRight, Plus, Target, Trash2, Wand2, XCircle } from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getCategoryLabel } from '@/lib/category-colors';

const currentMonth = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
};

const lastDayOf = (month: string) => {
  const [year, monthNumber] = month.split('-').map(Number);
  return new Date(year, monthNumber, 0).getDate();
};

const formatMoney = (value: number | string) =>
  `R$ ${Number(value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const formatMonthDisplay = (monthValue: string) => {
  const [year, month] = monthValue.split('-').map(Number);
  const label = new Date(year, month - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  return label.charAt(0).toUpperCase() + label.slice(1);
};

const shortMonth = (monthValue: string) => {
  const [year, month] = monthValue.split('-').map(Number);
  return `${String(month).padStart(2, '0')}/${String(year).slice(2)}`;
};

const statusLabel: Record<PurchaseIntention['status'], string> = {
  planned: 'Planejada',
  bought: 'Comprada',
  dismissed: 'Descartada',
};

const PIE_COLORS = ['#d97706', '#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#b45309', '#92400e', '#fef3c7'];

export const PlanningPage: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const [intentions, setIntentions] = useState<PurchaseIntention[]>([]);
  const [ledger, setLedger] = useState<LedgerResult | null>(null);
  const [projection, setProjection] = useState<ProjectionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [when, setWhen] = useState(currentMonth());
  const [installments, setInstallments] = useState('1');

  const load = async () => {
    setLoading(true);
    await ensureSalary(month).catch(() => undefined);
    Promise.all([
      getIntentions(month),
      getLedger({ start: `${month}-01`, end: `${month}-${String(lastDayOf(month)).padStart(2, '0')}` }),
      getProjection({ start: month }),
    ])
      .then(([list, ledgerResult, projectionResult]) => {
        setIntentions(list);
        setLedger(ledgerResult);
        setProjection(projectionResult);
      })
      .catch(() => toast.error('Falha ao carregar o planejamento'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [month]);

  const resetForm = () => {
    setName('');
    setAmount('');
    setWhen(month);
    setInstallments('1');
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createIntention({
        name,
        amount,
        month: `${when}-01`,
        installments: Math.max(1, parseInt(installments, 10) || 1),
      });
      resetForm();
      setShowForm(false);
      toast.success('Intenção adicionada!');
      load();
    } catch {
      toast.error('Falha ao adicionar a intenção');
    } finally {
      setSaving(false);
    }
  };

  const handleConvert = async (intention: PurchaseIntention) => {
    try {
      await convertIntention(intention.id);
      toast.success('Intenção virou transação! As parcelas já estão no extrato.');
      load();
    } catch (error) {
      const apiError = error as { response?: { data?: { error?: string } } };
      toast.error(apiError?.response?.data?.error || 'Falha ao converter a intenção');
    }
  };

  const handleDismiss = async (intention: PurchaseIntention) => {
    try {
      await updateIntention(intention.id, { status: 'dismissed' });
      load();
    } catch {
      toast.error('Falha ao descartar a intenção');
    }
  };

  const handleDelete = async (intention: PurchaseIntention) => {
    try {
      await deleteIntention(intention.id);
      load();
    } catch (error) {
      const apiError = error as { response?: { data?: { error?: string } } };
      toast.error(apiError?.response?.data?.error || 'Falha ao excluir a intenção');
    }
  };

  const projected = parseFloat(ledger?.summary.projected_balance || '0');
  const commitment = parseFloat(projection?.months?.[0]?.intentions_total || '0');
  const afterIntentions = projected - commitment;

  const spendingByCategory = Object.entries(
    (ledger?.entries || [])
      .filter((entry) => entry.direction === 'outgoing')
      .reduce<Record<string, number>>((acc, entry) => {
        const key = entry.category || 'other';
        acc[key] = (acc[key] || 0) + parseFloat(entry.amount || '0');
        return acc;
      }, {})
  ).map(([category, total]) => ({ name: getCategoryLabel(category), value: total }));

  const projectionData = (projection?.months || []).map((monthData) => ({
    month: shortMonth(monthData.month),
    intenções: parseFloat(monthData.intentions_total),
    sobra: parseFloat(monthData.leftover),
  }));

  const goToMonth = (offset: number) => {
    const [year, monthNumber] = month.split('-').map(Number);
    const date = new Date(year, monthNumber - 1 + offset, 1);
    setMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Target className="w-6 h-6 text-amber-500" />
          <h1 className="text-2xl font-bold text-gray-900">Planejamento</h1>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => goToMonth(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-base font-semibold text-gray-900 min-w-[180px] text-center">
            {formatMonthDisplay(month)}
          </span>
          <Button variant="outline" size="icon" onClick={() => goToMonth(1)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-amber-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Saldo projetado do mês</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatMoney(projected)}</div>
            <p className="text-xs text-muted-foreground mt-1">Salário e contas já incluídos</p>
          </CardContent>
        </Card>

        <Card className="border-amber-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Parcelas das intenções no mês</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">{formatMoney(commitment)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {intentions.filter((intention) => intention.status === 'planned').length} planejada(s)
            </p>
          </CardContent>
        </Card>

        <Card className="border-amber-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sobra depois de comprar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${afterIntentions < 0 ? 'text-red-600' : 'text-amber-600'}`}>
              {formatMoney(afterIntentions)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Saldo projetado − parcelas</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-amber-200">
          <CardHeader>
            <CardTitle>Gastos do mês por categoria</CardTitle>
            <CardDescription>O que já foi lançado neste mês</CardDescription>
          </CardHeader>
          <CardContent>
            {spendingByCategory.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted-foreground">Nenhum gasto no mês</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={spendingByCategory} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90}>
                    {spendingByCategory.map((entry, index) => (
                      <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatMoney(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card className="border-amber-200">
          <CardHeader>
            <CardTitle>Projeção dos próximos 12 meses</CardTitle>
            <CardDescription>Parcelas planejadas e sobra do salário mês a mês</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={projectionData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip formatter={(value: number) => formatMoney(value)} />
                <Legend />
                <Bar dataKey="intenções" fill="#d97706" radius={[4, 4, 0, 0]} />
                <Bar dataKey="sobra" fill="#fcd34d" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="border-amber-200">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Intenções do mês</CardTitle>
            <CardDescription>Vire transação quando decidir comprar</CardDescription>
          </div>
          <Button
            onClick={() => {
              setWhen(month);
              setShowForm(true);
            }}
            className="bg-amber-500 hover:bg-amber-600 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nova intenção
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="py-6 text-center text-sm text-muted-foreground">Carregando...</p>
          ) : intentions.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              Nenhuma intenção neste mês
            </p>
          ) : (
            <div className="divide-y">
              {intentions.map((intention) => {
                const perInstallment = parseFloat(intention.amount || '0') / Math.max(1, intention.installments);
                return (
                  <div key={intention.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="truncate text-sm font-medium text-gray-900">{intention.name}</span>
                        <Badge
                          variant="outline"
                          className={
                            intention.status === 'bought'
                              ? 'border-amber-400 text-amber-700'
                              : intention.status === 'dismissed'
                                ? 'text-muted-foreground'
                                : 'border-amber-300 bg-amber-50 text-amber-700'
                          }
                        >
                          {statusLabel[intention.status]}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(`${intention.month}T00:00:00`).toLocaleDateString('pt-BR')}
                        {intention.installments > 1 &&
                          ` · ${intention.installments}x de ${formatMoney(perInstallment)}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-amber-700">{formatMoney(intention.amount)}</span>
                      {intention.status === 'planned' && (
                        <>
                          <Button size="sm" className="bg-amber-500 hover:bg-amber-600 text-white" onClick={() => handleConvert(intention)}>
                            <Wand2 className="w-4 h-4 mr-1" />
                            Virar transação
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDismiss(intention)}>
                            <XCircle className="w-4 h-4 mr-1" />
                            Descartar
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => handleDelete(intention)} title="Excluir">
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova intenção de compra</DialogTitle>
            <DialogDescription>
              Dá para parcelar: a projeção mostra o impacto mês a mês.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAdd}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="intention-name">O que você quer comprar</Label>
                <Input
                  id="intention-name"
                  placeholder="Ex: Notebook"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="intention-amount">Valor total</Label>
                  <Input
                    id="intention-amount"
                    type="number"
                    step="0.01"
                    inputMode="decimal"
                    placeholder="0,00"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="intention-installments">Parcelas</Label>
                  <Input
                    id="intention-installments"
                    type="number"
                    min="1"
                    max="48"
                    inputMode="numeric"
                    value={installments}
                    onChange={(e) => setInstallments(e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="intention-month">Mês da primeira parcela</Label>
                <Input
                  id="intention-month"
                  type="month"
                  value={when}
                  onChange={(e) => setWhen(e.target.value)}
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={saving} className="bg-amber-500 hover:bg-amber-600 text-white">
                {saving ? 'Adicionando...' : 'Adicionar intenção'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};
