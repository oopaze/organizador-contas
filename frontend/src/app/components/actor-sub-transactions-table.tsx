import React from 'react';
import { SubTransaction } from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Badge } from '@/app/components/ui/badge';
import { Skeleton } from '@/app/components/ui/skeleton';

interface ActorSubTransactionsTableProps {
  subTransactions?: SubTransaction[];
  loading?: boolean;
  error?: string | null;
}

export const ActorSubTransactionsTable: React.FC<ActorSubTransactionsTableProps> = ({
  subTransactions = [],
  loading = false,
  error = null,
}) => {
  if (loading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Parcela</TableHead>
            <TableHead className="text-right">Valor</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[1, 2, 3].map((i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-20" /></TableCell>
              <TableCell><Skeleton className="h-4 w-48" /></TableCell>
              <TableCell><Skeleton className="h-4 w-32" /></TableCell>
              <TableCell><Skeleton className="h-4 w-12" /></TableCell>
              <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4 text-red-500 text-sm">
        {error}
      </div>
    );
  }

  if (subTransactions.length === 0) {
    return (
      <div className="text-center py-4 text-muted-foreground text-sm">
        Nenhuma subtransação vinculada a este ator
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Data</TableHead>
          <TableHead>Nome</TableHead>
          <TableHead>Fonte</TableHead>
          <TableHead>Descrição</TableHead>
          <TableHead>Parcela</TableHead>
          <TableHead className="text-right">Valor</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {subTransactions.map((subTransaction) => {
          const amount = parseFloat(subTransaction.amount);
          const isNegative = amount < 0;
          return (
            <TableRow key={subTransaction.id}>
              <TableCell className="text-sm">
                {new Date(subTransaction.date).toLocaleDateString('pt-BR')}
              </TableCell>
              <TableCell className="text-sm max-w-[200px] truncate">
                {subTransaction.description}
              </TableCell>
              <TableCell className="text-sm max-w-[300px] truncate">
                {subTransaction.transaction_identifier}
              </TableCell>
              <TableCell className="text-sm max-w-[300px] truncate">
                {subTransaction.user_provided_description || (
                  <span className="text-muted-foreground">-</span>
                )}
              </TableCell>
              <TableCell>
                {subTransaction.installment_info && subTransaction.installment_info !== 'not installment' ? (
                  <Badge variant="outline" className="text-xs">
                    {subTransaction.installment_info.replace('installment ', '').replace(' of ', '/')}
                  </Badge>
                ) : (
                  <span className="text-xs text-muted-foreground">À vista</span>
                )}
              </TableCell>
              <TableCell className={`text-right text-sm ${isNegative ? 'text-green-600' : 'text-red-600'}`}>
                R$ {Math.abs(amount).toFixed(2)}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};

