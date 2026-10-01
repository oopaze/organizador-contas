import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Plus from 'lucide-react-native/icons/plus';
import { CardFormDialog } from '../src/components/card-form-dialog';
import { InlineMessage } from '../src/components/inline-message';
import { Badge } from '../src/components/ui/badge';
import { Button } from '../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../src/components/ui/card';
import { Input } from '../src/components/ui/input';
import { Label } from '../src/components/ui/label';
import { Skeleton } from '../src/components/ui/skeleton';
import { Switch } from '../src/components/ui/switch';
import { useUser } from '../src/contexts/user-context';
import { toDecimalString } from '../src/lib/amount';
import { goalHint } from '../src/lib/goals';
import { formatUploadError } from '../src/lib/transaction-form';
import { getCards, setCardActive, updateProfile, type Card as CardType } from '../src/services';

function clampDay(value: string): number {
  return Math.min(31, Math.max(1, parseInt(value, 10) || 1));
}

/** Percentual vazio vira `null`; texto inválido vira `undefined` (bloqueia o envio). */
function parseGoalInput(value: string): number | null | undefined {
  if (value.trim() === '') return null;
  const decimal = toDecimalString(value);
  return decimal === null ? undefined : Number(decimal);
}

export default function SettingsScreen() {
  const { user, refetchUser } = useUser();
  const queryClient = useQueryClient();

  const [salary, setSalary] = useState('');
  const [salaryDay, setSalaryDay] = useState('1');
  const [spendingGoal, setSpendingGoal] = useState('');
  const [savingsGoal, setSavingsGoal] = useState('');
  const [essentialsGoal, setEssentialsGoal] = useState('');

  const [savingMode, setSavingMode] = useState(false);
  const [savingSalary, setSavingSalary] = useState(false);
  const [savingGoals, setSavingGoals] = useState(false);
  const [modeError, setModeError] = useState<string | null>(null);
  const [salaryError, setSalaryError] = useState<string | null>(null);
  const [goalsError, setGoalsError] = useState<string | null>(null);

  const [cardFormOpen, setCardFormOpen] = useState(false);
  const [editingCard, setEditingCard] = useState<CardType | null>(null);
  const [savingCardId, setSavingCardId] = useState<number | null>(null);
  const [cardToggleError, setCardToggleError] = useState<string | null>(null);

  const modoOn = user?.profile?.modo_on === true;

  useEffect(() => {
    if (!user?.profile) return;
    setSalary(user.profile.salary ? String(user.profile.salary) : '');
    setSalaryDay(String(user.profile.salary_day ?? 1));
    setSpendingGoal(
      user.profile.spending_goal_percent != null
        ? String(user.profile.spending_goal_percent)
        : ''
    );
    setSavingsGoal(
      user.profile.savings_goal_percent != null ? String(user.profile.savings_goal_percent) : ''
    );
    setEssentialsGoal(
      user.profile.essentials_goal_percent != null
        ? String(user.profile.essentials_goal_percent)
        : ''
    );
  }, [
    user?.profile?.salary,
    user?.profile?.salary_day,
    user?.profile?.spending_goal_percent,
    user?.profile?.savings_goal_percent,
    user?.profile?.essentials_goal_percent,
  ]);

  const cardsQuery = useQuery({ queryKey: ['cards'], queryFn: getCards });
  const cards = cardsQuery.data ?? [];

  /** Escrita de perfil invalida o usuário e relê o contexto (Modo On, salário). */
  const refreshUser = async () => {
    await queryClient.invalidateQueries({ queryKey: ['user'] });
    refetchUser();
  };

  const handleToggle = async (checked: boolean) => {
    setSavingMode(true);
    setModeError(null);
    try {
      await updateProfile({ modo_on: checked });
      await refreshUser();
    } catch (error) {
      setModeError(formatUploadError(error, 'Falha ao salvar a configuração'));
    } finally {
      setSavingMode(false);
    }
  };

  const handleSaveSalary = async () => {
    const decimal = toDecimalString(salary);
    if (salary.trim() !== '' && decimal === null) {
      setSalaryError('Informe um valor válido');
      return;
    }

    setSavingSalary(true);
    setSalaryError(null);
    try {
      const data: { salary?: number; salary_day: number } = { salary_day: clampDay(salaryDay) };
      if (decimal !== null) data.salary = Number(decimal);
      await updateProfile(data);
      await refreshUser();
    } catch (error) {
      setSalaryError(formatUploadError(error, 'Falha ao salvar o salário'));
    } finally {
      setSavingSalary(false);
    }
  };

  const handleSaveGoals = async () => {
    const spending = parseGoalInput(spendingGoal);
    const savings = parseGoalInput(savingsGoal);
    const essentials = parseGoalInput(essentialsGoal);
    if (spending === undefined || savings === undefined || essentials === undefined) {
      setGoalsError('Informe percentuais válidos');
      return;
    }

    setSavingGoals(true);
    setGoalsError(null);
    try {
      await updateProfile({
        spending_goal_percent: spending,
        savings_goal_percent: savings,
        essentials_goal_percent: essentials,
      });
      await refreshUser();
    } catch (error) {
      setGoalsError(formatUploadError(error, 'Falha ao salvar as metas'));
    } finally {
      setSavingGoals(false);
    }
  };

  const openCardForm = (card?: CardType) => {
    setEditingCard(card ?? null);
    setCardFormOpen(true);
  };

  const closeCardForm = () => {
    setCardFormOpen(false);
    setEditingCard(null);
  };

  const handleCardSaved = () => {
    void queryClient.invalidateQueries({ queryKey: ['cards'] });
  };

  const handleToggleCard = async (card: CardType) => {
    setSavingCardId(card.id);
    setCardToggleError(null);
    try {
      await setCardActive(card.id, !card.is_active);
      await queryClient.invalidateQueries({ queryKey: ['cards'] });
    } catch (error) {
      setCardToggleError(formatUploadError(error, 'Falha ao atualizar o cartão'));
    } finally {
      setSavingCardId(null);
    }
  };

  return (
    <ScrollView className="flex-1 bg-zinc-50" contentContainerClassName="gap-6 p-4 pb-24">
      <Card>
        <CardHeader>
          <CardTitle>Salário</CardTitle>
          <CardDescription>
            O valor entra todo mês como receita garantida: meses passados e o atual como
            recebido, meses futuros como previsto.
          </CardDescription>
        </CardHeader>
        <CardContent className="gap-4">
          {salaryError ? <InlineMessage>{salaryError}</InlineMessage> : null}
          <Input
            label="Salário mensal"
            keyboardType="decimal-pad"
            placeholder="Ex: 5000"
            value={salary}
            onChangeText={setSalary}
          />
          <Input
            label="Dia do recebimento"
            keyboardType="number-pad"
            value={salaryDay}
            onChangeText={setSalaryDay}
          />
          <Button
            className="self-end"
            disabled={savingSalary}
            onPress={() => void handleSaveSalary()}
          >
            {savingSalary ? 'Salvando...' : 'Salvar salário'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Metas (% da renda)</CardTitle>
          <CardDescription>
            Percentuais da sua renda. Aparecem no Planejamento acompanhando o período selecionado:
            linha de referência no gráfico e card de progresso.
          </CardDescription>
        </CardHeader>
        <CardContent className="gap-4">
          {goalsError ? <InlineMessage>{goalsError}</InlineMessage> : null}
          {[
            {
              label: 'Teto de gasto (%)',
              placeholder: 'Ex: 60',
              value: spendingGoal,
              onChangeText: setSpendingGoal,
            },
            {
              label: 'Quanto guardar (%)',
              placeholder: 'Ex: 20',
              value: savingsGoal,
              onChangeText: setSavingsGoal,
            },
            {
              label: 'Teto de essenciais (%)',
              placeholder: 'Ex: 30',
              value: essentialsGoal,
              onChangeText: setEssentialsGoal,
            },
          ].map((field) => (
            <View key={field.label} className="gap-2">
              <Input
                label={field.label}
                keyboardType="decimal-pad"
                placeholder={field.placeholder}
                value={field.value}
                onChangeText={field.onChangeText}
              />
              <Text className="text-xs text-zinc-500">{goalHint(field.value, salary)}</Text>
            </View>
          ))}
          <Button
            className="self-end"
            disabled={savingGoals}
            onPress={() => void handleSaveGoals()}
          >
            {savingGoals ? 'Salvando...' : 'Salvar metas'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-start justify-between gap-3">
          <View className="flex-1">
            <CardTitle>Cartões</CardTitle>
            <CardDescription>A fatura de cada cartão é criada todo mês, mesmo zerada.</CardDescription>
          </View>
          <Button size="sm" onPress={() => openCardForm()}>
            <Plus size={16} color="#ffffff" />
            <Text className="text-sm font-medium text-white">Novo cartão</Text>
          </Button>
        </CardHeader>
        <CardContent className="gap-3">
          {cardToggleError ? <InlineMessage>{cardToggleError}</InlineMessage> : null}
          {cardsQuery.isLoading ? (
            <View className="gap-3">
              <Skeleton className="h-14 w-full" />
              <Skeleton className="h-14 w-full" />
            </View>
          ) : cardsQuery.isError ? (
            <View className="gap-3">
              <InlineMessage>Falha ao carregar cartões</InlineMessage>
              <Button
                variant="outline"
                size="sm"
                className="self-start"
                onPress={() => void cardsQuery.refetch()}
              >
                Tentar novamente
              </Button>
            </View>
          ) : cards.length === 0 ? (
            <Text className="py-4 text-center text-sm text-zinc-500">
              Nenhum cartão cadastrado ainda.
            </Text>
          ) : (
            <View className="gap-3">
              {cards.map((card) => (
                <View
                  key={card.id}
                  className="flex-row items-center justify-between gap-3 rounded-md border border-zinc-100 p-3"
                >
                  <View className="min-w-0 flex-1 gap-1">
                    <View className="flex-row items-center gap-2">
                      <Text
                        className="text-sm font-medium text-zinc-900"
                        numberOfLines={1}
                      >
                        {card.name}
                      </Text>
                      <Badge variant={card.is_active ? 'default' : 'outline'}>
                        {card.is_active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </View>
                    <Text className="text-xs text-zinc-500">vence dia {card.due_day}</Text>
                  </View>
                  <View className="flex-row items-center gap-2">
                    <Button size="sm" variant="outline" onPress={() => openCardForm(card)}>
                      Editar
                    </Button>
                    <Switch
                      value={card.is_active}
                      disabled={savingCardId === card.id}
                      onValueChange={() => void handleToggleCard(card)}
                      accessibilityLabel={`Cartão ${card.name} ${card.is_active ? 'ativo' : 'inativo'}`}
                    />
                  </View>
                </View>
              ))}
            </View>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Modo lançamento rápido</CardTitle>
          <CardDescription>
            Lance no momento da transação, com extrato de saldo corrente e conciliação da fatura por
            IA. Desligado, o app mantém o fluxo de subir a fatura em lote.
          </CardDescription>
        </CardHeader>
        <CardContent className="gap-4">
          {modeError ? <InlineMessage>{modeError}</InlineMessage> : null}
          <View className="flex-row items-center justify-between gap-4">
            <Label className="flex-1">Ativar modo lançamento rápido</Label>
            <Switch
              value={modoOn}
              disabled={savingMode}
              onValueChange={(checked) => void handleToggle(checked)}
              accessibilityLabel="Ativar modo lançamento rápido"
            />
          </View>
        </CardContent>
      </Card>

      <CardFormDialog
        visible={cardFormOpen}
        card={editingCard}
        onClose={closeCardForm}
        onSaved={handleCardSaved}
      />
    </ScrollView>
  );
}
