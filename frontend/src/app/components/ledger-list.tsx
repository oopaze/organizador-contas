import React from 'react';
import { LedgerEntry } from '@/services';
import { Badge } from '@/app/components/ui/badge';

interface LedgerListProps {
  entries: LedgerEntry[];
  loading: boolean;
}

const formatMoney = (value: string) => `R$ ${parseFloat(value || '0').toFixed(2)}`;

const formatDate = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR');

export const LedgerList: React.FC<LedgerListProps> = ({ entries, loading }) => {
  if (loading) {
    return <p className="py-6 text-center text-sm text-muted-foreground">Carregando...</p>;
  }

  if (entries.length === 0) {
    return <p className="py-6 text-center text-sm text-muted-foreground">Nenhum lançamento no período</p>;
  }

  return (
    <div className="divide-y">
      {entries.map((entry, index) => (
        <div
          key={`${entry.transaction_id}-${entry.sub_transaction_id ?? 0}-${index}`}
          className="flex items-center justify-between gap-3 py-3"
        >
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{formatDate(entry.date)}</span>
              {entry.is_card && <Badge variant="secondary">Cartão</Badge>}
              {!entry.paid_at && <Badge variant="outline" className="border-orange-300 text-orange-700">Previsto</Badge>}
            </div>
            <p className="truncate text-sm font-medium text-gray-900">{entry.description}</p>
          </div>

          <div className="text-right">
            <p className={`text-sm font-semibold ${entry.direction === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
              {entry.direction === 'incoming' ? '+' : '-'} {formatMoney(entry.amount)}
            </p>
            <p className="text-xs text-muted-foreground">Saldo: {formatMoney(entry.running_balance)}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
