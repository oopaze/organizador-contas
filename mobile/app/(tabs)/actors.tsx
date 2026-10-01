import { useCallback, useMemo, useState } from 'react';
import { Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Calculator from 'lucide-react-native/icons/calculator';
import ChevronRight from 'lucide-react-native/icons/chevron-right';
import Pencil from 'lucide-react-native/icons/pencil';
import Plus from 'lucide-react-native/icons/plus';
import Share2 from 'lucide-react-native/icons/share-2';
import Trash from 'lucide-react-native/icons/trash';
import TrendingDown from 'lucide-react-native/icons/trending-down';
import TrendingUp from 'lucide-react-native/icons/trending-up';
import UserCheck from 'lucide-react-native/icons/user-check';
import Users from 'lucide-react-native/icons/users';
import Wallet from 'lucide-react-native/icons/wallet';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ActorSubTransactionsList } from '../../src/components/actor-sub-transactions-list';
import { AddActorDialog } from '../../src/components/add-actor-dialog';
import { EditActorDialog } from '../../src/components/edit-actor-dialog';
import { EmptyState } from '../../src/components/empty-state';
import { InlineMessage } from '../../src/components/inline-message';
import { MonthPicker } from '../../src/components/month-picker';
import { ShareActorDialog } from '../../src/components/share-actor-dialog';
import { StatCard } from '../../src/components/stat-card';
import { AlertDialog } from '../../src/components/ui/alert-dialog';
import { Button } from '../../src/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../src/components/ui/card';
import { Skeleton } from '../../src/components/ui/skeleton';
import { cn } from '../../src/components/ui/utils';
import { formatCurrency } from '../../src/lib/format';
import { formatSubmitError } from '../../src/lib/transaction-form';
import { useOnlineStatus } from '../../src/lib/use-online-status';
import {
  deleteActor,
  getActor,
  getActors,
  getActorStats,
  type Actor,
} from '../../src/services';

function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function lastDayOf(month: string): number {
  const [year, monthNumber] = month.split('-').map(Number);
  return new Date(year, monthNumber, 0).getDate();
}

interface ActorFieldProps {
  label: string;
  value: string;
  valueClassName?: string;
}

function ActorField({ label, value, valueClassName }: ActorFieldProps) {
  return (
    <View className="min-w-[40%] flex-1 gap-0.5">
      <Text className="text-xs text-zinc-500">{label}</Text>
      <Text className={cn('text-sm font-semibold text-zinc-900', valueClassName)}>{value}</Text>
    </View>
  );
}

interface ActorCardProps {
  actor: Actor;
  expanded: boolean;
  detail?: Actor;
  detailLoading: boolean;
  detailError: boolean;
  onToggle: () => void;
  onShare: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onRetryDetail: () => void;
  onChanged: () => void;
}

function ActorCard({
  actor,
  expanded,
  detail,
  detailLoading,
  detailError,
  onToggle,
  onShare,
  onEdit,
  onDelete,
  onRetryDetail,
  onChanged,
}: ActorCardProps) {
  const totalSpent = actor.total_spent ?? 0;
  const remaining = actor.total_remaining ?? 0;
  const lent = actor.loan_total_lent ?? 0;
  const outstanding = actor.loan_total_outstanding ?? 0;

  const outstandingValue =
    outstanding > 0 ? formatCurrency(outstanding) : lent > 0 ? formatCurrency(0) : '—';

  return (
    <View className="rounded-lg border border-zinc-200 bg-white">
      <View className="flex-row items-center gap-1 px-3 pt-3">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Expandir ${actor.name}`}
          accessibilityState={{ expanded }}
          onPress={onToggle}
          className="flex-1 flex-row items-center gap-2 py-1 active:opacity-70"
        >
          <ChevronRight
            size={16}
            color="#71717a"
            style={{ transform: [{ rotate: expanded ? '90deg' : '0deg' }] }}
          />
          <Text className="flex-1 text-sm font-medium text-zinc-900">{actor.name}</Text>
        </Pressable>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          accessibilityLabel="Compartilhar com este ator"
          onPress={onShare}
        >
          <Share2 size={16} color="#71717a" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          accessibilityLabel="Editar ator"
          onPress={onEdit}
        >
          <Pencil size={16} color="#18181b" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          accessibilityLabel="Remover ator"
          onPress={onDelete}
        >
          <Trash size={16} color="#dc2626" />
        </Button>
      </View>

      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Ver detalhes de ${actor.name}`}
        onPress={onToggle}
        className="flex-row flex-wrap gap-x-4 gap-y-2 px-3 pb-3 pl-8 pt-2 active:opacity-70"
      >
        <ActorField label="Cartão (Gasto)" value={formatCurrency(totalSpent)} />
        <ActorField
          label="Cartão (Restante)"
          value={formatCurrency(remaining)}
          valueClassName={remaining > 0 ? 'text-orange-600' : 'text-green-600'}
        />
        <ActorField label="Emprestado" value={lent > 0 ? formatCurrency(lent) : '—'} />
        <ActorField
          label="A Receber"
          value={outstandingValue}
          valueClassName={
            outstanding > 0 ? 'text-orange-600' : lent > 0 ? 'text-green-600' : undefined
          }
        />
      </Pressable>

      {expanded ? (
        <View className="gap-2 border-t border-zinc-100 bg-zinc-50 p-3">
          <Text className="text-sm font-medium text-zinc-500">Subtransações vinculadas</Text>
          <ActorSubTransactionsList
            subTransactions={detail?.sub_transactions}
            loading={detailLoading}
            error={detailError ? 'Falha ao carregar subtransações' : null}
            onRetry={onRetryDetail}
            onChanged={onChanged}
          />
        </View>
      ) : null}
    </View>
  );
}

