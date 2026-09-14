import React, { useEffect, useState } from 'react';
import { useUser } from '@/contexts/user-context';
import { getCards, createCard, updateCard, setCardActive, updateProfile, type Card as CardType } from '@/services';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Switch } from '@/app/components/ui/switch';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';

export const SettingsPage: React.FC = () => {
  const { user, refetchUser } = useUser();
  const [savingMode, setSavingMode] = useState(false);
  const [savingSalary, setSavingSalary] = useState(false);
  const [salary, setSalary] = useState('');
  const [salaryDay, setSalaryDay] = useState('1');
  const [cards, setCards] = useState<CardType[]>([]);
  const [showCardForm, setShowCardForm] = useState(false);
  const [editingCard, setEditingCard] = useState<CardType | null>(null);
  const [cardName, setCardName] = useState('');
  const [cardDueDay, setCardDueDay] = useState('1');
  const [savingCard, setSavingCard] = useState(false);
  const modoOn = user?.profile?.modo_on === true;

  useEffect(() => {
    if (!user?.profile) return;
    setSalary(user.profile.salary ? String(user.profile.salary) : '');
    setSalaryDay(String(user.profile.salary_day ?? 1));
  }, [user?.profile?.salary, user?.profile?.salary_day]);

  const handleToggle = async (checked: boolean) => {
    setSavingMode(true);
    try {
      await updateProfile({ modo_on: checked });
      await refetchUser();
      toast.success(
        checked ? 'Modo lançamento rápido ativado!' : 'Modo lançamento rápido desativado.'
      );
    } catch {
      toast.error('Falha ao salvar a configuração');
    } finally {
      setSavingMode(false);
    }
  };

  const handleSaveSalary = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSalary(true);
    try {
      const data: { salary?: number; salary_day?: number } = {
        salary_day: Math.min(31, Math.max(1, parseInt(salaryDay, 10) || 1)),
      };
      if (salary !== '') {
        data.salary = parseFloat(salary);
      }
      await updateProfile(data);
      await refetchUser();
      toast.success('Salário atualizado!');
    } catch {
      toast.error('Falha ao salvar o salário');
    } finally {
      setSavingSalary(false);
    }
  };

  const loadCards = () => getCards().then(setCards).catch(() => toast.error('Falha ao carregar cartões'));
  useEffect(() => { loadCards(); }, []);

  const openCardForm = (card?: CardType) => {
    setEditingCard(card ?? null);
    setCardName(card?.name ?? '');
    setCardDueDay(String(card?.due_day ?? 1));
    setShowCardForm(true);
  };

  const handleSaveCard = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCard(true);
    try {
      const payload = { name: cardName.trim(), due_day: Math.min(31, Math.max(1, parseInt(cardDueDay, 10) || 1)) };
      if (editingCard) await updateCard(editingCard.id, payload);
      else await createCard(payload);
      setShowCardForm(false);
      loadCards();
      toast.success(editingCard ? 'Cartão atualizado!' : 'Cartão adicionado!');
    } catch {
      toast.error('Falha ao salvar o cartão');
    } finally {
      setSavingCard(false);
    }
  };

  const handleToggleCard = async (card: CardType) => {
    try {
      await setCardActive(card.id, !card.is_active);
      loadCards();
    } catch {
      toast.error('Falha ao atualizar o cartão');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>

      <Card>
        <CardHeader>
          <CardTitle>Salário</CardTitle>
          <CardDescription>
            O valor entra todo mês como receita garantida: meses passados e o atual como
            recebido, meses futuros como previsto.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveSalary} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="salary">Salário mensal</Label>
                <Input
                  id="salary"
                  type="number"
                  step="0.01"
                  inputMode="decimal"
                  placeholder="Ex: 5000"
                  value={salary}
                  onChange={(e) => setSalary(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary-day">Dia do recebimento</Label>
                <Input
                  id="salary-day"
                  type="number"
                  min="1"
                  max="31"
                  inputMode="numeric"
                  value={salaryDay}
                  onChange={(e) => setSalaryDay(e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={savingSalary}>
                {savingSalary ? 'Salvando...' : 'Salvar salário'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
          <div>
            <CardTitle>Cartões</CardTitle>
            <CardDescription>
              A fatura de cada cartão é criada todo mês, mesmo zerada.
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => openCardForm()} className="shrink-0">
            <Plus className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">Novo cartão</span>
          </Button>
        </CardHeader>
        <CardContent>
          {cards.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">
              Nenhum cartão cadastrado ainda.
            </p>
          ) : (
            <div className="divide-y">
              {cards.map((card) => (
                <div key={card.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-gray-900">{card.name}</span>
                      <Badge variant={card.is_active ? 'default' : 'outline'} className={card.is_active ? '' : 'text-muted-foreground'}>
                        {card.is_active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">vence dia {card.due_day}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline" onClick={() => openCardForm(card)}>
                      Editar
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleToggleCard(card)}>
                      {card.is_active ? 'Desativar' : 'Ativar'}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showCardForm} onOpenChange={setShowCardForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCard ? 'Editar cartão' : 'Novo cartão'}</DialogTitle>
            <DialogDescription>
              O dia de vencimento ancora a fatura do mês no app.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSaveCard}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="card-name">Nome</Label>
                <Input
                  id="card-name"
                  placeholder="Ex: Nubank"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="card-due-day">Dia de vencimento</Label>
                <Input
                  id="card-due-day"
                  type="number"
                  min="1"
                  max="31"
                  inputMode="numeric"
                  value={cardDueDay}
                  onChange={(e) => setCardDueDay(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCardForm(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={savingCard}>
                {savingCard ? 'Salvando...' : 'Salvar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Card>
        <CardHeader>
          <CardTitle>Modo lançamento rápido</CardTitle>
          <CardDescription>
            Lance no momento da transação, com extrato de saldo corrente e conciliação da fatura por IA.
            Desligado, o app mantém o fluxo de subir a fatura em lote.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between gap-4">
            <Label htmlFor="modo-on" className="cursor-pointer">
              Ativar modo lançamento rápido
            </Label>
            <Switch id="modo-on" checked={modoOn} disabled={savingMode} onCheckedChange={handleToggle} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
