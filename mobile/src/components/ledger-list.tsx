import { FlatList, Text, View } from 'react-native';
import { EmptyState } from './empty-state';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';
import { cn } from './ui/utils';
import { getCategoryColor } from '../lib/category-colors';
import { parseIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import type { LedgerEntry, LedgerResult } from '../services';

export interface LedgerListProps {
  ledger?: LedgerResult;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
}

function formatDate(value: string): string {
  return parseIsoDate(value).toLocaleDateString('pt-BR');
}

function formatEntryValue(entry: LedgerEntry): string {
  const amount = Math.abs(parseFloat(entry.amount) || 0);
  const formatted = formatCurrency(amount);
  return entry.direction === 'incoming' ? `+${formatted}` : `-${formatted}`;
}

function LedgerRow({ entry }: { entry: LedgerEntry }) {
  const color = getCategoryColor(entry.category);
  const isIncoming = entry.direction === 'incoming';

  return (
    <View className="flex-row items-center justify-between gap-3 py-3">
      <View className="flex-1 gap-1">
        <View className="flex-row flex-wrap items-center gap-2">
          <Text className="text-xs text-zinc-500">{formatDate(entry.date)}</Text>
          {entry.is_card ? <Badge variant="secondary">Cartão</Badge> : null}
          {!entry.paid_at ? (
            <Badge variant="outline" className="border-orange-300">
              <Text className="text-xs font-medium text-orange-700">Previsto</Text>
            </Badge>
          ) : null}
          {entry.category ? (
            <Badge variant="outline" className={cn(color.bg, color.border)}>
              <Text className={cn('text-xs font-medium', color.text)}>{entry.category}</Text>
            </Badge>
          ) : null}
        </View>
        <Text numberOfLines={1} className="text-sm font-medium text-zinc-900">
          {entry.description}
        </Text>
      </View>

      <View className="items-end">
        <Text
          className={cn(
            'text-sm font-semibold',
            isIncoming ? 'text-green-600' : 'text-red-600'
          )}
        >
          {formatEntryValue(entry)}
        </Text>
        <Text className="text-xs text-zinc-500">
          Saldo: {formatCurrency(entry.running_balance)}
        </Text>
      </View>
    </View>
  );
}

export function LedgerList({ ledger, loading, error, onRetry }: LedgerListProps) {
  const entries = ledger?.entries ?? [];

  if (loading && entries.length === 0) {
    return (
      <View testID="ledger-loading" className="gap-4 py-2">
        {[0, 1, 2].map((index) => (
          <View key={index} className="flex-row items-center justify-between gap-3">
            <View className="flex-1 gap-2">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-4 w-40" />
            </View>
            <Skeleton className="h-4 w-20" />
          </View>
        ))}
      </View>
    );
  }

  if (error && entries.length === 0) {
    return (
      <EmptyState
        title={error}
        action={
          onRetry ? (
            <Button variant="outline" onPress={onRetry}>
              Tentar novamente
            </Button>
          ) : undefined
        }
      />
    );
  }

  if (entries.length === 0) {
    return <EmptyState title="Nenhum lançamento no período" />;
  }

  return (
    <FlatList
      data={entries}
      scrollEnabled={false}
      keyExtractor={(entry, index) =>
        `${entry.transaction_id}-${entry.sub_transaction_id ?? 0}-${index}`
      }
      ItemSeparatorComponent={() => <View className="h-px bg-zinc-100" />}
      renderItem={({ item }) => <LedgerRow entry={item} />}
    />
  );
}
