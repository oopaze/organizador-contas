import React, { useEffect, useState } from 'react';
import {
  convertIntention,
  createIntention,
  deleteIntention,
  ensureSalary,
  getIntentions,
  getLedger,
  LedgerResult,
  PurchaseIntention,
  updateIntention,
} from '@/services';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Badge } from '@/app/components/ui/badge';
import { toast } from 'sonner';
import { ChevronLeft, ChevronRight, ShoppingCart, Trash2, Wand2, XCircle } from 'lucide-react';

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

const statusLabel: Record<PurchaseIntention['status'], string> = {
  planned: 'Planejada',
  bought: 'Comprada',
  dismissed: 'Descartada',
};

export const PlanningPage: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const [intentions, setIntentions] = useState<PurchaseIntention[]>([]);
  const [ledger, setLedger] = useState<LedgerResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [when, setWhen] = useState(currentMonth());

  const load = async () => {
    setLoading(true);
    await ensureSalary(month).catch(() => undefined);
    Promise.all([
      getIntentions(month),
      getLedger({ start: `${month}-01`, end: `${month}-${String(lastDayOf(month)).padStart(2, '0')}` }),
    ])
      .then(([list, ledgerResult]) => {
        setIntentions(list);
        setLedger(ledgerResult);
      })
      .catch(() => toast.error('Falha ao carregar o planejamento'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [month]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createIntention({ name, amount, month: `${when}-01` });
      setName('');
      setAmount('');
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
      toast.success('Intenção virou lançamento previsto!');
      load();
    } catch {
      toast.error('Falha ao converter a intenção');
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
    } catch {
      toast.error('Falha ao excluir a intenção');
    }
  };

  const plannedTotal = intentions
    .filter((intention) => intention.status === 'planned')
    .reduce((sum, intention) => sum + parseFloat(intention.amount || '0'), 0);
  const projected = parseFloat(ledger?.summary.projected_balance || '0');
  const afterIntentions = projected - plannedTotal;

  const goToMonth = (offset: number) => {
    const [year, monthNumber] = month.split('-').map(Number);
    const date = new Date(year, monthNumber - 1 + offset, 1);
    setMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-center">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => goToMonth(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
            {formatMonthDisplay(month)}
          </span>
          <Button variant="outline" size="icon" onClick={() => goToMonth(1)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Saldo projetado do mês</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatMoney(projected)}</div>
            <p className="text-xs text-muted-foreground mt-1">Salário e contas já incluídos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Intenções planejadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{formatMoney(plannedTotal)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {intentions.filter((intention) => intention.status === 'planned').length} planejada(s) no mês
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sobra depois de comprar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${afterIntentions < 0 ? 'text-red-600' : 'text-green-600'}`}>
              {formatMoney(afterIntentions)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Saldo projetado − intenções</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Nova intenção de compra</CardTitle>
          <CardDescription>Planeje agora e vire gasto quando decidir comprar.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="intention-name">O que você quer comprar</Label>
              <Input
                id="intention-name"
                placeholder="Ex: Notebook"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="intention-amount">Valor</Label>
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
              <Label htmlFor="intention-month">Mês</Label>
              <Input
                id="intention-month"
                type="month"
                value={when}
                onChange={(e) => setWhen(e.target.value)}
                required
              />
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={saving} className="bg-emerald-600 hover:bg-emerald-700">
                <ShoppingCart className="w-4 h-4 mr-2" />
                {saving ? 'Adicionando...' : 'Adicionar intenção'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Intenções do mês</CardTitle>
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
              {intentions.map((intention) => (
                <div key={intention.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-gray-900">{intention.name}</span>
                      <Badge
                        variant={intention.status === 'bought' ? 'default' : 'outline'}
                        className={intention.status === 'dismissed' ? 'text-muted-foreground' : ''}
                      >
                        {statusLabel[intention.status]}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(`${intention.month}T00:00:00`).toLocaleDateString('pt-BR')}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">{formatMoney(intention.amount)}</span>
                    {intention.status === 'planned' && (
                      <>
                        <Button size="sm" onClick={() => handleConvert(intention)}>
                          <Wand2 className="w-4 h-4 mr-1" />
                          Virar gasto
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDismiss(intention)}>
                          <XCircle className="w-4 h-4 mr-1" />
                          Descartar
                        </Button>
                      </>
                    )}
                    <Button size="icon" variant="ghost" onClick={() => handleDelete(intention)} title="Excluir">
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
