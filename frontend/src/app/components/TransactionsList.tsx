import React, { useMemo } from 'react';
import { 
  Transaction, 
  deleteTransaction,
} from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Trash2, Calendar } from 'lucide-react';
import { toast } from 'sonner';

interface TransactionsListProps {
  type: 'expenses' | 'income' | 'all';
  transactions?: Transaction[];
  onUpdate: () => void;
  loading?: boolean;
}

const parseTypeToTransactionType = {
  expenses: 'outgoing',
  income: 'incoming',
  all: undefined,
}

const parseTypeToPortuguese = {
  expenses: 'despesa',
  income: 'receita',
  all: 'transação',
}

export const TransactionsList: React.FC<TransactionsListProps> = ({
  type,
  transactions = [],
  onUpdate,
  loading,
}) => {
  const filteredTransaction = useMemo(() => transactions.filter(t => {
    if (type === 'all') return true;
    return t.transaction_type === parseTypeToTransactionType[type];
  }), [transactions, type]);
  const handleDeleteTransaction = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) return;
    
    try {
      await deleteTransaction(id);
      toast.success('Transação excluída');
      onUpdate();
    } catch (error) {
      debugger

      toast.error('Falha ao excluir transação');
    }
  };


  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        Carregando...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Incoming Transactions */}
      {filteredTransaction.length > 0 && (
        <div>
          <h3 className="font-medium text-gray-900 mb-3">Receitas</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Identificador</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead className="text-right">Valor</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTransaction
                .map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell>
                      {new Date(transaction.due_date).toLocaleDateString('pt-BR')}
                    </TableCell>
                    <TableCell>{transaction.transaction_identifier}</TableCell>
                    <TableCell>
                      {transaction.is_salary && (
                        <Badge className="bg-green-100 text-green-800">Salário</Badge>
                      )}
                      {transaction.transaction_type === 'incoming' && !transaction.is_salary && (
                        <Badge variant="secondary">Receita</Badge>
                      )}
                      {transaction.transaction_type === 'outgoing' && (
                        <Badge variant="secondary">Despesa</Badge>
                      )}
                    </TableCell>
                    <TableCell className={`text-right ${transaction.transaction_type === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
                      R$ {parseFloat(transaction.total_amount).toFixed(2)}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteTransaction(transaction.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>
      )}

      {filteredTransaction.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Nenhuma {parseTypeToPortuguese[type]} encontrada
        </div>
      )}
    </div>
  );
};
