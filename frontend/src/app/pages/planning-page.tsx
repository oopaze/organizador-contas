import React, { useEffect, useState } from 'react';
import {
  convertIntention,
  createIntention,
  deleteIntention,
  ensureSalary,
  ensureCardBills,
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
import { ChevronLeft, ChevronRight, Pencil, Plus, Target, Trash2, Wand2, XCircle } from 'lucide-react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { getCategoryLabel } from '@/lib/category-colors';
import { ProjectionChart } from '@/app/components/planning/projection-chart';
import { GoalsProgressCard } from '@/app/components/planning/goals-progress-card';

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

const shortMonth = (monthValue: string) => {
  const [year, month] = monthValue.split('-').map(Number);
  return `${String(month).padStart(2, '0')}/${String(year).slice(2)}`;
};

const addMonths = (monthValue: string, offset: number) => {
  const [year, month] = monthValue.split('-').map(Number);
  const date = new Date(year, month - 1 + offset, 1);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
};

const statusLabel: Record<PurchaseIntention['status'], string> = {
  planned: 'Planejada',
  bought: 'Comprada',
  dismissed: 'Descartada',
};

const PIE_COLORS = ['#ef4444', '#3b82f6', '#8b5cf6', '#10b981', '#ec4899', '#f97316', '#06b6d4', '#84cc16'];

export const PlanningPage: React.FC = () => {
  const [startMonth, setStartMonth] = useState(currentMonth());
  const [endMonth, setEndMonth] = useState(addMonths(currentMonth(), 11));
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
  const [editing, setEditing] = useState<PurchaseIntention | null>(null);

  const load = async () => {
    setLoading(true);
    await ensureSalary(startMonth).catch(() => undefined);
    await ensureCardBills(startMonth).catch(() => undefined);
    Promise.all([
      getIntentions({ start: startMonth, end: endMonth }),
      getLedger({ start: `${startMonth}-01`, end: `${startMonth}-${String(lastDayOf(startMonth)).padStart(2, '0')}` }),
      getProjection({ start: startMonth, end: endMonth }),
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
  }, [startMonth, endMonth]);

  const resetForm = () => {
    setName('');
    setAmount('');
    setWhen(startMonth);
    setInstallments('1');
    setEditing(null);
  };

  const openEdit = (intention: PurchaseIntention) => {
    setName(intention.name);
    setAmount(String(parseFloat(intention.amount || '0')));
    setWhen(intention.month.slice(0, 7));
    setInstallments(String(intention.installments || 1));
    setEditing(intention);
    setShowForm(true);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editing) {
        await updateIntention(editing.id, {
          name,
          amount,
          month: `${when}-01`,
          installments: Math.max(1, parseInt(installments, 10) || 1),
        });
        toast.success('Intenção atualizada!');
      } else {
        await createIntention({
          name,
          amount,
          month: `${when}-01`,
          installments: Math.max(1, parseInt(installments, 10) || 1),
        });
        toast.success('Intenção adicionada!');
      }
      resetForm();
      setShowForm(false);
      load();
    } catch {
      toast.error(editing ? 'Falha ao atualizar a intenção' : 'Falha ao adicionar a intenção');
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
  const salary = parseFloat(projection?.months?.[0]?.salary || '0');

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
    salário: parseFloat(monthData.salary),
    gastos: parseFloat(monthData.expenses),
    intenções: parseFloat(monthData.intentions_total),
    sobra: parseFloat(monthData.leftover),
  }));

  const intentionsImpactTotal = (projection?.months || []).reduce(
    (sum, monthData) => sum + parseFloat(monthData.intentions_total),
    0,
  );
  const periodLeftover = (projection?.months || []).reduce(
    (sum, monthData) => sum + parseFloat(monthData.leftover),
    0,
  );
  const periodIncome = salary * (projection?.total_months || 0);
  const impactPercent = periodIncome > 0 ? (intentionsImpactTotal / periodIncome) * 100 : 0;
  const spendingGoal = projection?.goals?.monthly_spending_goal
    ? parseFloat(projection.goals.monthly_spending_goal)
    : null;
  const changeStart = (value: string) => {
    if (!value) return;
    setStartMonth(value);
    if (value > endMonth) setEndMonth(value);
  };

  const changeEnd = (value: string) => {
    if (!value) return;
    setEndMonth(value < startMonth ? startMonth : value);
  };

  const shiftRange = (offset: number) => {
    setStartMonth((value) => addMonths(value, offset));
    setEndMonth((value) => addMonths(value, offset));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center gap-3 sm:flex-row sm:flex-wrap sm:justify-between sm:gap-4">
        <div className="flex items-center gap-2">
          <Target className="w-6 h-6 text-gray-700" />
          <h1 className="text-2xl font-bold text-gray-900">Planejamento</h1>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Button variant="outline" size="icon" onClick={() => shiftRange(-1)} title="Período anterior">
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Input
            type="month"
            aria-label="Mês inicial"
            value={startMonth}
            onChange={(event) => changeStart(event.target.value)}
            className="w-[140px]"
          />
          <span className="text-sm text-muted-foreground">→</span>
          <Input
            type="month"
            aria-label="Mês final"
            value={endMonth}
            onChange={(event) => changeEnd(event.target.value)}
            className="w-[140px]"
          />
          <Button variant="outline" size="icon" onClick={() => shiftRange(1)} title="Próximo período">
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Saldo projetado ({shortMonth(startMonth)})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${projected < 0 ? 'text-red-600' : 'text-blue-600'}`}>
              {formatMoney(projected)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Salário e contas já incluídos</p>
          </CardContent>
        </Card>

        <Card className="border-amber-300 bg-amber-50/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Intenções no período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">{formatMoney(intentionsImpactTotal)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {intentions.filter((intention) => intention.status === 'planned').length} planejada(s) em{' '}
              {projection?.total_months || 0} mês(es)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sobra no período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${periodLeftover < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {formatMoney(periodLeftover)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Soma das sobras de {projection?.total_months || 0} mês(es)</p>
          </CardContent>
        </Card>
      </div>

      {projection?.goals && (
        <GoalsProgressCard goals={projection.goals} ledger={ledger!} salary={salary} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Gastos de {shortMonth(startMonth)} por categoria</CardTitle>
            <CardDescription>O que já foi lançado neste mês, como % da sua renda fixa</CardDescription>
          </CardHeader>
          <CardContent>
            {spendingByCategory.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted-foreground">Nenhum gasto no mês</p>
            ) : (
              <div className="space-y-3">
                <div className="h-[190px] sm:h-[220px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={spendingByCategory}
                        dataKey="value"
                        nameKey="name"
                        innerRadius="48%"
                        outerRadius="72%"
                        cy="50%"
                      >
                        {spendingByCategory.map((entry, index) => (
                          <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value: number) =>
                          `${formatMoney(value)}${salary > 0 ? ` (${((value / salary) * 100).toFixed(1)}% da renda)` : ''}`
                        }
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1">
                  {spendingByCategory.map((entry, index) => (
                    <div key={entry.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <span
                        className="h-2.5 w-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}
                      />
                      <span>{entry.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projeção</CardTitle>
            <CardDescription>
              {shortMonth(startMonth)} → {shortMonth(endMonth)}, na sua renda fixa
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] sm:h-[260px]">
              <ProjectionChart data={projectionData} spendingGoal={spendingGoal} />
            </div>
            {intentionsImpactTotal > 0 && (
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Em {projection?.total_months} mês(es), as intenções somam{' '}
                <span className="font-semibold text-amber-700">{formatMoney(intentionsImpactTotal)}</span> (
                {impactPercent.toFixed(1)}% da sua renda do período)
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="border-amber-300">
        <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
          <div>
            <CardTitle>Intenções do período</CardTitle>
            <CardDescription>
              {shortMonth(startMonth)} → {shortMonth(endMonth)} · vire transação quando decidir comprar
            </CardDescription>
          </div>
          <Button
            onClick={() => {
              setWhen(startMonth);
              setShowForm(true);
            }}
            size="sm"
            className="bg-amber-500 hover:bg-amber-600 text-white shrink-0"
          >
            <Plus className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">Nova intenção</span>
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="py-6 text-center text-sm text-muted-foreground">Carregando...</p>
          ) : intentions.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              Nenhuma intenção no período
            </p>
          ) : (
            <div className="divide-y">
              {intentions.map((intention) => {
                const perInstallment = parseFloat(intention.amount || '0') / Math.max(1, intention.installments);
                return (
                  <div key={intention.id} className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="truncate text-sm font-medium text-gray-900">{intention.name}</span>
                        <Badge
                          variant="outline"
                          className={
                            intention.status === 'bought'
                              ? 'border-emerald-400 text-emerald-700'
                              : intention.status === 'dismissed'
                                ? 'text-muted-foreground'
                                : 'border-amber-300 bg-amber-50 text-amber-700'
                          }
                        >
                          {statusLabel[intention.status]}
                        </Badge>
                        {intention.carry_over && (
                          <Badge variant="outline" className="border-blue-300 bg-blue-50 text-blue-700">
                            Parcela de intenção anterior
                          </Badge>
                        )}
                        <span className="text-sm font-semibold text-amber-700">
                          {formatMoney(intention.amount)}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(`${intention.month}T00:00:00`).toLocaleDateString('pt-BR')}
                        {intention.installments > 1 &&
                          ` · ${intention.installments}x de ${formatMoney(perInstallment)}`}
                      </p>
                    </div>

                    {intention.status === 'planned' && (
                      <div className="flex flex-wrap items-center gap-2">
                        <Button size="sm" className="bg-amber-500 hover:bg-amber-600 text-white" onClick={() => handleConvert(intention)}>
                          <Wand2 className="w-4 h-4 mr-1" />
                          Virar transação
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => openEdit(intention)}>
                          <Pencil className="w-4 h-4 mr-1" />
                          Editar
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDismiss(intention)}>
                          <XCircle className="w-4 h-4 mr-1" />
                          Descartar
                        </Button>
                        <Button size="icon" variant="ghost" onClick={() => handleDelete(intention)} title="Excluir">
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showForm} onOpenChange={(open) => {
        if (!open) resetForm();
        setShowForm(open);
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar intenção' : 'Nova intenção de compra'}</DialogTitle>
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
                {saving ? 'Salvando...' : editing ? 'Salvar alterações' : 'Adicionar intenção'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};