export default function ActorsScreen() {
  const queryClient = useQueryClient();
  const isOnline = useOnlineStatus();

  const [month, setMonth] = useState(currentMonth);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedActorId, setExpandedActorId] = useState<number | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [editingActor, setEditingActor] = useState<Actor | null>(null);
  const [actorToDelete, setActorToDelete] = useState<Actor | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [sharingActor, setSharingActor] = useState<Actor | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const dueDate = `${month}-01`;
  const dueDateEnd = `${month}-${String(lastDayOf(month)).padStart(2, '0')}`;
  const actorsFilters = useMemo(() => ({ due_date: dueDate }), [dueDate]);
  const statsFilters = useMemo(
    () => ({ due_date_start: dueDate, due_date_end: dueDateEnd }),
    [dueDate, dueDateEnd]
  );

  const actorsQuery = useQuery({
    queryKey: ['actors', actorsFilters],
    queryFn: () => getActors(actorsFilters),
  });

  const statsQuery = useQuery({
    queryKey: ['actorStats', statsFilters],
    queryFn: () => getActorStats(statsFilters),
  });

  const detailQuery = useQuery({
    queryKey: ['actor', expandedActorId, actorsFilters],
    queryFn: () => getActor(expandedActorId ?? 0, actorsFilters),
    enabled: expandedActorId !== null,
  });

  const refetchAll = useCallback(
    () =>
      Promise.all([
        queryClient.refetchQueries({ queryKey: ['actors', actorsFilters], exact: true }),
        queryClient.refetchQueries({ queryKey: ['actorStats', statsFilters], exact: true }),
        queryClient.refetchQueries({
          queryKey: ['actor', expandedActorId, actorsFilters],
          exact: true,
        }),
      ]),
    [queryClient, actorsFilters, statsFilters, expandedActorId]
  );

  /** Escritas de ator/subtransação invalidam atores/stats e releem a tela. */
  const handleChanged = useCallback(() => {
    void queryClient.invalidateQueries({ queryKey: ['actors'] });
    void queryClient.invalidateQueries({ queryKey: ['actorStats'] });
    void queryClient.invalidateQueries({ queryKey: ['actor'] });
    void refetchAll();
  }, [queryClient, refetchAll]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refetchAll();
    } finally {
      setRefreshing(false);
    }
  }, [refetchAll]);

  const changeMonth = (value: string) => {
    if (!value) return;
    setMonth(value);
    setExpandedActorId(null);
  };

  const toggleActor = (id: number) => {
    setExpandedActorId((current) => (current === id ? null : id));
  };

  const handleConfirmDelete = async () => {
    if (!actorToDelete || deleting) return;

    const target = actorToDelete;
    setDeleting(true);
    setActionError(null);
    try {
      await deleteActor(target.id);
      if (expandedActorId === target.id) setExpandedActorId(null);
      setActorToDelete(null);
      handleChanged();
    } catch (error) {
      setActorToDelete(null);
      setActionError(formatSubmitError(error, 'Falha ao excluir ator. Verifique a conexão e tente de novo.'));
    } finally {
      setDeleting(false);
    }
  };

  const actors = actorsQuery.data ?? [];
  const stats = statsQuery.data;
  const loading = actorsQuery.isLoading || statsQuery.isLoading;
  const hasData = actorsQuery.data !== undefined || statsQuery.data !== undefined;
  const hasError = actorsQuery.isError || statsQuery.isError;
  const showErrorState = !loading && hasError && !hasData;
  const showStaleNotice = hasError && hasData && isOnline;

  return (
    <SafeAreaView edges={['top']} className="flex-1 bg-zinc-50">
      <ScrollView
        contentContainerClassName="gap-6 p-4 pb-24"
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#059669']}
            tintColor="#059669"
          />
        }
      >
        <View className="gap-3">
          <View className="flex-row items-center gap-2">
            <Users size={24} color="#3f3f46" />
            <Text className="text-2xl font-bold text-zinc-900">Atores</Text>
          </View>
          <MonthPicker value={month} onChange={changeMonth} />
        </View>

        {showStaleNotice ? (
          <View className="rounded-md bg-amber-100 px-3 py-2">
            <Text className="text-center text-sm text-amber-900">
              Não foi possível atualizar — mostrando dados salvos
            </Text>
          </View>
        ) : null}

        {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}

        {loading ? (
          <View className="gap-3">
            <View className="flex-row flex-wrap gap-3">
              {[0, 1, 2, 3].map((index) => (
                <View
                  key={index}
                  className="w-[47%] grow gap-3 rounded-xl border border-zinc-200 bg-white p-4"
                >
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-7 w-28" />
                  <Skeleton className="h-3 w-32" />
                </View>
              ))}
            </View>
            <Skeleton className="h-32 w-full" />
          </View>
        ) : showErrorState ? (
          <EmptyState
            title="Falha ao carregar atores"
            description="Verifique a conexão e tente de novo."
            action={
              <Button variant="outline" onPress={() => void refetchAll()}>
                Tentar novamente
              </Button>
            }
          />
        ) : (
          <>
            <View className="flex-row flex-wrap gap-3">
              <View className="w-[47%] grow">
                <StatCard
                  title="Total Gasto"
                  value={formatCurrency(stats?.total_spent ?? 0)}
                  subtitle={
                    <Text className="mt-1 text-sm text-zinc-500">
                      <Text className="font-medium text-green-600">
                        {formatCurrency(stats?.total_spent_paid ?? 0)}
                      </Text>{' '}
                      já pago
                    </Text>
                  }
                  icon={<Wallet size={16} color="#71717a" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Maior Gastador"
                  value={stats?.biggest_spender || '-'}
                  subtitle={
                    stats?.biggest_spender
                      ? formatCurrency(stats.biggest_spender_amount ?? 0)
                      : 'Nenhum gasto no período'
                  }
                  tone="negative"
                  icon={<TrendingUp size={16} color="#dc2626" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Menor Gastador"
                  value={stats?.smallest_spender || '-'}
                  subtitle={
                    stats?.smallest_spender
                      ? formatCurrency(stats.smallest_spender_amount ?? 0)
                      : 'Nenhum gasto no período'
                  }
                  tone="positive"
                  icon={<TrendingDown size={16} color="#16a34a" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Média por Ator"
                  value={formatCurrency(stats?.average_spent ?? 0)}
                  subtitle="Gasto médio por ator"
                  icon={<Calculator size={16} color="#2563eb" />}
                />
              </View>
              <View className="w-[47%] grow">
                <StatCard
                  title="Atores Ativos"
                  value={String(stats?.active_actors ?? 0)}
                  subtitle={`De ${actors.length} atores cadastrados`}
                  icon={<UserCheck size={16} color="#9333ea" />}
                />
              </View>
            </View>

            <View className="flex-row justify-end">
              <Button variant="outline" onPress={() => setAddOpen(true)}>
                <Plus size={16} color="#18181b" />
                <Text className="text-sm font-medium text-zinc-900">Adicionar Ator</Text>
              </Button>
            </View>

            <Card>
              <CardHeader>
                <View className="flex-row items-center gap-2">
                  <Users size={20} color="#3f3f46" />
                  <CardTitle>Atores</CardTitle>
                </View>
                <CardDescription>Gerencie os atores das suas transações</CardDescription>
              </CardHeader>
              <CardContent>
                {actorsQuery.isError && actors.length === 0 ? (
                  <View className="gap-3">
                    <InlineMessage>Falha ao carregar atores</InlineMessage>
                    <Button
                      variant="outline"
                      size="sm"
                      className="self-start"
                      onPress={() => void actorsQuery.refetch()}
                    >
                      Tentar novamente
                    </Button>
                  </View>
                ) : actors.length === 0 ? (
                  <Text className="py-8 text-center text-sm text-zinc-500">
                    Nenhum ator encontrado
                  </Text>
                ) : (
                  <View className="gap-3">
                    {actors.map((actor) => {
                      const expanded = expandedActorId === actor.id;
                      return (
                        <ActorCard
                          key={actor.id}
                          actor={actor}
                          expanded={expanded}
                          detail={expanded ? detailQuery.data : undefined}
                          detailLoading={expanded && detailQuery.isLoading}
                          detailError={expanded && detailQuery.isError}
                          onToggle={() => toggleActor(actor.id)}
                          onShare={() => setSharingActor(actor)}
                          onEdit={() => setEditingActor(actor)}
                          onDelete={() => setActorToDelete(actor)}
                          onRetryDetail={() => void detailQuery.refetch()}
                          onChanged={handleChanged}
                        />
                      );
                    })}
                  </View>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </ScrollView>

      <AddActorDialog
        visible={addOpen}
        onClose={() => setAddOpen(false)}
        onSaved={handleChanged}
      />

      <EditActorDialog
        visible={editingActor !== null}
        actor={editingActor}
        onClose={() => setEditingActor(null)}
        onSaved={handleChanged}
      />

      <ShareActorDialog
        visible={sharingActor !== null}
        actorId={sharingActor?.id ?? null}
        actorName={sharingActor?.name}
        onClose={() => setSharingActor(null)}
      />

      <AlertDialog
        visible={actorToDelete !== null}
        onCancel={() => setActorToDelete(null)}
        onConfirm={() => void handleConfirmDelete()}
        title="Excluir ator"
        description={`Tem certeza que deseja excluir o ator "${actorToDelete?.name}"? Esta ação não pode ser desfeita.`}
        confirmLabel="Excluir"
        cancelLabel="Cancelar"
        destructive
      />
    </SafeAreaView>
  );
}
